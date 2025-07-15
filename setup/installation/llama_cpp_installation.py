#!/usr/bin/env python3
"""
LLama-cpp-python Installation Module
Pure installation logic for llama-cpp-python with CUDA and CPU-only options
"""

import os
import subprocess
import sys
from pathlib import Path

def uninstall_existing_llama_cpp():
    """
    Remove any existing llama-cpp-python installations.
    
    Returns:
        tuple: (success, message)
    """
    pip_path = Path("venv/Scripts/pip.exe")
    
    if not pip_path.exists():
        return False, "Virtual environment pip not found"
    
    try:
        # Try to uninstall both possible package names
        subprocess.run([str(pip_path), "uninstall", "-y", "llama-cpp-python"], 
                      capture_output=True, check=False)
        subprocess.run([str(pip_path), "uninstall", "-y", "llama-cpp-python-cuda"], 
                      capture_output=True, check=False)
        return True, "Existing llama-cpp-python installations removed"
        
    except Exception as e:
        return False, f"Failed to uninstall existing packages: {e}"

def install_llama_cpp_prebuilt():
    """
    Method 1: Install pre-built llama-cpp-python-cuda package.
    
    Returns:
        tuple: (success, message)
    """
    pip_path = Path("venv/Scripts/pip.exe")
    
    if not pip_path.exists():
        return False, "Virtual environment pip not found"
    
    try:
        # First uninstall existing
        uninstall_existing_llama_cpp()
        
        # Install pre-built CUDA package
        subprocess.run([str(pip_path), "install", "llama-cpp-python-cuda"], 
                      capture_output=True, text=True, check=True)
        
        return True, "Successfully installed pre-built llama-cpp-python-cuda package"
        
    except subprocess.CalledProcessError as e:
        error_msg = e.stderr.strip() if e.stderr else "Unknown installation error"
        return False, f"Pre-built package installation failed: {error_msg}"
    except Exception as e:
        return False, f"Pre-built package installation error: {e}"

def install_llama_cpp_source():
    """
    Method 2: Build llama-cpp-python from source with CUDA support.
    
    Returns:
        tuple: (success, message)
    """
    pip_path = Path("venv/Scripts/pip.exe")
    
    if not pip_path.exists():
        return False, "Virtual environment pip not found"
    
    try:
        # Set environment variables for CUDA build
        env_vars = os.environ.copy()
        env_vars["CMAKE_ARGS"] = "-DLLAMA_CUDA=on"
        env_vars["FORCE_CMAKE"] = "1"
        
        # Build from source with CUDA
        subprocess.run([
            str(pip_path), "install", "llama-cpp-python", 
            "--force-reinstall", "--no-cache-dir"
        ], env=env_vars, capture_output=True, text=True, check=True)
        
        return True, "Successfully built llama-cpp-python with CUDA from source"
        
    except subprocess.CalledProcessError as e:
        error_msg = e.stderr.strip() if e.stderr else "Unknown build error"
        return False, f"Source build failed: {error_msg}"
    except Exception as e:
        return False, f"Source build error: {e}"

def install_llama_cpp_wheel():
    """
    Method 3: Install from CUDA wheel repository.
    
    Returns:
        tuple: (success, message)
    """
    pip_path = Path("venv/Scripts/pip.exe")
    
    if not pip_path.exists():
        return False, "Virtual environment pip not found"
    
    try:
        # Install from CUDA wheel repository
        subprocess.run([
            str(pip_path), "install", "llama-cpp-python",
            "--extra-index-url", "https://abetlen.github.io/llama-cpp-python/whl/cu121",
            "--force-reinstall"
        ], capture_output=True, text=True, check=True)
        
        return True, "Successfully installed from CUDA wheel repository"
        
    except subprocess.CalledProcessError as e:
        error_msg = e.stderr.strip() if e.stderr else "Unknown installation error"
        return False, f"CUDA wheel installation failed: {error_msg}"
    except Exception as e:
        return False, f"CUDA wheel installation error: {e}"

