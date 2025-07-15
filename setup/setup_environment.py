#!/usr/bin/env python3
"""
Monster Hunter Game - Interactive Environment Setup
Walks user through setting up missing requirements
"""

import sys
from setup.check_requirements import check_requirements
from setup.checks import COMPONENT_CHECKS, run_all_checks
from setup.flows import COMPONENT_FLOWS
from setup.utils.ux_utils import (
    print_header, show_status_table, print_success, print_error, print_warning, 
    print_info, print_continue, prompt_user_confirmation
)

def auto_setup_basic_backend():
    """Perform automatic installation of basic requirements that do not require user attention"""

    from setup.flows.basic_backend_flow import auto_setup_basic_backend 
    auto_setup_basic_backend()

def main_interactive_setup(dry_run=False):
    """Interactive setup for missing requirements."""
    print_header("Interactive Environment Setup")
    print("This will help you set up missing requirements for Monster Hunter Game.")
    print("You'll be asked before each setup step.")
    print()
    
    # Get the list of components in setup order
    component_names = list(COMPONENT_FLOWS.keys())
    total_components = len(component_names)
    
    for current, component_name in enumerate(component_names, 1):
        
        # Check if already working
        check_function = COMPONENT_CHECKS[component_name]
        try:
            is_working = check_function()
            if is_working and not dry_run:
                print_success(f"{component_name} is already working correctly.")
                continue
        except Exception as e:
            print_error(f"Error checking {component_name}: {e}")
        
        # Ask user if they want to set this up
        print(f"\n{component_name} needs to be set up. (component {current} of {total_components})")
        if prompt_user_confirmation(f"Do you want to set up {component_name} now? [Y/n]: "):
            try:
                print()
                print(f"\nSetting up {component_name}...")
                
                # Run the interactive setup flow
                setup_function = COMPONENT_FLOWS[component_name]
                result = setup_function(current=current, total=total_components, dry_run=dry_run)
                
                if result:
                    print_success(f"{component_name} setup completed successfully.")
                else:
                    print(f"❌ {component_name} setup failed.")
            except Exception as e:
                print()
                print_error(f"Error during {component_name} setup: {e}")
                
            input("Press Enter to continue...")
        else:
            print()
            print_continue(f"Skipping {component_name} setup.")
 
    
    # Final summary  
    print()
    if prompt_user_confirmation(f"Would you like to recheck requirments? [Y/n]: "):
        check_requirements()

if __name__ == "__main__":
    if len(sys.argv) > 1 and sys.argv[1] == "auto":
        auto_setup_basic_backend()
    else:
        from setup.utils.dry_run_utils import run_as_standalone_component
        run_as_standalone_component("Setup Environment", main_interactive_setup)