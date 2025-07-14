#!/usr/bin/env python3
"""
MySQL Interactive Setup Flow
Orchestrates the complete MySQL setup experience with clean UX
"""

from setup.utils.ux_utils import *
from setup.checks.mysql_checks import (
    check_mysql_server, 
    check_mysql_cli, 
    check_mysql_service,
    check_mysql_installations,
    check_mysql_service_exists,
    get_mysql_installations_list,
    get_mysql_service_name
)
from setup.installation.mysql_installation import start_mysql_service

def run_mysql_interactive_setup(current=None, total=None, dry_run=False):
    """
    Interactive setup flow for MySQL server and CLI
    
    Returns:
        bool: True if setup completed successfully, False otherwise
    """

    # ================================================================
    # SECTION 1: INITIAL STATUS CHECK AND DISPLAY
    # ================================================================

    # Show clean component header
    show_component_header(
        component_name="MySQL Server",
        current=current,
        total=total,
        description="Required for database operations and game data storage"
    )

    print("Checking current status of MySQL setup...")
    
    # Initial status check
    server_ok, server_message = check_mysql_server()
    cli_ok, cli_message = check_mysql_cli()

    # Dry run mode - set check results to custom values
    if dry_run:
        print_dry_run_header()
        
        from setup.utils.dry_run_utils import set_dry_run
        server_ok, server_message = set_dry_run('check_mysql_server')
        cli_ok, cli_message = set_dry_run('check_mysql_cli')

    
    # Package results for display
    check_results = {
        "MySQL Server": (server_ok, server_message),
        "MySQL CLI": (cli_ok, cli_message)
    }
    
    # Display results beautifully
    overall_ok = display_check_results("MYSQL", check_results)

    # ================================================================
    # SECTION 2: INTERACTIVE SETUP FLOWS AND LOGIC
    # ================================================================
    
    # If everything is working, we're done!
    if overall_ok:
        print("All MySQL components are ready!")
        return True
    
    # If CLI is the only problem and server works, handle PATH issue
    if server_ok and not cli_ok:
        return handle_cli_path_issue()
    
    # If server fails, run diagnostic to determine the problem
    if not server_ok:
        return handle_server_issue()
    
    # ================================================================
    # SECTION 3: FINAL CHECKS AND DISPLAY
    # ================================================================

    print("Checking final status of MySQL setup...")

    # Final status check
    server_ok, server_message = check_mysql_server()
    cli_ok, cli_message = check_mysql_cli()
    
    # Package results for display
    final_check_results = {
        "MySQL Server": (server_ok, server_message),
        "MySQL CLI": (cli_ok, cli_message)
    }

    # Display results beautifully
    overall_ok = display_check_results("MYSQL", final_check_results)
    
    if overall_ok:
        return True
    else:
        return False

def handle_server_issue():
    """Handle MySQL server not responding"""
    
    print("MySQL server is not responding.")
    print()
    
    # Ask user if they want diagnostic
    choice = input("Run diagnostic to check if MySQL is installed? [Y/n]: ").strip()
    if choice.lower() in ['n', 'no']:
        print()
        print_continue("Skipping MySQL diagnostic...")
        return False
    
    print()
    print("Running diagnostic...")
    
    # Run diagnostic checks
    service_ok, service_message = check_mysql_service()
    installations_ok, installations_message = check_mysql_installations()
    service_exists_ok, service_exists_message = check_mysql_service_exists()
    
    # Package diagnostic results
    diagnostic_results = {
        "MySQL Installations": (installations_ok, installations_message),
        "MySQL Service": (service_exists_ok, service_exists_message),
        "Service Status": (service_ok, service_message)
    }
    
    # Show diagnostic results
    print()
    display_check_results("MYSQL DIAGNOSTIC", diagnostic_results)
    
    # Determine what kind of problem this is
    mysql_appears_installed = installations_ok or service_exists_ok
    
    if not mysql_appears_installed:
        # MySQL not installed
        print("MySQL does not appear to be installed on this system.")
        print()
        return handle_mysql_not_installed()
    
    else:
        # MySQL installed but not working
        print("MySQL appears to be installed but not working properly.")
        print()
        return handle_mysql_repair()

def handle_mysql_not_installed():
    """Handle case where MySQL is not installed"""
    
    print_error("MySQL Server installation required.")
    print()
    
    show_message_and_wait('mysql_installation', "Press Enter after installing MySQL...")
    
    # Check if installation worked
    return verify_mysql_setup()

def handle_mysql_repair():
    """Handle case where MySQL is installed but broken"""
    
    # Check if it's a service issue that we can fix
    service_name = get_mysql_service_name()
    service_running, _ = check_mysql_service()
    
    if service_name and not service_running:
        # Try automated service start
        print("MySQL service exists but is not running.")
        print()
        
        choice = input("Attempt to start the MySQL service automatically? [Y/n]: ").strip()
        if choice.lower() not in ['n', 'no']:
            print()
            print("Starting MySQL service...")
            
            success, message = start_mysql_service()
            
            if success:
                print_success(message)
                print()
                return verify_mysql_setup()
            else:
                print_error(message)
                print()
                return handle_service_start_failed()
        else:
            print()
            print_continue("Skipping automatic service start...")
            return handle_manual_mysql_repair()
    
    else:
        # Some other kind of problem
        return handle_manual_mysql_repair()

def handle_service_start_failed():
    """Handle case where automatic service start failed"""
    
    print("Automatic service start failed.")
    print()
    
    show_message_and_wait('mysql_service_start', "Press Enter after starting MySQL service...")
    
    return verify_mysql_setup()

def handle_manual_mysql_repair():
    """Handle case where manual MySQL repair is needed"""
    
    print("Manual MySQL troubleshooting required.")
    print()
    
    show_message_and_wait('mysql_troubleshooting', "Press Enter after fixing MySQL...")
    
    return verify_mysql_setup()

def handle_cli_path_issue():
    """Handle case where server works but CLI is missing from PATH"""
    
    print_error("MySQL CLI needs to be added to your system PATH.")
    print()
    
    # Try to find installation for PATH guidance
    installations = get_mysql_installations_list()
    
    if installations:
        mysql_path = installations[0]  # Use first found
        print(f"Found MySQL installation at: {mysql_path}")
        print()
        
        show_message_and_wait('mysql_cli_path', "Press Enter after adding MySQL to PATH...")
        
        return verify_mysql_setup()
    
    else:
        print_warning("Cannot locate MySQL installation for PATH configuration.")
        print()
        
        show_message_and_wait('mysql_cli_path_generic', "Press Enter after configuring PATH...")
        
        return verify_mysql_setup()

def verify_mysql_setup():
    """Final verification that MySQL setup is working"""
    
    print("Verifying MySQL setup...")
    
    # Re-check everything
    server_ok, server_message = check_mysql_server()
    cli_ok, cli_message = check_mysql_cli()
    
    # Package results for display
    check_results = {
        "MySQL Server": (server_ok, server_message),
        "MySQL CLI": (cli_ok, cli_message)
    }
    
    # Show final results
    overall_ok = display_check_results("MYSQL", check_results)
    
    if overall_ok:
        print_success("MySQL setup completed successfully!")
        print()
        return True
    else:
        print_warning("MySQL setup verification failed.")
        print_info("You may need to complete the setup manually.")
        print()
        return False

if __name__ == "__main__":
    from setup.utils.dry_run_utils import run_as_standalone_component
    run_as_standalone_component("MySQL", run_mysql_interactive_setup)
