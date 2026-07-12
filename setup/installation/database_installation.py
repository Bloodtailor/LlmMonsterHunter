#!/usr/bin/env python3
"""
Database Installation Module
Pure installation logic for database creation and configuration
"""

from setup.checks.database_checks import get_database_config
from setup.utils.env_utils import update_env_config
from setup.utils.mysql_client import run_statement


def create_database():
    """
    Create the Monster Hunter database using configuration from .env file.
    Uses PyMySQL (what the game uses) - works even when the MySQL CLI
    is not on PATH, and keeps the password out of process arguments.
    Returns (success, message) tuple for clean UX handling.
    """
    config = get_database_config()
    if not config:
        return False, "Invalid or missing database configuration in .env file"

    success, error = run_statement(
        config['host'],
        config['port'],
        config['user'],
        config['password'],
        f"CREATE DATABASE IF NOT EXISTS {config['name']};",
    )
    if success:
        return True, f"Database '{config['name']}' created successfully"
    return False, f"Database creation failed: {error}"


def update_database_password(new_password):
    """
    Update the database password in .env file.
    Returns (success, message) tuple for clean UX handling.

    Args:
        new_password (str): New password to set
    """
    if not new_password:
        return False, "Password cannot be empty"

    return update_env_config(DB_PASSWORD=new_password)
