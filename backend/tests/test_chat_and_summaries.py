# Chat & Rolling Summary Tests - OFFLINE (database only, no LLM, no server)
# Exercises the monster-chat feature and the rolling-summary upgrade:
# context budgets (fill percent), plan/compose math, chat threads and
# housekeeping (memory extraction + condensing, LLM stubbed), the
# last-run-log snapshot, and the dungeon/battle log summary storage.
#
# Usage: python -m backend.tests.test_chat_and_summaries   (from project root)
# Uses the dedicated test database (harness.py); creates and removes its own
# rows, and restores the dungeon/battle state and env vars it found.

import os

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


def noop_update(step, data):
    pass


def main():
    app = build_test_app()

    with app.app_context():
        from backend.game.battle import manager as battle
        from backend.game.chat import manager as chat
        from backend.game.dungeon import manager as dungeon
        from backend.game.memory import manager as memory
        from backend.game.utils import context_limits, rolling_summary
        from backend.models.chat_message import ChatMessage
        from backend.models.chat_summary import ChatSummary
        from backend.models.chat_thread import ChatThread
        from backend.models.core import create_tables, db
        from backend.models.following_monsters import FollowingMonster
        from backend.models.global_variables import GlobalVariable
        from backend.models.monster import Monster
        from backend.models.monster_memory import MonsterMemory

        print('🧪 CHAT & ROLLING SUMMARY TESTS')
        print('=' * 50)

        success, message = create_tables()
        check('create_tables (chat tables auto-create)', success, message)

        saved_dungeon_state = dungeon.get_dungeon_state()
        saved_battle_state = battle.get_battle_state()
        saved_last_run = dungeon.get_last_run_log()
        saved_fill = os.environ.get('LLM_CONTEXT_FILL_PERCENT')
        test_monster = None
        was_following = False
        created_run_ids = []

        try:
            # ===== Context fill percent =====
            print('\n-- Context fill percent knob --')
            os.environ.pop('LLM_CONTEXT_FILL_PERCENT', None)
            full_budget = context_limits.get_prompt_char_budget()
            os.environ['LLM_CONTEXT_FILL_PERCENT'] = '0.5'
            half_budget = context_limits.get_prompt_char_budget()
            check(
                'lower fill percent shrinks the prompt budget',
                half_budget < full_budget,
                f'{half_budget} vs {full_budget}',
            )
            os.environ['LLM_CONTEXT_FILL_PERCENT'] = '0.01'
            check(
                'fill percent clamps at a sane floor',
                context_limits.get_context_fill_percent() == 0.3,
            )
            os.environ['LLM_CONTEXT_FILL_PERCENT'] = 'not-a-number'
            check(
                'bad fill percent falls back to the default',
                context_limits.get_context_fill_percent()
                == context_limits.DEFAULT_CONTEXT_FILL_PERCENT,
            )
            os.environ.pop('LLM_CONTEXT_FILL_PERCENT', None)

            check(
                'new blocks have budget shares',
                context_limits.get_block_char_limit('chat_history')
                and context_limits.get_block_char_limit('last_run_log'),
            )

            # ===== Rolling summary math =====
            print('\n-- Rolling summary planning --')
            settings = rolling_summary.SUMMARY_SOURCES['chat_history']
            keep, batch_min, batch_max = (
                settings['keep_recent'],
                settings['batch_min'],
                settings['batch_max'],
            )

            check(
                'below threshold plans nothing',
                rolling_summary.plan_batch('chat_history', keep + batch_min - 1, 0) is None,
            )
            batch = rolling_summary.plan_batch('chat_history', keep + batch_min, 0)
            check('at threshold plans the first batch', batch == (0, batch_min), f'got {batch}')
            batch = rolling_summary.plan_batch('chat_history', keep + batch_max + 50, 0)
            check(
                'oversize backlogs are capped at batch_max', batch == (0, batch_max), f'got {batch}'
            )
            batch = rolling_summary.plan_batch('chat_history', 10 + keep + batch_min, 10)
            check('coverage offsets the next batch', batch == (10, 10 + batch_min), f'got {batch}')
            check(
                'unknown sources plan nothing',
                rolling_summary.plan_batch('nonsense', 1000, 0) is None,
            )

            check(
                'covered_count reads the furthest summary',
                rolling_summary.covered_count(
                    [{'through': 10, 'text': 'a'}, {'through': 30, 'text': 'b'}]
                )
                == 30,
            )
            check('covered_count of nothing is zero', rolling_summary.covered_count([]) == 0)

            composed = rolling_summary.compose_history(
                'chat_history',
                [{'through': 2, 'text': 'They spoke of storms.'}],
                ['You: "hello"', 'Rokk: "hm."'],
                'chat_history',
                empty_text='Nothing yet.',
            )
            check(
                'compose puts condensed old before verbatim recent',
                composed.index('storms') < composed.index('hello'),
            )
            check(
                'compose of nothing is the empty text',
                rolling_summary.compose_history(
                    'chat_history', [], [], 'chat_history', empty_text='Nothing yet.'
                )
                == 'Nothing yet.',
            )

            # ===== A monster to talk to =====
            print('\n-- Chat eligibility --')
            test_monster = Monster(
                name='Chatling',
                species='Test Sprite',
                description='A creature that exists only inside the test suite.',
            )
            test_monster.save()

            dungeon.save_dungeon_state(dict(dungeon._EMPTY_STATE))
            check(
                'unknown monsters cannot chat', chat.chat_eligibility_error(999999999) is not None
            )
            check('strangers cannot chat', chat.chat_eligibility_error(test_monster.id) is not None)

            was_following = FollowingMonster.is_following(test_monster.id)
            FollowingMonster.add_follower(test_monster.id)
            check(
                'following monsters can chat', chat.chat_eligibility_error(test_monster.id) is None
            )

            in_run_state = dict(dungeon._EMPTY_STATE)
            in_run_state['in_dungeon'] = True
            dungeon.save_dungeon_state(in_run_state)
            check(
                'chat is blocked during a dungeon run',
                chat.chat_eligibility_error(test_monster.id) is not None,
            )
            dungeon.save_dungeon_state(dict(dungeon._EMPTY_STATE))

            # ===== Thread storage =====
            print('\n-- Chat thread storage --')
            first = chat.record_player_message(test_monster.id, 'Hello there.')
            chat.record_monster_message(test_monster.id, 'Hmph. Hello.')
            for i in range(2, 30):
                role = 'player' if i % 2 == 0 else 'monster'
                ChatMessage.add(test_monster.id, role, f'Line number {i}.')
            check('messages store and count', ChatMessage.count_for_monster(test_monster.id) == 30)

            page = chat.get_history_page(test_monster.id, limit=10)
            check(
                'history page returns the latest, oldest first',
                len(page['messages']) == 10
                and page['messages'][-1]['text'] == 'Line number 29.'
                and page['has_more'] is True
                and page['total'] == 30,
            )

            older = chat.get_history_page(
                test_monster.id, limit=10, before_id=page['messages'][0]['id']
            )
            check(
                'before_id pages walk backward without overlap',
                len(older['messages']) == 10
                and older['messages'][-1]['id'] < page['messages'][0]['id'],
            )

            check(
                'after_id reads forward from a watermark',
                len(ChatMessage.after_id(test_monster.id, first.id)) == 29,
            )
            check(
                'slice_for_monster cuts by position',
                [m.text for m in ChatMessage.slice_for_monster(test_monster.id, 0, 2)]
                == ['Hello there.', 'Hmph. Hello.'],
            )

            thread = ChatThread.get_or_create(test_monster.id)
            check(
                'threads create once',
                thread is not None and ChatThread.get_or_create(test_monster.id).id == thread.id,
            )
            ChatThread.advance_extraction_watermark(test_monster.id, first.id)
            ChatThread.advance_extraction_watermark(test_monster.id, 0)
            check(
                'watermark advances and never moves back',
                ChatThread.extraction_watermark(test_monster.id) == first.id,
            )

            # ===== Chat context composition =====
            print('\n-- Chat context blocks --')
            ChatSummary.add(test_monster.id, first.id, 'They greeted each other warily.')
            block = chat.build_chat_history_block(test_monster.id, test_monster.name)
            check(
                'chat block holds condensed old + verbatim recent',
                'warily' in block and 'Line number 29.' in block and 'Hello there.' not in block,
            )

            # ===== Extraction validation (LLM seam stubbed) =====
            print('\n-- extract_chat_memories validation --')
            from backend.game.chat import generator as chat_generator

            real_generate = chat_generator.build_and_generate
            chat_generator.build_and_generate = lambda name, wf, variables: {
                'memories': [
                    {'kind': 'voiced_wish', 'content': 'It said it dreams of the open sky.'},
                    {'kind': 'nonsense-kind', 'content': 'This kind gets normalized.'},
                    {'kind': 'shared_lore', 'content': ''},  # dropped - empty
                    {'kind': 'confided', 'content': 'One.'},
                    {'kind': 'confided', 'content': 'Two - over the cap.'},
                ]
            }
            try:
                extracted = chat_generator.extract_chat_memories(
                    test_monster, ChatMessage.after_id(test_monster.id, 0, limit=4), 'test'
                )
            finally:
                chat_generator.build_and_generate = real_generate
            check(
                'extraction caps memories per pass',
                len(extracted) == chat.CHAT_SETTINGS['max_memories_per_pass'],
                str(extracted),
            )
            check(
                'unknown kinds normalize to confided',
                extracted and extracted[1]['kind'] == 'confided',
            )
            check('valid kinds pass through', extracted and extracted[0]['kind'] == 'voiced_wish')

            chat_generator.build_and_generate = lambda name, wf, variables: {'memories': []}
            try:
                empty = chat_generator.extract_chat_memories(test_monster, [], 'test')
            finally:
                chat_generator.build_and_generate = real_generate
            check('an empty extraction is a normal outcome', empty == [])

            def boom(name, wf, variables):
                raise Exception('LLM unavailable')

            chat_generator.build_and_generate = boom
            try:
                failed = chat_generator.extract_chat_memories(test_monster, [], 'test')
            finally:
                chat_generator.build_and_generate = real_generate
            check('a failed extraction returns None (watermark stays)', failed is None)

            # ===== Housekeeping workflow (extractor + condenser stubbed) =====
            print('\n-- chat_housekeeping (stubbed LLM) --')
            from backend.game.chat.registered_workflows import chat_housekeeping, chat_with_monster

            real_extract = chat_generator.extract_chat_memories
            real_summarize = rolling_summary.summarize_lines

            memories_before = len(MonsterMemory.for_monster(test_monster.id))
            chat_generator.extract_chat_memories = lambda monster, segment, wf: [
                {'kind': 'voiced_wish', 'content': 'It said it dreams of the open sky.'},
                {'kind': 'confided', 'content': 'It admitted it fears deep water.'},
            ]
            rolling_summary.summarize_lines = lambda source, lines, wf, prior_summary=None: (
                'Condensed for the test.'
            )
            try:
                result = chat_housekeeping({'monster_id': test_monster.id}, noop_update)
            finally:
                chat_generator.extract_chat_memories = real_extract
                rolling_summary.summarize_lines = real_summarize

            rows = MonsterMemory.for_monster(test_monster.id)
            new_rows = rows[memories_before:]
            check('housekeeping succeeded', result.get('success') is True, str(result))
            check('extraction wrote the memories', len(new_rows) == 2)
            check(
                'memories carry their source and span',
                all(
                    (r.details or {}).get('source') == 'home_chat'
                    and (r.details or {}).get('message_span')
                    for r in new_rows
                ),
            )
            check(
                'watermark advanced past the reviewed stretch',
                ChatThread.extraction_watermark(test_monster.id) > first.id,
            )
            check(
                'one summary batch was condensed',
                result.get('condensed') is True
                and ChatSummary.last_through_id(test_monster.id) > first.id,
            )

            memory_line = memory.get_memory_lines(test_monster.id)[-2]
            check(
                'chat memory lines say they came from a talk at home',
                'a talk at home' in memory_line,
                memory_line,
            )

            # Failed extraction leaves the watermark put
            watermark_before = ChatThread.extraction_watermark(test_monster.id)
            for i in range(30, 40):
                ChatMessage.add(test_monster.id, 'player' if i % 2 else 'monster', f'Line {i}.')
            chat_generator.extract_chat_memories = lambda monster, segment, wf: None
            rolling_summary.summarize_lines = lambda source, lines, wf, prior_summary=None: None
            try:
                chat_housekeeping({'monster_id': test_monster.id}, noop_update)
            finally:
                chat_generator.extract_chat_memories = real_extract
                rolling_summary.summarize_lines = real_summarize
            check(
                'failed extraction does NOT advance the watermark',
                ChatThread.extraction_watermark(test_monster.id) == watermark_before,
            )

            # ===== chat_with_monster workflow (stubbed reply) =====
            print('\n-- chat_with_monster (stubbed reply) --')
            real_queue_reply = chat_generator.queue_chat_reply
            real_wait = chat_generator.wait_for_streamed_text
            real_housekeeping_queue = chat.queue_housekeeping_if_due
            chat_generator.queue_chat_reply = lambda monster, msg, wf: 424242
            chat_generator.wait_for_streamed_text = lambda gen_id: 'A test reply from the void.'
            chat.queue_housekeeping_if_due = lambda monster_id: None  # offline - no real queue
            count_before = ChatMessage.count_for_monster(test_monster.id)
            try:
                result = chat_with_monster(
                    {'monster_id': test_monster.id, 'message': 'Testing, testing.'}, noop_update
                )
            finally:
                chat_generator.queue_chat_reply = real_queue_reply
                chat_generator.wait_for_streamed_text = real_wait
                chat.queue_housekeeping_if_due = real_housekeeping_queue

            check(
                'chat workflow stores both lines and returns the reply',
                result.get('success') is True
                and result.get('reply') == 'A test reply from the void.'
                and ChatMessage.count_for_monster(test_monster.id) == count_before + 2,
                str(result),
            )
            check(
                'chat workflow refuses strangers politely',
                chat_with_monster({'monster_id': 999999999, 'message': 'hi'}, noop_update).get(
                    'success'
                )
                is False,
            )

            # ===== Last-run-log snapshot =====
            print('\n-- Last run log snapshot --')
            dungeon.save_dungeon_state(
                {
                    **dict(dungeon._EMPTY_STATE),
                    'in_dungeon': True,
                    'dungeon_log': ['The party entered.', 'A fight broke out.'],
                    'dungeon_log_summaries': [{'through': 1, 'text': 'It began.'}],
                }
            )
            dungeon.snapshot_last_run_log('victory_exit')
            snapshot = dungeon.get_last_run_log()
            check(
                'snapshot preserves entries, summaries, and result',
                snapshot
                and snapshot['result'] == 'victory_exit'
                and len(snapshot['entries']) == 2
                and len(snapshot['summaries']) == 1,
            )

            status_line = chat.build_last_run_status()
            check(
                'last-run status names the ending', 'walked out alive' in status_line, status_line
            )
            last_run_block = chat.build_last_run_block()
            check(
                'last-run block composes condensed + verbatim',
                'It began.' in last_run_block and 'A fight broke out.' in last_run_block,
            )

            # ===== Dungeon log summaries =====
            print('\n-- Dungeon log rolling summaries --')
            dungeon.save_dungeon_state({**dict(dungeon._EMPTY_STATE), 'in_dungeon': True})
            for i in range(5):
                dungeon.append_dungeon_log(f'Dungeon moment {i}.')
            dungeon.record_dungeon_log_summary(2, 'The first moments, condensed.')
            log_text = dungeon.get_dungeon_log_text()
            check(
                'dungeon log text is condensed old + verbatim recent',
                'condensed' in log_text
                and 'Dungeon moment 4.' in log_text
                and 'Dungeon moment 1.' not in log_text,
            )

            # Overflow guard shifts summary coverage with dropped entries
            real_cap = dungeon.DUNGEON_LOG_MAX_ENTRIES
            dungeon.DUNGEON_LOG_MAX_ENTRIES = 6
            try:
                dungeon.append_dungeon_log('Overflow moment A.')
                dungeon.append_dungeon_log('Overflow moment B.')
            finally:
                dungeon.DUNGEON_LOG_MAX_ENTRIES = real_cap
            state = dungeon.get_dungeon_state()
            check(
                'overflow drops the oldest and shifts coverage',
                len(state['dungeon_log']) == 6
                and state['dungeon_log_summaries'][0]['through'] == 1,
                str(state['dungeon_log_summaries']),
            )

            # ===== Battle log summaries =====
            print('\n-- Battle log rolling summaries --')
            battle.start_battle(
                {str(test_monster.id): {'name': 'Chatling', 'condition': 'fresh'}},
                {'424242': {'name': 'Foe'}},
            )
            state = battle.get_battle_state()
            for i in range(5):
                battle.append_log(state, f'Blow number {i}.')
            battle.save_battle_state(state)
            battle.record_log_summary(2, 'The opening blows, condensed.')

            from backend.game.battle.generator import build_recent_log

            log_text = build_recent_log(battle.get_battle_state())
            check(
                'battle log text is condensed old + verbatim recent',
                'condensed' in log_text
                and 'Blow number 4.' in log_text
                and 'Blow number 1.' not in log_text,
            )
            battle.end_battle()

            # ===== Abandon run (call the party home) =====
            print('\n-- abandon_run --')
            from backend.models.dungeon_run import DungeonRun
            from backend.services import dungeon_service

            dungeon.save_dungeon_state(dict(dungeon._EMPTY_STATE))
            result = dungeon_service.abandon_run()
            check(
                'abandon when already home is a quiet no-op',
                result.get('success') is True and result.get('abandoned') is False,
            )

            # Never touch a real active run - only test the full path when
            # there is no run in progress on this save
            if DungeonRun.get_active() is None:
                abandon_run_row = DungeonRun.begin()
                created_run_ids.append(abandon_run_row.id)
                dungeon.save_dungeon_state(
                    {
                        **dict(dungeon._EMPTY_STATE),
                        'in_dungeon': True,
                        'run_id': abandon_run_row.id,
                        'dungeon_log': ['The party set out.', 'They turned back early.'],
                    }
                )
                result = dungeon_service.abandon_run()
                db.session.refresh(abandon_run_row)
                snap = dungeon.get_last_run_log() or {}
                check(
                    'abandon closes the run and wipes the state',
                    result.get('abandoned') is True
                    and abandon_run_row.result == 'abandoned'
                    and not dungeon.is_in_dungeon(),
                )
                check(
                    'abandon snapshots the log for home chats',
                    snap.get('result') == 'abandoned' and len(snap.get('entries', [])) == 2,
                )
            else:
                print('  ⏭️ active run present on this save - full abandon path skipped')

        finally:
            # ===== Cleanup: leave the test DB as we found it =====
            print('\n-- Cleanup --')
            try:
                if test_monster:
                    if not was_following:
                        FollowingMonster.remove_follower(test_monster.id)
                    ChatMessage.query.filter_by(monster_id=test_monster.id).delete()
                    ChatSummary.query.filter_by(monster_id=test_monster.id).delete()
                    ChatThread.query.filter_by(monster_id=test_monster.id).delete()
                    MonsterMemory.query.filter_by(monster_id=test_monster.id).delete()
                    db.session.commit()
                    test_monster.delete()
                from backend.models.dungeon_run import DungeonRun as _RunCleanup

                for run_id in created_run_ids:
                    run = _RunCleanup.get_by_id(run_id)
                    if run:
                        run.delete()
                dungeon.save_dungeon_state(saved_dungeon_state)
                battle.save_battle_state(saved_battle_state)
                if saved_last_run is None:
                    GlobalVariable.set(dungeon.LAST_RUN_LOG_KEY, None)
                else:
                    GlobalVariable.set(dungeon.LAST_RUN_LOG_KEY, saved_last_run)
                if saved_fill is None:
                    os.environ.pop('LLM_CONTEXT_FILL_PERCENT', None)
                else:
                    os.environ['LLM_CONTEXT_FILL_PERCENT'] = saved_fill
                print('  🧹 test rows removed, states and env restored')
            except Exception as e:
                print(f'  ⚠️ cleanup problem (test DB may hold test rows): {e}')

        print('\n' + '=' * 50)
        print(f'🎉 {PASSED} passed, {FAILED} failed')
        return FAILED


if __name__ == '__main__':
    raise SystemExit(main())
