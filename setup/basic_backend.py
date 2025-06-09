#!/usr/bin/env python3
"""
Basic Backend Setup - pip, network, virtual environment, basic dependencies, .env file
These components usually work correctly on first try, so they're grouped together.
"""

import os
import sys
import subprocess
import urllib.request
from pathlib import Path

def check_python_version():
    """Check if Python version is adequate."""
    version = sys.version_info
    if version.major < 3 or (version.major == 3 and version.minor < 8):
        print(f"❌ Python 3.8+ required. Current: {sys.version}")
        return False
    print(f"✅ Python {sys.version.split()[0]} is adequate")
    return True

def check_pip():
    """Check if pip is available."""
    try:
        result = subprocess.run([sys.executable, "-m", "pip", "--version"], 
                              capture_output=True, text=True, check=True)
        print(f"✅ pip available: {result.stdout.strip()}")
        return True
    except subprocess.CalledProcessError:
        print("❌ pip not available")
        return False

def check_network_access():
    """Check if we can access PyPI (optional - only needed for installing packages)."""
    try:
        urllib.request.urlopen('https://pypi.org', timeout=5)
        print("✅ Network access to PyPI confirmed (for package installation)")
        return True
    except Exception:
        print("⚠️  No network access to PyPI (only needed for installing packages)")
        return True  # Return True since network isn't required to run the game

def check_virtual_environment():
    """Check if virtual environment exists and is functional."""
    venv_path = Path("backend/venv")
    
    if not venv_path.exists():
        print("❌ Virtual environment not found at backend/venv")
        return False
    
    # Check if Python executable exists in venv
    python_path = venv_path / "Scripts" / "python.exe"
    pip_path = venv_path / "Scripts" / "pip.exe"
    
    if not python_path.exists():
        print("❌ Virtual environment Python not found")
        return False
    
    print("✅ Virtual environment exists and appears functional")
    return True

def check_basic_dependencies():
    """Check if basic Flask dependencies are installed."""
    pip_path = Path("backend/venv/Scripts/pip.exe")
    
    if not pip_path.exists():
        print("❌ Virtual environment pip not found")
        return False
    
    # Check for Flask
    try:
        result = subprocess.run([str(pip_path), "show", "Flask"], 
                              capture_output=True, text=True, check=True)
        if "Version:" in result.stdout:
            print("✅ Flask is installed")
            return True
    except subprocess.CalledProcessError:
        pass
    
    print("❌ Basic dependencies not installed")
    return False

def check_env_file():
    """Check if .env file exists."""
    env_file = Path(".env")
    if env_file.exists():
        print("✅ .env file exists")
        return True
    else:
        print("❌ .env file not found")
        return False

def check_basic_backend_requirements():
    """Check all basic backend requirements."""
    # Silent check - only return True/False
    checks = [
        check_python_version(),
        check_pip(),
        True,  # Network is optional - only needed for installing
        check_virtual_environment(),
        check_basic_dependencies(),
        check_env_file()
    ]
    
    # Also run network check for info, but don't fail on it
    check_network_access()
    
    return all(checks)

def check_basic_backend_requirements_silent():
    """Silently check basic backend requirements."""
    try:
        version = sys.version_info
        if version.major < 3 or (version.major == 3 and version.minor < 8):
            return False
        
        # Check pip
        try:
            subprocess.run([sys.executable, "-m", "pip", "--version"], 
                          capture_output=True, text=True, check=True)
        except subprocess.CalledProcessError:
            return False
        
        # Network is optional - skip check
        
        # Check venv
        venv_path = Path("backend/venv")
        if not venv_path.exists():
            return False
        python_path = venv_path / "Scripts" / "python.exe"
        if not python_path.exists():
            return False
        
        # Check Flask
        pip_path = Path("backend/venv/Scripts/pip.exe")
        if not pip_path.exists():
            return False
        try:
            result = subprocess.run([str(pip_path), "show", "Flask"], 
                                  capture_output=True, text=True, check=True)
            if "Version:" not in result.stdout:
                return False
        except subprocess.CalledProcessError:
            return False
        
        # Check .env
        env_file = Path(".env")
        if not env_file.exists():
            return False
        
        return True
    except Exception:
        return False

def create_virtual_environment():
    """Create virtual environment."""
    venv_path = Path("backend/venv")
    
    if venv_path.exists():
        print("✅ Virtual environment already exists")
        return True
    
    print("Creating virtual environment...")
    try:
        subprocess.run([sys.executable, "-m", "venv", str(venv_path)], check=True)
        print("✅ Virtual environment created")
        return True
    except subprocess.CalledProcessError as e:
        print(f"❌ Failed to create virtual environment: {e}")
        return False

