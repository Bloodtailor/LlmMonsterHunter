# Registers as a callable function for the game orchestration queue to use
print("🔍 Loading monster workflow")

from backend.core.workflow_registry import workflow_task

@workflow_task()
def monster_basic(context: dict) -> dict:
    """ generate basic monster using AI """
    try:
        from backend.game.monster.generator import MonsterGenerator
        
        generator = MonsterGenerator()
        
        # Call existing game logic - this will make AI requests and wait for completion
        result = generator.generate_monster()
        
        return result
        
    except Exception as e:
        return {
            'success': False,
            'error': f'Monster generation failed: {str(e)}',
            'monster': None
        }
        
        