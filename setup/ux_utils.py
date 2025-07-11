#!/usr/bin/env python3
"""
UX Utilities for Setup System
Provides shared utility functions for consistent, scannable user experience
"""

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
    print("│                      SYSTEM STATUS                         │")
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
        line = f"│  {icon} {component_name:<25} {status:<31} │"
        print(line)
    
    # Summary footer
    print("├─────────────────────────────────────────────────────────────┤")
    print(f"│  STATUS: {ready_components}/{total_components} components ready{' ' * (35 - len(str(ready_components)) - len(str(total_components)))}│")
    print("└─────────────────────────────────────────────────────────────┘")
    print()
    
    return ready_components, total_components

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
        print("================================================================")
        print(f"                    INTERACTIVE SETUP ({current}/{total})".center(64))
        print("================================================================")
    else:
        print("================================================================")
        print(f"                    COMPONENT SETUP".center(64))
        print("================================================================")
    
    print()
    print(f"🔧 SETTING UP: {component_name}")
    print()
    
    # Description if provided
    if description:
        print(description)
        print()

