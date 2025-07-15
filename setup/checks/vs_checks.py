#!/usr/bin/env python3
"""
Visual Studio Checks Module
Pure detection logic for Visual Studio installations and C++ build tools
Returns data instead of printing for clean UX flow

Note: These checks may have false negatives due to varied VS installation patterns.
They're designed to guide users, not provide perfect detection.
"""

import os
from pathlib import Path
from setup.constants import VS_LOCATIONS, SDK_LOCATIONS, NODEJS_LOCATIONS

def check_visual_studio_installations():
    """
    Check for Visual Studio installations in common directories.
    
    Returns:
        tuple: (success, message) where success indicates if any VS installation found
    """
    vs_paths = VS_LOCATIONS
    
    found_installations = []
    for name, path in vs_paths:
        if os.path.exists(path):
            found_installations.append((name, path))
    
    if found_installations:
        # Return info about the first (most relevant) installation found
        first_name, first_path = found_installations[0]
        if len(found_installations) == 1:
            return True, f"{first_name} found at {first_path}"
        else:
            return True, f"{len(found_installations)} VS installations found (primary: {first_name})"
    else:
        return False, "No Visual Studio installations found in common directories"

def check_windows_sdk():
    """
    Check for Windows SDK installation.
    
    Returns:
        tuple: (success, message)
    """
    sdk_paths = SDK_LOCATIONS
    
    for path in sdk_paths:
        if os.path.exists(path):
            return True, f"Windows SDK found at {path}"
    
    return False, "Windows SDK not found in common directories"

def check_cpp_build_tools():
    """
    Check for C++ build tools within Visual Studio installations.
    This is the critical check - VS can exist without C++ capabilities.
    
    Returns:
        tuple: (success, message)
    """
    # First get VS installations
    vs_found, vs_message = check_visual_studio_installations()
    
    if not vs_found:
        return False, "No Visual Studio installations to check for C++ tools"
    
    # Common base paths where VS might be installed
    base_paths = NODEJS_LOCATIONS
    
    for base_path in base_paths:
        if not os.path.exists(base_path):
            continue
            
        # Look for VC tools in this installation
        vc_path = os.path.join(base_path, "VC", "Tools", "MSVC")
        if os.path.exists(vc_path):
            try:
                versions = [d for d in os.listdir(vc_path) if os.path.isdir(os.path.join(vc_path, d))]
                if versions:
                    latest_version = sorted(versions)[-1]
                    return True, f"C++ build tools found (MSVC {latest_version})"
            except OSError:
                continue
    
    return False, "C++ build tools not found in Visual Studio installations"

def check_visual_studio_requirements():
    """
    Check all Visual Studio requirements for compiling Python packages.
    This orchestrates the individual checks to determine overall readiness.
    
    Returns:
        bool: True if VS environment appears ready for compilation
    """
    
    # Run all individual checks
    installations_ok, _ = check_visual_studio_installations()
    sdk_ok, _ = check_windows_sdk()
    cpp_tools_ok, _ = check_cpp_build_tools()
    
    return installations_ok and sdk_ok and cpp_tools_ok

def get_diagnostic_info(include_overall=False):
    """
    Get comprehensive Visual Studio diagnostic information.
    Used by flows to understand what specifically needs to be addressed.
    
    Args:
        include_overall (bool): Whether to include overall requirement check
    
    Returns:
        dict: All VS check results for detailed analysis
    """
    installations_ok, installations_msg = check_visual_studio_installations()
    sdk_ok, sdk_msg = check_windows_sdk()
    cpp_tools_ok, cpp_tools_msg = check_cpp_build_tools()
    
    result = {
        'installations': (installations_ok, installations_msg),
        'windows_sdk': (sdk_ok, sdk_msg),
        'cpp_build_tools': (cpp_tools_ok, cpp_tools_msg),
    }
    
    if include_overall:
        overall_ok = check_visual_studio_requirements()
        result['overall'] = (overall_ok, "All Visual Studio requirements met" if overall_ok else "Some Visual Studio requirements missing")
    
    return result