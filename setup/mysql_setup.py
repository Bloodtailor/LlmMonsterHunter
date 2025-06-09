#!/usr/bin/env python3
"""
MySQL Server and CLI Setup Module
Checks for MySQL server and command line client
"""

import socket
import subprocess
import sys
from pathlib import Path

def check_mysql_service():
    """Check if MySQL service exists and is running."""
    service_names = ["MySQL84", "MySQL80", "MySQL", "mysqld"]
    
    for service in service_names:
        try:
            result = subprocess.run(["sc", "query", service], 
                                  capture_output=True, text=True, check=True)
            if "RUNNING" in result.stdout:
                return True, service
            elif "STOPPED" in result.stdout:
                return False, service
        except subprocess.CalledProcessError:
            continue
    
    return False, None

def check_mysql_port():
    """Check if something is listening on MySQL port 3306."""
    try:
        sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        sock.settimeout(2)
        result = sock.connect_ex(('localhost', 3306))
        sock.close()
        
        if result == 0:
            print("✅ MySQL port 3306 is responding")
            return True
        else:
            print("❌ Nothing responding on MySQL port 3306")
            return False
    except Exception:
        print("❌ Cannot test MySQL port 3306")
        return False

def test_mysql_connection():
    """Test MySQL server by attempting connection - most reliable method."""
    try:
        # Try to connect - we expect auth failure, which means server is working
        result = subprocess.run([
            "mysql", "-h", "localhost", "-P", "3306", 
            "-u", "nonexistentuser", "-e", "SELECT 1;"
        ], capture_output=True, text=True, timeout=5)
        
        # If it succeeds somehow, great!
        if result.returncode == 0:
            print("✅ MySQL server connection successful")
            return True
        
        # If it fails with auth error, server is definitely working
        if "Access denied" in result.stderr:
            print("✅ MySQL server is working (authentication required)")
            return True
        
        # Other connection errors indicate server problems
        if any(error in result.stderr for error in [
            "Can't connect", "Connection refused", "Unknown MySQL server host",
            "Lost connection", "No connection could be made"
        ]):
            print("❌ Cannot connect to MySQL server")
            return False
        
        print("⚠️  MySQL server connection unclear")
        return False
        
    except FileNotFoundError:
        print("⚠️  Cannot test connection (mysql command not available)")
        return False
    except subprocess.TimeoutExpired:
        print("⚠️  MySQL connection test timed out")
        return False
    except Exception as e:
        print(f"⚠️  MySQL connection test failed: {e}")
        return False

def check_mysql_process():
    """Check if any MySQL-related process is running."""
    mysql_processes = ["mysqld.exe", "mysql.exe", "mysqld-nt.exe", "mysqld-opt.exe"]
    found_processes = []
    
    try:
        for process in mysql_processes:
            result = subprocess.run(["tasklist", "/FI", f"IMAGENAME eq {process}"], 
                                  capture_output=True, text=True, check=True)
            if process in result.stdout:
                found_processes.append(process)
        
        if found_processes:
            process_list = ", ".join(found_processes)
            print(f"✅ MySQL process(es) running: {process_list}")
            return True
        else:
            print("❌ No MySQL processes found")
            return False
    except subprocess.CalledProcessError:
        print("⚠️  Cannot check MySQL processes")
        return False

def find_mysql_installations():
    """Find MySQL installations by scanning filesystem."""
    possible_locations = [
        "C:\\Program Files\\MySQL",
        "C:\\Program Files (x86)\\MySQL", 
        "C:\\mysql",
        "C:\\xampp\\mysql",
        "C:\\wamp64\\bin\\mysql",
        "C:\\laragon\\bin\\mysql",
        "C:\\AppServ\\MySQL",
        "C:\\Server\\MySQL",
        "D:\\xampp\\mysql",
        "D:\\wamp\\bin\\mysql"
    ]
    
    installations = []
    
    for location in possible_locations:
        location_path = Path(location)
        if location_path.exists():
            # Look for mysql.exe in bin subdirectories
            for bin_dir in location_path.rglob("bin"):
                mysql_exe = bin_dir / "mysql.exe"
                if mysql_exe.exists():
                    installations.append(str(bin_dir))
    
    # Also check if mysql is in PATH
    try:
        result = subprocess.run(["where", "mysql"], capture_output=True, text=True, check=True)
        path_location = result.stdout.strip().split('\n')[0]
        if path_location and path_location not in installations:
            installations.append(str(Path(path_location).parent))
    except subprocess.CalledProcessError:
        pass
    
    return installations

