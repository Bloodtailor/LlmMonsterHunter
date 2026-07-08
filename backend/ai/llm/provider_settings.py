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
# a gate, and new models work the day they ship. (The legacy 128K ids -
# deepseek-chat / deepseek-reasoner - fell below the context floor, and
# DeepSeek removes them 2026-07-24; a saved row pointing at one resolves
# local until its owner re-picks a model.)
DEEPSEEK_KNOWN_CONTEXT_WINDOWS = {
    'deepseek-v4-flash': 1_000_000,
    'deepseek-v4-pro': 1_000_000,
}

# THE HARD FLOOR (locked decision, docs/plans/cloud-generation.md):
# models with less than 1M tokens of context are unsupported - the panel
# refuses smaller windows outright. Sub-1M local GGUFs configured in .env
# remain a use-at-your-own-risk escape hatch; prompt budgets stay sane
# there because they are absolute token caps under a 70% ceiling either
# way (context_limits.py).
MIN_CONTEXT_WINDOW = 1_000_000


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

    # A pre-floor row (a saved sub-1M window, or a removed legacy model
    # with no supported size on record): the local floor holds until the
    # panel re-picks a 1M-class model. Budgeting a 700K-token prompt for
    # a 128K model is the one thing this resolver must never do.
    if not context_window:
        return _local_settings()

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


def _deepseek_context_window(deepseek: dict[str, Any], model: str) -> Optional[int]:
    """Stored value first, known-model map second - but NOTHING below the
    hard floor. None means 'no supported window': the caller falls back
    to local rather than trusting a stale sub-1M row."""
    stored = deepseek.get('context_window')

    try:
        if stored and int(stored) >= MIN_CONTEXT_WINDOW:
            return int(stored)
    except (TypeError, ValueError):
        pass

    known = DEEPSEEK_KNOWN_CONTEXT_WINDOWS.get(model)
    if known and known >= MIN_CONTEXT_WINDOW:
        return known
    return None


def _env_context_size() -> int:
    return int(os.getenv('LLM_CONTEXT_SIZE', '1000000'))
