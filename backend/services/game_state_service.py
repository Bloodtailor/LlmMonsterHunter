# Game State Service - Session Management
# Manages the current game state using simple global variables
# No database persistence - resets on server restart

from typing import List, Dict, Any, Optional
from backend.models.monster import Monster

# Global game state variables
_following_monsters: List[int] = []        # Monster IDs that are following the player
_active_party: List[int] = []             # Monster IDs in the current party (max 4)
_current_dungeon_state: Optional[Dict[str, Any]] = None  # Current dungeon state if in dungeon
_in_dungeon: bool = False                 # Whether player is currently in a dungeon

def get_game_state() -> Dict[str, Any]:
    """
    Get complete current game state
    
    Returns:
        dict: All current game state information
    """
    global _following_monsters, _active_party, _current_dungeon_state, _in_dungeon
    
    # Get monster details for following monsters
    following_monster_details = []
    for monster_id in _following_monsters:
        monster = Monster.get_monster_by_id(monster_id)
        if monster:
            following_monster_details.append(monster.to_dict())
    
    # Get monster details for active party
    active_party_details = []
    for monster_id in _active_party:
        monster = Monster.get_monster_by_id(monster_id)
        if monster:
            active_party_details.append(monster.to_dict())
    
    return {
        'following_monsters': {
            'ids': _following_monsters.copy(),
            'count': len(_following_monsters),
            'details': following_monster_details
        },
        'active_party': {
            'ids': _active_party.copy(),
            'count': len(_active_party),
            'details': active_party_details
        },
        'dungeon_state': {
            'in_dungeon': _in_dungeon,
            'current_state': _current_dungeon_state.copy() if _current_dungeon_state else None
        },
        'game_status': 'in_dungeon' if _in_dungeon else 'home_base'
    }

def add_following_monster(monster_id: int) -> Dict[str, Any]:
    """
    Add a monster to the following list (for testing)
    
    Args:
        monster_id (int): ID of monster to add
        
    Returns:
        dict: Success status and updated state
    """
    global _following_monsters
    
    try:
        # Check if monster exists
        monster = Monster.get_monster_by_id(monster_id)
        if not monster:
            return {
                'success': False,
                'error': f'Monster {monster_id} not found',
                'following_count': len(_following_monsters)
            }
        
        # Check if already following
        if monster_id in _following_monsters:
            return {
                'success': False,
                'error': f'Monster {monster.name} is already following you',
                'following_count': len(_following_monsters)
            }
        
        # Add to following list
        _following_monsters.append(monster_id)
        
        print(f"🐾 {monster.name} is now following the player! ({len(_following_monsters)} total)")
        
        return {
            'success': True,
            'message': f'{monster.name} is now following you',
            'monster': monster.to_dict(),
            'following_count': len(_following_monsters)
        }
        
    except Exception as e:
        return {
            'success': False,
            'error': str(e),
            'following_count': len(_following_monsters)
        }

def remove_following_monster(monster_id: int) -> Dict[str, Any]:
    """
    Remove a monster from the following list
    
    Args:
        monster_id (int): ID of monster to remove
        
    Returns:
        dict: Success status and updated state
    """
    global _following_monsters, _active_party
    
    try:
        # Check if monster is following
        if monster_id not in _following_monsters:
            return {
                'success': False,
                'error': f'Monster {monster_id} is not following you',
                'following_count': len(_following_monsters)
            }
        
        # Get monster details for message
        monster = Monster.get_monster_by_id(monster_id)
        monster_name = monster.name if monster else f"Monster {monster_id}"
        
        # Remove from following list
        _following_monsters.remove(monster_id)
        
        # Also remove from active party if present
        if monster_id in _active_party:
            _active_party.remove(monster_id)
            print(f"🚫 {monster_name} also removed from active party")
        
        print(f"👋 {monster_name} is no longer following the player")
        
        return {
            'success': True,
            'message': f'{monster_name} is no longer following you',
            'following_count': len(_following_monsters),
            'party_count': len(_active_party)
        }
        
    except Exception as e:
        return {
            'success': False,
            'error': str(e),
            'following_count': len(_following_monsters)
        }

