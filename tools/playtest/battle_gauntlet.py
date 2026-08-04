# The battle gauntlet - directed scenarios that force the battle system
# into its promised corners and ASSERT the promises, using the scripted
# stub (zero cost). The crash driver asks "does a random battle crash?";
# the gauntlet asks "does the softlock valve actually fire at 6, does a
# caught negotiation actually forfeit the run's spoils, does a wary ally
# actually refuse orders". One command, every scenario:
#
#   PYTHONIOENCODING=utf-8 ./venv/Scripts/python.exe tools/playtest/battle_gauntlet.py
#   ... --scenario softlock_valve       # just one
#
# Exit code = number of failed checks. Failures also land in
# playtest_results/battle_gauntlet_<stamp>.jsonl with full context.

import sys
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(REPO_ROOT))

import backend  # noqa: F401 - loads .env
from tools.playtest.gauntlet_rig import (
    STALL,
    Rig,
    ScriptedStub,
    hostile_streaks,
    pick_enemy,
    pick_player,
    scenario_registry,
)
from tools.playtest.rig import run_workflow
from tools.playtest.scripted_stub import ForcedEvents

SCENARIOS, scenario = scenario_registry()

# ===== SCENARIOS =====


@scenario
def softlock_valve(rig: Rig, stub: ScriptedStub):
    """The director may never run more than 6 enemy turns in a row"""
    from backend.game.battle import manager as battle
    from backend.game.battle.constants import MAX_CONSECUTIVE_ENEMY_TURNS

    stub.script.update(STALL)
    stub.set('next_turn', pick_enemy)  # the LLM director only ever picks enemies
    rig.start_forced_battle()

    status = rig.drive_to_pending()
    for _ in range(3):
        result = status.get('result') or {}
        rig.checks.ok('control returned to the player', result.get('pending') == 'player_turn')
        status = rig.defend(status)

    # The promise is the CAP. A short streak (even zero) just means the
    # dice never gave the enemies a long run - only exceeding the cap is
    # a defect, so asserting a MINIMUM made the suite flaky, not stricter.
    state = battle.get_battle_state()
    streak = hostile_streaks(state)
    rig.checks.ok(
        f'enemy streak never exceeds {MAX_CONSECUTIVE_ENEMY_TURNS} (saw {streak})',
        streak <= MAX_CONSECUTIVE_ENEMY_TURNS,
        {'longest_streak': streak},
    )
    rig.checks.ok(
        'the battle actually resolved turns',
        state.get('turn_count', 0) > 0,
        state.get('turn_count'),
    )

    stub.set('battle_talk', {'response': 'We are done here.', 'decision': 'enemies_yield'})
    status = rig.talk('Enough - lay down your claws and go in peace.')
    result = status.get('result') or {}
    rig.checks.ok(
        'yield ended the battle',
        result.get('outcome') == 'victory' and result.get('resolution') == 'yielded',
        result,
    )


@scenario
def turn_cost_bound(rig: Rig, stub: ScriptedStub):
    """ONE battle_turn resolves every NPC turn before the player is asked
    again - and a WARY ally satisfies the softlock valve without handing
    control back (director.py resets the streak counter when an
    autonomous ally acts). Only the fairness guardrail guarantees the
    player is reached. This measures how many turns that costs, because
    every one of them is several REAL model calls in a live game: the
    first live adversarial run had a single battle_turn exceed 900s."""
    from backend.game.battle import manager as battle
    from backend.game.battle.constants import OVERDUE_WAIT_MULTIPLIER
    from backend.game.monster.affinity import get_affinity
    from backend.game.player.manager import get_player_monster_id
    from backend.game.state.manager import get_party_monster_ids
    from backend.models.monster import Monster

    stub.script.update(STALL)
    # The director never volunteers the player's own monster
    stub.set('next_turn', pick_enemy)
    rig.start_forced_battle()

    player_id = str(get_player_monster_id())
    companions = [
        Monster.get_monster_by_id(mid) for mid in get_party_monster_ids() if str(mid) != player_id
    ]
    rig.checks.ok(
        'the default party is wary (autonomous) companions',
        all(get_affinity(m) == 'wary' for m in companions if m),
        [(m.name, get_affinity(m)) for m in companions if m],
    )

    status = rig.drive_to_pending()
    state = battle.get_battle_state()
    result = status.get('result') or {}
    rig.checks.ok(
        'the player is eventually asked to act',
        result.get('pending') == 'player_turn' and str(result.get('pending_actor')) == player_id,
        result.get('pending'),
    )

    living = len(battle.active_ids(state, 'allies')) + len(battle.active_ids(state, 'enemies'))
    turns = state.get('turn_count', 0)
    # The fairness guardrail force-picks anyone waiting this long, so the
    # player cannot be starved past it (plus one cycle of slack)
    bound = OVERDUE_WAIT_MULTIPLIER * living + living + 2
    # Only the UPPER bound is a promise: being asked immediately (zero
    # NPC turns) is a perfectly good roll, being asked never is not
    rig.checks.ok(
        f'NPC turns before the player acts stay under the fairness bound ({turns} <= {bound})',
        turns <= bound,
        {'turns': turns, 'bound': bound, 'living': living},
    )

    stub.set('battle_talk', {'response': 'Enough.', 'decision': 'enemies_yield'})
    rig.talk('Stand down.')


