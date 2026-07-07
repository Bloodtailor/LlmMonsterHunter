# LLM Provider Settings - which text engine speaks, resolved per request
# The in-game panel writes one game_settings row; this module reads it and
# merges it over .env. Local/env is the UNBREAKABLE FLOOR: a missing row,
# missing table, or missing app context resolves to the local model exactly
# as the game behaved before the settings panel existed. Resolution happens
# on every generation request (one tiny SELECT against seconds of LLM
# latency) so a settings save needs no cache invalidation and no restart.

import os
from pathlib import Path
from typing import Any, Optional

SETTINGS_KEY = 'llm_provider'

PROVIDER_LOCAL = 'local'
PROVIDER_DEEPSEEK = 'deepseek'
VALID_PROVIDERS = (PROVIDER_LOCAL, PROVIDER_DEEPSEEK)

# Context windows for the DeepSeek models we recognize. Their /models
# endpoint returns ids only - no sizes (verified July 2026) - so the panel
# auto-fills from this map and the player can ALWAYS override. Unknown
# models just need a manual value: entries here are a convenience, never
# a gate, and new models work the day they ship.
DEEPSEEK_KNOWN_CONTEXT_WINDOWS = {
    'deepseek-v4-flash': 1_000_000,
    'deepseek-v4-pro': 1_000_000,
    # Deprecated ids (removal 2026-07-24) kept so pre-deprecation saves
    # keep resolving until their owners re-pick a model
    'deepseek-chat': 128_000,
    'deepseek-reasoner': 128_000,
}

# context_limits.py reserves 1200 tokens for the model's answer; a window
# near that starves every prompt block to nothing, so the service refuses
# anything smaller than this.
MIN_CONTEXT_WINDOW = 2048


def resolve_llm_settings() -> dict[str, Any]:
    """
    The active text-generation configuration, DB row over env.

    Returns:
        dict: {
            'provider': 'local' | 'deepseek',
            'model_name': str | None,   # GGUF filename or DeepSeek model id
            'context_size': int,        # tokens - feeds prompt budgeting
            'deepseek': {'api_key', 'model', 'context_window'} | None,
        }
    """
    saved = get_saved_settings()

    if not saved or saved.get('provider') != PROVIDER_DEEPSEEK:
        return _local_settings()

    deepseek = saved.get('deepseek') or {}
    api_key = deepseek.get('api_key')
    model = deepseek.get('model')

    # A half-configured row (key without model, or vice versa) is not an
    # error state - the floor simply holds until the panel finishes the job
    if not api_key or not model:
        return _local_settings()

    context_window = _deepseek_context_window(deepseek, model)

    return {
        'provider': PROVIDER_DEEPSEEK,
        'model_name': model,
        'context_size': context_window,
        'deepseek': {
            'api_key': api_key,
            'model': model,
            'context_window': context_window,
        },
    }


def get_saved_settings() -> Optional[dict[str, Any]]:
    """The raw game_settings row value, or None when anything at all is
    missing (row, table, app context) - callers never see the difference"""
    try:
        from backend.models.game_setting import GameSetting

        saved = GameSetting.get(SETTINGS_KEY)
        return saved if isinstance(saved, dict) else None
    except Exception:
        # No app context / no table yet / DB down: the local floor holds
        return None


def should_apply_nothink_prefill(provider: str) -> bool:
    """
    The nothink prefill is a RAW-COMPLETION trick for local reasoning GGUFs
    (an empty <think> block glued onto the prompt). DeepSeek's chat API
    gets thinking disabled as a request parameter instead, and prefilling
    would pollute its prompt - so the prefill is local-only.
    """
    from backend.core.config.llm_config import get_disable_thinking

    return provider == PROVIDER_LOCAL and get_disable_thinking()


def _local_settings() -> dict[str, Any]:
    """The pre-initiative configuration, straight from .env"""
    model_path = os.getenv('LLM_MODEL_PATH')

    return {
        'provider': PROVIDER_LOCAL,
        'model_name': Path(model_path).name if model_path else None,
        'context_size': _env_context_size(),
        'deepseek': None,
    }


def _deepseek_context_window(deepseek: dict[str, Any], model: str) -> int:
    """Stored value first, known-model map second, env floor last"""
    stored = deepseek.get('context_window')

    try:
        if stored and int(stored) >= MIN_CONTEXT_WINDOW:
            return int(stored)
    except (TypeError, ValueError):
        pass

    return DEEPSEEK_KNOWN_CONTEXT_WINDOWS.get(model, _env_context_size())


def _env_context_size() -> int:
    return int(os.getenv('LLM_CONTEXT_SIZE', '4096'))
