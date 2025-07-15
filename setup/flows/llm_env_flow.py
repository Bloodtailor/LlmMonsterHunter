#!/usr/bin/env python3
"""
LLM Environment Interactive Setup Flow
Orchestrates the complete LLM environment configuration experience with clean UX
"""
COMPONENT_NAME = "LLM Model Configuration"

from setup.utils.ux_utils import *
from setup.checks.llm_env_checks import (
    check_env_model_path,
    validate_model_file,
    get_model_info
)
from setup.installation.llm_env_installation import update_env_model_path

def run_llm_env_interactive_setup(current=None, total=None, dry_run=False):
    """
    Interactive setup flow for LLM environment configuration
    
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
        description="Configure path to your language model file for AI inference"
    )

    print("Checking current status...")
    
    # Run individual checks
    model_path_ok, model_path_message = check_env_model_path()

    # Dry run mode - set check results to custom values
    if dry_run:
        print_dry_run_header()
        
        from setup.utils.dry_run_utils import set_dry_run
        model_path_ok, model_path_message = set_dry_run('check_env_model_path')

    # Package results for display
    check_results = {
        "Model Path Configuration": (model_path_ok, model_path_message)
    }

    # Display results beautifully
    overall_ok = display_check_results("LLM MODEL CONFIG", check_results)

    # ================================================================
    # SECTION 2: INTERACTIVE SETUP FLOWS AND LOGIC
    # ================================================================

    # If everything is working, we're done!
    if overall_ok:
        print("LLM model configuration is ready!")
        print("🤖 Ready for AI language model inference")
        print()
        return True
    
    # Show requirement explanation
    show_message('llm_model_requirement_explanation')
    
    # Handle the configuration issue
    if not model_path_ok:
        return handle_model_path_configuration(model_path_message)
    
    # ================================================================
    # SECTION 3: FINAL CHECKS AND DISPLAY
    # ================================================================

    return verify_llm_env_setup()

def handle_model_path_configuration(current_message):
    """Handle model path configuration issues"""

    if not "placeholder" in current_message.lower():
        input("Press Enter to continue...")
        print("LLM model path needs to be configured.")
        print_error(current_message)
        print()

        if "not found" in current_message.lower():
            show_message('llm_model_file_missing')  
        else:
            show_message('llm_model_path_invalid')
    
    options = [
        ("M", "Configure model path now"),
        ("H", "Get help finding and dowloading a language model")
    ]

    choice = handle_user_choice(options, COMPONENT_NAME)

    if choice == "M":
        return handle_model_path_input()
    elif choice == "H":
        show_message('llm_model_download_guidance')
        return handle_model_path_configuration(current_message)
    elif choice == "CONTINUE":
        return True
    else:
        return False

def handle_model_path_input():
    """Handle interactive model path input and validation"""
    
    show_message('llm_model_path_placeholder')
    
    while True:
        model_path = input("Enter full path to your model file: ").strip()

        if not model_path:
            choice = input("No path entered. Try again? [Y/n]: ").strip()
            if choice.lower() in ['n', 'no']:
                print()
                print_continue("Skipping model path configuration...")
                return False
            continue

        # Clean up quotes if user copied from file explorer
        model_path = model_path.strip('"').strip("'")

        # Validate the model file
        is_valid, message = validate_model_file(model_path)

        if is_valid:
            # Update .env file
            success, update_message = update_env_model_path(model_path)
            
            if success:
                print_success(update_message)
                
                # Show model info
                model_info = get_model_info(model_path)
                if model_info:
                    print(f"   Model: {model_info['name']}")
                    print(f"   Size: {model_info['size_gb']:.1f} GB")
                print()
                return True
            else:
                print_error(f"Failed to save configuration: {update_message}")
                print()
                return False
        else:
            print_error(f"Invalid model file: {message}")
            print(f"   Path: {model_path}")
            print()

            choice = input("Try different path? [Y/n]: ").strip()
            if choice.lower() in ['n', 'no']:
                print()
                print_continue("Skipping model path configuration...")
                return False

def verify_llm_env_setup():
    """Final verification that LLM environment is configured properly"""
    
    print("Verifying LLM environment configuration...")
    print()
    
    # Re-check everything
    model_path_ok, model_path_message = check_env_model_path()
    
    # Package results for display
    check_results = {
        "Model Path Configuration": (model_path_ok, model_path_message)
    }
    
    # Show final results
    overall_ok = display_check_results("LLM MODEL CONFIG FINAL", check_results)
    
    if overall_ok:
        print_success("LLM model configuration completed successfully!")
        print("🤖 Ready for AI language model inference")
        print()
        return True
    else:
        print_warning("LLM model configuration verification failed.")
        print_info("You may need to complete the configuration manually.")
        print()
        return False

if __name__ == "__main__":
    from setup.utils.dry_run_utils import run_as_standalone_component
    run_as_standalone_component(COMPONENT_NAME, run_llm_env_interactive_setup)