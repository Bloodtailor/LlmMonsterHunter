# Dev Database Column Add - image_logs.params + image_logs.model_name
# (Cloud Generation M2)
# db.create_all() never ALTERs existing tables and this project has no
# migration tooling, so this one-off script adds the image-seam
# observability columns to the DEV database without touching any data
# (the add_provider_log_columns.py precedent). Idempotent - safe to run
# any number of times. The TEST database heals itself via harness.py's
# _SCHEMA_MARKERS; this script is only for the dev world.
#
# What it does:
#   1. ALTER TABLE image_logs ADD COLUMN params JSON NULL
#   2. ALTER TABLE image_logs ADD COLUMN model_name VARCHAR(200) NULL
#   (each skipped if the column already exists; no backfill - NULL reads
#    as "logged before the Gemini seam existed", which is the truth)
#
# Usage: python -m backend.tests.add_image_log_columns   (from project root)

import os

from flask import Flask


def build_minimal_app():
    """A Flask app with ONLY the database configured - no LLM load,
    no AI queue (reset_db.py pattern)"""

    from backend.models.core import init_db

    app = Flask(__name__)

    db_user = os.getenv('DB_USER', 'root')
    db_password = os.getenv('DB_PASSWORD', '')
    db_host = os.getenv('DB_HOST', 'localhost')
    db_port = os.getenv('DB_PORT', '3306')
    db_name = os.getenv('DB_NAME', 'monster_hunter_game')

    app.config['SQLALCHEMY_DATABASE_URI'] = (
        f'mysql+pymysql://{db_user}:{db_password}@{db_host}:{db_port}/{db_name}'
    )
    app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

    init_db(app)
    return app


def column_exists(db, table: str, column: str) -> bool:
    from sqlalchemy import inspect

    return any(col['name'] == column for col in inspect(db.engine).get_columns(table))


def add_column(db, table: str, column: str, definition: str):
    from sqlalchemy import text

    if column_exists(db, table, column):
        print(f'Column {table}.{column} already exists - nothing to add.')
        return

    db.session.execute(text(f'ALTER TABLE {table} ADD COLUMN {column} {definition}'))
    db.session.commit()
    print(f'Added column {table}.{column} ({definition}).')


def main():
    db_name = os.getenv('DB_NAME', 'monster_hunter_game')
    print('🖼️ IMAGE LOG COLUMNS ADD')
    print('=' * 50)
    print(f"Database: '{db_name}' - adds image_logs.params and image_logs.model_name.")

    app = build_minimal_app()
    from backend.models.core import db

    with app.app_context():
        add_column(db, 'image_logs', 'params', 'JSON NULL')
        add_column(db, 'image_logs', 'model_name', 'VARCHAR(200) NULL')

        print('🎉 Done.')


if __name__ == '__main__':
    main()
