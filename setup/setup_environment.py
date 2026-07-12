#!/usr/bin/env python3
"""
Monster Hunter Game - Interactive Environment Setup
Walks a new player through whatever their machine is missing.

The happy path asks ZERO questions: each step checks itself, fixes what
it can silently, and only involves the user when something genuinely
needs them (like the MySQL installer wizard). The unsupported local-LLM
escape hatch (GPU/CUDA/Build Tools/GGUF model) is developer-facing and
only runs with --local-extras - a new player never sees that
vocabulary.
"""

import sys

from setup.checks import COMPONENT_CHECKS
from setup.components import components_for
from setup.flows import COMPONENT_FLOWS
from setup.utils.ux_utils import (
    print_error,
    print_header,
    print_success,
    print_warning,
)

# Plain-English step names: the walkthrough says what each component
# MEANS to the player; the component flows narrate what they're doing
STEP_DESCRIPTIONS = {
    'Basic Backend': "the game's engine (Python packages)",
    'Node.js & npm': "the game's interface (Node.js)",
    'MySQL Server': "the database that stores your monsters (MySQL)",
    'Database Connection': "connecting the game to its database",
    'NVIDIA GPU & CUDA': "local-LLM extra: NVIDIA GPU & CUDA toolkit",
    'Visual Studio Build Tools': "local-LLM extra: Visual Studio Build Tools",
    'Model Directory': "local-LLM extra: the GGUF model file",
    'LLM Integration': "local-LLM extra: llama-cpp-python",
}


def auto_setup_basic_backend():
    """Perform automatic installation of basic requirements that do not require user attention"""

    from setup.flows.basic_backend_flow import auto_setup_basic_backend

    return auto_setup_basic_backend()


def main_interactive_setup(dry_run=False, include_local_extras=False):
    """Auto-fix-first setup pass over whatever this machine is missing."""
    print_header("Setting up Monster Hunter Game")
    print("This checks what's already in place and fixes what's missing.")
    print("Most steps run by themselves - you'll only be asked to help when")
    print("something genuinely needs you (like the MySQL install).")
    print()

    component_names = list(components_for(include_local_extras))
    total_components = len(component_names)
    unresolved = []

    for current, component_name in enumerate(component_names, 1):
        step = STEP_DESCRIPTIONS.get(component_name, component_name)
        print(f"Step {current} of {total_components} - {step}...")

        # Already working? Say so in one line and move on
        check_function = COMPONENT_CHECKS[component_name]
        try:
            if check_function() and not dry_run:
                print_success("Already good - nothing to do.")
                print()
                continue
        except Exception as e:
            print_error(f"Error checking {component_name}: {e}")

        # Needs attention: run the component's flow directly - it fixes
        # what it can and only involves the user when it must
        try:
            print()
            setup_function = COMPONENT_FLOWS[component_name]
            result = setup_function(current=current, total=total_components, dry_run=dry_run)
        except Exception as e:
            print_error(f"Error during {component_name} setup: {e}")
            result = False

        if result:
            print_success(f"Done - {step} is ready.")
        else:
            unresolved.append(component_name)
            print_warning(f"{component_name} isn't finished yet - continuing with the rest.")
        print()

    show_finish_screen(unresolved)


def show_finish_screen(unresolved):
    """End on the one action that matters: the gear icon and the API key."""

    if unresolved:
        print_header("Setup finished - with loose ends")
        print("Almost there! These still need attention:")
        for name in unresolved:
            print(f"   - {name}")
        print()
        print("The messages above say what to do. Once that's done, double-click")
        print("start_game.bat and it will pick up right where this left off.")
        print()
        return

    print_header("All set!")
    print("Everything the game needs is ready. When the game opens in your")
    print("browser, there's one last thing only you can do:")
    print()
    print("   Click the GEAR ICON (top of the screen) and paste in your")
    print("   DeepSeek API key - that powers all the story text.")
    print("   Get one at: https://platform.deepseek.com")
    print()
    print("   Card art is optional: add a Google Gemini key from")
    print("   https://aistudio.google.com whenever you like. The game plays")
    print("   fully art-less without it.")
    print()
    print("Costs are pay-as-you-go and small: a heavy session is a dollar or")
    print("two, mostly in card art - just pennies of text without it.")
    print()


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