def install_llama_cpp_cpu_only():
    """
    Install CPU-only version of llama-cpp-python.
    WARNING: This will result in extremely slow performance for AI inference.
    
    Returns:
        tuple: (success, message)
    """
    pip_path = Path("venv/Scripts/pip.exe")
    
    if not pip_path.exists():
        return False, "Virtual environment pip not found"
    
    try:
        # First uninstall existing
        uninstall_existing_llama_cpp()
        
        # Install regular llama-cpp-python (CPU-only)
        subprocess.run([str(pip_path), "install", "llama-cpp-python"], 
                      capture_output=True, text=True, check=True)
        
        return True, "Successfully installed CPU-only llama-cpp-python (WARNING: Will be very slow)"
        
    except subprocess.CalledProcessError as e:
        error_msg = e.stderr.strip() if e.stderr else "Unknown installation error"
        return False, f"CPU-only installation failed: {error_msg}"
    except Exception as e:
        return False, f"CPU-only installation error: {e}"

def install_llama_cpp_with_cuda():
    """
    Attempt CUDA-based llama-cpp-python installation using three methods in sequence.
    Tries pre-built package first, then source build, then wheel repository.
    
    Returns:
        tuple: (success, message) with details about which method succeeded or all failures
    """
    methods = [
        ("Pre-built CUDA package", install_llama_cpp_prebuilt),
        ("Source build with CUDA", install_llama_cpp_source),
        ("CUDA wheel repository", install_llama_cpp_wheel)
    ]
    
    failed_methods = []
    
    for method_name, install_func in methods:
        success, message = install_func()
        
        if success:
            return True, f"{method_name}: {message}"
        else:
            failed_methods.append(f"{method_name}: {message}")
    
    # All methods failed
    failure_summary = "; ".join(failed_methods)
    return False, f"All CUDA installation methods failed. {failure_summary}"

def install_llama_cpp_any_method():
    """
    Install llama-cpp-python using any available method.
    Tries CUDA methods first, falls back to CPU-only as last resort.
    
    Returns:
        tuple: (success, message) with installation details
    """
    
    # First try CUDA installation
    cuda_success, cuda_message = install_llama_cpp_with_cuda()
    
    if cuda_success:
        return True, cuda_message
    
    # If CUDA failed, try CPU-only as last resort
    cpu_success, cpu_message = install_llama_cpp_cpu_only()
    
    if cpu_success:
        return True, f"CUDA failed, fell back to CPU-only: {cpu_message}"
    else:
        return False, f"All installation methods failed. CUDA: {cuda_message}. CPU: {cpu_message}"

def upgrade_pip():
    """
    Upgrade pip in the virtual environment.
    Sometimes needed before installing complex packages.
    
    Returns:
        tuple: (success, message)
    """
    pip_path = Path("venv/Scripts/pip.exe")
    
    if not pip_path.exists():
        return False, "Virtual environment pip not found"
    
    try:
        subprocess.run([str(pip_path), "install", "--upgrade", "pip"], 
                      capture_output=True, text=True, check=True)
        return True, "pip upgraded successfully"
        
    except subprocess.CalledProcessError as e:
        error_msg = e.stderr.strip() if e.stderr else "Unknown upgrade error"
        return False, f"pip upgrade failed: {error_msg}"
    except Exception as e:
        return False, f"pip upgrade error: {e}"

def install_llama_cpp_with_retry():
    """
    Install llama-cpp-python with automatic pip upgrade retry.
    Sometimes pip needs to be upgraded before complex package installations work.
    
    Returns:
        tuple: (success, message)
    """
    
    # First attempt with current pip
    success, message = install_llama_cpp_with_cuda()
    
    if success:
        return True, message
    
    # If failed, try upgrading pip first
    pip_success, pip_message = upgrade_pip()
    
    if not pip_success:
        return False, f"Installation failed and pip upgrade failed: {message}. Pip: {pip_message}"
    
    # Retry installation after pip upgrade
    retry_success, retry_message = install_llama_cpp_with_cuda()
    
    if retry_success:
        return True, f"Installation succeeded after pip upgrade: {retry_message}"
    else:
        return False, f"Installation failed even after pip upgrade: {retry_message}"