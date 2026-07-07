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


# Columns that create_all can't add to tables that already exist. When a
# marker is missing from the TEST database, the whole database is dropped
# and rebuilt - it is disposable by contract (suites create their own
# rows). Add a (table, column) pair here whenever a model gains a column.
_SCHEMA_MARKERS = (
    ('monsters', 'affinity'),
    ('llm_logs', 'provider'),
    ('llm_logs', 'prompt_tokens'),
)


def _ensure_database_exists():
    """Create the test database if it's missing, and REBUILD it when its
    schema has drifted behind the models (create_all never ALTERs)"""
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

            if _schema_drifted(cursor):
                print(f"🔁 Test DB schema drifted - rebuilding '{test_db_name()}'")
                cursor.execute(f"DROP DATABASE `{test_db_name()}`")
                cursor.execute(
                    f"CREATE DATABASE `{test_db_name()}` "
                    "CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci"
                )
        connection.commit()
    finally:
        connection.close()


def _schema_drifted(cursor) -> bool:
    """Does any existing test table lack a marker column?"""
    for table, column in _SCHEMA_MARKERS:
        cursor.execute(
            "SELECT COUNT(*) FROM information_schema.tables "
            "WHERE table_schema = %s AND table_name = %s",
            (test_db_name(), table),
        )
        if cursor.fetchone()[0] == 0:
            continue  # table not created yet - create_all will handle it
        cursor.execute(
            "SELECT COUNT(*) FROM information_schema.columns "
            "WHERE table_schema = %s AND table_name = %s AND column_name = %s",
            (test_db_name(), table, column),
        )
        if cursor.fetchone()[0] == 0:
            return True
    return False


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
