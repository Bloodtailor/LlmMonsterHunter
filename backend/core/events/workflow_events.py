# Workflow-Specific Events - Multi-Step Workflow Processing
# Contains all workflow events and their emission helper functions
# Separated from core event registry for better organization

from typing import Dict, Any, List
from .event_registry import register_events, _emit_from_schema

# ===== WORKFLOW EVENT DEFINITIONS =====

WORKFLOW_EVENTS = {
    # === Workflow Lifecycle Events (Frontend) ===
    
    'workflow.started': {
        'data_fields': {
            'item': 'Complete workflow item data (from item.to_dict())',
            'workflow_id': 'Database workflow ID'
        },
        'send_to_frontend': True
    },
    
    'workflow.completed': {
        'data_fields': {
            'item': 'Complete workflow item data (from item.to_dict())',
            'workflow_id': 'Database workflow ID',
            'result': 'Workflow result data'
        },
        'send_to_frontend': True
    },
    
    'workflow.failed': {
        'data_fields': {
            'item': 'Complete workflow item data (from item.to_dict())',
            'workflow_id': 'Database workflow ID',
            'error': 'Error message describing failure'
        },
        'send_to_frontend': True
    },
    
    # === Workflow Progress Events (Frontend) ===
    
    'workflow.update': {
        'data_fields': {
            'workflow_id': 'Database workflow ID',
            'workflow_type': 'Type of workflow (monster_generation, dungeon_entry, etc.)',
            'step': 'Current workflow step identifier (snake_case)',
            'data': 'Step-specific data object (generation_id, state, etc.)'
        },
        'send_to_frontend': True
    },
    
    # === Workflow Queue Events (Frontend) ===
    
    'workflow.queue.update': {
        'data_fields': {
            'all_items': 'List of all active workflow items [item1.to_dict(), item2.to_dict(), ...]',
            'trigger': 'What triggered the update (added, started, completed, failed)'
        },
        'send_to_frontend': True
    }
}

# Register workflow events with the core registry
register_events(WORKFLOW_EVENTS)

# ===== WORKFLOW LIFECYCLE EVENT FUNCTIONS =====

def emit_workflow_started(item: Dict[str, Any], workflow_id: int) -> bool:
    """Emit when workflow processing starts"""
    return _emit_from_schema('workflow.started',
        item=item,
        workflow_id=workflow_id
    )

def emit_workflow_completed(item: Dict[str, Any], workflow_id: int, result: Dict[str, Any]) -> bool:
    """Emit when workflow completes successfully"""
    return _emit_from_schema('workflow.completed',
        item=item,
        workflow_id=workflow_id,
        result=result
    )

def emit_workflow_failed(item: Dict[str, Any], workflow_id: int, error: str) -> bool:
    """Emit when workflow fails"""
    return _emit_from_schema('workflow.failed',
        item=item,
        workflow_id=workflow_id,
        error=error
    )

# ===== WORKFLOW PROGRESS EVENT FUNCTIONS =====

def emit_workflow_update(workflow_id: int, workflow_type: str, step: str, data: Dict[str, Any]) -> bool:
    """Emit workflow progress update during processing"""
    return _emit_from_schema('workflow.update',
        workflow_id=workflow_id,
        workflow_type=workflow_type,
        step=step,
        data=data
    )

# ===== WORKFLOW QUEUE EVENT FUNCTIONS =====

def emit_workflow_queue_update(all_items: List[Dict[str, Any]], trigger: str) -> bool:
    """Emit complete workflow queue state update"""
    return _emit_from_schema('workflow.queue.update',
        all_items=all_items,
        trigger=trigger
    )