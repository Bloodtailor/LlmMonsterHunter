#!/usr/bin/env python3
"""
GPU CUDA Checks Module
Pure detection logic for NVIDIA GPU, drivers, and CUDA toolkit
Returns data instead of printing for clean UX flow
"""

import subprocess
import sys
import re
import os
from pathlib import Path

def check_nvidia_gpu():
    """Check for NVIDIA GPU and drivers using nvidia-smi."""
    try:
        result = subprocess.run(["nvidia-smi"], capture_output=True, text=True, check=True)
        
        # Parse GPU info from nvidia-smi output
        gpu_info = "GPU detected"
        vram_info = ""
        
        lines = result.stdout.split('\n')
        for line in lines:
            # Look for GPU info line (contains GPU name)
            if any(gpu in line for gpu in ['GeForce', 'RTX', 'GTX', 'Quadro', 'Tesla']):
                parts = line.split('|')
                if len(parts) > 1:
                    gpu_info = parts[1].strip()
                break
        
        # Parse VRAM info
        for line in lines:
            if 'MiB' in line and '/' in line:
                # Look for memory usage line
                parts = line.split('|')
                for part in parts:
                    if 'MiB' in part and '/' in part:
                        vram_info = part.strip()
                        break
                break
        
        message = f"NVIDIA GPU: {gpu_info}"
        if vram_info:
            message += f", Memory: {vram_info}"
            
        return True, message
        
    except FileNotFoundError:
        return False, "nvidia-smi not found (NVIDIA drivers not installed)"
    except subprocess.CalledProcessError:
        return False, "nvidia-smi failed (GPU or driver issues)"

def check_nvidia_driver_version():
    """Check NVIDIA driver version for CUDA compatibility."""
    try:
        result = subprocess.run(["nvidia-smi"], capture_output=True, text=True, check=True)
        
        # Parse driver version from nvidia-smi output
        # Look for line like "Driver Version: 545.84"
        driver_version = None
        for line in result.stdout.split('\n'):
            if 'Driver Version:' in line:
                # Extract version number
                match = re.search(r'Driver Version:\s*(\d+\.\d+)', line)
                if match:
                    driver_version = match.group(1)
                    break
        
        if driver_version:
            # Check if driver is modern enough for CUDA 12.x
            try:
                version_num = float(driver_version)
                if version_num >= 530.0:  # Minimum for CUDA 12.x
                    return True, f"NVIDIA driver {driver_version} (CUDA 12.x compatible)"
                elif version_num >= 470.0:  # Minimum for CUDA 11.x
                    return True, f"NVIDIA driver {driver_version} (CUDA 11.x compatible, consider updating)"
                else:
                    return False, f"NVIDIA driver {driver_version} is too old (need 530+ for CUDA 12.x)"
            except ValueError:
                return True, f"NVIDIA driver {driver_version} (version check uncertain)"
        else:
            return False, "Could not parse NVIDIA driver version"
            
    except FileNotFoundError:
        return False, "nvidia-smi not found (cannot check driver version)"
    except subprocess.CalledProcessError:
        return False, "nvidia-smi failed (cannot check driver version)"

def check_cuda_directories():
    """Check for CUDA installation in common directories."""
    common_paths = [
        "C:\\Program Files\\NVIDIA GPU Computing Toolkit\\CUDA",
        "C:\\Program Files (x86)\\NVIDIA GPU Computing Toolkit\\CUDA"
    ]
    
    found_cuda = False
    latest_version = None
    cuda_dir = None
    
    for base_path in common_paths:
        if os.path.exists(base_path):
            # Look for version directories
            try:
                versions = [d for d in os.listdir(base_path) if os.path.isdir(os.path.join(base_path, d))]
                if versions:
                    latest_version = sorted(versions)[-1]  # Get latest version
                    cuda_dir = os.path.join(base_path, latest_version)
                    found_cuda = True
                    break
            except OSError:
                continue
    
    if found_cuda:
        return True, f"CUDA Toolkit found: {cuda_dir}"
    else:
        return False, "CUDA Toolkit directories not found"

