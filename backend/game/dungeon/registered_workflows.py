print(f"🔍 Loading {__file__.split('LlmMonsterHunter', 1)[-1]}")

# Dungeon workflows - the thin, queueable surface of the dungeon domain.
# Every function here only wires a WorkflowStep to its handler and shapes
# the error envelope; the logic lives in handlers/ (one module per event
# or action). Step names are a frontend contract - see docs/architecture.md.

from typing import Any, Callable

from backend.core.utils.responses import error_response
from backend.core.workflow_registry import register_workflow
from backend.core.workflow_steps import WorkflowStep

from . import first_run
from .handlers import camp, items_abilities, notices, paths, run_lifecycle, stealth, talk


def _step_error(step: WorkflowStep, error: Exception) -> dict:
    """The workflow error envelope: which step died, with the work so far"""
    return error_response(
        {'failed_at': step.name, 'completed_work': step.data, 'error': str(error)}
    )


@register_workflow()
def begin_first_run(context: dict, on_update: Callable[[str, dict[str, Any]], None]) -> dict:
    """
    New Game: stream the opening scene (the wish-granting premise). The
    frontend follows opening_text_generation_id, then enters the dungeon
    with first_run=true for the guided, scripted first expedition.
    """
    step = WorkflowStep(on_update)
    try:
        return first_run.run_begin_first_run(context, step)
    except Exception as e:
        return _step_error(step, e)


@register_workflow()
def generate_expedition_notices(
    context: dict, on_update: Callable[[str, dict[str, Any]], None]
) -> dict:
    """
    Write the expedition notices posted at the dungeon entrance: the LLM
    invents each notice's theme and pitch, Python rolls its danger word.
    The player's chosen notice shapes the whole run (theme + difficulty).
    """
    step = WorkflowStep(on_update)
    try:
        return notices.run_generate_notices(context, step)
    except Exception as e:
        return _step_error(step, e)


@register_workflow()
def enter_dungeon(context: dict, on_update: Callable[[str, dict[str, Any]], None]) -> dict:
    """Enter the dungeon: entry text, starting location, and first paths"""
    step = WorkflowStep(on_update)
    try:
        return run_lifecycle.run_enter_dungeon(context, step)
    except Exception as e:
        return _step_error(step, e)


@register_workflow()
def choose_path(context: dict, on_update: Callable[[str, dict[str, Any]], None]) -> dict:
    """
    Take a chosen path: generate the arrival location, then play out the
    path's hidden event (or exit the dungeon)
    """
    step = WorkflowStep(on_update)
    try:
        return paths.run_choose_path(context, step)
    except Exception as e:
        return _step_error(step, e)


@register_workflow()
def respond_to_monster(context: dict, on_update: Callable[[str, dict[str, Any]], None]) -> dict:
    """
    The party speaks to the encounter monster(s). The LLM responds in the
    monster's voice and DECIDES the outcome: keep talking, battle, let the
    party pass, reward them, punish them, or join the party.
    Also how the party opens talks with monsters found while exploring.
    """
    step = WorkflowStep(on_update)
    try:
        return talk.run_respond_to_monster(context, step)
    except Exception as e:
        return _step_error(step, e)


@register_workflow()
def sneak_past(context: dict, on_update: Callable[[str, dict[str, Any]], None]) -> dict:
    """
    Try to slip past the monsters spotted while exploring.
    The LLM judges success; failure means the monsters notice - battle.
    """
    step = WorkflowStep(on_update)
    try:
        return stealth.run_sneak_past(context, step)
    except Exception as e:
        return _step_error(step, e)


@register_workflow()
def surprise_attack(context: dict, on_update: Callable[[str, dict[str, Any]], None]) -> dict:
    """Strike first at the monsters spotted while exploring - battle on the party's terms"""
    step = WorkflowStep(on_update)
    try:
        return stealth.run_surprise_attack(context, step)
    except Exception as e:
        return _step_error(step, e)


@register_workflow()
def setup_camp(context: dict, on_update: Callable[[str, dict[str, Any]], None]) -> dict:
    """
    Set up camp in a monster-free location: streamed vanity dialogue
    between the party's monsters as they rest
    """
    step = WorkflowStep(on_update)
    try:
        return camp.run_setup_camp(context, step)
    except Exception as e:
        return _step_error(step, e)


@register_workflow()
def use_dungeon_ability(context: dict, on_update: Callable[[str, dict[str, Any]], None]) -> dict:
    """
    A party monster uses an ability on ANYTHING outside battle - a path,
    a monster, the location, or something the player describes. The LLM
    referee decides whether it does anything at all (heals land, keen
    senses reveal true hints about paths, most odd attempts fizzle).
    """
    step = WorkflowStep(on_update)
    try:
        return items_abilities.run_use_dungeon_ability(context, step)
    except Exception as e:
        return _step_error(step, e)


@register_workflow()
def use_dungeon_item(context: dict, on_update: Callable[[str, dict[str, Any]], None]) -> dict:
    """
    The party uses an inventory ITEM on anything outside battle. The LLM
    referee reads the item's description and decides what actually happens.
    One use is spent regardless of the outcome (during battle, items cost
    a turn instead - see the battle_turn workflow).
    """
    step = WorkflowStep(on_update)
    try:
        return items_abilities.run_use_dungeon_item(context, step)
    except Exception as e:
        return _step_error(step, e)


@register_workflow()
def continue_exploring(context: dict, on_update: Callable[[str, dict[str, Any]], None]) -> dict:
    """Generate fresh paths onward from the current location"""
    step = WorkflowStep(on_update)
    try:
        return run_lifecycle.run_continue_exploring(context, step)
    except Exception as e:
        return _step_error(step, e)


@register_workflow()
def condense_dungeon_log(context: dict, on_update: Callable[[str, dict[str, Any]], None]) -> dict:
    """
    Housekeeping: condense ONE batch of the oldest un-summarized dungeon
    log entries into a rolling summary. Queued by the heavier dungeon
    workflows when enough entries pile up; the sequential worker runs it
    after the player already has their result. A no-op if the run ended
    or the batch is no longer due.
    """
    step = WorkflowStep(on_update)
    try:
        return run_lifecycle.run_condense_dungeon_log(context, step)
    except Exception as e:
        return _step_error(step, e)
