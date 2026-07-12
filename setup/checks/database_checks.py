#!/usr/bin/env python3
"""
Database Checks Module
Pure detection logic for database configuration and connectivity
Returns data instead of printing for clean UX flow
"""

from setup.utils.env_utils import load_env_config


def check_env_database_config():
    """
    Check if database configuration exists and is valid in .env file.
    Does not test connectivity, just validates config format.
    """
    env_vars = load_env_config()

    if not env_vars:
        return False, ".env file not found or unreadable"

    # Required database configuration keys
    required_keys = ['DB_HOST', 'DB_PORT', 'DB_NAME', 'DB_USER', 'DB_PASSWORD']
    missing_keys = [key for key in required_keys if key not in env_vars]

    if missing_keys:
        missing_str = ', '.join(missing_keys)
        return False, f"Missing database config: {missing_str}"

    # Check if password is set (not default placeholder)
    password = env_vars.get('DB_PASSWORD', '')
    if not password or password == 'your_mysql_password_here':
        return False, "Database password not set in .env file"

    # Basic port format validation
    try:
        port = int(env_vars.get('DB_PORT', '3306'))
    except ValueError:
        return False, f"Database port must be a number: {env_vars.get('DB_PORT')}"

    # Return success with configuration summary
    host = env_vars.get('DB_HOST', 'localhost')
    user = env_vars.get('DB_USER', 'root')
    db_name = env_vars.get('DB_NAME', 'monster_hunter_game')

    return True, f"Database config: {user}@{host}:{port}/{db_name}"


def get_database_config():
    """
    Helper function to get database configuration from .env file.
    Used by other functions that need the config.

    Returns:
        dict or None: Database configuration or None if env file unreadable
    """
    env_vars = load_env_config()

    if not env_vars:
        return None

    try:
        return {
            'host': env_vars.get('DB_HOST', 'localhost'),
            'port': int(env_vars.get('DB_PORT', '3306')),
            'name': env_vars.get('DB_NAME', 'monster_hunter_game'),
            'user': env_vars.get('DB_USER', 'root'),
            'password': env_vars.get('DB_PASSWORD', ''),
        }
    except ValueError:
        return None


def check_mysql_server_connection():
    """
    Test connection to MySQL server using .env configuration.
    Tests server connectivity without checking specific database.
    Uses PyMySQL (what the game uses) - no CLI, no password in the
    process list.
    """
    from setup.utils.mysql_client import connect

    config = get_database_config()
    if not config:
        return False, "Invalid or missing database configuration"

    connection, error = connect(
        config['host'], config['port'], config['user'], config['password']
    )
    if connection is None:
        return False, f"MySQL connection failed: {error}"

    connection.close()
    return True, "MySQL server connection successful"


def check_database_exists():
    """
    Check if the configured database exists and is accessible.
    """
    from setup.utils.mysql_client import connect

    config = get_database_config()
    if not config:
        return False, "Invalid or missing database configuration"

    connection, error = connect(
        config['host'], config['port'], config['user'], config['password'],
        database=config['name'],
    )
    if connection is None:
        if "does not exist" in (error or ""):
            return False, f"Database '{config['name']}' does not exist"
        return False, f"Database check failed: {error}"

    connection.close()
    return True, f"Database '{config['name']}' exists and is accessible"


def check_database_requirements():
    """Check all database related requirements (for orchestration)."""

    config_ok, _ = check_env_database_config()
    server_ok, _ = check_mysql_server_connection()
    database_ok, _ = check_database_exists()

    return config_ok and server_ok and database_ok


def get_database_diagnostic(include_overall=False):
    """
    Get comprehensive database diagnostic information.
    Used by flows to understand what specifically needs to be addressed.

    Args:
        include_overall (bool): Whether to include overall requirement check

    Returns:
        dict: All database check results for detailed analysis
    """
    config_ok, config_msg = check_env_database_config()
    connection_ok, connection_msg = check_mysql_server_connection()
    database_ok, database_msg = check_database_exists()

    result = {
        "Database Configuration": (config_ok, config_msg),
        "MySQL Connection": (connection_ok, connection_msg),
        "Game Database": (database_ok, database_msg),
    }

    if include_overall:
        overall_ok = check_database_requirements()
        result["overall"] = (
            overall_ok,
            "All database requirements met" if overall_ok else "Some database requirements missing",
        )

    return result
