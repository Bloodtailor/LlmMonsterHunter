# Dungeon Service - TRUST BOUNDARY: Validation + Delegation
# Validates all inputs and delegates to game logic
# Single source of truth for dungeon business rules

from typing import Dict, Any
from backend.game.dungeon import DungeonManager
from backend.services.validators import (
    validate_party_ready_for_dungeon,
    validate_door_choice,
    validate_in_dungeon
)
from backend.core.utils import error_response, success_response, validate_and_continue

# Create singleton manager instance
_manager = DungeonManager()

def enter_dungeon() -> Dict[str, Any]:
    """
    Enter dungeon with validation
    Trust boundary: validates party readiness, then delegates
    """
    
    # Validate party is ready
    party_validation = validate_party_ready_for_dungeon()
    error_check = validate_and_continue(party_validation)
    if error_check:
        return error_check
    
    # Delegate to game logic (no validation needed)
    return _manager.enter_dungeon()

def choose_door(door_choice: str) -> Dict[str, Any]:
    """
    Choose door with validation
    Trust boundary: validates door choice and dungeon state, then delegates
    """
    
    # Get current dungeon state
    current_state = _get_dungeon_state()
    
    # Validate in dungeon
    dungeon_validation = validate_in_dungeon()
    error_check = validate_and_continue(dungeon_validation, {'in_dungeon': False})
    if error_check:
        return error_check
    
    # Validate door choice
    available_doors = current_state.get('available_doors', [])
    door_validation = validate_door_choice(door_choice, available_doors)
    error_check = validate_and_continue(door_validation, {'in_dungeon': True})
    if error_check:
        return error_check
    
    # Delegate to game logic (no validation needed)
    return _manager.choose_door(door_choice)

def get_dungeon_state() -> Dict[str, Any]:
    """
    Get dungeon state - no validation needed
    Simple delegation to game logic
    """
    return _manager.get_dungeon_state()

def get_dungeon_status() -> Dict[str, Any]:
    """
    Get dungeon status - enhanced with party info
    Trust boundary: adds extra context for UI
    """
    
    try:
        state_result = _manager.get_dungeon_state()
        
        if not state_result['success']:
            return error_response(
                state_result.get('error', 'Failed to get dungeon state'),
                in_dungeon=False
            )
        
        if state_result['in_dungeon']:
            current_state = state_result['state']
            location_name = current_state.get('current_location', {}).get('name', 'Unknown Location')
            party_summary = current_state.get('party_summary', 'Unknown party')
            door_count = len(current_state.get('available_doors', []))
            
            return success_response({
                'in_dungeon': True,
                'location_name': location_name,
                'party_summary': party_summary,
                'door_count': door_count,
                'message': f'Currently in {location_name} with {party_summary}'
            })
        else:
            return success_response({
                'in_dungeon': False,
                'message': 'Currently at home base'
            })
        
    except Exception as e:
        return error_response(str(e), in_dungeon=False)

def _get_dungeon_state():
    """Helper to get raw dungeon state"""
    from backend.services import game_state_service
    return game_state_service.get_dungeon_state_raw()