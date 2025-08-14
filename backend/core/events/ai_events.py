# AI-Specific Events - LLM and Image Generation
# Contains all AI generation events and their emission helper functions
# Separated from core event registry for better organization

from typing import Dict, Any, List
from .event_registry import register_events, _emit_from_schema

# ===== AI EVENT DEFINITIONS =====

AI_EVENTS = {
    # === LLM Generation Events (Frontend) ===
    
    'llm.generation.started': {
        'data_fields': {
            'item': 'Complete queue item data (from item.to_dict())',
            'generation_id': 'Database generation ID'
        },
        'send_to_frontend': True
    },
    
    'llm.generation.update': {
        'data_fields': {
            'generation_id': 'Database generation ID',
            'partial_text': 'Current generated text',
            'tokens_so_far': 'Number of tokens generated so far'
        },
        'send_to_frontend': True
    },
    
    'llm.generation.completed': {
        'data_fields': {
            'item': 'Complete queue item data (from item.to_dict())',
            'generation_id': 'Database generation ID',
            'result': 'Generation result data'
        },
        'send_to_frontend': True
    },
    
    'llm.generation.failed': {
        'data_fields': {
            'item': 'Complete queue item data (from item.to_dict())',
            'generation_id': 'Database generation ID',
            'error': 'Error message describing failure'
        },
        'send_to_frontend': True
    },
    
    # === Unified Queue Events ===
    
    'ai.queue.update': {
        'data_fields': {
            'all_items': 'List of all queue items [item1.to_dict(), item2.to_dict(), ...]',
            'trigger': 'What triggered the update (added, started, completed, failed)'
        },
        'send_to_frontend': True
    },
    
    # === Image Generation Events (Frontend) ===
    
    'image.generation.started': {
        'data_fields': {
            'item': 'Complete queue item data (from item.to_dict())',
            'generation_id': 'Database generation ID'
        },
        'send_to_frontend': True
    },

    'image.generation.update': {
        'data_fields': {
            'item': 'Complete queue item data (from item.to_dict())',
            'generation_id': 'Database generation ID',
            'elapsed_seconds': 'The number of seconds the image has been generating (int)'
        },
        'send_to_frontend': True
    },
    
    'image.generation.completed': {
        'data_fields': {
            'item': 'Complete queue item data (from item.to_dict())',
            'generation_id': 'Database generation ID',
            'result': 'Generation result data'
        },
        'send_to_frontend': True
    },
    
    'image.generation.failed': {
        'data_fields': {
            'item': 'Complete queue item data (from item.to_dict())',
            'generation_id': 'Database generation ID',
            'error': 'Error message describing failure'
        },
        'send_to_frontend': True
    },
    

}

# Register AI events with the core registry
register_events(AI_EVENTS)

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

# ===== UNIFIED QUEUE EVENT FUNCTION =====

def emit_ai_queue_update(all_items: List[Dict[str, Any]], trigger: str) -> bool:
    """Emit complete queue state update"""
    return _emit_from_schema('ai.queue.update',
        all_items=all_items,
        trigger=trigger
    )

# ===== IMAGE GENERATION EVENT FUNCTIONS =====

def emit_image_generation_started(item: Dict[str, Any], generation_id: int) -> bool:
    """Emit when image generation starts"""
    return _emit_from_schema('image.generation.started',
        item=item,
        generation_id=generation_id
    )

def emit_image_generation_update(item: Dict[str, Any], generation_id: int, elapsed_seconds: int) -> bool:
    """Emit streaming updates during image generation"""
    return _emit_from_schema('image.generation.update',
                             item=item,
                             generation_id=generation_id,
                             elapsed_seconds=elapsed_seconds
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