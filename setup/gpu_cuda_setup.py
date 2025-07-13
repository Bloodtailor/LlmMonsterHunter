#!/usr/bin/env python3
"""
NVIDIA GPU and CUDA Toolkit Setup Module
Checks for NVIDIA GPU, drivers, and CUDA toolkit installation
"""

import os
import subprocess
import sys
from pathlib import Path

def check_nvidia_gpu():
    """Check for NVIDIA GPU and drivers using nvidia-smi."""
    try:
        result = subprocess.run(["nvidia-smi"], capture_output=True, text=True, check=True)
        print("✅ NVIDIA GPU detected")
        
        # Parse GPU info from nvidia-smi output
        lines = result.stdout.split('\n')
        for line in lines:
            # Look for GPU info line
            if any(gpu in line for gpu in ['GeForce', 'RTX', 'GTX', 'Quadro', 'Tesla']):
                parts = line.split('|')
                if len(parts) > 1:
                    gpu_info = parts[1].strip()
                    print(f"   GPU: {gpu_info}")
                break
        
        # Parse VRAM info
        for line in lines:
            if 'MiB' in line and '/' in line:
                # Look for memory usage line
                parts = line.split('|')
                for part in parts:
                    if 'MiB' in part and '/' in part:
                        memory_info = part.strip()
                        print(f"   Memory: {memory_info}")
                        break
                break
        
        return True
        
    except FileNotFoundError:
        print("❌ nvidia-smi not found (NVIDIA drivers not installed)")
        return False
    except subprocess.CalledProcessError:
        print("❌ nvidia-smi failed (GPU or driver issues)")
        return False

def check_cuda_path_env():
    """Check CUDA_PATH environment variable."""
    cuda_path = os.environ.get("CUDA_PATH")
    if cuda_path and os.path.exists(cuda_path):
        print(f"✅ CUDA_PATH environment variable: {cuda_path}")
        return True
    else:
        print("❌ CUDA_PATH environment variable not set or invalid")
        return False

def check_nvcc_compiler():
    """Check for CUDA compiler (nvcc)."""
    try:
        result = subprocess.run(["nvcc", "--version"], capture_output=True, text=True, check=True)
        print("✅ CUDA compiler (nvcc) available")
        
        # Extract CUDA version
        for line in result.stdout.split('\n'):
            if 'release' in line.lower():
                parts = line.split('release')[1].split(',')[0].strip()
                print(f"   CUDA Version: {parts}")
                break
        
        return True
    except FileNotFoundError:
        print("❌ CUDA compiler (nvcc) not found")
        return False
    except subprocess.CalledProcessError:
        print("❌ CUDA compiler (nvcc) failed")
        return False

def check_cuda_directories():
    """Check for CUDA installation in common directories."""
    common_paths = [
        "C:\\Program Files\\NVIDIA GPU Computing Toolkit\\CUDA",
        "C:\\Program Files (x86)\\NVIDIA GPU Computing Toolkit\\CUDA"
    ]
    
    found_cuda = False
    for base_path in common_paths:
        if os.path.exists(base_path):
            # Look for version directories
            try:
                versions = [d for d in os.listdir(base_path) if os.path.isdir(os.path.join(base_path, d))]
                if versions:
                    latest_version = sorted(versions)[-1]  # Get latest version
                    cuda_dir = os.path.join(base_path, latest_version)
                    print(f"✅ CUDA Toolkit found: {cuda_dir}")
                    found_cuda = True
                    break
            except OSError:
                continue
    
    if not found_cuda:
        print("❌ CUDA Toolkit directories not found")
    
    return found_cuda

