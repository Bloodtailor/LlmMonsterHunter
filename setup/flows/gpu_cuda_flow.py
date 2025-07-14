#!/usr/bin/env python3
"""
GPU CUDA Interactive Setup Flow
Orchestrates the complete NVIDIA GPU and CUDA setup experience with clean UX
"""
COMPONENT_NAME = "NVIDIA GPU & CUDA"

from setup.utils.ux_utils import *
from setup.checks.gpu_cuda_checks import (
    check_nvidia_gpu,
    check_nvidia_driver_version, 
    check_cuda_directories,
    check_nvcc_compiler,
    check_cuda_path_env,
    check_gpu_compute_capability
)

def run_gpu_cuda_interactive_setup(current=None, total=None, dry_run=False):
    """
    Interactive setup flow for NVIDIA GPU and CUDA toolkit
    
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
        description="Required for GPU-accelerated AI model inference"
    )

    print("Checking current status...")
    
    # Run individual checks
    gpu_ok, gpu_message = check_nvidia_gpu()
    compute_ok, compute_message = check_gpu_compute_capability()
    driver_ok, driver_message = check_nvidia_driver_version()
    cuda_dirs_ok, cuda_dirs_message = check_cuda_directories()
    nvcc_ok, nvcc_message = check_nvcc_compiler()
    cuda_path_ok, cuda_path_message = check_cuda_path_env()


    # Dry run mode - simulate common first-time setup scenario
    if dry_run:
        print_dry_run_header()
        
        from setup.utils.dry_run_utils import set_dry_run
        # Most common first-time setup: GPU works, but drivers/CUDA need setup
        gpu_ok, gpu_message = set_dry_run('check_nvidia_gpu')
        compute_ok, compute_message = set_dry_run('check_gpu_compute_capability')
        driver_ok, driver_message = set_dry_run('check_nvidia_driver_version')
        cuda_dirs_ok, cuda_dirs_message = set_dry_run('check_cuda_directories')
        nvcc_ok, nvcc_message = set_dry_run('check_nvcc_compiler')
        cuda_path_ok, cuda_path_message = set_dry_run('check_cuda_path_env')
        

    # Package results for display
    check_results = {
        "NVIDIA GPU": (gpu_ok, gpu_message),
        "GPU Capability": (compute_ok, compute_message),
        "NVIDIA Drivers": (driver_ok, driver_message),
        "CUDA Toolkit": (cuda_dirs_ok, cuda_dirs_message),
        "CUDA Compiler": (nvcc_ok, nvcc_message),
        "CUDA Environment": (cuda_path_ok, cuda_path_message),\

    }

    # Display results beautifully
    overall_ok = display_check_results("GPU & CUDA", check_results)

    # ================================================================
    # SECTION 2: INTERACTIVE SETUP FLOWS AND LOGIC
    # ================================================================

    # If everything is working, we're done!
    if overall_ok:
        print("All GPU and CUDA components are ready!")
        return True
    
    # Show the requirement explanation
    show_message_and_wait('gpu_requirement_explanation')
    
    # Now handle specific issues in dependency order
    if not gpu_ok:
        if not handle_no_gpu_detected(check_results):
            return False
    else:
        print(f"NVIDIA GPU Detected")
        print(gpu_message)
        print()

        # Let the user know their GPU Capability
        if compute_ok:
            print("Your GPU is likely fast enough to run the game")
            print(compute_message)
            show_message_and_wait('gpu_hardware_capable')
        else:
            print("Your GPU may not be fast enough to run the game")
            print_error(compute_message)
            show_message_and_wait('gpu_hardware_not_capable')

    # Handle driver issues (foundation layer)
    if not driver_ok:
        if not handle_driver_issues(driver_message):
            return False

    # Handle CUDA toolkit installation (foundation for GPU acceleration)
    if not cuda_dirs_ok:
        if not handle_cuda_toolkit_missing(cuda_dirs_message):
            return False
        # Re-check CUDA after potential installation
        cuda_dirs_ok, cuda_dirs_message = check_cuda_directories()

    # Handle CUDA environment/PATH issues (requires toolkit to be installed)
    if not nvcc_ok or not cuda_path_ok:
        if not handle_cuda_environment_issues(nvcc_ok, nvcc_message, cuda_path_ok, cuda_path_message):
            return False

    # ================================================================
    # SECTION 3: FINAL CHECKS AND DISPLAY
    # ================================================================


    # Final verification - run all checks again
    print("Verifying complete GPU and CUDA setup...")
    print()

    # Re-run all checks
    gpu_ok, gpu_message = check_nvidia_gpu()
    compute_ok, compute_message = check_gpu_compute_capability()
    driver_ok, driver_message = check_nvidia_driver_version()
    cuda_dirs_ok, cuda_dirs_message = check_cuda_directories()
    nvcc_ok, nvcc_message = check_nvcc_compiler()
    cuda_path_ok, cuda_path_message = check_cuda_path_env()


    # Package final results
    final_check_results = {
        "NVIDIA GPU": (gpu_ok, gpu_message),
        "GPU Capability": (compute_ok, compute_message),
        "NVIDIA Drivers": (driver_ok, driver_message),
        "CUDA Toolkit": (cuda_dirs_ok, cuda_dirs_message),
        "CUDA Compiler": (nvcc_ok, nvcc_message),
        "CUDA Environment": (cuda_path_ok, cuda_path_message)

    }

    # Display final results
    final_overall_ok = display_check_results("GPU & CUDA FINAL", final_check_results)

    if final_overall_ok:
        print_success("GPU and CUDA setup completed successfully!")
        print("🚀 Ready for GPU-accelerated AI inference")
        print()
        return True
    else:
        print_warning("GPU setup completed with some issues remaining.")
        print_info("The game may still work but with reduced performance.")
        print()
        return True  # Return True to continue - partial setup is better than nothing

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
    
    options = [
        ("G", "Get troubleshooting instructions to fix GPU detection")
    ]

    choice = handle_user_choice(options, COMPONENT_NAME)

    if choice == "G":
        if cuda_signs:
            show_message('gpu_driver_troubleshooting')
        else:
            show_message('gpu_hardware_troubleshooting') 
        return prompt_continue_or_skip(COMPONENT_NAME)
    elif choice == "CONTINUE":
        return True
    else:
        return False  


def handle_driver_issues(driver_message):
    """
    Handle NVIDIA driver problems
    
    Args:
        driver_message (str): Message from driver version check
        
    Returns:
        bool: True if user wants to continue, False to exit component
    """
    
    print("NVIDIA Driver Issues Detected")
    print_error(driver_message)
    
    # Determine issue type based on message
    if driver_message and "too old" in driver_message.lower():
        show_message('gpu_driver_outdated')
    else:
        show_message('gpu_driver_general_issues')
    
    options = [
        ("G", "Get instructions to fix driver issues")
    ]

    choice = handle_user_choice(options, COMPONENT_NAME)

    if choice == "G":
        return handle_driver_fix_instructions()
    elif choice == "CONTINUE":
        return True
    else:
        return False         

def handle_driver_fix_instructions():
    """Display instructions on how to manually fix driver issue"""

    show_message('gpu_driver_fix_instructions')

    return prompt_continue_or_skip(COMPONENT_NAME)


def handle_cuda_toolkit_missing(cuda_dirs_message):
    """
    Handle missing CUDA toolkit installation
    
    Args:
        cuda_dirs_message (str): Message from CUDA directories check
        
    Returns:
        bool: True if user wants to continue, False to exit component
    """
    
    print("CUDA Toolkit Not Found")
    print_error(cuda_dirs_message)
    
    show_message('cuda_toolkit_missing')

    options = [
        ("G", "Get CUDA toolkit installation instructions")
    ]

    choice = handle_user_choice(options, COMPONENT_NAME)

    if choice == "G":
        return handle_cuda_toolkit_installation_instructions()
    elif choice == "CONTINUE":
        return True
    else:
        return False  

def handle_cuda_toolkit_installation_instructions():
    """Display instruction on how to manually install cuda toolkit"""
    
    show_message('cuda_toolkit_installation')
 
    options = [
        ("R", "Re-check CUDA toolkit installation")
    ]

    choice = handle_user_choice(options, COMPONENT_NAME)

    if choice == "R":
        return handle_cuda_toolkit_recheck()
    elif choice == "CONTINUE":
        return True
    else:
        return False

def handle_cuda_toolkit_recheck():
    """Run cuda toolkit check and displays results"""

    print("Re-checking CUDA toolkit installation...")
    
    # Re-run CUDA directories check
    cuda_ok, cuda_message = check_cuda_directories()
    
    if cuda_ok:
        print_success("CUDA toolkit installation detected!")
        print(cuda_message)
        print()
        return True
    else:
        print_warning("CUDA toolkit still not found:")
        print(cuda_message)
        print()
        print("You can try the installation instructions again or continue anyway.")
        handle_cuda_environment_issues(cuda_message)

def handle_cuda_environment_issues(nvcc_ok, nvcc_message, cuda_path_ok, cuda_path_message):
    """
    Handle CUDA environment and PATH configuration issues
    
    Args:
        nvcc_ok (bool): Whether nvcc compiler is available
        nvcc_message (str): Message from nvcc check
        cuda_path_ok (bool): Whether CUDA_PATH is set
        cuda_path_message (str): Message from CUDA_PATH check
        
    Returns:
        bool: True if user wants to continue, False to exit component
    """
    
    print("CUDA Environment Configuration Issues")
    print()
    
    # Show specific issues
    if nvcc_ok:
        print_success(nvcc_message)
    else:
        print_error(nvcc_message)

    if cuda_path_ok:
        print_success(cuda_path_message)
    else:
        print_error(cuda_path_message)
    
    print()
    print("CUDA toolkit appears to be installed but is not properly configured.")
    print()
    
    show_message('cuda_environment_issues')
    
    options = [
        ("G", "Get instructions to fix CUDA environment")
    ]

    choice = handle_user_choice(options, COMPONENT_NAME)

    if choice == "G":
        return handle_cuda_environment_fix_instructions()
    elif choice == "CONTINUE":
        return True
    else:
        return False
    
def handle_cuda_environment_fix_instructions():
    """Display instructions on how to manually fix CUDA environment """

    show_message('cuda_environment_fix')

    options = [
        ("R", "Re-check CUDA environment")
    ]

    choice = handle_user_choice(options, COMPONENT_NAME)

    if choice == "R":
        return handle_recheck_cuda()
    elif choice == "CONTINUE":
        return True
    else:
        return False

def handle_recheck_cuda():
    """Run CUDA environment checks and displays results"""

    print("Re-checking CUDA environment...")
    
    # Re-run environment checks
    nvcc_ok, nvcc_message = check_nvcc_compiler()
    cuda_path_ok, cuda_path_message = check_cuda_path_env()
    
    if nvcc_ok and cuda_path_ok:
        print_success("CUDA environment issues resolved!")
        print(f"Compiler: {nvcc_message}")
        print(f"Environment: {cuda_path_message}")
        print()
        return True
    else:
        print_warning("CUDA environment issues still detected:")
        if not nvcc_ok:
            print(f"  Compiler: {nvcc_message}")
        if not cuda_path_ok:
            print(f"  Environment: {cuda_path_message}")
        print()
        print("You can try the fix instructions again or continue anyway.")
        handle_cuda_environment_issues(nvcc_ok, nvcc_message, cuda_path_ok, cuda_path_message)
                

if __name__ == "__main__":
    from setup.utils.dry_run_utils import run_as_standalone_component
    run_as_standalone_component(COMPONENT_NAME, run_gpu_cuda_interactive_setup)