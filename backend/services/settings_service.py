# Settings Service - TRUST BOUNDARY for the in-game settings panel
# Validates panel input and shapes safe responses. The DeepSeek and
# Gemini API keys are WRITE-ONLY through this layer: reads carry
# has_api_key + the last four characters, never the key itself, and a
# save with a blank key field keeps the stored key (the panel has
# nothing real to echo back).

import os
from pathlib import Path
from typing import Any, Optional

from backend.core.utils import error_response, success_response


def get_llm_settings() -> dict[str, Any]:
    """The panel's read: active provider, local model status (read-only in
    v1 - .env owns it), masked DeepSeek config, and the known-models map
    the panel uses to auto-fill context windows."""
    try:
        from backend.ai.llm.core import get_model_status
        from backend.ai.llm.provider_settings import (
            DEEPSEEK_KNOWN_CONTEXT_WINDOWS,
            MIN_CONTEXT_WINDOW,
            PROVIDER_LOCAL,
            get_saved_settings,
        )

        saved = get_saved_settings() or {}
        deepseek = saved.get('deepseek') or {}
        api_key = deepseek.get('api_key') or ''

        model_path = os.getenv('LLM_MODEL_PATH')
        model_status = get_model_status()

        return success_response(
            {
                'provider': saved.get('provider') or PROVIDER_LOCAL,
                'local': {
                    'configured': bool(model_path),
                    'model_file': Path(model_path).name if model_path else None,
                    'loaded': bool(model_status.get('loaded')),
                    'error': model_status.get('error'),
                    'context_size': int(os.getenv('LLM_CONTEXT_SIZE', '1000000')),
                    'gpu_layers': int(os.getenv('LLM_GPU_LAYERS', '35')),
                },
                'deepseek': {
                    'has_api_key': bool(api_key),
                    'api_key_last4': api_key[-4:] if api_key else None,
                    'model': deepseek.get('model'),
                    'context_window': deepseek.get('context_window'),
                },
                'known_models': DEEPSEEK_KNOWN_CONTEXT_WINDOWS,
                'min_context_window': MIN_CONTEXT_WINDOW,
            }
        )

    except Exception as e:
        return error_response(str(e))


def update_llm_settings(payload: dict[str, Any]) -> dict[str, Any]:
    """
    Validate and persist the panel's save.

    Rules (locked decisions, docs/plans/game-settings.md):
    - provider must be 'local' or 'deepseek'
    - DeepSeek fields may be saved while staying on local (paste the key
      now, switch later), but each field given must be valid
    - switching TO deepseek requires a complete config: key
      (stored-or-provided), model, and a context window (auto-filled from
      the known-models map when the model is recognized)
    """
    payload = payload or {}

    try:
        from backend.ai.llm.provider_settings import (
            DEEPSEEK_KNOWN_CONTEXT_WINDOWS,
            MIN_CONTEXT_WINDOW,
            PROVIDER_DEEPSEEK,
            SETTINGS_KEY,
            VALID_PROVIDERS,
            get_saved_settings,
        )
        from backend.models.game_setting import GameSetting

        provider = payload.get('provider')
        if provider not in VALID_PROVIDERS:
            return error_response(
                f"Unknown provider '{provider}' - expected one of {', '.join(VALID_PROVIDERS)}"
            )

        stored = (get_saved_settings() or {}).get('deepseek') or {}
        incoming = payload.get('deepseek') or {}

        # Blank/absent key keeps the stored one - the panel never holds the
        # real key, so "unchanged" arrives as empty
        api_key = _clean_text(incoming.get('api_key')) or stored.get('api_key')
        model = _clean_text(incoming.get('model')) or stored.get('model')

        context_window, context_error = _resolve_context_window(
            incoming, stored, model, DEEPSEEK_KNOWN_CONTEXT_WINDOWS, MIN_CONTEXT_WINDOW
        )
        if context_error:
            return error_response(context_error)

        if provider == PROVIDER_DEEPSEEK:
            if not api_key:
                return error_response('Switching to DeepSeek needs an API key - paste one first')
            if not model:
                return error_response('Switching to DeepSeek needs a model - fetch or type one')
            if not context_window:
                return error_response(
                    f"'{model}' is not a model this game knows - set its context window manually"
                )

        new_value = {
            'provider': provider,
            'deepseek': {
                'api_key': api_key,
                'model': model,
                'context_window': context_window,
            },
        }

        if not GameSetting.set(SETTINGS_KEY, new_value):
            return error_response('Failed to save settings')

        # Echo the (masked) state the panel should now show
        current = get_llm_settings()
        if current.get('success'):
            current['message'] = 'Settings saved'
        return current

    except Exception as e:
        return error_response(str(e))