def install_basic_dependencies():
    """Install basic Flask dependencies (without llama-cpp-python)."""
    pip_path = Path("backend/venv/Scripts/pip.exe")
    
    if not pip_path.exists():
        print(f"❌ Virtual environment pip not found at {pip_path}")
        return False
    
    # Upgrade pip first
    try:
        print("Upgrading pip...")
        subprocess.run([str(pip_path), "install", "--upgrade", "pip"], check=True)
        print("✅ pip upgraded")
    except subprocess.CalledProcessError:
        print("⚠️  Failed to upgrade pip, continuing...")
    
    # Basic dependencies (excluding llama-cpp-python)
    basic_deps = [
        "Flask==3.0.0",
        "Flask-SQLAlchemy==3.1.1", 
        "Flask-CORS==4.0.0",
        "PyMySQL==1.1.0",
        "python-dotenv==1.0.0",
        "requests==2.31.0"
    ]
    
    print("Installing basic dependencies...")
    for dep in basic_deps:
        try:
            pkg_name = dep.split("==")[0]
            # Check if already installed
            try:
                subprocess.run([str(pip_path), "show", pkg_name], 
                             capture_output=True, text=True, check=True)
                print(f"✅ {pkg_name} already installed")
                continue
            except subprocess.CalledProcessError:
                pass
            
            print(f"Installing {dep}...")
            subprocess.run([str(pip_path), "install", dep], check=True)
            print(f"✅ {pkg_name} installed")
        except subprocess.CalledProcessError as e:
            print(f"❌ Failed to install {dep}: {e}")
            return False
    
    print("✅ Basic dependencies installed")
    return True

def create_env_file():
    """Create .env file from template or create basic one."""
    env_file = Path(".env")
    env_example = Path(".env.example")
    
    if env_file.exists():
        return True  # Don't print if running silently
    
    if env_example.exists():
        try:
            with open(env_example, 'r') as example:
                content = example.read()
            with open(env_file, 'w') as env:
                env.write(content)
            print("✅ .env file created from template")
        except Exception as e:
            print(f"❌ Failed to create .env from example: {e}")
            return False
    else:
        env_content = """# Monster Hunter Game Environment Variables

# Database Configuration
DB_HOST=localhost
DB_PORT=3306
DB_NAME=monster_hunter_game
DB_USER=root
DB_PASSWORD=your_mysql_password_here

# Flask Configuration
FLASK_ENV=development
FLASK_DEBUG=True
SECRET_KEY=your-secret-key-here

# LLM Configuration
LLM_MODEL_PATH=models/your-model.gguf
LLM_CONTEXT_SIZE=4096
LLM_GPU_LAYERS=35

# Game Configuration
MAX_PARTY_SIZE=4
"""
        try:
            with open(env_file, 'w') as f:
                f.write(env_content)
            print("✅ .env file created")
        except Exception as e:
            print(f"❌ Failed to create .env file: {e}")
            return False
    
    return True

def setup_basic_backend_interactive():
    """Interactive setup for basic backend components."""
    print("Setting up basic backend components...")
    
    # Create virtual environment
    if not create_virtual_environment():
        return False
    
    # Install basic dependencies
    if not install_basic_dependencies():
        return False
    
    # Create .env file
    if not create_env_file():
        return False
    
    # Ask for database password
    print("\n📋 Database Configuration")
    print("The .env file has been created with default settings.")
    
    env_file = Path(".env")
    try:
        with open(env_file, 'r') as f:
            content = f.read()
        
        if "your_mysql_password_here" in content:
            print("You need to set your MySQL password in the .env file.")
            
            while True:
                choice = input("Do you want to (E)nter password now, (S)kip for later, or (C)ancel? [E/S/C]: ").upper().strip()
                
                if choice == 'E':
                    password = input("Enter your MySQL root password: ").strip()
                    if password:
                        updated_content = content.replace("your_mysql_password_here", password)
                        with open(env_file, 'w') as f:
                            f.write(updated_content)
                        print("✅ Database password updated in .env file")
                        break
                    else:
                        print("Empty password entered. Please try again or skip.")
                elif choice == 'S':
                    print("⏭️  Skipping password setup. You'll need to edit .env manually later.")
                    break
                elif choice == 'C':
                    print("❌ Setup cancelled")
                    return False
                else:
                    print("Please enter E, S, or C")
    
    except Exception as e:
        print(f"❌ Error updating .env file: {e}")
        return False
    
    print("✅ Basic backend setup completed")
    return True

def auto_setup_basic_backend():
    """Automatically set up basic backend requirements, only showing output when installing."""
    # Check if everything is already working
    if check_basic_backend_requirements_silent():
        return True  # All good, no output needed
    
    print("Setting up basic backend requirements...")
    
    # Create virtual environment if needed
    venv_path = Path("backend/venv")
    if not venv_path.exists():
        print("Creating virtual environment...")
        try:
            subprocess.run([sys.executable, "-m", "venv", str(venv_path)], check=True)
            print("✅ Virtual environment created")
        except subprocess.CalledProcessError as e:
            print(f"❌ Failed to create virtual environment: {e}")
            return False
    
    # Install basic dependencies if needed
    pip_path = Path("backend/venv/Scripts/pip.exe")
    if pip_path.exists():
        try:
            result = subprocess.run([str(pip_path), "show", "Flask"], 
                                  capture_output=True, text=True, check=True)
            if "Version:" not in result.stdout:
                raise subprocess.CalledProcessError(1, "Flask not found")
        except subprocess.CalledProcessError:
            if not install_basic_dependencies():
                return False
    else:
        print("❌ Virtual environment pip not found")
        return False
    
    # Create .env file if needed
    env_file = Path(".env")
    if not env_file.exists():
        if not create_env_file():
            return False
    
    print("✅ Basic backend setup completed")
    return True

if __name__ == "__main__":
    if len(sys.argv) > 1 and sys.argv[1] == "setup":
        setup_basic_backend_interactive()
    elif len(sys.argv) > 1 and sys.argv[1] == "auto":
        auto_setup_basic_backend()
    else:
        check_basic_backend_requirements()