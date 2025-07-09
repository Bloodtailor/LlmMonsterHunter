# Game State Manager - DATABASE-BACKED: No Validation
# Pure business logic using normalized database models
# Persistent state that survives server restarts

from typing import List, Dict, Any, Optional
from backend.models.game_state import GameState
from backend.models.game_state_relations import DungeonState, DungeonDoor
from backend.utils import (
    error_response, success_response, print_success
)

class GameStateManager:
    """Database-backed game state management - no validation"""
    
    def get_game_state(self) -> Dict[str, Any]:
        """Get complete current game state from database"""
        try:
            game_state = GameState.get_current_game_state()
            
            return success_response({
                'following_monsters': {
                    'ids': game_state.get_following_monster_ids(),
                    'count': game_state.following_monsters.count(),
                    'details': game_state.get_following_monster_details()
                },
                'active_party': {
                    'ids': game_state.get_active_party_ids(),
                    'count': game_state.active_party.count(),
                    'details': game_state.get_active_party_details()
                },
                'dungeon_state': {
                    'in_dungeon': game_state.in_dungeon,
                    'current_state': game_state.dungeon_state.get_legacy_format() if game_state.dungeon_state else None
                },
                'game_status': 'in_dungeon' if game_state.in_dungeon else 'home_base'
            })
            
        except Exception as e:
            return error_response(str(e))
    
    def add_following_monster(self, monster_id: int) -> Dict[str, Any]:
        """Add a monster to the following list - assumes monster exists"""
        try:
            game_state = GameState.get_current_game_state()
            
            # Check if already following
            if monster_id in game_state.get_following_monster_ids():
                from backend.models.monster import Monster
                monster = Monster.get_monster_by_id(monster_id)
                monster_name = monster.name if monster else f"Monster {monster_id}"
                
                return error_response(
                    f'{monster_name} is already following you',
                    following_count=game_state.following_monsters.count()
                )
            
            # Add to following list
            success = game_state.add_following_monster(monster_id)
            if not success:
                return error_response(
                    'Failed to add monster to following list',
                    following_count=game_state.following_monsters.count()
                )
            
            # Get monster details for response
            from backend.models.monster import Monster
            monster = Monster.get_monster_by_id(monster_id)
            
            print_success(f"{monster.name} is now following the player! ({game_state.following_monsters.count()} total)")
            
            return success_response({
                'message': f'{monster.name} is now following you',
                'monster': monster.to_dict(),
                'following_count': game_state.following_monsters.count()
            })
            
        except Exception as e:
            return error_response(str(e))
    
    def remove_following_monster(self, monster_id: int) -> Dict[str, Any]:
        """Remove a monster from following list - assumes monster exists"""
        try:
            game_state = GameState.get_current_game_state()
            
            # Check if monster is following
            if monster_id not in game_state.get_following_monster_ids():
                return error_response(
                    f'Monster {monster_id} is not following you',
                    following_count=game_state.following_monsters.count()
                )
            
            # Get monster details for message
            from backend.models.monster import Monster
            monster = Monster.get_monster_by_id(monster_id)
            monster_name = monster.name if monster else f"Monster {monster_id}"
            
            # Remove from following list (also removes from active party)
            game_state.remove_following_monster(monster_id)
            
            print_success(f"{monster_name} is no longer following the player")
            
            return success_response({
                'message': f'{monster_name} is no longer following you',
                'following_count': game_state.following_monsters.count(),
                'party_count': game_state.active_party.count()
            })
            
        except Exception as e:
            return error_response(str(e))
    
    def set_active_party(self, monster_ids: List[int]) -> Dict[str, Any]:
        """Set active party - assumes all monsters are following"""
        try:
            game_state = GameState.get_current_game_state()
            
            # Remove duplicates while preserving order
            unique_ids = []
            for mid in monster_ids:
                if mid not in unique_ids:
                    unique_ids.append(mid)
            
            # Set new active party
            game_state.set_active_party(unique_ids)
            
            # Get monster details for response
            party_details = game_state.get_active_party_details()
            party_names = [monster['name'] for monster in party_details]
            
            print_success(f"Active party set: {party_names} ({len(unique_ids)} monsters)")
            
            return success_response({
                'message': f'Active party set: {", ".join(party_names)}',
                'active_party': {
                    'ids': unique_ids,
                    'count': len(unique_ids),
                    'details': party_details
                }
            })
            
        except Exception as e:
            return error_response(str(e))
    
    def get_active_party(self) -> Dict[str, Any]:
        """Get current active party details"""
        try:
            game_state = GameState.get_current_game_state()
            
            return success_response({
                'active_party': {
                    'ids': game_state.get_active_party_ids(),
                    'count': game_state.active_party.count(),
                    'details': game_state.get_active_party_details()
                }
            })
            
        except Exception as e:
            return error_response(str(e))
    
    def get_following_monsters(self) -> Dict[str, Any]:
        """Get all monsters currently following the player"""
        try:
            game_state = GameState.get_current_game_state()
            
            return success_response({
                'following_monsters': {
                    'ids': game_state.get_following_monster_ids(),
                    'count': game_state.following_monsters.count(),
                    'details': game_state.get_following_monster_details()
                }
            })
            
        except Exception as e:
            return error_response(str(e))
    
    def reset_game_state(self) -> Dict[str, Any]:
        """Reset all game state to initial values (for testing)"""
        try:
            # Reset to fresh state
            game_state = GameState.reset_game_state()
            
            print_success("Game state reset to initial values")
            
            return success_response({
                'message': 'Game state reset to initial values',
                'game_state': self.get_game_state()
            })
            
        except Exception as e:
            return error_response(str(e))
    
    def is_party_ready_for_dungeon(self) -> bool:
        """Check if party is ready for dungeon (has at least 1 monster)"""
        try:
            game_state = GameState.get_current_game_state()
            return game_state.is_party_ready_for_dungeon()
        except Exception:
            return False
    
    def get_party_summary(self) -> str:
        """Get a text summary of the current party for display/logging"""
        try:
            game_state = GameState.get_current_game_state()
            return game_state.get_party_summary()
        except Exception:
            return "No active party"
    
    # === Dungeon State Management ===
    
    def get_dungeon_state_raw(self) -> Optional[Dict[str, Any]]:
        """Get raw dungeon state for dungeon service"""
        try:
            game_state = GameState.get_current_game_state()
            if not game_state.in_dungeon or not game_state.dungeon_state:
                return None
            return game_state.dungeon_state.get_legacy_format()
        except Exception:
            return None
    
    def set_dungeon_state_raw(self, state: Dict[str, Any]) -> None:
        """Set raw dungeon state for dungeon service"""
        try:
            game_state = GameState.get_current_game_state()
            
            # Mark as in dungeon
            game_state.enter_dungeon()
            
            # Create or update dungeon state
            if game_state.dungeon_state:
                dungeon_state = game_state.dungeon_state
            else:
                dungeon_state = DungeonState(game_state_id=game_state.id)
            
            # Set location
            location = state.get('current_location', {})
            dungeon_state.current_location_name = location.get('name', 'Unknown Location')
            dungeon_state.current_location_description = location.get('description', 'A mysterious place.')
            dungeon_state.last_event_text = state.get('last_event_text')
            dungeon_state.party_summary = state.get('party_summary', 'Unknown party')
            dungeon_state.save()
            
            # Set doors
            doors_data = state.get('available_doors', [])
            dungeon_state.set_doors(doors_data)
            
        except Exception as e:
            print(f"❌ Error setting dungeon state: {e}")
    
    def clear_dungeon_state_raw(self) -> None:
        """Clear dungeon state for dungeon service"""
        try:
            game_state = GameState.get_current_game_state()
            game_state.exit_dungeon()
        except Exception as e:
            print(f"❌ Error clearing dungeon state: {e}")