def fetch_deepseek_models(payload: dict[str, Any]) -> dict[str, Any]:
    """
    Live model list from DeepSeek, proxied so the key never round-trips
    the panel: the provided key wins, the stored key backs it up. The
    /models endpoint needs auth, so a successful fetch IS key validation.
    """
    payload = payload or {}

    try:
        from backend.ai.llm.provider_settings import (
            DEEPSEEK_KNOWN_CONTEXT_WINDOWS,
            get_saved_settings,
        )
        from backend.ai.llm.providers import deepseek

        stored = (get_saved_settings() or {}).get('deepseek') or {}
        api_key = _clean_text(payload.get('api_key')) or stored.get('api_key')
        if not api_key:
            return error_response('Paste a DeepSeek API key first')

        result = deepseek.list_models(api_key)
        if not result['success']:
            return error_response(result['error'])

        return success_response(
            {
                'models': result['models'],
                'known_models': DEEPSEEK_KNOWN_CONTEXT_WINDOWS,
                'key_valid': True,
            }
        )

    except Exception as e:
        return error_response(str(e))


def test_llm_generation() -> dict[str, Any]:
    """
    One tiny real generation through the normal gateway: it queues, it
    streams in the panel (with the model name in the title), and it lands
    in the developer log with prompt tokens. The whole path IS the test.
    """
    try:
        from backend.ai import gateway
        from backend.models.generation_log import GenerationLog

        result = gateway.text_generation_request(
            prompt=(
                'You are the storyteller of a monster-taming adventure. '
                'In one short, characterful sentence, announce that you are '
                'ready to referee.'
            ),
            prompt_type='settings',
            prompt_name='provider_test',
            max_tokens=48,
        )

        # Name the engine that answered from the log - the source of truth.
        # The queue worker wrote the token counts in ITS session while this
        # request's REPEATABLE READ snapshot was already open - end the
        # snapshot first or prompt_tokens reads as None
        from backend.models.core import db

        db.session.rollback()
        log = GenerationLog.query.get(result['generation_id'])
        llm_log = log.llm_log if log else None

        return success_response(
            {
                'text': result.get('text'),
                'provider': llm_log.provider if llm_log else None,
                'model_name': llm_log.model_name if llm_log else None,
                'prompt_tokens': llm_log.prompt_tokens if llm_log else None,
            }
        )

    except Exception as e:
        # Gateway raises on failed generations - the provider's mapped
        # message (401 bad key, 402 balance, ...) is exactly what the
        # panel should show
        return error_response(str(e))


# ===== IMAGES SECTION (docs/plans/cloud-generation.md: Gemini painter) =====


def get_image_settings() -> dict[str, Any]:
    """The Images section's read: enabled switch, masked key, model pick,
    and the code-default model for the picker's empty state."""
    try:
        from backend.ai.image.image_settings import get_saved_settings
        from backend.core.config.image_config import DEFAULT_IMAGE_MODEL

        saved = get_saved_settings() or {}
        api_key = saved.get('api_key') or ''

        return success_response(
            {
                'enabled': bool(saved.get('enabled')),
                'has_api_key': bool(api_key),
                'api_key_last4': api_key[-4:] if api_key else None,
                'model': saved.get('model') or None,
                'default_model': DEFAULT_IMAGE_MODEL,
            }
        )

    except Exception as e:
        return error_response(str(e))


