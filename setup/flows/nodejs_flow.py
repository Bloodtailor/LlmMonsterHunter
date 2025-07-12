#!/usr/bin/env python3
"""
Node.js Interactive Setup Flow
Orchestrates the complete Node.js setup experience with clean UX
"""

from setup.ux_utils import *
from setup.checks.nodejs_checks import check_nodejs, check_npm, check_frontend_dependencies
from setup.installation.nodejs_installation import install_frontend_dependencies
from setup.instructions import get_instructions

def run_nodejs_interactive_setup():
    """
    Interactive setup flow for Node.js and React frontend
    
    Returns:
        bool: True if setup completed successfully, False otherwise
    """
    
    # Show clean component header
    show_component_header(
        component_name="Node.js & npm",
        description="Required for React frontend development server"
    )
    
    # Run individual checks
    nodejs_ok, nodejs_message = check_nodejs()
    npm_ok, npm_message = check_npm()
    frontend_ok, frontend_message = check_frontend_dependencies()
    
    # Package results for display
    check_results = {
        "Node.js Runtime": (nodejs_ok, nodejs_message),
        "npm Package Manager": (npm_ok, npm_message),
        "Frontend Dependencies": (frontend_ok, frontend_message)
    }
    
    # Display results beautifully
    overall_ok = display_check_results(check_results)
    
    # If everything is working, we're done!
    if overall_ok:
        print("All Node.js components are ready!")
        return True
    
    # If Node.js/npm are missing, we need user to install them
    if not nodejs_ok or not npm_ok:
        print_error("Node.js or npm is missing - this requires manual installation.")
        print()
        
        # Show installation instructions
        instructions = get_instructions('nodejs_installation'),
        for line in instructions:
            print(line)
        
        while True:
            choice = input("Do you want to [S]kip, [T]ry anyways, or [E]xit [S/T/E]: ").strip()
            
            if choice == "S":
                print()
                print_continue("Continuing to other components...")
                print_info("Remember to come back and complete Node.js setup later!")
                print()
                return False
            
            elif choice == "T":
                
                print()
                print("Attempting to install frontend dependencies anyway...")
                success, message = install_frontend_dependencies()
                
                if success:
                    print(f"Surprise! Frontend dependencies installed successfully!")
                    print("Your Node.js setup might be working after all.")
                    print()
                    return True
                else:
                    print(f"Frontend dependency installation failed: {message}")
                    print_info("You'll need to install Node.js properly first.")
                    print()
                    return False
            
            elif choice == "E":
                print()
                print("Exiting setup...")
                print()
                import sys
                sys.exit(0)
            else:
                print("Please enter S, T, or E")
    
    # Node.js and npm are present, but frontend dependencies are missing
    # This is the ideal auto-install scenario
    elif not frontend_ok:
        print("🔧 Node.js and npm are working! Installing frontend dependencies...")
        print()
        
        success, message = install_frontend_dependencies()
        
        if success:
            print("Frontend dependencies installed successfully!")
            print("Node.js setup is now complete!")
            print()
            final_result = True
        else:
            print_warning(f"Frontend dependency installation failed: {message}")
            print_info("You may need to run 'npm install' manually in the frontend directory.")
            print()
            final_result = False

    # This shouldn't happen, but just in case
    else:
        print_warning("Unexpected state in Node.js setup")
        print()
        final_result = False
    
    # Check everything one more time
    print("Final state of the component:")

    # Run individual checks
    nodejs_ok, nodejs_message = check_nodejs()
    npm_ok, npm_message = check_npm()
    frontend_ok, frontend_message = check_frontend_dependencies()
    
    # Package results for display
    check_results = {
        "Node.js Runtime": (nodejs_ok, nodejs_message),
        "npm Package Manager": (npm_ok, npm_message),
        "Frontend Dependencies": (frontend_ok, frontend_message)
    }

    return final_result