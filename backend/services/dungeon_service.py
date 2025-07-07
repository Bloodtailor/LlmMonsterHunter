# Dungeon Service - Thin Wrapper for Game Logic
# Delegates all business logic to backend/game/dungeon/

from typing import Dict, Any
from backend.game import DungeonManager

# Create singleton manager instance
_manager = DungeonManager()

def enter_dungeon() -> Dict[str, Any]:
    """
    Start a dungeon adventure
    Delegates to game logic layer
    """
    return _manager.enter_dungeon()

def choose_door(door_choice: str) -> Dict[str, Any]:
    """
    Choose a door in the dungeon
    Delegates to game logic layer
    """
    return _manager.choose_door(door_choice)

def get_dungeon_state() -> Dict[str, Any]:
    """
    Get current dungeon state
    Delegates to game logic layer
    """
    return _manager.get_dungeon_state()