#!/usr/bin/env python3
"""
Basic Backend Installation Module
Pure installation logic for basic backend requirements
"""

import sys
import subprocess
from pathlib import Path
from setup.utils.env_utils import create_env_file_from_template, update_env_config

def create_virtual_environment():
    """Create virtual environment."""
    venv_path = Path("venv")
    
    if venv_path.exists():
        return True, "Virtual environment already exists"
    
    try:
        subprocess.run([sys.executable, "-m", "venv", str(venv_path)], check=True)
        return True, "Virtual environment created"
    except subprocess.CalledProcessError as e:
        return False, f"Failed to create virtual environment: {e}"

def install_basic_dependencies():
    """Install basic Flask dependencies (without llama-cpp-python)."""
    pip_path = Path("venv/Scripts/pip.exe")
    
    if not pip_path.exists():
        return False, f"Virtual environment pip not found at {pip_path}"
    
    # Upgrade pip first
    try:
        subprocess.run([str(pip_path), "install", "--upgrade", "pip"], check=True)
    except subprocess.CalledProcessError:
        pass  # Continue if pip upgrade fails
    
    # Basic dependencies (excluding llama-cpp-python)
    basic_deps = [
        "Flask==3.0.0",
        "Flask-SQLAlchemy==3.1.1", 
        "Flask-CORS==4.0.0",
        "PyMySQL==1.1.0",
        "python-dotenv==1.0.0",
        "requests==2.31.0"
    ]
    
    for dep in basic_deps:
        try:
            pkg_name = dep.split("==")[0]
            # Check if already installed
            try:
                subprocess.run([str(pip_path), "show", pkg_name], 
                             capture_output=True, text=True, check=True)
                continue  # Already installed
            except subprocess.CalledProcessError:
                pass
            
            subprocess.run([str(pip_path), "install", dep], check=True)
        except subprocess.CalledProcessError as e:
            return False, f"Failed to install {dep}: {e}"
    
    return True, "Basic dependencies installed"

def create_env_file():
    """Create .env file from template."""
    return create_env_file_from_template()

def auto_setup_basic_backend():
    """Automatically set up basic backend requirements, only showing output when installing."""
    print("Setting up basic backend requirements...")
    
    # Create virtual environment if needed
    venv_path = Path("venv")
    if not venv_path.exists():
        print("Creating virtual environment...")
        success, message = create_virtual_environment()
        if success:
            print("✅ Virtual environment created")
        else:
            print(f"❌ {message}")
            return False
    
    # Install basic dependencies if needed
    pip_path = Path("venv/Scripts/pip.exe")
    if pip_path.exists():
        try:
            result = subprocess.run([str(pip_path), "show", "Flask"], 
                                  capture_output=True, text=True, check=True)
            if "Version:" not in result.stdout:
                raise subprocess.CalledProcessError(1, "Flask not found")
        except subprocess.CalledProcessError:
            success, message = install_basic_dependencies()
            if not success:
                print(f"❌ {message}")
                return False
    else:
        print("❌ Virtual environment pip not found")
        return False
    
    # Create .env file if needed
    from setup.utils.env_utils import env_file_exists
    if not env_file_exists():
        success, message = create_env_file()
        if not success:
            print(f"❌ {message}")
            return False
    
    print("✅ Basic backend setup completed")
    return True