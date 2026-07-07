# Events Package - Clean Imports for Event System
# Provides easy access to event bus, registry, and emission functions
print(f"🔍 Loading {__file__.split('LlmMonsterHunter', 1)[-1]}")

# Import core event bus functionality
from .event_bus import (
    EventService,
    get_event_service,
    emit_event,
    subscribe_to_event
)

# Import core registry functionality
from .event_registry import (
    EventSchema,
    register_events,
    get_sse_events,
    get_internal_events,
    get_all_events,
    get_event_schema,
    get_events_by_category
)

# Import AI event emission functions
from .ai_events import (
    emit_llm_generation_started,
    emit_llm_generation_update,
    emit_llm_generation_completed,
    emit_llm_generation_failed,
    emit_image_generation_started,
    emit_image_generation_update,
    emit_image_generation_completed,
    emit_image_generation_failed,
    emit_ai_queue_update
)

from .workflow_events import (
  emit_workflow_started,
  emit_workflow_update,
  emit_workflow_completed,
  emit_workflow_failed,
  emit_workflow_queue_update
)

# Import monster domain event emission functions
from .monster_events import (
  emit_monster_created,
  emit_monster_updated,
  emit_monster_ability_added,
  emit_monster_art_ready,
  emit_monster_memory_added
)

# Import dungeon domain event emission functions
from .dungeon_events import (
  emit_dungeon_monster_revealed
)

# Import inventory domain event emission functions
from .inventory_events import (
  emit_inventory_item_added,
  emit_inventory_item_updated,
  emit_inventory_item_consumed,
  emit_inventory_cocatok_added
)

# Import ai_events module to ensure events get registered
from . import ai_events
from . import workflow_events
from . import monster_events
from . import inventory_events
from . import dungeon_events

__all__ = [
    # Event Bus
    'EventService',
    'get_event_service',
    'emit_event',
    'subscribe_to_event',
    
    # Event Registry
    'EventSchema',
    'register_events',
    'get_sse_events',
    'get_internal_events',
    'get_all_events',
    'get_event_schema',
    'get_events_by_category',
    
    # AI Event Emission Functions
    'emit_llm_generation_started',
    'emit_llm_generation_update',
    'emit_llm_generation_completed',
    'emit_llm_generation_failed',
    'emit_image_generation_started',
    'emit_image_generation_update',
    'emit_image_generation_completed',
    'emit_image_generation_failed',
    'emit_ai_queue_update',

    # Workflow Event Emission Functions
    'emit_workflow_started',
    'emit_workflow_update',
    'emit_workflow_completed',
    'emit_workflow_failed',
    'emit_workflow_queue_update',

    # Monster Domain Event Emission Functions
    'emit_monster_created',
    'emit_monster_updated',
    'emit_monster_ability_added',
    'emit_monster_art_ready',
    'emit_monster_memory_added',

    # Dungeon Domain Event Emission Functions
    'emit_dungeon_monster_revealed',

    # Inventory Domain Event Emission Functions
    'emit_inventory_item_added',
    'emit_inventory_item_updated',
    'emit_inventory_item_consumed',
    'emit_inventory_cocatok_added'
]