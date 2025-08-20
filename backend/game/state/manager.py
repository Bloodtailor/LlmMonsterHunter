# Game State Manager - REWRITTEN FOR SIMPLIFIED ARCHITECTURE
# Uses new simplified models: ActiveParty, FollowingMonster, GlobalVariable
# Contains game-specific convenience methods that were moved from GlobalVariable

from typing import List, Dict, Any, Optional
from backend.models.active_party import ActiveParty
from backend.models.following_monsters import FollowingMonster
from backend.models.global_variables import GlobalVariable
from backend.models.monster import Monster
from backend.core.utils import (
    error_response, success_response, print_success
)

# ===== FOLLOWING MONSTERS MANAGEMENT =====

def get_following_monsters() -> Dict[str, Any]:
    """Get all monsters currently following the player"""
    try:
        return success_response({
            'following_monsters': FollowingMonster.get_following_summary()
        })
    except Exception as e:
        return error_response(str(e))

def add_following_monster(monster_id: int) -> Dict[str, Any]:
    """Add a monster to the following list - assumes monster exists and validation done"""
    try:
        # Check if already following
        if FollowingMonster.is_following(monster_id):
            monster = Monster.get_monster_by_id(monster_id)
            monster_name = monster.name if monster else f"Monster {monster_id}"
            
            return error_response(
                f'{monster_name} is already following you',
                following_count=FollowingMonster.get_following_count()
            )
        
        # Add to following list
        success = FollowingMonster.add_follower(monster_id)
        if not success:
            return error_response(
                'Failed to add monster to following list',
                following_count=FollowingMonster.get_following_count()
            )
        
        # Get monster details for response
        monster = Monster.get_monster_by_id(monster_id)
        
        print_success(f"{monster.name} is now following the player! ({FollowingMonster.get_following_count()} total)")
        
        return success_response({
            'message': f'{monster.name} is now following you',
            'monster': monster.to_dict(),
            'following_count': FollowingMonster.get_following_count()
        })
        
    except Exception as e:
        return error_response(str(e))

def remove_following_monster(monster_id: int) -> Dict[str, Any]:
    """Remove a monster from following list - assumes monster exists and validation done"""
    try:
        # Check if monster is following
        if not FollowingMonster.is_following(monster_id):
            return error_response(
                f'Monster {monster_id} is not following you',
                following_count=FollowingMonster.get_following_count()
            )
        
        # Get monster details for message
        monster = Monster.get_monster_by_id(monster_id)
        monster_name = monster.name if monster else f"Monster {monster_id}"
        
        # Remove from following list
        FollowingMonster.remove_follower(monster_id)
        
        # Also remove from active party if present
        ActiveParty.remove_from_party(monster_id)
        
        print_success(f"{monster_name} is no longer following the player")
        
        return success_response({
            'message': f'{monster_name} is no longer following you',
            'following_count': FollowingMonster.get_following_count(),
            'party_count': ActiveParty.get_party_count()
        })
        
    except Exception as e:
        return error_response(str(e))

# ===== ACTIVE PARTY MANAGEMENT =====

def get_active_party() -> Dict[str, Any]:
    """Get current active party details"""
    try:
        party_members = ActiveParty.get_all_party_members()
        party_details = []
        
        for party_member in party_members:
            monster = Monster.get_monster_by_id(party_member.monster_id)
            if monster:
                party_details.append(monster.to_dict())
        
        return success_response({
            'active_party': {
                'ids': ActiveParty.get_party_monster_ids(),
                'count': ActiveParty.get_party_count(),
                'details': party_details
            }
        })
        
    except Exception as e:
        return error_response(str(e))

def set_active_party(monster_ids: List[int]) -> Dict[str, Any]:
    """Set active party - assumes all monsters are following and validation done"""
    try:
        # Set new active party
        ActiveParty.set_party(monster_ids)
        
        # Get monster details for response
        party_details = []
        party_names = []
        
        for monster_id in monster_ids:
            monster = Monster.get_monster_by_id(monster_id)
            if monster:
                party_details.append(monster.to_dict())
                party_names.append(monster.name)
        
        print_success(f"Active party set: {party_names} ({len(monster_ids)} monsters)")
        
        return success_response({
            'message': f'Active party set: {", ".join(party_names)}',
            'active_party': {
                'ids': monster_ids,
                'count': len(monster_ids),
                'details': party_details
            }
        })
        
    except Exception as e:
        return error_response(str(e))

