print(f"🔍 Loading {__file__.split('LlmMonsterHunter', 1)[-1]}")

from backend.core.workflow_registry import register_workflow
from backend.core.utils.responses import success_response, error_response
from backend.core.utils.validation import require_keys
from typing import Callable, Dict, Any

@register_workflow()
def enter_dungeon(context: dict, on_update: Callable[[str, Dict[str, Any]], None]) -> dict:
    """Generate detailed monster using AI with progress updates"""

    workflow_name='enter_dungeon'
    # "context" should have the following keys:
    required_keys = []

    # Set the initial conditions
    step = "initialize_workflow"
    progress_data = {}

    try:
        from backend.game.dungeon.generator import generate_random_location, build_door_choices, generate_entry_text

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
        step = "generate_location_1"
        on_update(step, progress_data)
        location_1 = generate_random_location(workflow_name)
        progress_data.update({ "location_1": location_1 })

        # Step 4
        step = "generate_location_2"
        on_update(step, progress_data)
        location_2 = generate_random_location(workflow_name)
        progress_data.update({ "location_2": location_2})

        # Step 5
        step = "assemble_door_choices"
        on_update(step, progress_data)
        door_choices = build_door_choices(location_1, location_2)

        return success_response(door_choices)
        
    except Exception as e:
        return error_response({
            'failed_at': step,
            'completed_work': progress_data,
            'error': str(e)
        })