"""
MySQL access for setup - via PyMySQL, the same driver the game uses.

WHY this file exists: the old checks shelled out to the `mysql` CLI,
which the MSI installer often leaves OFF the system PATH. That made
"edit your system PATH" a required onboarding step for a tool the game
never uses (the backend talks PyMySQL), and it put the root password
into visible process arguments. Setup now speaks PyMySQL too: a working
server is enough, and credentials stay out of the process list.

Setup may run under system Python while PyMySQL lives in ./venv.
PyMySQL is pure Python, so borrowing the venv's copy is safe - and the
Basic Backend component installs it before any database component runs.
"""

import socket
import sys
from pathlib import Path


def _import_pymysql():
    """Import PyMySQL, borrowing the venv's copy when setup runs under system Python."""
    try:
        import pymysql

        return pymysql
    except ImportError:
        pass

    site_packages = Path("venv") / "Lib" / "site-packages"
    if site_packages.exists() and str(site_packages) not in sys.path:
        sys.path.append(str(site_packages))
        try:
            import pymysql

            return pymysql
        except ImportError:
            pass
    return None


def probe_server(host="localhost", port=3306, timeout=3):
    """Is anything listening on the MySQL port? Needs no credentials, no driver."""
    try:
        with socket.create_connection((host, port), timeout=timeout):
            return True
    except OSError:
        return False


def connect(host, port, user, password, database=None, timeout=10):
    """
    Open a PyMySQL connection.

    Returns:
        tuple: (connection, None) on success, (None, error_message) on failure.
        Error messages keep the "Access denied" / "Cannot connect" /
        "does not exist" phrases the flows branch on.
    """
    pymysql = _import_pymysql()
    if pymysql is None:
        return None, "PyMySQL not installed yet (Basic Backend setup provides it)"

    try:
        connection = pymysql.connect(
            host=host,
            port=port,
            user=user,
            password=password,
            database=database,
            connect_timeout=timeout,
        )
        return connection, None
    except pymysql.err.OperationalError as e:
        code = e.args[0] if e.args else None
        if code == 1045:
            return None, "Access denied (check password)"
        if code == 1049:
            return None, f"Database '{database}' does not exist"
        if code == 2003:
            return None, "Cannot connect to server"
        detail = e.args[1] if len(e.args) > 1 else str(e)
        return None, f"MySQL error {code}: {detail}"
    except Exception as e:
        return None, f"MySQL connection error: {e}"


def run_statement(host, port, user, password, statement, database=None):
    """
    Run one SQL statement and close the connection.

    Returns:
        tuple: (success, error_message_or_None)
    """
    connection, error = connect(host, port, user, password, database=database)
    if connection is None:
        return False, error
    try:
        with connection.cursor() as cursor:
            cursor.execute(statement)
        connection.commit()
        return True, None
    except Exception as e:
        return False, f"MySQL statement failed: {e}"
    finally:
        connection.close()
