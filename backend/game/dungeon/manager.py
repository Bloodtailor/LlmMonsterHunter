# Dungeon Manager - Clean Dungeon Flow Logic

from typing import Dict, Any, Optional
from backend.game.utils import validate_door_choice, validate_and_continue
from backend.utils.responses import error_response, success_response
from backend.utils.console import print_success
from .generator import DungeonGenerator

class DungeonManager:
    """Clean dungeon management - handles exploration flow and business logic"""
    
    def __init__(self):
        self.generator = DungeonGenerator()
    
    def enter_dungeon(self) -> Dict[str, Any]:
        """
        Start a dungeon adventure
        
        Returns:
            dict: Dungeon entry results with location and door choices
        """
        
        try:
            # Check if party is ready
            from backend.services import game_state_service
            
            if not game_state_service.is_party_ready_for_dungeon():
                return error_response(
                    'No active party set. Add monsters to your party before entering the dungeon.',
                    ready_for_dungeon=False
                )
            
            # Get party summary for atmospheric text
            party_summary = game_state_service.get_party_summary()
            
            print_success(f"Entering dungeon with: {party_summary}")
            
            # Generate atmospheric entry text using generator
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
            
            # Generate door choices (2 locations + 1 exit)
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
            
            # Update global game state
            self._set_dungeon_state(dungeon_state)
            
            return success_response({
                'dungeon_entered': True,
                'entry_text': entry_text_result['text'],
                'location': location_result['location'],
                'doors': doors_result['doors'],
                'party_summary': party_summary,
                'message': 'Welcome to the dungeon! Choose your path wisely.'
            })
            
        except Exception as e:
            return error_response(str(e), dungeon_entered=False)
    
    def choose_door(self, door_choice: str) -> Dict[str, Any]:
        """
        Choose a door in the dungeon
        
        Args:
            door_choice (str): 'location_1', 'location_2', or 'exit'
            
        Returns:
            dict: Results of door choice
        """
        
        try:
            # Check if in dungeon
            current_state = self._get_dungeon_state()
            if not current_state:
                return error_response(
                    'Not currently in a dungeon',
                    in_dungeon=False
                )
            
            # Validate door choice
            available_doors = current_state.get('available_doors', [])
            door_validation = validate_door_choice(door_choice, available_doors)
            error_check = validate_and_continue(door_validation, {'in_dungeon': True})
            if error_check:
                return error_check
            
            chosen_door = door_validation['door']
            
            if door_choice == 'exit':
                # Handle dungeon exit
                return self._handle_dungeon_exit(chosen_door)
            else:
                # Handle location choice
                return self._handle_location_choice(chosen_door)
            
        except Exception as e:
            return error_response(
                str(e),
                in_dungeon=self._get_dungeon_state() is not None
            )
    
    def get_dungeon_state(self) -> Dict[str, Any]:
        """
        Get current dungeon state
        
        Returns:
            dict: Current dungeon state or None if not in dungeon
        """
        
        try:
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
            
        except Exception as e:
            return error_response(str(e), in_dungeon=False)
    
    def _handle_location_choice(self, chosen_door: Dict[str, Any]) -> Dict[str, Any]:
        """Handle choosing a location door"""
        
        try:
            # Generate event text for this location
            location_name = chosen_door.get('name', 'Unknown Location')
            
            event_text_result = self.generator.generate_location_event_text(location_name)
            if not event_text_result['success']:
                event_text = f"You step through the {location_name} and find yourself in a new area of the dungeon."
            else:
                event_text = event_text_result['text']
            
            # Generate new location after the event
            new_location_result = self.generator.generate_random_location()
            if not new_location_result['success']:
                return error_response('Failed to generate new location', in_dungeon=True)
            
            # Generate new door choices
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
            
        except Exception as e:
            return error_response(str(e), in_dungeon=True)
    
    def _handle_dungeon_exit(self, chosen_door: Dict[str, Any]) -> Dict[str, Any]:
        """Handle choosing the exit door"""
        
        try:
            # Generate exit text
            party_summary = self._get_dungeon_state().get('party_summary', 'your party')
            
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
            
        except Exception as e:
            return error_response(str(e), in_dungeon=True)
    
    # Helper functions for dungeon state management
    def _get_dungeon_state(self) -> Optional[Dict[str, Any]]:
        """Get current dungeon state from game_state_service"""
        from backend.services import game_state_service
        return game_state_service.get_dungeon_state_raw()
    
    def _set_dungeon_state(self, state: Dict[str, Any]) -> None:
        """Set dungeon state in game_state_service"""
        from backend.services import game_state_service
        game_state_service.set_dungeon_state_raw(state)
    
    def _clear_dungeon_state(self) -> None:
        """Clear dungeon state when exiting"""
        from backend.services import game_state_service
        game_state_service.clear_dungeon_state_raw()