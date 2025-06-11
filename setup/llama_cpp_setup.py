#!/usr/bin/env python3
"""
Llama-cpp-python Setup Module
Only installs llama-cpp-python with CUDA support (no CPU-only fallback)
"""

import os
import subprocess
import sys
from pathlib import Path

def check_llama_cpp_installed():
    """Check if llama-cpp-python or llama-cpp-python-cuda is installed."""
    pip_path = Path("venv/Scripts/pip.exe")
    
    if not pip_path.exists():
        print("❌ Virtual environment pip not found")
        return False

    try:
        result = subprocess.run([str(pip_path), "show", "llama-cpp-python-cuda"], capture_output=True, text=True, check=True)
        version_line = [line for line in result.stdout.split('\n') if line.startswith('Version:')]
        if version_line:
            version = version_line[0].split(':', 1)[1].strip()
            print(f"✅ llama-cpp-python-cuda installed: {version}")
            return True
    except subprocess.CalledProcessError:
        pass

    print("❌ llama-cpp-python-cuda not installed")
    return False

def check_llama_cpp_requirements():
    """Check llama-cpp-python CUDA installation."""
    print("Checking llama-cpp-python CUDA installation...")
    if not check_llama_cpp_installed():
        return False
    print("✅ llama-cpp-python-cuda is working")
    return True

def uninstall_existing_llama_cpp():
    """Remove any existing llama-cpp installations."""
    pip_path = Path("venv/Scripts/pip.exe")
    subprocess.run([str(pip_path), "uninstall", "-y", "llama-cpp-python"], check=False)
    subprocess.run([str(pip_path), "uninstall", "-y", "llama-cpp-python-cuda"], check=False)

def install_llama_cpp_with_cuda():
    """Attempt CUDA-based llama-cpp-python installation using three methods."""
    pip_path = Path("venv/Scripts/pip.exe")

    print("Installing llama-cpp-python with CUDA support...")

    # Method 1: Pre-built llama-cpp-python-cuda package
    print("Method 1: Trying pre-built llama-cpp-python-cuda package...")
    try:
        uninstall_existing_llama_cpp()
        subprocess.run([str(pip_path), "install", "llama-cpp-python-cuda"], check=True)
        print("🎉 Successfully installed pre-built llama-cpp-python-cuda package!")
        return True
    except subprocess.CalledProcessError:
        print("❌ Pre-built package failed, trying Method 2...")

    # Method 2: Build from source
    print("Method 2: Building from source with CUDA support...")
    try:
        env_vars = os.environ.copy()
        env_vars["CMAKE_ARGS"] = "-DLLAMA_CUDA=on"
        env_vars["FORCE_CMAKE"] = "1"

        subprocess.run([
            str(pip_path), "install", "llama-cpp-python", "--force-reinstall", "--no-cache-dir"
        ], env=env_vars, check=True)

        print("🎉 Successfully built llama-cpp-python with CUDA support!")
        return True
    except subprocess.CalledProcessError:
        print("❌ Source build failed, trying Method 3...")

    # Method 3: Install from CUDA wheel repo
    print("Method 3: Trying CUDA wheel repository...")
    try:
        subprocess.run([
            str(pip_path), "install", "llama-cpp-python",
            "--extra-index-url", "https://abetlen.github.io/llama-cpp-python/whl/cu121",
            "--force-reinstall"
        ], check=True)
        print("🎉 Successfully installed from CUDA wheel repository!")
        return True
    except subprocess.CalledProcessError:
        print("❌ All CUDA installation methods failed")
        return False

def setup_llama_cpp_interactive():
    """Interactive installer for llama-cpp-python with CUDA only."""
    print("Setting up llama-cpp-python with CUDA...")

    if check_llama_cpp_installed():
        choice = input("llama-cpp-python-cuda is already installed. Reinstall? (y/n): ").lower().strip()
        if choice not in ('y', 'yes'):
            return True

    success = install_llama_cpp_with_cuda()
    if not success:
        print("❌ Failed to install llama-cpp-python with CUDA")
    return success

if __name__ == "__main__":
    if len(sys.argv) > 1 and sys.argv[1] == "setup":
        setup_llama_cpp_interactive()
    else:
        check_llama_cpp_requirements()