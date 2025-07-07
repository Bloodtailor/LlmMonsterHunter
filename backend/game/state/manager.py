# Game State Manager - Clean State Management Logic

from typing import List, Dict, Any, Optional
from backend.models.monster import Monster
from backend.game.utils import (
    validate_party_size, validate_monster_exists, validate_monsters_are_following,
    validate_following_monster_addition, validate_and_continue
)
from backend.utils.responses import error_response, success_response
from backend.utils.console import print_success

class GameStateManager:
    """Clean game state management - handles all session state logic"""
    
    def __init__(self):
        # Game state variables - private to manager
        self._following_monsters: List[int] = []        # Monster IDs following the player
        self._active_party: List[int] = []             # Monster IDs in current party (max 4)
        self._current_dungeon_state: Optional[Dict[str, Any]] = None  # Current dungeon state
        self._in_dungeon: bool = False                 # Whether player is in dungeon
    
    def get_game_state(self) -> Dict[str, Any]:
        """
        Get complete current game state
        
        Returns:
            dict: All current game state information
        """
        try:
            # Get monster details for following monsters
            following_monster_details = []
            for monster_id in self._following_monsters:
                monster = Monster.get_monster_by_id(monster_id)
                if monster:
                    following_monster_details.append(monster.to_dict())
            
            # Get monster details for active party
            active_party_details = []
            for monster_id in self._active_party:
                monster = Monster.get_monster_by_id(monster_id)
                if monster:
                    active_party_details.append(monster.to_dict())
            
            return success_response({
                'following_monsters': {
                    'ids': self._following_monsters.copy(),
                    'count': len(self._following_monsters),
                    'details': following_monster_details
                },
                'active_party': {
                    'ids': self._active_party.copy(),
                    'count': len(self._active_party),
                    'details': active_party_details
                },
                'dungeon_state': {
                    'in_dungeon': self._in_dungeon,
                    'current_state': self._current_dungeon_state.copy() if self._current_dungeon_state else None
                },
                'game_status': 'in_dungeon' if self._in_dungeon else 'home_base'
            })
            
        except Exception as e:
            return error_response(str(e))
    
    def add_following_monster(self, monster_id: int) -> Dict[str, Any]:
        """
        Add a monster to the following list
        
        Args:
            monster_id (int): ID of monster to add
            
        Returns:
            dict: Success status and updated state
        """
        try:
            # Validate using our utilities
            validation = validate_following_monster_addition(monster_id, self._following_monsters)
            error_check = validate_and_continue(validation, {'following_count': len(self._following_monsters)})
            if error_check:
                return error_check
            
            monster = validation['monster']
            
            # Add to following list
            self._following_monsters.append(monster_id)
            
            print_success(f"{monster.name} is now following the player! ({len(self._following_monsters)} total)")
            
            return success_response({
                'message': f'{monster.name} is now following you',
                'monster': monster.to_dict(),
                'following_count': len(self._following_monsters)
            })
            
        except Exception as e:
            return error_response(str(e), following_count=len(self._following_monsters))
    
    def remove_following_monster(self, monster_id: int) -> Dict[str, Any]:
        """
        Remove a monster from the following list
        
        Args:
            monster_id (int): ID of monster to remove
            
        Returns:
            dict: Success status and updated state
        """
        try:
            # Check if monster is following
            if monster_id not in self._following_monsters:
                return error_response(
                    f'Monster {monster_id} is not following you',
                    following_count=len(self._following_monsters)
                )
            
            # Get monster details for message
            monster = Monster.get_monster_by_id(monster_id)
            monster_name = monster.name if monster else f"Monster {monster_id}"
            
            # Remove from following list
            self._following_monsters.remove(monster_id)
            
            # Also remove from active party if present
            if monster_id in self._active_party:
                self._active_party.remove(monster_id)
                print_success(f"{monster_name} also removed from active party")
            
            print_success(f"{monster_name} is no longer following the player")
            
            return success_response({
                'message': f'{monster_name} is no longer following you',
                'following_count': len(self._following_monsters),
                'party_count': len(self._active_party)
            })
            
        except Exception as e:
            return error_response(str(e), following_count=len(self._following_monsters))
    
    def set_active_party(self, monster_ids: List[int]) -> Dict[str, Any]:
        """
        Set the active party from following monsters
        
        Args:
            monster_ids (list): List of monster IDs to set as active party (max 4)
            
        Returns:
            dict: Success status and party details
        """
        try:
            # Validate party size using our utilities
            party_validation = validate_party_size(monster_ids, max_size=4)
            error_check = validate_and_continue(party_validation, {'party_count': len(self._active_party)})
            if error_check:
                return error_check
            
            unique_ids = party_validation['unique_ids']
            
            # Validate all monsters are following using our utilities
            following_validation = validate_monsters_are_following(unique_ids, self._following_monsters)
            error_check = validate_and_continue(following_validation, {'party_count': len(self._active_party)})
            if error_check:
                return error_check
            
            # Set new active party
            self._active_party = unique_ids
            
            # Get monster details for response
            party_details = []
            for monster_id in self._active_party:
                monster = Monster.get_monster_by_id(monster_id)
                if monster:
                    party_details.append(monster.to_dict())
            
            party_names = [monster['name'] for monster in party_details]
            
            print_success(f"Active party set: {party_names} ({len(self._active_party)} monsters)")
            
            return success_response({
                'message': f'Active party set: {", ".join(party_names)}',
                'active_party': {
                    'ids': self._active_party.copy(),
                    'count': len(self._active_party),
                    'details': party_details
                }
            })
            
        except Exception as e:
            return error_response(str(e), party_count=len(self._active_party))
    
    def get_active_party(self) -> Dict[str, Any]:
        """
        Get current active party details
        
        Returns:
            dict: Active party information
        """
        try:
            # Get monster details
            party_details = []
            for monster_id in self._active_party:
                monster = Monster.get_monster_by_id(monster_id)
                if monster:
                    party_details.append(monster.to_dict())
            
            return success_response({
                'active_party': {
                    'ids': self._active_party.copy(),
                    'count': len(self._active_party),
                    'details': party_details
                }
            })
            
        except Exception as e:
            return error_response(str(e),
                active_party={
                    'ids': [],
                    'count': 0,
                    'details': []
                }
            )
    
    def get_following_monsters(self) -> Dict[str, Any]:
        """
        Get all monsters currently following the player
        
        Returns:
            dict: Following monsters information
        """
        try:
            # Get monster details
            following_details = []
            for monster_id in self._following_monsters:
                monster = Monster.get_monster_by_id(monster_id)
                if monster:
                    following_details.append(monster.to_dict())
            
            return success_response({
                'following_monsters': {
                    'ids': self._following_monsters.copy(),
                    'count': len(self._following_monsters),
                    'details': following_details
                }
            })
            
        except Exception as e:
            return error_response(str(e),
                following_monsters={
                    'ids': [],
                    'count': 0,
                    'details': []
                }
            )
    
    def reset_game_state(self) -> Dict[str, Any]:
        """
        Reset all game state to initial values (for testing)
        
        Returns:
            dict: Reset confirmation
        """
        try:
            self._following_monsters.clear()
            self._active_party.clear()
            self._current_dungeon_state = None
            self._in_dungeon = False
            
            print_success("Game state reset to initial values")
            
            return success_response({
                'message': 'Game state reset to initial values',
                'game_state': self.get_game_state()
            })
            
        except Exception as e:
            return error_response(str(e))
    
    def is_party_ready_for_dungeon(self) -> bool:
        """
        Check if party is ready for dungeon (has at least 1 monster)
        
        Returns:
            bool: True if party is ready for dungeon
        """
        return len(self._active_party) > 0
    
    def get_party_summary(self) -> str:
        """
        Get a text summary of the current party for display/logging
        
        Returns:
            str: Human-readable party summary
        """
        if not self._active_party:
            return "No active party"
        
        try:
            party_names = []
            for monster_id in self._active_party:
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
            return f"Party: {len(self._active_party)} monsters"
    
    # Dungeon state management for dungeon service
    def get_dungeon_state_raw(self):
        """Get raw dungeon state for dungeon service"""
        return self._current_dungeon_state if self._in_dungeon else None
    
    def set_dungeon_state_raw(self, state):
        """Set raw dungeon state for dungeon service"""  
        self._current_dungeon_state = state
        self._in_dungeon = True
    
    def clear_dungeon_state_raw(self):
        """Clear dungeon state for dungeon service"""
        self._current_dungeon_state = None
        self._in_dungeon = False