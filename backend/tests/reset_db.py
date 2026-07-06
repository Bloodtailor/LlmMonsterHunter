# Dev Database Reset - DROPS AND RECREATES ALL TABLES
# Destroys every monster, ability, log, and workflow record.
# Needed after schema changes because db.create_all() never ALTERs
# existing tables (this project has no migration tooling).
#
# Usage: python -m backend.tests.reset_db   (from the project root)

import os
from flask import Flask

def build_minimal_app():
    """A Flask app with ONLY the database configured - no LLM load,
    no AI queue, no ComfyUI check"""

    # Importing backend loads .env (backend/__init__.py calls load_dotenv)
    from backend.models.core import init_db

    app = Flask(__name__)

    db_user = os.getenv('DB_USER', 'root')
    db_password = os.getenv('DB_PASSWORD', '')
    db_host = os.getenv('DB_HOST', 'localhost')
    db_port = os.getenv('DB_PORT', '3306')
    db_name = os.getenv('DB_NAME', 'monster_hunter_game')

    app.config['SQLALCHEMY_DATABASE_URI'] = f'mysql+pymysql://{db_user}:{db_password}@{db_host}:{db_port}/{db_name}'
    app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

    init_db(app)
    return app

def import_all_models():
    """Every model module, so SQLAlchemy metadata knows every table"""

    from backend.models.monster import Monster
    from backend.models.ability import Ability
    from backend.models.item import Item
    from backend.models.cocatok import CoCaTok
    from backend.models.following_monsters import FollowingMonster
    from backend.models.active_party import ActiveParty
    from backend.models.global_variables import GlobalVariable
    from backend.models.generation_log import GenerationLog
    from backend.models.llm_log import LLMLog
    from backend.models.image_log import ImageLog
    from backend.models.game_workflow import GameWorkflow

def main():
    db_name = os.getenv('DB_NAME', 'monster_hunter_game')
    print('💣 DEV DATABASE RESET')
    print('=' * 50)
    print(f"This will DROP ALL TABLES in '{db_name}' and recreate them empty.")
    print('Every monster, ability, and log will be gone.')

    answer = input("Type 'yes' to continue: ")
    if answer.strip().lower() != 'yes':
        print('Aborted - nothing was changed.')
        return

    app = build_minimal_app()
    from backend.models.core import db

    with app.app_context():
        import_all_models()

        print('Dropping all tables...')
        db.drop_all()

        print('Recreating tables...')
        db.create_all()

        from sqlalchemy import inspect
        table_names = inspect(db.engine).get_table_names()
        print(f'🎉 Reset complete. {len(table_names)} empty tables:')
        for table_name in sorted(table_names):
            print(f'    {table_name}')

if __name__ == '__main__':
    main()
