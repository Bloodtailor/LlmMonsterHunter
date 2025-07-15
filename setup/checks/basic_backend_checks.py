#!/usr/bin/env python3
"""
Basic Backend Checks Module
Pure detection logic for basic backend requirements
Returns data instead of printing for clean UX flow
"""

import sys
import subprocess
import urllib.request
from pathlib import Path
from setup.utils.env_utils import env_file_exists

def check_python_version():
    """Check if Python version is adequate."""
    version = sys.version_info
    if version.major < 3 or (version.major == 3 and version.minor < 8):
        return False, f"Python 3.8+ required. Current: {sys.version}"
    return True, f"Python {sys.version.split()[0]} is adequate"

def check_pip():
    """Check if pip is available."""
    try:
        result = subprocess.run([sys.executable, "-m", "pip", "--version"], 
                              capture_output=True, text=True, check=True)
        return True, f"pip available: {result.stdout.strip()}"
    except subprocess.CalledProcessError:
        return False, "pip not available"

def check_network_access():
    """Check if we can access PyPI (optional - only needed for installing packages)."""
    try:
        urllib.request.urlopen('https://pypi.org', timeout=5)
        return True, "Network access to PyPI confirmed (for package installation)"
    except Exception:
        return True, "No network access to PyPI (only needed for installing packages)"

def check_virtual_environment():
    """Check if virtual environment exists and is functional."""
    venv_path = Path("venv")
    
    if not venv_path.exists():
        return False, "Virtual environment not found at venv"
    
    # Check if Python executable exists in venv
    python_path = venv_path / "Scripts" / "python.exe"
    pip_path = venv_path / "Scripts" / "pip.exe"
    
    if not python_path.exists():
        return False, "Virtual environment Python not found"
    
    return True, "Virtual environment exists and appears functional"

def check_basic_dependencies():
    """Check if basic Flask dependencies are installed."""
    pip_path = Path("venv/Scripts/pip.exe")
    
    if not pip_path.exists():
        return False, "Virtual environment pip not found"
    
    # Check for Flask
    try:
        result = subprocess.run([str(pip_path), "show", "Flask"], 
                              capture_output=True, text=True, check=True)
        if "Version:" in result.stdout:
            return True, "Flask is installed"
    except subprocess.CalledProcessError:
        pass
    
    return False, "Basic dependencies not installed"

def check_env_file():
    """Check if .env file exists."""
    if env_file_exists():
        return True, ".env file exists"
    else:
        return False, ".env file not found"

def check_basic_backend_requirements():
    """Check all basic backend requirements (for orchestration)."""
    
    python_ok, _ = check_python_version()
    pip_ok, _ = check_pip()
    venv_ok, _ = check_virtual_environment()
    deps_ok, _ = check_basic_dependencies()
    env_ok, _ = check_env_file()
    
    # Network is optional - only needed for installing
    return all([python_ok, pip_ok, venv_ok, deps_ok, env_ok])

def check_basic_backend_requirements_silent():
    """Silently check basic backend requirements."""
    try:
        # Use the tuple-returning functions but only keep the boolean result
        python_ok, _ = check_python_version()
        pip_ok, _ = check_pip()
        venv_ok, _ = check_virtual_environment()
        deps_ok, _ = check_basic_dependencies()
        env_ok, _ = check_env_file()
        
        return all([python_ok, pip_ok, venv_ok, deps_ok, env_ok])
    except Exception:
        return False
    
def get_basic_backend_diagnostic(include_overall=False):
    """
    Get comprehensive basic backend diagnostic information.
    Used by flows to understand what specifically needs to be addressed.
    
    Args:
        include_overall (bool): Whether to include overall requirement check
    
    Returns:
        dict: All basic backend check results for detailed analysis
    """
    python_ok, python_msg = check_python_version()
    pip_ok, pip_msg = check_pip()
    network_ok, network_msg = check_network_access()
    venv_ok, venv_msg = check_virtual_environment()
    deps_ok, deps_msg = check_basic_dependencies()
    env_ok, env_msg = check_env_file()
    
    result = {
        'python_version': (python_ok, python_msg),
        'pip': (pip_ok, pip_msg),
        'network_access': (network_ok, network_msg),
        'virtual_environment': (venv_ok, venv_msg),
        'basic_dependencies': (deps_ok, deps_msg),
        'env_file': (env_ok, env_msg),
    }
    
    if include_overall:
        overall_ok = check_basic_backend_requirements()
        result['overall'] = (overall_ok, "All basic backend requirements met" if overall_ok else "Some basic backend requirements missing")
    
    return result