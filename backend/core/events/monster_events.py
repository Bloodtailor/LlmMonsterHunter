# Monster Domain Events - Facts About Monsters in the Game World
# Contains all monster lifecycle events and their emission helper functions
# Emitted from the generator layer (game/monster/generator.py), so every
# workflow that creates monsters/abilities/art broadcasts these automatically
print(f"🔍 Loading {__file__.split('LlmMonsterHunter', 1)[-1]}")

from typing import Dict, Any
from .event_registry import register_events, _emit_from_schema

# ===== MONSTER EVENT DEFINITIONS =====

MONSTER_EVENTS = {

    'monster.created': {
        'data_fields': {
            'monster': 'Complete monster data (from monster.to_dict())'
        },
        'send_to_frontend': True
    },

    'monster.updated': {
        'data_fields': {
            'monster': 'Complete monster data (from monster.to_dict()) after a staged-generation update'
        },
        'send_to_frontend': True
    },

    'monster.ability_added': {
        'data_fields': {
            'monster_id': 'Database ID of the monster the ability belongs to',
            'ability': 'Complete ability data (from ability.to_dict())'
        },
        'send_to_frontend': True
    },

    'monster.art_ready': {
        'data_fields': {
            'monster_id': 'Database ID of the monster the art belongs to',
            'image_path': 'Relative path to the card art image'
        },
        'send_to_frontend': True
    },

    'monster.memory_added': {
        'data_fields': {
            'monster_id': 'Database ID of the monster the memory belongs to',
            'memory': 'Complete memory data (from memory.to_dict())'
        },
        'send_to_frontend': True
    }
}

# Register monster events with the core registry
register_events(MONSTER_EVENTS)

# ===== MONSTER EVENT FUNCTIONS =====

def emit_monster_created(monster: Dict[str, Any]) -> bool:
    """Emit when a new monster is saved to the database"""
    return _emit_from_schema('monster.created',
        monster=monster
    )

def emit_monster_updated(monster: Dict[str, Any]) -> bool:
    """Emit when staged generation fills in more of an existing monster"""
    return _emit_from_schema('monster.updated',
        monster=monster
    )

def emit_monster_ability_added(monster_id: int, ability: Dict[str, Any]) -> bool:
    """Emit when a new ability is saved for a monster"""
    return _emit_from_schema('monster.ability_added',
        monster_id=monster_id,
        ability=ability
    )

def emit_monster_art_ready(monster_id: int, image_path: str) -> bool:
    """Emit when card art is generated and attached to a monster"""
    return _emit_from_schema('monster.art_ready',
        monster_id=monster_id,
        image_path=image_path
    )

def emit_monster_memory_added(monster_id: int, memory: Dict[str, Any]) -> bool:
    """Emit when a monster records a new memory of the party"""
    return _emit_from_schema('monster.memory_added',
        monster_id=monster_id,
        memory=memory
    )