def check_gpu_cuda_requirements():
    """Check all GPU and CUDA requirements."""
    print("Checking NVIDIA GPU and CUDA requirements...")
    
    # Check individual components
    gpu_detected = check_nvidia_gpu()
    cuda_path_set = check_cuda_path_env()
    nvcc_available = check_nvcc_compiler()
    cuda_installed = check_cuda_directories()
    
    # Determine overall status
    if gpu_detected and (nvcc_available or cuda_installed):
        print("✅ NVIDIA GPU and CUDA Toolkit are available")
        return True
    elif gpu_detected and cuda_installed:
        print("⚠️  NVIDIA GPU found but CUDA may not be properly configured")
        return False
    elif gpu_detected:
        print("⚠️  NVIDIA GPU found but CUDA Toolkit not installed")
        return False
    else:
        print("❌ NVIDIA GPU not detected")
        return False

def setup_gpu_cuda_interactive():
    """Interactive setup guidance for GPU and CUDA."""
    print("Setting up NVIDIA GPU and CUDA support...")
    
    # Check GPU first
    if not check_nvidia_gpu():
        print("\n❌ NVIDIA GPU not detected")
        print("📋 This could mean:")
        print("1. You don't have an NVIDIA GPU")
        print("2. NVIDIA drivers are not installed")
        print("3. GPU is disabled in BIOS/UEFI")
        print("")
        print("📋 To fix this:")
        print("1. Verify you have an NVIDIA GPU (check Device Manager)")
        print("2. Download latest drivers from https://www.nvidia.com/drivers/")
        print("3. Restart after installation")
        print("4. Run 'nvidia-smi' command to test")
        print("")
        
        choice = input("Do you want to continue setup anyway? (y/n): ").lower().strip()
        if choice not in ['y', 'yes']:
            return False
    
    # Check CUDA installation
    if not check_cuda_directories():
        print("\n❌ CUDA Toolkit not installed")
        print("📋 To install CUDA Toolkit:")
        print("1. Go to https://developer.nvidia.com/cuda-toolkit")
        print("2. Download CUDA Toolkit 12.x (latest stable)")
        print("3. Run the installer with these options:")
        print("   - Express installation (recommended)")
        print("   - Or Custom: Select CUDA Toolkit, samples, documentation")
        print("4. Restart your computer after installation")
        print("5. Verify with 'nvcc --version' command")
        print("")
        
        input("Press Enter after installing CUDA Toolkit...")
        
        # Check again
        if not check_cuda_directories():
            print("❌ CUDA Toolkit still not found")
            print("⚠️  You can still run the game with CPU-only inference (slower)")
            
            choice = input("Continue without CUDA? (y/n): ").lower().strip()
            if choice not in ['y', 'yes']:
                return False
    
    # Check CUDA PATH and compiler
    if not check_nvcc_compiler():
        print("\n⚠️  CUDA compiler not available")
        print("📋 This usually means:")
        print("1. CUDA Toolkit is installed but not in PATH")
        print("2. Installation was incomplete")
        print("")
        print("📋 To fix:")
        print("1. Add CUDA bin directory to system PATH:")
        print("   Typical path: C:\\Program Files\\NVIDIA GPU Computing Toolkit\\CUDA\\v12.x\\bin")
        print("2. Set CUDA_PATH environment variable:")
        print("   Typical path: C:\\Program Files\\NVIDIA GPU Computing Toolkit\\CUDA\\v12.x")
        print("3. Restart command prompt after making changes")
        print("4. Test with 'nvcc --version'")
        print("")
        
        choice = input("Continue with current CUDA setup? (y/n): ").lower().strip()
        if choice not in ['y', 'yes']:
            return False
    
    # Final status
    if check_nvidia_gpu():
        if check_cuda_directories():
            print("✅ GPU and CUDA setup completed")
            print("🚀 LLM models will run with GPU acceleration")
        else:
            print("⚠️  GPU detected but CUDA setup incomplete")
            print("💡 Models will run on CPU (slower but functional)")
        return True
    else:
        print("❌ GPU setup could not be completed")
        print("💡 Models will run on CPU only")
        return False

if __name__ == "__main__":

    setup_gpu_cuda_interactive()
