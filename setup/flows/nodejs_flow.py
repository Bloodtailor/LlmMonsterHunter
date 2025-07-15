#!/usr/bin/env python3
"""
Node.js Interactive Setup Flow
Orchestrates the complete Node.js setup experience with clean UX
"""

COMPONENT_NAME = "Nodejs"

from setup.utils.ux_utils import *
from setup.checks.nodejs_checks import check_nodejs, check_npm, check_frontend_dependencies
from setup.installation.nodejs_installation import install_frontend_dependencies

def run_nodejs_interactive_setup(current=None, total=None, dry_run=False):
    """
    Interactive setup flow for Node.js and React frontend
    
    Returns:
        bool: True if setup completed successfully, False otherwise
    """
    
    # ================================================================
    # SECTION 1: INITIAL STATUS CHECK AND DISPLAY
    # ================================================================

    # Show clean component header
    show_component_header(
        component_name="Node.js & npm",
        current = current,
        total = total,
        description="Required for React frontend development server"
    )

    print("Checking current status...")
    
    # Run individual checks
    nodejs_ok, nodejs_message = check_nodejs()
    npm_ok, npm_message = check_npm()
    frontend_ok, frontend_message = check_frontend_dependencies()

    # Dry run mode - set check results to custom values
    if dry_run:
        print_dry_run_header()
        
        from setup.utils.dry_run_utils import set_dry_run
        nodejs_ok, nodejs_message = set_dry_run('check_nodejs')
        npm_ok, npm_message = set_dry_run('check_npm')
        frontend_ok, frontend_message = set_dry_run('check_frontend_dependencies')

    # Package results for display
    check_results = {
        "Node.js Runtime": (nodejs_ok, nodejs_message),
        "npm Package Manager": (npm_ok, npm_message),
        "Frontend Dependencies": (frontend_ok, frontend_message)
    }

    # Display results beautifully
    overall_ok = display_check_results("NODEJS", check_results)
    
    # If everything is working, we're done!
    if overall_ok:
        print("All Node.js components are ready!")
        return True
    
    # ================================================================
    # SECTION 2: INTERACTIVE SETUP FLOWS AND LOGIC
    # ================================================================

    # If Node.js/npm are missing, we need user to install them
    if not nodejs_ok or not npm_ok:
        if not handle_nodejs_issue():
            return False
        else:
            frontend_ok, frontend_message = check_frontend_dependencies()
    
    if not frontend_ok:
        if not handle_frontend_issue():
            return False
    
    # ================================================================
    # SECTION 3: FINAL CHECKS AND DISPLAY
    # ================================================================

    # Check everything one more time
    print("Checking final state of the component...")

    # Run individual checks
    nodejs_ok, nodejs_message = check_nodejs()
    npm_ok, npm_message = check_npm()
    frontend_ok, frontend_message = check_frontend_dependencies()
    
    # Package results for display
    final_check_results = {
        "Node.js Runtime": (nodejs_ok, nodejs_message),
        "npm Package Manager": (npm_ok, npm_message),
        "Frontend Dependencies": (frontend_ok, frontend_message)
    }

    # Display results beautifully
    overall_ok = display_check_results("NODEJS", final_check_results)
    
    if overall_ok:
        return True
    else:
        return False

def handle_nodejs_issue():
    """Handle case where nodejs or npm is not installed"""
    
    print_error("Node.js or npm is missing - this requires manual installation.")
    print()
    
    show_message('nodejs_installation')
    
    while True:
        choice = input("Do you want to [S]kip, [T]ry anyways, or [E]xit [S/T/E]: ").strip()
        
        if choice == "S":
            print()
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

def handle_frontend_issue():
    """
    Handle case where frontend dependencies is not installed 
    But nodejs and npm are working.
    """
    
    print("🔧 Node.js and npm are working! Installing frontend dependencies...")
    print()
    
    success, message = install_frontend_dependencies()
    
    if success:
        print("Frontend dependencies installed successfully!")
        print("Node.js setup is now complete!")
        print()
        return True
    else:
        print_warning(f"Frontend dependency installation failed: {message}")
        print_info("You may need to run 'npm install' manually in the frontend directory.")
        print()
        return False


if __name__ == "__main__":
    from setup.utils.dry_run_utils import run_as_standalone_component
    run_as_standalone_component(COMPONENT_NAME, run_nodejs_interactive_setup)