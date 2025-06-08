#!/usr/bin/env python
"""
Complete setup script for the Monster Hunter Game environment.
Checks system requirements and sets up the environment with CUDA support.
"""

import os
import sys
import platform
import subprocess
import shutil
from pathlib import Path

def print_header(text):
    """Print a formatted header."""
    print("\n" + "=" * 60)
    print(text.center(60))
    print("=" * 60 + "\n")

def print_section(text):
    """Print a section header."""
    print(f"\n{text}")
    print("-" * len(text))

def check_python_version():
    """Check if the Python version is adequate."""
    print("Checking Python version...")
    version = sys.version_info
    
    if version.major < 3 or (version.major == 3 and version.minor < 8):
        print("ERROR: Python 3.8 or higher is required.")
        print(f"Current Python version: {platform.python_version()}")
        return False
    
    print(f"✅ Python version {platform.python_version()} is adequate.")
    if version.minor == 11:
        print("✅ Using recommended Python 3.11")
    return True

def check_nodejs():
    """Check for Node.js and npm for React frontend."""
    try:
        # Check Node.js
        result = subprocess.run(["node", "--version"], capture_output=True, text=True, check=True)
        node_version = result.stdout.strip()
        print(f"✅ Node.js found: {node_version}")
        
        # Check npm using shutil.which
        npm_path = shutil.which("npm") or shutil.which("npm.cmd") or shutil.which("npm.exe")
        
        if npm_path:
            try:
                result = subprocess.run([npm_path, "--version"], capture_output=True, text=True, check=True)
                npm_version = result.stdout.strip()
                print(f"✅ npm found: {npm_version} at {npm_path}")
            except subprocess.CalledProcessError:
                print(f"✅ npm found at {npm_path} (version check failed but executable exists)")
        else:
            print("✅ npm should be available (comes with Node.js)")
            print("   Note: npm not found in PATH but Node.js is installed")
        
        # Check if Node version is adequate (16+)
        try:
            version_num = int(node_version.replace('v', '').split('.')[0])
            if version_num < 16:
                print(f"⚠️  Node.js {node_version} detected. Node.js 16+ recommended for React.")
            else:
                print(f"✅ Node.js version is adequate for React development")
        except:
            print("⚠️  Could not parse Node.js version, but should be fine")
        
        return True  # Return True since Node.js is found
        
    except (FileNotFoundError, subprocess.CalledProcessError):
        print("❌ Node.js not found")
        print("   Download from: https://nodejs.org/")
        print("   Required for React frontend development")
        print("   npm (Node Package Manager) comes included with Node.js")
        return False

def check_mysql_cli():
    """Check if MySQL command line client is available."""
    try:
        # Try to run mysql --version to see if it's available
        result = subprocess.run(["mysql", "--version"], 
                              capture_output=True, text=True, check=True)
        print(f"✅ MySQL CLI found: {result.stdout.strip()}")
        return True
    except FileNotFoundError:
        print("❌ MySQL command line client not found")
        return False
    except subprocess.CalledProcessError:
        print("⚠️  MySQL CLI found but may have issues")
        return True  # At least the command exists
    except Exception as e:
        print(f"❌ Error checking MySQL CLI: {e}")
        return False

