# The dungeon gauntlet - directed scenarios for every path event the
# crash driver only reaches by luck: treasure, the full dialogue-outcome
# tree, the out-of-battle referee (abilities and items), camp rest, the
# victory-exit ceremony, and the goal's reward. Zero cost, scripted stub.
#
#   PYTHONIOENCODING=utf-8 ./venv/Scripts/python.exe tools/playtest/dungeon_gauntlet.py
#   ... --scenario dialogue_tree
#
# Exit code = number of failed checks; failures land in
# playtest_results/dungeon_gauntlet_<stamp>.jsonl.

import sys
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(REPO_ROOT))

import backend  # noqa: F401 - loads .env
from tools.playtest.gauntlet_rig import (
    STALL,
    Rig,
    ScriptedStub,
    pick_player,
    run_suite,
    scenario_registry,
    suite_args,
)
from tools.playtest.rig import refresh_session, run_workflow

SCENARIOS, scenario = scenario_registry()


def active_monster_id():
    """The single monster of the current encounter (dialogue or explore)"""
    from backend.game.dungeon import manager as dungeon

    encounter = dungeon.get_active_encounter() or {}
    ids = encounter.get('monster_ids') or []
    return int(ids[0]) if ids else None


@scenario
def treasure_spoils(rig: Rig, stub: ScriptedStub):
    """Treasure is provisional in the run and REAL after a living exit"""
    from backend.game.dungeon.spoils import get_run_spoils
    from backend.models.item import Item

    status = rig.walk_onto('treasure')
    result = status.get('result') or {}
    item = result.get('item') or {}
    rig.checks.ok(
        'treasure event delivered an item', result.get('event') == 'treasure' and item, result
    )
    rig.checks.ok(
        'found item recorded as provisional spoils',
        item.get('id') in get_run_spoils()['run_item_ids'],
        get_run_spoils(),
    )

    status = rig.exit_run()
    rig.checks.ok('walked out alive', (status.get('result') or {}).get('exited') is True)
    refresh_session()
    kept = Item.get_item_by_id(item.get('id')) if item.get('id') else None
    rig.checks.ok(
        'the exit made the treasure real', kept is not None and kept.name == item.get('name')
    )


@scenario
def dialogue_tree(rig: Rig, stub: ScriptedStub):
    """Each dialogue outcome does exactly what its word promises"""
    from backend.game.dungeon import manager as dungeon
    from backend.game.dungeon.spoils import get_run_spoils
    from backend.models.following_monsters import FollowingMonster
    from backend.models.monster_memory import MonsterMemory

    def talk_expecting(outcome_word: str):
        stub.set(
            'monster_dialogue_turn',
            {'response': f'So be it - {outcome_word}.', 'outcome': outcome_word},
        )
        status = run_workflow(rig.queue, 'respond_to_monster', {'message': 'We come in peace.'})
        rig.checks.invariants(status)
        return status.get('result') or {}

    # continue_dialogue keeps the encounter (and its monster) in place
    rig.walk_onto('monster_dialogue')
    speaker_id = active_monster_id()
    rig.checks.ok('dialogue event staged a speaking monster', speaker_id is not None)
    result = talk_expecting('continue_dialogue')
    rig.checks.ok(
        'continue_dialogue keeps the encounter open',
        result.get('outcome') == 'continue_dialogue' and active_monster_id() == speaker_id,
    )

    # allow_passage resolves it peacefully and leaves a warm memory
    result = talk_expecting('allow_passage')
    rig.checks.ok('allow_passage clears the encounter', active_monster_id() is None, result)
    rig.checks.ok(
        'allow_passage remembered as let_party_pass',
        MonsterMemory.count_kind(speaker_id, 'let_party_pass') == 1,
    )

    # begin_battle turns words into a fight
    rig.walk_onto('monster_dialogue')
    result = talk_expecting('begin_battle')
    from backend.game.battle import manager as battle

    rig.checks.ok(
        'begin_battle opened a battle',
        result.get('outcome') == 'begin_battle' and battle.get_battle_state().get('in_battle'),
    )
    stub.script.update(STALL)
    stub.set('next_turn', pick_player)
    stub.set('battle_talk', {'response': 'We yield.', 'decision': 'enemies_yield'})
    rig.drive_to_pending()
    rig.talk('Stand down.')
    run_workflow(rig.queue, 'continue_exploring', {})

    # join_party recruits (provisionally) and follows the party
    rig.walk_onto('monster_dialogue')
    joiner_id = active_monster_id()
    result = talk_expecting('join_party')
    rig.checks.ok('join_party reported the joined names', bool(result.get('joined_names')), result)
    rig.checks.ok(
        'joiner follows the party as provisional spoils',
        joiner_id in FollowingMonster.get_following_monster_ids()
        and joiner_id in get_run_spoils()['run_recruits'],
    )

    # reward grants a real, provisional item
    rig.walk_onto('monster_dialogue')
    giver_id = active_monster_id()
    result = talk_expecting('reward')
    item = result.get('item') or {}
    rig.checks.ok('reward delivered an item', bool(item), result)
    rig.checks.ok(
        'reward item is provisional + remembered as gave_reward',
        item.get('id') in get_run_spoils()['run_item_ids']
        and MonsterMemory.count_kind(giver_id, 'gave_reward') == 1,
    )

    # punish resolves the encounter and leaves the sour memory
    rig.walk_onto('monster_dialogue')
    punisher_id = active_monster_id()
    result = talk_expecting('punish')
    rig.checks.ok(
        'punish resolves peacefully with the sour memory',
        active_monster_id() is None
        and MonsterMemory.count_kind(punisher_id, 'punished_party') == 1,
        result,
    )
    rig.checks.ok('the run itself continues', dungeon.is_in_dungeon())


