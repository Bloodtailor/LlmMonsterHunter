#!/usr/bin/env python3
"""
MySQL Checks Module
Pure detection logic for MySQL server, CLI, and service status
Returns data instead of printing for clean UX flow
"""

import subprocess
from pathlib import Path

from setup.constants import MYSQL_LOCATIONS, MYSQL_SERVICE_NAMES


def check_mysql_server():
    """
    Check if MySQL server is accessible (primary detection method).
    A plain socket probe: needs no credentials, no driver, and - unlike
    the old `mysql` CLI probe - works even when the MSI installer left
    the CLI off the system PATH (it usually does).
    """
    from setup.checks.database_checks import get_database_config
    from setup.utils.mysql_client import probe_server

    config = get_database_config() or {}
    host = config.get('host', 'localhost')
    port = config.get('port', 3306)

    if probe_server(host, port):
        return True, f"MySQL server is running ({host}:{port})"
    return False, "Cannot connect to MySQL server"


def check_mysql_cli():
    """
    Check if MySQL command line client is available.
    Informational only: the game and setup both speak PyMySQL, so a
    missing CLI never blocks anything - it just helps diagnostics.
    """
    try:
        result = subprocess.run(["mysql", "--version"], capture_output=True, text=True, check=True)
        version_info = result.stdout.strip()
        return True, f"MySQL CLI: {version_info}"
    except FileNotFoundError:
        return False, "MySQL command line client not found in PATH"
    except subprocess.CalledProcessError:
        return False, "MySQL command line client not working"


def check_mysql_service():
    """
    Check MySQL service status (for automation purposes)
    Returns service name if found, useful for starting/stopping
    """
    service_names = MYSQL_SERVICE_NAMES

    for service in service_names:
        try:
            result = subprocess.run(
                ["sc", "query", service], capture_output=True, text=True, check=True
            )
            if "RUNNING" in result.stdout:
                return True, f"MySQL service '{service}' is running"
            elif "STOPPED" in result.stdout:
                return False, f"MySQL service '{service}' is stopped"
        except subprocess.CalledProcessError:
            continue

    return False, "No MySQL service found"


def check_mysql_installations():
    """
    Check if MySQL installations can be found on the system
    Used for diagnostic purposes to distinguish "not installed" vs "installed but broken"
    """
    possible_locations = MYSQL_LOCATIONS

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

    if installations:
        # Show first installation found
        return True, f"MySQL installation found at: {installations[0]}"
    else:
        return False, "No MySQL installations detected"


def check_mysql_service_exists():
    """
    Check if any MySQL service exists on the system (regardless of running state)
    Used for diagnostic purposes to detect installed but non-running MySQL
    """
    service_names = MYSQL_SERVICE_NAMES

    for service in service_names:
        try:
            subprocess.run(["sc", "query", service], capture_output=True, text=True, check=True)
            # If we can query it, the service exists
            return True, f"MySQL service '{service}' exists"
        except subprocess.CalledProcessError:
            continue

    return False, "No MySQL service detected"


def get_mysql_installations_list():
    """
    Helper function to get list of installation paths (for flow logic)
    Returns list of paths for PATH troubleshooting
    """
    possible_locations = MYSQL_LOCATIONS

    installations = []

    for location in possible_locations:
        location_path = Path(location)
        if location_path.exists():
            for bin_dir in location_path.rglob("bin"):
                mysql_exe = bin_dir / "mysql.exe"
                if mysql_exe.exists():
                    installations.append(str(bin_dir))

    return installations


def get_mysql_service_name():
    """
    Helper function to get actual MySQL service name (for installation logic)
    Returns service name string or None
    """
    service_names = MYSQL_SERVICE_NAMES

    for service in service_names:
        try:
            subprocess.run(["sc", "query", service], capture_output=True, text=True, check=True)
            return service
        except subprocess.CalledProcessError:
            continue

    return None


def check_mysql_requirements():
    """Check all MySQL related requirements (for orchestration).

    A running server is the whole requirement: setup and the game both
    connect via PyMySQL, so the CLI's presence/PATH no longer gates
    anything.
    """

    server_ok, _ = check_mysql_server()
    return server_ok


def get_mysql_diagnostic(include_overall=False):
    """
    Get comprehensive MySQL diagnostic information.
    Used by flows to understand what specifically needs to be addressed.

    Args:
        include_overall (bool): Whether to include overall requirement check

    Returns:
        dict: All MySQL check results for detailed analysis
    """
    server_ok, server_msg = check_mysql_server()
    cli_ok, cli_msg = check_mysql_cli()
    service_ok, service_msg = check_mysql_service()
    installations_ok, installations_msg = check_mysql_installations()
    service_exists_ok, service_exists_msg = check_mysql_service_exists()

    result = {
        'mysql_server': (server_ok, server_msg),
        'mysql_cli': (cli_ok, cli_msg),
        'mysql_service': (service_ok, service_msg),
        'mysql_installations': (installations_ok, installations_msg),
        'mysql_service_exists': (service_exists_ok, service_exists_msg),
    }

    if include_overall:
        overall_ok = check_mysql_requirements()
        result['overall'] = (
            overall_ok,
            "All MySQL requirements met" if overall_ok else "Some MySQL requirements missing",
        )

    return result
