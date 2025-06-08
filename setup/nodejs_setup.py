#!/usr/bin/env python3
"""
Node.js and npm Setup Module
Checks for Node.js, npm, and handles React frontend dependencies
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
        print(f"✅ Node.js found: {version}")
        
        # Check if version is adequate (16+)
        try:
            version_num = int(version.replace('v', '').split('.')[0])
            if version_num < 16:
                print(f"⚠️  Node.js {version} detected. Node.js 16+ recommended for React.")
                return False
            else:
                print(f"✅ Node.js version is adequate for React development")
                return True
        except Exception:
            print("⚠️  Could not parse Node.js version, but executable found")
            return True
            
    except (FileNotFoundError, subprocess.CalledProcessError):
        print("❌ Node.js not found")
        return False

def check_npm():
    """Check if npm is available."""
    npm_path = shutil.which("npm") or shutil.which("npm.cmd") or shutil.which("npm.exe")
    
    if npm_path:
        try:
            result = subprocess.run([npm_path, "--version"], capture_output=True, text=True, check=True)
            version = result.stdout.strip()
            print(f"✅ npm found: {version} at {npm_path}")
            return True
        except subprocess.CalledProcessError:
            print(f"✅ npm found at {npm_path} (version check failed but executable exists)")
            return True
    else:
        print("❌ npm not found in PATH")
        return False

def check_frontend_dependencies():
    """Check if React frontend dependencies are installed."""
    frontend_path = Path("frontend")
    node_modules_path = frontend_path / "node_modules"
    
    if not frontend_path.exists():
        print("⚠️  Frontend directory not found")
        return False
    
    if node_modules_path.exists():
        print("✅ Frontend dependencies installed (node_modules exists)")
        return True
    else:
        print("❌ Frontend dependencies not installed")
        return False

def check_nodejs_requirements():
    """Check all Node.js related requirements."""
    print("Checking Node.js and npm requirements...")
    
    checks = [
        check_nodejs(),
        check_npm(),
        check_frontend_dependencies()
    ]
    
    return all(checks)

def install_frontend_dependencies():
    """Install React frontend dependencies using npm."""
    frontend_path = Path("frontend")
    
    if not frontend_path.exists():
        print("❌ Frontend directory not found")
        return False
    
    # Check if already installed
    node_modules_path = frontend_path / "node_modules"
    if node_modules_path.exists():
        print("✅ Frontend dependencies already installed")
        return True
    
    # Find npm executable
    npm_path = shutil.which("npm") or shutil.which("npm.cmd") or shutil.which("npm.exe")
    
    if not npm_path:
        print("❌ npm not found in PATH")
        return False
    
    try:
        print(f"Installing React dependencies using npm at: {npm_path}")
        print("This may take a few minutes...")
        subprocess.run([npm_path, "install"], cwd=str(frontend_path), check=True)
        print("✅ Frontend dependencies installed successfully")
        return True
    except subprocess.CalledProcessError as e:
        print(f"❌ npm install failed: {e}")
        return False

def setup_nodejs_interactive():
    """Interactive setup for Node.js and npm."""
    print("Setting up Node.js and React frontend...")
    
    # Check Node.js
    if not check_nodejs():
        print("\n❌ Node.js is not installed or version is too old")
        print("📋 To fix this:")
        print("1. Go to https://nodejs.org/")
        print("2. Download and install Node.js 16+ (LTS recommended)")
        print("3. npm comes included with Node.js")
        print("4. After installation, restart your command prompt")
        print("5. Run this setup again")
        
        input("Press Enter after installing Node.js...")
        
        # Check again
        if not check_nodejs():
            print("❌ Node.js still not found. Please install and try again.")
            return False
    
    # Check npm
    if not check_npm():
        print("\n❌ npm is not available")
        print("📋 npm should come with Node.js. Try:")
        print("1. Restart your command prompt")
        print("2. Run 'npm --version' to test")
        print("3. If still not working, reinstall Node.js from nodejs.org")
        
        input("Press Enter after fixing npm...")
        
        if not check_npm():
            print("❌ npm still not found. Please reinstall Node.js.")
            return False
    
    # Install frontend dependencies
    if not check_frontend_dependencies():
        print("\n📦 Installing React frontend dependencies...")
        if not install_frontend_dependencies():
            print("❌ Failed to install frontend dependencies")
            print("You can try manually: cd frontend && npm install")
            return False
    
    print("✅ Node.js and React frontend setup completed")
    return True

if __name__ == "__main__":
    if len(sys.argv) > 1 and sys.argv[1] == "setup":
        setup_nodejs_interactive()
    else:
        check_nodejs_requirements()