def update_image_settings(payload: dict[str, Any]) -> dict[str, Any]:
    """
    Validate and persist the Images section's save (the LLM section's
    rules): a blank key keeps the stored one, fields may be saved while
    the switch stays off, and turning painting ON requires a key
    (stored-or-provided). A missing model falls back to the code default
    at resolve time.
    """
    payload = payload or {}

    try:
        from backend.ai.image.image_settings import SETTINGS_KEY, get_saved_settings
        from backend.models.game_setting import GameSetting

        stored = get_saved_settings() or {}

        api_key = _clean_text(payload.get('api_key')) or stored.get('api_key')
        model = _clean_text(payload.get('model')) or stored.get('model')
        enabled = bool(payload.get('enabled'))

        if enabled and not api_key:
            return error_response(
                'Turning image generation on needs a Gemini API key - paste one first'
            )

        new_value = {'enabled': enabled, 'api_key': api_key, 'model': model}
        if not GameSetting.set(SETTINGS_KEY, new_value):
            return error_response('Failed to save settings')

        current = get_image_settings()
        if current.get('success'):
            current['message'] = 'Settings saved'
        return current

    except Exception as e:
        return error_response(str(e))


def fetch_gemini_models(payload: dict[str, Any]) -> dict[str, Any]:
    """
    Live image-capable model list from Gemini, proxied so the key never
    round-trips the panel (the DeepSeek fetch precedent). The endpoint
    needs auth, so a successful fetch IS key validation.
    """
    payload = payload or {}

    try:
        from backend.ai.image import gemini
        from backend.ai.image.image_settings import get_saved_settings

        stored = get_saved_settings() or {}
        api_key = _clean_text(payload.get('api_key')) or stored.get('api_key')
        if not api_key:
            return error_response('Paste a Gemini API key first')

        result = gemini.list_models(api_key)
        if not result['success']:
            return error_response(result['error'])

        return success_response({'models': result['models'], 'key_valid': True})

    except Exception as e:
        return error_response(str(e))


def test_image_generation() -> dict[str, Any]:
    """
    One tiny real paint through the normal gateway: it queues, shows in
    the queue panel, lands in the developer log with its model, and
    files a real image the panel can show. The whole path IS the test.
    """
    try:
        from backend.ai import gateway

        result = gateway.image_generation_request(
            prompt_text=(
                'A small, friendly slime creature waving hello - a test '
                'illustration for a monster-taming game.'
            ),
            prompt_type='settings',
            prompt_name='image_provider_test',
        )

        return success_response(
            {
                'image_path': result.get('image_path'),
                'model_name': result.get('model_name'),
            }
        )

    except Exception as e:
        # Gateway raises on failures - the provider's mapped message
        # (401 bad key, 429 rate limit, ...) is exactly what the panel
        # should show
        return error_response(str(e))


def _clean_text(value: Any) -> Optional[str]:
    """Trimmed non-empty string, else None"""
    if isinstance(value, str) and value.strip():
        return value.strip()
    return None


def _resolve_context_window(
    incoming: dict[str, Any],
    stored: dict[str, Any],
    model: Optional[str],
    known_models: dict[str, int],
    minimum: int,
) -> tuple[Optional[int], Optional[str]]:
    """(window, error): explicit value first (validated), stored second,
    known-models auto-fill last. No value for an unknown model is only an
    error when switching to DeepSeek - the caller decides."""
    explicit = incoming.get('context_window')

    if explicit is not None and explicit != '':
        try:
            window = int(explicit)
        except (TypeError, ValueError):
            return None, f"Context window must be a whole number of tokens, got '{explicit}'"
        if window < minimum:
            return None, (
                f'Context window must be at least {minimum} tokens - '
                'the game reserves room for the model to answer'
            )
        return window, None

    # A stored window below the (raised) floor is treated as absent so a
    # pre-floor row self-heals through the known-models auto-fill on its
    # next save instead of re-persisting an unsupported size
    stored_window = stored.get('context_window')
    try:
        if stored_window and int(stored_window) >= minimum:
            return stored_window, None
    except (TypeError, ValueError):
        pass

    if model and model in known_models:
        return known_models[model], None

    return None, None
