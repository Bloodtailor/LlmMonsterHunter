# Monster Service - GREATLY SIMPLIFIED: Minimal Trust Boundary
# Only validates what routes absolutely cannot handle
# Eliminates all redundant error checking

from typing import Dict, Any
from backend.core.utils import success_response, error_response, validate_and_continue
from backend.workflow.workflow_gateway import request_workflow
from backend.game import monster
from .validators import validate_monster_list_params 

def generate_monster() -> Dict[str, Any]:
    """Generate monster using workflow system - queued processing"""
    
    try:
        # Request workflow execution
        success, workflow_id = request_workflow( workflow_type="generate_detailed_monster")
        
        if success:
            return success_response({'workflow_id': workflow_id})
        else:
            return error_response('Failed to queue monster generation workflow')
            
    except Exception as e:
        return error_response(f'Workflow request failed: {str(e)}')

def get_all_monsters(limit: int = None, offset: int = 0, 
                    filter_type: str = 'all', sort_by: str = 'newest') -> Dict[str, Any]:
    """Get monsters - validate complex parameters"""
    
    params_validation = validate_monster_list_params(limit, offset, filter_type, sort_by)
    error_check = validate_and_continue(params_validation)
    if error_check:
        return error_check
    
    return monster.manager.get_all_monsters(limit, offset, filter_type, sort_by)

def get_monster_stats(filter_type: str = 'all') -> Dict[str, Any]:
    """Get stats - validate filter parameter"""
    
    valid_filters = ['all', 'with_art', 'without_art']
    if filter_type not in valid_filters:
        return error_response(f'Invalid filter parameter - must be: {", ".join(valid_filters)}')
    
    return monster.manager.get_monster_stats(filter_type)

def get_monster_by_id(monster_id: int) -> Dict[str, Any]:
    """Get monster - delegate directly (routes handle integer validation)"""
    return monster.manager.get_monster_by_id(monster_id)

def generate_ability(monster_id: int) -> Dict[str, Any]:
    """Generate ability - only validate monster exists"""

    try:
        # Request workflow execution
        success, workflow_id = request_workflow(
            workflow_type="generate_ability",
            context={"monster_id": monster_id}
            )
        
        if success:
            return success_response({'workflow_id': workflow_id})
        else:
            return error_response('Failed to queue ability generation workflow')
            
    except Exception as e:
        return error_response(f'Workflow request failed: {str(e)}')