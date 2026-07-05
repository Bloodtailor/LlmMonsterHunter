print(f"🔍 Loading {__file__.split('LlmMonsterHunter', 1)[-1]}")

from backend.core.workflow_registry import register_workflow
from backend.core.utils.responses import success_response, error_response
from backend.core.utils.validation import require_keys
from typing import Callable, Dict, Any

@register_workflow()
def enter_dungeon(context: dict, on_update: Callable[[str, Dict[str, Any]], None]) -> dict:
    """Enter the dungeon: entry text, starting location, and first paths"""

    workflow_name = 'enter_dungeon'
    # "context" should have the following keys:
    required_keys = []

    # Set the initial conditions
    step = "initialize_workflow"
    progress_data = {}

    try:
        from backend.game.dungeon.generator import generate_random_location, generate_paths, generate_entry_text
        from backend.game.dungeon import manager

        # Step 0 - validate required keys
        step = "validate_context"
        on_update(step, progress_data)
        require_keys(context, required_keys)

        # Step 1
        step = "queue_entry_text"
        on_update(step, progress_data)
        entry_text_generation_id = generate_entry_text(workflow_name)
        progress_data.update({ "entry_text_generation_id": entry_text_generation_id })

        # Step 2
        step = "emit_generation_id"
        on_update(step, progress_data)

        # Step 3
        step = "generate_starting_location"
        on_update(step, progress_data)
        location = generate_random_location(workflow_name)
        progress_data.update({ "current_location": location })

        # Step 4 - generate paths (hidden events assigned inside, never emitted)
        step = "generate_paths"
        on_update(step, progress_data)
        paths = generate_paths(location, workflow_name)

        # Step 5 - persist the dungeon run
        step = "save_dungeon_state"
        on_update(step, progress_data)
        manager.start_dungeon(location, paths)

        return success_response({
            "current_location": location,
            "paths": manager.get_public_paths()
        })

    except Exception as e:
        return error_response({
            'failed_at': step,
            'completed_work': progress_data,
            'error': str(e)
        })

@register_workflow()
def choose_path(context: dict, on_update: Callable[[str, Dict[str, Any]], None]) -> dict:
    """
    Take a chosen path: generate the arrival location, then play out the
    path's hidden event (or exit the dungeon)
    """

    workflow_name = 'choose_path'
    # "context" should have the following keys:
    required_keys = ["path_id"]

    # Set the initial conditions
    step = "initialize_workflow"
    progress_data = {}

    try:
        from backend.game.dungeon.generator import (
            generate_arrival_location,
            generate_encounter_vanity_text,
            generate_exit_text
        )
        from backend.game.dungeon import manager
        from backend.game.monster.generator import generate_contextual_monster, generate_ability, generate_card_art
        from backend.game.state.manager import get_party_summary
        from backend.game.utils import build_and_generate

        # Step 0 - validate required keys
        step = "validate_context"
        on_update(step, progress_data)
        require_keys(context, required_keys)

        # Look up the chosen path WITH its hidden event (backend only)
        path = manager.get_path(context["path_id"])
        if not path:
            raise Exception(f"Unknown path: {context['path_id']}")

        previous_location = manager.get_current_location()

        # === EXIT BRANCH ===
        if path.get('type') == 'exit':
            step = "generate_exit_text"
            on_update(step, progress_data)
            exit_text = generate_exit_text(get_party_summary(), workflow_name)

            step = "exit_dungeon"
            on_update(step, progress_data)
            manager.exit_dungeon()

            return success_response({
                "exited": True,
                "exit_text": exit_text
            })

        # === PATH BRANCH ===
        # Step 1 - where does this path lead?
        step = "generate_arrival_location"
        on_update(step, progress_data)
        location = generate_arrival_location(previous_location, path, workflow_name)
        manager.set_current_location(location)

        # Step 2 - announce the arrival location to the frontend
        step = "location_generated"
        progress_data.update({ "current_location": location })
        on_update(step, progress_data)

        # === EVENT: MONSTER RIDDLE ===
        event = path.get('event')
        if event == 'monster_riddle':

            # Step 3 - queue streamed vanity text
            step = "queue_encounter_text"
            on_update(step, progress_data)
            encounter_text_generation_id = generate_encounter_vanity_text(location, workflow_name)
            progress_data.update({ "encounter_text_generation_id": encounter_text_generation_id })

            # Step 4 - frontend picks the generation id up from this step
            step = "emit_generation_id"
            on_update(step, progress_data)

            # Step 5 - the monster that dwells here (emits monster.created)
            step = "generate_encounter_monster"
            on_update(step, progress_data)
            monster = generate_contextual_monster(location)
            progress_data.update({ "monster_id": monster.id })

            # Steps 6-7 - abilities (emit monster.ability_added)
            step = "generate_first_ability"
            on_update(step, progress_data)
            generate_ability(monster)

            step = "generate_second_ability"
            on_update(step, progress_data)
            generate_ability(monster)

            # Step 8 - card art, full reveal before the riddle (emits monster.art_ready)
            step = "generate_card_art"
            on_update(step, progress_data)
            generate_card_art(monster)

            # Step 9 - the riddle (answer NEVER leaves the backend)
            step = "generate_riddle"
            on_update(step, progress_data)
            riddle_data = build_and_generate('riddle', workflow_name, {
                'monster_name': monster.name,
                'monster_species': monster.species,
                'monster_description': monster.description
            })

            manager.set_active_encounter({
                'event': 'monster_riddle',
                'monster_id': monster.id,
                'riddle': riddle_data['riddle'],
                'answer': riddle_data['answer']
            })

            return success_response({
                "event": "monster_riddle",
                "current_location": location,
                "monster_id": monster.id,
                "riddle": riddle_data['riddle']
            })

        # Unknown event - shouldn't happen, but don't strand the player
        raise Exception(f"Unknown path event: {event}")

    except Exception as e:
        return error_response({
            'failed_at': step,
            'completed_work': progress_data,
            'error': str(e)
        })