@scenario
def referee_effects(rig: Rig, stub: ScriptedStub):
    """Out-of-battle referee: heals move the ladder, costs tire the actor,
    item uses are spent no matter the outcome"""
    from backend.game.dungeon import manager as dungeon
    from backend.game.player.manager import get_player_monster_id
    from backend.game.state.manager import get_party_monster_ids
    from backend.models.item import Item
    from backend.models.monster import Monster

    rig.walk_onto('location_explore', monsters_present=False)

    player_id = get_player_monster_id()
    dungeon.set_party_conditions({str(player_id): 'battered'})

    actor_id = next(mid for mid in get_party_monster_ids() if mid != player_id)
    actor = Monster.get_monster_by_id(actor_id)
    ability = actor.abilities[0]

    stub.set(
        'dungeon_ability_use',
        {
            'narration': 'Warm light knits the wounds.',
            'effect': 'heal_light',
            'stamina_cost': 'minor',
            'mana_cost': 'none',
        },
    )
    status = run_workflow(
        rig.queue,
        'use_dungeon_ability',
        {
            'monster_id': actor_id,
            'ability_id': ability.id,
            'target_type': 'monster',
            'target_id': player_id,
        },
    )
    rig.checks.invariants(status)
    result = status.get('result') or {}
    conditions = dungeon.get_party_conditions()
    rig.checks.ok(
        'heal_light stepped the target battered -> wounded',
        result.get('effect') == 'heal_light' and conditions.get(str(player_id)) == 'wounded',
        conditions,
    )
    resources = dungeon.get_party_resources()
    rig.checks.ok(
        'minor cost tired the ACTOR brimming -> steady',
        (resources.get(str(actor_id)) or {}).get('stamina') == 'steady',
        resources,
    )

    # An item heal: spends a use AND heals the party target
    item = Item.query.filter(Item.uses_remaining > 0).first()
    uses_before = item.uses_remaining
    stub.set(
        'dungeon_item_use',
        {'narration': 'The bread does its quiet work.', 'effect': 'heal_light'},
    )
    status = run_workflow(
        rig.queue,
        'use_dungeon_item',
        {'item_id': item.id, 'target_type': 'monster', 'target_id': player_id},
    )
    rig.checks.invariants(status)
    refresh_session()
    conditions = dungeon.get_party_conditions()
    spent = Item.get_item_by_id(item.id)
    rig.checks.ok(
        'item heal stepped wounded -> scuffed and spent one use',
        conditions.get(str(player_id)) == 'scuffed'
        and (spent is None or spent.uses_remaining == uses_before - 1),
        conditions,
    )

    # A reveal on a path passes the referee's word through untouched
    paths = dungeon.get_dungeon_state().get('available_paths') or {}
    path_id = next(iter(paths))
    stub.set(
        'dungeon_ability_use',
        {
            'narration': 'A vision of what waits beyond.',
            'effect': 'reveal',
            'stamina_cost': 'none',
            'mana_cost': 'minor',
        },
    )
    status = run_workflow(
        rig.queue,
        'use_dungeon_ability',
        {
            'monster_id': actor_id,
            'ability_id': ability.id,
            'target_type': 'path',
            'target_id': path_id,
        },
    )
    rig.checks.invariants(status)
    rig.checks.ok(
        'reveal passes through with its narration',
        (status.get('result') or {}).get('effect') == 'reveal',
        status.get('result'),
    )


