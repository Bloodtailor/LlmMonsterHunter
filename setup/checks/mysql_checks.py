#!/usr/bin/env python3
"""
MySQL Checks Module
Pure detection logic for MySQL server, CLI, and service status
Returns data instead of printing for clean UX flow
"""

import subprocess
import sys
from pathlib import Path

def check_mysql_server():
    """
    Check if MySQL server is accessible (primary detection method)
    Uses connection test - most reliable way to verify server is working
    """
    try:
        # Try to connect - we expect auth failure, which means server is working
        result = subprocess.run([
            "mysql", "-h", "localhost", "-P", "3306", 
            "-u", "nonexistentuser", "-e", "SELECT 1;"
        ], capture_output=True, text=True, timeout=5)
        
        # If it succeeds somehow, great!
        if result.returncode == 0:
            return True, "MySQL server connection successful"
        
        # If it fails with auth error, server is definitely working
        if "Access denied" in result.stderr:
            return True, "MySQL server responding (authentication required)"
        
        # Other connection errors indicate server problems
        if any(error in result.stderr for error in [
            "Can't connect", "Connection refused", "Unknown MySQL server host",
            "Lost connection", "No connection could be made"
        ]):
            return False, "Cannot connect to MySQL server"
        
        return False, "MySQL server connection unclear"
        
    except FileNotFoundError:
        return False, "Cannot test connection (mysql command not available)"
    except subprocess.TimeoutExpired:
        return False, "MySQL connection test timed out"
    except Exception as e:
        return False, f"MySQL connection test failed: {e}"

def check_mysql_cli():
    """Check if MySQL command line client is available."""
    try:
        result = subprocess.run(["mysql", "--version"], 
                              capture_output=True, text=True, check=True)
        version_info = result.stdout.strip()
        return True, f"MySQL CLI: {version_info}"
    except FileNotFoundError:
        return False, "MySQL command line client not found in PATH"
    except subprocess.CalledProcessError:
        return False, "MySQL command line client not working"

def check_mysql_service():
    """
    Check MySQL service status (for automation purposes)
    Returns service name if found, useful for starting/stopping
    """
    service_names = ["MySQL84", "MySQL80", "MySQL", "mysqld"]
    
    for service in service_names:
        try:
            result = subprocess.run(["sc", "query", service], 
                                  capture_output=True, text=True, check=True)
            if "RUNNING" in result.stdout:
                return True, f"MySQL service '{service}' is running"
            elif "STOPPED" in result.stdout:
                return False, f"MySQL service '{service}' is stopped"
        except subprocess.CalledProcessError:
            continue
    
    return False, "No MySQL service found"

def check_mysql_installations():
    """
    Check if MySQL installations can be found on the system
    Used for diagnostic purposes to distinguish "not installed" vs "installed but broken"
    """
    possible_locations = [
        "C:\\Program Files\\MySQL",
        "C:\\Program Files (x86)\\MySQL", 
        "C:\\mysql",
        "C:\\xampp\\mysql",
        "C:\\wamp64\\bin\\mysql",
        "C:\\laragon\\bin\\mysql",
        "C:\\AppServ\\MySQL",
        "C:\\Server\\MySQL",
        "D:\\xampp\\mysql",
        "D:\\wamp\\bin\\mysql"
    ]
    
    installations = []
    
    for location in possible_locations:
        location_path = Path(location)
        if location_path.exists():
            # Look for mysql.exe in bin subdirectories
            for bin_dir in location_path.rglob("bin"):
                mysql_exe = bin_dir / "mysql.exe"
                if mysql_exe.exists():
                    installations.append(str(bin_dir))
    
    # Also check if mysql is in PATH
    try:
        result = subprocess.run(["where", "mysql"], capture_output=True, text=True, check=True)
        path_location = result.stdout.strip().split('\n')[0]
        if path_location and path_location not in installations:
            installations.append(str(Path(path_location).parent))
    except subprocess.CalledProcessError:
        pass
    
    if installations:
        # Show first installation found
        return True, f"MySQL installation found at: {installations[0]}"
    else:
        return False, "No MySQL installations detected"

def check_mysql_service_exists():
    """
    Check if any MySQL service exists on the system (regardless of running state)
    Used for diagnostic purposes to detect installed but non-running MySQL
    """
    service_names = ["MySQL84", "MySQL80", "MySQL", "mysqld"]
    
    for service in service_names:
        try:
            result = subprocess.run(["sc", "query", service], 
                                  capture_output=True, text=True, check=True)
            # If we can query it, the service exists
            return True, f"MySQL service '{service}' exists"
        except subprocess.CalledProcessError:
            continue
    
    return False, "No MySQL service detected"

def get_mysql_installations_list():
    """
    Helper function to get list of installation paths (for flow logic)
    Returns list of paths for PATH troubleshooting
    """
    possible_locations = [
        "C:\\Program Files\\MySQL",
        "C:\\Program Files (x86)\\MySQL", 
        "C:\\mysql",
        "C:\\xampp\\mysql",
        "C:\\wamp64\\bin\\mysql",
        "C:\\laragon\\bin\\mysql"
    ]
    
    installations = []
    
    for location in possible_locations:
        location_path = Path(location)
        if location_path.exists():
            for bin_dir in location_path.rglob("bin"):
                mysql_exe = bin_dir / "mysql.exe"
                if mysql_exe.exists():
                    installations.append(str(bin_dir))
    
    return installations

def get_mysql_service_name():
    """
    Helper function to get actual MySQL service name (for installation logic)
    Returns service name string or None
    """
    service_names = ["MySQL93", "MySQL84", "MySQL80", "MySQL", "mysqld"]
    
    for service in service_names:
        try:
            subprocess.run(["sc", "query", service], 
                          capture_output=True, text=True, check=True)
            return service
        except subprocess.CalledProcessError:
            continue
    
    return None

def check_mysql_requirements():
    """Check all MySQL related requirements (for orchestration)."""
    print("Checking MySQL server and CLI requirements...")
    
    server_ok, _ = check_mysql_server()
    cli_ok, _ = check_mysql_cli()
    
    return server_ok and cli_ok