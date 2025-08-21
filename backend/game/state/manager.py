# Game State Manager - REWRITTEN FOR SIMPLIFIED ARCHITECTURE
# Uses new simplified models: ActiveParty, FollowingMonster, GlobalVariable
# Contains game-specific convenience methods that were moved from GlobalVariable

from typing import List, Dict, Any, Optional
from backend.models.active_party import ActiveParty
from backend.models.following_monsters import FollowingMonster
from backend.models.global_variables import GlobalVariable
from backend.models.monster import Monster
from backend.core.utils.console import print_success

def get_following_monsters():

    return FollowingMonster.get_all_following()

def add_following_monster(monster_id: int):

    FollowingMonster.add_follower(monster_id)
        
    return

def remove_from_party(monster_id: int):

    if ActiveParty.is_in_active_party(monster_id):
        ActiveParty.remove_from_party(monster_id)

    return

def remove_following_monster(monster_id: int):

    if FollowingMonster.is_following(monster_id):
        FollowingMonster.remove_follower(monster_id)
        remove_from_party(monster_id)
        
    return

def get_active_party():
    
    return ActiveParty.get_all_party_members()

def set_active_party(monster_ids: List[int]):

    ActiveParty.set_party(monster_ids)
        
    return get_following_monsters()

def is_party_ready_for_dungeon() -> bool:
    """Check if party is ready for dungeon (has at least 1 monster)"""

    return ActiveParty.is_party_ready()


def get_party_summary() -> str:
    """Get a text summary of the current party for display/logging"""

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


def reset_game_state() -> Dict[str, Any]:
    """Reset all game state to initial values (for testing)"""

    ActiveParty.clear_party()
    FollowingMonster.clear_all_followers()
    GlobalVariable.clear_all()
    
    print_success("Game state reset to initial values")
    
    return
