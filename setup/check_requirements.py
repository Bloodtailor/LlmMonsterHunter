#!/usr/bin/env python3
"""
Monster Hunter Game - Requirements Checker
Checks system requirements and reports status.

By default this checks only what the API-first game needs (Python env,
Node, MySQL, database) - the local-LLM extras are an unsupported escape
hatch and only appear with --local-extras (setup/components.py is the
single source of that split).

Returns 0 if the checked requirements are met, 1 if some are missing.
"""

import sys

from setup.checks import run_all_checks
from setup.components import components_for
from setup.utils.ux_utils import print_header, show_status_table


def check_requirements(include_local_extras=False):
    """Check requirements and report status."""

    print_header("System Requirements Check")
    print("Checking everything Monster Hunter Game needs to run...")
    print()

    component_names = components_for(include_local_extras)
    results = run_all_checks(component_names)
    ready_components, total_components = show_status_table(results)

    if ready_components == total_components:
        print("🎉 Everything the game needs is ready!")
        if not include_local_extras:
            print("(Local-LLM extras not checked - the API-first game doesn't need them.")
            print(" Developers: add --local-extras to include them.)")
        return 0  # Success

    missing = total_components - ready_components
    print(f"⚠️  {missing} of {total_components} components still need setup.")
    print("The launcher can walk you through fixing them.")
    return 1


if __name__ == "__main__":
    sys.exit(check_requirements(include_local_extras="--local-extras" in sys.argv[1:]))
