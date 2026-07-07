# New Game Tests - OFFLINE (no LLM, test DB)
# Exercises Ngx-M1 (docs/plans/new-game-experience.md): wipe_world()
# erases every game-domain table in FK-safe order while the developer
# log tables survive, the busy guard asks the LIVE queue (stale table
# rows from a dead process must never block New Game),
# GameWorkflow.close_dangling() sweeps those strays at startup, and
# has_world_data flips with the world.
#
# Usage: python -m backend.tests.test_new_game   (from project root)

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


def seed_world():
    """One row in every game-domain table, wired like the real thing.
    Returns the pending workflow (the busy-guard prop)."""
    from backend.models.ability import Ability
    from backend.models.active_party import ActiveParty
    from backend.models.chat_message import ChatMessage
    from backend.models.chat_summary import ChatSummary
    from backend.models.chat_thread import ChatThread
    from backend.models.cocatok import CoCaTok
    from backend.models.dungeon_run import DungeonRun
    from backend.models.following_monsters import FollowingMonster
    from backend.models.game_workflow import GameWorkflow
    from backend.models.global_variables import GlobalVariable
    from backend.models.item import Item
    from backend.models.monster import Monster
    from backend.models.monster_evolution import MonsterEvolution
    from backend.models.monster_memory import MonsterMemory

    monster = Monster(
        name='Doomed Friend',
        species='Test Species',
        description='Exists only to be erased by this suite.',
        max_health=50,
        attack=10,
        defense=10,
        speed=10,
    )
    monster.save()

    Ability(
        monster_id=monster.id,
        name='Farewell Wave',
        description='A test ability that will not survive the wipe.',
        ability_type='support',
    ).save()

    run = DungeonRun.begin()
    MonsterMemory.add(monster.id, 'joined_party', 'It joined a doomed world.', run_id=run.id)

    MonsterEvolution(
        monster_id=monster.id,
        stage=1,
        old_name='Doomed Friend',
        old_species='Test Species',
        new_name='Doomed Friend Prime',
        new_species='Test Species Prime',
        new_rarity='rare',
    ).save()

    ChatThread.get_or_create(monster.id)
    message = ChatMessage.add(monster.id, 'player', 'Goodbye, little world.')
    ChatSummary.add(monster.id, message.id, 'They said their goodbyes.')

    FollowingMonster.add_follower(monster.id)
    ActiveParty.add_to_party(monster.id)

    Item(name='Test Trinket', description='A trinket the wipe will claim.').save()
    CoCaTok(title='Last Victory', commemoration='A victory no one will remember.').save()
    GlobalVariable.set('first_run_complete', True)

    workflow = GameWorkflow.create_workflow('test_new_game_prop', {})
    workflow.save()
    return workflow


def game_row_counts() -> dict[str, int]:
    """Row count per game-domain table (mirrors the wipe list)"""
    from backend.models.ability import Ability
    from backend.models.active_party import ActiveParty
    from backend.models.chat_message import ChatMessage
    from backend.models.chat_summary import ChatSummary
    from backend.models.chat_thread import ChatThread
    from backend.models.cocatok import CoCaTok
    from backend.models.dungeon_run import DungeonRun
    from backend.models.following_monsters import FollowingMonster
    from backend.models.game_workflow import GameWorkflow
    from backend.models.global_variables import GlobalVariable
    from backend.models.item import Item
    from backend.models.monster import Monster
    from backend.models.monster_evolution import MonsterEvolution
    from backend.models.monster_memory import MonsterMemory

    models = (
        ActiveParty,
        FollowingMonster,
        ChatMessage,
        ChatSummary,
        ChatThread,
        MonsterMemory,
        MonsterEvolution,
        Ability,
        Monster,
        DungeonRun,
        Item,
        CoCaTok,
        GameWorkflow,
        GlobalVariable,
    )
    return {model.__tablename__: model.query.count() for model in models}


