# The life gauntlet - the monster-catching life OUTSIDE the dungeon
# loop, plus the one arc that spans runs: campfire chats feeding the
# memory pipeline, the evolution altar preserving identity, and a
# monster met once returning later with truthful memories. Zero cost.
#
#   PYTHONIOENCODING=utf-8 ./venv/Scripts/python.exe tools/playtest/life_gauntlet.py
#   ... --scenario yield_return_remembers
#
# Exit code = number of failed checks; failures land in
# playtest_results/life_gauntlet_<stamp>.jsonl.

import sys
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(REPO_ROOT))

import backend  # noqa: F401 - loads .env
from tools.playtest.chat_faithfulness import score_chat_memories
from tools.playtest.gauntlet_rig import (
    STALL,
    Rig,
    ScriptedStub,
    pick_player,
    run_suite,
    scenario_registry,
    suite_args,
)
from tools.playtest.rig import run_workflow

SCENARIOS, scenario = scenario_registry()

# The chat lines carry DISTINCTIVE tokens so faithfulness has something
# to measure: the faithful memory reuses them, the fabricated one cannot
CHAT_LINES = (
    'Do you remember the sunfall bridge we crossed?',
    'The old toll keeper there sang about copper bells.',
    'I still think about the flooded orchard road.',
    'Someday we should map the glass fields together.',
)


@scenario
def chat_memory_pipeline(rig: Rig, stub: ScriptedStub):
    """Chats accumulate, housekeeping extracts memories with sources,
    the watermark advances, and the faithfulness checker catches a
    planted confabulation while passing the faithful memory"""
    from backend.game.player.manager import get_player_monster_id
    from backend.game.state.manager import get_party_monster_ids
    from backend.models.chat_thread import ChatThread
    from backend.models.monster import Monster

    player_id = get_player_monster_id()
    companion_id = next(mid for mid in get_party_monster_ids() if mid != player_id)

    # One faithful memory (reuses the transcript's distinctive tokens)
    # and one fabricated memory (talks about things nobody said)
    stub.set(
        'chat_memory_extraction',
        {
            'memories': [
                {
                    'kind': 'shared_story',
                    'content': 'Talked about the sunfall bridge and the copper bells '
                    'the toll keeper sang about.',
                },
                {
                    'kind': 'promise',
                    'content': 'Swore to slay the moon dragon of Zanzibar for the emperor.',
                },
            ]
        },
    )

    for line in CHAT_LINES:
        status = run_workflow(
            rig.queue, 'chat_with_monster', {'monster_id': companion_id, 'message': line}
        )
        rig.checks.ok(
            'chat exchange completed',
            status['status'] == 'completed' and bool((status.get('result') or {}).get('reply')),
            status.get('error'),
        )

    # 4 exchanges = 8 lines = the extraction threshold, so the last chat
    # queued a chat_housekeeping workflow BEHIND itself. run_workflow
    # waited for the chat, not for that - settle() waits for the worker
    # to finish it. (This comment previously claimed the housekeeping
    # "has already run". It had, on this machine, every time; CI caught
    # the extraction mid-write and failed four checks.)
    rig.settle()
    results = score_chat_memories(companion_id)
    rig.checks.ok('housekeeping extracted the two memories', len(results) == 2, results)

    suspects = [r for r in results if r['suspect']]
    faithful = [r for r in results if not r['suspect']]
    rig.checks.ok(
        'the checker flags exactly the fabricated memory',
        len(suspects) == 1 and 'moon dragon' in suspects[0]['content'],
        results,
    )
    rig.checks.ok(
        'the faithful memory passes clean',
        len(faithful) == 1 and 'sunfall' in faithful[0]['content'],
        results,
    )

    watermark = ChatThread.extraction_watermark(companion_id)
    rig.checks.ok('the extraction watermark advanced', watermark > 0, watermark)
    companion = Monster.get_monster_by_id(companion_id)
    rig.checks.ok(
        'a talk that produced memories deepened the bond',
        companion.affinity == 'familiar',
        companion.affinity,
    )


