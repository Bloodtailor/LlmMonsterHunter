#!/usr/bin/env python3
"""
MySQL Server and CLI Setup Module
Checks for MySQL server, command line client, and service status
"""

import os
import subprocess
import sys
from pathlib import Path

def check_mysql_cli():
    """Check if MySQL command line client is available."""
    try:
        result = subprocess.run(["mysql", "--version"], 
                              capture_output=True, text=True, check=True)
        print(f"✅ MySQL CLI found: {result.stdout.strip()}")
        return True
    except FileNotFoundError:
        print("❌ MySQL command line client not found")
        return False
    except subprocess.CalledProcessError:
        print("⚠️  MySQL CLI found but may have issues")
        return True

def check_mysql_server_service():
    """Check if MySQL server service is running on Windows."""
    print("Checking MySQL server service...")
    
    # Common MySQL service names
    service_names = ["MySQL84", "MySQL80", "MySQL", "mysqld"]
    
    for service in service_names:
        try:
            result = subprocess.run(["sc", "query", service], 
                                  capture_output=True, text=True, check=True)
            if "RUNNING" in result.stdout:
                print(f"✅ MySQL service '{service}' is running")
                return True
            elif "STOPPED" in result.stdout:
                print(f"⚠️  MySQL service '{service}' is stopped")
                return False
        except subprocess.CalledProcessError:
            continue
    
    print("❌ No MySQL service found")
    return False

def check_mysql_workbench():
    """Check if MySQL Workbench is installed (indicates MySQL presence)."""
    workbench_paths = [
        "C:\\Program Files\\MySQL\\MySQL Workbench 8.0",
        "C:\\Program Files (x86)\\MySQL\\MySQL Workbench 8.0",
        "C:\\Program Files\\MySQL\\MySQL Workbench 8.1",
        "C:\\Program Files (x86)\\MySQL\\MySQL Workbench 8.1"
    ]
    
    for path in workbench_paths:
        if os.path.exists(path):
            print(f"✅ MySQL Workbench found at: {path}")
            return True
    
    print("❌ MySQL Workbench not found")
    return False

def check_mysql_server_directories():
    """Check for MySQL server installation directories."""
    server_paths = [
        "C:\\Program Files\\MySQL\\MySQL Server 8.0",
        "C:\\Program Files\\MySQL\\MySQL Server 8.4",
        "C:\\Program Files (x86)\\MySQL\\MySQL Server 8.0",
        "C:\\Program Files (x86)\\MySQL\\MySQL Server 8.4"
    ]
    
    for path in server_paths:
        if os.path.exists(path):
            print(f"✅ MySQL Server found at: {path}")
            return True
    
    print("❌ MySQL Server installation not found")
    return False

def test_mysql_connection():
    """Test basic MySQL connection (without authentication)."""
    if not check_mysql_cli():
        return False
    
    try:
        # Just test that mysql command works (will fail with auth error, but that's ok)
        result = subprocess.run(["mysql", "-e", "SELECT 1;"], 
                              capture_output=True, text=True, timeout=5)
        
        # If it succeeds, great
        if result.returncode == 0:
            print("✅ MySQL connection test successful")
            return True
        
        # If it fails with access denied, that's actually good (server is running)
        if "Access denied" in result.stderr:
            print("✅ MySQL server is responding (authentication required)")
            return True
        
        # Other errors indicate server issues
        print(f"⚠️  MySQL server may not be running: {result.stderr}")
        return False
        
    except subprocess.TimeoutExpired:
        print("⚠️  MySQL connection test timed out")
        return False
    except Exception as e:
        print(f"⚠️  MySQL connection test error: {e}")
        return False

def check_mysql_requirements():
    """Check all MySQL related requirements."""
    print("Checking MySQL Server and CLI requirements...")
    
    # Check individual components
    cli_available = check_mysql_cli()
    server_running = check_mysql_server_service()
    workbench_found = check_mysql_workbench()
    server_installed = check_mysql_server_directories()
    connection_works = test_mysql_connection()
    
    # Determine overall status
    if server_running and cli_available:
        print("✅ MySQL Server and CLI are working")
        return True
    elif server_installed and workbench_found:
        print("⚠️  MySQL is installed but may not be running")
        return False
    elif workbench_found:
        print("⚠️  MySQL Workbench found but MySQL Server may not be installed")
        return False
    else:
        print("❌ MySQL not found")
        return False

def start_mysql_service():
    """Attempt to start MySQL service."""
    service_names = ["MySQL84", "MySQL80", "MySQL", "mysqld"]
    
    for service in service_names:
        try:
            print(f"Attempting to start {service} service...")
            result = subprocess.run(["net", "start", service], 
                                  capture_output=True, text=True, check=True)
            print(f"✅ {service} service started successfully")
            return True
        except subprocess.CalledProcessError as e:
            if "already been started" in str(e.stderr):
                print(f"✅ {service} service was already running")
                return True
            print(f"⚠️  Failed to start {service}: {e.stderr}")
            continue
    
    print("❌ Could not start any MySQL service")
    return False

def setup_mysql_interactive():
    """Interactive setup for MySQL."""
    print("Setting up MySQL Server and CLI...")
    
    # Check if server is installed
    if not check_mysql_server_directories():
        print("\n❌ MySQL Server is not installed")
        print("📋 To install MySQL Server:")
        print("1. Go to https://dev.mysql.com/downloads/mysql/")
        print("2. Download 'MySQL Community Server'")
        print("3. During installation:")
        print("   - Choose 'Developer Default' or 'Server only'")
        print("   - Set a root password (remember it!)")
        print("   - Install as Windows Service")
        print("   - Include MySQL Command Line Client")
        print("4. Optionally download MySQL Workbench (GUI tool)")
        print("5. After installation, restart your computer")
        
        input("Press Enter after installing MySQL Server...")
        
        # Check again
        if not check_mysql_server_directories():
            print("❌ MySQL Server still not found. Please install and try again.")
            return False
    
    # Check if service is running
    if not check_mysql_server_service():
        print("\n⚠️  MySQL Server service is not running")
        
        choice = input("Do you want to try starting the MySQL service? (y/n): ").lower().strip()
        if choice in ['y', 'yes']:
            if start_mysql_service():
                print("✅ MySQL service started")
            else:
                print("❌ Failed to start MySQL service")
                print("📋 Try manually:")
                print("1. Open Windows Services (services.msc)")
                print("2. Find MySQL service and start it")
                print("3. Or restart your computer")
                return False
    
    # Check CLI
    if not check_mysql_cli():
        print("\n❌ MySQL command line client not found")
        print("📋 To fix this:")
        print("1. Add MySQL bin directory to your system PATH")
        print("2. Typical path: C:\\Program Files\\MySQL\\MySQL Server 8.x\\bin")
        print("3. Or reinstall MySQL with command line tools included")
        
        input("Press Enter after fixing MySQL CLI...")
        
        if not check_mysql_cli():
            print("❌ MySQL CLI still not found. Check PATH settings.")
            return False
    
    print("✅ MySQL Server and CLI setup completed")
    return True

if __name__ == "__main__":
    if len(sys.argv) > 1 and sys.argv[1] == "setup":
        setup_mysql_interactive()
    else:
        check_mysql_requirements()