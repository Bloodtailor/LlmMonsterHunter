# Gemini Image Provider Tests - OFFLINE (no network, test DB)
# Exercises Cgn-M2 (docs/plans/cloud-generation.md) with requests fully
# faked: interactions request shaping (geometry, reference blocks),
# response parsing (output_image + steps fallback), player-facing HTTP
# error mapping, list_models filtering, the image-settings row
# resolution, the gateway's enabled gate + byte-exact prompt composition
# + param stamping, sequential file numbering, and the legacy
# ComfyUI-outputs migration.
#
# Usage: python -m backend.tests.test_gemini_provider   (from project root)

import base64
import shutil
import tempfile
from pathlib import Path

import requests as real_requests

from backend.tests.harness import build_test_app

PASSED = 0
FAILED = 0

TEST_API_KEY = 'AIza-test-000000abcd1234'

PNG_BYTES = b'\x89PNG\r\n\x1a\n' + b'fake-png-payload'


def check(name: str, condition: bool, detail: str = ''):
    global PASSED, FAILED
    if condition:
        PASSED += 1
        print(f"  ✅ {name}")
    else:
        FAILED += 1
        print(f"  ❌ {name}{f' - {detail}' if detail else ''}")


class FakeResponse:
    def __init__(self, status_code=200, json_data=None):
        self.status_code = status_code
        self._json = json_data or {}

    def json(self):
        return self._json


class FakeRequests:
    """Stands in for the requests module inside the gemini provider.
    Real exception classes ride along so the provider's except clauses
    keep working."""

    exceptions = real_requests.exceptions

    def __init__(self, post_response=None, get_response=None):
        self.post_response = post_response
        self.get_response = get_response
        self.last_post = None
        self.last_get = None

    def post(self, url, headers=None, json=None, timeout=None):
        self.last_post = {'url': url, 'headers': headers, 'json': json}
        if isinstance(self.post_response, Exception):
            raise self.post_response
        return self.post_response

    def get(self, url, headers=None, params=None, timeout=None):
        self.last_get = {'url': url, 'headers': headers, 'params': params}
        if isinstance(self.get_response, Exception):
            raise self.get_response
        return self.get_response


def _happy_payload():
    return {
        'id': 'interaction-1',
        'output_image': {
            'data': base64.b64encode(PNG_BYTES).decode('ascii'),
            'mime_type': 'image/png',
        },
    }


