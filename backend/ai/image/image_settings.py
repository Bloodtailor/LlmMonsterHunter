# Image Provider Settings - whether and how card art gets painted
# Mirrors the LLM provider seam (ai/llm/provider_settings.py): the
# in-game panel writes one game_settings row; this module reads it per
# call, so a panel save applies to the very next paint with no restart.
# There is NO env floor here - unconfigured means image generation is
# OFF, and art is a bonus the game fully supports living without (the
# old ENABLE_IMAGE_GENERATION env switch retired with ComfyUI).

from typing import Any, Optional

from backend.core.config.image_config import DEFAULT_IMAGE_MODEL

SETTINGS_KEY = 'image_provider'

PROVIDER_GEMINI = 'gemini'
VALID_IMAGE_PROVIDERS = (PROVIDER_GEMINI,)


def resolve_image_settings() -> dict[str, Any]:
    """
    The active image-generation configuration.

    Returns:
        dict: {
            'enabled': bool,     # row says on AND a key exists
            'provider': 'gemini',
            'api_key': str | None,
            'model': str,        # saved pick or the code default
        }
    """
    saved = get_saved_settings() or {}
    api_key = (saved.get('api_key') or '').strip() or None
    model = (saved.get('model') or '').strip() or DEFAULT_IMAGE_MODEL
    enabled = bool(saved.get('enabled')) and bool(api_key)

    return {
        'enabled': enabled,
        'provider': PROVIDER_GEMINI,
        'api_key': api_key,
        'model': model,
    }


def get_saved_settings() -> Optional[dict[str, Any]]:
    """The raw game_settings row value, or None when anything at all is
    missing (row, table, app context) - callers never see the difference"""
    try:
        from backend.models.game_setting import GameSetting

        saved = GameSetting.get(SETTINGS_KEY)
        return saved if isinstance(saved, dict) else None
    except Exception:
        # No app context / no table yet / DB down: art simply stays off
        return None


def is_image_generation_enabled() -> bool:
    """The one question most callers ask"""
    return resolve_image_settings()['enabled']
