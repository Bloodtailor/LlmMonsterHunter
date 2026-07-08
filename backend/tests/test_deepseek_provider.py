# DeepSeek Provider Tests - OFFLINE (no network, test DB)
# Exercises Set-M3 (docs/plans/game-settings.md) with requests fully
# faked: the SSE stream loop (content accumulates, reasoning_content is
# skipped, the usage chunk yields exact token counts), param translation
# (llama-only knobs dropped, thinking disabled except for the legacy
# reasoner id), player-facing HTTP error mapping, list_models parsing,
# provider dispatch, and the context budget following the active provider.
#
# Usage: python -m backend.tests.test_deepseek_provider   (from project root)

import json
import os

import requests as real_requests

from backend.tests.harness import build_test_app

PASSED = 0
FAILED = 0

TEST_API_KEY = 'sk-test-000000abcd1234'


def check(name: str, condition: bool, detail: str = ''):
    global PASSED, FAILED
    if condition:
        PASSED += 1
        print(f"  ✅ {name}")
    else:
        FAILED += 1
        print(f"  ❌ {name}{f' - {detail}' if detail else ''}")


def set_env(key: str, value):
    original = os.environ.get(key)
    if value is None:
        os.environ.pop(key, None)
    else:
        os.environ[key] = value
    return original


def sse(chunk: dict) -> str:
    return 'data: ' + json.dumps(chunk)


class FakeResponse:
    def __init__(self, status_code=200, lines=None, json_data=None):
        self.status_code = status_code
        self._lines = lines or []
        self._json = json_data or {}

    def iter_lines(self, decode_unicode=False):
        return iter(self._lines)

    def json(self):
        return self._json

    def close(self):
        pass


class FakeRequests:
    """Stands in for the requests module inside the deepseek provider.
    Real exception classes ride along so the provider's except clauses
    keep working."""

    exceptions = real_requests.exceptions

    def __init__(self, post_response=None, get_response=None):
        self.post_response = post_response
        self.get_response = get_response
        self.last_post = None
        self.last_get = None

    def post(self, url, headers=None, json=None, stream=False, timeout=None):
        self.last_post = {'url': url, 'headers': headers, 'json': json}
        if isinstance(self.post_response, Exception):
            raise self.post_response
        return self.post_response

    def get(self, url, headers=None, timeout=None):
        self.last_get = {'url': url, 'headers': headers}
        if isinstance(self.get_response, Exception):
            raise self.get_response
        return self.get_response


# The shape llm_log.get_inference_params() hands the provider
LLAMA_STYLE_PARAMS = {
    'max_tokens': 256,
    'temperature': 0.8,
    'top_p': 0.9,
    'top_k': 40,
    'repeat_penalty': 1.1,
    'frequency_penalty': 0.0,
    'presence_penalty': 0.0,
    'tfs_z': 1.0,
    'typical_p': 1.0,
    'mirostat_mode': 0,
    'mirostat_tau': 5.0,
    'mirostat_eta': 0.1,
    'seed': -1,
    'stop': ['</s>'],
    'echo': False,
}

HAPPY_STREAM = [
    sse({'choices': [{'delta': {'role': 'assistant'}}]}),
    sse({'choices': [{'delta': {'content': 'Once'}}]}),
    '',  # SSE keep-alive blank line
    sse({'choices': [{'delta': {'reasoning_content': 'let me think...'}}]}),
    sse({'choices': [{'delta': {'content': ' upon'}}]}),
    sse({'choices': [{'delta': {'content': ' a time.'}, 'finish_reason': 'stop'}]}),
    sse({'choices': [], 'usage': {'prompt_tokens': 42, 'completion_tokens': 5}}),
    'data: [DONE]',
]


