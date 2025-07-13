#!/usr/bin/env python3
"""
GPU CUDA Interactive Setup Flow
Orchestrates the complete GPU and CUDA setup experience with clean UX
"""

from setup.ux_utils import *
from setup.checks.gpu_cuda_checks import (
    check_nvidia_gpu,
    check_nvidia_driver_version,
    check_cuda_directories,
    check_nvcc_compiler,
    check_cuda_path_env,
    check_gpu_compute_capability,
    get_detailed_gpu_info
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
        description="Required for GPU-accelerated AI inference (35x faster than CPU)"
    )

    print("Checking current status...")
    
    # Get comprehensive GPU/CUDA information
    gpu_info = get_detailed_gpu_info()
    
    # Package results for display (all 6 checks)
    check_results = {
        "NVIDIA GPU": gpu_info['gpu'],
        "Driver Version": gpu_info['driver'], 
        "CUDA Installation": gpu_info['cuda_installation'],
        "Development Tools": gpu_info['cuda_compiler'],
        "Environment Config": gpu_info['cuda_environment'],
        "Compute Capability": gpu_info['compute_capability']
    }
    
    # Display results beautifully
    overall_ok = display_check_results("GPU & CUDA", check_results)
    
    # If everything is working, we're done!
    if overall_ok:
        print("GPU & CUDA setup is complete!")
        print("🚀 LLM inference will be 35x faster than CPU")
        print("🚀 ComfyUI image generation will be lightning fast")
        return True
    
    # Analyze what's wrong and handle in priority order
    gpu_ok = gpu_info['gpu'][0]
    driver_ok = gpu_info['driver'][0]
    cuda_ok = gpu_info['cuda_installation'][0]
    compiler_ok = gpu_info['cuda_compiler'][0]
    env_ok = gpu_info['cuda_environment'][0] 
    compute_ok = gpu_info['compute_capability'][0]
    
    # Priority 1: No GPU at all
    if not gpu_ok:
        if not handle_no_gpu():
            return False
    
    # Priority 2: GPU but old/bad drivers  
    if not driver_ok:
        return handle_driver_issues(gpu_info['driver'][1])
    
    # Priority 3: GPU + drivers but no CUDA toolkit
    if not cuda_ok:
        return handle_missing_cuda_toolkit()
    
    # Priority 4: CUDA installed but development tools not accessible
    if not compiler_ok and not env_ok:
        return handle_environment_issues()
    
    # Priority 5: Everything works but compute capability is low
    if not compute_ok:
        return handle_low_compute_capability(gpu_info['compute_capability'][1])
    
    # This shouldn't happen, but handle unexpected states
    print_warning("GPU setup is in an unexpected state.")
    return offer_expert_bypass()

def handle_no_gpu():
    """Handle case where no NVIDIA GPU is detected"""
    print_error("No NVIDIA GPU detected.")
    print()
    
    show_message('no_nvidia_gpu_detected')
    
    while True:
        choice = input("You have several options:\n"
                      "1. [R]equirements - See what NVIDIA hardware you need\n"
                      "2. [C]ontinue anyway - Set up CPU-only mode (very slow)\n"
                      "3. [S]kip this component - Come back later when you have NVIDIA GPU\n"
                      "4. [Q]uit setup\n\n"
                      "What would you like to do? [R/C/S/Q]: ").strip().upper()
        
        if choice == 'R':
            show_message('gpu_hardware_requirements')
            print()
        elif choice == 'C':
            print()
            print_continue("Continuing with CPU-only setup...")
            print_info("Game will be very slow but functional for testing")
            return False  # Not truly "successful" but continue setup
        elif choice == 'S':
            print()
            print_continue("Skipping GPU setup...")
            print_info("You can run this setup again later")
            return False
        elif choice == 'Q':
            print()
            print("Exiting setup...")
            import sys
            sys.exit(0)
        else:
            print("Please enter R, C, S, or Q")

