# Ability Service - GREATLY SIMPLIFIED: Minimal Trust Boundary
# Only validates what routes absolutely cannot handle
# Eliminates all redundant error checking

from typing import Dict, Any
from backend.core.utils import success_response, error_response

def generate_ability(monster_id: int) -> Dict[str, Any]:
    """Generate ability - only validate monster exists"""

    try:
        from backend.workflow.workflow_gateway import request_workflow
        
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