# The battle_turn orchestrator - validate, resolve the player's input,
# advance until the player is needed again, then finish the battle.

from typing import Any

from backend.core.workflow_steps import WorkflowStep

from . import director, ending, player_phase
from .context import TurnContext


def run_battle_turn(context: dict, step: WorkflowStep) -> dict[str, Any]:
    """One full battle_turn: player input -> advance loop -> ending"""
    workflow_name = 'battle_turn'

    from backend.game.battle import manager as battle

    step.emit("validate_context")

    # Long battles grow the log - condense old turns if enough piled
    # up (the queued workflow runs AFTER this one)
    battle.queue_log_condense_if_due()

    state = battle.get_battle_state()
    phase = state.get('phase')
    if not state.get('in_battle') or phase not in (
        'ready',
        'awaiting_player_turn',
        'awaiting_player_response',
    ):
        raise Exception(f"Battle is not awaiting input (phase: {phase})")

    ctx = TurnContext(state, step, workflow_name)

    # ===== PHASE A: resolve the player's input =====
    outcome, resolution, joined_names = player_phase.resolve_player_input(ctx, context, phase)

    # Combat may have decided things already
    if outcome == 'unresolved':
        outcome = battle.derive_outcome(state)
        if outcome != 'unresolved':
            resolution = 'combat'

    # ===== PHASE B: advance until an ally's turn or the battle ends =====
    pending, outcome, resolution = director.advance_until_player_or_end(ctx, outcome, resolution)
    if pending is not None:
        return pending

    # ===== ENDING =====
    return ending.finish_battle(ctx, outcome, resolution, joined_names)