@scenario
def fairness_guardrail(rig: Rig, stub: ScriptedStub):
    """A director fixated on one monster cannot starve the others"""
    from backend.game.battle import manager as battle
    from backend.game.battle.constants import OVERDUE_WAIT_MULTIPLIER

    stub.script.update(STALL)
    stub.set('next_turn', pick_enemy)  # always the SAME first enemy
    rig.start_forced_battle()

    state = battle.get_battle_state()
    living = [(s, mid) for s in ('allies', 'enemies') for mid in battle.active_ids(state, s)]
    threshold = OVERDUE_WAIT_MULTIPLIER * len(living) + len(living) + 1

    # Defend until the battle has run long enough for the guardrail to
    # have cycled EVERYONE at least once (3x the overdue threshold in
    # recorded turns) - a fixed workflow count was flaky on unlucky dice
    status = rig.drive_to_pending()
    for _ in range(15):
        if battle.get_battle_state().get('turn_count', 0) >= 3 * threshold:
            break
        status = rig.defend(status)

    state = battle.get_battle_state()
    worst = max(battle.turns_waiting(state, mid) for _, mid in living)
    rig.checks.ok(
        'no living combatant starves past the overdue threshold',
        worst <= threshold,
        {'worst_wait': worst, 'threshold': threshold},
    )
    acted = {entry.get('actor') for entry in state.get('turn_history', [])}
    names = {state[s][mid]['name'] for s, mid in living}
    rig.checks.ok(
        'every living combatant has acted',
        names.issubset(acted),
        {'missing': sorted(names - acted)},
    )

    stub.set('battle_talk', {'response': 'Fine.', 'decision': 'enemies_flee'})
    rig.talk('Scatter, all of you!')


