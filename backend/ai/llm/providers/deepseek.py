# DeepSeek Provider - the cloud engine behind the provider seam
# Speaks DeepSeek's OpenAI-compatible chat completions API over plain
# requests (no SDK dependency): the whole game prompt rides as one user
# message, tokens stream back as SSE chunks, and stream_options'
# include_usage makes the final chunk carry EXACT prompt/completion
# token counts for the developer log. The MODEL was stamped into the log
# at request time and arrives as model_name; the API key is read from
# game_settings at call time (keys rotate freely and never belong in a
# log row).

import json
import time
from typing import Any, Callable, Optional

import requests

from backend.core.config.llm_config import get_timeout

DEEPSEEK_BASE_URL = 'https://api.deepseek.com'
CONNECT_TIMEOUT_SECONDS = 10
MODELS_READ_TIMEOUT_SECONDS = 30

# Params DeepSeek's chat API understands. Everything else in the logged
# inference params (top_k, repeat_penalty, mirostat family, tfs_z,
# typical_p, seed, echo) is llama-cpp-only and is dropped in translation.
TRANSLATED_PARAMS = ('max_tokens', 'temperature', 'top_p', 'frequency_penalty', 'presence_penalty')

# The one legacy id that IS thinking mode by definition (an alias of
# v4-flash thinking until its 2026-07-24 removal) - disabling thinking on
# it would contradict what the player asked for by picking it
THINKING_MODEL_IDS = ('deepseek-reasoner',)


def generate_streaming(
    prompt: str,
    callback: Optional[Callable[[str], None]] = None,
    model_name: Optional[str] = None,
    **params,
) -> dict[str, Any]:
    """The provider contract, spoken by the DeepSeek API"""
    start_time = time.time()

    api_key = _stored_api_key()
    if not api_key:
        return _failure('DeepSeek API key is not configured - add one in Settings', start_time)

    model = model_name or _stored_model()
    if not model:
        return _failure('No DeepSeek model configured - pick one in Settings', start_time)

    try:
        response = requests.post(
            f'{DEEPSEEK_BASE_URL}/chat/completions',
            headers={'Authorization': f'Bearer {api_key}', 'Content-Type': 'application/json'},
            json=_request_body(prompt, model, params),
            stream=True,
            timeout=(CONNECT_TIMEOUT_SECONDS, get_timeout()),
        )
    except requests.exceptions.RequestException as request_error:
        return _failure(f'Could not reach DeepSeek: {request_error}', start_time)

    if response.status_code != 200:
        error_message = _map_http_error(response)
        response.close()
        return _failure(error_message, start_time)

    accumulated_text = ''
    content_chunk_count = 0
    usage = None

    if callback:
        callback('')

    # A dropped connection mid-stream keeps whatever arrived (mirroring
    # the local provider's stream loop) - an empty result still fails
    try:
        for line in response.iter_lines(decode_unicode=True):
            if not line or not line.startswith('data:'):
                continue

            payload = line[len('data:') :].strip()
            if payload == '[DONE]':
                break

            try:
                chunk = json.loads(payload)
            except json.JSONDecodeError:
                continue

            # The extra final chunk (stream_options.include_usage) carries
            # the exact token counts - remember it whenever it appears
            if chunk.get('usage'):
                usage = chunk['usage']

            choices = chunk.get('choices') or []
            if not choices:
                continue

            delta = choices[0].get('delta') or {}

            # Thinking-mode deltas narrate reasoning in reasoning_content -
            # never game text, so only content reaches the story
            content = delta.get('content')
            if content:
                accumulated_text += content
                content_chunk_count += 1
                if callback:
                    callback(accumulated_text)
    except Exception:
        pass
    finally:
        response.close()

    if not accumulated_text:
        return _failure('DeepSeek returned no text', start_time)

    if callback:
        callback(accumulated_text)

    duration = time.time() - start_time
    completion_tokens = (usage or {}).get('completion_tokens') or content_chunk_count
    tokens_per_second = completion_tokens / duration if duration > 0 else 0

    return {
        'success': True,
        'error': None,
        'text': accumulated_text,
        'tokens': completion_tokens,
        'prompt_tokens': (usage or {}).get('prompt_tokens'),
        'model_name': model,
        'duration': duration,
        'tokens_per_second': round(tokens_per_second, 2),
    }


