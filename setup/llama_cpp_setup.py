#!/usr/bin/env python3
"""
Llama-cpp-python Setup Module
Checks for and installs llama-cpp-python with CUDA support
"""

import os
import subprocess
import sys
from pathlib import Path

def check_llama_cpp_installed():
    """Check if llama-cpp-python is installed."""
    pip_path = Path("venv/Scripts/pip.exe")
    
    if not pip_path.exists():
        print("❌ Virtual environment pip not found")
        return False
    
    try:
        result = subprocess.run([str(pip_path), "show", "llama-cpp-python"], 
                              capture_output=True, text=True, check=True)
        
        # Parse version info
        version_line = [line for line in result.stdout.split('\n') if line.startswith('Version:')]
        if version_line:
            version = version_line[0].split(':', 1)[1].strip()
            print(f"✅ llama-cpp-python installed: {version}")
            return True
        else:
            print("⚠️  llama-cpp-python found but version unclear")
            return True
            
    except subprocess.CalledProcessError:
        print("❌ llama-cpp-python not installed")
        return False

def check_llama_cpp_requirements():
    """Check all llama-cpp-python requirements."""
    print("Checking LLM integration (llama-cpp-python) requirements...")
    
    # Check if installed
    if not check_llama_cpp_installed():
        return False
    
    print("✅ llama-cpp-python is working")
    return True

def install_llama_cpp_cpu_only():
    """Install CPU-only version of llama-cpp-python."""
    pip_path = Path("venv/Scripts/pip.exe")
    
    print("Installing llama-cpp-python (CPU-only)...")
    try:
        subprocess.run([str(pip_path), "install", "llama-cpp-python"], check=True)
        print("✅ llama-cpp-python (CPU-only) installed successfully")
        return True
    except subprocess.CalledProcessError as e:
        print(f"❌ CPU-only installation failed: {e}")
        return False

def install_llama_cpp_cuda_source():
    """Install llama-cpp-python with CUDA support from source."""
    pip_path = Path("venv/Scripts/pip.exe")
    
    print("Installing llama-cpp-python with CUDA from source...")
    print("⚠️  This may take 10-15 minutes to compile!")
    
    # Set environment variables for CUDA build
    env = os.environ.copy()
    env["CMAKE_ARGS"] = "-DLLAMA_CUBLAS=on"
    env["FORCE_CMAKE"] = "1"
    
    try:
        subprocess.run([
            str(pip_path), "install", "llama-cpp-python", 
            "--no-cache-dir", "--force-reinstall"
        ], env=env, check=True)
        print("🎉 llama-cpp-python with CUDA compiled successfully!")
        return True
    except subprocess.CalledProcessError as e:
        print(f"❌ CUDA source build failed: {e}")
        return False

def install_llama_cpp_cuda_wheel():
    """Try to install pre-built CUDA wheel."""
    pip_path = Path("venv/Scripts/pip.exe")
    
    print("Trying pre-built CUDA wheel...")
    try:
        subprocess.run([
            str(pip_path), "install", "llama-cpp-python",
            "--extra-index-url", "https://abetlen.github.io/llama-cpp-python/whl/cu121",
            "--force-reinstall"
        ], check=True)
        print("✅ Pre-built CUDA wheel installed successfully!")
        return True
    except subprocess.CalledProcessError as e:
        print(f"❌ CUDA wheel installation failed: {e}")
        return False

def uninstall_llama_cpp():
    """Uninstall existing llama-cpp-python."""
    pip_path = Path("venv/Scripts/pip.exe")
    
    try:
        subprocess.run([str(pip_path), "uninstall", "llama-cpp-python", "-y"], 
                      capture_output=True, check=True)
        print("✅ Previous llama-cpp-python uninstalled")
        return True
    except subprocess.CalledProcessError:
        # It's okay if uninstall fails (package might not be installed)
        return True

def setup_llama_cpp_interactive():
    """Interactive setup for llama-cpp-python."""
    print("Setting up LLM integration (llama-cpp-python)...")
    
    # Check if already working
    if check_llama_cpp_installed():
        print("✅ llama-cpp-python is already working")
        
        choice = input("Do you want to reinstall for better CUDA support? (y/n): ").lower().strip()
        if choice not in ['y', 'yes']:
            return True
    
    # Determine installation strategy based on system capabilities
    print("\n📋 Determining best installation method...")
    
    # Check for CUDA availability (from gpu_cuda_setup)
    try:
        from setup.gpu_cuda_setup import check_nvidia_gpu, check_cuda_directories
        has_gpu = check_nvidia_gpu()
        has_cuda = check_cuda_directories()
    except ImportError:
        has_gpu = False
        has_cuda = False
    
    # Check for build tools (from visual_studio_setup)
    try:
        from setup.visual_studio_setup import check_visual_studio_requirements
        has_build_tools = check_visual_studio_requirements()
    except ImportError:
        has_build_tools = False
    
    # Uninstall existing version first
    if check_llama_cpp_installed():
        print("Removing existing installation...")
        uninstall_llama_cpp()
    
    # Choose installation method
    if has_gpu and has_cuda and has_build_tools:
        print("🚀 Full CUDA setup detected - trying CUDA installation")
        
        # Try pre-built wheel first
        if install_llama_cpp_cuda_wheel():
            if check_llama_cpp_installed():
                print("✅ CUDA wheel installation successful")
                return True
        
        # Fall back to source build
        print("Wheel failed, trying source build...")
        if install_llama_cpp_cuda_source():
            if check_llama_cpp_installed():
                print("✅ CUDA source build successful")
                return True
    
    elif has_gpu and has_cuda:
        print("⚠️  GPU and CUDA detected but no build tools - trying CUDA wheel only")
        if install_llama_cpp_cuda_wheel():
            if check_llama_cpp_installed():
                print("✅ CUDA wheel installation successful")
                return True
    
    # Fall back to CPU-only
    print("🔄 Falling back to CPU-only installation...")
    if install_llama_cpp_cpu_only():
        if check_llama_cpp_installed():
            print("✅ CPU-only installation successful")
            print("💡 Models will run on CPU (slower but functional)")
            return True
    
    print("❌ All llama-cpp-python installation methods failed")
    print("📋 You can try manually:")
    print("1. Activate virtual environment: venv\\Scripts\\activate")
    print("2. Install manually: pip install llama-cpp-python")
    print("3. Or check the llama-cpp-python documentation for your system")
    return False

if __name__ == "__main__":
    if len(sys.argv) > 1 and sys.argv[1] == "setup":
        setup_llama_cpp_interactive()
    else:
        check_llama_cpp_requirements()