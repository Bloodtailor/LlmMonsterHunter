print(f"🔍 Loading {__file__.split('LlmMonsterHunter', 1)[-1]}")

# Battle workflows - the thin, queueable surface of the battle domain.
# The turn itself lives in turn/ (context, actions, negotiation,
# player_phase, director, ending, run). Step names, action_resolved
# payloads, and response shapes are a frontend contract - see
# docs/architecture.md.

from typing import Any, Callable

from backend.core.utils.responses import error_response
from backend.core.workflow_registry import register_workflow
from backend.core.workflow_steps import WorkflowStep

from .turn import housekeeping, run


def _step_error(step: WorkflowStep, error: Exception) -> dict:
    """The workflow error envelope: which step died, with the work so far"""
    return error_response(
        {'failed_at': step.name, 'completed_work': step.data, 'error': str(error)}
    )


@register_workflow()
def battle_turn(context: dict, on_update: Callable[[str, dict[str, Any]], None]) -> dict:
    """
    Process battle turns, one monster at a time. Resolves the player's
    input (an ally's turn or a reply to enemy talk), then advances -
    the LLM directs turn order - resolving enemy turns until it is an
    ally's turn again, someone starts talking, or the battle ends.
    """
    step = WorkflowStep(on_update)
    try:
        return run.run_battle_turn(context, step)

    except Exception as e:
        # Unstick the battle so the player can retry
        try:
            from backend.game.battle import manager as battle

            recovery = battle.get_battle_state()
            if recovery.get('in_battle') and recovery.get('phase') == 'processing':
                if recovery.get('pending_talk'):
                    recovery['phase'] = 'awaiting_player_response'
                elif recovery.get('pending_actor'):
                    recovery['phase'] = 'awaiting_player_turn'
                else:
                    recovery['phase'] = 'ready'
                battle.save_battle_state(recovery)
        except Exception:
            pass

        return _step_error(step, e)


@register_workflow()
def condense_battle_log(context: dict, on_update: Callable[[str, dict[str, Any]], None]) -> dict:
    """
    Housekeeping: condense ONE batch of the oldest un-summarized battle
    log turns into a rolling summary. Queued by battle_turn when enough
    turns pile up; the sequential worker runs it between turns. A no-op
    if the battle ended or the batch is no longer due.
    """
    step = WorkflowStep(on_update)
    try:
        return housekeeping.run_condense_battle_log(context, step)
    except Exception as e:
        return _step_error(step, e)
