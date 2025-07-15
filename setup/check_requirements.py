#!/usr/bin/env python3
"""
Monster Hunter Game - Requirements Checker
Checks all system requirements and reports status
Returns 0 if all requirements met, 1 if some are missing
"""

import sys
from setup.checks import run_all_checks
from setup.utils.ux_utils import show_status_table, print_header

def check_requirements():
    """Check all requirements and report status."""
    
    print_header("System Requirements Check")
    print("Checking all requirements for Monster Hunter Game...")
    print()
    
    # Run all checks - they return clean data now
    results = run_all_checks()
    ready_components, total_components = show_status_table(results)
    
    # Determine overall status and show appropriate message
    if ready_components == total_components:
        print("🎉 All requirements met! Ready to run the game.")
        return 0  # Success
    elif ready_components >= total_components * 0.75:  # At least 75% passed
        print(f"⚠️  Most requirements met ({ready_components}/{total_components})")
        print("Please setup the final components.")
        return 1  # Partial success
    else:
        print(f"❌ Many requirements missing ({total_components - ready_components}/{total_components} failed)")
        print("Game likely won't work without setup.")
        return 1  # Many failures

if __name__ == "__main__":
    sys.exit(check_requirements())