def check_mysql():
    """Enhanced MySQL check for system requirements."""
    print("Checking MySQL Server and command line tools...")
    
    # Check if MySQL CLI is available
    cli_available = check_mysql_cli()
    
    # Check for MySQL Workbench first (easier to detect)
    workbench_paths = [
        "C:\\Program Files\\MySQL\\MySQL Workbench 8.0",
        "C:\\Program Files (x86)\\MySQL\\MySQL Workbench 8.0"
    ]
    
    workbench_found = any(os.path.exists(path) for path in workbench_paths)
    
    # Check for MySQL server service on Windows
    server_running = False
    try:
        result = subprocess.run(["sc", "query", "MySQL84"], capture_output=True, text=True, check=True)
        if "RUNNING" in result.stdout:
            print("✅ MySQL Server 8.4 service is running")
            server_running = True
    except subprocess.CalledProcessError:
        # Try other common service names
        for service in ["MySQL80", "MySQL", "mysqld"]:
            try:
                result = subprocess.run(["sc", "query", service], capture_output=True, text=True, check=True)
                if "RUNNING" in result.stdout:
                    print(f"✅ MySQL service '{service}' is running")
                    server_running = True
                    break
            except subprocess.CalledProcessError:
                continue
    
    # Try MySQL command line (if CLI is available)
    if cli_available:
        try:
            subprocess.run(["mysql", "-e", "SELECT 1;"], 
                          capture_output=True, check=True)
            print("✅ MySQL Server connection successful")
            return True
        except subprocess.CalledProcessError:
            print("⚠️  MySQL Server may not be running or requires authentication")
            return False
    else:
        print("   Cannot test MySQL Server connection without CLI tools")
    
    # Determine overall success
    if server_running:
        print("✅ MySQL server is running")
        return True
    elif workbench_found:
        print("✅ MySQL Workbench found")
        print("⚠️  Make sure MySQL Server is also installed and running")
        return True
    else:
        print("❌ MySQL not found")
        print("   Download MySQL Server from: https://dev.mysql.com/downloads/mysql/")
        print("   MySQL Workbench (GUI) is separate from MySQL Server")
        return False

def check_nvidia_gpu():
    """Check for NVIDIA GPU and drivers."""
    try:
        result = subprocess.run(["nvidia-smi"], capture_output=True, text=True, check=True)
        print("✅ NVIDIA GPU detected")
        
        # Parse GPU info
        lines = result.stdout.split('\n')
        for line in lines:
            if any(gpu in line for gpu in ['GeForce', 'RTX', 'GTX', 'Quadro']):
                parts = line.split('|')
                if len(parts) > 1:
                    gpu_info = parts[1].strip()
                    print(f"   GPU: {gpu_info}")
                break
        return True
        
    except (FileNotFoundError, subprocess.CalledProcessError):
        print("❌ NVIDIA GPU or drivers not detected")
        print("   Install NVIDIA GPU drivers from https://www.nvidia.com/drivers/")
        return False

def check_cuda_toolkit():
    """Check for CUDA Toolkit installation."""
    cuda_found = False
    
    # Check CUDA_PATH environment variable
    cuda_path = os.environ.get("CUDA_PATH")
    if cuda_path and os.path.exists(cuda_path):
        print(f"✅ CUDA Toolkit found: {cuda_path}")
        cuda_found = True
    
    # Check nvcc command
    try:
        result = subprocess.run(["nvcc", "--version"], capture_output=True, text=True, check=True)
        print("✅ CUDA compiler (nvcc) available")
        
        # Extract version
        for line in result.stdout.split('\n'):
            if 'release' in line.lower():
                parts = line.split('release')[1].split(',')[0].strip()
                print(f"   CUDA Version: {parts}")
                break
        cuda_found = True
    except (FileNotFoundError, subprocess.CalledProcessError):
        pass
    
    # Check common paths
    if not cuda_found:
        common_paths = [
            "C:\\Program Files\\NVIDIA GPU Computing Toolkit\\CUDA",
            "C:\\Program Files (x86)\\NVIDIA GPU Computing Toolkit\\CUDA"
        ]
        
        for path in common_paths:
            if os.path.exists(path):
                print(f"✅ CUDA Toolkit found at: {path}")
                cuda_found = True
                break
    
    if not cuda_found:
        print("❌ CUDA Toolkit not found")
        print("   Download from: https://developer.nvidia.com/cuda-toolkit")
    
    return cuda_found

def check_visual_studio():
    """Check for Visual Studio Build Tools."""
    vs_paths = [
        "C:\\Program Files\\Microsoft Visual Studio\\2022",
        "C:\\Program Files\\Microsoft Visual Studio\\2019",
        "C:\\Program Files (x86)\\Microsoft Visual Studio\\2022\\BuildTools",
        "C:\\Program Files (x86)\\Microsoft Visual Studio\\2019\\BuildTools"
    ]
    
    for path in vs_paths:
        if os.path.exists(path):
            print(f"✅ Visual Studio/Build Tools found: {path}")
            return True
    
    print("❌ Visual Studio Build Tools not found")
    print("   Download from: https://visualstudio.microsoft.com/downloads/")
    print("   Install 'C++ build tools' workload")
    return False