@scenario
def camp_rest(rig: Rig, stub: ScriptedStub):
    """Camp restores by the referee's words, bonds deepen, one camp only"""
    from backend.game.dungeon import manager as dungeon
    from backend.game.player.manager import get_player_monster_id
    from backend.game.state.manager import get_party_monster_ids
    from backend.models.monster import Monster

    rig.walk_onto('location_explore', monsters_present=False)

    party_ids = get_party_monster_ids()
    dungeon.set_party_resources(
        {str(mid): {'stamina': 'spent', 'mana': 'spent'} for mid in party_ids}
    )

    def real_name_restores(stub_instance):
        names = [
            m.name for m in (Monster.get_monster_by_id(mid) for mid in get_party_monster_ids()) if m
        ]
        return {
            'restores': [
                {'name': name, 'stamina': 'restore_major', 'mana': 'restore_minor'}
                for name in names
            ]
        }

    stub.set('camp_restore', real_name_restores)
    status = run_workflow(rig.queue, 'setup_camp', {})
    rig.checks.invariants(status)
    rig.checks.ok('camp completed', status['status'] == 'completed', status.get('error'))

    resources = dungeon.get_party_resources()
    sample = resources.get(str(party_ids[0])) or {}
    rig.checks.ok(
        'restore words moved the pools (spent -> strained / drained)',
        sample.get('stamina') == 'strained' and sample.get('mana') == 'drained',
        resources,
    )

    player_id = get_player_monster_id()
    companions = [Monster.get_monster_by_id(mid) for mid in party_ids if mid != player_id]
    rig.checks.ok(
        'the night deepened every companion bond one step',
        all(m.affinity == 'familiar' for m in companions),
        [(m.name, m.affinity) for m in companions],
    )

    status = run_workflow(rig.queue, 'setup_camp', {})
    error_text = str(status.get('error') or '')
    rig.checks.ok(
        'a second camp at the same location is refused honestly',
        status['status'] == 'failed' and 'already camped' in error_text,
        status.get('error'),
    )


@scenario
def victory_exit(rig: Rig, stub: ScriptedStub):
    """Walking out alive: growth, memories, chronicle, closed run row"""
    from backend.game.state.manager import get_party_monster_ids
    from backend.models.dungeon_run import DungeonRun
    from backend.models.monster_memory import MonsterMemory

    stub.set(
        'growth_reflection',
        {
            'reflection': 'The road gave, and it took.',
            'stat': 'attack',
            'tier': 'notable',
            'memory_note': 'Came home harder.',
        },
    )
    rig.walk_onto('location_explore', monsters_present=False)
    party_ids = get_party_monster_ids()

    status = rig.exit_run()
    result = status.get('result') or {}
    rig.checks.ok('the exit completed', result.get('exited') is True, result)
    rig.checks.ok(
        'every member got a growth reflection',
        len(result.get('growth') or []) == len(party_ids),
        result.get('growth'),
    )
    rig.checks.ok('the chronicle was written', bool(result.get('chronicle')))

    refresh_session()
    latest = DungeonRun.query.order_by(DungeonRun.id.desc()).first()
    rig.checks.ok(
        "run row closed as victory_exit with the chronicle as its summary",
        latest is not None and latest.result == 'victory_exit' and bool(latest.summary),
        getattr(latest, 'result', None),
    )
    walked_out = [MonsterMemory.count_kind(mid, 'run_complete') for mid in party_ids]
    rig.checks.ok(
        'every member remembers walking out alive', all(n >= 1 for n in walked_out), walked_out
    )


@scenario
def goal_reward(rig: Rig, stub: ScriptedStub):
    """A fulfilled goal pays out at the exit - item plus bonus growth"""
    from backend.game.dungeon import goal
    from backend.models.item import Item

    stub.set('goal_check', {'answer': 'complete', 'note': 'The very thing, found.'})

    # The completion valve (GOAL_MIN_EVENTS) downgrades early "complete"
    # answers to progress - the gauntlet found that on its first run.
    # Walk enough resolved events for a completion to be allowed to stand.
    from backend.game.dungeon.goal import GOAL_MIN_EVENTS

    for _ in range(GOAL_MIN_EVENTS):
        rig.walk_onto('location_explore', monsters_present=False)

    snapshot = goal.goal_snapshot()
    rig.checks.ok(
        'the goal completed once past the completion valve',
        bool(snapshot) and snapshot.get('status') == 'complete',
        snapshot,
    )

    status = rig.exit_run()
    result = status.get('result') or {}
    reward = result.get('goal_reward') or {}
    reward_item = reward.get('item') or {}
    rig.checks.ok('the reward ceremony granted an item', bool(reward_item), result)
    rig.checks.ok(
        'the ceremony granted bonus growth to the party', bool(reward.get('growth')), reward
    )
    refresh_session()
    kept = Item.get_item_by_id(reward_item.get('id')) if reward_item.get('id') else None
    rig.checks.ok('the reward item survived the exit', kept is not None)


if __name__ == '__main__':
    raise SystemExit(run_suite('🕳️', SCENARIOS, suite_args(SCENARIOS, 'dungeon_gauntlet')))
