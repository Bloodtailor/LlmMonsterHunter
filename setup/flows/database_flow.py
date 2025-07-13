#!/usr/bin/env python3
"""
Database Interactive Setup Flow
Orchestrates the complete database configuration experience with clean UX
"""

from setup.ux_utils import *
from setup.checks.database_checks import (
    check_env_database_config,
    check_mysql_server_connection, 
    check_database_exists
)
from setup.installation.database_installation import (
    update_database_password,
    create_database
)

def run_database_interactive_setup(current=None, total=None):
    """
    Interactive setup flow for database configuration
    
    Returns:
        bool: True if setup completed successfully, False otherwise
    """
    
    # Show clean component header
    show_component_header(
        component_name="Database Connection",
        current=current,
        total=total,
        description="Configure and create the Monster Hunter game database"
    )
    
    print("Checking current status...")

    # Initial status check (dependency order: Config → Connection → Database)
    config_ok, config_message = check_env_database_config()
    connection_ok, connection_message = check_mysql_server_connection()
    database_ok, database_message = check_database_exists()
    
    # Package results for display
    check_results = {
        "Database Configuration": (config_ok, config_message),
        "MySQL Connection": (connection_ok, connection_message),
        "Game Database": (database_ok, database_message)
    }
    
    # Display results beautifully
    overall_ok = display_check_results("DATABASE", check_results)
    
    # If everything is working, we're done!
    if overall_ok:
        print("Database setup is complete!")
        return True
    
    # Handle issues in dependency order
    if not config_ok:
        if not handle_config_issues():
            return False
    
    # Re-check connection after config fixes
    if config_ok or not config_ok:  # Always check if config was just fixed
        connection_ok, connection_message = check_mysql_server_connection()
        if not connection_ok:
            if not handle_connection_issues(connection_message):
                return False
    
    # Re-check database after connection fixes  
    database_ok, database_message = check_database_exists()
    if not database_ok:
        print("Game database needs to be created.")
        print()
        if not handle_database_missing():
            return False
    
    # Final verification
    return verify_database_setup()

def handle_config_issues():
    """Handle missing or invalid database configuration"""
    
    # Check what specifically is missing
    from setup.env_utils import load_env_config
    env_vars = load_env_config()
    
    if not env_vars:
        print_error(".env file not found")
        print_info("Run basic setup first to create .env file")
        return False
    
    password = env_vars.get('DB_PASSWORD', '')
    if not password or password == 'your_mysql_password_here':
        return handle_missing_password()
    else:
        print_error("Database configuration has issues")
        print_info("Check your .env file database settings")
        return False

def handle_missing_password():
    """Handle missing or placeholder database password"""
    
    show_instructions('database_password_setup')
    
    while True:
        choice = input("Enter your MySQL root password now? [Y/n]: ").strip()
        if choice.lower() in ['n', 'no']:
            print()
            print_continue("Skipping database password setup...")
            print_info("You'll need to set DB_PASSWORD in .env later")
            return False
        
        print()
        password = input("Enter your MySQL root password: ").strip()
        
        if not password:
            print("Empty password entered. Please try again.")
            continue
        
        # Save password and test it
        print("Saving password and testing connection...")
        success, message = update_database_password(password)
        
        if not success:
            print_error(f"Failed to save password: {message}")
            continue
        
        # Test the new password
        connection_ok, connection_message = check_mysql_server_connection()
        
        if connection_ok:
            print_success("Database password configured successfully!")
            print()
            return True
        else:
            print_warning(connection_message)
            

def handle_connection_issues(connection_message):
    """Handle database connection failures"""
    
    print("Database connection is not working.")
    print()
    
    # Distinguish between different connection problems
    if "Access denied" in connection_message:
        print_error("Database password appears to be incorrect.")
        print()

        return handle_missing_password()  # Reuse password entry flow

    
    elif "Cannot connect" in connection_message:
        print_error(connection_message)
        print("This usually means MySQL server is not running.")
        print("Scanning for MySQL service...")
        print()
        
        # Check for MySQL service
        from setup.checks.mysql_checks import get_mysql_service_name
        mysql_service_name = get_mysql_service_name()

        if not mysql_service_name:
            print("No MySQL service found")
        else:
            print_info(f"MySQL service found: {mysql_service_name}")
            print("Attempting to start MySQL server automatically...")
            print()

            from setup.installation.mysql_installation import start_mysql_service
            success, message = start_mysql_service()
        
            if success:
                print_success(message)
                print()
                return verify_connection_working()
            else:
                print(f"Automatic start failed: {message}")
        
        print_info("You may need to start MySQL manually.")
        print()
        
        show_instructions_and_wait('database_connection_troubleshooting', "Press Enter after starting MySQL...")
        return verify_connection_working()
    
    else:
        print_error(connection_message)
        print()
        
        show_instructions('database_troubleshooting')
        show_instructions_and_wait('database_troubleshooting', "Press Enter after fixing connection...")
        
        return verify_connection_working()

def handle_database_missing():
    """Handle missing game database"""
    

    print("Creating database...")
    
    success, message = create_database()
    
    if success:
        print_success(message)
        print()
        return True
    else:
        print_error(f"Database creation failed: {message}")
        print()
        
        show_instructions('database_manual_creation')
        
        retry = input("Try again, or continue anyway? [R]etry/[C]ontinue/[Q]uit: ").strip().upper()
        
        if retry == 'R':
            return handle_database_missing()  # Recursive retry
        elif retry == 'C':
            print()
            print_continue("Continuing without database creation...")
            print_info("You'll need to create the database later")
            return False
        else:
            print()
            print("Exiting setup...")
            print()
            import sys
            sys.exit(0)

def verify_connection_working():
    """Helper to verify connection is working after troubleshooting"""
    
    print("Verifying database connection...")
    
    connection_ok, connection_message = check_mysql_server_connection()
    
    if connection_ok:
        print_success("Database connection is now working!")
        print()
        return True
    else:
        print_warning(f"Connection still not working: {connection_message}")
        print_info("You may need additional troubleshooting")
        print()
        return False

def verify_database_setup():
    """Final verification that database setup is working"""
    
    print("Verifying complete database setup...")
    
    # Re-check everything
    config_ok, config_message = check_env_database_config()
    connection_ok, connection_message = check_mysql_server_connection()
    database_ok, database_message = check_database_exists()
    
    # Package results for display
    check_results = {
        "Database Configuration": (config_ok, config_message),
        "MySQL Connection": (connection_ok, connection_message),
        "Game Database": (database_ok, database_message)
    }
    
    # Show final results
    overall_ok = display_check_results("DATABASE", check_results)
    
    if overall_ok:
        print_success("Database setup completed successfully!")
        print()
        return True
    else:
        print_warning("Database setup verification failed.")
        print_info("Some issues may need manual resolution.")
        print()
        return False

if __name__ == "__main__":
    run_database_interactive_setup()