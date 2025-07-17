# Registers as a callable function for the game orchestration queue to use


from backend.core.workflow_registry import workflow_task

@workflow_task()
def dungeon_entry(context: dict) -> dict:
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