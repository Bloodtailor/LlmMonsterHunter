#!/usr/bin/env python3
"""
Monster Hunter Game - Interactive Environment Setup
Walks user through setting up missing requirements.

Default run covers only what the API-first game needs (Python env,
Node, MySQL, database). The unsupported local-LLM escape hatch
(GPU/CUDA/Build Tools/GGUF model) is developer-facing and only runs
with --local-extras - a new player never sees that vocabulary.
"""

import sys

from setup.check_requirements import check_requirements
from setup.checks import COMPONENT_CHECKS, run_component_diagnostic
from setup.components import components_for
from setup.flows import COMPONENT_FLOWS
from setup.utils.ux_utils import (
    print_continue,
    print_error,
    print_header,
    print_success,
    prompt_user_confirmation,
)


def auto_setup_basic_backend():
    """Perform automatic installation of basic requirements that do not require user attention"""

    from setup.flows.basic_backend_flow import auto_setup_basic_backend

    return auto_setup_basic_backend()


def main_interactive_setup(dry_run=False, include_local_extras=False):
    """Interactive setup for missing requirements."""
    print_header("Interactive Environment Setup")
    print("This will help you set up missing requirements for Monster Hunter Game.")
    print("You'll be asked before each setup step.")
    print()

    # Get the list of components in setup order
    component_names = list(components_for(include_local_extras))
    total_components = len(component_names)

    for current, component_name in enumerate(component_names, 1):
        # Check if already working
        check_function = COMPONENT_CHECKS[component_name]
        try:
            is_working = check_function()
            if is_working and not dry_run:
                continue
        except Exception as e:
            print_error(f"\nError checking {component_name}: {e}\n")

        # Ask user if they want to set this up
        print(
            f"\n{component_name} needs to be set up. (component {current} of {total_components})\n"
        )
        run_component_diagnostic(component_name)

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

            print()
            print_header(f"{component_name} setup complete!")
            print()
            input("Press Enter to continue to the next component...")
        else:
            print()
            print_continue(f"Skipping {component_name} setup.")

    # Final summary
    print()
    print_header("Interactive Environment Setup: FINISHED")
    print()
    if prompt_user_confirmation("Would you like to recheck requirments before exiting? [Y/n]: "):
        check_requirements(include_local_extras=include_local_extras)


if __name__ == "__main__":
    args = sys.argv[1:]
    if "auto" in args:
        # start_game.bat gates on this exit code - report failures honestly
        sys.exit(0 if auto_setup_basic_backend() else 1)
    else:
        main_interactive_setup(
            dry_run="--dry-run" in args,
            include_local_extras="--local-extras" in args,
        )
