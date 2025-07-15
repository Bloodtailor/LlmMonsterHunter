#!/usr/bin/env python3
"""
Basic Backend Interactive Setup Flow
Diagnostic flow for fundamental environment problems
"""
COMPONENT_NAME = "Basic Backend"

from setup.utils.ux_utils import *
from setup.checks.basic_backend_checks import (
    check_python_version,
    check_pip,
    check_network_access,
    check_virtual_environment,
    check_basic_dependencies,
    check_env_file
)

def run_basic_backend_interactive_setup(current=None, total=None, dry_run=False):
    """
    Interactive setup flow for basic backend components
    
    Returns:
        bool: True if user wants to continue, False to exit
    """
    
    # ================================================================
    # SECTION 1: INITIAL STATUS CHECK AND DISPLAY
    # ================================================================

    # Show clean component header
    show_component_header(
        component_name=COMPONENT_NAME,
        current=current,
        total=total,
        description="Python virtual environment and basic dependencies"
    )

    print("Checking current status...")
    
    # Run individual checks
    python_ok, python_message = check_python_version()
    pip_ok, pip_message = check_pip()
    network_ok, network_message = check_network_access()
    venv_ok, venv_message = check_virtual_environment()
    deps_ok, deps_message = check_basic_dependencies()
    env_ok, env_message = check_env_file()

    # Dry run mode - hardcoded scenario
    if dry_run:
        print_dry_run_header()
        # Scenario: Python and pip work, but everything else is missing
        python_ok, python_message = True, "Python 3.11.5 is adequate"
        pip_ok, pip_message = True, "pip available: pip 23.2.1"
        network_ok, network_message = True, "Network access to PyPI confirmed"
        venv_ok, venv_message = False, "Virtual environment not found at venv"
        deps_ok, deps_message = False, "Virtual environment pip not found"
        env_ok, env_message = False, ".env file not found"

    # Package results for display
    check_results = {
        "Python Version": (python_ok, python_message),
        "pip Package Manager": (pip_ok, pip_message),
        "Network Access": (network_ok, network_message),
        "Virtual Environment": (venv_ok, venv_message),
        "Basic Dependencies": (deps_ok, deps_message),
        "Environment File": (env_ok, env_message)
    }

    # Display results beautifully
    overall_ok = display_check_results("BASIC BACKEND", check_results)

    # ================================================================
    # SECTION 2: INTERACTIVE SETUP LOGIC
    # ================================================================

    # If everything is working, we shouldn't be here
    if overall_ok:
        print("All basic backend components are ready!")
        print("This interactive setup shouldn't have been needed.")
        print()
        return True
    
    # Show diagnostic message
    show_message('basic_backend_diagnostic')
    
    # Ask user if they want to continue despite problems
    if not prompt_user_confirmation("Do you want to continue setup anyway? [y/N]: "):
        print()
        print("Exiting setup to fix basic backend issues...")
        print("Please resolve the above problems and run setup again.")
        print()
        import sys
        sys.exit(0)
    
    # User chose to continue despite problems
    print()
    print_continue("Continuing with basic backend issues...")
    print("You brave, brave soul.")
    print()
    
    return True

if __name__ == "__main__":
    from setup.utils.dry_run_utils import run_as_standalone_component
    run_as_standalone_component(COMPONENT_NAME, run_basic_backend_interactive_setup)