# Seed the TEST database's LLM provider settings from the dev database.
#
# WHY this exists: the DeepSeek API key lives ONLY in the game_settings
# row the in-game panel writes (ai/llm/provider_settings.py has no env
# path for DeepSeek), and that row exists only in the dev database. The
# playtest tools run exclusively against the test DB, which starts with
# no settings row and would silently resolve to the local-model floor.
# This script copies the ONE llm_provider row across so real DeepSeek
# generation works headlessly.
#
# The dev database is opened READ-ONLY here - a single SELECT of a
# single row, nothing else read, nothing ever written. The image
# provider row is deliberately NOT copied: a missing image_provider row
# means image generation stays OFF (image_settings.py has no env floor),
# which is exactly what playtesting wants.
#
# Usage: ./venv/Scripts/python.exe tools/playtest/seed_provider.py

import json
import os
import sys
from pathlib import Path

# Run as a plain script from the repo root - put the root on sys.path
# so `import backend` resolves (backend/__init__.py loads .env)
sys.path.insert(0, str(Path(__file__).resolve().parents[2]))

import backend  # noqa: F401 - imports load .env for the DB credentials

SETTINGS_KEY = 'llm_provider'


def read_dev_provider_row():
    """One read-only SELECT of the llm_provider row from the dev DB"""
    import pymysql

    from backend.tests.harness import test_db_name

    dev_database_name = os.getenv('DB_NAME', 'monster_hunter_game')
    if dev_database_name == test_db_name():
        raise SystemExit(
            'DB_NAME and DB_NAME_TEST point at the same database - refusing to continue'
        )

    connection = pymysql.connect(
        host=os.getenv('DB_HOST', 'localhost'),
        port=int(os.getenv('DB_PORT', '3306')),
        user=os.getenv('DB_USER', 'root'),
        password=os.getenv('DB_PASSWORD', ''),
        database=dev_database_name,
    )
    try:
        with connection.cursor() as cursor:
            cursor.execute(
                'SELECT value FROM game_settings WHERE `key` = %s LIMIT 1', (SETTINGS_KEY,)
            )
            row = cursor.fetchone()
    finally:
        connection.close()

    if not row:
        return None
    value = row[0]
    return json.loads(value) if isinstance(value, str) else value


def main() -> int:
    value = read_dev_provider_row()

    if not isinstance(value, dict) or value.get('provider') != 'deepseek':
        print('❌ The dev database has no configured DeepSeek provider row.')
        print('   Open the game, set up DeepSeek in Settings (gear icon), and rerun.')
        return 1

    deepseek = value.get('deepseek') or {}
    if not deepseek.get('api_key') or not deepseek.get('model'):
        print('❌ The dev DeepSeek row is half-configured (missing key or model).')
        return 1

    from backend.tests.harness import build_test_app, test_db_name

    app = build_test_app()
    with app.app_context():
        from backend.models.core import create_tables
        from backend.models.game_setting import GameSetting

        create_tables()
        GameSetting.set(SETTINGS_KEY, value)

    key_last_four = deepseek['api_key'][-4:]
    print(
        f"✅ Seeded '{test_db_name()}' with provider=deepseek "
        f"model={deepseek['model']} key=...{key_last_four}"
    )
    return 0


if __name__ == '__main__':
    raise SystemExit(main())
