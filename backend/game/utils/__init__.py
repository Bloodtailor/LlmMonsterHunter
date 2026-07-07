# Game Utils Package - UPDATED: Cleaned up exports
# Now only exports public interface functions
# Private prompt helpers are no longer exposed

print(f"🔍 Loading {__file__.split('LlmMonsterHunter', 1)[-1]}")
from backend.core.config.comfyui_config import IMAGE_GENERATION_ENABLED

from .context_limits import clamp_context, get_block_char_limit
from .prompt_helpers import build_and_generate, build_and_stream

__all__ = [
    'IMAGE_GENERATION_ENABLED',
    'build_and_generate',
    'build_and_stream',
    'clamp_context',
    'get_block_char_limit',
]
