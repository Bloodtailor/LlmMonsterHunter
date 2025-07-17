# Game Utils Package - SIMPLIFIED: Removed Validators
# Validators moved to backend/services/validators.py where they belong
# Common utilities for game logic
print(f"🔍 Loading {__file__}")
from backend.core.config.comfyui_config import IMAGE_GENERATION_ENABLED
from .prompt_helpers import build_game_prompt, make_generation_request, build_and_generate
from backend.core.utils import (
    success_response, error_response, check_and_return, validate_and_continue,
    print_success, print_error, print_warning, print_info
)


__all__ = [
    'IMAGE_GENERATION_ENABLED',
    'build_game_prompt',
    'make_generation_request',
    'build_and_generate',
    'success_response',
    'error_response', 
    'check_and_return',
    'validate_and_continue',
    'print_success',
    'print_error',
    'print_warning',
    'print_info'
]