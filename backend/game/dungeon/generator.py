# Dungeon Generator - SIMPLIFIED: No Validation
# Pure business logic - assumes all inputs are valid
# Eliminates defensive programming completely

from typing import Dict, Any
import random
from backend.game.utils import build_and_generate, build_and_stream
from backend.game.state.manager import get_party_summary
from backend.game.dungeon.events import (
    assign_random_event,
    roll_path_count,
    roll_include_exit,
    PATH_OVERGENERATE_COUNT
)
    
def generate_entry_text(workflow_name) -> Dict[str, Any]:
    """Generate entry text - assumes valid party_summary"""
    
    party_summary = get_party_summary()
    variables = {'party_summary': party_summary}
    entry_text_generation_id = build_and_stream('entry_atmosphere', workflow_name, variables)
    
    return entry_text_generation_id

def generate_random_location(workflow_name) -> Dict[str, Any]:
    """Generate location - no validation, fallback on any error"""
    
    try:
        location = build_and_generate('random_location', workflow_name)
    except Exception:
        location = _get_fallback_location()
        
    return location

def generate_location_event_text(location_name: str, workflow_name) -> Dict[str, Any]:
    """Generate event text - assumes valid location_name"""
    
    variables = {'location_name': location_name}
    location_event_text = build_and_generate('location_event', workflow_name, variables)
    
    return location_event_text

def generate_exit_text(party_summary: str, workflow_name) -> Dict[str, Any]:
    """Generate exit text - assumes valid party_summary"""
    
    variables = {'party_summary': party_summary}
    dungeon_exit_text = build_and_generate('exit_narrative', workflow_name, variables)
    
    return dungeon_exit_text

def generate_paths(location: Dict[str, Any], workflow_name: str) -> Dict[str, Dict[str, Any]]:
    """
    Generate the paths leading onward from a location
    One batch LLM call over-generates paths (later entries are more
    creative) and we keep the LAST ones. Every non-exit path gets a
    hidden random event AND a pre-generated destination location, so
    arrival displays instantly when the player chooses it
    """

    paths = {}

    count = roll_path_count()
    include_exit = roll_include_exit()

    # An exit takes one of the rolled slots
    regular_count = count - 1 if include_exit else count

    # One batch call for all paths - over-generated for variety
    generated = []
    try:
        batch = build_and_generate('path_choices', workflow_name, {
            'location_name': location.get('name', 'Unknown Location'),
            'location_description': location.get('description', ''),
            'total_count': PATH_OVERGENERATE_COUNT
        })
        raw_paths = batch.get('paths') or []
        generated = [
            p for p in raw_paths
            if isinstance(p, dict) and p.get('name') and p.get('description')
        ]
    except Exception:
        generated = []

    # Small LLMs repeat themselves early - the later entries are the
    # creative ones, so take from the END of the batch
    chosen = generated[-regular_count:] if len(generated) >= regular_count else list(generated)
    while len(chosen) < regular_count:
        chosen.append(_get_fallback_path())

    for i, path in enumerate(chosen):
        # Pre-generate where this path leads (hidden from the player)
        destination = generate_arrival_location(location, path, workflow_name)

        paths[f'path_{i + 1}'] = {
            'name': path.get('name', 'Mysterious Passage'),
            'description': path.get('description', ''),
            'type': 'path',
            'event': assign_random_event(),
            'destination': destination
        }

    if include_exit:
        variables = {
            'location_name': location.get('name', 'Unknown Location'),
            'location_description': location.get('description', '')
        }

        try:
            exit_path = build_and_generate('exit_path', workflow_name, variables)
        except Exception:
            exit_path = {
                'name': 'Stone Stairway to the Surface',
                'description': 'A familiar stone stairway leading back to the surface and the safety of the outside world.'
            }

        paths[f'path_{regular_count + 1}'] = {
            'name': exit_path.get('name', 'Way Out'),
            'description': exit_path.get('description', ''),
            'type': 'exit',
            'event': None
        }

    return paths

def generate_arrival_location(previous_location: Dict[str, Any], path: Dict[str, Any], workflow_name: str) -> Dict[str, Any]:
    """Generate the location a chosen path leads to, based on where the party came from"""

    variables = {
        'previous_location_name': previous_location.get('name', 'Unknown Location'),
        'previous_location_description': previous_location.get('description', ''),
        'path_name': path.get('name', 'Mysterious Passage'),
        'path_description': path.get('description', '')
    }

    try:
        location = build_and_generate('arrival_location', workflow_name, variables)
    except Exception:
        location = _get_fallback_location()

    return location

def generate_encounter_vanity_text(location: Dict[str, Any], workflow_name: str) -> int:
    """Queue streamed vanity text for arriving where a monster waits - returns generation_id"""

    variables = {
        'party_summary': get_party_summary(),
        'location_name': location.get('name', 'Unknown Location'),
        'location_description': location.get('description', '')
    }
    encounter_text_generation_id = build_and_stream('encounter_vanity', workflow_name, variables)

    return encounter_text_generation_id

def build_door_choices(loc1: Dict[str, Any], loc2: Dict[str, Any]) -> Dict[str, Dict[str, str]]:
    door_choices = {
        "door_1": {
            "type": "location",
            "name": loc1.get("name", "Unknown Location"),
            "description": loc1.get("description", ""),
        },
        "door_2": {
            "type": "location",
            "name": loc2.get("name", "Unknown Location"),
            "description": loc2.get("description", ""),
        },
        "door_3": {
            "type": "exit",
            "name": "Exit the Dungeon",
            "description": "A familiar stone stairway leading back to the surface and safety of the outside world.",
        },
    }

    return door_choices


def _get_fallback_path() -> Dict[str, str]:
    """Get fallback path - always works"""

    fallback_paths = [
        {
            "name": "Crumbling Archway",
            "description": "A stone archway whose carvings have long worn away, opening into darkness beyond."
        },
        {
            "name": "Narrow Crawlspace",
            "description": "A tight gap between fallen slabs, just wide enough for one adventurer at a time."
        },
        {
            "name": "Iron-Banded Door",
            "description": "A heavy wooden door reinforced with rusted iron bands, slightly ajar."
        },
        {
            "name": "Rope Ladder",
            "description": "A frayed rope ladder descending into an unlit shaft below."
        }
    ]

    return random.choice(fallback_paths)

def _get_fallback_location() -> Dict[str, str]:
    """Get fallback location - always works"""
    
    fallback_locations = [
        {
            "name": "Echoing Cavern", 
            "description": "Ancient stone walls glisten with moisture as your footsteps echo endlessly into the darkness ahead."
        },
        {
            "name": "Crystal Grove", 
            "description": "Luminescent crystals cast dancing shadows across twisted root formations that seem to pulse with inner life."
        },
        {
            "name": "Forgotten Sanctum", 
            "description": "Weathered statues stand sentinel in this abandoned temple, their eyes seeming to follow your every movement."
        },
        {
            "name": "Whispering Chamber", 
            "description": "Strange murmurs drift through the air in this circular room, though no source can be seen."
        },
        {
            "name": "Moonlit Corridor", 
            "description": "Pale light filters down through cracks in the ceiling, illuminating dust motes that dance like tiny spirits."
        }
    ]
    
    return random.choice(fallback_locations)