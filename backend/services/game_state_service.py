# Game State Service - Thin Wrapper for Game Logic
# Delegates all business logic to backend/game/state/manager.py

from typing import List, Dict, Any
from backend.game import GameStateManager

# Create singleton manager instance
_manager = GameStateManager()

def get_game_state() -> Dict[str, Any]:
    """
    Get complete current game state
    Delegates to game logic layer
    """
    return _manager.get_game_state()

def add_following_monster(monster_id: int) -> Dict[str, Any]:
    """
    Add a monster to the following list
    Delegates to game logic layer
    """
    return _manager.add_following_monster(monster_id)

def remove_following_monster(monster_id: int) -> Dict[str, Any]:
    """
    Remove a monster from the following list
    Delegates to game logic layer
    """
    return _manager.remove_following_monster(monster_id)

def set_active_party(monster_ids: List[int]) -> Dict[str, Any]:
    """
    Set the active party from following monsters
    Delegates to game logic layer
    """
    return _manager.set_active_party(monster_ids)

def get_active_party() -> Dict[str, Any]:
    """
    Get current active party details
    Delegates to game logic layer
    """
    return _manager.get_active_party()

def get_following_monsters() -> Dict[str, Any]:
    """
    Get all monsters currently following the player
    Delegates to game logic layer
    """
    return _manager.get_following_monsters()

def reset_game_state() -> Dict[str, Any]:
    """
    Reset all game state to initial values (for testing)
    Delegates to game logic layer
    """
    return _manager.reset_game_state()

def is_party_ready_for_dungeon() -> bool:
    """
    Check if party is ready for dungeon (has at least 1 monster)
    Delegates to game logic layer
    """
    return _manager.is_party_ready_for_dungeon()

def get_party_summary() -> str:
    """
    Get a text summary of the current party for display/logging
    Delegates to game logic layer
    """
    return _manager.get_party_summary()

# Dungeon state management - maintain backward compatibility for dungeon service
def get_dungeon_state_raw():
    """Get raw dungeon state for dungeon service - LEGACY compatibility"""
    return _manager.get_dungeon_state_raw()

def set_dungeon_state_raw(state):
    """Set raw dungeon state for dungeon service - LEGACY compatibility"""  
    return _manager.set_dungeon_state_raw(state)

def clear_dungeon_state_raw():
    """Clear dungeon state for dungeon service - LEGACY compatibility"""
    return _manager.clear_dungeon_state_raw()

# No need for legacy variable exposure - dungeon service should use the raw methods above