@scenario
def evolution_identity(rig: Rig, stub: ScriptedStub):
    """The altar transforms the monster IN PLACE - same id, memories and
    abilities survive, the lineage records the step"""
    from backend.game.memory.manager import write_memory
    from backend.game.player.manager import get_player_monster_id
    from backend.game.state.manager import get_party_monster_ids
    from backend.models.monster import Monster
    from backend.models.monster_evolution import MonsterEvolution
    from backend.models.monster_memory import MonsterMemory

    player_id = get_player_monster_id()
    companion_id = next(mid for mid in get_party_monster_ids() if mid != player_id)
    write_memory(companion_id, 'growth', 'Grew a little on the road.')

    before = Monster.get_monster_by_id(companion_id)
    species_before = before.species
    ability_ids_before = [a.id for a in (before.abilities or [])]
    memories_before = MonsterMemory.query.filter_by(monster_id=companion_id).count()

    stub.set(
        'evolution_form',
        {
            'species': 'Greater Lanternkin',
            'evolved_name': before.name,
            'family': 'Lanternkin',
            'genus': 'Newshape',
            'race_label': 'evolved',
            'size_class': 'large',
            'form_theme': 'a lantern relit',
        },
    )
    status = run_workflow(rig.queue, 'evolve_monster', {'monster_id': companion_id})
    rig.checks.ok('the ceremony completed', status['status'] == 'completed', status.get('error'))

    rig.settle()
    after = Monster.get_monster_by_id(companion_id)
    rig.checks.ok(
        'same id, transformed species',
        after is not None
        and after.species == 'Greater Lanternkin'
        and species_before != after.species,
        getattr(after, 'species', None),
    )
    memories_after = MonsterMemory.query.filter_by(monster_id=companion_id).count()
    rig.checks.ok(
        'memories survived and the ceremony added its own',
        memories_after > memories_before,
        {'before': memories_before, 'after': memories_after},
    )
    rig.checks.ok(
        'abilities survived untouched',
        [a.id for a in (after.abilities or [])] == ability_ids_before,
        ability_ids_before,
    )
    rig.checks.ok(
        'the lineage recorded exactly one step',
        MonsterEvolution.count_for_monster(companion_id) == 1,
    )
    rig.checks.ok('the monster remains fully generated', after.generation_stage == 'complete')


@scenario
def yield_return_remembers(rig: Rig, stub: ScriptedStub):
    """A monster that yielded once returns in a later run, remembering
    the yield at the place it happened"""
    from backend.game.dungeon import manager as dungeon
    from backend.models.monster_memory import MonsterMemory

    # A deterministic returning pool: this scenario's yielded enemy must
    # be the ONLY remembered monster (the shared test DB accumulates
    # memories across suites; the DB is disposable by contract)
    for row in MonsterMemory.query.all():
        row.delete()

    from tools.playtest.scripted_stub import ForcedEvents

    stub.script.update(STALL)
    stub.set('next_turn', pick_player)
    stub.set('battle_talk', {'response': 'Enough. We yield.', 'decision': 'enemies_yield'})

    # Run 1: meet, spare, walk out
    with ForcedEvents(event='monster_battle', include_exit=False):
        rig.start_forced_battle()
    from backend.game.battle import manager as battle

    enemy_ids = [int(mid) for mid in battle.get_battle_state().get('enemies', {})]
    location_then = (dungeon.get_current_location() or {}).get('name')
    rig.drive_to_pending()
    rig.talk('Yield, and keep your den.')
    run_workflow(rig.queue, 'continue_exploring', {})
    status = rig.exit_run()
    rig.checks.ok('run 1 exited alive', (status.get('result') or {}).get('exited') is True)

    yielded = [mid for mid in enemy_ids if MonsterMemory.count_kind(mid, 'yielded_to_party') >= 1]
    rig.checks.ok('the yield was remembered', bool(yielded), enemy_ids)

    # Run 2: the remembered monster returns, wary
    stub.set(
        'returning_transform',
        {
            'disposition': 'wary',
            'greeting': 'You. The ones who let us keep the den.',
            'stat_boost': 'minor',
            'battle_line': '',
            'grudge_note': '',
            'new_ability': 'no',
            'ability_theme': '',
        },
    )
    status = rig.walk_onto('returning_monster')
    result = status.get('result') or {}
    rig.checks.ok('a remembered monster returned', result.get('returning') is True, result)

    encounter = dungeon.get_active_encounter() or {}
    returned_ids = [int(mid) for mid in (encounter.get('monster_ids') or [])]
    rig.checks.ok(
        'the returner is the monster that yielded',
        bool(returned_ids) and set(returned_ids) <= set(yielded),
        {'returned': returned_ids, 'yielded': yielded},
    )

    if returned_ids:
        memory_rows = MonsterMemory.query.filter_by(monster_id=returned_ids[0]).all()
        yield_rows = [r for r in memory_rows if r.kind == 'yielded_to_party']
        rig.checks.ok(
            'its memory names the true place of the yield',
            any((r.details or {}).get('location') == location_then for r in yield_rows),
            {'expected': location_then, 'rows': [(r.kind, r.details) for r in memory_rows]},
        )


if __name__ == '__main__':
    raise SystemExit(run_suite('🏕️', SCENARIOS, suite_args(SCENARIOS, 'life_gauntlet')))
