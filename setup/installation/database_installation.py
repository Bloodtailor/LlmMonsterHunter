#!/usr/bin/env python3
"""
Database Installation Module
Pure installation logic for database creation and configuration
"""

import subprocess
from setup.checks.database_checks import get_database_config
from setup.env_utils import update_env_config

def create_database():
    """
    Create the Monster Hunter database using configuration from .env file.
    Returns (success, message) tuple for clean UX handling.
    """
    config = get_database_config()
    if not config:
        return False, "Invalid or missing database configuration in .env file"
    
    try:
        # Build MySQL command to create database
        cmd = [
            "mysql", 
            f"-h{config['host']}", 
            f"-P{config['port']}", 
            f"-u{config['user']}", 
            f"-p{config['password']}", 
            "-e", f"CREATE DATABASE IF NOT EXISTS {config['name']};"
        ]
        
        result = subprocess.run(cmd, capture_output=True, text=True, check=True, timeout=30)
        return True, f"Database '{config['name']}' created successfully"
        
    except subprocess.TimeoutExpired:
        return False, "Database creation timed out"
    except subprocess.CalledProcessError as e:
        if "Access denied" in e.stderr:
            return False, "Database creation failed: Access denied (check password and permissions)"
        elif "Can't connect" in e.stderr or "Connection refused" in e.stderr:
            return False, "Database creation failed: Cannot connect to MySQL server"
        else:
            error_msg = e.stderr.strip() or "Unknown MySQL error"
            return False, f"Database creation failed: {error_msg}"
    except FileNotFoundError:
        return False, "Database creation failed: MySQL command line client not available"
    except Exception as e:
        return False, f"Database creation error: {e}"

def update_database_password(new_password):
    """
    Update the database password in .env file.
    Returns (success, message) tuple for clean UX handling.
    
    Args:
        new_password (str): New password to set
    """
    if not new_password:
        return False, "Password cannot be empty"
    
    return update_env_config(DB_PASSWORD=new_password)