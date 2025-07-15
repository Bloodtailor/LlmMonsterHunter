#!/usr/bin/env python3
"""
Node.js Checks Module
Pure detection logic for Node.js, npm, and React frontend dependencies
Returns data instead of printing for clean UX flow
"""

import subprocess
import shutil
import sys
from pathlib import Path

def check_nodejs():
    """Check if Node.js is installed and get version."""
    try:
        result = subprocess.run(["node", "--version"], capture_output=True, text=True, check=True)
        version = result.stdout.strip()
        
        # Check if version is adequate (16+)
        try:
            version_num = int(version.replace('v', '').split('.')[0])
            if version_num < 16:
                return False, f"Node.js {version} (version 16+ recommended)"
            else:
                return True, f"Node.js {version}"
        except Exception:
            return True, f"Node.js {version}"
            
    except (FileNotFoundError, subprocess.CalledProcessError):
        return False, "Node.js not found"

def check_npm():
    """Check if npm is available."""
    npm_path = shutil.which("npm") or shutil.which("npm.cmd") or shutil.which("npm.exe")
    
    if npm_path:
        try:
            result = subprocess.run([npm_path, "--version"], capture_output=True, text=True, check=True)
            version = result.stdout.strip()
            return True, f"npm {version}"
        except subprocess.CalledProcessError:
            return True, f"npm at {npm_path}"
    else:
        return False, "npm not found in PATH"

def check_frontend_dependencies():
    """Check if React frontend dependencies are installed."""
    frontend_path = Path("frontend")
    node_modules_path = frontend_path / "node_modules"
    
    if not frontend_path.exists():
        return False, "Frontend directory not found"
    
    if node_modules_path.exists():
        return True, "Frontend dependencies installed"
    else:
        return False, "Frontend dependencies not installed"

def check_nodejs_requirements():
    """Check all Node.js related requirements (for orchestration)."""
    
    nodejs_ok, _ = check_nodejs()
    npm_ok, _ = check_npm()
    deps_ok, _ = check_frontend_dependencies()
    
    return nodejs_ok and npm_ok and deps_ok

def get_diagnostic_info(include_overall=False):
    """
    Get comprehensive Node.js diagnostic information.
    Used by flows to understand what specifically needs to be addressed.
    
    Args:
        include_overall (bool): Whether to include overall requirement check
    
    Returns:
        dict: All Node.js check results for detailed analysis
    """
    nodejs_ok, nodejs_msg = check_nodejs()
    npm_ok, npm_msg = check_npm()
    deps_ok, deps_msg = check_frontend_dependencies()
    
    result = {
        'nodejs': (nodejs_ok, nodejs_msg),
        'npm': (npm_ok, npm_msg),
        'frontend_dependencies': (deps_ok, deps_msg),
    }
    
    if include_overall:
        overall_ok = check_nodejs_requirements()
        result['overall'] = (overall_ok, "All Node.js requirements met" if overall_ok else "Some Node.js requirements missing")
    
    return result