def is_party_ready_for_dungeon() -> bool:
    """Check if party is ready for dungeon (has at least 1 monster)"""
    try:
        return ActiveParty.is_party_ready()
    except Exception:
        return False

def get_party_summary() -> str:
    """Get a text summary of the current party for display/logging"""
    try:
        party_ids = ActiveParty.get_party_monster_ids()
        
        if not party_ids:
            return "No active party"
        
        party_names = []
        for monster_id in party_ids:
            monster = Monster.get_monster_by_id(monster_id)
            if monster:
                party_names.append(monster.name)
        
        if len(party_names) == 1:
            return party_names[0]
        elif len(party_names) == 2:
            return f"{party_names[0]} and {party_names[1]}"
        else:
            return f"{', '.join(party_names[:-1])}, and {party_names[-1]}"
            
    except Exception:
        return "Unknown party"

# ===== GLOBAL GAME STATE =====

def get_game_state() -> Dict[str, Any]:
    """Get complete current game state"""
    try:
        return success_response({
            'following_monsters': FollowingMonster.get_following_summary(),
            'active_party': {
                'ids': ActiveParty.get_party_monster_ids(),
                'count': ActiveParty.get_party_count(),
                'details': [Monster.get_monster_by_id(mid).to_dict() 
                           for mid in ActiveParty.get_party_monster_ids() 
                           if Monster.get_monster_by_id(mid)]
            },
            'dungeon_state': {
                'in_dungeon': is_in_dungeon(),
                'current_state': get_dungeon_state_legacy() if is_in_dungeon() else None
            },
            'game_status': 'in_dungeon' if is_in_dungeon() else 'home_base'
        })
        
    except Exception as e:
        return error_response(str(e))

def reset_game_state() -> Dict[str, Any]:
    """Reset all game state to initial values (for testing)"""
    try:
        # Clear all tables
        ActiveParty.clear_party()
        FollowingMonster.clear_all_followers()
        GlobalVariable.clear_all()
        
        print_success("Game state reset to initial values")
        
        return success_response({
            'message': 'Game state reset to initial values',
            'game_state': get_game_state()
        })
        
    except Exception as e:
        return error_response(str(e))

# ===== DUNGEON STATE CONVENIENCE METHODS =====
# These were moved from GlobalVariable model to maintain SRP

def is_in_dungeon() -> bool:
    """Check if player is in dungeon"""
    return GlobalVariable.get('in_dungeon', False)

def set_in_dungeon(in_dungeon: bool):
    """Set dungeon status"""
    return GlobalVariable.set('in_dungeon', in_dungeon)

def get_current_location() -> Dict[str, str]:
    """
    Get current location as dict
    
    Returns:
        dict: Location with name and description
    """
    return {
        'name': GlobalVariable.get('current_location_name', 'Unknown Location'),
        'description': GlobalVariable.get('current_location_description', 'A mysterious place.')
    }

def set_current_location(name: str, description: str):
    """Set current location"""
    GlobalVariable.set('current_location_name', name)
    GlobalVariable.set('current_location_description', description)

def get_doors() -> List[Dict[str, Any]]:
    """
    Get all door information
    
    Returns:
        list: List of door dictionaries
    """
    doors = []
    door_keys = GlobalVariable.get_keys_by_prefix('door_')
    
    # Extract door numbers and sort them
    door_nums = []
    for key in door_keys.keys():
        if key.startswith('door_') and len(key) > 5:
            try:
                door_num = int(key[5:])  # Extract number after "door_"
                door_nums.append(door_num)
            except ValueError:
                continue
    
    # Get doors in order
    for door_num in sorted(door_nums):
        door_data = GlobalVariable.get(f'door_{door_num}')
        if door_data and isinstance(door_data, dict):
            doors.append(door_data)
    
    return doors

