"""
Utils Package
Shared utility functions for setup system
"""

from .dry_run_utils import run_as_standalone_component, set_dry_run
from .env_utils import (
    create_env_file_from_template,
    env_file_exists,
    load_env_config,
    update_env_config,
    validate_env_keys,
)
from .ux_utils import (
    display_check_results,
    handle_user_choice,
    print_continue,
    print_dry_run,
    print_dry_run_header,
    print_error,
    print_info,
    print_success,
    print_warning,
    prompt_continue_or_skip,
    prompt_user_confirmation,
    show_component_header,
    show_component_status_table,
    show_message,
    show_message_and_wait,
    show_status_table,
)

__all__ = [
    # Environment utilities
    'env_file_exists',
    'load_env_config',
    'validate_env_keys',
    'update_env_config',
    'create_env_file_from_template',

    # UX utilities
    'show_status_table',
    'show_component_status_table',
    'show_message',
    'show_message_and_wait',
    'show_component_header',
    'display_check_results',
    'print_error',
    'print_warning',
    'print_success',
    'print_continue',
    'print_info',
    'print_dry_run',
    'print_dry_run_header',
    'handle_user_choice',
    'prompt_continue_or_skip',
    'prompt_user_confirmation',

    # Dry run utilities
    'set_dry_run',
    'run_as_standalone_component'
]