def check_pip_and_network():
    """Check pip and network access."""
    # Check pip
    try:
        result = subprocess.run([sys.executable, "-m", "pip", "--version"], 
                              capture_output=True, text=True, check=True)
        print(f"✅ pip available: {result.stdout.strip()}")
    except subprocess.CalledProcessError:
        print("❌ pip not available")
        return False
    
    # Check network
    try:
        import urllib.request
        urllib.request.urlopen('https://pypi.org', timeout=10)
        print("✅ Network access to PyPI confirmed")
        return True
    except:
        print("❌ Cannot access PyPI - check internet connection")
        return False

def run_system_requirements_check():
    """Run comprehensive system requirements check."""
    print_header("System Requirements Check")
    print("Checking if your system can run Monster Hunter Game with CUDA support...")
    
    checks = [
        ("Python Version", check_python_version()),
        ("Node.js & npm", check_nodejs()),
        ("MySQL Database", check_mysql()),
        ("NVIDIA GPU", check_nvidia_gpu()),
        ("CUDA Toolkit", check_cuda_toolkit()),
        ("Visual Studio Build Tools", check_visual_studio()),
        ("pip & Network", check_pip_and_network())
    ]
    
    passed_checks = sum(1 for _, result in checks if result)
    total_checks = len(checks)
    
    print_section("Requirements Summary")
    for check_name, result in checks:
        status = "✅ PASS" if result else "❌ FAIL"
        print(f"{check_name:<25} {status}")
    
    print(f"\nPassed: {passed_checks}/{total_checks} checks")
    
    if passed_checks >= 5:  # Allow some flexibility
        print("\n🎉 Most requirements met! Setup should work.")
        return True
    elif passed_checks >= 3:
        print("\n⚠️  Some requirements missing. Will try setup but may have issues.")
        choice = input("Continue anyway? (y/n): ")
        return choice.lower() == 'y'
    else:
        print("\n❌ Critical requirements missing. Setup will likely fail.")
        choice = input("Continue anyway? (y/n): ")
        return choice.lower() == 'y'

def create_virtual_environment():
    """Create a virtual environment if it doesn't exist."""
    venv_path = Path("backend/venv")
    
    if venv_path.exists():
        print("✅ Virtual environment already exists in backend/venv")
        
        # Quick check if it's working
        if platform.system() == "Windows":
            python_path = venv_path / "Scripts" / "python.exe"
        else:
            python_path = venv_path / "bin" / "python"
            
        if python_path.exists():
            print("✅ Virtual environment appears to be functional")
            return True
        else:
            print("⚠️  Virtual environment exists but may be corrupted, recreating...")
            shutil.rmtree(venv_path)

    print("Creating virtual environment in backend/venv...")
    try:
        subprocess.run([sys.executable, "-m", "venv", str(venv_path)], check=True)
        print("✅ Virtual environment created successfully.")
        return True
    except subprocess.CalledProcessError:
        print("ERROR: Failed to create virtual environment.")
        return False

def check_llama_cpp_cuda(pip_path):
    """Check if llama-cpp-python is installed and has CUDA support."""
    try:
        # First check if llama-cpp-python is installed
        result = subprocess.run([str(pip_path), "show", "llama-cpp-python"], 
                              capture_output=True, text=True, check=True)
        if "Version:" not in result.stdout:
            return False, "not_installed"
        
        print("✅ llama-cpp-python already installed")
        
        # For now, assume it's working if it's installed
        # We could add more sophisticated CUDA testing here later
        print("✅ Assuming CUDA support (skipping 20-minute reinstall)")
        return True, "cuda_assumed"
            
    except subprocess.CalledProcessError:
        return False, "not_installed"

