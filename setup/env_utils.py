#!/usr/bin/env python3
"""
Environment Utilities Module
Centralized utilities for .env file handling across all setup modules
"""

import os
from pathlib import Path

def load_env_config():
    """
    Load and parse the .env file into a dictionary.
    Safe function that only reads, doesn't modify anything.
    
    Returns:
        dict: Environment variables as key-value pairs, empty dict if file missing/error
    """
    env_file = Path(".env")
    if not env_file.exists():
        return {}
    
    env_vars = {}
    try:
        with open(env_file, 'r') as f:
            for line_num, line in enumerate(f, 1):
                line = line.strip()
                
                # Skip empty lines and comments
                if not line or line.startswith('#'):
                    continue
                
                # Must contain = to be valid
                if '=' not in line:
                    continue
                
                # Split on first = only (values can contain =)
                key, value = line.split('=', 1)
                key = key.strip()
                value = value.strip()
                
                # Remove quotes if present
                if value.startswith('"') and value.endswith('"'):
                    value = value[1:-1]
                elif value.startswith("'") and value.endswith("'"):
                    value = value[1:-1]
                
                env_vars[key] = value
        
        return env_vars
        
    except Exception:
        return {}



def validate_env_keys(required_keys):
    """
    Check if all required keys exist in .env file.
    
    Args:
        required_keys (list): List of required key names
        
    Returns:
        tuple: (success, message, missing_keys)
    """
    if not env_file_exists():
        return False, ".env file not found", required_keys
    
    env_vars = load_env_config()
    missing_keys = [key for key in required_keys if key not in env_vars]
    
    if missing_keys:
        missing_str = ', '.join(missing_keys)
        return False, f"Missing required keys: {missing_str}", missing_keys
    
    return True, "All required keys present", []

def update_env_config(**kwargs):
    """
    Update multiple environment variables in .env file.
    PERMANENT CHANGE: Modifies .env file on disk.
    
    Args:
        **kwargs: Key-value pairs to update
        
    Returns:
        tuple: (success, message)
    """
    env_file = Path(".env")
    
    if not env_file.exists():
        return False, ".env file not found"
    
    if not kwargs:
        return True, "No changes needed"
    
    try:
        # Read current content
        with open(env_file, 'r') as f:
            content = f.read()
        
        lines = content.split('\n')
        updated_lines = []
        updated_keys = set()
        
        # Process existing lines
        for line in lines:
            if '=' in line and not line.strip().startswith('#'):
                key = line.split('=', 1)[0].strip()
                if key in kwargs:
                    # Update this line
                    updated_lines.append(f'{key}={kwargs[key]}')
                    updated_keys.add(key)
                else:
                    # Keep unchanged
                    updated_lines.append(line)
            else:
                # Keep comments and empty lines
                updated_lines.append(line)
        
        # Add any new keys that weren't found
        for key, value in kwargs.items():
            if key not in updated_keys:
                updated_lines.append(f'{key}={value}')
        
        # Write back to file
        with open(env_file, 'w') as f:
            f.write('\n'.join(updated_lines))
        
        updated_list = ', '.join(kwargs.keys())
        return True, f"Updated .env keys: {updated_list}"
        
    except Exception as e:
        return False, f"Failed to update .env file: {e}"



def create_env_file_from_template(template_path=".env.example"):
    """
    Create .env file from .env.example template file.
    PERMANENT CHANGE: Creates .env file on disk.
    
    Args:
        template_path (str): Path to template file (default: ".env.example")
        
    Returns:
        tuple: (success, message)
    """
    env_file = Path(".env")
    template = Path(template_path)
    
    if env_file.exists():
        return True, ".env file already exists"
    
    if not template.exists():
        return False, f"Template file {template_path} not found"
    
    try:
        with open(template, 'r') as src:
            content = src.read()
        with open(env_file, 'w') as dst:
            dst.write(content)
        return True, f".env file created from {template.name}"
    except Exception as e:
        return False, f"Failed to create .env from template: {e}"