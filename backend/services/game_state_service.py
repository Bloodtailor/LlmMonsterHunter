# Game State Service - TRUST BOUNDARY: Validation + Delegation
# Uses new simplified game state manager with thin business logic wrappers
# Handles validation, response formatting, and error handling

from typing import List, Dict, Any
from backend.game.state import manager as state_manager
from backend.services.validators import (
    validate_monster_exists,
    validate_party_size,
    validate_monsters_are_following
)
from backend.core.utils import error_response, success_response, validate_and_continue

# ===== FOLLOWING MONSTERS MANAGEMENT =====

def get_following_monsters() -> Dict[str, Any]:
    """Get all monsters currently following the player"""
    try:
        following_data = state_manager.get_following_monsters()
        
        # Convert to expected API format
        following_details = []
        following_ids = []
        
        for following_monster in following_data:
            if following_monster.monster:
                following_details.append(following_monster.monster.to_dict())
                following_ids.append(following_monster.monster_id)
        
        return success_response({
            'following_monsters': {
                'ids': following_ids,
                'count': len(following_ids),
                'details': following_details
            }
        })
        
    except Exception as e:
        return error_response(str(e))

def add_following_monster(monster_id: int) -> Dict[str, Any]:
    """Add a monster to the following list"""
    
    # Trust boundary validation - monster exists and isn't already following
    monster_validation = validate_monster_exists(monster_id)
    error_check = validate_and_continue(monster_validation, {'following_count': 0})
    if error_check:
        return error_check
    
    monster = monster_validation['monster']
    
    try:
        # Check if already following (business rule)
        from backend.models.following_monsters import FollowingMonster
        if FollowingMonster.is_following(monster_id):
            return error_response(
                f'{monster.name} is already following you',
                following_count=FollowingMonster.get_following_count()
            )
        
        # Business logic
        state_manager.add_following_monster(monster_id)
        
        return success_response({
            'message': f'{monster.name} is now following you',
            'monster': monster.to_dict(),
            'following_count': FollowingMonster.get_following_count()
        })
        
    except Exception as e:
        return error_response(str(e))

def remove_following_monster(monster_id: int) -> Dict[str, Any]:
    """Remove a monster from the following list"""
    
    # Trust boundary validation - monster exists
    monster_validation = validate_monster_exists(monster_id)
    error_check = validate_and_continue(monster_validation, {'following_count': 0})
    if error_check:
        return error_check
    
    monster = monster_validation['monster']
    
    try:
        # Business logic (idempotent - no error if not following)
        state_manager.remove_following_monster(monster_id)
        
        from backend.models.following_monsters import FollowingMonster
        from backend.models.active_party import ActiveParty
        
        return success_response({
            'message': f'{monster.name} is no longer following you',
            'following_count': FollowingMonster.get_following_count(),
            'party_count': ActiveParty.get_party_count()
        })
        
    except Exception as e:
        return error_response(str(e))

# ===== ACTIVE PARTY MANAGEMENT =====

def get_active_party() -> Dict[str, Any]:
    """Get current active party details"""
    try:
        party_data = state_manager.get_active_party()
        
        # Convert to expected API format
        party_details = []
        party_ids = []
        
        for party_member in party_data:
            if party_member.monster:
                party_details.append(party_member.monster.to_dict())
                party_ids.append(party_member.monster_id)
        
        return success_response({
            'active_party': {
                'ids': party_ids,
                'count': len(party_ids),
                'details': party_details
            }
        })
        
    except Exception as e:
        return error_response(str(e))

def set_active_party(monster_ids: List[int]) -> Dict[str, Any]:
    """Set the active party from following monsters"""
    
    try:
        # Business logic - Note: Your manager returns get_following_monsters() but should probably return get_active_party()
        active_party = state_manager.set_active_party(monster_ids)
        
        party_names = []
        
        for party_member in active_party:
            if party_member.monster:
                party_names.append(party_member.monster.name)
        
        return success_response({
            'message': f'Active party set: {", ".join(party_names)}',
            'active_party': {
                'ids': monster_ids,
                'count': len(monster_ids)
            }
        })
        
    except Exception as e:
        return error_response(str(e))

# ===== GLOBAL GAME STATE =====

def reset_game_state() -> Dict[str, Any]:
    """Reset all game state to initial values (for testing)"""
    try:
        state_manager.reset_game_state()
        
        return success_response({
            'message': 'Game state reset to initial values',
            'game_state': 'Need to add game state implementation'
        })
        
    except Exception as e:
        return error_response(str(e))