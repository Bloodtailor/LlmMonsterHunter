# Point the TEST database's DeepSeek row at a dedicated playtest key,
# so playtest spending tracks separately from the dev key. Touches ONLY
# the test DB; model and context window are kept as-is. Note that
# seed_provider.py COPIES the dev row, so re-running it brings the dev
# key back - run this again afterward to restore the playtest key.
#
# Usage: ./venv/Scripts/python.exe tools/playtest/set_playtest_key.py sk-...

import argparse
import sys
from pathlib import Path

# Run as a plain script from the repo root - put the root on sys.path
# so `import backend` resolves (backend/__init__.py loads .env)
sys.path.insert(0, str(Path(__file__).resolve().parents[2]))

import backend  # noqa: F401 - imports load .env for the DB credentials


def main() -> int:
    parser = argparse.ArgumentParser(description='Set the test DB DeepSeek key')
    parser.add_argument('api_key', help='the dedicated playtest API key')
    args = parser.parse_args()

    key = args.api_key.strip()
    if not key:
        print('❌ Empty key.')
        return 1

    from backend.tests.harness import build_test_app, test_db_name

    app = build_test_app()
    with app.app_context():
        from backend.models.core import create_tables
        from backend.models.game_setting import GameSetting

        create_tables()

        value = GameSetting.get('llm_provider')
        if not isinstance(value, dict) or not (value.get('deepseek') or {}).get('model'):
            print('❌ No seeded llm_provider row - run tools/playtest/seed_provider.py first.')
            return 1

        value['deepseek']['api_key'] = key
        GameSetting.set('llm_provider', value)
        print(
            f"✅ '{test_db_name()}' now uses key=...{key[-4:]} "
            f"(model={value['deepseek']['model']} unchanged)"
        )
    return 0


if __name__ == '__main__':
    raise SystemExit(main())
