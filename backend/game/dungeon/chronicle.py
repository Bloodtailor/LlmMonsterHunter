# The Run Chronicle - every run ends as a story beat
# After EVERY run end (victory exit or defeat) one streamed "chronicle"
# scene condenses the run's log into its place in history: the goal's
# outcome, who was met, recruited, and lost, and the run number stamped
# on it. The final text persists to DungeonRun.summary - the Sanctuary
# timeline stops being a list of one-liners and becomes a saga.
# Inputs are composed from LIVE run state, so callers must queue the
# chronicle BEFORE the wipes; failures never block a run's ending.

from typing import Any, Optional

# The chronicle shares the chat reply's stream-then-await plumbing
CHRONICLE_TIMEOUT_SECONDS = 240


def queue_run_chronicle(result_word: str, workflow_name: str) -> Optional[dict[str, Any]]:
    """
    Compose the chronicle's inputs from live state and queue the streamed
    generation. Returns {'generation_id', 'run_number'} or None on any
    failure (the run's ending never waits on a broken chronicle).
    """
    try:
        from backend.game.dungeon import manager
        from backend.game.dungeon.goal import goal_snapshot
        from backend.game.dungeon.spoils import get_run_spoils
        from backend.game.state.manager import get_party_summary
        from backend.game.utils import build_and_stream
        from backend.models.dungeon_run import DungeonRun
        from backend.models.monster import Monster

        run_number = None
        run_id = manager.get_run_id()
        if run_id:
            run = DungeonRun.get_by_id(run_id)
            run_number = run.run_number if run else None

        goal = goal_snapshot()
        if goal:
            status = 'FULFILLED' if goal.get('status') == 'complete' else 'left unfinished'
            goal_line = f"The run's goal: {goal['text']} - {status}."
        else:
            goal_line = 'No goal was set for this run.'

        recruit_names = [
            monster.name
            for monster in (
                Monster.get_monster_by_id(mid) for mid in get_run_spoils()['run_recruits']
            )
            if monster
        ]
        if recruit_names:
            kept_or_lost = (
                'walking out with the party' if result_word == 'victory' else 'lost with the run'
            )
            companions_line = (
                f"Companions recruited this run: {', '.join(recruit_names)} ({kept_or_lost})."
            )
        else:
            companions_line = 'No new companions were recruited this run.'

        generation_id = build_and_stream(
            'run_chronicle',
            workflow_name,
            {
                'run_number': str(run_number or 'unknown'),
                'result_word': 'victory' if result_word == 'victory' else 'defeat',
                'party_summary': get_party_summary(),
                'goal_line': goal_line,
                'companions_line': companions_line,
                'dungeon_log': manager.get_dungeon_log_text(),
            },
        )
        return {'generation_id': generation_id, 'run_number': run_number}

    except Exception as chronicle_error:
        print(f"❌ Chronicle queueing failed (the run still ends): {chronicle_error}")
        return None


def await_run_chronicle(queued: Optional[dict[str, Any]]) -> Optional[str]:
    """
    Wait for the queued chronicle's final text (the frontend may be
    streaming it live meanwhile). Returns the text, or None on any
    failure - callers fall back to their old one-line summaries.
    """
    if not queued:
        return None
    try:
        from backend.game.chat.generator import wait_for_streamed_text

        return wait_for_streamed_text(queued['generation_id'], timeout=CHRONICLE_TIMEOUT_SECONDS)
    except Exception as chronicle_error:
        print(f"❌ Chronicle generation failed (the run still ends): {chronicle_error}")
        return None
