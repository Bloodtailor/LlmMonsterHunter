#!/usr/bin/env python3
"""
Database Connection and Creation Module
Handles creating the Monster Hunter database and testing connections
"""

import subprocess
import sys
import os
from pathlib import Path

def load_env_vars():
    """Load database configuration from .env file."""
    env_file = Path(".env")
    if not env_file.exists():
        print("❌ .env file not found")
        return None
    
    env_vars = {}
    try:
        with open(env_file, 'r') as f:
            for line in f:
                line = line.strip()
                if line and not line.startswith('#') and '=' in line:
                    key, value = line.split('=', 1)
                    env_vars[key.strip()] = value.strip()
        
        # Extract database config
        db_config = {
            'host': env_vars.get('DB_HOST', 'localhost'),
            'port': env_vars.get('DB_PORT', '3306'),
            'name': env_vars.get('DB_NAME', 'monster_hunter_game'),
            'user': env_vars.get('DB_USER', 'root'),
            'password': env_vars.get('DB_PASSWORD', '')
        }
        
        print(f"✅ Loaded database config: {db_config['user']}@{db_config['host']}:{db_config['port']}")
        return db_config
        
    except Exception as e:
        print(f"❌ Error loading .env file: {e}")
        return None

def test_mysql_connection(db_config):
    """Test connection to MySQL server (without specific database)."""
    if not db_config:
        return False
    
    try:
        if db_config['password']:
            cmd = [
                "mysql", 
                f"-h{db_config['host']}", 
                f"-P{db_config['port']}", 
                f"-u{db_config['user']}", 
                f"-p{db_config['password']}", 
                "-e", "SELECT 1;"
            ]
        else:
            cmd = [
                "mysql", 
                f"-h{db_config['host']}", 
                f"-P{db_config['port']}", 
                f"-u{db_config['user']}", 
                "-e", "SELECT 1;"
            ]
        
        result = subprocess.run(cmd, capture_output=True, text=True, check=True)
        print("✅ MySQL server connection successful")
        return True
        
    except subprocess.CalledProcessError as e:
        if "Access denied" in e.stderr:
            print("❌ MySQL connection failed: Access denied (check password)")
        elif "Can't connect" in e.stderr:
            print("❌ MySQL connection failed: Cannot connect to server")
        else:
            print(f"❌ MySQL connection failed: {e.stderr}")
        return False
    except Exception as e:
        print(f"❌ MySQL connection error: {e}")
        return False

def check_database_exists(db_config):
    """Check if the Monster Hunter database exists."""
    if not db_config:
        return False
    
    try:
        if db_config['password']:
            cmd = [
                "mysql", 
                f"-h{db_config['host']}", 
                f"-P{db_config['port']}", 
                f"-u{db_config['user']}", 
                f"-p{db_config['password']}", 
                "-e", f"USE {db_config['name']}; SELECT 1;"
            ]
        else:
            cmd = [
                "mysql", 
                f"-h{db_config['host']}", 
                f"-P{db_config['port']}", 
                f"-u{db_config['user']}", 
                "-e", f"USE {db_config['name']}; SELECT 1;"
            ]
        
        result = subprocess.run(cmd, capture_output=True, text=True, check=True)
        print(f"✅ Database '{db_config['name']}' exists and is accessible")
        return True
        
    except subprocess.CalledProcessError as e:
        if "Unknown database" in e.stderr:
            print(f"❌ Database '{db_config['name']}' does not exist")
        else:
            print(f"❌ Database check failed: {e.stderr}")
        return False
    except Exception as e:
        print(f"❌ Database check error: {e}")
        return False

def check_database_connection():
    """Check database connection and existence."""
    print("Checking database connection...")
    
    # Load config
    db_config = load_env_vars()
    if not db_config:
        return False
    
    # Check password is set
    if not db_config['password'] or db_config['password'] == 'your_mysql_password_here':
        print("❌ Database password not set in .env file")
        return False
    
    # Test connection to MySQL server
    if not test_mysql_connection(db_config):
        return False
    
    # Check if database exists
    if not check_database_exists(db_config):
        return False
    
    print("✅ Database connection verified")
    return True

