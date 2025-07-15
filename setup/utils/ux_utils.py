#!/usr/bin/env python3
"""
UX Utilities for Setup System
Provides shared utility functions for consistent, scannable user experience
"""

import io
import contextlib
from setup.user_messages import get_message

def print_header(text):
    """Print a formatted header."""
    print("\n" + "=" * 60)
    print(text.center(60))
    print("=" * 60)

def print_warning(message):
    """
    Display standardized warning message
    """
    
    print(f"⚠️  {message}")

def print_error(message):
    """
    Display standardized error message
    """

    print(f"❌  {message}")

def print_success(message):
    """Display standardized error message"""

    print(f"✅  {message}")

def print_continue(message):
    """Display standardized continue message for continuning onto next component"""

    print(f"⏭️   {message}")

def print_info(message):
    """Display standardized info message for instructions for the user or important information"""

    print(f"💡  {message}")

def print_dry_run(message):
    """
    Display standardized dry run message with color
    """
    # ANSI color codes: cyan text
    CYAN = '\033[96m'
    RESET = '\033[0m'
    
    print(f"{CYAN}{message}{RESET}")

def print_dry_run_header():
    """
    Display standardized header to identify a component is being run in dry run mode
    """
    
    print_dry_run("🧪 DRY RUN: Running as a dry run")

def show_status_table(components):
    """
    Display a clean status overview table for all components
    
    Args:
        components (dict or list): Component statuses
            - If dict: {"Component Name": True/False, ...}
            - If list: [("Component Name", True/False), ...]
    """
    
    # Convert list to dict if needed
    if isinstance(components, list):
        components = dict(components)
    
    # Calculate summary
    total_components = len(components)
    ready_components = sum(1 for status in components.values() if status)
    
    # Table header
    print()
    print("┌─────────────────────────────────────────────────────────────┐")
    print("│                      SYSTEM STATUS                          │")
    print("├─────────────────────────────────────────────────────────────┤")
    
    # Component rows
    for component_name, is_ready in components.items():
        if is_ready:
            status = "READY"
            icon = "✅"
        else:
            status = "NEEDS SETUP"
            icon = "❌"
        
        # Format: "  ✅ Component Name          READY                           │"
        line = f"│  {icon} {component_name:<30} {status:<24} │"
        print(line)
    
    # Summary footer
    print("├─────────────────────────────────────────────────────────────┤")
    print(f"│  STATUS: {ready_components}/{total_components} components ready{' ' * (33 - len(str(ready_components)) - len(str(total_components)))}│")
    print("└─────────────────────────────────────────────────────────────┘")
    print()
    
    return ready_components, total_components

def show_component_status_table(component_name, checks):
    """
    Display a clean status overview table for a specific component
    
    Args:
        component_name (text): in all caps for table header
        checks (dict or list): checks statuses
            - If dict: {"Check Name": True/False, ...}
            - If list: [("Check Name", True/False), ...]
    """
    
    # Convert list to dict if needed
    if isinstance(checks, list):
        checks = dict(checks)
    
    # Calculate summary
    total_checks = len(checks)
    ready_checks = sum(1 for status in checks.values() if status)
    
    # Table header
    print()
    print("┌─────────────────────────────────────────────────────────────┐")
    print(f"│                      {component_name} STATUS{' ' * (32 - len(str(component_name)))}│")
    print("├─────────────────────────────────────────────────────────────┤")
    
    # Component rows
    for check_name, is_ready in checks.items():
        if is_ready:
            status = "READY"
            icon = "✅"
        else:
            status = "NEEDS SETUP"
            icon = "❌"
        
        # Format: "  ✅ Component Name          READY                           │"
        line = f"│  {icon} {check_name:<30} {status:<24} │"
        print(line)
    
    # Summary footer
    print("├─────────────────────────────────────────────────────────────┤")
    print(f"│  STATUS: {ready_checks}/{total_checks} checks passed{' ' * (36 - len(str(ready_checks)) - len(str(total_checks)))}│")
    print("└─────────────────────────────────────────────────────────────┘")
    print()
    
    return ready_checks, total_checks

def show_message(message_key):
    """
    Show message for user to read
    """

    message = get_message(message_key)
    for line in message:
        print(line)

def show_message_and_wait(message_key, pause_message="Press Enter to continue..."):
    """
    Show message block and pause for user to read and act
    
    Args:
        message_key (key): Key to message in user_message.py
        pause_message (str): Message to show before pausing
    """
    # Display all message lines
    message = get_message(message_key)
    for line in message:
        print(line)
    
    print()
    input(pause_message)
    print()


