# choose_path - resolve the chosen path, then dispatch its hidden event.
# The heavy lifting lives in one module per event (exit_run, reunion,
# explore, treasure, dialogue_event, battle_event).

from typing import Any

from backend.core.utils.validation import require_keys
from backend.core.workflow_steps import WorkflowStep

from . import battle_event, dialogue_event, exit_run, explore, reunion, treasure


def run_choose_path(context: dict, step: WorkflowStep) -> dict[str, Any]:
    """
    Take a chosen path: generate the arrival location, then play out the
    path's hidden event (or exit the dungeon)
    """
    workflow_name = 'choose_path'

    from backend.game.dungeon import goal, manager
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

    # Unknown event - shouldn't happen, but don't strand the player
    raise Exception(f"Unknown path event: {event}")
