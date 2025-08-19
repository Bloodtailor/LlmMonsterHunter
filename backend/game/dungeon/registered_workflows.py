print(f"🔍 Loading {__file__.split('LlmMonsterHunter', 1)[-1]}")

from backend.core.workflow_registry import register_workflow
from backend.core.utils.responses import success_response, error_response
from backend.core.utils.validation import require_keys
from typing import Callable, Dict, Any

@register_workflow()
def generate_door_choices(context: dict, on_update: Callable[[str, Dict[str, Any]], None]) -> dict:
    """Generate detailed monster using AI with progress updates"""

    # "context" should have the following keys:
    required_keys = []

    # Set the initial conditions
    step = "initializing"
    progress_data = {}

    try:
        from backend.game.dungeon.generator import generate_random_location, build_door_choices

        # Step 0 - validate required keys
        step = "validating_context"
        on_update(step, progress_data)
        require_keys(context, required_keys)

        # Step 1
        step = "generate_location_1"
        on_update(step, progress_data)
        location_1 = generate_random_location()
        progress_data.update({ "location_1": location_1 })

        # Step 2
        step = "generate_location_2"
        on_update(step, progress_data)
        location_2 = generate_random_location()
        progress_data.update({ "location_2": location_2})

        # Step 3
        step = "assembling_door_choices"
        on_update(step, progress_data)
        door_choices = build_door_choices(location_1, location_2)
        progress_data.update({ "door_choices": door_choices})

        # Step 4
        step = "sending_success_response"
        on_update(step, progress_data)

        return success_response(door_choices)
        
    except Exception as e:
        return error_response({
            'failed_at': step,
            'completed_work': progress_data,
            'error': str(e)
        })