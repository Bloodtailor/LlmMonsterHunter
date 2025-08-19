# Dungeon Generator - SIMPLIFIED: No Validation
# Pure business logic - assumes all inputs are valid
# Eliminates defensive programming completely

from typing import Dict, Any
import random
from backend.game.utils import build_and_generate
    
def generate_entry_text(party_summary: str) -> Dict[str, Any]:
    """Generate entry text - assumes valid party_summary"""
    
    variables = {'party_summary': party_summary}
    dungeon_entry_text = build_and_generate('entry_atmosphere', 'dungeon_generation', variables)
    
    return dungeon_entry_text

def generate_random_location() -> Dict[str, Any]:
    """Generate location - no validation, fallback on any error"""
    
    try:
        location_data = build_and_generate('random_location', 'dungeon_generation')
        location = {
            'name': location_data['name'],
            'description': location_data['description']
        }
        return location
            
    except Exception:
        # Always succeed with fallback
        fallback_location = _get_fallback_location()
        return fallback_location

def generate_location_event_text(location_name: str) -> Dict[str, Any]:
    """Generate event text - assumes valid location_name"""
    
    variables = {'location_name': location_name}
    location_event_text = build_and_generate('location_event', 'dungeon_generation', variables)
    
    return location_event_text

def generate_exit_text(party_summary: str) -> Dict[str, Any]:
    """Generate exit text - assumes valid party_summary"""
    
    variables = {'party_summary': party_summary}
    dungeon_exit_text = build_and_generate('exit_narrative', 'dungeon_generation', variables)
    
    return dungeon_exit_text

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