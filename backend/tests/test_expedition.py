# Expedition Tests - OFFLINE (LLM stubbed, test DB)
# Exercises Game Loop M2: the run_context spine, the danger word ladder
# and its code knobs, the expedition brief block, and the notice board
# (generation, Python-rolled danger, storage, and the enter trust check).
#
# Usage: python -m backend.tests.test_expedition   (from project root)

import copy

from backend.core.workflow_steps import WorkflowStep
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


def _quiet_step() -> WorkflowStep:
    return WorkflowStep(lambda name, data: None)


def main():
    app = build_test_app()

    with app.app_context():
        import backend.game.utils as game_utils
        from backend.game.dungeon import events, run_context
        from backend.game.dungeon.handlers import notices
        from backend.models.core import create_tables

        print('🧪 EXPEDITION TESTS')
        print('=' * 50)
        create_tables()

        real_build_and_generate = game_utils.build_and_generate

        try:
            # ===== danger profiles: the word ladder is complete =====
            print('\n-- danger profile completeness --')
            required_knobs = {
                'enemy_count_range',
                'battle_event_weight',
                'explore_monsters_chance',
                'returning_event_weight',
                'referee_hint',
            }
            for word in run_context.DANGER_LADDER:
                profile = run_context.DANGER_PROFILES.get(word, {})
                check(
                    f"'{word}' profile has every knob",
                    required_knobs.issubset(profile.keys()),
                    f"missing: {required_knobs - set(profile.keys())}",
                )
            check(
                "'risky' matches the pre-danger tuning defaults",
                run_context.DANGER_PROFILES['risky']['enemy_count_range'] == (1, 2)
                and run_context.DANGER_PROFILES['risky']['battle_event_weight'] == 0.18
                and run_context.DANGER_PROFILES['risky']['explore_monsters_chance'] == 0.5,
            )

            # ===== run_context lifecycle =====
            print('\n-- run_context lifecycle --')
            run_context.clear_run_context()
            check('no run -> empty context', run_context.get_run_context() == {})
            check('no run -> no active danger', run_context.active_danger() is None)
            check(
                'no run -> danger_knob falls back to the caller default',
                run_context.danger_knob('enemy_count_range', (7, 9)) == (7, 9),
            )
            check(
                'no run -> ordinary-expedition brief',
                'ordinary expedition' in run_context.expedition_brief(),
            )

            run_context.begin_run_context(theme='drowned halls', danger='perilous')
            check(
                'begin stores the theme', run_context.get_run_context()['theme'] == 'drowned halls'
            )
            check('begin stores the danger', run_context.active_danger() == 'perilous')
            check(
                'danger_knob reads the active profile',
                run_context.danger_knob('enemy_count_range', (1, 2)) == (2, 3),
            )
            brief = run_context.expedition_brief()
            check('brief carries the theme', 'drowned halls' in brief)
            check('brief carries the danger word', 'perilous' in brief)

            run_context.begin_run_context(theme=None, danger='astronomical')
            check(
                'unknown danger word is dropped (not stored)',
                run_context.active_danger() is None,
            )

            run_context.clear_run_context()
            check('clear empties the context', run_context.get_run_context() == {})

            # ===== danger drives the event rolls =====
            print('\n-- danger-aware rolls --')
            real_random = events.random.random
            try:
                run_context.begin_run_context(theme=None, danger='calm')
                events.random.random = lambda: 0.45
                check(
                    'calm: 0.45 roll finds no monsters (chance 0.4)',
                    events.roll_monsters_present() is False,
                )
                run_context.begin_run_context(theme=None, danger='perilous')
                check(
                    'perilous: 0.45 roll finds monsters (chance 0.65)',
                    events.roll_monsters_present() is True,
                )
            finally:
                events.random.random = real_random
                run_context.clear_run_context()

            valid_events = set(events.EVENT_WEIGHTS) | {'returning_monster'}
            rolled = {events.assign_random_event(include_returning=True) for _ in range(60)}
            check('assign_random_event only rolls known events', rolled.issubset(valid_events))

            # ===== the notice board =====
            print('\n-- notice board generation --')

            def fake_notices(template, workflow, variables=None):
                assert template == 'expedition_notices'
                return {
                    'notices': [
                        {
                            'title': 'The Sunken Belfry',
                            'pitch': 'Bells below.',
                            'theme': 'drowned bells',
                        },
                        {'title': 'Mosswood', 'pitch': 'It hums.', 'theme': 'singing moss'},
                        {'title': 'Ash Vaults', 'pitch': 'Still warm.', 'theme': 'ash and cinders'},
                    ]
                }

            game_utils.build_and_generate = fake_notices
            result = notices.run_generate_notices({}, _quiet_step())
            check('workflow returns a success envelope', bool(result.get('success')))
            board = result.get('notices') or []
            check('three notices posted', len(board) == 3, f'got {len(board)}')
            check(
                'every notice carries id/title/theme/danger',
                all(
                    n.get('id') and n.get('title') and n.get('theme') and n.get('danger')
                    for n in board
                ),
            )
            check(
                'every danger word is on the ladder (Python rolled it)',
                all(n['danger'] in run_context.DANGER_LADDER for n in board),
            )

            print('\n-- notice storage + trust check --')
            first = board[0]
            check(
                'the stored board answers by id',
                run_context.get_pending_notice(first['id'])['title'] == first['title'],
            )
            check(
                'unknown notice id is rejected', run_context.get_pending_notice('notice_99') is None
            )

            print('\n-- notice fallbacks --')

            def broken_llm(template, workflow, variables=None):
                raise Exception('the model choked')

            game_utils.build_and_generate = broken_llm
            result = notices.run_generate_notices({}, _quiet_step())
            board = result.get('notices') or []
            check('a broken LLM still posts a full board', len(board) == 3)
            check(
                'fallback notices carry rolled danger words',
                all(n['danger'] in run_context.DANGER_LADDER for n in board),
            )

            run_context.clear_pending_notices()
            check(
                'cleared board answers nothing', run_context.get_pending_notice('notice_1') is None
            )

            # ===== run goals (Game Loop M3) =====
            print('\n-- goal generation --')
            from backend.game.dungeon import goal as goal_module
            from backend.game.dungeon import manager as dungeon_manager

            run_context.begin_run_context(theme='drowned halls', danger='calm')

            def fake_goal(template, workflow, variables=None):
                return {'goal': 'Find the moonlit spring said to rise in these halls.'}

            game_utils.build_and_generate = fake_goal
            goal_module.generate_run_goal('test')
            snapshot = goal_module.goal_snapshot()
            check('goal stored as pending', snapshot and snapshot['status'] == 'pending')
            check('brief carries the goal', 'moonlit spring' in run_context.expedition_brief())

            def broken_goal(template, workflow, variables=None):
                raise Exception('no goal today')

            game_utils.build_and_generate = broken_goal
            goal_module.generate_run_goal('test')
            check('a broken LLM still writes a fallback goal', bool(goal_module.goal_snapshot()))

            print('\n-- goal referee + completion valve --')
            game_utils.build_and_generate = fake_goal
            goal_module.generate_run_goal('test')

            # The dungeon log is where the referee reads events from -
            # give the checks an in-dungeon state to log against
            saved_state = dungeon_manager.get_dungeon_state()
            dungeon_manager.save_dungeon_state(
                {
                    'in_dungeon': True,
                    'current_location': {'name': 'Test Hall', 'description': ''},
                    'available_paths': {},
                    'active_encounter': None,
                    'party_conditions': {},
                    'party_resources': {},
                    'run_journal': {},
                    'run_id': None,
                    'seen_monster_ids': [],
                    'dungeon_log': ['The party entered.'],
                    'dungeon_log_summaries': [],
                }
            )
            try:

                def referee_says(answer, note=None):
                    def fake_check(template, workflow, variables=None):
                        assert template == 'goal_check'
                        return {'answer': answer, 'note': note}

                    return fake_check

                # Check 1: 'complete' too early is VALVED down to progress
                game_utils.build_and_generate = referee_says('complete', 'Found it immediately!')
                goal_module.check_goal_progress('test')
                snapshot = goal_module.goal_snapshot()
                check(
                    "valve: 'complete' before GOAL_MIN_EVENTS becomes progress",
                    snapshot['status'] == 'pending' and len(snapshot['progress_notes']) == 1,
                )

                # Check 2: 'no' changes nothing
                game_utils.build_and_generate = referee_says('no')
                goal_module.check_goal_progress('test')
                snapshot = goal_module.goal_snapshot()
                check("'no' leaves the goal untouched", len(snapshot['progress_notes']) == 1)

                # Check 3: at GOAL_MIN_EVENTS, 'complete' lands
                game_utils.build_and_generate = referee_says('complete', 'The spring was found.')
                goal_module.check_goal_progress('test')
                snapshot = goal_module.goal_snapshot()
                check(
                    'complete lands once enough events resolved',
                    snapshot['status'] == 'complete',
                    f"status={snapshot['status']}",
                )

                # Check 4: a completed goal stops asking the referee
                def referee_must_not_run(template, workflow, variables=None):
                    raise AssertionError('goal_check ran after completion')

                game_utils.build_and_generate = referee_must_not_run
                goal_module.check_goal_progress('test')
                check('a completed goal is never re-checked', True)

                # Check 5: garbage answers degrade to 'no'
                game_utils.build_and_generate = fake_goal
                goal_module.generate_run_goal('test')
                game_utils.build_and_generate = referee_says('absolutely!', 'so sure')
                goal_module.check_goal_progress('test')
                snapshot = goal_module.goal_snapshot()
                check(
                    'unknown referee words count as no',
                    snapshot['status'] == 'pending' and not snapshot['progress_notes'],
                )
            finally:
                dungeon_manager.save_dungeon_state(saved_state)

            # ===== the post-run chronicle (Game Loop M7) =====
            print('\n-- run chronicle --')
            from backend.game.dungeon import chronicle
            from backend.models.dungeon_run import DungeonRun

            saved_state = dungeon_manager.get_dungeon_state()
            run = DungeonRun.begin()
            try:
                run_state = copy.deepcopy(dungeon_manager._EMPTY_STATE)
                run_state.update(
                    {
                        'in_dungeon': True,
                        'run_id': run.id if run else None,
                        'dungeon_log': ['The party entered.', 'A spring was found.'],
                    }
                )
                dungeon_manager.save_dungeon_state(run_state)
                run_context.begin_run_context(theme='drowned halls', danger='calm')
                game_utils.build_and_generate = fake_goal
                goal_module.generate_run_goal('test')

                captured = {}

                def fake_stream(template, workflow, variables=None):
                    captured['template'] = template
                    captured.update(variables or {})
                    return 4242

                real_build_and_stream = game_utils.build_and_stream
                game_utils.build_and_stream = fake_stream
                try:
                    queued = chronicle.queue_run_chronicle('victory', 'test')
                finally:
                    game_utils.build_and_stream = real_build_and_stream

                check('the chronicle queued', queued and queued['generation_id'] == 4242)
                check(
                    'it knows its run number',
                    run and queued.get('run_number') == run.run_number,
                )
                check(
                    'the goal line rides in',
                    'moonlit spring' in captured.get('goal_line', ''),
                )
                check(
                    'the log rides in',
                    'A spring was found.' in captured.get('dungeon_log', ''),
                )
                check(
                    'a run without recruits says so',
                    'No new companions' in captured.get('companions_line', ''),
                )

                check(
                    'an unqueued chronicle awaits to None',
                    chronicle.await_run_chronicle(None) is None,
                )
            finally:
                DungeonRun.close('abandoned')
                dungeon_manager.save_dungeon_state(saved_state)

        finally:
            game_utils.build_and_generate = real_build_and_generate
            run_context.clear_run_context()
            run_context.clear_pending_notices()

    print('\n' + '=' * 50)
    print(f'PASSED: {PASSED}  FAILED: {FAILED}')
    return FAILED


if __name__ == '__main__':
    raise SystemExit(main())
