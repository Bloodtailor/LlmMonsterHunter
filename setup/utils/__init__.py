"""
Utils Package
Shared utility functions for setup system
"""

from .env_utils import (
    env_file_exists,
    load_env_config,
    validate_env_keys,
    update_env_config,
    create_env_file_from_template
)

from .ux_utils import (
    show_status_table,
    show_component_status_table,
    show_message,
    show_message_and_wait,
    show_component_header,
    display_check_results,
    print_error,
    print_warning,
    print_success,
    print_continue,
    print_info,
    print_dry_run,
    print_dry_run_header,
    handle_user_choice,
    prompt_continue_or_skip,
    prompt_user_confirmation
)

from .dry_run_utils import (
    set_dry_run,
    run_as_standalone_component
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