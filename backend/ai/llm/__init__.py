# LLM Module Package - CLEAN INTERFACE
# Exports core LLM functionality with simplified architecture

print(f"🔍 Loading {__file__.split('LlmMonsterHunter', 1)[-1]}")

# Core model operations
from .core import unload_model, warm_up_model

# Prompt management
from .prompt_engine import build_prompt, get_template_config

__all__ = [
    # Core model operations
    'unload_model',
    'warm_up_model',
    'get_template_config',
    'build_prompt'
]
