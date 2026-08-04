# choose_path - resolve the chosen path, then dispatch its hidden event.
# The heavy lifting lives in one module per event (exit_run, reunion,
# explore, treasure, dialogue_event, battle_event).

from typing import Any

from backend.core.utils.responses import success_response
from backend.core.utils.validation import require_keys
from backend.core.workflow_steps import WorkflowStep

from . import battle_event, dialogue_event, exit_run, explore, reunion, treasure


def run_choose_path(context: dict, step: WorkflowStep) -> dict[str, Any]:
    """
    Take a chosen path: generate the arrival location, then play out the
    path's hidden event (or exit the dungeon)
    """
    workflow_name = 'choose_path'

    from backend.game.dungeon import manager
    from backend.game.dungeon.generator import generate_arrival_location

    # Step 0 - validate required keys
    step.emit("validate_context")
    require_keys(context, ["path_id"])

    # Condense old dungeon-log entries if enough have piled up (the
    # queued workflow runs AFTER this one - the player never waits)
    manager.queue_log_condense_if_due()

    # Look up the chosen path WITH its hidden event (backend only)
    path = manager.get_path(context["path_id"])
    if not path:
        raise Exception(f"Unknown path: {context['path_id']}")

    previous_location = manager.get_current_location()

    # === EXIT BRANCH ===
    if path.get('type') == 'exit':
        return exit_run.run_exit(step, workflow_name)

    # === PATH BRANCH ===
    # Step 1 - the destination was pre-generated with the path, so
    # arrival is instant (fall back to generating for old saved paths)
    step.emit("resolve_arrival_location")
    location = path.get('destination') or generate_arrival_location(
        previous_location, path, workflow_name
    )
    manager.set_current_location(location)

    # Arriving RETIRES the junction just left: those paths belong to the
    # previous location and only continue_exploring generates new ones.
    # The frontend already funnels the player through "Continue to the
    # Paths" (arePathsReady goes false here), but the state itself kept
    # offering the stale list - a live playtester walked it, and any
    # future client could too. The state now matches the flow.
    manager.set_available_paths({})
    manager.append_dungeon_log(
        f"The party took the path '{path.get('name', 'unknown')}' and arrived at "
        f"{location.get('name', 'an unknown place')}: {location.get('description', '')}"
    )

    # Step 2 - announce the arrival location to the frontend
    step.data.update({"current_location": location})
    step.emit("location_generated")

    event = path.get('event')

    # A guided first run consumes its script one taken path at a time -
    # the NEXT junction's paths carry the story's next beat
    from backend.game.dungeon import first_run

    if first_run.is_first_run() and event == first_run.next_scripted_event():
        first_run.advance_scripted_event()

    # THE ARRIVAL IS ALREADY REAL. The party has moved and the junction
    # it left has been retired, so from here on a raised exception does
    # not "fail an action" - it strands the player in a room with no
    # encounter and nothing to click. That is precisely how a real
    # playthrough died: one ability generation returned prose instead of
    # JSON three times and the whole expedition became unplayable.
    #
    # So every event plays out inside this net. A failure costs the
    # party the ENCOUNTER, never the run: the area falls quiet, the log
    # says so, and the player walks on.
    try:
        return _play_arrival_event(event, step, location, workflow_name)
    except Exception as arrival_error:
        print(f"❌ Arrival event '{event}' failed - degrading to a quiet area: {arrival_error}")
        return _quiet_arrival(location, event, arrival_error)


def _play_arrival_event(event: str, step: WorkflowStep, location: dict, workflow_name: str):
    """Dispatch one path's hidden event"""
    from backend.game.dungeon import goal

    # === EVENT: RETURNING MONSTER (someone here remembers the party) ===
    if event == 'returning_monster':
        response = reunion.run_returning_monster(step, location, workflow_name)
        if response is not None:
            return response
        # The pool emptied since this path was generated - degrade
        # invisibly to a plain explore; events are hidden anyway
        event = 'location_explore'

    # === EVENT: LOCATION EXPLORE (the most common arrival) ===
    if event == 'location_explore':
        response = explore.run_location_explore(step, location, workflow_name)
        # A resolved arrival is a goal-check moment ("find the spring"
        # completes by ARRIVING somewhere) - never blocks the response
        goal.check_goal_progress(workflow_name)
        return response

    # === EVENT: TREASURE (a hidden item waits to be discovered) ===
    if event == 'treasure':
        response = treasure.run_treasure(step, location, workflow_name)
        goal.check_goal_progress(workflow_name)
        return response

    # === EVENT: MONSTER DIALOGUE (a monster stops the party with a question) ===
    if event == 'monster_dialogue':
        return dialogue_event.run_monster_dialogue(step, location, workflow_name)

    # === EVENT: MONSTER BATTLE ===
    if event == 'monster_battle':
        return battle_event.run_monster_battle(step, location, workflow_name)

    raise Exception(f"Unknown path event: {event}")


def _quiet_arrival(location: dict, event: str, error: Exception) -> dict[str, Any]:
    """The safety net: a real arrival whose event could not be staged.

    The party is here, the area is empty, and every onward action still
    works. A battle that failed mid-setup is cleared too - half a battle
    is worse than none.
    """
    from backend.game.battle import manager as battle
    from backend.game.dungeon import manager

    try:
        state = battle.get_battle_state()
        if state.get('in_battle') and not state.get('enemies'):
            battle.end_battle()
    except Exception as battle_error:
        print(f"❌ Could not clear a half-started battle: {battle_error}")

    manager.set_active_encounter(
        {
            'event': 'location_explore',
            'monster_ids': [],
            'monsters_present': False,
            'camped': False,
        }
    )
    manager.append_dungeon_log(
        f"The party arrived at {location.get('name', 'the new location')}, but whatever "
        f"was stirring here never took shape. The area lies quiet."
    )

    return success_response(
        {
            "event": "location_explore",
            "current_location": location,
            "monsters_present": False,
            "monster_ids": [],
            "degraded_from": event,
            "degraded_reason": str(error),
            "party_conditions": manager.get_party_conditions(),
        }
    )
