# Run Goal - each run's one objective, rolled at the entrance
# The LLM writes a themed, checkable goal; it rides in the expedition
# brief so every location leans toward it; and after each RESOLVED event
# (explore/treasure arrival, dialogue outcome, battle victory) a tiny
# referee call answers one word - no / progress / complete - with CODE
# owning the completion valve. The reward ceremony lives in exit_run.py.

import random
from typing import Any, Optional

from backend.game.dungeon.run_context import get_run_context, save_run_context

# The referee's answer words for a goal check
GOAL_ANSWERS = ('no', 'progress', 'complete')

# THE VALVE: 'complete' is ignored before this many resolved events -
# a goal can never be won at the first door (docs/tuning.md)
GOAL_MIN_EVENTS = 3

# How many recent dungeon-log entries the goal referee gets to judge by
GOAL_CHECK_LOG_TAIL = 4

# When the LLM can't write a goal, the run still gets one
_FALLBACK_GOALS = [
    "Find a place in the deep worth remembering, and learn what makes it special.",
    "Earn the trust of a creature met along the way - leave on better terms than you arrived.",
    "Recover something the dungeon has kept hidden and carry it out alive.",
]


def generate_run_goal(workflow_name: str) -> Optional[dict[str, Any]]:
    """Write this run's goal (themed via the expedition brief) and store
    it in the run context. Never raises - a run always gets a goal."""
    from backend.game.dungeon.run_context import expedition_brief
    from backend.game.state.manager import get_party_summary
    from backend.game.utils import build_and_generate

    try:
        result = build_and_generate(
            'run_goal',
            workflow_name,
            {
                'expedition_brief': expedition_brief(),
                'party_summary': get_party_summary(),
            },
        )
        text = str(result.get('goal') or '').strip()
    except Exception:
        text = ''

    if not text:
        text = random.choice(_FALLBACK_GOALS)

    context = get_run_context()
    context['goal'] = {
        'text': text[:400],
        'status': 'pending',
        'progress_notes': [],
        'events_resolved': 0,
    }
    save_run_context(context)
    return context['goal']


def set_fixed_goal(text: str) -> None:
    """A code-chosen goal (the guided first run) - no LLM call"""
    context = get_run_context()
    context['goal'] = {
        'text': str(text)[:400],
        'status': 'pending',
        'progress_notes': [],
        'events_resolved': 0,
    }
    save_run_context(context)


def complete_goal_directly(note: str) -> None:
    """Code-visible completion (the first run's goal completes the moment
    the first companion joins - no referee needed). Never raises."""
    try:
        context = get_run_context()
        goal = context.get('goal')
        if not goal or goal.get('status') == 'complete':
            return
        goal['status'] = 'complete'
        if note:
            goal.setdefault('progress_notes', []).append(str(note)[:200])
        context['goal'] = goal
        save_run_context(context)

        from backend.core.events.dungeon_events import emit_dungeon_goal_updated
        from backend.game.dungeon import manager

        manager.append_dungeon_log(f"THE RUN'S GOAL WAS FULFILLED: {goal['text']}")
        emit_dungeon_goal_updated(goal_snapshot())
    except Exception as goal_error:
        print(f"❌ Direct goal completion failed (the run continues): {goal_error}")


def goal_snapshot() -> Optional[dict[str, Any]]:
    """The goal as workflow payloads and the frontend see it"""
    goal = get_run_context().get('goal')
    if not goal or not goal.get('text'):
        return None
    return {
        'text': goal['text'],
        'status': goal.get('status', 'pending'),
        'progress_notes': list(goal.get('progress_notes', [])),
    }


def check_goal_progress(workflow_name: str) -> None:
    """
    THE GOAL REFEREE: after a resolved event, ask whether what just
    happened touched the goal. One word comes back; Python applies the
    completion valve, records progress, and announces changes over SSE.
    Never raises - a broken check never blocks the run.
    """
    try:
        context = get_run_context()
        goal = context.get('goal')
        if not goal or not goal.get('text') or goal.get('status') == 'complete':
            return

        goal['events_resolved'] = int(goal.get('events_resolved', 0)) + 1

        answer, note = _ask_referee(goal, workflow_name)

        # THE VALVE: too early to win, however sure the referee sounds
        if answer == 'complete' and goal['events_resolved'] < GOAL_MIN_EVENTS:
            answer = 'progress'

        changed = False
        if answer in ('progress', 'complete') and note:
            goal.setdefault('progress_notes', []).append(note[:200])
            changed = True
        if answer == 'complete':
            goal['status'] = 'complete'
            changed = True

        context['goal'] = goal
        save_run_context(context)

        if changed:
            from backend.core.events.dungeon_events import emit_dungeon_goal_updated
            from backend.game.dungeon import manager

            if answer == 'complete':
                manager.append_dungeon_log(
                    f"THE RUN'S GOAL WAS FULFILLED: {goal['text']} ({note or 'the moment spoke for itself'})"
                )
            elif note:
                manager.append_dungeon_log(f"A step toward the run's goal: {note}")
            emit_dungeon_goal_updated(goal_snapshot())

    except Exception as goal_error:
        print(f"❌ Goal check failed (the run continues): {goal_error}")


def _ask_referee(goal: dict[str, Any], workflow_name: str) -> tuple[str, str]:
    """One small LLM call: did what just happened touch the goal?
    Returns (validated answer word, note)."""
    from backend.game.dungeon import manager
    from backend.game.utils import build_and_generate

    recent = manager.get_dungeon_log_entries()[-GOAL_CHECK_LOG_TAIL:]
    progress_so_far = "\n".join(f"- {n}" for n in goal.get('progress_notes', [])) or "None yet."

    try:
        result = build_and_generate(
            'goal_check',
            workflow_name,
            {
                'goal_text': goal['text'],
                'recent_events': "\n".join(f"- {entry}" for entry in recent) or "Nothing yet.",
                'progress_so_far': progress_so_far,
            },
        )
        answer = str(result.get('answer', '')).strip().lower()
        note = str(result.get('note') or '').strip()
        if answer not in GOAL_ANSWERS:
            answer = 'no'
        return answer, note
    except Exception:
        # Can't judge what we can't parse - the goal simply isn't touched
        return 'no', ''