def set_doors(doors: List[Dict[str, Any]]):
    """
    Set door information (clears existing doors first)
    
    Args:
        doors (list): List of door dictionaries with id, type, name, description
    """
    # Clear existing doors
    existing_door_keys = [key for key in GlobalVariable.get_keys_by_prefix('door_').keys()]
    for key in existing_door_keys:
        GlobalVariable.delete_key(key)
    
    # Set new doors
    for i, door in enumerate(doors, 1):
        door_data = {
            'id': door.get('id', f'door_{i}'),
            'type': door.get('type', 'location'),
            'name': door.get('name', f'Door {i}'),
            'description': door.get('description', 'A mysterious passage.')
        }
        GlobalVariable.set(f'door_{i}', door_data)

def get_door(door_number: int) -> Optional[Dict[str, Any]]:
    """
    Get specific door by number
    
    Args:
        door_number (int): Door number (1, 2, 3, etc.)
        
    Returns:
        dict: Door data or None if not found
    """
    return GlobalVariable.get(f'door_{door_number}')

def set_door(door_number: int, door_data: Dict[str, Any]):
    """
    Set specific door data
    
    Args:
        door_number (int): Door number
        door_data (dict): Door information
    """
    return GlobalVariable.set(f'door_{door_number}', door_data)

def get_last_event_text() -> str:
    """Get last dungeon event text"""
    return GlobalVariable.get('last_event_text', '')

def set_last_event_text(text: str):
    """Set last dungeon event text"""
    return GlobalVariable.set('last_event_text', text)

def get_party_summary_cached() -> str:
    """Get cached party summary text (for dungeon use)"""
    return GlobalVariable.get('party_summary', get_party_summary())

def set_party_summary_cached(summary: str):
    """Set cached party summary text (for dungeon use)"""
    return GlobalVariable.set('party_summary', summary)

def update_party_summary_cache():
    """Update the cached party summary with current party"""
    current_summary = get_party_summary()
    set_party_summary_cached(current_summary)
    return current_summary

# ===== LEGACY COMPATIBILITY =====
# These maintain backward compatibility with existing dungeon service

def get_dungeon_state_raw() -> Optional[Dict[str, Any]]:
    """Get raw dungeon state for dungeon service - LEGACY compatibility"""
    try:
        if not is_in_dungeon():
            return None
        
        return {
            'current_location': get_current_location(),
            'available_doors': get_doors(),
            'last_event_text': get_last_event_text(),
            'party_summary': get_party_summary_cached()
        }
    except Exception:
        return None

def get_dungeon_state_legacy() -> Dict[str, Any]:
    """Get dungeon state in legacy format"""
    return get_dungeon_state_raw()

def set_dungeon_state_raw(state: Dict[str, Any]) -> None:
    """Set raw dungeon state for dungeon service - LEGACY compatibility"""
    try:
        # Mark as in dungeon
        set_in_dungeon(True)
        
        # Set location
        location = state.get('current_location', {})
        set_current_location(
            location.get('name', 'Unknown Location'),
            location.get('description', 'A mysterious place.')
        )
        
        # Set other state
        if 'last_event_text' in state:
            set_last_event_text(state['last_event_text'])
        
        if 'party_summary' in state:
            set_party_summary_cached(state['party_summary'])
        
        # Set doors
        doors_data = state.get('available_doors', [])
        if doors_data:
            set_doors(doors_data)
        
    except Exception as e:
        print(f"❌ Error setting dungeon state: {e}")

def clear_dungeon_state_raw() -> None:
    """Clear dungeon state for dungeon service - LEGACY compatibility"""
    try:
        set_in_dungeon(False)
        
        # Clear dungeon-specific state
        GlobalVariable.delete_key('current_location_name')
        GlobalVariable.delete_key('current_location_description')
        GlobalVariable.delete_key('last_event_text')
        
        # Clear doors
        existing_door_keys = [key for key in GlobalVariable.get_keys_by_prefix('door_').keys()]
        for key in existing_door_keys:
            GlobalVariable.delete_key(key)
            
    except Exception as e:
        print(f"❌ Error clearing dungeon state: {e}")