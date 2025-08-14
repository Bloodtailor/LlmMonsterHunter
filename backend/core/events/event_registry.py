# Core Event Registry - Event System Foundation
# Provides the base event registration and emission framework
# Individual event modules (ai_events.py, dungeon_events.py, etc.) register their events here

from dataclasses import dataclass
from typing import Dict, Any, List
from .event_bus import emit_event

@dataclass
class EventSchema:
    """Schema definition for an event type"""
    data_fields: Dict[str, str]  # field_name: field_description
    send_to_frontend: bool = True  # Whether this should go to SSE

# ===== CORE EVENT REGISTRY =====
# Central registry where all event modules register their events

EVENT_REGISTRY: Dict[str, EventSchema] = {}

def register_events(events: Dict[str, Dict[str, Any]]) -> None:
    """
    Register a collection of events with the core registry
    Used by event modules (ai_events.py, dungeon_events.py, etc.) to register their events
    
    Args:
        events (dict): Dictionary of event_type -> event_definition
    """
    global EVENT_REGISTRY
    
    for event_type, event_def in events.items():
        schema = EventSchema(
            data_fields=event_def['data_fields'],
            send_to_frontend=event_def.get('send_to_frontend', True)
        )
        EVENT_REGISTRY[event_type] = schema

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

# ===== REGISTRY QUERY FUNCTIONS =====

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

def get_events_by_category(category_prefix: str) -> List[str]:
    """
    Get events that start with a specific category prefix
    
    Args:
        category_prefix (str): Event category prefix (e.g., 'llm.', 'image.', 'dungeon.')
        
    Returns:
        list: Event types matching the category
    """
    return [event_type for event_type in EVENT_REGISTRY.keys() 
            if event_type.startswith(category_prefix)]