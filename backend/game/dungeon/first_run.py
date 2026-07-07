# The Guided First Run - the game's opening, taught by playing
# New Game streams the wish-granting-power premise, then leads the
# (possibly empty-handed) player into a calm, fixed-theme dungeon with a
# SCRIPTED event sequence: a dialogue encounter tuned winnable by words
# (the first monster is RECRUITED, not generated), one battle beside the
# new companion (wary - it fights on its own terms), then a forced exit.
# Python scripts the rolls; the LLM does everything else.

from typing import Any, Optional

from backend.core.utils.responses import success_response
from backend.core.workflow_steps import WorkflowStep
from backend.game.dungeon import run_context

# The scripted path events, consumed in order as paths are taken.
# When the list empties, every junction offers an exit.
FIRST_RUN_EVENT_SEQUENCE = ('monster_dialogue', 'monster_battle')

# The first run is always this expedition - gentle on purpose
FIRST_RUN_THEME = (
    'the welcoming upper halls - soft light through old stone, moss and '
    'quiet water, and small curious creatures that watch more than they hunt'
)
FIRST_RUN_DANGER = 'calm'

# The fixed goal; it completes the moment the first monster joins
FIRST_RUN_GOAL = 'Leave the dungeon with a new companion at your side.'

# The line that tunes the first dialogue encounter winnable by words
FIRST_RUN_DIALOGUE_HINT = (
    "IMPORTANT: This is the adventurer's VERY FIRST encounter, and the "
    "creature before them is curious and quietly lonely. It WANTS to be "
    "won over: sincere, kind words should genuinely move it, and once the "
    "party has spoken with any real sincerity, choosing to join them "
    "(join_party) is the outcome it hopes for. Do not make this a battle."
)


# ===== LIFECYCLE =====


def begin_first_run_context() -> None:
    """Open the run context for a guided first run: fixed theme, calm
    danger, the fixed goal, and the scripted event sequence"""
    from backend.game.dungeon.goal import set_fixed_goal

    run_context.begin_run_context(
        theme=FIRST_RUN_THEME, danger=FIRST_RUN_DANGER, first_run=True
    )
    context = run_context.get_run_context()
    context['first_run_events'] = list(FIRST_RUN_EVENT_SEQUENCE)
    run_context.save_run_context(context)
    set_fixed_goal(FIRST_RUN_GOAL)


def is_first_run() -> bool:
    return bool(run_context.get_run_context().get('first_run'))


def next_scripted_event() -> Optional[str]:
    """The event every path at the current junction carries (None once
    the script is spent - junctions then offer the exit)"""
    events = run_context.get_run_context().get('first_run_events') or []
    return events[0] if events else None


def advance_scripted_event() -> None:
    """A scripted path was taken - the story moves to its next beat"""
    context = run_context.get_run_context()
    events = context.get('first_run_events') or []
    if events:
        context['first_run_events'] = events[1:]
        run_context.save_run_context(context)


def dialogue_hint() -> str:
    """The winnable-by-words tuning line (empty outside the first run)"""
    return FIRST_RUN_DIALOGUE_HINT if is_first_run() else ''


def complete_first_run_if_active() -> None:
    """Called from the exit ceremony: walking out alive finishes the
    opening - home base unlocks. Never raises."""
    try:
        if not is_first_run():
            return
        from backend.game.dungeon import manager
        from backend.game.state.manager import set_first_run_complete

        set_first_run_complete()
        manager.append_dungeon_log(
            "The first expedition is complete - the adventurer walked out "
            "with a companion at their side, and the home base opened its doors."
        )
    except Exception as first_run_error:
        print(f"❌ First-run completion failed (the exit stands): {first_run_error}")


# ===== THE OPENING SCENE WORKFLOW HANDLER =====


def run_begin_first_run(context: dict, step: WorkflowStep) -> dict[str, Any]:
    """Stream the opening scene: the wish-granting premise, on screen at
    last - told about THE character the player just created. The
    frontend follows opening_text_generation_id, then enters the dungeon
    with first_run=true."""
    workflow_name = 'begin_first_run'

    from backend.game.monster.context_builder import build_monster_block
    from backend.game.player.manager import get_player_monster
    from backend.game.utils import build_and_stream

    step.emit("validate_context")

    # The opening narrates the created character by name and wish; a
    # pre-character world keeps the old nameless framing
    player = get_player_monster()
    player_details = (
        build_monster_block(player, tier='compact')
        if player is not None
        else 'A nameless adventurer carrying an unspoken wish.'
    )

    step.emit("queue_opening_scene")
    opening_text_generation_id = build_and_stream(
        'opening_scene', workflow_name, {'player_details': player_details}
    )
    step.data.update({"opening_text_generation_id": opening_text_generation_id})

    step.emit("emit_generation_id")

    return success_response({"opening_started": True})
