#!/usr/bin/env python3
"""
Visual Studio Interactive Setup Flow
Orchestrates the complete Visual Studio Build Tools setup experience with clean UX
"""
COMPONENT_NAME = "Visual Studio Build Tools"

from setup.utils.ux_utils import *
from setup.checks.vs_checks import (
    check_visual_studio_installations,
    check_windows_sdk,
    check_cpp_build_tools,
)

def run_visual_studio_interactive_setup(current=None, total=None, dry_run=False):
    """
    Interactive setup flow for Visual Studio Build Tools
    
    Returns:
        bool: True if setup completed successfully, False otherwise
    """
    
    # ================================================================
    # SECTION 1: INITIAL STATUS CHECK AND DISPLAY
    # ================================================================

    # Show clean component header
    show_component_header(
        component_name=COMPONENT_NAME,
        current=current,
        total=total,
        description="Required for compiling Python packages like llama-cpp-python"
    )

    print("Checking current status...")
    
    # Run individual checks
    installations_ok, installations_message = check_visual_studio_installations()
    sdk_ok, sdk_message = check_windows_sdk()
    cpp_tools_ok, cpp_tools_message = check_cpp_build_tools()

    # Dry run mode - set check results to custom values
    if dry_run:
        print_dry_run_header()
        
        from setup.utils.dry_run_utils import set_dry_run
        installations_ok, installations_message = set_dry_run('check_visual_studio_installations')
        sdk_ok, sdk_message = set_dry_run('check_windows_sdk')
        cpp_tools_ok, cpp_tools_message = set_dry_run('check_cpp_build_tools')

    # Package results for display
    check_results = {
        "Visual Studio": (installations_ok, installations_message),
        "Windows SDK": (sdk_ok, sdk_message),
        "C++ Build Tools": (cpp_tools_ok, cpp_tools_message)
    }

    # Display results beautifully
    overall_ok = display_check_results("VISUAL STUDIO", check_results)

    # ================================================================
    # SECTION 2: INTERACTIVE SETUP FLOWS AND LOGIC
    # ================================================================

    # If everything is working, we're done!
    if overall_ok:
        print("Visual Studio Build Tools are ready!")
        print("🔨 Ready for compiling Python packages")
        print()
        return True
    
    # Show requirement explanation
    show_message('visual_studio_requirement_explanation')
    choice = handle_user_choice([("G", "Get instructions")], COMPONENT_NAME)

    if choice == "CONTINUE" or choice == "SKIP":
        return True
    
    # Handle case if vs is installed but missing tools
    if installations_ok and (not cpp_tools_ok or not sdk_ok):
        print()
        print()
        print_info("Visual Studio found, but missing requirements")
        print_success(installations_message)

        if not cpp_tools_ok and not sdk_ok:
            show_message('visual_studio_modify_for_cpp_tools')
            return prompt_continue_or_skip(COMPONENT_NAME)
        elif not cpp_tools_ok:
            show_message('visual_studio_missing_cpp_tools_detected')
            return prompt_continue_or_skip(COMPONENT_NAME)
        else:
            show_message('visual_studio_sdk_detection_issue')
            return prompt_continue_or_skip(COMPONENT_NAME)

    
    if not (installations_ok and cpp_tools_ok and sdk_ok):
        show_message('visual_studio_installation_instructions')
    else:
        show_message('visual_studio_installation_instructions')

        
    return prompt_continue_or_skip(COMPONENT_NAME)

if __name__ == "__main__":
    from setup.utils.dry_run_utils import run_as_standalone_component
    run_as_standalone_component(COMPONENT_NAME, run_visual_studio_interactive_setup)
    
    
    
