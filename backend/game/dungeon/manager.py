# Dungeon Manager - SIMPLIFIED: No Validation
# Pure business logic - assumes all inputs are valid
# Eliminates defensive programming completely
print(f"🔍 Loading {__file__}")
from typing import Dict, Any, Optional
from backend.core.utils import error_response, success_response, print_success
from .generator import DungeonGenerator

class DungeonManager:
    """Pure business logic - no validation"""
    
    def __init__(self):
        self.generator = DungeonGenerator()
    
    def enter_dungeon(self) -> Dict[str, Any]:
        """Enter dungeon - assumes party is ready"""
        
        # Get party summary (assumes party exists)
        from backend.services import game_state_service
        party_summary = game_state_service.get_party_summary()
        
        print_success(f"Entering dungeon with: {party_summary}")
        
        # Generate entry text
        entry_text_result = self.generator.generate_entry_text(party_summary)
        if not entry_text_result['success']:
            return error_response(
                f"Failed to generate entry text: {entry_text_result['error']}",
                dungeon_entered=False
            )
        
        # Generate initial location
        location_result = self.generator.generate_random_location()
        if not location_result['success']:
            return error_response(
                f"Failed to generate location: {location_result['error']}",
                dungeon_entered=False
            )
        
        # Generate door choices
        doors_result = self.generator.generate_door_choices()
        if not doors_result['success']:
            return error_response(
                f"Failed to generate doors: {doors_result['error']}",
                dungeon_entered=False
            )
        
        # Set dungeon state
        dungeon_state = {
            'current_location': location_result['location'],
            'available_doors': doors_result['doors'],
            'entry_text': entry_text_result['text'],
            'party_summary': party_summary
        }
        
        self._set_dungeon_state(dungeon_state)
        
        return success_response({
            'dungeon_entered': True,
            'entry_text': entry_text_result['text'],
            'location': location_result['location'],
            'doors': doors_result['doors'],
            'party_summary': party_summary,
            'message': 'Welcome to the dungeon! Choose your path wisely.'
        })
    
    def choose_door(self, door_choice: str) -> Dict[str, Any]:
        """Choose door - assumes valid door choice and dungeon state"""
        
        # Get current state (assumes we're in dungeon)
        current_state = self._get_dungeon_state()
        
        # Find chosen door (assumes it exists)
        chosen_door = next(
            (door for door in current_state['available_doors'] if door['id'] == door_choice),
            None
        )
        
        if door_choice == 'exit':
            return self._handle_dungeon_exit(chosen_door)
        else:
            return self._handle_location_choice(chosen_door)
    
    def get_dungeon_state(self) -> Dict[str, Any]:
        """Get dungeon state - no validation needed"""
        
        state = self._get_dungeon_state()
        
        if not state:
            return success_response({
                'in_dungeon': False,
                'state': None,
                'message': 'Not currently in a dungeon'
            })
        
        return success_response({
            'in_dungeon': True,
            'state': state,
            'party_summary': state.get('party_summary', 'Unknown party')
        })
    
    def _handle_location_choice(self, chosen_door: Dict[str, Any]) -> Dict[str, Any]:
        """Handle location choice - assumes valid door"""
        
        location_name = chosen_door.get('name', 'Unknown Location')
        
        # Generate event text
        event_text_result = self.generator.generate_location_event_text(location_name)
        if not event_text_result['success']:
            event_text = f"You step through the {location_name} and find yourself in a new area of the dungeon."
        else:
            event_text = event_text_result['text']
        
        # Generate new location
        new_location_result = self.generator.generate_random_location()
        if not new_location_result['success']:
            return error_response('Failed to generate new location', in_dungeon=True)
        
        # Generate new doors
        new_doors_result = self.generator.generate_door_choices()
        if not new_doors_result['success']:
            return error_response('Failed to generate new doors', in_dungeon=True)
        
        # Update dungeon state
        new_state = {
            'current_location': new_location_result['location'],
            'available_doors': new_doors_result['doors'],
            'last_event_text': event_text,
            'party_summary': self._get_dungeon_state().get('party_summary', 'Unknown party')
        }
        
        self._set_dungeon_state(new_state)
        
        return success_response({
            'choice_made': chosen_door['name'],
            'event_text': event_text,
            'new_location': new_location_result['location'],
            'new_doors': new_doors_result['doors'],
            'continue_button': True,
            'in_dungeon': True
        })
    
    def _handle_dungeon_exit(self, chosen_door: Dict[str, Any]) -> Dict[str, Any]:
        """Handle exit choice - assumes valid door"""
        
        party_summary = self._get_dungeon_state().get('party_summary', 'your party')
        
        # Generate exit text
        exit_text_result = self.generator.generate_exit_text(party_summary)
        if not exit_text_result['success']:
            exit_text = f"You and {party_summary} emerge from the dungeon, glad to see daylight once again."
        else:
            exit_text = exit_text_result['text']
        
        # Clear dungeon state
        self._clear_dungeon_state()
        
        return success_response({
            'choice_made': 'Exit the Dungeon',
            'exit_text': exit_text,
            'dungeon_completed': True,
            'in_dungeon': False,
            'return_to_home_button': True,
            'message': 'You have successfully exited the dungeon!'
        })
    
    # Helper functions for dungeon state management
    def _get_dungeon_state(self) -> Optional[Dict[str, Any]]:
        """Get current dungeon state"""
        from backend.services import game_state_service
        return game_state_service.get_dungeon_state_raw()
    
    def _set_dungeon_state(self, state: Dict[str, Any]) -> None:
        """Set dungeon state"""
        from backend.services import game_state_service
        game_state_service.set_dungeon_state_raw(state)
    
    def _clear_dungeon_state(self) -> None:
        """Clear dungeon state"""
        from backend.services import game_state_service
        game_state_service.clear_dungeon_state_raw()