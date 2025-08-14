# Workflow_gateway
# THE ONLY WAY to request any workflow exicution
# Validates workflow and context before adding to queue


from typing import Dict, Any, Optional, Callable
from .workflow_queue import get_queue
from backend.core.utils import print_error
from backend.core.workflow_registry import get_workflow, list_workflows

### for reference: _WORKFLOW_REGISTRY: Dict[str, Callable[[dict], dict]]

def request_workflow(workflow_type: str, context: Dict[str, Any] = {"content": "no content"}, priority: int = 5):
    """
    THE ONLY WAY to request workflow exicution
    
    Args:
        workflow_type (str): key for a registered workflow (ONLY REQUIRED parameter)
        context (Dict): arguments for the workflow (optional)
        priority (int): priority level for exicuting the workflow (optional)
        
    Returns:
        success: whether or not the workflow was successfully added to queue
        workflow_id: the log id of the workflow
    """

    success = False
    workflow_id = None

    # Initialize the game folder to register workflows
    from backend import game 

    fn = get_workflow(workflow_type)
    if not fn:
        print_error(f"Unknown workflow type: {workflow_type}")
        return success, workflow_id
    
    que = get_queue()

    workflow_id = que.add_workflow(workflow_type=workflow_type, context=context, priority=priority)

    if not workflow_id:
        print_error(f"Failed to add workflow to queue: {workflow_type}")
        return success, workflow_id
    else:
        success = True

    return success, workflow_id


