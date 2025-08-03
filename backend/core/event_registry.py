# Event Registry - Single Source of Truth for All Events
# Defines event schemas and provides structured event emission functions
# Separates frontend events (sent via SSE) from internal events
print(f"🔍 Loading {__file__}")
from dataclasses import dataclass
from typing import Dict, Any, List
from backend.core.event_bus import emit_event

@dataclass
class EventSchema:
    """Schema definition for an event type"""
    data_fields: Dict[str, str]  # field_name: field_description
    send_to_frontend: bool = True  # Whether this should go to SSE

# ===== EVENT REGISTRY =====
# Single source of truth for all events currently used in the system

EVENT_REGISTRY = {
    # === LLM Generation Events (Frontend) ===
    
    'llm.generation.started': EventSchema(
        data_fields={
            'item': 'Complete queue item data (from item.to_dict())',
            'generation_id': 'Database generation ID'
        },
        send_to_frontend=True
    ),
    
    'llm.generation.update': EventSchema(
        data_fields={
            'generation_id': 'Database generation ID',
            'partial_text': 'Current generated text',
            'tokens_so_far': 'Number of tokens generated so far'
        },
        send_to_frontend=True
    ),
    
    'llm.generation.completed': EventSchema(
        data_fields={
            'item': 'Complete queue item data (from item.to_dict())',
            'generation_id': 'Database generation ID',
            'result': 'Generation result data'
        },
        send_to_frontend=True
    ),
    
    'llm.generation.failed': EventSchema(
        data_fields={
            'item': 'Complete queue item data (from item.to_dict())',
            'generation_id': 'Database generation ID',
            'error': 'Error message describing failure'
        },
        send_to_frontend=True
    ),
    
    'llm.queue.update': EventSchema(
        data_fields={
            'action': 'What happened (added)',
            'item': 'Complete queue item data (from item.to_dict())',
            'queue_size': 'Current queue size'
        },
        send_to_frontend=True
    ),
    
    # === Image Generation Events (Frontend) ===
    
    'image.generation.started': EventSchema(
        data_fields={
            'item': 'Complete queue item data (from item.to_dict())',
            'generation_id': 'Database generation ID'
        },
        send_to_frontend=True
    ),

    'image.generation.update': EventSchema(
        data_fields={
            'item': 'Complete queue item data (from item.to_dict())',
            'generation_id': 'Database generation ID',
            'comfyui_queue_status_response': 'The response of the /queue endpoint from the comfyui server (from response.json())'
        },
        send_to_frontend=True

    ),
    
    'image.generation.completed': EventSchema(
        data_fields={
            'item': 'Complete queue item data (from item.to_dict())',
            'generation_id': 'Database generation ID',
            'result': 'Generation result data'
        },
        send_to_frontend=True
    ),
    
    'image.generation.failed': EventSchema(
        data_fields={
            'item': 'Complete queue item data (from item.to_dict())',
            'generation_id': 'Database generation ID',
            'error': 'Error message describing failure'
        },
        send_to_frontend=True
    ),
    
    'image.queue.update': EventSchema(
        data_fields={
            'action': 'What happened (added)',
            'item': 'Complete queue item data (from item.to_dict())',
            'queue_size': 'Current queue size'
        },
        send_to_frontend=True
    ),
    
    # === Workflow Events (Frontend) ===
    # Note: These are dynamic - workflow_type can be monster_basic, dungeon_entry, etc.
    
    'workflow.monster_basic.queued': EventSchema(
        data_fields={
            'workflow_id': 'Database workflow ID',
            'workflow_type': 'Type of workflow (monster_basic)',
            'queue_size': 'Current workflow queue size'
        },
        send_to_frontend=True
    ),
    
    'workflow.monster_basic.started': EventSchema(
        data_fields={
            'workflow_id': 'Database workflow ID',
            'workflow_type': 'Type of workflow (monster_basic)'
        },
        send_to_frontend=True
    ),
    
    'workflow.monster_basic.completed': EventSchema(
        data_fields={
            'workflow_id': 'Database workflow ID',
            'workflow_type': 'Type of workflow (monster_basic)',
            'result': 'Workflow execution result'
        },
        send_to_frontend=True
    ),
    
    'workflow.monster_basic.failed': EventSchema(
        data_fields={
            'workflow_id': 'Database workflow ID',
            'workflow_type': 'Type of workflow (monster_basic)',
            'error': 'Error message describing failure'
        },
        send_to_frontend=True
    ),
    
    'workflow.dungeon_entry.queued': EventSchema(
        data_fields={
            'workflow_id': 'Database workflow ID',
            'workflow_type': 'Type of workflow (dungeon_entry)',
            'queue_size': 'Current workflow queue size'
        },
        send_to_frontend=True
    ),
    
    'workflow.dungeon_entry.started': EventSchema(
        data_fields={
            'workflow_id': 'Database workflow ID',
            'workflow_type': 'Type of workflow (dungeon_entry)'
        },
        send_to_frontend=True
    ),
    
    'workflow.dungeon_entry.completed': EventSchema(
        data_fields={
            'workflow_id': 'Database workflow ID',
            'workflow_type': 'Type of workflow (dungeon_entry)',
            'result': 'Workflow execution result'
        },
        send_to_frontend=True
    ),
    
    'workflow.dungeon_entry.failed': EventSchema(
        data_fields={
            'workflow_id': 'Database workflow ID',
            'workflow_type': 'Type of workflow (dungeon_entry)',
            'error': 'Error message describing failure'
        },
        send_to_frontend=True
    )
}