def install_llama_cpp_python(pip_path):
    """Install llama-cpp-python with CUDA support using multiple methods."""
    print("Installing llama-cpp-python with CUDA support...")
    print("⚠️  This may take 10-15 minutes to compile!")
    
    # Method 1: Environment variables for CUDA build
    print("\nMethod 1: Building from source with CUDA...")
    env = os.environ.copy()
    env["CMAKE_ARGS"] = "-DLLAMA_CUBLAS=on"
    env["FORCE_CMAKE"] = "1"
    
    try:
        subprocess.run([
            str(pip_path), "install", "llama-cpp-python", "--no-cache-dir", "--force-reinstall"
        ], env=env, check=True)
        print("🎉 Successfully built with CUDA support!")
        return True
    except subprocess.CalledProcessError:
        print("❌ Source build failed, trying Method 2...")
    
    # Method 2: Pre-built CUDA wheel
    print("\nMethod 2: Trying CUDA wheel repository...")
    try:
        subprocess.run([
            str(pip_path), "install", "llama-cpp-python",
            "--extra-index-url", "https://abetlen.github.io/llama-cpp-python/whl/cu121"
        ], check=True)
        print("🎉 Successfully installed from CUDA wheel repository!")
        return True
    except subprocess.CalledProcessError:
        print("❌ Wheel repository failed, falling back to CPU version...")
    
    # Fallback: CPU-only version
    print("\nFallback: Installing CPU-only version...")
    try:
        subprocess.run([str(pip_path), "install", "llama-cpp-python"], check=True)
        print("✅ Installed CPU-only version as fallback")
        print("⚠️  Your models will run on CPU only (slower but still works)")
        return True
    except subprocess.CalledProcessError as e:
        print(f"ERROR: Even CPU installation failed: {e}")
        return False

def install_backend_dependencies():
    """Install backend dependencies with CUDA support for llama-cpp-python."""
    print_section("Installing Backend Dependencies")
    
    # Determine pip path
    if platform.system() == "Windows":
        pip_path = Path("backend/venv/Scripts/pip.exe")  # Add .exe extension
        python_path = Path("backend/venv/Scripts/python.exe")
    else:
        pip_path = Path("backend/venv/bin/pip")
        python_path = Path("backend/venv/bin/python")
    
    if not pip_path.exists():
        print(f"ERROR: Virtual environment pip not found at {pip_path}")
        # Try alternative paths
        alt_pip = Path("backend/venv/Scripts/pip") if platform.system() == "Windows" else None
        if alt_pip and alt_pip.exists():
            pip_path = alt_pip
            print(f"Found pip at alternative path: {pip_path}")
        else:
            print("Virtual environment may be corrupted. Please delete backend/venv and run again.")
            return False
    
    # Check if llama-cpp-python already installed
    llama_installed, status = check_llama_cpp_cuda(pip_path)
    
    # Upgrade pip first
    try:
        print("Upgrading pip...")
        subprocess.run([str(pip_path), "install", "--upgrade", "pip"], check=True)
        print("✅ pip upgraded successfully")
    except subprocess.CalledProcessError:
        print("⚠️  Failed to upgrade pip, continuing...")
    
    # Install from requirements.txt first (without llama-cpp-python)
    print("Installing base dependencies from requirements.txt...")
    try:
        # Read requirements and filter out llama-cpp-python
        req_file = Path("backend/requirements.txt")
        if not req_file.exists():
            print(f"⚠️  requirements.txt not found at {req_file}")
            print("Will install basic dependencies manually...")
            basic_deps = ["Flask==3.0.0", "Flask-SQLAlchemy==3.1.1", "Flask-CORS==4.0.0", 
                         "PyMySQL==1.1.0", "python-dotenv==1.0.0", "requests==2.31.0"]
            requirements = basic_deps
        else:
            with open(req_file, "r") as f:
                requirements = [line.strip() for line in f.readlines() 
                              if line.strip() and not line.startswith("llama-cpp-python")]
        
        for req in requirements:
            if req and not req.startswith("#"):
                # Check if already installed
                pkg_name = req.split("==")[0].split(">=")[0].split("<=")[0]
                try:
                    subprocess.run([str(pip_path), "show", pkg_name], 
                                 capture_output=True, text=True, check=True)
                    print(f"✅ {pkg_name} already installed")
                except subprocess.CalledProcessError:
                    print(f"Installing {req}...")
                    try:
                        subprocess.run([str(pip_path), "install", req], check=True)
                        print(f"✅ {pkg_name} installed successfully")
                    except subprocess.CalledProcessError as e:
                        print(f"❌ Failed to install {req}: {e}")
                        return False
        
        print("✅ Base dependencies installed successfully")
        
    except Exception as e:
        print(f"❌ Error installing base dependencies: {e}")
        return False
    
    # Handle llama-cpp-python installation
    if not llama_installed:
        if not install_llama_cpp_python(pip_path):
            print("❌ Failed to install llama-cpp-python")
            return False
    
    print("✅ Backend dependencies installation completed!")
    return True

