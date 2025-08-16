# Registers as a callable function for the game orchestration queue to use
print(f"🔍 Loading {__file__.split('LlmMonsterHunter', 1)[-1]}")

from backend.core.workflow_registry import register_workflow
from typing import Callable, Dict, Any

@register_workflow()
def generate_detailed_monster(context: dict, on_update: Callable[[str, Dict[str, Any]], None]) -> dict:
    """Generate detailed monster using AI with progress updates"""
    try:
        from backend.game.monster.generator import MonsterGenerator
        
        generator = MonsterGenerator()
        
        # Step 1: Started
        on_update("started", {
            "message": "Beginning monster generation process",
            "progress": 0
        })
        
        # Call existing game logic - this will make AI requests and wait for completion
        result = generator.generate_monster()
        
        # Step 2: Finished
        on_update("finished", {
            "message": "Monster generation completed successfully",
            "progress": 100,
            "monster_data": result.get('data', {}) if result.get('success') else None
        })
        
        if result.get('success'):
            return {
                'success': True,
                'monster': result.get('data', {}),
                'message': 'Monster generation completed successfully'
            }
        else:
            return {
                'success': False,
                'error': result.get('error', 'Monster generation failed'),
                'monster': None
            }
        
    except Exception as e:
        # Send error update before returning
        on_update("error", {
            "message": f"Monster generation failed: {str(e)}",
            "error": str(e)
        })
        
        return {
            'success': False,
            'error': f'Monster generation failed: {str(e)}',
            'monster': None
        }