def handle_driver_issues(driver_message):
    """Handle outdated or problematic NVIDIA drivers"""
    print_error("NVIDIA driver issues detected.")
    print(driver_message)
    print()
    
    show_message('nvidia_driver_issues_detected')
    
    show_message('nvidia_driver_update')
    
    choice = input("Continue with driver update? [Y/n]: ").strip()
    if choice.lower() in ['n', 'no']:
        print()
        print_continue("Skipping driver update...")
        print_info("GPU acceleration will not work until drivers are updated")
        return False
    
    print()
    show_message_and_wait('nvidia_driver_update_steps', "Press Enter after updating drivers...")
    
    return verify_gpu_setup()

def handle_missing_cuda_toolkit():
    """Handle missing CUDA Toolkit installation"""
    print_warning("CUDA Toolkit missing - this will prevent GPU acceleration.")
    print()
    
    show_message('cuda_toolkit_missing')
    
    show_message('cuda_toolkit_installation')
    
    choice = input("Continue with CUDA installation, or skip? [Y/s]: ").strip()
    if choice.lower() in ['s', 'skip']:
        print()
        print_continue("Continuing without CUDA Toolkit...")
        print_info("You can install CUDA later for GPU acceleration")
        return False
    
    print()
    show_message_and_wait('cuda_toolkit_installation_steps', 
                         "Press Enter after installing CUDA Toolkit...")
    
    return verify_gpu_setup()

def handle_environment_issues():
    """Handle CUDA installed but environment/PATH problems"""
    print_warning("CUDA is installed but development tools are not accessible.")
    print()
    
    show_message('cuda_environment_issues')
    
    show_message('cuda_environment_setup')
    
    choice = input("Fix environment configuration? [Y/n]: ").strip()
    if choice.lower() in ['n', 'no']:
        print()
        print_continue("Skipping environment setup...")
        print_info("GPU compilation may fail but runtime might work")
        return True  # Partial success - might work for ComfyUI
    
    print()
    show_message_and_wait('cuda_environment_setup_steps',
                         "Press Enter after fixing environment...")
    
    return verify_gpu_setup()

def handle_low_compute_capability(compute_message):
    """Handle GPU with low compute capability"""
    print_warning("GPU compute capability may limit AI performance.")
    print(f"Your GPU: {compute_message}")
    print()
    
    show_message('low_compute_capability_warning')
    
    choice = input("Continue with current GPU? [Y/n]: ").strip()
    if choice.lower() in ['n', 'no']:
        show_message('gpu_upgrade_recommendations')
        print()
        return False
    
    print()
    print_continue("Continuing with current GPU...")
    print_info("Most models should work, but performance may vary")
    return True

def offer_expert_bypass():
    """Offer expert users a way to bypass checks"""
    show_message('expert_bypass_offer')
    
    choice = input("Bypass GPU checks and continue? [y/N]: ").strip()
    if choice.lower() in ['y', 'yes']:
        print()
        print_continue("Bypassing GPU checks...")
        print_info("You're responsible for ensuring GPU acceleration works")
        return True
    
    print()
    print_continue("GPU setup incomplete...")
    return False

def verify_gpu_setup():
    """Re-verify GPU setup after user makes changes"""
    print("Verifying GPU setup...")
    print()
    
    # Re-run all checks
    gpu_info = get_detailed_gpu_info()
    
    # Package results for display
    check_results = {
        "NVIDIA GPU": gpu_info['gpu'],
        "Driver Version": gpu_info['driver'], 
        "CUDA Installation": gpu_info['cuda_installation'],
        "Development Tools": gpu_info['cuda_compiler'],
        "Environment Config": gpu_info['cuda_environment'],
        "Compute Capability": gpu_info['compute_capability']
    }
    
    # Show verification results
    overall_ok = display_check_results("GPU & CUDA", check_results)
    
    if overall_ok:
        print_success("GPU & CUDA setup completed successfully!")
        print("🚀 GPU acceleration is ready for AI workloads")
        return True
    else:
        print_warning("Some GPU/CUDA issues remain.")
        return offer_expert_bypass()

if __name__ == "__main__":
    run_gpu_cuda_interactive_setup()