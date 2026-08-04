# Invariants the game must hold after EVERY workflow, no matter what the
# LLM answered. A violation is a finding: either the game wedged (a state
# no action can leave), lied (malformed envelope), or leaked (values off
# the word ladders). The driver logs violations with full context.

from typing import Any

from backend.game.battle.constants import CONDITION_LADDER, RESOURCE_LADDER

# Terminal phases: ending.py stamps the OUTCOME word into the phase slot
# ('victory'/'defeat') and the state stays until the player moves on
KNOWN_BATTLE_PHASES = (
    'ready',
    'awaiting_player_turn',
    'awaiting_player_response',
    'processing',
    'victory',
    'defeat',
)

# A finished workflow whose queue error is a plain STRING means the
# exception ESCAPED the workflow function and only the queue's blanket
# except saved it - dungeon/battle workflows promise to catch everything
# themselves and return {'failed_at', ...} envelopes instead.
ESCAPED_EXCEPTION = 'escaped_exception'


def check_workflow_result(status: dict[str, Any]) -> list[str]:
    """The workflow ended in a well-formed way (success or honest error)"""
    violations = []
    state = status.get('status')

    if state == 'completed':
        result = status.get('result')
        if not isinstance(result, dict) or result.get('success') is not True:
            violations.append(f"completed workflow carries a malformed result: {result!r}")

    elif state == 'failed':
        error = status.get('error')
        if isinstance(error, str) and error != 'Handler returned None':
            violations.append(
                f"{ESCAPED_EXCEPTION}: workflow raised instead of returning an envelope: {error}"
            )
        elif isinstance(error, dict) and 'failed_at' not in error:
            violations.append(f"error envelope missing failed_at: {error!r}")

    else:
        violations.append(f"workflow ended in unexpected status {state!r}")

    return violations


def check_dungeon_state() -> list[str]:
    """The run state is readable and every word sits on its ladder"""
    from backend.game.dungeon import manager

    violations = []
    state = manager.get_dungeon_state()
    if not isinstance(state, dict):
        return [f"dungeon state is not a dict: {type(state).__name__}"]

    if not state.get('in_dungeon'):
        return violations

    location = state.get('current_location')
    if not isinstance(location, dict) or not location.get('name'):
        violations.append(f"in dungeon without a usable current_location: {location!r}")

    if not isinstance(state.get('available_paths'), dict):
        violations.append("available_paths is not a dict")

    for monster_id, condition in (state.get('party_conditions') or {}).items():
        if condition not in CONDITION_LADDER:
            violations.append(f"condition off the ladder for {monster_id}: {condition!r}")

    for monster_id, pools in (state.get('party_resources') or {}).items():
        if not isinstance(pools, dict):
            violations.append(f"resources for {monster_id} not a dict: {pools!r}")
            continue
        for pool_name in ('stamina', 'mana'):
            word = pools.get(pool_name)
            if word not in RESOURCE_LADDER:
                violations.append(f"{pool_name} off the ladder for {monster_id}: {word!r}")

    return violations


def check_battle_state(after_workflow: bool) -> list[str]:
    """The battle is in a known phase - and never left mid-'processing'
    once a battle_turn workflow has returned (the wedged state the
    recovery handler exists to prevent)"""
    from backend.game.battle import manager as battle

    violations = []
    state = battle.get_battle_state()
    if not isinstance(state, dict):
        return [f"battle state is not a dict: {type(state).__name__}"]

    if not state.get('in_battle'):
        return violations

    phase = state.get('phase')
    if phase not in KNOWN_BATTLE_PHASES:
        violations.append(f"battle phase unknown: {phase!r}")
    if after_workflow and phase == 'processing':
        violations.append("battle left wedged in 'processing' after the workflow returned")

    if not state.get('allies'):
        violations.append("battle has no allies side")
    if not state.get('enemies'):
        violations.append("battle has no enemies side")

    for side in ('allies', 'enemies'):
        for entry_id, entry in (state.get(side) or {}).items():
            condition = (entry or {}).get('condition')
            if condition not in CONDITION_LADDER:
                violations.append(f"{side}/{entry_id} condition off the ladder: {condition!r}")

    return violations


def check_run_rows() -> list[str]:
    """The run history never holds two live runs at once"""
    from backend.models.dungeon_run import DungeonRun

    violations = []
    try:
        active_rows = DungeonRun.query.filter_by(result=None).count()
    except Exception as query_error:
        return [f"could not query dungeon_runs: {query_error}"]
    if active_rows > 1:
        violations.append(f"{active_rows} dungeon runs open at once")
    return violations


def check_all(after_workflow_status: dict[str, Any] = None) -> list[str]:
    """Every invariant in one sweep; workflow-result checks when given"""
    violations = []
    if after_workflow_status is not None:
        violations.extend(check_workflow_result(after_workflow_status))
    violations.extend(check_dungeon_state())
    violations.extend(check_battle_state(after_workflow=after_workflow_status is not None))
    violations.extend(check_run_rows())
    return violations
