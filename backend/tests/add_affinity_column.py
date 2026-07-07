# Dev Database Column Add - monsters.affinity (Game Loop M5)
# db.create_all() never ALTERs existing tables and this project has no
# migration tooling, so this one-off script adds the affinity column to
# the DEV database without touching any data (reset_db.py remains the
# nuclear option). Idempotent - safe to run any number of times.
#
# What it does:
#   1. ALTER TABLE monsters ADD COLUMN affinity VARCHAR(20) NULL
#      (skipped if the column already exists)
#   2. Backfill: current FOLLOWERS become 'trusting' (they have been
#      around - nobody in the sanctuary turns disobedient), everyone
#      else stays NULL (reads as 'wary' - meaningless until they join)
#
# Usage: python -m backend.tests.add_affinity_column   (from project root)

import os

from flask import Flask


def build_minimal_app():
    """A Flask app with ONLY the database configured - no LLM load,
    no AI queue, no image-provider check (reset_db.py pattern)"""

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


def main():
    db_name = os.getenv('DB_NAME', 'monster_hunter_game')
    print('🤝 AFFINITY COLUMN ADD')
    print('=' * 50)
    print(f"Database: '{db_name}' - adds monsters.affinity, touches nothing else.")

    app = build_minimal_app()
    from backend.models.core import db

    with app.app_context():
        from sqlalchemy import text

        # 1. The column itself (idempotent)
        if column_exists(db, 'monsters', 'affinity'):
            print('Column monsters.affinity already exists - nothing to add.')
        else:
            db.session.execute(text('ALTER TABLE monsters ADD COLUMN affinity VARCHAR(20) NULL'))
            db.session.commit()
            print('Added column monsters.affinity (VARCHAR(20), NULL).')

        # 2. Backfill: existing followers have earned their trust
        result = db.session.execute(
            text(
                'UPDATE monsters SET affinity = :tier '
                'WHERE affinity IS NULL AND id IN (SELECT monster_id FROM following_monsters)'
            ),
            {'tier': 'trusting'},
        )
        db.session.commit()
        print(f'Backfilled {result.rowcount} follower(s) to trusting.')

        print('🎉 Done.')


if __name__ == '__main__':
    main()