def install_frontend_dependencies():
    """Install frontend dependencies using npm."""
    print_section("Installing Frontend Dependencies")
    
    frontend_path = Path("frontend")
    if not frontend_path.exists():
        print("⚠️  Frontend directory not found, skipping npm install")
        return True
    
    node_modules_path = frontend_path / "node_modules"
    if node_modules_path.exists():
        print("✅ Frontend dependencies already installed (node_modules exists)")
        print("⚠️  Run 'npm install' in frontend/ if you need to update dependencies")
        return True
    
    # Use shutil.which to find npm reliably
    npm_path = shutil.which("npm") or shutil.which("npm.cmd") or shutil.which("npm.exe")
    
    if not npm_path:
        print("❌ npm not found in PATH")
        print("   Please install Node.js from https://nodejs.org/")
        print("   Then run manually: cd frontend && npm install")
        return False
    
    try:
        print(f"Installing React dependencies using npm at: {npm_path}")
        subprocess.run([npm_path, "install"], cwd=str(frontend_path), check=True)
        print("✅ Frontend dependencies installed successfully")
        return True
    except subprocess.CalledProcessError as e:
        print(f"❌ npm install failed: {e}")
        print("   Please run manually: cd frontend && npm install")
        return False

def create_env_file():
    """Create .env file if it doesn't exist."""
    env_file = Path(".env")
    env_example = Path(".env.example")
    
    if env_file.exists():
        print("✅ .env file already exists")
        return True
    
    if env_example.exists():
        print("Creating .env from .env.example...")
        with open(env_example, 'r') as example:
            content = example.read()
        with open(env_file, 'w') as env:
            env.write(content)
        print("✅ .env file created from template")
        print("⚠️  Please update .env with your MySQL password and model path")
        return True
    else:
        print("Creating basic .env file...")
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
        with open(env_file, 'w') as f:
            f.write(env_content)
        print("✅ Basic .env file created")
        print("⚠️  Please update .env with your actual MySQL password and model path")
        return True

def check_model_directory():
    """Check and create models directory."""
    models_dir = Path("models")
    
    if not models_dir.exists():
        models_dir.mkdir()
        print("✅ Created models directory")
    else:
        print("✅ Models directory exists")
    
    # Check for any existing models
    model_files = list(models_dir.glob("*.gguf"))
    if model_files:
        print("✅ Found existing model files:")
        for model in model_files:
            print(f"   {model.name}")
    else:
        print("⚠️  No model files found in models/ directory")
        print("   You'll need to download a GGUF model file")
        print("   Recommended: Llama 2 7B Chat or Mistral 7B Instruct")
    
    return True

