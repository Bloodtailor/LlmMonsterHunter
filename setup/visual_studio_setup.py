#!/usr/bin/env python3
"""
Visual Studio Build Tools Setup Module
Checks for Visual Studio or Build Tools needed for compiling Python packages
"""

import os
import subprocess
import sys
from pathlib import Path

def check_visual_studio_installations():
    """Check for Visual Studio installations."""
    vs_paths = [
        ("Visual Studio 2022", "C:\\Program Files\\Microsoft Visual Studio\\2022"),
        ("Visual Studio 2019", "C:\\Program Files\\Microsoft Visual Studio\\2019"),
        ("VS Build Tools 2022", "C:\\Program Files (x86)\\Microsoft Visual Studio\\2022\\BuildTools"),
        ("VS Build Tools 2019", "C:\\Program Files (x86)\\Microsoft Visual Studio\\2019\\BuildTools"),
        ("VS Community 2022", "C:\\Program Files\\Microsoft Visual Studio\\2022\\Community"),
        ("VS Professional 2022", "C:\\Program Files\\Microsoft Visual Studio\\2022\\Professional"),
        ("VS Enterprise 2022", "C:\\Program Files\\Microsoft Visual Studio\\2022\\Enterprise")
    ]
    
    found_installations = []
    for name, path in vs_paths:
        if os.path.exists(path):
            found_installations.append((name, path))
            print(f"✅ {name} found: {path}")
    
    return found_installations

def check_windows_sdk():
    """Check for Windows SDK installation."""
    sdk_paths = [
        "C:\\Program Files (x86)\\Windows Kits\\10",
        "C:\\Program Files\\Windows Kits\\10",
        "C:\\Program Files (x86)\\Microsoft SDKs\\Windows"
    ]
    
    for path in sdk_paths:
        if os.path.exists(path):
            print(f"✅ Windows SDK found: {path}")
            return True
    
    print("❌ Windows SDK not found")
    return False

def check_cpp_build_tools():
    """Check for C++ build tools components."""
    # Look for specific build tools in VS installations
    vs_installations = check_visual_studio_installations()
    
    if not vs_installations:
        return False
    
    # Check if any installation has C++ build tools
    for name, base_path in vs_installations:
        # Look for VC tools
        vc_path = os.path.join(base_path, "VC", "Tools", "MSVC")
        if os.path.exists(vc_path):
            try:
                versions = [d for d in os.listdir(vc_path) if os.path.isdir(os.path.join(vc_path, d))]
                if versions:
                    latest_version = sorted(versions)[-1]
                    print(f"✅ C++ build tools found in {name}: MSVC {latest_version}")
                    return True
            except OSError:
                continue
    
    print("❌ C++ build tools not found in any Visual Studio installation")
    return False

def check_visual_studio_requirements():
    """Check all Visual Studio build requirements."""
    print("Checking Visual Studio Build Tools requirements...")
    
    # Check for installations
    installations = check_visual_studio_installations()
    
    # Check for Windows SDK
    sdk_available = check_windows_sdk()
    
    # Check for C++ build tools
    cpp_tools_available = check_cpp_build_tools()
    
    # Determine overall status
    if installations and cpp_tools_available:
        print("✅ Visual Studio Build Tools are available")
        return True
    elif installations:
        print("⚠️  Visual Studio found but C++ build tools may not be installed")
        return False
    else:
        print("❌ Visual Studio Build Tools not found")
        return False

def setup_visual_studio_interactive():
    """Interactive setup guidance for Visual Studio Build Tools."""
    print("Setting up Visual Studio Build Tools...")
    
    # Check current installations
    installations = check_visual_studio_installations()
    
    if not installations:
        print("\n❌ No Visual Studio installations found")
        print("📋 You need Visual Studio Build Tools to compile Python packages like llama-cpp-python")
        print("")
        print("📋 To install Visual Studio Build Tools:")
        print("1. Go to https://visualstudio.microsoft.com/downloads/")
        print("2. Scroll down to 'All Downloads'")
        print("3. Download 'Build Tools for Visual Studio 2022'")
        print("4. Run the installer and select:")
        print("   - 'C++ build tools' workload")
        print("   - Include: MSVC v143 compiler toolset")
        print("   - Include: Windows 10/11 SDK (latest)")
        print("   - Include: CMake tools for Visual Studio")
        print("5. Complete the installation (may take 30+ minutes)")
        print("6. Restart your computer")
        print("")
        
        input("Press Enter after installing Visual Studio Build Tools...")
        
        # Check again
        installations = check_visual_studio_installations()
        if not installations:
            print("❌ Visual Studio Build Tools still not found")
            print("⚠️  You can still try to run the game, but llama-cpp-python installation may fail")
            
            choice = input("Continue without Build Tools? (y/n): ").lower().strip()
            if choice not in ['y', 'yes']:
                return False
    
    # Check for C++ build tools specifically
    if installations and not check_cpp_build_tools():
        print("\n⚠️  Visual Studio found but C++ build tools not detected")
        print("📋 To add C++ build tools to existing Visual Studio:")
        print("1. Open Visual Studio Installer")
        print("2. Click 'Modify' on your Visual Studio installation")
        print("3. Go to 'Workloads' tab")
        print("4. Check 'C++ build tools' or 'Desktop development with C++'")
        print("5. In 'Individual components', ensure you have:")
        print("   - MSVC v143 - VS 2022 C++ x64/x86 build tools")
        print("   - Windows 10/11 SDK")
        print("   - CMake tools for Visual Studio")
        print("6. Click 'Modify' to install")
        print("")
        
        input("Press Enter after adding C++ build tools...")
        
        if not check_cpp_build_tools():
            print("❌ C++ build tools still not found")
            print("⚠️  llama-cpp-python compilation may fail")
    
    # Final verification
    if check_visual_studio_requirements():
        print("✅ Visual Studio Build Tools setup completed")
        print("🔨 Ready for compiling Python packages")
        return True
    else:
        print("⚠️  Visual Studio Build Tools setup incomplete")
        print("💡 You can still try running the game setup")
        print("💡 Some Python packages may use pre-built wheels instead")
        return True  # Return True to allow continuing

if __name__ == "__main__":

    setup_visual_studio_interactive()
