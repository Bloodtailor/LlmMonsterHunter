#!/usr/bin/env python3
"""
GPU CUDA Interactive Setup Flow
Orchestrates the complete NVIDIA GPU and CUDA setup experience with clean UX
"""

from setup.ux_utils import *
from setup.checks.gpu_cuda_checks import (
    check_nvidia_gpu,
    check_nvidia_driver_version, 
    check_cuda_directories,
    check_nvcc_compiler,
    check_cuda_path_env,
    check_gpu_compute_capability
)

def run_gpu_cuda_interactive_setup(current=None, total=None):
    """
    Interactive setup flow for NVIDIA GPU and CUDA toolkit
    
    Returns:
        bool: True if setup completed successfully, False otherwise
    """
    
    # Show clean component header
    show_component_header(
        component_name="NVIDIA GPU & CUDA",
        current=current,
        total=total,
        description="Required for GPU-accelerated AI model inference"
    )

    print("Checking current status...")
    
    # Run individual checks
    gpu_ok, gpu_message = check_nvidia_gpu()
    driver_ok, driver_message = check_nvidia_driver_version()
    cuda_dirs_ok, cuda_dirs_message = check_cuda_directories()
    nvcc_ok, nvcc_message = check_nvcc_compiler()
    cuda_path_ok, cuda_path_message = check_cuda_path_env()
    compute_ok, compute_message = check_gpu_compute_capability()

    # Package results for display
    check_results = {
        "NVIDIA GPU": (gpu_ok, gpu_message),
        "NVIDIA Drivers": (driver_ok, driver_message),
        "CUDA Toolkit": (cuda_dirs_ok, cuda_dirs_message),
        "CUDA Compiler": (nvcc_ok, nvcc_message),
        "CUDA Environment": (cuda_path_ok, cuda_path_message),
        "GPU Capability": (compute_ok, compute_message)
    }

    # Display results beautifully
    overall_ok = display_check_results("GPU & CUDA", check_results)
    
    # If everything is working, we're done!
    if overall_ok:
        print("All GPU and CUDA components are ready!")
        return True
    
    # Show the requirement explanation
    show_message_and_wait('gpu_requirement_explanation')
    
    # Now handle specific issues
    if not gpu_ok:
        return handle_no_gpu_detected(check_results)
    
    # TODO: Handle other cases (GPU detected but other issues)
    print_warning("GPU detected but other CUDA issues need to be handled")
    return False

def handle_no_gpu_detected(check_results):
    """
    Handle case where NVIDIA GPU is not detected
    Provides different troubleshooting guidance based on whether CUDA components are present
    
    Args:
        check_results (dict): Results from all GPU/CUDA checks
        
    Returns:
        bool: Always False (component setup cannot continue)
    """
    
    # Analyze diagnostic information
    cuda_signs = any([
        check_results["CUDA Toolkit"][0],      # CUDA directories exist
        check_results["CUDA Compiler"][0],     # nvcc command works  
        check_results["CUDA Environment"][0]   # CUDA_PATH set
    ])
    
    print("Diagnosing GPU detection failure...")
    print()
    
    # Show appropriate diagnostic message
    if cuda_signs:
        show_message('gpu_driver_issue_detected')
    else:
        show_message('gpu_hardware_missing')
    
    print()
    
    # Present troubleshooting options
    while True:
        print("Choose how to proceed:")
        print("  [T] Get troubleshooting instructions to fix GPU detection")  
        print("  [S] Skip GPU setup and continue with other components")
        print("  [E] Exit setup entirely")
        print()
        
        choice = input("Your choice [T/S/E]: ").strip().upper()
        
        if choice == "T":
            print()
            if cuda_signs:
                show_message_and_wait('gpu_driver_troubleshooting')
            else:
                show_message_and_wait('gpu_hardware_troubleshooting') 
            
            print()
            print("End: Troubleshooting Instructions")
            print("You can run this setup again after fixing GPU issues")
            print()
            print("Please choose an option other than [T]")
            print()
            
        elif choice == "S":
            print()
            print_continue("Continuing setup without GPU acceleration...")
            print_info("Remember: You can run this setup again after fixing GPU issues")
            print()
            return False  # Exit this component, continue to next
            
        elif choice == "E":
            print()
            print("Exiting setup...")
            print()
            import sys
            sys.exit(0)
            
        else:
            print("Please enter T, S, or E")
            print()