def create_database():
    """Try to create the database if it doesn't exist."""
    print_section("Database Setup")
    
    try:
        # This is a basic attempt - user may need to do this manually
        print("Attempting to create database...")
        subprocess.run([
            "mysql", "-e", 
            "CREATE DATABASE IF NOT EXISTS monster_hunter_game;"
        ], check=True)
        print("✅ Database created successfully")
        return True
    except FileNotFoundError:
        print("❌ MySQL command line client not found")
        print("")
        print("The 'mysql' command is not available on your system.")
        print("This usually means you need to install the MySQL command line client.")
        print("")
        print("📋 How to fix this:")
        print("   Option 1 - Install MySQL command line tools:")
        print("     • Download MySQL Community Server from https://dev.mysql.com/downloads/mysql/")
        print("     • During installation, make sure to include 'MySQL Command Line Client'")
        print("     • Add MySQL bin directory to your system PATH")
        print("     • Typical path: C:\\Program Files\\MySQL\\MySQL Server 8.x\\bin")
        print("")
        print("   Option 2 - Use MySQL Workbench to create database manually:")
        print("     • Open MySQL Workbench")
        print("     • Connect to your local server")
        print("     • Run this SQL command: CREATE DATABASE IF NOT EXISTS monster_hunter_game;")
        print("")
        print("   Option 3 - Skip database creation (you can create it later):")
        print("     • The rest of the setup will continue")
        print("     • You'll need to create the database before running the game")
        print("")
        return False
    except subprocess.CalledProcessError as e:
        print("⚠️  MySQL command failed")
        print(f"   Error: {e}")
        print("   This usually means MySQL server is not running or connection failed")
        print("")
        print("📋 How to fix this:")
        print("   • Make sure MySQL Server is running (check Windows Services)")
        print("   • Verify MySQL server is accessible")
        print("   • Or create the database manually using MySQL Workbench")
        print("")
        return False
    except Exception as e:
        print(f"❌ Unexpected error creating database: {e}")
        print("   Please create the database manually using MySQL Workbench")
        return False

def main():
    """Main function to run all setup steps."""
    print_header("Monster Hunter Game Environment Setup")
    print("This script will set up your environment for the AI-powered monster hunting game.")
    print("🔄 This script is safe to run multiple times - it will skip completed steps.")
    
    # Run system requirements check first
    if not run_system_requirements_check():
        print("Setup cancelled by user.")
        sys.exit(1)
    
    # Proceed with setup - track success of each step
    setup_steps = [
        ("Virtual Environment", create_virtual_environment()),
        ("Backend Dependencies", install_backend_dependencies()),
        ("Frontend Dependencies", install_frontend_dependencies()),
        ("Environment File", create_env_file()),
        ("Model Directory", check_model_directory()),
        ("Database Setup", create_database())
    ]
    
    # Summary of results
    print_header("Setup Results")
    successful_steps = 0
    for step_name, success in setup_steps:
        status = "✅ SUCCESS" if success else "❌ FAILED"
        print(f"{step_name:<20} {status}")
        if success:
            successful_steps += 1
    
    print(f"\nCompleted: {successful_steps}/{len(setup_steps)} setup steps")
    
    if successful_steps == len(setup_steps):
        print_header("Setup Complete!")
        print("🎉 Environment setup finished successfully!")
    elif successful_steps >= 4:
        print_header("Setup Mostly Complete!")
        print("⚠️  Most steps completed - you can continue with manual fixes")
    else:
        print_header("Setup Had Issues")
        print("❌ Several steps failed - please review errors above")
    
    print("\nNext steps:")
    print("1. Download a GGUF model file to the models/ directory")
    print("   Recommended: Llama 2 7B Chat or Mistral 7B Instruct")
    print("2. Update .env file with your MySQL password and model path")
    print("3. Verify Node.js/npm: run 'node --version' and 'npm --version'")
    print("4. Start backend: python backend/run.py")
    print("5. Start frontend: cd frontend && npm start")
    print("6. Open http://localhost:3000 to play the game")
    
    print(f"\n📋 Your setup summary:")
    print(f"   Python: {platform.python_version()}")
    print(f"   Platform: {platform.system()} {platform.release()}")
    print(f"   Backend environment: ./backend/venv/")
    print(f"   Frontend dependencies: ./frontend/node_modules/")
    print(f"   Configuration: ./.env")
    print(f"   Models directory: ./models/")
    
    input("\nPress Enter to exit...")

if __name__ == "__main__":
    main()