@register_workflow()
def answer_riddle(context: dict, on_update: Callable[[str, Dict[str, Any]], None]) -> dict:
    """Judge the player's riddle answer semantically via the LLM"""

    workflow_name = 'answer_riddle'
    # "context" should have the following keys:
    required_keys = ["player_answer"]

    # Set the initial conditions
    step = "initialize_workflow"
    progress_data = {}

    try:
        from backend.game.dungeon import manager
        from backend.game.utils import build_and_generate

        # Step 0 - validate required keys
        step = "validate_context"
        on_update(step, progress_data)
        require_keys(context, required_keys)

        encounter = manager.get_active_encounter()
        if not encounter:
            raise Exception("No active encounter to answer")

        # Step 1 - LLM judges the answer (leniently, semantically)
        step = "judge_answer"
        on_update(step, progress_data)
        judgement = build_and_generate('riddle_judgement', workflow_name, {
            'riddle': encounter['riddle'],
            'correct_answer': encounter['answer'],
            'player_answer': context['player_answer']
        })

        # Step 2 - the encounter is resolved either way
        step = "resolve_encounter"
        on_update(step, progress_data)
        manager.clear_active_encounter()

        return success_response({
            "correct": bool(judgement.get('correct')),
            "verdict": judgement.get('verdict', '')
        })

    except Exception as e:
        return error_response({
            'failed_at': step,
            'completed_work': progress_data,
            'error': str(e)
        })

@register_workflow()
def continue_exploring(context: dict, on_update: Callable[[str, Dict[str, Any]], None]) -> dict:
    """Generate fresh paths onward from the current location"""

    workflow_name = 'continue_exploring'
    # "context" should have the following keys:
    required_keys = []

    # Set the initial conditions
    step = "initialize_workflow"
    progress_data = {}

    try:
        from backend.game.dungeon.generator import generate_paths
        from backend.game.dungeon import manager

        # Step 0 - validate required keys
        step = "validate_context"
        on_update(step, progress_data)
        require_keys(context, required_keys)

        location = manager.get_current_location()
        if not location:
            raise Exception("Not currently in a dungeon")

        # Step 1 - new paths from here (hidden events assigned inside)
        step = "generate_paths"
        on_update(step, progress_data)
        paths = generate_paths(location, workflow_name)
        manager.set_available_paths(paths)

        return success_response({
            "current_location": location,
            "paths": manager.get_public_paths()
        })

    except Exception as e:
        return error_response({
            'failed_at': step,
            'completed_work': progress_data,
            'error': str(e)
        })
