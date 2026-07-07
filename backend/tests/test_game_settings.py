# Game Settings Tests - OFFLINE (no LLM, test DB)
# Exercises Set-M1 (docs/plans/game-settings.md): the game_settings
# key-value store, the provider resolver's unbreakable local/env floor
# (missing row/table/app-context must resolve to pre-initiative behavior),
# the service's write-only API key masking + validation rules, and the
# locked decision that settings SURVIVE the New Game wipe.
#
# Usage: python -m backend.tests.test_game_settings   (from project root)

import os

from backend.tests.harness import build_test_app

PASSED = 0
FAILED = 0

TEST_API_KEY = 'sk-test-000000abcd1234'


def check(name: str, condition: bool, detail: str = ''):
    global PASSED, FAILED
    if condition:
        PASSED += 1
        print(f"  ✅ {name}")
    else:
        FAILED += 1
        print(f"  ❌ {name}{f' - {detail}' if detail else ''}")


def set_env(key: str, value):
    """Set/unset an env var, returning the original for restore"""
    original = os.environ.get(key)
    if value is None:
        os.environ.pop(key, None)
    else:
        os.environ[key] = value
    return original


def main():
    from backend.ai.llm.provider_settings import (
        DEEPSEEK_KNOWN_CONTEXT_WINDOWS,
        PROVIDER_DEEPSEEK,
        PROVIDER_LOCAL,
        SETTINGS_KEY,
        resolve_llm_settings,
        should_apply_nothink_prefill,
    )

    print('🧪 GAME SETTINGS TESTS')
    print('=' * 50)

    # ===== the floor holds with no app context at all =====
    print('\n-- the unbreakable floor --')
    settings = resolve_llm_settings()
    check(
        'no app context resolves to the local floor',
        settings['provider'] == PROVIDER_LOCAL,
        str(settings),
    )

    app = build_test_app()

    with app.app_context():
        from backend.models.core import create_tables
        from backend.models.game_setting import GameSetting
        from backend.services import settings_service

        create_tables()

        original_context_size = set_env('LLM_CONTEXT_SIZE', '4096')
        original_disable_thinking = os.environ.get('LLM_DISABLE_THINKING')

        try:
            GameSetting.delete_key(SETTINGS_KEY)  # a clean slate

            # ===== the store =====
            print('\n-- the game_settings store --')
            check('missing key returns the default', GameSetting.get('nope', 42) == 42)
            GameSetting.set(SETTINGS_KEY, {'provider': 'local'})
            check(
                'a set value reads back',
                GameSetting.get(SETTINGS_KEY) == {'provider': 'local'},
            )
            GameSetting.set(SETTINGS_KEY, {'provider': 'deepseek'})
            check(
                'a second set updates in place',
                GameSetting.get(SETTINGS_KEY) == {'provider': 'deepseek'}
                and GameSetting.query.filter_by(key=SETTINGS_KEY).count() == 1,
            )
            GameSetting.delete_key(SETTINGS_KEY)

            # ===== the resolver =====
            print('\n-- the resolver --')
            settings = resolve_llm_settings()
            check('no row resolves local', settings['provider'] == PROVIDER_LOCAL)
            check(
                'local context size comes from env',
                settings['context_size'] == 4096,
                str(settings['context_size']),
            )

            GameSetting.set(
                SETTINGS_KEY,
                {'provider': 'deepseek', 'deepseek': {'api_key': TEST_API_KEY}},
            )
            settings = resolve_llm_settings()
            check(
                'a half-configured row (no model) still resolves local',
                settings['provider'] == PROVIDER_LOCAL,
            )

            GameSetting.set(
                SETTINGS_KEY,
                {
                    'provider': 'deepseek',
                    'deepseek': {
                        'api_key': TEST_API_KEY,
                        'model': 'deepseek-v4-flash',
                        'context_window': 65536,
                    },
                },
            )
            settings = resolve_llm_settings()
            check('a complete row resolves deepseek', settings['provider'] == PROVIDER_DEEPSEEK)
            check('the model becomes the model name', settings['model_name'] == 'deepseek-v4-flash')
            check('the stored window wins', settings['context_size'] == 65536)

            GameSetting.set(
                SETTINGS_KEY,
                {
                    'provider': 'deepseek',
                    'deepseek': {'api_key': TEST_API_KEY, 'model': 'deepseek-v4-flash'},
                },
            )
            settings = resolve_llm_settings()
            check(
                'a missing window falls back to the known-models map',
                settings['context_size'] == DEEPSEEK_KNOWN_CONTEXT_WINDOWS['deepseek-v4-flash'],
                str(settings['context_size']),
            )

            GameSetting.set(
                SETTINGS_KEY,
                {
                    'provider': 'deepseek',
                    'deepseek': {'api_key': TEST_API_KEY, 'model': 'deepseek-v9-someday'},
                },
            )
            settings = resolve_llm_settings()
            check(
                'an unknown model with no window falls back to the env floor',
                settings['context_size'] == 4096,
                str(settings['context_size']),
            )

            # ===== the prefill decision =====
            print('\n-- the nothink prefill decision --')
            set_env('LLM_DISABLE_THINKING', 'true')
            check('local + disable-thinking prefills', should_apply_nothink_prefill('local'))
            check(
                'deepseek NEVER prefills (thinking is a request param there)',
                not should_apply_nothink_prefill('deepseek'),
            )
            set_env('LLM_DISABLE_THINKING', 'false')
            check(
                'local without disable-thinking does not prefill',
                not should_apply_nothink_prefill('local'),
            )

            # ===== the service: masked reads =====
            print('\n-- the service: masking --')
            GameSetting.set(
                SETTINGS_KEY,
                {
                    'provider': 'deepseek',
                    'deepseek': {
                        'api_key': TEST_API_KEY,
                        'model': 'deepseek-v4-flash',
                        'context_window': 65536,
                    },
                },
            )
            result = settings_service.get_llm_settings()
            check('the read succeeds', result.get('success') is True, str(result))
            check(
                'the read knows a key exists',
                result['deepseek']['has_api_key'] is True
                and result['deepseek']['api_key_last4'] == TEST_API_KEY[-4:],
            )
            check(
                'the key itself NEVER leaves the service',
                TEST_API_KEY not in str(result),
            )
            check(
                'the known-models map ships to the panel',
                result['known_models'].get('deepseek-v4-flash') is not None,
            )

            # ===== the service: validation =====
            print('\n-- the service: validation --')
            GameSetting.delete_key(SETTINGS_KEY)

            result = settings_service.update_llm_settings({'provider': 'openai'})
            check('an unknown provider is refused', result['success'] is False)

            result = settings_service.update_llm_settings(
                {'provider': 'deepseek', 'deepseek': {'model': 'deepseek-v4-flash'}}
            )
            check('switching to deepseek without a key is refused', result['success'] is False)

            result = settings_service.update_llm_settings(
                {'provider': 'deepseek', 'deepseek': {'api_key': TEST_API_KEY}}
            )
            check('switching to deepseek without a model is refused', result['success'] is False)

            result = settings_service.update_llm_settings(
                {
                    'provider': 'deepseek',
                    'deepseek': {'api_key': TEST_API_KEY, 'model': 'deepseek-v9-someday'},
                }
            )
            check(
                'an unknown model with no window is refused',
                result['success'] is False,
            )

            result = settings_service.update_llm_settings(
                {
                    'provider': 'deepseek',
                    'deepseek': {
                        'api_key': TEST_API_KEY,
                        'model': 'deepseek-v4-flash',
                        'context_window': 512,
                    },
                }
            )
            check('a starving-small window is refused', result['success'] is False)

            result = settings_service.update_llm_settings(
                {
                    'provider': 'deepseek',
                    'deepseek': {
                        'api_key': TEST_API_KEY,
                        'model': 'deepseek-v4-flash',
                        'context_window': 'lots',
                    },
                }
            )
            check('a non-numeric window is refused', result['success'] is False)

            result = settings_service.update_llm_settings(
                {
                    'provider': 'deepseek',
                    'deepseek': {'api_key': TEST_API_KEY, 'model': 'deepseek-v4-flash'},
                }
            )
            check(
                'a known model auto-fills its window',
                result.get('success') is True
                and (GameSetting.get(SETTINGS_KEY)['deepseek']['context_window'])
                == DEEPSEEK_KNOWN_CONTEXT_WINDOWS['deepseek-v4-flash'],
                str(result),
            )

            result = settings_service.update_llm_settings(
                {
                    'provider': 'deepseek',
                    'deepseek': {'api_key': '', 'model': 'deepseek-v4-flash'},
                }
            )
            check(
                'a blank key on save keeps the stored key',
                result.get('success') is True
                and GameSetting.get(SETTINGS_KEY)['deepseek']['api_key'] == TEST_API_KEY,
            )

            result = settings_service.update_llm_settings({'provider': 'local'})
            saved = GameSetting.get(SETTINGS_KEY)
            check(
                'switching back to local keeps the deepseek config for later',
                result.get('success') is True
                and saved['provider'] == 'local'
                and saved['deepseek']['api_key'] == TEST_API_KEY,
                str(saved),
            )
            settings = resolve_llm_settings()
            check(
                'and generation follows the switch immediately',
                settings['provider'] == PROVIDER_LOCAL,
            )

            # ===== survival: the New Game wipe =====
            print('\n-- surviving the wipe --')
            from backend.game.state.new_game import wipe_world

            deleted = wipe_world()
            check(
                'the wipe never touches game_settings',
                'game_settings' not in deleted,
                str(sorted(deleted)),
            )
            saved = GameSetting.get(SETTINGS_KEY)
            check(
                'settings outlive the wiped world',
                bool(saved) and saved['deepseek']['api_key'] == TEST_API_KEY,
            )

        finally:
            GameSetting.delete_key(SETTINGS_KEY)
            set_env('LLM_CONTEXT_SIZE', original_context_size)
            set_env('LLM_DISABLE_THINKING', original_disable_thinking)

    print('\n' + '=' * 50)
    print(f'PASSED: {PASSED}  FAILED: {FAILED}')
    return FAILED


if __name__ == '__main__':
    raise SystemExit(main())
