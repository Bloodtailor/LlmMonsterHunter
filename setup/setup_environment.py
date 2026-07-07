#!/usr/bin/env python3
"""
Monster Hunter Game - Interactive Environment Setup
Walks user through setting up missing requirements
"""

import sys

from setup.check_requirements import check_requirements
from setup.checks import COMPONENT_CHECKS, run_component_diagnostic
from setup.flows import COMPONENT_FLOWS, LOCAL_EXTRA_COMPONENTS
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

    auto_setup_basic_backend()


def _ask_about_local_extras():
    """One gate for the GPU/CUDA/Build-Tools/GGUF chain."""
    print()
    print_header("Optional: local-LLM extras")
    print("The game is API-first: text runs on DeepSeek and card art on Gemini,")
    print("both configured IN-GAME (gear icon -> Settings) with API keys.")
    print("The remaining components (NVIDIA GPU & CUDA, Visual Studio Build")
    print("Tools, a local GGUF model) only matter for the UNSUPPORTED")
    print("local-model escape hatch: the game requires a 1M-token context")
    print("window, and consumer GPUs don't run 1M-token models.")
    print()
    return prompt_user_confirmation("Set up the local-LLM extras anyway? [y/N]: ")


def main_interactive_setup(dry_run=False):
    """Interactive setup for missing requirements."""
    print_header("Interactive Environment Setup")
    print("This will help you set up missing requirements for Monster Hunter Game.")
    print("You'll be asked before each setup step.")
    print()

    # Get the list of components in setup order
    component_names = list(COMPONENT_FLOWS.keys())
    total_components = len(component_names)

    # The game is API-first: text (DeepSeek) and card art (Gemini) run on
    # keys pasted IN-GAME, so the local-LLM chain is one opt-in question
    include_local_extras = None

    for current, component_name in enumerate(component_names, 1):
        if component_name in LOCAL_EXTRA_COMPONENTS:
            if include_local_extras is None:
                include_local_extras = _ask_about_local_extras()
            if not include_local_extras:
                continue

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
        check_requirements()


if __name__ == "__main__":
    if len(sys.argv) > 1 and sys.argv[1] == "auto":
        auto_setup_basic_backend()
    else:
        # from setup.utils.dry_run_utils import run_as_standalone_component
        main_interactive_setup()