def main():
    app = build_test_app()

    with app.app_context():
        from backend.models.core import create_tables
        from backend.models.generation_log import GenerationLog
        from backend.services import game_state_service

        print('🧪 NEW GAME TESTS')
        print('=' * 50)
        create_tables()

        survivor = None
        try:
            # ===== a world worth grieving =====
            print('\n-- seeding a world --')
            workflow = seed_world()

            survivor = GenerationLog(
                generation_type='llm',
                prompt_type='test',
                prompt_name='test_new_game_survivor',
                prompt_text='This log must outlive the wipe.',
            )
            survivor.save()

            counts = game_row_counts()
            check(
                'every game table holds at least one row',
                all(count > 0 for count in counts.values()),
                str({table: count for table, count in counts.items() if count == 0}),
            )
            state = game_state_service.get_game_state()
            check('the seeded world reads as world data', state.get('has_world_data') is True)

            # ===== dangling rows from a dead process =====
            print('\n-- the dangling sweep --')
            from backend.models.game_workflow import GameWorkflow

            stuck_processing = GameWorkflow.create_workflow('test_stuck_processing', {})
            stuck_processing.mark_started()
            stuck_processing.save()

            closed = GameWorkflow.close_dangling()
            check('both stray rows were closed', closed == 2, str(closed))
            check(
                'nothing reads as live work anymore',
                GameWorkflow.query.filter(
                    GameWorkflow.status.in_(('pending', 'processing'))
                ).count()
                == 0,
            )
            swept = GameWorkflow.query.get(workflow.id)
            check(
                'the closed row says why',
                'shutdown' in (swept.error_message or ''),
                str(swept.error_message),
            )

            # ===== the busy guard asks the LIVE queue =====
            print('\n-- the busy guard --')
            import backend.workflow.workflow_queue as workflow_queue_module

            class BusyQueueStub:
                def get_queue_status(self):
                    return {'status_counts': {'pending': 1, 'processing': 0}}

            real_get_queue = workflow_queue_module.get_queue
            workflow_queue_module.get_queue = lambda: BusyQueueStub()
            try:
                result = game_state_service.start_new_game()
                check('a live queued workflow blocks the wipe', result['success'] is False)
                check(
                    'the blocked world is untouched',
                    game_row_counts()['monsters'] > 0,
                )
            finally:
                workflow_queue_module.get_queue = real_get_queue

            # ===== the wipe =====
            print('\n-- the wipe --')
            # A stale pending row (as if a process died mid-story) must
            # NOT block - the guard reads the live queue, and the wipe
            # clears the stray with everything else
            GameWorkflow.create_workflow('test_stale_leftover', {}).save()

            # The frontend empties its rosters on this event - it must
            # fire, and only after the world is already gone
            from backend.core.events import subscribe_to_event

            erased_events = []
            subscribe_to_event(
                'game.world_erased',
                lambda event: erased_events.append(game_row_counts()['monsters']),
            )

            result = game_state_service.start_new_game()
            check('a stale table row never blocks the wipe', result['success'] is True)
            check(
                'the world-erased event fired over an empty world',
                erased_events == [0],
                str(erased_events),
            )

            counts = game_row_counts()
            check(
                'every game table is empty',
                all(count == 0 for count in counts.values()),
                str({table: count for table, count in counts.items() if count}),
            )
            check(
                'the developer logs survive',
                GenerationLog.query.get(survivor.id) is not None,
            )
            state = game_state_service.get_game_state()
            check('the erased world reads as fresh', state.get('has_world_data') is False)
            check(
                'the opening is unfinished again',
                state.get('first_run_complete') is False,
            )

        finally:
            # The wipe already left the game tables empty (their natural
            # post-suite state); only the survivor log is ours to remove.
            if survivor is not None:
                fresh = GenerationLog.query.get(survivor.id)
                if fresh:
                    fresh.delete()

    print('\n' + '=' * 50)
    print(f'PASSED: {PASSED}  FAILED: {FAILED}')
    return FAILED


if __name__ == '__main__':
    raise SystemExit(main())
