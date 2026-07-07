# Test Harness - the shared minimal app for offline suites
# Points at the TEST database (DB_NAME_TEST, default monster_hunter_game_test),
# NEVER the dev database - a crashed suite must not leave debris in real data.
# Creates the database on first use; suites still call create_tables() inside
# their own app context.
#
# reset_db.py intentionally does NOT use this harness - resetting the real
# dev database is its whole job.

import os
from flask import Flask


def test_db_name() -> str:
    return os.getenv('DB_NAME_TEST', 'monster_hunter_game_test')


def _ensure_database_exists():
    """Create the test database if it's missing (idempotent)"""
    import pymysql

    connection = pymysql.connect(
        host=os.getenv('DB_HOST', 'localhost'),
        port=int(os.getenv('DB_PORT', '3306')),
        user=os.getenv('DB_USER', 'root'),
        password=os.getenv('DB_PASSWORD', ''),
    )
    try:
        with connection.cursor() as cursor:
            cursor.execute(
                f"CREATE DATABASE IF NOT EXISTS `{test_db_name()}` "
                "CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci"
            )
        connection.commit()
    finally:
        connection.close()


def build_test_app() -> Flask:
    """Minimal Flask app wired to the test database (no routes, no AI)"""
    from backend.models.core import init_db

    _ensure_database_exists()

    app = Flask(__name__)
    app.config['SQLALCHEMY_DATABASE_URI'] = (
        f"mysql+pymysql://{os.getenv('DB_USER', 'root')}:{os.getenv('DB_PASSWORD', '')}"
        f"@{os.getenv('DB_HOST', 'localhost')}:{os.getenv('DB_PORT', '3306')}"
        f"/{test_db_name()}"
    )
    app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
    init_db(app)
    return app
