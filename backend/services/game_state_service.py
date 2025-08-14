# Game State Service - TRUST BOUNDARY: Validation + Delegation
# Validates all inputs and delegates to game logic
# Single source of truth for game state business rules

from typing import List, Dict, Any
from backend.game.state import GameStateManager
from backend.services.validators import (
    validate_party_size,
    validate_monsters_are_following,
    validate_following_monster_addition,
    validate_following_monster_removal
)
from backend.core.utils import error_response, success_response, validate_and_continue

# Create singleton manager instance
_manager = GameStateManager()

def get_game_state() -> Dict[str, Any]:
    """
    Get complete current game state
    No validation needed - simple delegation to game logic
    """
    return _manager.get_game_state()

def add_following_monster(monster_id: int) -> Dict[str, Any]:
    """
    Add a monster to the following list
    Trust boundary: validates monster exists and isn't already following
    """
    
    # Validate monster exists and isn't already following
    monster_validation = validate_following_monster_addition(monster_id)
    error_check = validate_and_continue(monster_validation, {'following_count': 0})
    if error_check:
        return error_check
    
    # Delegate to game logic (no validation needed)
    return _manager.add_following_monster(monster_id)

def remove_following_monster(monster_id: int) -> Dict[str, Any]:
    """
    Remove a monster from the following list
    Trust boundary: validates monster exists and is actually following
    """
    
    # Validate monster exists and is following
    monster_validation = validate_following_monster_removal(monster_id)
    error_check = validate_and_continue(monster_validation, {'following_count': 0})
    if error_check:
        return error_check
    
    # Delegate to game logic (no validation needed)
    return _manager.remove_following_monster(monster_id)

def set_active_party(monster_ids: List[int]) -> Dict[str, Any]:
    """
    Set the active party from following monsters
    Trust boundary: validates party size and that all monsters are following
    """
    
    # Validate party size constraints
    party_validation = validate_party_size(monster_ids, max_size=4)
    error_check = validate_and_continue(party_validation, {'party_count': 0})
    if error_check:
        return error_check
    
    unique_ids = party_validation['unique_ids']
    
    # Validate all monsters are following
    following_validation = validate_monsters_are_following(unique_ids)
    error_check = validate_and_continue(following_validation, {'party_count': 0})
    if error_check:
        return error_check
    
    # Delegate to game logic (no validation needed)
    return _manager.set_active_party(unique_ids)

def get_active_party() -> Dict[str, Any]:
    """
    Get current active party details
    No validation needed - simple delegation to game logic
    """
    return _manager.get_active_party()

def get_following_monsters() -> Dict[str, Any]:
    """
    Get all monsters currently following the player
    No validation needed - simple delegation to game logic
    """
    return _manager.get_following_monsters()

def reset_game_state() -> Dict[str, Any]:
    """
    Reset all game state to initial values (for testing)
    No validation needed - simple delegation to game logic
    """
    return _manager.reset_game_state()

def is_party_ready_for_dungeon() -> bool:
    """
    Check if party is ready for dungeon (has at least 1 monster)
    No validation needed - simple delegation to game logic
    """
    return _manager.is_party_ready_for_dungeon()

def get_party_summary() -> str:
    """
    Get a text summary of the current party for display/logging
    No validation needed - simple delegation to game logic
    """
    return _manager.get_party_summary()

# === Dungeon state management - maintain backward compatibility ===

def get_dungeon_state_raw():
    """Get raw dungeon state for dungeon service - LEGACY compatibility"""
    return _manager.get_dungeon_state_raw()

def set_dungeon_state_raw(state):
    """Set raw dungeon state for dungeon service - LEGACY compatibility"""  
    return _manager.set_dungeon_state_raw(state)

def clear_dungeon_state_raw():
    """Clear dungeon state for dungeon service - LEGACY compatibility"""
    return _manager.clear_dungeon_state_raw()