def check_mysql_cli():
    """Check if MySQL command line client is available."""
    try:
        result = subprocess.run(["mysql", "--version"], 
                              capture_output=True, text=True, check=True)
        version_info = result.stdout.strip()
        print(f"✅ MySQL CLI available: {version_info}")
        return True
    except FileNotFoundError:
        print("❌ MySQL command line client not found in PATH")
        return False
    except subprocess.CalledProcessError:
        print("❌ MySQL command line client not working")
        return False

def check_mysql_requirements():
    """Check all MySQL requirements - simplified output."""
    print("Checking MySQL Server and CLI requirements...")
    
    # Quick server check - connection test is most reliable
    connection_works = test_mysql_connection()
    port_responding = check_mysql_port()
    
    # Server is working if connection works OR port responds
    server_working = connection_works or port_responding
    
    # Quick CLI check
    cli_available = check_mysql_cli()
    
    if server_working and cli_available:
        print("✅ MySQL Server and CLI are working")
        return True
    elif server_working:
        print("✅ MySQL Server is working")
        print("❌ MySQL CLI needs to be added to PATH")
        return False
    else:
        print("❌ MySQL Server not responding")
        return False

def find_mysql_installations():
    """Find MySQL installations by scanning common locations."""
    possible_locations = [
        "C:\\Program Files\\MySQL",
        "C:\\Program Files (x86)\\MySQL", 
        "C:\\xampp\\mysql",
        "C:\\wamp64\\bin\\mysql",
        "C:\\laragon\\bin\\mysql"
    ]
    
    installations = []
    
    for location in possible_locations:
        location_path = Path(location)
        if location_path.exists():
            # Look for mysql.exe in bin subdirectories
            for bin_dir in location_path.rglob("bin"):
                mysql_exe = bin_dir / "mysql.exe"
                if mysql_exe.exists():
                    installations.append(str(bin_dir))
    
    return installations

def start_mysql_service():
    """Try to start MySQL service."""
    service_names = ["MySQL84", "MySQL80", "MySQL", "mysqld"]
    
    for service in service_names:
        try:
            print(f"Trying to start {service} service...")
            result = subprocess.run(["net", "start", service], 
                                  capture_output=True, text=True, check=True)
            print(f"✅ {service} service started successfully")
            return True
        except subprocess.CalledProcessError as e:
            if "already been started" in str(e.stderr):
                print(f"✅ {service} service was already running")
                return True
            # Try next service name
            continue
    
    print("❌ Could not start any MySQL service")
    return False

def setup_mysql_interactive():
    """Interactive setup for MySQL - simplified and user-friendly."""
    print("Setting up MySQL...")
    
    # Quick status check
    connection_works = test_mysql_connection()
    port_responding = check_mysql_port()
    cli_available = check_mysql_cli()
    
    server_working = connection_works or port_responding
    
    if server_working and cli_available:
        print("🎉 MySQL is already working perfectly!")
        return True
    
    elif server_working:
        # Server works, just need CLI in PATH
        print("✅ MySQL Server is working")
        print("🔧 Just need to add MySQL CLI to your system PATH")
        
        # Find MySQL installation
        installations = find_mysql_installations()
        
        if installations:
            mysql_path = installations[0]  # Use first found
            print(f"\n💡 Found MySQL at: {mysql_path}")
            
            print(f"\n📋 Add this path to your system PATH:")
            print(f"   {mysql_path}")
            
            print(f"\n📋 Quick steps:")
            print("1. Press Win+R, type 'sysdm.cpl', press Enter")
            print("2. Click 'Environment Variables'")
            print("3. Edit 'Path' in System Variables")
            print("4. Add the path above")
            print("5. Restart command prompt")
            print("6. Test: mysql --version")
            
            print(f"\n✅ After adding to PATH, MySQL will be fully working!")
            return False  # Return False so setup shows this needs to be done
        else:
            print("\n❌ Cannot find MySQL CLI installation")
            print("MySQL Server is working but CLI location unknown")
            return False
    
    else:
        # Server not working
        print("❌ MySQL Server is not responding")
        
        # Check if service exists but not running
        service_running, service_name = check_mysql_service()
        
        if service_name and not service_running:
            print(f"💡 Found MySQL service '{service_name}' but it's stopped")
            
            choice = input("Try starting MySQL service? (y/n): ").lower().strip()
            if choice in ['y', 'yes']:
                if start_mysql_service():
                    print("✅ MySQL service started successfully!")
                    return True
                else:
                    print("❌ Failed to start service")
        
        print("\n📋 Install MySQL Server:")
        print("1. Download: https://dev.mysql.com/downloads/mysql/")
        print("2. Choose 'MySQL Community Server'")
        print("3. Install with default settings")
        print("4. Include MySQL Command Line Client")
        
        return False

if __name__ == "__main__":
    if len(sys.argv) > 1 and sys.argv[1] == "setup":
        setup_mysql_interactive()
    else:
        check_mysql_requirements()