# ===== HELPER FUNCTIONS =====

def _emit_from_schema(event_type: str, **kwargs) -> bool:
    """
    Helper to emit events based on schema definition
    Automatically filters kwargs to only include schema-defined fields
    
    Args:
        event_type (str): Event type from EVENT_REGISTRY
        **kwargs: Event data fields
        
    Returns:
        bool: True if event was emitted successfully
    """
    schema = EVENT_REGISTRY.get(event_type)
    if not schema:
        print(f"❌ Unknown event type: {event_type}")
        return False
    
    # Build data using only schema-defined fields
    data = {field: kwargs[field] for field in schema.data_fields.keys() if field in kwargs}
    
    # Log missing required fields in development
    missing_fields = [field for field in schema.data_fields.keys() if field not in kwargs]
    if missing_fields:
        print(f"⚠️ Event {event_type} missing fields: {missing_fields}")
    
    return emit_event(event_type, data)

def get_sse_events() -> List[str]:
    """Get only events that should be sent to frontend via SSE"""
    return [event_type for event_type, schema in EVENT_REGISTRY.items() 
            if schema.send_to_frontend]

def get_internal_events() -> List[str]:
    """Get events that are internal only (not sent to frontend)"""
    return [event_type for event_type, schema in EVENT_REGISTRY.items() 
            if not schema.send_to_frontend]

def get_all_events() -> List[str]:
    """Get all events regardless of frontend flag"""
    return list(EVENT_REGISTRY.keys())

def get_event_schema(event_type: str) -> EventSchema:
    """Get schema for a specific event type"""
    return EVENT_REGISTRY.get(event_type)

# ===== LLM GENERATION EVENT FUNCTIONS =====

def emit_llm_generation_started(item: Dict[str, Any], generation_id: int) -> bool:
    """Emit when LLM text generation starts"""
    return _emit_from_schema('llm.generation.started',
        item=item,
        generation_id=generation_id
    )

def emit_llm_generation_update(generation_id: int, partial_text: str, tokens_so_far: int) -> bool:
    """Emit streaming text updates during LLM generation"""
    return _emit_from_schema('llm.generation.update',
        generation_id=generation_id,
        partial_text=partial_text,
        tokens_so_far=tokens_so_far
    )

def emit_llm_generation_completed(item: Dict[str, Any], generation_id: int, result: Dict[str, Any]) -> bool:
    """Emit when LLM generation completes successfully"""
    return _emit_from_schema('llm.generation.completed',
        item=item,
        generation_id=generation_id,
        result=result
    )

def emit_llm_generation_failed(item: Dict[str, Any], generation_id: int, error: str) -> bool:
    """Emit when LLM generation fails"""
    return _emit_from_schema('llm.generation.failed',
        item=item,
        generation_id=generation_id,
        error=error
    )

