# Growth Tests - DATABASE ONLY (LLM stubbed, no server)
# Exercises the Mem-M5 layer: tier math, lifetime caps, the reword length
# rule, ability-count cap, spotlight fallback, and the defeat lesson.
#
# Usage: python -m backend.tests.test_growth   (from project root)
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
        import backend.game.monster.generator as monster_generator
        import backend.game.utils as game_utils
        from backend.game.dungeon import manager as dungeon
        from backend.game.memory import growth, journal
        from backend.game.memory import manager as memory
        from backend.models.ability import Ability
        from backend.models.core import create_tables, db
        from backend.models.monster import Monster
        from backend.models.monster_memory import MonsterMemory

        print('🧪 GROWTH TESTS')
        print('=' * 50)
        create_tables()

        saved_state = dungeon.get_dungeon_state()
        real_build_and_generate = game_utils.build_and_generate
        real_generate_ability = monster_generator.generate_ability
        test_monster = None

        try:
            test_monster = Monster(
                name='Sproutling',
                species='Test Fern',
                description='A creature that exists only inside the test suite.',
                max_health=100,
                attack=20,
                defense=15,
                speed=10,
            )
            test_monster.save()
            old_description = 'Hardens its fronds into a broad green shield that soaks up blows meant for others nearby.'
            shield = Ability(
                monster_id=test_monster.id,
                name='Frond Shield',
                description=old_description,
                ability_type='defense',
            )
            shield.save()

            dungeon.save_dungeon_state(
                {
                    'in_dungeon': True,
                    'current_location': {'name': 'Test Glade', 'description': ''},
                    'available_paths': {},
                    'active_encounter': None,
                    'party_conditions': {},
                    'party_resources': {},
                    'run_journal': {},
                    'run_id': None,
                    'seen_monster_ids': [],
                    'dungeon_log': [],
                }
            )

            # ===== stat tiers =====
            print('\n-- stat tier math --')
            applied = growth.apply_growth(
                test_monster,
                {
                    'reflection': 'It held the line.',
                    'stat': 'attack',
                    'tier': 'slight',
                    'new_ability': 'no',
                    'memory_note': 'Held the line at the glade.',
                },
            )
            db.session.refresh(test_monster)
            check(
                'slight attack: min +1 beats 2% rounding',
                test_monster.attack == 21,
                f'got {test_monster.attack}',
            )
            check('applied summary names the stat', applied['stat'] == 'attack')

            growth.apply_growth(
                test_monster,
                {
                    'reflection': 'It endured.',
                    'stat': 'health',
                    'tier': 'notable',
                    'new_ability': 'no',
                    'memory_note': 'Endured.',
                },
            )
            db.session.refresh(test_monster)
            check(
                'notable health: 5% and current topped',
                test_monster.max_health == 105 and test_monster.current_health == 105,
                f'got {test_monster.max_health}/{test_monster.current_health}',
            )

            # ===== lifetime cap =====
            print('\n-- lifetime growth cap --')
            MonsterMemory.add(
                test_monster.id, 'growth', 'cap filler', {'stat': 'defense', 'amount_pct': 0.28}
            )
            defense_before = test_monster.defense
            applied = growth.apply_growth(
                test_monster,
                {
                    'reflection': 'It braced.',
                    'stat': 'defense',
                    'tier': 'notable',
                    'new_ability': 'no',
                    'memory_note': 'Braced.',
                },
            )
            db.session.refresh(test_monster)
            check(
                'growth past the 30% lifetime cap is skipped',
                test_monster.defense == defense_before and applied['stat'] is None,
                f'got {test_monster.defense}',
            )

            # ===== rewording rules =====
            print('\n-- reword length rule --')
            ok_description = old_description[: len(old_description) - 5] + ' now.'
            growth.apply_growth(
                test_monster,
                {
                    'reflection': 'Its shield is truer now.',
                    'stat': 'none',
                    'tier': 'none',
                    'new_ability': 'no',
                    'reword_ability': 'frond shield',
                    'reworded_description': ok_description,
                    'memory_note': 'Its words matched its deeds.',
                },
            )
            db.session.refresh(shield)
            check(
                'similar-length reword accepted (case-insensitive name match)',
                shield.description == ok_description,
            )

            too_long = old_description + ' ' + 'x' * len(old_description)
            growth.apply_growth(
                test_monster,
                {
                    'reflection': 'It reaches too far.',
                    'stat': 'none',
                    'tier': 'none',
                    'new_ability': 'no',
                    'reword_ability': 'Frond Shield',
                    'reworded_description': too_long,
                    'memory_note': 'note',
                },
            )
            db.session.refresh(shield)
            check('overlong reword rejected', shield.description == ok_description)

            # ===== ability creation: stub + cap =====
            print('\n-- new ability rules --')
            calls = []

            def fake_generate_ability(monster, growth_context=''):
                calls.append(growth_context)
                ability = Ability(
                    monster_id=monster.id,
                    name=f'Grown {len(calls)}',
                    description='Test-grown.',
                    ability_type='support',
                )
                ability.save()
                return ability

            monster_generator.generate_ability = fake_generate_ability

            growth.apply_growth(
                test_monster,
                {
                    'reflection': 'It kept wishing to shield the others.',
                    'stat': 'none',
                    'tier': 'none',
                    'new_ability': 'yes',
                    'ability_theme': 'a ward that answers its repeated wish to protect',
                    'memory_note': 'Learned to protect.',
                },
            )
            check(
                'justified ability generated with the theme in context',
                len(calls) == 1 and 'repeated wish to protect' in calls[0],
            )

            for i in range(5):
                extra = Ability(
                    monster_id=test_monster.id,
                    name=f'Filler {i}',
                    description='filler',
                    ability_type='utility',
                )
                extra.save()
            db.session.refresh(test_monster)
            growth.apply_growth(
                test_monster,
                {
                    'reflection': 'Enough is enough.',
                    'stat': 'none',
                    'tier': 'none',
                    'new_ability': 'yes',
                    'ability_theme': 'one trick too many',
                    'memory_note': 'note',
                },
            )
            check('ability cap (6) stops further learning', len(calls) == 1, f'{len(calls)} calls')

            growth_rows = [
                m for m in MonsterMemory.for_monster(test_monster.id) if m.kind == 'growth'
            ]
            check('growth memories written along the way', len(growth_rows) >= 4)

            # ===== spotlight fallback =====
            print('\n-- spotlight fallback --')
            journal.append_journal(test_monster.id, 'Did a great deed.')
            quiet = [
                Monster(name=f'Quiet{i}', species='Test Moss', description='Background member.')
                for i in range(3)
            ]
            for q in quiet:
                q.save()

            def boom(*args, **kwargs):
                raise Exception('LLM unavailable')

            game_utils.build_and_generate = boom

            picked = growth.pick_spotlight([test_monster] + quiet, 'test')
            check(
                'fallback spotlights the fullest journal',
                len(picked) == 1 and picked[0].id == test_monster.id,
            )

            # ===== defeat lesson =====
            print('\n-- defeat lesson --')
            game_utils.build_and_generate = lambda *a, **k: {
                'reflection': 'They learned to guard the healer.',
                'memory_note': 'Lost the glade because no one guarded the healer.',
            }
            text = growth.run_defeat_reflection(
                [test_monster] + quiet, {'recent_log': ['Turn 1: it went badly.']}, 'test'
            )
            check('defeat reflection text returned', text == 'They learned to guard the healer.')
            lesson_rows = [m for m in MonsterMemory.for_monster(quiet[0].id) if m.kind == 'lesson']
            check('shared lesson written to every member', len(lesson_rows) == 1)

            for q in quiet:
                MonsterMemory.query.filter_by(monster_id=q.id).delete()
                db.session.commit()
                q.delete()

        finally:
            print('\n-- cleanup --')
            game_utils.build_and_generate = real_build_and_generate
            monster_generator.generate_ability = real_generate_ability
            try:
                if test_monster:
                    MonsterMemory.query.filter_by(monster_id=test_monster.id).delete()
                    db.session.commit()
                    test_monster.delete()  # abilities cascade
                dungeon.save_dungeon_state(saved_state)
                print('  🧹 test rows removed, dungeon state restored')
            except Exception as e:
                print(f'  ⚠️ cleanup problem: {e}')

        print('\n' + '=' * 50)
        print(f'🎉 {PASSED} passed, {FAILED} failed')
        return FAILED


if __name__ == '__main__':
    raise SystemExit(main())