def create_database(db_config):
    """Create the Monster Hunter database."""
    if not db_config:
        return False
    
    try:
        print(f"Creating database '{db_config['name']}'...")
        
        if db_config['password']:
            cmd = [
                "mysql", 
                f"-h{db_config['host']}", 
                f"-P{db_config['port']}", 
                f"-u{db_config['user']}", 
                f"-p{db_config['password']}", 
                "-e", f"CREATE DATABASE IF NOT EXISTS {db_config['name']};"
            ]
        else:
            cmd = [
                "mysql", 
                f"-h{db_config['host']}", 
                f"-P{db_config['port']}", 
                f"-u{db_config['user']}", 
                "-e", f"CREATE DATABASE IF NOT EXISTS {db_config['name']};"
            ]
        
        result = subprocess.run(cmd, capture_output=True, text=True, check=True)
        print(f"✅ Database '{db_config['name']}' created successfully")
        return True
        
    except subprocess.CalledProcessError as e:
        print(f"❌ Database creation failed: {e.stderr}")
        return False
    except Exception as e:
        print(f"❌ Database creation error: {e}")
        return False

def update_env_password(new_password):
    """Update the database password in .env file."""
    env_file = Path(".env")
    if not env_file.exists():
        return False
    
    try:
        with open(env_file, 'r') as f:
            content = f.read()
        
        # Replace the password line
        lines = content.split('\n')
        updated_lines = []
        
        for line in lines:
            if line.startswith('DB_PASSWORD='):
                updated_lines.append(f'DB_PASSWORD={new_password}')
            else:
                updated_lines.append(line)
        
        with open(env_file, 'w') as f:
            f.write('\n'.join(updated_lines))
        
        print("✅ Database password updated in .env file")
        return True
        
    except Exception as e:
        print(f"❌ Failed to update .env file: {e}")
        return False

def setup_database_interactive():
    """Interactive setup for database connection."""
    print("Setting up database connection...")
    
    # Load current config
    db_config = load_env_vars()
    if not db_config:
        print("❌ Cannot load database configuration")
        return False
    
    # Check if password needs to be set
    if not db_config['password'] or db_config['password'] == 'your_mysql_password_here':
        print("\n📋 Database password is not set")
        
        while True:
            password = input("Enter your MySQL root password: ").strip()
            if password:
                # Update config for testing
                db_config['password'] = password
                
                # Test connection
                if test_mysql_connection(db_config):
                    # Update .env file
                    if update_env_password(password):
                        break
                    else:
                        print("❌ Failed to save password. Try again.")
                else:
                    print("❌ Connection failed. Check password and try again.")
            else:
                print("Empty password entered. Please try again.")
    
    # Test connection again
    if not test_mysql_connection(db_config):
        print("❌ Cannot connect to MySQL. Check server and credentials.")
        return False
    
    # Check/create database
    if not check_database_exists(db_config):
        print(f"\n📋 Database '{db_config['name']}' does not exist")
        
        choice = input("Do you want to create it now? (y/n): ").lower().strip()
        if choice in ['y', 'yes']:
            if not create_database(db_config):
                print("❌ Failed to create database")
                print("📋 Try manually:")
                print("1. Open MySQL Workbench")
                print("2. Connect to your server")
                print(f"3. Run: CREATE DATABASE {db_config['name']};")
                return False
        else:
            print("❌ Database setup cancelled")
            return False
    
    # Final verification
    if check_database_exists(db_config):
        print("✅ Database connection and setup completed")
        return True
    else:
        print("❌ Database setup verification failed")
        return False

if __name__ == "__main__":
    if len(sys.argv) > 1 and sys.argv[1] == "setup":
        setup_database_interactive()
    else:
        check_database_connection()