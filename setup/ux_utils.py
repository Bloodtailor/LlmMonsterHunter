#!/usr/bin/env python3
"""
UX Utilities for Setup System
Provides shared utility functions for consistent, scannable user experience
"""

import io
import contextlib

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

def show_instructions_and_wait(instructions, pause_message="Press Enter to continue..."):
    """
    Show instruction block and pause for user to read and act
    
    Args:
        instructions (list): List of instruction lines
        pause_message (str): Message to show before pausing
    """
    # Display all instruction lines
    for line in instructions:
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
    
    print("Checking current status...")
    
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

__all__ = [
    "show_status_table",
    "show_component_status_table",
    "show_instructions_and_wait",
    "show_component_header",
    "display_check_results",
    "print_error",
    "print_warning",
    "print_success",
    "print_continue",
    "print_info"
]