@scenario
def negotiation_tree(rig: Rig, stub: ScriptedStub):
    """Every talk decision does exactly what its word promises"""
    from backend.game.battle import manager as battle
    from backend.game.dungeon import manager as dungeon
    from backend.game.dungeon.spoils import get_run_spoils

    stub.script.update(STALL)
    stub.set('next_turn', pick_player)  # control comes straight back

    # -- continue: the battle goes on --
    rig.start_forced_battle()
    stub.set('battle_talk', {'response': 'Keep talking.', 'decision': 'continue'})
    status = rig.drive_to_pending()
    status = rig.talk('We only want to pass.')
    result = status.get('result') or {}
    rig.checks.ok(
        'continue keeps the battle alive',
        result.get('pending') == 'player_turn' and battle.get_battle_state().get('in_battle'),
    )

    # -- enemies_yield --
    stub.set('battle_talk', {'response': 'We yield.', 'decision': 'enemies_yield'})
    result = (rig.talk('Yield, and no one is hurt.').get('result')) or {}
    rig.checks.ok(
        'yield = victory/yielded',
        (result.get('outcome'), result.get('resolution')) == ('victory', 'yielded'),
        result,
    )

    # -- enemies_flee --
    run_workflow(rig.queue, 'continue_exploring', {})
    rig.start_forced_battle()
    stub.set('battle_talk', {'response': 'Run!', 'decision': 'enemies_flee'})
    status = rig.drive_to_pending()
    result = (rig.talk('Leave now while you can.').get('result')) or {}
    fled = all(e.get('fled') for e in battle.get_battle_state().get('enemies', {}).values())
    rig.checks.ok(
        'flee = victory/fled + all enemies marked fled',
        (result.get('outcome'), result.get('resolution')) == ('victory', 'fled') and fled,
        result,
    )

    # -- enemies_join: provisional recruits recorded --
    run_workflow(rig.queue, 'continue_exploring', {})
    rig.start_forced_battle()
    stub.set('battle_talk', {'response': 'We walk with you.', 'decision': 'enemies_join'})
    status = rig.drive_to_pending()
    result = (rig.talk('Walk with us instead.').get('result')) or {}
    joined = result.get('joined_names') or []
    recruits = get_run_spoils()['run_recruits']
    rig.checks.ok(
        'join = victory/joined + names',
        (result.get('outcome'), result.get('resolution')) == ('victory', 'joined') and joined,
        result,
    )
    rig.checks.ok(
        'joined recruits recorded as provisional spoils', len(recruits) >= len(joined), recruits
    )

    # -- party_spared: a defeat that ends the run --
    run_workflow(rig.queue, 'continue_exploring', {})
    rig.start_forced_battle()
    stub.set('battle_talk', {'response': 'Go. Do not return.', 'decision': 'party_spared'})
    status = rig.drive_to_pending()
    result = (rig.talk('Mercy - we are beaten.').get('result')) or {}
    rig.checks.ok(
        'spared = defeat/spared',
        (result.get('outcome'), result.get('resolution')) == ('defeat', 'spared'),
        result,
    )
    rig.checks.ok(
        'spared defeat ends the run',
        not dungeon.is_in_dungeon() and not battle.get_battle_state().get('in_battle'),
    )


@scenario
def defeat_stakes(rig: Rig, stub: ScriptedStub):
    """Going down forfeits the run's provisional spoils - memories stay"""
    from backend.game.dungeon.spoils import get_run_spoils
    from backend.models.dungeon_run import DungeonRun

    stub.script.update(STALL)
    stub.set('next_turn', pick_player)

    # Battle 1: win a recruit (and a victory keepsake) mid-run
    rig.start_forced_battle()
    stub.set('battle_talk', {'response': 'We follow.', 'decision': 'enemies_join'})
    status = rig.drive_to_pending()
    result = (rig.talk('Join us - there is a better road.').get('result')) or {}
    joined = result.get('joined_names') or []
    spoils = get_run_spoils()
    rig.checks.ok(
        'recruit + keepsake are provisional',
        bool(spoils['run_recruits']) and bool(spoils['run_cocatok_ids']),
        spoils,
    )
    recruit_ids = list(spoils['run_recruits'])

    # Battle 2: lose it all. Enemies devastate, the party only defends.
    run_workflow(rig.queue, 'continue_exploring', {})
    stub.set('enemy_turn', {'action': 'attack', 'target': '', 'ability_name': '', 'dialogue': ''})
    stub.set(
        'action_resolution',
        {
            'narration': 'The blow lands terribly.',
            'impact': 'devastating',
            'stamina_cost': 'none',
            'mana_cost': 'none',
        },
    )
    stub.set('next_turn', pick_enemy)
    rig.start_forced_battle()
    status = rig.turn({})
    for _ in range(20):
        result = status.get('result') or {}
        if result.get('outcome'):
            break
        if result.get('pending') == 'player_turn':
            status = rig.defend(status)
        elif result.get('pending') == 'player_response':
            status = rig.turn({'player_response': 'We fight on.'})
        else:
            status = rig.turn({})

    result = status.get('result') or {}
    rig.checks.ok('the party fell', result.get('outcome') == 'defeat', result)
    lost = result.get('spoils_lost') or {}
    released = set(lost.get('released_names') or [])
    rig.checks.ok('defeat released the run recruits', set(joined) <= released, lost)

    from backend.game.state.manager import get_party_monster_ids

    party = set(get_party_monster_ids())
    rig.checks.ok('released recruits left the party', not (set(recruit_ids) & party))
    from backend.models.monster_memory import MonsterMemory

    for monster_id in recruit_ids:
        broken = MonsterMemory.count_kind(monster_id, 'bond_broken')
        rig.checks.ok('released recruit keeps a bond_broken memory', broken >= 1, broken)

    latest = DungeonRun.query.order_by(DungeonRun.id.desc()).first()
    rig.checks.ok("run row closed as 'defeat'", latest is not None and latest.result == 'defeat')