def emit_llm_queue_update(action: str, item: Dict[str, Any], queue_size: int) -> bool:
    """Emit when LLM queue status changes"""
    return _emit_from_schema('llm.queue.update',
        action=action,
        item=item,
        queue_size=queue_size
    )

# ===== IMAGE GENERATION EVENT FUNCTIONS =====

def emit_image_generation_started(item: Dict[str, Any], generation_id: int) -> bool:
    """Emit when image generation starts"""
    return _emit_from_schema('image.generation.started',
        item=item,
        generation_id=generation_id
    )

def emit_image_generation_update(item: Dict[str, Any], generation_id: int, comfyui_queue_status_response: Dict[str, Any]) -> bool:
    """Emit streaming updates durring image generation"""
    return _emit_from_schema('image.generation.update',
                             item=item,
                             generation_id=generation_id,
                             comfyui_queue_status_response=comfyui_queue_status_response
    )

def emit_image_generation_completed(item: Dict[str, Any], generation_id: int, result: Dict[str, Any]) -> bool:
    """Emit when image generation completes successfully"""
    return _emit_from_schema('image.generation.completed',
        item=item,
        generation_id=generation_id,
        result=result
    )

def emit_image_generation_failed(item: Dict[str, Any], generation_id: int, error: str) -> bool:
    """Emit when image generation fails"""
    return _emit_from_schema('image.generation.failed',
        item=item,
        generation_id=generation_id,
        error=error
    )

def emit_image_queue_update(action: str, item: Dict[str, Any], queue_size: int) -> bool:
    """Emit when image queue status changes"""
    return _emit_from_schema('image.queue.update',
        action=action,
        item=item,
        queue_size=queue_size
    )

# ===== WORKFLOW EVENT FUNCTIONS =====

def emit_workflow_monster_basic_queued(workflow_id: int, workflow_type: str, queue_size: int) -> bool:
    """Emit when monster_basic workflow is queued"""
    return _emit_from_schema('workflow.monster_basic.queued',
        workflow_id=workflow_id,
        workflow_type=workflow_type,
        queue_size=queue_size
    )

def emit_workflow_monster_basic_started(workflow_id: int, workflow_type: str) -> bool:
    """Emit when monster_basic workflow starts"""
    return _emit_from_schema('workflow.monster_basic.started',
        workflow_id=workflow_id,
        workflow_type=workflow_type
    )

def emit_workflow_monster_basic_completed(workflow_id: int, workflow_type: str, result: Dict[str, Any]) -> bool:
    """Emit when monster_basic workflow completes"""
    return _emit_from_schema('workflow.monster_basic.completed',
        workflow_id=workflow_id,
        workflow_type=workflow_type,
        result=result
    )

def emit_workflow_monster_basic_failed(workflow_id: int, workflow_type: str, error: str) -> bool:
    """Emit when monster_basic workflow fails"""
    return _emit_from_schema('workflow.monster_basic.failed',
        workflow_id=workflow_id,
        workflow_type=workflow_type,
        error=error
    )

def emit_workflow_dungeon_entry_queued(workflow_id: int, workflow_type: str, queue_size: int) -> bool:
    """Emit when dungeon_entry workflow is queued"""
    return _emit_from_schema('workflow.dungeon_entry.queued',
        workflow_id=workflow_id,
        workflow_type=workflow_type,
        queue_size=queue_size
    )

def emit_workflow_dungeon_entry_started(workflow_id: int, workflow_type: str) -> bool:
    """Emit when dungeon_entry workflow starts"""
    return _emit_from_schema('workflow.dungeon_entry.started',
        workflow_id=workflow_id,
        workflow_type=workflow_type
    )

def emit_workflow_dungeon_entry_completed(workflow_id: int, workflow_type: str, result: Dict[str, Any]) -> bool:
    """Emit when dungeon_entry workflow completes"""
    return _emit_from_schema('workflow.dungeon_entry.completed',
        workflow_id=workflow_id,
        workflow_type=workflow_type,
        result=result
    )

def emit_workflow_dungeon_entry_failed(workflow_id: int, workflow_type: str, error: str) -> bool:
    """Emit when dungeon_entry workflow fails"""
    return _emit_from_schema('workflow.dungeon_entry.failed',
        workflow_id=workflow_id,
        workflow_type=workflow_type,
        error=error
    )