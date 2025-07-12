#!/usr/bin/env python3
"""
MySQL Installation Module
Pure installation logic for MySQL service management
"""

import subprocess
from setup.checks.mysql_checks import get_mysql_service_name

def start_mysql_service():
    """
    Try to start MySQL service
    Returns (success, message) tuple for clean UX handling
    """
    # First, find which MySQL service exists on this system
    service_name = get_mysql_service_name()
    
    if not service_name:
        return False, "No MySQL service found to start"
    
    try:
        # Try to start the service
        result = subprocess.run(["net", "start", service_name], 
                              capture_output=True, text=True, check=True)
        return True, f"MySQL service '{service_name}' started successfully"
        
    except subprocess.CalledProcessError as e:
        # Check if it was already running
        if "already been started" in str(e.stderr):
            return True, f"MySQL service '{service_name}' was already running"
        
        # Check for permission issues
        if "Access is denied" in str(e.stderr):
            return False, f"Permission denied - try running as Administrator"
        
        # Other errors
        return False, f"Failed to start MySQL service '{service_name}': {e.stderr.strip()}"
    
    except Exception as e:
        return False, f"Unexpected error starting MySQL service: {e}"