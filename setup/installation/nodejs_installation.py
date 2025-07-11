#!/usr/bin/env python3
"""
Node.js Installation Module
Pure installation logic for React frontend dependencies
"""

import subprocess
import shutil
from pathlib import Path

def install_frontend_dependencies():
    """Install React frontend dependencies using npm."""
    frontend_path = Path("frontend")
    
    if not frontend_path.exists():
        return False, "Frontend directory not found"
    
    # Check if already installed
    node_modules_path = frontend_path / "node_modules"
    if node_modules_path.exists():
        return True, "Frontend dependencies already installed"
    
    # Find npm executable
    npm_path = shutil.which("npm") or shutil.which("npm.cmd") or shutil.which("npm.exe")
    
    if not npm_path:
        return False, "npm not found in PATH"
    
    try:
        subprocess.run([npm_path, "install"], cwd=str(frontend_path), check=True)
        return True, "npm intalled"
    except subprocess.CalledProcessError as e:
        return False, f"npm install failed: {e}"