@scenario
def resource_drain(rig: Rig, stub: ScriptedStub):
    """Referee cost words walk the pools down the ladder and clamp"""
    from backend.game.battle import manager as battle

    stub.script.update(STALL)
    stub.set('next_turn', pick_player)
    stub.set(
        'action_resolution',
        {
            'narration': 'A huge effort.',
            'impact': 'none',
            'stamina_cost': 'heavy',
            'mana_cost': 'none',
        },
    )
    rig.start_forced_battle()
    status = rig.drive_to_pending()

    expected = ['drained', 'spent', 'spent']  # brimming -3-> drained -3-> spent (clamped)
    for step_index, want in enumerate(expected):
        result = status.get('result') or {}
        actor = str(result.get('pending_actor'))
        enemy = battle.active_ids(battle.get_battle_state(), 'enemies')[0]
        status = rig.turn({'player_action': {'type': 'attack', 'target_id': enemy}})
        stamina = (battle.get_battle_state().get('allies', {}).get(actor) or {}).get('stamina')
        rig.checks.ok(
            f'heavy cost #{step_index + 1}: stamina lands on {want}', stamina == want, stamina
        )

    # An item turn spends a use and completes cleanly
    from backend.models.item import Item

    item = Item.query.filter(Item.uses_remaining > 0).first()
    if item is not None:
        uses_before = item.uses_remaining
        result = status.get('result') or {}
        status = rig.turn({'player_action': {'type': 'item', 'item_id': item.id}})
        from tools.playtest.rig import refresh_session

        refresh_session()
        item = Item.get_item_by_id(item.id)
        spent_or_gone = item is None or item.uses_remaining == uses_before - 1
        rig.checks.ok('item turn spends exactly one use', spent_or_gone)

    stub.set('battle_talk', {'response': 'Pause.', 'decision': 'enemies_yield'})
    rig.talk('Enough - we are spent.')


@scenario
def wary_autonomy(rig: Rig, stub: ScriptedStub):
    """Wary allies act alone; a familiar ally awaits the player's order"""
    from backend.game.player.manager import get_player_monster_id
    from backend.models.monster import Monster

    stub.script.update(STALL)
    rig.start_forced_battle()

    player_id = str(get_player_monster_id())
    status = rig.drive_to_pending()
    pendings = set()
    for _ in range(6):
        result = status.get('result') or {}
        if result.get('pending') == 'player_turn':
            pendings.add(str(result.get('pending_actor')))
            status = rig.defend(status)
        else:
            status = rig.turn({})
    rig.checks.ok('wary companions never awaited orders', pendings == {player_id}, sorted(pendings))

    # Trust changes the contract: a familiar companion awaits orders
    from backend.game.state.manager import get_party_monster_ids

    companions = [mid for mid in get_party_monster_ids() if str(mid) != player_id]
    for monster_id in companions:
        monster = Monster.get_monster_by_id(monster_id)
        monster.affinity = 'familiar'
        monster.save()

    def pick_companion(stub_instance):
        monster = Monster.get_monster_by_id(companions[0])
        return {'next': monster.name if monster else ''}

    stub.set('next_turn', pick_companion)
    pendings = set()
    for _ in range(4):
        status = rig.defend(status) if (status.get('result') or {}).get('pending') else rig.turn({})
        pending_actor = (status.get('result') or {}).get('pending_actor')
        if pending_actor is not None:
            pendings.add(str(pending_actor))
    rig.checks.ok(
        'a familiar companion now awaits orders',
        any(str(mid) in pendings for mid in companions),
        sorted(pendings),
    )

    stub.set('battle_talk', {'response': 'Done.', 'decision': 'enemies_yield'})
    rig.talk('Stand down, friends.')


# ===== MAIN =====


def main() -> int:
    from tools.playtest.gauntlet_rig import run_suite, suite_args

    args = suite_args(SCENARIOS, 'battle_gauntlet')
    return run_suite(
        '⚔️',
        SCENARIOS,
        args,
        wrap_factory=lambda: ForcedEvents(event='monster_battle', include_exit=False),
    )


if __name__ == '__main__':
    raise SystemExit(main())