def set_active_party(monster_ids: List[int]) -> Dict[str, Any]:
    """
    Set the active party from following monsters
    
    Args:
        monster_ids (list): List of monster IDs to set as active party (max 4)
        
    Returns:
        dict: Success status and party details
    """
    global _active_party, _following_monsters
    
    try:
        # Validate party size
        if len(monster_ids) > 4:
            return {
                'success': False,
                'error': 'Active party cannot exceed 4 monsters',
                'party_count': len(_active_party)
            }
        
        # Validate all monsters are following
        not_following = [mid for mid in monster_ids if mid not in _following_monsters]
        if not_following:
            return {
                'success': False,
                'error': f'Monsters {not_following} are not following you',
                'party_count': len(_active_party)
            }
        
        # Remove duplicates while preserving order
        unique_ids = []
        for mid in monster_ids:
            if mid not in unique_ids:
                unique_ids.append(mid)
        
        # Set new active party
        _active_party = unique_ids
        
        # Get monster details for response
        party_details = []
        for monster_id in _active_party:
            monster = Monster.get_monster_by_id(monster_id)
            if monster:
                party_details.append(monster.to_dict())
        
        party_names = [monster['name'] for monster in party_details]
        
        print(f"⚔️ Active party set: {party_names} ({len(_active_party)} monsters)")
        
        return {
            'success': True,
            'message': f'Active party set: {", ".join(party_names)}',
            'active_party': {
                'ids': _active_party.copy(),
                'count': len(_active_party),
                'details': party_details
            }
        }
        
    except Exception as e:
        return {
            'success': False,
            'error': str(e),
            'party_count': len(_active_party)
        }

def get_active_party() -> Dict[str, Any]:
    """
    Get current active party details
    
    Returns:
        dict: Active party information
    """
    global _active_party
    
    try:
        # Get monster details
        party_details = []
        for monster_id in _active_party:
            monster = Monster.get_monster_by_id(monster_id)
            if monster:
                party_details.append(monster.to_dict())
        
        return {
            'success': True,
            'active_party': {
                'ids': _active_party.copy(),
                'count': len(_active_party),
                'details': party_details
            }
        }
        
    except Exception as e:
        return {
            'success': False,
            'error': str(e),
            'active_party': {
                'ids': [],
                'count': 0,
                'details': []
            }
        }

def get_following_monsters() -> Dict[str, Any]:
    """
    Get all monsters currently following the player
    
    Returns:
        dict: Following monsters information
    """
    global _following_monsters
    
    try:
        # Get monster details
        following_details = []
        for monster_id in _following_monsters:
            monster = Monster.get_monster_by_id(monster_id)
            if monster:
                following_details.append(monster.to_dict())
        
        return {
            'success': True,
            'following_monsters': {
                'ids': _following_monsters.copy(),
                'count': len(_following_monsters),
                'details': following_details
            }
        }
        
    except Exception as e:
        return {
            'success': False,
            'error': str(e),
            'following_monsters': {
                'ids': [],
                'count': 0,
                'details': []
            }
        }

def reset_game_state() -> Dict[str, Any]:
    """
    Reset all game state to initial values (for testing)
    
    Returns:
        dict: Reset confirmation
    """
    global _following_monsters, _active_party, _current_dungeon_state, _in_dungeon
    
    _following_monsters.clear()
    _active_party.clear()
    _current_dungeon_state = None
    _in_dungeon = False
    
    print("🔄 Game state reset to initial values")
    
    return {
        'success': True,
        'message': 'Game state reset to initial values',
        'game_state': get_game_state()
    }

def is_party_ready_for_dungeon() -> bool:
    """
    Check if party is ready for dungeon (has at least 1 monster)
    
    Returns:
        bool: True if party is ready for dungeon
    """
    global _active_party
    return len(_active_party) > 0

def get_party_summary() -> str:
    """
    Get a text summary of the current party for display/logging
    
    Returns:
        str: Human-readable party summary
    """
    global _active_party
    
    if not _active_party:
        return "No active party"
    
    try:
        party_names = []
        for monster_id in _active_party:
            monster = Monster.get_monster_by_id(monster_id)
            if monster:
                party_names.append(monster.name)
        
        if len(party_names) == 1:
            return f"Party: {party_names[0]}"
        elif len(party_names) == 2:
            return f"Party: {party_names[0]} and {party_names[1]}"
        else:
            return f"Party: {', '.join(party_names[:-1])}, and {party_names[-1]}"
            
    except Exception:
        return f"Party: {len(_active_party)} monsters"
    
def get_dungeon_state_raw():
    """Get raw dungeon state for dungeon service"""
    global _current_dungeon_state, _in_dungeon
    return _current_dungeon_state if _in_dungeon else None

def set_dungeon_state_raw(state):
    """Set raw dungeon state for dungeon service"""  
    global _current_dungeon_state, _in_dungeon
    _current_dungeon_state = state
    _in_dungeon = True

def clear_dungeon_state_raw():
    """Clear dungeon state for dungeon service"""
    global _current_dungeon_state, _in_dungeon
    _current_dungeon_state = None
    _in_dungeon = False