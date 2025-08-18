# Registers as a callable function for the game orchestration queue to use
print(f"🔍 Loading {__file__.split('LlmMonsterHunter', 1)[-1]}")

from backend.core.workflow_registry import register_workflow
from backend.core.utils.responses import success_response, error_response
from backend.core.utils.validation import require_keys
from typing import Callable, Dict, Any

@register_workflow()
def generate_detailed_monster(context: dict, on_update: Callable[[str, Dict[str, Any]], None]) -> dict:
    """Generate detailed monster using AI with progress updates"""

    step = "initializing"
    progress_data = {}

    try:
        from backend.game.monster.generator import MonsterGenerator
        
        monster_generator = MonsterGenerator()
        
        # Step 1
        step = "creating_monster"
        on_update(step, progress_data)
        monster = monster_generator.generate_base_monster()
        progress_data.update({ "monster": monster.to_dict()})

        # Step 2
        step = "adding_first_ability"
        on_update(step, progress_data)
        ability_1 = monster_generator.generate_ability(monster)
        progress_data.update({ "ability_1": ability_1.to_dict()})

        # Step 3
        step = "adding_second_ability"
        on_update(step, progress_data)
        ability_2 = monster_generator.generate_ability(monster)
        progress_data.update({ "ability_2": ability_2.to_dict()})

        # Step 4
        step = "creating_card_art"
        on_update(step, progress_data)
        image_path = monster_generator.generate_card_art(monster)
        progress_data.update({ "card_art_path": image_path})

        return success_response(progress_data)
        
    except Exception as e:
        
        return error_response({
            'failed_at': step,
            'completed_work': progress_data,
            'error': str(e)
        })
    

@register_workflow()
def generate_ability(context: dict, on_update: Callable[[str, Dict[str, Any]], None]) -> dict:
    """Generate detailed monster using AI with progress updates"""

    # "context" should have the following keys:
    required_keys = ["monster_id"]

    # Set the initial conditions
    step = "initializing"
    progress_data = {}

    try:
        from backend.game.monster.generator import MonsterGenerator
        monster_generator = MonsterGenerator()

        # Step 0 - validate required keys
        step = "validating_context"
        on_update(step, progress_data)
        require_keys(context, required_keys)

        # Step 1
        step = "generating_ability"
        on_update(step, progress_data)
        ability = monster_generator.generate_ability_by_id(context["monster_id"])
        progress_data.update({ "ability": ability.to_dict()})

        return success_response(progress_data)
        
    except Exception as e:
        
        return error_response({
            'failed_at': step,
            'completed_work': progress_data,
            'error': str(e)
        })