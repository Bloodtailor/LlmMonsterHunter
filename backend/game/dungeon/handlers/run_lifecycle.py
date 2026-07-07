# Run lifecycle - entering the dungeon, finding fresh paths onward, and
# the queued housekeeping that condenses the run's log.

from typing import Any

from backend.core.utils.responses import success_response
from backend.core.utils.validation import require_keys
from backend.core.workflow_steps import WorkflowStep


def run_enter_dungeon(context: dict, step: WorkflowStep) -> dict[str, Any]:
    """Enter the dungeon: entry text, starting location, and first paths"""
    workflow_name = 'enter_dungeon'

    from backend.game.battle import manager as battle_manager
    from backend.game.dungeon import manager, run_context
    from backend.game.dungeon.generator import (
        generate_entry_text,
        generate_paths,
        generate_random_location,
    )
    from backend.game.state.manager import get_party_monster_ids, get_party_summary

    # Step 0 - validate required keys
    step.emit("validate_context")
    require_keys(context, [])

    # A fresh run starts clean: any stale battle from a previous run
    # is cleared (start_dungeon below resets the dungeon state and log)
    battle_manager.end_battle()

    # The chosen expedition notice (validated by the service) shapes this
    # whole run. Its theme and danger enter the run context BEFORE any
    # generation, so even the starting location is already themed.
    notice = context.get('notice') or {}
    run_context.begin_run_context(theme=notice.get('theme'), danger=notice.get('danger'))
    run_context.clear_pending_notices()

    # A leftover run (the player walked away mid-run) still deserves
    # its place in the chat context - snapshot its log before begin()
    # closes it and start_dungeon wipes it
    if manager.is_in_dungeon():
        manager.snapshot_last_run_log('abandoned')

    # Open this run's row in the run history (closes any dangling
    # active run as 'abandoned' first)
    from backend.models.dungeon_run import DungeonRun

    run = DungeonRun.begin()

    # Step 1
    step.emit("queue_entry_text")
    entry_text_generation_id = generate_entry_text(workflow_name)
    step.data.update({"entry_text_generation_id": entry_text_generation_id})

    # Step 2
    step.emit("emit_generation_id")

    # Step 2.5 - the run's goal, BEFORE the first location generates, so
    # even the starting location can lean toward it (rides in the brief)
    from backend.game.dungeon import goal as run_goal

    step.emit("generate_run_goal")
    run_goal.generate_run_goal(workflow_name)

    # Step 3
    step.emit("generate_starting_location")
    location = generate_random_location(workflow_name)
    step.data.update({"current_location": location})

    # Step 4 - generate paths (hidden events assigned inside, never emitted)
    step.emit("generate_paths")
    paths = generate_paths(location, workflow_name)

    # Step 5 - persist the dungeon run, party starts the run fresh
    step.emit("save_dungeon_state")
    manager.start_dungeon(location, paths, run_id=run.id if run else None)

    party_conditions = {str(monster_id): 'fresh' for monster_id in get_party_monster_ids()}
    manager.set_party_conditions(party_conditions)

    # Stamina and mana come back full ONLY here - entering the
    # dungeon is the one guaranteed reset of the party's reserves
    from backend.game.battle.constants import full_resources

    party_resources = {str(monster_id): full_resources() for monster_id in get_party_monster_ids()}
    manager.set_party_resources(party_resources)

    # The run's story begins
    if notice:
        manager.append_dungeon_log(
            f"The party answered an expedition notice: '{notice.get('title', 'Unnamed')}' "
            f"({notice.get('theme', 'no theme')}; danger: {notice.get('danger', 'unknown')})."
        )
    goal_state = run_goal.goal_snapshot()
    if goal_state:
        manager.append_dungeon_log(f"The party set out with a goal: {goal_state['text']}")
    manager.append_dungeon_log(
        f"The party ({get_party_summary()}) entered the dungeon and arrived at "
        f"{location.get('name', 'an unknown place')}: {location.get('description', '')}"
    )

    return success_response(
        {
            "current_location": location,
            "paths": manager.get_public_paths(),
            "party_conditions": party_conditions,
            "party_resources": party_resources,
            "expedition": {
                "theme": notice.get('theme'),
                "danger": notice.get('danger'),
                "title": notice.get('title'),
            }
            if notice
            else None,
            "goal": goal_state,
        }
    )


def run_continue_exploring(context: dict, step: WorkflowStep) -> dict[str, Any]:
    """Generate fresh paths onward from the current location"""
    workflow_name = 'continue_exploring'

    from backend.game.battle import manager as battle_manager
    from backend.game.dungeon import manager
    from backend.game.dungeon.generator import generate_paths

    # Step 0 - validate required keys
    step.emit("validate_context")
    require_keys(context, [])

    # Moving on - condense old dungeon-log entries if due
    manager.queue_log_condense_if_due()

    # A finished battle is over once the party moves on, and a
    # resolved encounter (explored area, ended conversation) is left behind
    battle_manager.end_battle()
    manager.clear_active_encounter()

    location = manager.get_current_location()
    if not location:
        raise Exception("Not currently in a dungeon")

    # Step 1 - new paths from here (hidden events assigned inside)
    step.emit("generate_paths")
    paths = generate_paths(location, workflow_name)
    manager.set_available_paths(paths)

    path_names = ', '.join(p.get('name', 'unknown') for p in paths.values())
    manager.append_dungeon_log(
        f"The party looked for ways onward from {location.get('name', 'the area')}. "
        f"Paths ahead: {path_names}."
    )

    return success_response(
        {
            "current_location": location,
            "paths": manager.get_public_paths(),
            "party_conditions": manager.get_party_conditions(),
        }
    )


def run_condense_dungeon_log(context: dict, step: WorkflowStep) -> dict[str, Any]:
    """
    Housekeeping: condense ONE batch of the oldest un-summarized dungeon
    log entries into a rolling summary. Queued by the heavier dungeon
    workflows when enough entries pile up; the sequential worker runs it
    after the player already has their result. A no-op if the run ended
    or the batch is no longer due.
    """
    workflow_name = 'condense_dungeon_log'

    from backend.game.dungeon import manager
    from backend.game.utils.rolling_summary import covered_count, plan_batch, summarize_lines

    step.emit("plan_batch")
    entries = manager.get_dungeon_log_entries()
    summaries = manager.get_dungeon_log_summaries()
    batch = plan_batch('dungeon_log', len(entries), covered_count(summaries))
    if not batch:
        return success_response({"condensed": False})

    step.emit("condense_batch")
    start, end = batch
    prior = summaries[-1]['text'] if summaries else None
    summary_text = summarize_lines(
        'dungeon_log', entries[start:end], workflow_name, prior_summary=prior
    )
    if not summary_text:
        # The batch stays uncovered and retries at the next trigger
        return success_response({"condensed": False})

    step.emit("record_summary")
    manager.record_dungeon_log_summary(end, summary_text)

    return success_response({"condensed": True, "covers_entries": end})