def show_component_header(component_name, current=None, total=None, description=None):
    """
    Display standardized component setup header
    
    Args:
        component_name (str): Name of component being set up
        current (int, optional): Current component number
        total (int, optional): Total number of components
        description (str, optional): What this component does
    """
    # Main header with progress if provided
    if current is not None and total is not None:
        status = f" ({current}/{total})"
    else:
        status = ""

    print("================================================================")
    print(f"INTERACTIVE SETUP{status}: {component_name}".center(64))
    print("================================================================")
    
    # Description if provided
    if description:
        print(description)
    
    print()
    print()

def display_check_results(component_name, check_results):
    """
    Display check results beautifully
    
    Args:
        component_name (text): in all caps for table header
        check_results (dict): Dictionary of check results
            Format: {"Check Name": (success_bool, message_string)}
        
    Returns:
        bool: True if all checks passed, False otherwise
    """
    
    # Extract just the boolean results for the status table
    status_only = {name: result[0] for name, result in check_results.items()}
    
    # Show beautiful status table
    ready_count, total_count = show_component_status_table(component_name, status_only)
    
    # Show detailed messages
    print("📋 Details:")
    for check_name, (success, message) in check_results.items():
        print(f"   {check_name}: {message}")
    print()
    
    overall_ok = all(result[0] for result in check_results.values())
    return overall_ok

def handle_user_choice(custom_options, component_name="this component"):
    """
    Handle standard user choices with optional custom options
    
    Args:
        custom_options: List of tuples like [("I", "Get installation instructions"), ...]
        component_name: Name for messages like "MySQL"
        
    Returns:
        str: The choice letter (uppercased)

    Usage:
    choice = handle_user_choice([
        ("I", "Get CUDA toolkit installation instructions"),
        ("R", "Re-check installation")
    ], "CUDA toolkit setup")
    """
    
    while True:
        print("Choose how to proceed:")
        
        # Show custom options first
        for letter, description in custom_options:
            print(f"  [{letter.upper()}] {description}")
        
        # Show standard options
        print(f"  [S] Skip {component_name} setup for now (you can finish it later)")
        print(f"  [C] Continue {component_name} setup without resolving issue (not recommended)")
        print(f"  [E] Exit setup and try again later")
        print()
        
        # Build valid choices
        valid_choices = [letter.upper() for letter, _ in custom_options] + ['S', 'C', 'E']
        choice_str = "/".join(valid_choices)
        
        choice = input(f"Your choice [{choice_str}]: ").strip().upper()
        
        if choice in valid_choices:
            if choice == "S":
                print()
                print_continue("Continuing to other components...")
                print_info(f"Remember to come back and complete {component_name} setup later!")
                print()
                return "SKIP"
            elif choice == "C":
                print()
                print(f"Continuing {component_name} setup without resolving issue")
                print("This may cause problems later.")
                print()
                return "CONTINUE"
            elif choice == "E":
                print()
                print("Exiting setup...")
                print()
                import sys
                sys.exit(0)
            else:
                return choice
        else:
            print(f"Please enter one of: {choice_str}")
            print()

def prompt_continue_or_skip(component_name="this component"):
    """
    Prompt the user to decide whether to continue, skip, or exit a setup component.

    Args:
        component_name: Name for messages like "MySQL"

    Returns:
        bool: True if the user chooses to continue setup,
              False if the user chooses to skip.
              Exits the program if the user chooses to exit.
    """
    
    while True:
        print("Choose how to proceed:")
        
        # Show standard options
        print(f"  [S] Skip {component_name} setup for now (you can finish it later)")
        print(f"  [C] Continue {component_name} setup without resolving issue (not recommended)")
        print(f"  [E] Exit setup and try again later")
        print()
        
        choice = input("Your choice [S/C/E]: ").strip().upper()
        
        if choice in ['S', 'C', 'E']:
            if choice == "S":
                print()
                print_continue("Continuing to other components...")
                print_info(f"Remember to come back and complete {component_name} setup later!")
                print()
                return False
            elif choice == "C":
                print()
                print(f"Continuing {component_name} setup without resolving issue")
                print("This may cause problems later.")
                print()
                return True
            elif choice == "E":
                print()
                print("Exiting setup...")
                print()
                import sys
                sys.exit(0)
        else:
            print("Please enter S C or E")
            print()

def prompt_user_confirmation(message):
    """
    Prompt the user input yes or no.

    Returns:
        bool: True/False if the user chooses yes/no

    """
    
    while True:
        choice = input(message).strip().upper()
        
        if choice in ['Y', 'YES','N','NO']:
            if choice in ['Y', 'YES']:
                return True
            elif ['N','NO']:
                return False
        else:
            print("Please enter Y or N")
            print()
            
__all__ = [
    "show_status_table",
    "show_component_status_table",
    "show_message",
    "show_message_and_wait",
    "show_component_header",
    "display_check_results",
    "print_header",
    "print_error",
    "print_warning",
    "print_success",
    "print_continue",
    "print_info",
    "print_dry_run",
    "print_dry_run_header",
    "handle_user_choice",
    "prompt_continue_or_skip",
    "prompt_user_confirmation"
]
