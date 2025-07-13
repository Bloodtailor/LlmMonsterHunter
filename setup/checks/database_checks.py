#!/usr/bin/env python3
"""
Database Checks Module
Pure detection logic for database configuration and connectivity
Returns data instead of printing for clean UX flow
"""

import subprocess
import sys
from pathlib import Path
from setup.env_utils import load_env_config

def check_env_database_config():
    """
    Check if database configuration exists and is valid in .env file.
    Does not test connectivity, just validates config format.
    """
    env_vars = load_env_config()
    
    if not env_vars:
        return False, ".env file not found or unreadable"
    
    # Required database configuration keys
    required_keys = ['DB_HOST', 'DB_PORT', 'DB_NAME', 'DB_USER', 'DB_PASSWORD']
    missing_keys = [key for key in required_keys if key not in env_vars]
    
    if missing_keys:
        missing_str = ', '.join(missing_keys)
        return False, f"Missing database config: {missing_str}"
    
    # Check if password is set (not default placeholder)
    password = env_vars.get('DB_PASSWORD', '')
    if not password or password == 'your_mysql_password_here':
        return False, "Database password not set in .env file"
    
    # Basic port format validation
    try:
        port = int(env_vars.get('DB_PORT', '3306'))
    except ValueError:
        return False, f"Database port must be a number: {env_vars.get('DB_PORT')}"
    
    # Return success with configuration summary
    host = env_vars.get('DB_HOST', 'localhost')
    user = env_vars.get('DB_USER', 'root') 
    db_name = env_vars.get('DB_NAME', 'monster_hunter_game')
    
    return True, f"Database config: {user}@{host}:{port}/{db_name}"

def get_database_config():
    """
    Helper function to get database configuration from .env file.
    Used by other functions that need the config.
    
    Returns:
        dict or None: Database configuration or None if env file unreadable
    """
    env_vars = load_env_config()
    
    if not env_vars:
        return None
    
    try:
        return {
            'host': env_vars.get('DB_HOST', 'localhost'),
            'port': int(env_vars.get('DB_PORT', '3306')),
            'name': env_vars.get('DB_NAME', 'monster_hunter_game'),
            'user': env_vars.get('DB_USER', 'root'),
            'password': env_vars.get('DB_PASSWORD', '')
        }
    except ValueError:
        return None

def check_mysql_server_connection():
    """
    Test connection to MySQL server using .env configuration.
    Tests server connectivity without checking specific database.
    """
    config = get_database_config()
    if not config:
        return False, "Invalid or missing database configuration"
    
    try:
        # Test connection to MySQL server (not specific database)
        cmd = [
            "mysql", 
            f"-h{config['host']}", 
            f"-P{config['port']}", 
            f"-u{config['user']}", 
            f"-p{config['password']}", 
            "-e", "SELECT 1;"
        ]
        
        result = subprocess.run(cmd, capture_output=True, text=True, check=True, timeout=10)
        return True, "MySQL server connection successful"
        
    except subprocess.TimeoutExpired:
        return False, "MySQL connection timed out"
    except subprocess.CalledProcessError as e:
        if "Access denied" in e.stderr:
            return False, "MySQL connection failed: Access denied (check password)"
        elif "Can't connect" in e.stderr or "Connection refused" in e.stderr:
            return False, "MySQL connection failed: Cannot connect to server"
        elif "Unknown MySQL server host" in e.stderr:
            return False, f"MySQL connection failed: Unknown host '{config['host']}'"
        else:
            return False, f"MySQL connection failed: {e.stderr.strip()}"
    except FileNotFoundError:
        return False, "MySQL command line client not available"
    except Exception as e:
        return False, f"MySQL connection error: {e}"

def check_database_exists():
    """
    Check if the configured database exists and is accessible.
    """
    config = get_database_config()
    if not config:
        return False, "Invalid or missing database configuration"
    
    try:
        # Test access to specific database
        cmd = [
            "mysql", 
            f"-h{config['host']}", 
            f"-P{config['port']}", 
            f"-u{config['user']}", 
            f"-p{config['password']}", 
            "-e", f"USE {config['name']}; SELECT 1;"
        ]
        
        result = subprocess.run(cmd, capture_output=True, text=True, check=True, timeout=10)
        return True, f"Database '{config['name']}' exists and is accessible"
        
    except subprocess.TimeoutExpired:
        return False, "Database check timed out"
    except subprocess.CalledProcessError as e:
        if "Unknown database" in e.stderr:
            return False, f"Database '{config['name']}' does not exist"
        elif "Access denied" in e.stderr:
            return False, "Database access denied (check password and permissions)"
        elif "Can't connect" in e.stderr:
            return False, "Cannot connect to database (check MySQL connection)"
        else:
            return False, f"Database check failed: {e.stderr.strip()}"
    except FileNotFoundError:
        return False, "MySQL command line client not available"
    except Exception as e:
        return False, f"Database check error: {e}"

def check_database_requirements():
    """Check all database related requirements (for orchestration)."""
    print("Checking database configuration and connectivity...")
    
    config_ok, _ = check_env_database_config()
    server_ok, _ = check_mysql_server_connection()
    database_ok, _ = check_database_exists()
    
    return config_ok and server_ok and database_ok
