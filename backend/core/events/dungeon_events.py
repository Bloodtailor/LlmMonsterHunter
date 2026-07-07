# Dungeon Domain Events - Facts About the Current Run
# Emitted from the dungeon game layer when the run stages something the
# frontend cannot learn from monster.created (which only fires for NEW
# monsters) - e.g. a remembered monster stepping back into the story.
print(f"🔍 Loading {__file__.split('LlmMonsterHunter', 1)[-1]}")

from typing import Any

from .event_registry import _emit_from_schema, register_events

# ===== DUNGEON EVENT DEFINITIONS =====

DUNGEON_EVENTS = {

    'dungeon.monster_revealed': {
        'data_fields': {
            'monster': 'Complete monster data for a PRE-EXISTING monster staged into the current encounter (returning monsters and blend-ins; new monsters arrive via monster.created)'
        },
        'send_to_frontend': True
    }
}

# Register dungeon events with the core registry
register_events(DUNGEON_EVENTS)

# ===== DUNGEON EVENT FUNCTIONS =====

def emit_dungeon_monster_revealed(monster: dict[str, Any]) -> bool:
    """Emit when an existing monster is staged into the active encounter"""
    return _emit_from_schema('dungeon.monster_revealed',
        monster=monster
    )
