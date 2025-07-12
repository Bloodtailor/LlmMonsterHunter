#!/usr/bin/env python3
"""
Monster Hunter Game - Requirements Checker
Checks all system requirements and reports status
Returns 0 if all requirements met, 1 if some are missing
"""

import sys
from pathlib import Path

# Import checker modules (mix of old and new patterns during transition)
from setup.checks.nodejs_checks import check_nodejs_requirements  # NEW PATTERN
from setup.checks.mysql_checks import check_mysql_requirements  # NEW PATTERN
from setup.database_connection import check_database_connection
from setup.gpu_cuda_setup import check_gpu_cuda_requirements
from setup.visual_studio_setup import check_visual_studio_requirements
from setup.llama_cpp_setup import check_llama_cpp_requirements
from setup.model_directory import check_model_directory_requirements
from setup.basic_backend import check_basic_backend_requirements_silent

# Import UX utilities
from setup.ux_utils import show_status_table

def print_header(text):
    """Print a formatted header."""
    print("\n" + "=" * 60)
    print(text.center(60))
    print("=" * 60)

def print_section(text):
    """Print a section header."""
    print(f"\n{text}")
    print("-" * len(text))

def check_requirements_silent():
    """Silently check all requirements and return results."""
    # Define all requirement checks with their modules
    requirement_checks = [
        ("Basic Backend", check_basic_backend_requirements_silent),
        ("Node.js & npm", check_nodejs_requirements),
        ("MySQL Server", check_mysql_requirements),
        ("Database Connection", check_database_connection),
        ("NVIDIA GPU & CUDA", check_gpu_cuda_requirements),
        ("Visual Studio Build Tools", check_visual_studio_requirements),
        ("LLM Integration", check_llama_cpp_requirements),
        ("Model Directory", check_model_directory_requirements)
    ]
    
    # Run all checks silently
    results = []
    for check_name, check_function in requirement_checks:
        try:
            # Capture output to suppress it
            import io
            import contextlib
            
            f = io.StringIO()
            with contextlib.redirect_stdout(f):
                with contextlib.redirect_stderr(f):
                    result = check_function()
            results.append((check_name, result))
        except Exception:
            results.append((check_name, False))
    
    return results

def main():
    """Check all requirements and report status."""
    # Check if we should run in summary mode
    summary_mode = len(sys.argv) > 1 and sys.argv[1] == "summary"
    
    if summary_mode:
        print("Checking system requirements...")
        results = check_requirements_silent()
    else:
        print_header("System Requirements Check")
        print("Checking all requirements for Monster Hunter Game...")
        
        # Define all requirement checks with their modules
        requirement_checks = [
            ("Basic Backend", check_basic_backend_requirements_silent),
            ("Node.js & npm", check_nodejs_requirements),
            ("MySQL Server", check_mysql_requirements),
            ("Database Connection", check_database_connection),
            ("NVIDIA GPU & CUDA", check_gpu_cuda_requirements),
            ("Visual Studio Build Tools", check_visual_studio_requirements),
            ("LLM Integration", check_llama_cpp_requirements),
            ("Model Directory", check_model_directory_requirements)
        ]
        
        # Run all checks
        results = []
        for check_name, check_function in requirement_checks:
            print_section(f"Checking {check_name}")
            try:
                result = check_function()
                results.append((check_name, result))
                status = "✅ PASS" if result else "❌ FAIL"
                print(f"Result: {status}")
            except Exception as e:
                print(f"❌ ERROR: {e}")
                results.append((check_name, False))
    
    # New improved status display using UX utilities
    if summary_mode:
        ready_components, total_components = show_status_table(results)
    else:
        print_header("Requirements Summary")
        ready_components, total_components = show_status_table(results)
    
    # Determine overall status and show appropriate message
    if ready_components == total_components:
        print("🎉 All requirements met! Ready to run the game.")
        return 0  # Success
    elif ready_components >= total_components * 0.75:  # At least 75% passed
        print(f"⚠️  Most requirements met ({ready_components}/{total_components})")
        print("Game should work but may have some issues.")
        return 1  # Partial success
    else:
        print(f"❌ Many requirements missing ({total_components - ready_components}/{total_components} failed)")
        print("Game likely won't work without setup.")
        return 1  # Many failures

if __name__ == "__main__":
    sys.exit(main())