def main():
    global PASSED, FAILED
    PASSED = 0
    FAILED = 0

    from backend.ai.image import gemini, paths, processor
    from backend.ai.image.image_settings import SETTINGS_KEY, resolve_image_settings

    print('🧪 GEMINI IMAGE PROVIDER TESTS')
    print('=' * 50)

    app = build_test_app()

    with app.app_context():
        from backend.models.core import create_tables
        from backend.models.game_setting import GameSetting

        create_tables()

        real_requests_module = gemini.requests

        try:
            # ===== request shaping =====
            print('\n-- request shaping --')
            fake = FakeRequests(post_response=FakeResponse(json_data=_happy_payload()))
            gemini.requests = fake

            result = gemini.generate_image(
                prompt='A stone beetle guarding a cavern.',
                api_key=TEST_API_KEY,
                model='gemini-3.1-flash-image',
                aspect_ratio='2:3',
                resolution='1K',
                reference_images=[PNG_BYTES],
            )

            check('the generation succeeds', result['success'] is True, str(result.get('error')))
            check('the PNG bytes round-trip', result['image_bytes'] == PNG_BYTES)
            check(
                'the model name rides the result', result['model_name'] == 'gemini-3.1-flash-image'
            )
            check(
                'the interactions endpoint is the one called',
                fake.last_post['url'].endswith('/v1beta/interactions'),
                str(fake.last_post['url']),
            )
            check(
                'the key rides the x-goog-api-key header',
                fake.last_post['headers']['x-goog-api-key'] == TEST_API_KEY,
            )

            body = fake.last_post['json']
            check(
                'the prompt rides as the first input block',
                body['model'] == 'gemini-3.1-flash-image'
                and body['input'][0]
                == {'type': 'text', 'text': 'A stone beetle guarding a cavern.'},
            )
            check(
                'card geometry rides response_format',
                body['response_format']
                == {
                    'type': 'image',
                    'mime_type': 'image/png',
                    'aspect_ratio': '2:3',
                    'image_size': '1K',
                },
            )
            reference_block = body['input'][1]
            check(
                'the reference image rides as sniffed base64',
                reference_block['type'] == 'image'
                and reference_block['mime_type'] == 'image/png'
                and base64.b64decode(reference_block['data']) == PNG_BYTES,
            )

            # ===== response parsing =====
            print('\n-- response parsing --')
            steps_only = {
                'steps': [
                    {'type': 'tool_call', 'content': []},
                    {
                        'type': 'model_output',
                        'content': [
                            {'type': 'text', 'text': 'painting...'},
                            {
                                'type': 'image',
                                'data': base64.b64encode(PNG_BYTES).decode('ascii'),
                                'mime_type': 'image/png',
                            },
                        ],
                    },
                ]
            }
            gemini.requests = FakeRequests(post_response=FakeResponse(json_data=steps_only))
            result = gemini.generate_image(
                prompt='x', api_key=TEST_API_KEY, model='m', aspect_ratio='2:3', resolution='1K'
            )
            check(
                'interleaved steps output parses too (no output_image field)',
                result['success'] is True and result['image_bytes'] == PNG_BYTES,
                str(result.get('error')),
            )

            gemini.requests = FakeRequests(post_response=FakeResponse(json_data={'steps': []}))
            result = gemini.generate_image(
                prompt='x', api_key=TEST_API_KEY, model='m', aspect_ratio='2:3', resolution='1K'
            )
            check(
                'a response with no image fails instead of returning silence',
                result['success'] is False and 'no image' in result['error'],
                str(result.get('error')),
            )

            gemini.requests = FakeRequests(
                post_response=FakeResponse(json_data={'output_image': {'data': '!!!not-base64!!!'}})
            )
            result = gemini.generate_image(
                prompt='x', api_key=TEST_API_KEY, model='m', aspect_ratio='2:3', resolution='1K'
            )
            check('undecodable image data fails cleanly', result['success'] is False)

            # ===== error mapping =====
            print('\n-- error mapping --')
            for status, needle in (
                (401, 'API key'),
                (403, 'API key'),
                (429, 'rate limit'),
                (400, 'rejected the request'),
                (503, 'server error'),
            ):
                gemini.requests = FakeRequests(
                    post_response=FakeResponse(
                        status_code=status, json_data={'error': {'message': 'details'}}
                    )
                )
                result = gemini.generate_image(
                    prompt='x', api_key=TEST_API_KEY, model='m', aspect_ratio='2:3', resolution='1K'
                )
                check(
                    f'{status} maps to a player-facing message',
                    result['success'] is False and needle in result['error'],
                    str(result.get('error')),
                )

            gemini.requests = FakeRequests(
                post_response=real_requests.exceptions.ConnectionError('no route')
            )
            result = gemini.generate_image(
                prompt='x', api_key=TEST_API_KEY, model='m', aspect_ratio='2:3', resolution='1K'
            )
            check(
                'a network failure says so plainly',
                result['success'] is False and 'Could not reach Gemini' in result['error'],
            )

            # ===== list_models =====
            print('\n-- list_models --')
            fake = FakeRequests(
                get_response=FakeResponse(
                    json_data={
                        'models': [
                            {'name': 'models/gemini-3.1-flash-image'},
                            {'name': 'models/gemini-3.1-flash'},
                            {'name': 'models/gemini-2.5-flash-image'},
                            {'name': 'models/embedding-001'},
                        ]
                    }
                )
            )
            gemini.requests = fake
            result = gemini.list_models(TEST_API_KEY)
            check(
                'only image-capable ids reach the picker',
                result['success'] is True
                and result['models'] == ['gemini-3.1-flash-image', 'gemini-2.5-flash-image'],
                str(result['models']),
            )
            check('the models endpoint is the one called', fake.last_get['url'].endswith('/models'))

            gemini.requests = FakeRequests(
                get_response=FakeResponse(status_code=401, json_data={'error': {'message': 'bad'}})
            )
            result = gemini.list_models(TEST_API_KEY)
            check('a bad key fails the fetch with the mapped message', result['success'] is False)

            # ===== settings resolution =====
            print('\n-- image settings resolution --')
            GameSetting.delete_key(SETTINGS_KEY)
            resolved = resolve_image_settings()
            check(
                'no row means image generation is OFF (no env switch anymore)',
                resolved['enabled'] is False and resolved['model'] == 'gemini-3.1-flash-image',
            )

            GameSetting.set(
                SETTINGS_KEY,
                {'enabled': True, 'api_key': TEST_API_KEY, 'model': 'gemini-2.5-flash-image'},
            )
            resolved = resolve_image_settings()
            check(
                'a complete row enables painting with the saved model',
                resolved['enabled'] is True and resolved['model'] == 'gemini-2.5-flash-image',
            )

            GameSetting.set(SETTINGS_KEY, {'enabled': True, 'api_key': '', 'model': 'x'})
            check(
                'enabled without a key still resolves OFF',
                resolve_image_settings()['enabled'] is False,
            )

            GameSetting.set(SETTINGS_KEY, {'enabled': False, 'api_key': TEST_API_KEY})
            check(
                'a key with the switch off resolves OFF',
                resolve_image_settings()['enabled'] is False,
            )

            # ===== the gateway gate + stamping =====
            print('\n-- the gateway gate + stamping --')
            GameSetting.delete_key(SETTINGS_KEY)

            from backend.ai import gateway

            gate_message = ''
            try:
                gateway.image_generation_request(prompt_text='a beetle')
            except Exception as gate_error:
                gate_message = str(gate_error)
            check(
                'unconfigured image generation refuses at the gateway',
                'not configured' in gate_message,
                gate_message,
            )

            from backend.core.config.image_config import (
                AVOID_INSTRUCTION,
                HOUSE_STYLE_PROMPT,
                compose_image_prompt,
            )

            composed = compose_image_prompt('A stone beetle')
            check(
                'the prompt recipe is subject + house style + avoid instruction',
                composed.startswith('A stone beetle')
                and HOUSE_STYLE_PROMPT in composed
                and AVOID_INSTRUCTION in composed,
            )

            from backend.models.generation_log import GenerationLog

            stamped_log = GenerationLog.create_image_log(
                prompt_type='monster_card_art',
                prompt_name='card_art',
                prompt_text=composed,
                image_params={
                    'model': 'gemini-3.1-flash-image',
                    'aspect_ratio': '2:3',
                    'resolution': '1K',
                    'reference_images': ['monster_card_art/00000001.png'],
                },
            )
            check('the stamped log saves', bool(stamped_log.save()))
            try:
                fresh = GenerationLog.query.get(stamped_log.id)
                check(
                    'the model is stamped onto the image log',
                    fresh.image_log.model_name == 'gemini-3.1-flash-image',
                )
                check(
                    'params round-trip the JSON column',
                    fresh.image_log.get_params().get('reference_images')
                    == ['monster_card_art/00000001.png'],
                )
            finally:
                stamped_log.delete()  # cascade removes the image_log child

            # ===== file numbering + legacy migration =====
            print('\n-- outputs tree --')
            temp_root = Path(tempfile.mkdtemp())
            original_target = paths.IMAGE_OUTPUTS_DIR
            original_legacy = paths._LEGACY_OUTPUTS_DIR
            try:
                paths.IMAGE_OUTPUTS_DIR = temp_root / 'outputs'
                paths._LEGACY_OUTPUTS_DIR = temp_root / 'legacy'
                legacy_art = paths._LEGACY_OUTPUTS_DIR / 'monster_card_art'
                legacy_art.mkdir(parents=True)
                (legacy_art / '00000007.png').write_bytes(PNG_BYTES)

                root = paths.outputs_root()
                check(
                    'the legacy ComfyUI outputs tree migrates on first touch',
                    (root / 'monster_card_art' / '00000007.png').exists()
                    and not paths._LEGACY_OUTPUTS_DIR.exists(),
                )

                first = processor._save_image_bytes(PNG_BYTES, 'monster_card_art')
                check(
                    'sequential numbering continues after migrated art',
                    first == 'monster_card_art/00000008.png',
                    first,
                )
                second = processor._save_image_bytes(PNG_BYTES, 'monster_card_art')
                check(
                    'the counter keeps counting', second == 'monster_card_art/00000009.png', second
                )
            finally:
                paths.IMAGE_OUTPUTS_DIR = original_target
                paths._LEGACY_OUTPUTS_DIR = original_legacy
                shutil.rmtree(temp_root, ignore_errors=True)

            GameSetting.delete_key(SETTINGS_KEY)

        finally:
            gemini.requests = real_requests_module

    print('\n' + '=' * 50)
    print(f'PASSED: {PASSED}  FAILED: {FAILED}')
    return FAILED


if __name__ == '__main__':
    main()
