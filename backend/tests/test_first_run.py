# First Run Tests - OFFLINE (no LLM, test DB)
# Exercises Game Loop M6: the guided first run's scripted event sequence
# (dialogue -> battle -> forced exit), the fixed goal completing on
# recruitment, the empty-party auto-join, the winnable-dialogue hint, and
# the first_run_complete flag flow.
#
# Usage: python -m backend.tests.test_first_run   (from project root)

import copy

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
        from backend.game.dungeon import events, first_run, run_context
        from backend.game.dungeon import goal as goal_module
        from backend.game.dungeon import manager as dungeon
        from backend.game.state import manager as state_manager
        from backend.models.core import create_tables
        from backend.models.following_monsters import FollowingMonster
        from backend.models.global_variables import GlobalVariable
        from backend.models.monster import Monster
        from backend.models.monster_memory import MonsterMemory

        print('🧪 FIRST RUN TESTS')
        print('=' * 50)
        create_tables()

        saved_dungeon_state = dungeon.get_dungeon_state()
        saved_flag = GlobalVariable.get(state_manager.FIRST_RUN_COMPLETE_KEY, None)
        created = []

        try:
            # ===== the guided context =====
            print('\n-- first-run context --')
            state_manager.reset_game_state()  # clean party/following/globals
            first_run.begin_first_run_context()

            check('first run is active', first_run.is_first_run())
            check(
                'the danger is calm',
                run_context.active_danger() == 'calm',
            )
            check(
                'the fixed theme rides the brief',
                'welcoming upper halls' in run_context.expedition_brief(),
            )
            snapshot = goal_module.goal_snapshot()
            check(
                'the fixed goal is set and pending',
                snapshot and snapshot['status'] == 'pending' and 'companion' in snapshot['text'],
            )
            check(
                'the winnable-dialogue hint is active',
                'VERY FIRST encounter' in first_run.dialogue_hint(),
            )

            # ===== the scripted sequence =====
            print('\n-- scripted event sequence --')
            check(
                'beat 1: every path carries the dialogue',
                events.assign_random_event(include_returning=True) == 'monster_dialogue',
            )
            check('no exit while the script runs', events.roll_include_exit() is False)

            first_run.advance_scripted_event()
            check(
                'beat 2: every path carries the battle',
                events.assign_random_event() == 'monster_battle',
            )

            first_run.advance_scripted_event()
            check('the spent script forces the exit', events.roll_include_exit() is True)
            rolled = events.assign_random_event()
            check(
                'after the script, events roll normally',
                rolled in set(events.EVENT_WEIGHTS),
                f'rolled {rolled}',
            )

            # ===== recruitment: auto-party + goal completion =====
            print('\n-- the first companion --')
            first_run.begin_first_run_context()  # fresh script + goal

            # An in-dungeon state so goal logging works
            run_state = copy.deepcopy(dungeon._EMPTY_STATE)
            run_state.update({'in_dungeon': True, 'dungeon_log': []})
            dungeon.save_dungeon_state(run_state)

            companion = Monster(
                name='First Friend',
                species='Test Species',
                description='The first companion, existing only in this suite.',
                max_health=50,
                attack=10,
                defense=10,
                speed=10,
            )
            companion.save()
            created.append(companion)
            FollowingMonster.add_follower(companion.id)

            from backend.game.dungeon.outcomes import _apply_first_run_recruitment

            _apply_first_run_recruitment([companion.id])

            from backend.game.state.manager import get_party_monster_ids

            check(
                'the recruit stepped into the empty party',
                get_party_monster_ids() == [companion.id],
            )
            snapshot = goal_module.goal_snapshot()
            check(
                'the fixed goal completed on recruitment',
                snapshot and snapshot['status'] == 'complete',
            )

            # A second join must NOT displace the first companion
            second = Monster(
                name='Second Friend',
                species='Test Species',
                description='A later joiner, existing only in this suite.',
                max_health=50,
                attack=10,
                defense=10,
                speed=10,
            )
            second.save()
            created.append(second)
            _apply_first_run_recruitment([second.id])
            check(
                'a later join never displaces the party',
                get_party_monster_ids() == [companion.id],
            )

            # ===== the completion flag =====
            print('\n-- first_run_complete flow --')
            GlobalVariable.set(state_manager.FIRST_RUN_COMPLETE_KEY, False)
            check('the opening starts incomplete', not state_manager.is_first_run_complete())

            first_run.complete_first_run_if_active()
            check(
                'walking out alive completes the opening',
                state_manager.is_first_run_complete(),
            )

            # Outside a first run the hook is a quiet no-op
            GlobalVariable.set(state_manager.FIRST_RUN_COMPLETE_KEY, False)
            run_context.clear_run_context()
            first_run.complete_first_run_if_active()
            check(
                'ordinary exits never set the flag',
                not state_manager.is_first_run_complete(),
            )
            check('the hint is silent outside first runs', first_run.dialogue_hint() == '')

        finally:
            from backend.models.active_party import ActiveParty

            ActiveParty.clear_party()  # release FK holds before deletes
            run_context.clear_run_context()
            dungeon.save_dungeon_state(saved_dungeon_state)
            if saved_flag is None:
                GlobalVariable.delete_key(state_manager.FIRST_RUN_COMPLETE_KEY)
            else:
                GlobalVariable.set(state_manager.FIRST_RUN_COMPLETE_KEY, saved_flag)
            for monster in created:
                FollowingMonster.remove_follower(monster.id)
                for memory in MonsterMemory.query.filter_by(monster_id=monster.id).all():
                    memory.delete()
                fresh = Monster.get_monster_by_id(monster.id)
                if fresh:
                    fresh.delete()

    print('\n' + '=' * 50)
    print(f'PASSED: {PASSED}  FAILED: {FAILED}')
    return FAILED


if __name__ == '__main__':
    raise SystemExit(main())
