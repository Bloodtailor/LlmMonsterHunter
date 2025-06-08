#!/usr/bin/env python3
"""
Monster Hunter Game - Interactive Environment Setup
Walks user through setting up missing requirements
"""

import sys
from pathlib import Path

# Import all setup modules
from setup.nodejs_setup import check_nodejs_requirements, setup_nodejs_interactive
from setup.mysql_setup import check_mysql_requirements, setup_mysql_interactive
from setup.database_connection import check_database_connection, setup_database_interactive
from setup.gpu_cuda_setup import check_gpu_cuda_requirements, setup_gpu_cuda_interactive
from setup.visual_studio_setup import check_visual_studio_requirements, setup_visual_studio_interactive
from setup.llama_cpp_setup import check_llama_cpp_requirements, setup_llama_cpp_interactive
from setup.model_directory import check_model_directory_requirements, setup_model_directory_interactive
from setup.basic_backend import check_basic_backend_requirements, setup_basic_backend_interactive

def print_header(text):
    """Print a formatted header."""
    print("\n" + "=" * 60)
    print(text.center(60))
    print("=" * 60)

def print_section(text):
    """Print a section header."""
    print(f"\n{text}")
    print("-" * len(text))

def ask_user_confirmation(prompt):
    """Ask user for yes/no confirmation."""
    while True:
        response = input(f"{prompt} (y/n): ").lower().strip()
        if response in ['y', 'yes']:
            return True
        elif response in ['n', 'no']:
            return False
        else:
            print("Please enter 'y' for yes or 'n' for no.")

def main():
    """Interactive setup for missing requirements."""
    print_header("Interactive Environment Setup")
    print("This will help you set up missing requirements for Monster Hunter Game.")
    print("You'll be asked before each setup step.")
    
    # Define all requirement setups
    setup_modules = [
        ("Basic Backend", check_basic_backend_requirements, setup_basic_backend_interactive),
        ("Node.js & npm", check_nodejs_requirements, setup_nodejs_interactive),
        ("MySQL Server", check_mysql_requirements, setup_mysql_interactive),
        ("Database Connection", check_database_connection, setup_database_interactive),
        ("NVIDIA GPU & CUDA", check_gpu_cuda_requirements, setup_gpu_cuda_interactive),
        ("Visual Studio Build Tools", check_visual_studio_requirements, setup_visual_studio_interactive),
        ("LLM Integration", check_llama_cpp_requirements, setup_llama_cpp_interactive),
        ("Model Directory", check_model_directory_requirements, setup_model_directory_interactive)
    ]
    
    setup_results = []
    
    for module_name, check_function, setup_function in setup_modules:
        print_section(f"Setting up {module_name}")
        
        # Check if already working
        try:
            is_working = check_function()
            if is_working:
                print(f"✅ {module_name} is already working correctly.")
                setup_results.append((module_name, True, "already_working"))
                continue
        except Exception as e:
            print(f"❌ Error checking {module_name}: {e}")
        
        # Ask user if they want to set this up
        print(f"\n{module_name} needs to be set up.")
        if ask_user_confirmation(f"Do you want to set up {module_name} now?"):
            try:
                print(f"\nSetting up {module_name}...")
                result = setup_function()
                if result:
                    print(f"✅ {module_name} setup completed successfully.")
                    setup_results.append((module_name, True, "setup_successful"))
                else:
                    print(f"❌ {module_name} setup failed.")
                    setup_results.append((module_name, False, "setup_failed"))
            except Exception as e:
                print(f"❌ Error during {module_name} setup: {e}")
                setup_results.append((module_name, False, "setup_error"))
        else:
            print(f"⏭️  Skipping {module_name} setup.")
            setup_results.append((module_name, False, "user_skipped"))
    
    # Final summary
    print_header("Setup Summary")
    
    successful_setups = 0
    for module_name, success, reason in setup_results:
        if success:
            if reason == "already_working":
                status = "✅ Already Working"
            else:
                status = "✅ Setup Successful"
            successful_setups += 1
        else:
            if reason == "user_skipped":
                status = "⏭️  Skipped by User"
            elif reason == "setup_failed":
                status = "❌ Setup Failed"
            else:
                status = "❌ Error During Setup"
        
        print(f"{module_name:<25} {status}")
    
    total_modules = len(setup_results)
    print(f"\nSuccessful: {successful_setups}/{total_modules}")
    
    if successful_setups == total_modules:
        print("\n🎉 All components are now set up!")
        print("You can now run the game launcher (start_game.bat).")
    elif successful_setups >= total_modules * 0.75:
        print(f"\n✅ Most components are set up ({successful_setups}/{total_modules})")
        print("The game should work, but you may want to complete the remaining setups.")
    else:
        print(f"\n⚠️  Some components still need setup ({total_modules - successful_setups} remaining)")
        print("You can run this setup again or try to start the game anyway.")
    
    print("\nNext steps:")
    print("1. Run start_game.bat to check requirements and start the game")
    print("2. If needed, run this setup again to complete remaining items")
    print("3. Check the individual setup files in setup/ directory for manual configuration")
    
    input("\nPress Enter to exit...")

if __name__ == "__main__":
    main()