def list_models(api_key: str) -> dict[str, Any]:
    """
    Live model ids from GET /models - the reason new DeepSeek models work
    the day they ship. Needs auth, so a successful fetch IS key validation.
    """
    try:
        response = requests.get(
            f'{DEEPSEEK_BASE_URL}/models',
            headers={'Authorization': f'Bearer {api_key}'},
            timeout=(CONNECT_TIMEOUT_SECONDS, MODELS_READ_TIMEOUT_SECONDS),
        )
    except requests.exceptions.RequestException as request_error:
        return {
            'success': False,
            'error': f'Could not reach DeepSeek: {request_error}',
            'models': [],
        }

    if response.status_code != 200:
        return {'success': False, 'error': _map_http_error(response), 'models': []}

    try:
        data = response.json().get('data') or []
    except ValueError:
        return {
            'success': False,
            'error': 'DeepSeek returned an unreadable model list',
            'models': [],
        }

    models = [entry.get('id') for entry in data if entry.get('id')]
    return {'success': True, 'error': None, 'models': models}


def _request_body(prompt: str, model: str, params: dict[str, Any]) -> dict[str, Any]:
    """Translate the logged llama-style params into a chat completion"""
    body = {
        'model': model,
        'messages': [{'role': 'user', 'content': prompt}],
        'stream': True,
        'stream_options': {'include_usage': True},
    }

    for name in TRANSLATED_PARAMS:
        if params.get(name) is not None:
            body[name] = params[name]

    stop_sequences = params.get('stop')
    if stop_sequences:
        body['stop'] = stop_sequences

    # The game wants fast structured output, not chains of thought
    # (locked decision 7, docs/plans/game-settings.md)
    if model not in THINKING_MODEL_IDS:
        body['thinking'] = {'type': 'disabled'}

    return body


def _map_http_error(response) -> str:
    """HTTP status → a message the settings panel can show a player"""
    try:
        detail = (response.json().get('error') or {}).get('message') or ''
    except Exception:
        detail = ''

    status = response.status_code
    if status == 401:
        base = 'DeepSeek rejected the API key (401) - check it in Settings'
    elif status == 402:
        base = 'DeepSeek account balance is empty (402) - top up to keep playing'
    elif status == 429:
        base = 'DeepSeek rate limit hit (429) - give it a moment and try again'
    elif status == 400:
        base = 'DeepSeek rejected the request (400)'
    elif status >= 500:
        base = f'DeepSeek server error ({status}) - try again shortly'
    else:
        base = f'DeepSeek returned HTTP {status}'

    return f'{base}: {detail}' if detail else base


def _stored_api_key() -> Optional[str]:
    """The key from game_settings - read at call time, NOT stamp time, so
    a rotated key applies to already-queued work and never touches a log"""
    from backend.ai.llm.provider_settings import get_saved_settings

    saved = get_saved_settings() or {}
    deepseek = saved.get('deepseek') or {}
    return deepseek.get('api_key') or None


def _stored_model() -> Optional[str]:
    from backend.ai.llm.provider_settings import get_saved_settings

    saved = get_saved_settings() or {}
    deepseek = saved.get('deepseek') or {}
    return deepseek.get('model') or None


def _failure(error_message: str, start_time: float) -> dict[str, Any]:
    return {
        'success': False,
        'error': error_message,
        'text': None,
        'tokens': 0,
        'prompt_tokens': None,
        'model_name': None,
        'duration': time.time() - start_time,
        'tokens_per_second': 0,
    }
