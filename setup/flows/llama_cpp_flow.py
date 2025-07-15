#!/usr/bin/env python3
"""
LLama-cpp-python Interactive Setup Flow
Orchestrates the complete llama-cpp-python setup experience with clean UX
"""
COMPONENT_NAME = "LLM Integration"

from setup.utils.ux_utils import *
from setup.checks.llama_cpp_checks import (
    check_llama_cpp_installed,
    test_llama_cpp_import,
    test_llama_cpp_performance
)
from setup.installation.llama_cpp_installation import (
    install_llama_cpp_cpu_only,
    install_llama_cpp_with_retry
)

def run_llama_cpp_interactive_setup(current=None, total=None, dry_run=False):
    """
    Interactive setup flow for llama-cpp-python with CUDA acceleration
    
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
        description="GPU-accelerated AI language model inference library"
    )

    print("Checking current status...")
    
    # Run individual checks
    installed_ok, installed_message = check_llama_cpp_installed()
    import_ok, import_message = test_llama_cpp_import()
    performance_ok, performance_message = test_llama_cpp_performance()

    # Dry run mode - set check results to custom values
    if dry_run:
        print_dry_run_header()
        
        from setup.utils.dry_run_utils import set_dry_run
        # Most common scenario: Not installed yet
        installed_ok, installed_message = set_dry_run('check_llama_cpp_installed')
        import_ok, import_message = set_dry_run('test_llama_cpp_import')
        performance_ok, performance_message = set_dry_run('test_llama_cpp_performance')

    # Package results for display
    check_results = {
        "Installation": (installed_ok, installed_message),
        "Import Test": (import_ok, import_message),
        "Performance Test": (performance_ok, performance_message)
    }

    # Display results beautifully
    overall_ok = display_check_results("LLM INTEGRATION", check_results)

    # ================================================================
    # SECTION 2: INTERACTIVE SETUP FLOWS AND LOGIC
    # ================================================================

    # If everything is working great, we're done!
    if overall_ok and performance_ok:
        print("LLM integration is ready and performing well!")
        print("🚀 Ready for fast AI inference")
        print()
        return True
    
    # If installed and imports but performance is poor
    if installed_ok and import_ok and not performance_ok:
        print("LLM integration is installed but performance is poor.")
        print_warning(performance_message)
        print()
        return handle_poor_performance(performance_message)
    
    # If installed but import fails
    if installed_ok and not import_ok:
        print("LLM integration is installed but not working properly.")
        print_error(import_message)
        print()
        return handle_broken_installation()
    
    # If not installed at all
    if not installed_ok:
        print("LLM integration needs to be installed.")
        print()
        return handle_fresh_installation()
    
    # Fallback case
    print_warning("LLM integration status unclear - proceeding with installation")
    print()
    return handle_fresh_installation()

def handle_fresh_installation():
    """Handle case where llama-cpp-python is not installed"""
    
    show_message('llama_cpp_requirement_explanation')
    
    options = [
        ("A", "Install with CUDA acceleration (recommended)"),
        ("I", "Install CPU-only version (very slow, not recommended)")
    ]

    choice = handle_user_choice(options, COMPONENT_NAME)

    if choice == "A":
        return handle_cuda_installation()
    elif choice == "I":
        return handle_cpu_installation_warning()
    elif choice == "CONTINUE":
        return True
    else:
        return False

def handle_cuda_installation():
    """Handle CUDA installation with multiple methods"""
    
    print("Installing llama-cpp-python with CUDA acceleration...")
    print("This may take several minutes and will try multiple installation methods.")
    print()
    
    success, message = install_llama_cpp_with_retry()
    
    if success:
        print_success(message)
        print()
        return verify_installation()
    else:
        print_error(f"CUDA installation failed: {message}")
        print()

        show_message('llama_cpp_cuda_install_failed')
        
        options = [
            ("A", "Retry CUDA installation"),
            ("I", "Install CPU-only version instead (very slow)")
        ]

        choice = handle_user_choice(options, COMPONENT_NAME)

        if choice == "A":
            return handle_cuda_installation()  # Recursive retry
        elif choice == "I":
            return handle_cpu_installation_warning()
        elif choice == "CONTINUE":
            return True
        else:
            return False

def handle_cpu_installation_warning():
    """Handle CPU-only installation with strong warnings"""
    
    show_message_and_wait('llama_cpp_cpu_warning')
        
    if not prompt_user_confirmation("Are you sure you want to proceed with CPU-only installation of Llama CPP? [Y/N]: "):
        return handle_fresh_installation()
    
    print("Installing CPU-only llama-cpp-python...")
    print()
    
    success, message = install_llama_cpp_cpu_only()
    
    if success:
        print_success(message)
        print()
        return verify_installation()
    else:
        print_error(f"CPU installation failed: {message}")
        print()
        return prompt_continue_or_skip(COMPONENT_NAME)

def handle_broken_installation():
    """Handle case where installation exists but is broken"""
    
    print("The current llama-cpp-python installation appears to be corrupted.")
    print()
    
    show_message('llama_cpp_broken_installation')
    
    options = [
        ("A", "Reinstall with CUDA acceleration"),
        ("I", "Reinstall CPU-only version (not recommended)")
    ]

    choice = handle_user_choice(options, COMPONENT_NAME)

    if choice == "A":
        return handle_cuda_installation()
    elif choice == "I":
        return handle_cpu_installation_warning()
    elif choice == "CONTINUE":
        return True
    else:
        return False

def handle_poor_performance(performance_message):
    """Handle case where installation works but performance is poor"""
    
    # Extract tokens/sec from message if possible
    try:
        tokens_per_sec = float(performance_message.split()[0])
    except:
        tokens_per_sec = 0
    
    if tokens_per_sec < 3:
        # Very slow - likely CPU-only
        show_message('llama_cpp_cpu_detected')
        
        options = [
            ("U", "Upgrade to CUDA acceleration (recommended)"),
            ("K", "Keep CPU-only version (game will be very slow)")
        ]

        choice = handle_user_choice(options, COMPONENT_NAME)

        if choice == "U":
            return handle_cuda_installation()
        elif choice == "K":
            print_continue("Continuing with CPU-only llama-cpp-python")
            print_warning("Game performance will be severely impacted")
            print()
            return True
        elif choice == "CONTINUE":
            return True
        else:
            return False
    
    else:
        # Slow but not terrible - weak GPU
        show_message('llama_cpp_weak_gpu_detected')
        
        options = [
            ("T", "Try CUDA reinstall (may improve performance)"),
            ("K", "Keep current installation")
        ]

        choice = handle_user_choice(options, COMPONENT_NAME)

        if choice == "T":
            return handle_cuda_installation()
        elif choice == "K":
            print_continue("Continuing with current llama-cpp-python installation")
            print_info("Performance should be acceptable for gameplay")
            print()
            return True
        elif choice == "CONTINUE":
            return True
        else:
            return False

def verify_installation():
    """Final verification that llama-cpp-python is working properly"""
    
    print("Verifying llama-cpp-python installation...")
    print()
    
    # Re-check everything
    installed_ok, installed_message = check_llama_cpp_installed()
    import_ok, import_message = test_llama_cpp_import()
    performance_ok, performance_message = test_llama_cpp_performance()
    
    # Package results for display
    check_results = {
        "Installation": (installed_ok, installed_message),
        "Import Test": (import_ok, import_message),
        "Performance Test": (performance_ok, performance_message)
    }
    
    # Show final results
    display_check_results("LLM INTEGRATION FINAL", check_results)
    
    if installed_ok and performance_ok:
        print_success("LLM integration setup completed successfully!")
        print("🚀 Ready for fast AI inference")
        print()
        return True
    elif installed_ok:
        print_success("LLM integration is installed and working.")
        if not import_ok:
            return handle_broken_installation()
        if not performance_ok:
            return handle_poor_performance(performance_message)
        print()
        return True
    else:
        return False

if __name__ == "__main__":
    from setup.utils.dry_run_utils import run_as_standalone_component
    run_as_standalone_component(COMPONENT_NAME, run_llama_cpp_interactive_setup)