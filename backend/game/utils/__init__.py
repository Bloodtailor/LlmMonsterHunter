# Game Utils Package - SIMPLIFIED: Removed Validators
# Validators moved to backend/services/validators.py where they belong
# Common utilities for game logic

from .prompt_helpers import build_game_prompt, make_generation_request, build_and_generate
from backend.utils import (
    success_response, error_response, check_and_return, validate_and_continue,
    print_success, print_error, print_warning, print_info
)

__all__ = [
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