def check_nvcc_compiler():
    """Check for CUDA compiler (nvcc)."""
    try:
        result = subprocess.run(["nvcc", "--version"], capture_output=True, text=True, check=True)
        
        # Extract CUDA version
        cuda_version = None
        for line in result.stdout.split('\n'):
            if 'release' in line.lower():
                # Look for pattern like "release 12.8, V12.8.89"
                match = re.search(r'release\s+([\d.]+)', line)
                if match:
                    cuda_version = match.group(1)
                    break
        
        if cuda_version:
            return True, f"CUDA compiler (nvcc) available, version {cuda_version}"
        else:
            return True, "CUDA compiler (nvcc) available"
        
    except FileNotFoundError:
        return False, "CUDA compiler (nvcc) not found in PATH"
    except subprocess.CalledProcessError:
        return False, "CUDA compiler (nvcc) failed to run"

def check_cuda_path_env():
    """Check CUDA_PATH environment variable (informational)."""
    cuda_path = os.environ.get("CUDA_PATH")
    if cuda_path and os.path.exists(cuda_path):
        return True, f"CUDA_PATH environment variable: {cuda_path}"
    else:
        return False, "CUDA_PATH environment variable not set or invalid"

def check_gpu_compute_capability():
    """Check GPU compute capability for modern AI workloads."""
    try:
        result = subprocess.run(["nvidia-smi", "--query-gpu=compute_cap", "--format=csv,noheader,nounits"], 
                              capture_output=True, text=True, check=True)
        
        compute_caps = result.stdout.strip().split('\n')
        if compute_caps and compute_caps[0]:
            try:
                # Parse compute capability (e.g., "8.9" -> 8.9)
                compute_cap = float(compute_caps[0].strip())
                
                if compute_cap >= 8.0:
                    return True, f"GPU compute capability {compute_cap} (excellent for AI)"
                elif compute_cap >= 6.0:
                    return True, f"GPU compute capability {compute_cap} (good for AI)"
                elif compute_cap >= 3.5:
                    return False, f"GPU compute capability {compute_cap} (limited AI support)"
                else:
                    return False, f"GPU compute capability {compute_cap} (too old for modern AI)"
            except ValueError:
                return True, f"GPU compute capability: {compute_caps[0]} (could not parse)"
        else:
            return False, "Could not determine GPU compute capability"
            
    except FileNotFoundError:
        return False, "nvidia-smi not found (cannot check compute capability)"
    except subprocess.CalledProcessError:
        return False, "Failed to query GPU compute capability"

def get_detailed_gpu_info():
    """
    Helper function to get comprehensive GPU information for diagnostics.
    Returns dict with all available GPU/CUDA info.
    """
    info = {}
    
    gpu_ok, gpu_msg = check_nvidia_gpu()
    info['gpu'] = (gpu_ok, gpu_msg)
    
    driver_ok, driver_msg = check_nvidia_driver_version()
    info['driver'] = (driver_ok, driver_msg)
    
    dirs_ok, dirs_msg = check_cuda_directories()
    info['cuda_installation'] = (dirs_ok, dirs_msg)
    
    nvcc_ok, nvcc_msg = check_nvcc_compiler()
    info['cuda_compiler'] = (nvcc_ok, nvcc_msg)
    
    path_ok, path_msg = check_cuda_path_env()
    info['cuda_environment'] = (path_ok, path_msg)
    
    compute_ok, compute_msg = check_gpu_compute_capability()
    info['compute_capability'] = (compute_ok, compute_msg)
    
    return info

def check_gpu_cuda_requirements():
    """Check all GPU and CUDA requirements (for orchestration)."""

    # Core requirements for GPU acceleration
    gpu_ok, _ = check_nvidia_gpu()
    driver_ok, _ = check_nvidia_driver_version()
    
    # CUDA development tools (needed for llama-cpp-python compilation)
    cuda_dirs_ok, _ = check_cuda_directories()
    nvcc_ok, _ = check_nvcc_compiler()
    
    # Environment configuration (helpful but not strictly required)
    cuda_path_ok, _ = check_cuda_path_env()
    
    # AI capability check (informational)
    compute_ok, _ = check_gpu_compute_capability()
    
    # Logic: Need GPU + reasonable driver + CUDA toolkit + (compiler OR environment)
    # This catches most working configurations while allowing for edge cases
    has_gpu_and_driver = gpu_ok and driver_ok
    has_cuda_toolkit = cuda_dirs_ok
    has_development_access = nvcc_ok or cuda_path_ok
    
    return has_gpu_and_driver and has_cuda_toolkit and has_development_access
