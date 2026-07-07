# Between-turns housekeeping - condensing old battle-log turns into a
# rolling summary (queued by battle_turn, run by the sequential worker).

from typing import Any

from backend.core.utils.responses import success_response
from backend.core.workflow_steps import WorkflowStep


def run_condense_battle_log(context: dict, step: WorkflowStep) -> dict[str, Any]:
    """Condense ONE due batch of the oldest un-summarized battle turns"""
    workflow_name = 'condense_battle_log'

    from backend.game.battle import manager as battle
    from backend.game.utils.rolling_summary import covered_count, plan_batch, summarize_lines

    step.emit("plan_batch")
    state = battle.get_battle_state()
    if not state.get('in_battle'):
        return success_response({"condensed": False})
    log = state.get('recent_log', [])
    summaries = state.get('log_summaries', [])
    batch = plan_batch('battle_log', len(log), covered_count(summaries))
    if not batch:
        return success_response({"condensed": False})

    step.emit("condense_batch")
    start, end = batch
    prior = summaries[-1]['text'] if summaries else None
    summary_text = summarize_lines('battle_log', log[start:end], workflow_name, prior_summary=prior)
    if not summary_text:
        # The batch stays uncovered and retries at the next trigger
        return success_response({"condensed": False})

    step.emit("record_summary")
    battle.record_log_summary(end, summary_text)

    return success_response({"condensed": True, "covers_entries": end})
