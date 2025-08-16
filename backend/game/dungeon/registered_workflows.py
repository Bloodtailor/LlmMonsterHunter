# Registers as a callable function for the game orchestration queue to use

print(f"🔍 Loading {__file__.split('LlmMonsterHunter', 1)[-1]}")
from backend.core.workflow_registry import register_workflow

@register_workflow()
def dungeon_entry(context: dict, on_update) -> dict:
    """Handle dungeon entry workflow by calling existing DungeonManager"""    
    try:
        from backend.game.dungeon.manager import DungeonManager
        
        manager = DungeonManager()
        
        # Call existing game logic - this will make AI requests and wait for completion
        result = manager.enter_dungeon()
        
        return result
        
    except Exception as e:
        return {
            'success': False,
            'error': f'Dungeon entry failed: {str(e)}',
            'dungeon_entered': False
        }