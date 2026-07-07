# Memory Foundation Tests - OFFLINE (database only, no LLM, no server)
# Exercises the Mem-M1 layer: dungeon run lifecycle, monster memories,
# the run journal, and returning-monster eligibility.
#
# Usage: python -m backend.tests.test_memory_foundation   (from project root)
# Uses the dedicated test database (harness.py); creates and removes its own
# rows, and restores the dungeon state it found.

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
        from backend.game.battle.constants import BRIMMING, RESOURCE_KEYS, full_resources
        from backend.game.dungeon import manager as dungeon
        from backend.game.memory import journal
        from backend.game.memory import manager as memory
        from backend.models.core import create_tables, db
        from backend.models.dungeon_run import DungeonRun
        from backend.models.following_monsters import FollowingMonster
        from backend.models.monster import Monster
        from backend.models.monster_memory import MonsterMemory

        print('🧪 MEMORY FOUNDATION TESTS')
        print('=' * 50)

        # New tables auto-create without touching existing ones
        success, message = create_tables()
        check('create_tables (new tables auto-create)', success, message)

        saved_state = dungeon.get_dungeon_state()
        created_run_ids = []
        test_monster = None
        was_following = False

        try:
            # ===== DungeonRun lifecycle =====
            print('\n-- DungeonRun lifecycle --')
            first = DungeonRun.begin()
            check('begin() opens a run', first is not None and first.result is None)
            created_run_ids.append(first.id)

            second = DungeonRun.begin()
            created_run_ids.append(second.id)
            db.session.refresh(first)
            check(
                'begin() abandons the dangling active run',
                first.result == 'abandoned' and first.ended_at is not None,
            )
            check('run numbers count up', second.run_number == first.run_number + 1)

            active = DungeonRun.get_active()
            check('get_active() finds the open run', active is not None and active.id == second.id)

            DungeonRun.close('victory_exit', summary='Test run went well.')
            db.session.refresh(second)
            check(
                'close() stamps result and summary',
                second.result == 'victory_exit' and second.summary == 'Test run went well.',
            )
            check('close() with no active run is quiet', DungeonRun.close('defeat') is None)

            # ===== Memories =====
            print('\n-- Monster memories --')
            test_monster = Monster(
                name='Testling',
                species='Test Sprite',
                description='A creature that exists only inside the test suite.',
            )
            test_monster.save()

            third = DungeonRun.begin()  # active run for stamping
            created_run_ids.append(third.id)

            # A dungeon state pointing at the active run (journal needs in_dungeon)
            dungeon.save_dungeon_state(
                {
                    'in_dungeon': True,
                    'current_location': {'name': 'Test Chamber', 'description': ''},
                    'available_paths': {},
                    'active_encounter': None,
                    'party_conditions': {},
                    'party_resources': {},
                    'run_journal': {},
                    'run_id': third.id,
                    'seen_monster_ids': [],
                    'dungeon_log': [],
                }
            )

            memory.write_memory(
                test_monster.id,
                'was_defeated',
                'Brought down by Testhero with a basic attack.',
                details={'by': 'Testhero', 'with': 'a basic attack'},
            )
            rows = MonsterMemory.for_monster(test_monster.id)
            check('write_memory saves a row', len(rows) == 1)
            check(
                'memory is stamped with the active run',
                rows
                and rows[0].run_id == third.id
                and (rows[0].details or {}).get('run_number') == third.run_number,
            )

            lines = memory.get_memory_lines(test_monster.id)
            check(
                'memory lines carry run number and kind',
                lines and lines[0].startswith(f'[run {third.run_number}] was_defeated:'),
            )

            block = memory.build_memory_block(test_monster.id)
            check('memory block is non-empty prompt text', bool(block) and 'was_defeated' in block)
            check(
                'empty-memory block explains itself',
                'never met' in memory.build_memory_block(999999999),
            )

            memory.write_memory(
                test_monster.id,
                'growth',
                'Grew tougher.',
                details={'stat': 'attack', 'amount_pct': 0.05},
            )
            memory.write_memory(
                test_monster.id,
                'returned',
                'Came back stronger.',
                details={'stat': 'attack', 'amount_pct': 0.10},
            )
            total = MonsterMemory.growth_total_pct(test_monster.id, 'attack')
            check(
                'growth_total_pct sums growth + returned rows',
                abs(total - 0.15) < 1e-9,
                f'got {total}',
            )
            check(
                'count_kind counts one kind only',
                MonsterMemory.count_kind(test_monster.id, 'returned') == 1,
            )

            # ===== Journal =====
            print('\n-- Run journal --')
            journal.append_journal(test_monster.id, 'Struck the training dummy.')
            journal.append_journal(test_monster.id, 'Struck the training dummy.')  # duplicate
            check(
                'adjacent duplicate lines are dropped',
                len(journal.get_journal_lines(test_monster.id)) == 1,
            )

            journal.append_journal(test_monster.id, 'x' * 500)
            check(
                'lines are clipped to 160 chars',
                len(journal.get_journal_lines(test_monster.id)[-1]) == journal.JOURNAL_LINE_CLIP,
            )

            for i in range(40):
                journal.append_journal(test_monster.id, f'Moment number {i}.')
            kept = journal.get_journal_lines(test_monster.id)
            check(
                'journal caps at 30 lines, oldest out',
                len(kept) == journal.JOURNAL_MAX_LINES and kept[-1] == 'Moment number 39.',
            )

            journal_block = journal.build_journal_block(test_monster.id)
            check('journal block is non-empty prompt text', 'Moment number 39.' in journal_block)

            # ===== Eligibility =====
            print('\n-- Returning-monster eligibility --')
            eligible = memory.eligible_returning_ids()
            check('remembered non-follower is eligible', test_monster.id in eligible)

            memory.mark_seen([test_monster.id])
            check(
                'seen-this-run monsters are excluded',
                test_monster.id not in memory.eligible_returning_ids(),
            )

            # Reset seen, then exclude via following
            state = dungeon.get_dungeon_state()
            state['seen_monster_ids'] = []
            dungeon.save_dungeon_state(state)
            was_following = FollowingMonster.is_following(test_monster.id)
            FollowingMonster.add_follower(test_monster.id)
            check(
                'following monsters are excluded',
                test_monster.id not in memory.eligible_returning_ids(),
            )

            # ===== Dialogue outcome memories (M3) =====
            print('\n-- dialogue outcome memories --')
            from backend.game.dungeon.outcomes import apply_dialogue_outcome

            state = dungeon.get_dungeon_state()
            state['active_encounter'] = {
                'event': 'monster_dialogue',
                'monster_ids': [test_monster.id],
                'dialogue': [
                    {'speaker': 'The party', 'text': 'We mean you no harm.'},
                    {'speaker': 'Testling', 'text': 'Then pass, strangers.'},
                ],
            }
            dungeon.save_dungeon_state(state)

            before = len(MonsterMemory.for_monster(test_monster.id))
            applied = apply_dialogue_outcome(
                'allow_passage', [test_monster.id], {'name': 'Test Chamber', 'description': ''}
            )
            rows = MonsterMemory.for_monster(test_monster.id)
            new_kinds = [r.kind for r in rows[before:]]
            check(
                'allow_passage writes let_party_pass + talked_with_party',
                'let_party_pass' in new_kinds and 'talked_with_party' in new_kinds,
                f'got {new_kinds}',
            )
            passage = next((r for r in rows[before:] if r.kind == 'let_party_pass'), None)
            check(
                'outcome memory carries the exchange excerpt',
                passage is not None and 'exchange' in (passage.details or {}),
            )
            check(
                'outcome journal line reaches the party journal shape ok', applied['log_note'] != ''
            )
            dungeon.clear_active_encounter()

            # ===== Resource constants =====
            print('\n-- Resource pool seeds --')
            pools = full_resources()
            check(
                'full_resources covers both pools at brimming',
                set(pools.keys()) == set(RESOURCE_KEYS)
                and all(level == BRIMMING for level in pools.values()),
            )

        finally:
            # ===== Cleanup: leave the test DB as we found it =====
            print('\n-- Cleanup --')
            try:
                if test_monster:
                    if not was_following:
                        FollowingMonster.remove_follower(test_monster.id)
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
                print(f'  ⚠️ cleanup problem (test DB may hold test rows): {e}')

        print('\n' + '=' * 50)
        print(f'🎉 {PASSED} passed, {FAILED} failed')
        return FAILED


if __name__ == '__main__':
    raise SystemExit(main())
