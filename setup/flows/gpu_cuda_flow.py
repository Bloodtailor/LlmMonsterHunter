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

def run_gpu_cuda_interactive_setup(current=None, total=None, dry_run=False):
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

    # Dry run mode - simulate common first-time setup scenario
    if dry_run:
        print_dry_run_header("Running as a dry run")
        
        from setup.dry_run_utils import set_dry_run
        # Most common first-time setup: GPU works, but drivers/CUDA need setup
        gpu_ok, gpu_message = set_dry_run('check_nvidia_gpu')
        driver_ok, driver_message = set_dry_run('check_nvidia_driver_version')
        cuda_dirs_ok, cuda_dirs_message = set_dry_run('check_cuda_directories')
        nvcc_ok, nvcc_message = set_dry_run('check_nvcc_compiler')
        cuda_path_ok, cuda_path_message = set_dry_run('check_cuda_path_env')
        compute_ok, compute_message = set_dry_run('check_gpu_compute_capability')

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
    
    # TODO: Handle CUDA toolkit installation
    # TODO: Handle CUDA environment/PATH issues
    
    print_warning("GPU detected but remaining CUDA issues need to be handled")
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
        print("  [C] Continue with CUDA setup anyway (I have an NVIDIA GPU)")
        print("  [T] Get troubleshooting instructions to fix GPU detection")  
        print("  [S] Skip GPU setup and continue with other components")
        print("  [E] Exit setup entirely")
        print()
        
        choice = input("Your choice [C/T/S/E]: ").strip().upper()
        

        if choice == "C":
            print("Continuing... ")
            print()
            return True

        elif choice == "T":
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
            print("Please enter C, T, S, or E")
            print()

def handle_driver_issues(driver_message):
    """
    Handle NVIDIA driver problems
    
    Args:
        driver_message (str): Message from driver version check
        
    Returns:
        bool: True if user wants to continue, False to exit component
    """
    
    print("NVIDIA Driver Issues Detected")
    print()
    print_error(driver_message)
    print()
    
    # Determine issue type based on message
    if driver_message and "too old" in driver_message.lower():
        show_message('gpu_driver_outdated')
    else:
        show_message('gpu_driver_general_issues')
    
    print()
    
    # Present user options
    while True:
        print("Choose how to proceed:")
        print("  [F] Get instructions to fix driver issues")
        print("  [C] Continue with current drivers anyway")
        print("  [S] Skip GPU setup and continue with other components")
        print("  [E] Exit setup entirely")
        print()
        
        choice = input("Your choice [F/C/S/E]: ").strip().upper()
        
        if choice == "F":
            print()
            show_message('gpu_driver_fix_instructions')
            print()
            
            # Give option to re-check after following instructions
            while True:
                print("Choose how to proceed:")
                print("  [R] Re-check drivers now")
                print("  [C] Continue with current drivers anyway")
                print("  [E] Exit setup")
                print()
                
                recheck_choice = input("Your choice [R/C/E]: ").strip().upper()
                
                if recheck_choice == "R":
                    print()
                    print("Re-checking NVIDIA drivers...")
                    
                    # Re-run driver check
                    new_driver_ok, new_driver_message = check_nvidia_driver_version()
                    
                    if new_driver_ok:
                        print_success("Driver issues resolved!")
                        print(new_driver_message)
                        print()
                        return True
                    else:
                        print_warning("Driver issues still detected:")
                        print(new_driver_message)
                        print()
                        print("You can try the fix instructions again or continue anyway.")
                        # Loop back to give them the options again
                        
                elif recheck_choice == "C":
                    print()
                    print("Continuing with current driver setup...")
                    print_info("Driver issues may cause problems later")
                    print()
                    return True
                    
                elif recheck_choice == "E":
                    print()
                    print("Exiting setup...")
                    print()
                    import sys
                    sys.exit(0)
                    
                else:
                    print("Please enter R, C, or E")
                    print()
                
        elif choice == "C":
            print()
            print_continue("Continuing with current drivers...")
            print_info("Driver issues may cause problems with CUDA compilation")
            print()
            return True
            
        elif choice == "S":
            print()
            print_continue("Skipping GPU setup...")
            print_info("You can complete this later after fixing driver issues")
            print()
            return False
            
        elif choice == "E":
            print()
            print("Exiting setup...")
            print()
            import sys
            sys.exit(0)
            
        else:
            print("Please enter F, C, S, or E")
            print()

if __name__ == "__main__":
    run_gpu_cuda_interactive_setup(dry_run=True)