def main():
    from backend.ai.llm.provider_settings import SETTINGS_KEY
    from backend.ai.llm.providers import deepseek, get_provider

    print('🧪 DEEPSEEK PROVIDER TESTS')
    print('=' * 50)

    app = build_test_app()

    with app.app_context():
        from backend.models.core import create_tables
        from backend.models.game_setting import GameSetting

        create_tables()

        original_context_size = set_env('LLM_CONTEXT_SIZE', '4096')
        real_requests_module = deepseek.requests

        try:
            GameSetting.set(
                SETTINGS_KEY,
                {
                    'provider': 'deepseek',
                    'deepseek': {
                        'api_key': TEST_API_KEY,
                        'model': 'deepseek-v4-flash',
                        'context_window': 65536,
                    },
                },
            )

            # ===== dispatch =====
            print('\n-- dispatch --')
            check(
                'a deepseek stamp dispatches to the deepseek provider',
                get_provider('deepseek') is deepseek,
            )

            # ===== the happy stream =====
            print('\n-- the happy stream --')
            fake = FakeRequests(post_response=FakeResponse(lines=HAPPY_STREAM))
            deepseek.requests = fake

            streamed = []
            result = deepseek.generate_streaming(
                'Tell a story.',
                callback=streamed.append,
                model_name='deepseek-v4-flash',
                **LLAMA_STYLE_PARAMS,
            )

            check('the generation succeeds', result['success'] is True, str(result.get('error')))
            check(
                'content accumulates and reasoning_content never reaches the story',
                result['text'] == 'Once upon a time.',
                repr(result['text']),
            )
            check('completion tokens come from the usage chunk', result['tokens'] == 5)
            check('prompt tokens are exact from the usage chunk', result['prompt_tokens'] == 42)
            check('the model name rides the result', result['model_name'] == 'deepseek-v4-flash')
            check(
                'the callback streamed the growing text',
                streamed[-1] == 'Once upon a time.' and 'Once' in streamed,
                str(streamed[:3]),
            )

            body = fake.last_post['json']
            check(
                'the prompt rides as one user message',
                body['messages'] == [{'role': 'user', 'content': 'Tell a story.'}],
            )
            check(
                'streaming asks for the usage chunk',
                body['stream'] is True and body['stream_options'] == {'include_usage': True},
            )
            check(
                'thinking is disabled for v4 models', body.get('thinking') == {'type': 'disabled'}
            )
            check(
                'chat-API params translate through',
                body['max_tokens'] == 256
                and body['temperature'] == 0.8
                and body['stop'] == ['</s>'],
            )
            check(
                'llama-only knobs are dropped in translation',
                all(
                    name not in body
                    for name in (
                        'top_k',
                        'repeat_penalty',
                        'tfs_z',
                        'typical_p',
                        'mirostat_mode',
                        'seed',
                        'echo',
                    )
                ),
                str(sorted(body)),
            )
            check(
                'the key rides the Authorization header',
                fake.last_post['headers']['Authorization'] == f'Bearer {TEST_API_KEY}',
            )

            # ===== the legacy reasoner id =====
            print('\n-- the legacy reasoner id --')
            fake = FakeRequests(post_response=FakeResponse(lines=HAPPY_STREAM))
            deepseek.requests = fake
            deepseek.generate_streaming('x', model_name='deepseek-reasoner', **LLAMA_STYLE_PARAMS)
            check(
                'deepseek-reasoner IS thinking mode - no disable sent',
                'thinking' not in fake.last_post['json'],
            )

            # ===== error mapping =====
            print('\n-- error mapping --')
            for status, expected_words in (
                (401, 'API key'),
                (402, 'balance'),
                (429, 'rate limit'),
                (503, 'server error'),
            ):
                fake = FakeRequests(
                    post_response=FakeResponse(
                        status_code=status,
                        json_data={'error': {'message': 'upstream detail'}},
                    )
                )
                deepseek.requests = fake
                result = deepseek.generate_streaming('x', model_name='deepseek-v4-flash')
                check(
                    f'{status} maps to a player-facing message',
                    result['success'] is False
                    and expected_words in result['error']
                    and 'upstream detail' in result['error'],
                    str(result['error']),
                )

            fake = FakeRequests(
                post_response=real_requests.exceptions.ConnectionError('no route to host')
            )
            deepseek.requests = fake
            result = deepseek.generate_streaming('x', model_name='deepseek-v4-flash')
            check(
                'a network failure says so plainly',
                result['success'] is False and 'Could not reach DeepSeek' in result['error'],
                str(result['error']),
            )

            fake = FakeRequests(post_response=FakeResponse(lines=['data: [DONE]']))
            deepseek.requests = fake
            result = deepseek.generate_streaming('x', model_name='deepseek-v4-flash')
            check(
                'an empty stream fails instead of returning silence',
                result['success'] is False and 'no text' in result['error'],
            )

            # ===== the key must exist =====
            print('\n-- missing configuration --')
            GameSetting.delete_key(SETTINGS_KEY)
            result = deepseek.generate_streaming('x', model_name='deepseek-v4-flash')
            check(
                'a missing key fails with a settings pointer, never a crash',
                result['success'] is False and 'Settings' in result['error'],
                str(result.get('error')),
            )
            GameSetting.set(
                SETTINGS_KEY,
                {
                    'provider': 'deepseek',
                    'deepseek': {
                        'api_key': TEST_API_KEY,
                        'model': 'deepseek-v4-flash',
                        'context_window': 65536,
                    },
                },
            )

            # ===== list_models =====
            print('\n-- list_models --')
            fake = FakeRequests(
                get_response=FakeResponse(
                    json_data={
                        'object': 'list',
                        'data': [
                            {'id': 'deepseek-v4-flash', 'object': 'model', 'owned_by': 'deepseek'},
                            {'id': 'deepseek-v4-pro', 'object': 'model', 'owned_by': 'deepseek'},
                        ],
                    }
                )
            )
            deepseek.requests = fake
            result = deepseek.list_models(TEST_API_KEY)
            check(
                'the live model ids parse out',
                result['success'] is True
                and result['models'] == ['deepseek-v4-flash', 'deepseek-v4-pro'],
                str(result),
            )
            check(
                'the models endpoint is the one called',
                fake.last_get['url'].endswith('/models'),
            )

            fake = FakeRequests(
                get_response=FakeResponse(
                    status_code=401, json_data={'error': {'message': 'bad key'}}
                )
            )
            deepseek.requests = fake
            result = deepseek.list_models('sk-wrong')
            check(
                'a bad key fails the fetch with the mapped message',
                result['success'] is False and 'API key' in result['error'],
            )

            # ===== the service proxy =====
            print('\n-- the fetch-models service --')
            from backend.services import settings_service

            fake = FakeRequests(
                get_response=FakeResponse(json_data={'data': [{'id': 'deepseek-v4-flash'}]})
            )
            deepseek.requests = fake
            result = settings_service.fetch_deepseek_models({})
            check(
                'the stored key backs an empty request',
                result.get('success') is True and result['models'] == ['deepseek-v4-flash'],
                str(result),
            )
            check(
                'the known-context map ships with the models',
                result['known_models'].get('deepseek-v4-flash') is not None,
            )

            GameSetting.delete_key(SETTINGS_KEY)
            result = settings_service.fetch_deepseek_models({})
            check(
                'no key anywhere refuses the fetch',
                result.get('success') is False,
            )

            # ===== budgets follow the provider =====
            print('\n-- context budgets follow the provider --')
            from backend.game.utils.context_limits import get_context_size_tokens

            GameSetting.set(
                SETTINGS_KEY,
                {
                    'provider': 'deepseek',
                    'deepseek': {
                        'api_key': TEST_API_KEY,
                        'model': 'deepseek-v4-flash',
                        'context_window': 2_000_000,
                    },
                },
            )
            check(
                'deepseek active: budgets use the saved window',
                get_context_size_tokens() == 2_000_000,
                str(get_context_size_tokens()),
            )

            GameSetting.set(SETTINGS_KEY, {'provider': 'local'})
            check(
                'local active: budgets use the env window',
                get_context_size_tokens() == int(os.environ.get('LLM_CONTEXT_SIZE', '1000000')),
                str(get_context_size_tokens()),
            )

        finally:
            deepseek.requests = real_requests_module
            GameSetting.delete_key(SETTINGS_KEY)
            set_env('LLM_CONTEXT_SIZE', original_context_size)

    print('\n' + '=' * 50)
    print(f'PASSED: {PASSED}  FAILED: {FAILED}')
    return FAILED


if __name__ == '__main__':
    raise SystemExit(main())
