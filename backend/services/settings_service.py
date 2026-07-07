# Settings Service - TRUST BOUNDARY for the in-game settings panel
# Validates panel input and shapes safe responses. The DeepSeek API key is
# WRITE-ONLY through this layer: reads carry has_api_key + the last four
# characters, never the key itself, and a save with a blank key field
# keeps the stored key (the panel has nothing real to echo back).

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
                    'context_size': int(os.getenv('LLM_CONTEXT_SIZE', '4096')),
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
                    f"'{model}' is not a model this game knows - "
                    'set its context window manually'
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

    if stored.get('context_window'):
        return stored['context_window'], None

    if model and model in known_models:
        return known_models[model], None

    return None, None
