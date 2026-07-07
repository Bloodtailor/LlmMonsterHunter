# Game Utils Package - UPDATED: Cleaned up exports
# Now only exports public interface functions
# Private prompt helpers are no longer exposed

print(f"🔍 Loading {__file__.split('LlmMonsterHunter', 1)[-1]}")
from backend.ai.image.image_settings import is_image_generation_enabled

from .context_limits import clamp_context, get_block_char_limit
from .prompt_helpers import build_and_generate, build_and_stream

__all__ = [
    'build_and_generate',
    'build_and_stream',
    'clamp_context',
    'get_block_char_limit',
    'is_image_generation_enabled',
]
