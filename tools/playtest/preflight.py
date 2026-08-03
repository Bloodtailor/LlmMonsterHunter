# Playtest preflight - is the headless generation rig actually live?
#
# Proves the whole real-generation path works before any tool spends
# money on it: test DB reachable, provider row resolves to DeepSeek,
# image generation OFF, and ONE real generation through the gateway
# whose llm_logs row stamps provider='deepseek' with exact token counts
# and fires zero image requests. Run it before any corpus generation or
# agent playtest session; a red preflight means seed_provider.py hasn't
# run (or the key/model went stale).
#
# Usage: ./venv/Scripts/python.exe tools/playtest/preflight.py

import sys
from pathlib import Path

# Run as a plain script from the repo root - put the root on sys.path
# so `import backend` resolves (backend/__init__.py loads .env)
sys.path.insert(0, str(Path(__file__).resolve().parents[2]))

import backend  # noqa: F401 - imports load .env for the DB credentials

PASSED = 0
FAILED = 0


def check(name: str, condition: bool, detail: str = ''):
    global PASSED, FAILED
    if condition:
        PASSED += 1
        print(f"  ✅ {name}")
    else:
        FAILED += 1
        print(f"  ❌ {name}{f' - {detail}' if detail else ''}")


def main() -> int:
    from backend.tests.harness import build_test_app, test_db_name

    print('🧪 PLAYTEST PREFLIGHT')
    print('=' * 50)

    app = build_test_app()

    # The AI queue worker needs the app handle for DB context - this is
    # the one piece of startup.py the headless rig has to repeat
    from backend.ai.queue import get_ai_queue

    queue = get_ai_queue()
    queue.set_flask_app(app)

    with app.app_context():
        from backend.ai.gateway import text_generation_request
        from backend.ai.image.image_settings import is_image_generation_enabled
        from backend.ai.llm.provider_settings import resolve_llm_settings
        from backend.models.core import create_tables
        from backend.models.image_log import ImageLog
        from backend.models.llm_log import LLMLog

        create_tables()
        print(f"\n-- test database: {test_db_name()} --")

        settings = resolve_llm_settings()
        check(
            'provider resolves to deepseek',
            settings['provider'] == 'deepseek',
            f"resolved '{settings['provider']}' - run tools/playtest/seed_provider.py first",
        )
        check('image generation is OFF', not is_image_generation_enabled())

        if settings['provider'] != 'deepseek':
            print('\nSkipping the live probe - no cloud provider to speak to.')
            print(f'\nPASSED: {PASSED}  FAILED: {FAILED}')
            return FAILED

        image_rows_before = ImageLog.query.count()
        llm_rows_before = LLMLog.query.count()

        print(f"\n-- live probe ({settings['model_name']}) --")
        result = text_generation_request(
            prompt='Reply with the single word: ready',
            prompt_type='playtest',
            prompt_name='preflight_probe',
            max_tokens=16,
            temperature=0.0,
        )

        check('the probe generation succeeded', bool(result.get('success')), str(result))
        check('the model answered with text', bool((result.get('text') or '').strip()))

        # The worker thread wrote the tokens in ITS session - end this
        # session's read transaction so the row below shows them (MySQL
        # REPEATABLE READ would otherwise serve the pre-write snapshot
        # and fail the token checks against a perfectly good row)
        from tools.playtest.rig import refresh_session

        refresh_session()

        log_row = LLMLog.get_by_generation_id(result['generation_id'])
        check('an llm_logs row exists for the probe', log_row is not None)
        if log_row:
            check(
                "the row stamps provider='deepseek'",
                log_row.provider == 'deepseek',
                f'stamped {log_row.provider!r}',
            )
            check(
                'exact prompt tokens recorded',
                isinstance(log_row.prompt_tokens, int) and log_row.prompt_tokens > 0,
            )
            check(
                'exact response tokens recorded',
                isinstance(log_row.response_tokens, int) and log_row.response_tokens > 0,
            )

        check('zero image requests fired', ImageLog.query.count() == image_rows_before)

        print('\n-- budget tally --')
        print(f'  llm_logs rows in {test_db_name()}: {llm_rows_before} before, ')
        print(f'  {LLMLog.query.count()} after this probe')

    print('\n' + '=' * 50)
    print(f'PASSED: {PASSED}  FAILED: {FAILED}')
    return FAILED


if __name__ == '__main__':
    raise SystemExit(main())
