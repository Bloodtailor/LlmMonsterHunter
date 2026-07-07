# Returning Monster Tests - DATABASE ONLY (LLM stubbed, no server)
# Exercises the Mem-M4 layer: the reunion transform's clamped stat boosts,
# persona changes, memory writing, and the deterministic fallback path.
#
# Usage: python -m backend.tests.test_returning   (from project root)
# Uses the dedicated test database (harness.py); creates and removes its own rows.

from backend.tests.harness import build_test_app

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

def main():
    app = build_test_app()

    with app.app_context():
        from backend.models.core import db, create_tables
        from backend.models.monster import Monster
        from backend.models.monster_memory import MonsterMemory
        from backend.models.dungeon_run import DungeonRun
        from backend.game.memory import returning
        from backend.game.memory import manager as memory
        from backend.game.dungeon import manager as dungeon
        import backend.game.utils as game_utils

        print('🧪 RETURNING MONSTER TESTS')
        print('=' * 50)
        create_tables()

        saved_state = dungeon.get_dungeon_state()
        real_build_and_generate = game_utils.build_and_generate
        test_monster = None
        created_run_ids = []

        try:
            test_monster = Monster(
                name='Grudgeling', species='Test Wraith',
                description='A creature that exists only inside the test suite.',
                max_health=100, attack=20, defense=15, speed=10,
                persona={'battle_line': 'You shall not pass this hall!'}
            )
            test_monster.save()

            run = DungeonRun.begin()
            created_run_ids.append(run.id)
            dungeon.save_dungeon_state({
                'in_dungeon': True, 'current_location': {'name': 'Test Hall', 'description': ''},
                'available_paths': {}, 'active_encounter': None,
                'party_conditions': {}, 'party_resources': {}, 'run_journal': {},
                'run_id': run.id, 'seen_monster_ids': [], 'dungeon_log': []
            })

            memory.write_memory(
                test_monster.id, 'was_defeated',
                'Was defeated by the party. Brought down by Testhero with Flame Burst.',
                {'by': 'Testhero', 'with': 'Flame Burst'}
            )

            # ===== Transform with a canned LLM answer =====
            print('\n-- transform (stubbed LLM) --')
            game_utils.build_and_generate = lambda *args, **kwargs: {
                'disposition': 'hostile',
                'greeting': 'You. I remember the fire. I remember falling.',
                'stat_boost': 'notable',
                'battle_line': 'This time, the mountain does not fall!',
                'grudge_note': 'Owes Testhero a fall and intends to collect.',
                'new_ability': 'no',
                'ability_theme': None
            }

            result = returning.transform_returning_monster(test_monster, 'test')
            db.session.refresh(test_monster)

            check('disposition honored', result['disposition'] == 'hostile')
            check('greeting carried through', 'remember' in result['greeting'])
            check('notable boost applied to attack (6%)',
                  test_monster.attack == max(21, round(20 * 1.06)), f'got {test_monster.attack}')
            check('max_health boosted and current topped',
                  test_monster.max_health == round(100 * 1.06)
                  and test_monster.current_health == test_monster.max_health)
            check('battle line reworded',
                  test_monster.persona.get('battle_line') == 'This time, the mountain does not fall!')
            check('grudge note appended',
                  'Owes Testhero a fall' in (test_monster.persona.get('grudges_and_bonds') or [''])[-1])
            returned_rows = [m for m in MonsterMemory.for_monster(test_monster.id) if m.kind == 'returned']
            check('returned memory written with amount_pct',
                  len(returned_rows) == 1 and (returned_rows[0].details or {}).get('amount_pct', 0) > 0)

            # ===== Second return compounds, then the lifetime cap bites =====
            print('\n-- repeat returns: multiplier and lifetime cap --')
            attack_before = test_monster.attack
            returning.transform_returning_monster(test_monster, 'test')
            db.session.refresh(test_monster)
            # return_count now 1 -> notable 6% x 1.25 = 7.5%
            check('second return compounds the boost',
                  test_monster.attack == max(attack_before + 1, round(attack_before * 1.075)),
                  f'got {test_monster.attack}')

            # Exhaust the lifetime cap and confirm boosts stop
            memory.write_memory(test_monster.id, 'growth', 'cap filler',
                                {'stat': 'all_stats', 'amount_pct': 0.50})
            attack_capped = test_monster.attack
            returning.transform_returning_monster(test_monster, 'test')
            db.session.refresh(test_monster)
            check('lifetime cap stops further boosts',
                  test_monster.attack == attack_capped, f'got {test_monster.attack}')

            # ===== Fallback path: LLM fails -> memory-driven disposition =====
            print('\n-- deterministic fallback --')
            def boom(*args, **kwargs):
                raise Exception('LLM unavailable')
            game_utils.build_and_generate = boom

            result = returning.transform_returning_monster(test_monster, 'test')
            check('fallback disposition from was_defeated is hostile',
                  result['disposition'] == 'hostile')
            check('fallback greeting exists', bool(result['greeting']))

            # ===== Eligibility integration =====
            print('\n-- eligibility --')
            check('remembered monster is in the returning pool',
                  test_monster.id in memory.eligible_returning_ids())
            memory.mark_seen([test_monster.id])
            check('staged monster leaves the pool',
                  test_monster.id not in memory.eligible_returning_ids())

        finally:
            print('\n-- cleanup --')
            game_utils.build_and_generate = real_build_and_generate
            try:
                if test_monster:
                    MonsterMemory.query.filter_by(monster_id=test_monster.id).delete()
                    db.session.commit()
                    test_monster.delete()
                for run_id in created_run_ids:
                    run = DungeonRun.get_by_id(run_id)
                    if run:
                        run.delete()
                dungeon.save_dungeon_state(saved_state)
                print('  🧹 test rows removed, dungeon state restored')
            except Exception as e:
                print(f'  ⚠️ cleanup problem: {e}')

        print('\n' + '=' * 50)
        print(f'🎉 {PASSED} passed, {FAILED} failed')
        return FAILED

if __name__ == '__main__':
    raise SystemExit(main())
