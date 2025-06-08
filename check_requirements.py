#!/usr/bin/env python3
"""
Monster Hunter Game - Requirements Checker
Checks all system requirements and reports status
Returns 0 if all requirements met, 1 if some are missing
"""

import sys
from pathlib import Path

# Import all checker modules
from setup.nodejs_setup import check_nodejs_requirements
from setup.mysql_setup import check_mysql_requirements
from setup.database_connection import check_database_connection
from setup.gpu_cuda_setup import check_gpu_cuda_requirements
from setup.visual_studio_setup import check_visual_studio_requirements
from setup.llama_cpp_setup import check_llama_cpp_requirements
from setup.model_directory import check_model_directory_requirements
from setup.basic_backend import check_basic_backend_requirements

def print_header(text):
    """Print a formatted header."""
    print("\n" + "=" * 60)
    print(text.center(60))
    print("=" * 60)

def print_section(text):
    """Print a section header."""
    print(f"\n{text}")
    print("-" * len(text))

def main():
    """Check all requirements and report status."""
    print_header("System Requirements Check")
    print("Checking all requirements for Monster Hunter Game...")
    
    # Define all requirement checks with their modules
    requirement_checks = [
        ("Basic Backend", check_basic_backend_requirements),
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
    
    # Summary
    passed_checks = sum(1 for _, result in results if result)
    total_checks = len(results)
    
    print_header("Requirements Summary")
    for check_name, result in results:
        status = "✅ PASS" if result else "❌ FAIL"
        print(f"{check_name:<25} {status}")
    
    print(f"\nPassed: {passed_checks}/{total_checks} checks")
    
    # Determine overall status
    if passed_checks == total_checks:
        print("\n🎉 All requirements met! Ready to run the game.")
        return 0  # Success
    elif passed_checks >= total_checks * 0.75:  # At least 75% passed
        print(f"\n⚠️  Most requirements met ({passed_checks}/{total_checks})")
        print("Game should work but may have some issues.")
        return 1  # Partial success
    else:
        print(f"\n❌ Many requirements missing ({total_checks - passed_checks}/{total_checks} failed)")
        print("Game likely won't work without setup.")
        return 1  # Many failures

if __name__ == "__main__":
    sys.exit(main())