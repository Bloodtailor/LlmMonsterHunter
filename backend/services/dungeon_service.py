# Dungeon Service - Basic Dungeon Flow Management
# Handles dungeon entry, location generation, door choices, and exit

from typing import Dict, Any, List, Optional
from backend.services import game_state_service, generation_service
from backend.ai.llm.prompt_engine import get_template_config, build_prompt
import random

def enter_dungeon() -> Dict[str, Any]:
    """
    Start a dungeon adventure
    
    Returns:
        dict: Dungeon entry results with location and door choices
    """
    
    try:
        # Check if party is ready
        if not game_state_service.is_party_ready_for_dungeon():
            return {
                'success': False,
                'error': 'No active party set. Add monsters to your party before entering the dungeon.',
                'ready_for_dungeon': False
            }
        
        # Get party summary for atmospheric text
        party_summary = game_state_service.get_party_summary()
        
        print(f"🏰 Entering dungeon with: {party_summary}")
        
        # Generate atmospheric entry text using LLM
        entry_text_result = _generate_dungeon_entry_text(party_summary)
        if not entry_text_result['success']:
            return {
                'success': False,
                'error': f"Failed to generate entry text: {entry_text_result['error']}",
                'dungeon_entered': False
            }
        
        # Generate initial location
        location_result = _generate_random_location()
        if not location_result['success']:
            return {
                'success': False,
                'error': f"Failed to generate location: {location_result['error']}",
                'dungeon_entered': False
            }
        
        # Generate door choices (2 locations + 1 exit)
        doors_result = _generate_door_choices()
        if not doors_result['success']:
            return {
                'success': False,
                'error': f"Failed to generate doors: {doors_result['error']}",
                'dungeon_entered': False
            }
        
        # Set dungeon state
        dungeon_state = {
            'current_location': location_result['location'],
            'available_doors': doors_result['doors'],
            'entry_text': entry_text_result['text'],
            'party_summary': party_summary
        }
        
        # Update global game state (this would be in game_state_service)
        _set_dungeon_state(dungeon_state)
        
        return {
            'success': True,
            'dungeon_entered': True,
            'entry_text': entry_text_result['text'],
            'location': location_result['location'],
            'doors': doors_result['doors'],
            'party_summary': party_summary,
            'message': 'Welcome to the dungeon! Choose your path wisely.'
        }
        
    except Exception as e:
        return {
            'success': False,
            'error': str(e),
            'dungeon_entered': False
        }

def choose_door(door_choice: str) -> Dict[str, Any]:
    """
    Choose a door in the dungeon
    
    Args:
        door_choice (str): 'location_1', 'location_2', or 'exit'
        
    Returns:
        dict: Results of door choice
    """
    
    try:
        # Check if in dungeon
        current_state = _get_dungeon_state()
        if not current_state:
            return {
                'success': False,
                'error': 'Not currently in a dungeon',
                'in_dungeon': False
            }
        
        # Validate door choice
        available_doors = current_state.get('available_doors', [])
        valid_choices = [door['id'] for door in available_doors]
        
        if door_choice not in valid_choices:
            return {
                'success': False,
                'error': f'Invalid door choice. Available: {valid_choices}',
                'in_dungeon': True
            }
        
        # Find the chosen door
        chosen_door = next((door for door in available_doors if door['id'] == door_choice), None)
        
        if door_choice == 'exit':
            # Handle dungeon exit
            return _handle_dungeon_exit(chosen_door)
        else:
            # Handle location choice
            return _handle_location_choice(chosen_door)
        
    except Exception as e:
        return {
            'success': False,
            'error': str(e),
            'in_dungeon': _get_dungeon_state() is not None
        }

def get_dungeon_state() -> Dict[str, Any]:
    """
    Get current dungeon state
    
    Returns:
        dict: Current dungeon state or None if not in dungeon
    """
    
    try:
        state = _get_dungeon_state()
        
        if not state:
            return {
                'success': True,
                'in_dungeon': False,
                'state': None,
                'message': 'Not currently in a dungeon'
            }
        
        return {
            'success': True,
            'in_dungeon': True,
            'state': state,
            'party_summary': state.get('party_summary', 'Unknown party')
        }
        
    except Exception as e:
        return {
            'success': False,
            'error': str(e),
            'in_dungeon': False
        }

def _generate_dungeon_entry_text(party_summary: str) -> Dict[str, Any]:
    """Generate atmospheric dungeon entry text using template system"""
    
    try:
        # Get template configuration
        template_config = get_template_config('entry_atmosphere')
        if not template_config:
            return {
                'success': False,
                'error': 'Entry atmosphere template not found'
            }
        
        # Build prompt with variables
        prompt_text = build_prompt('entry_atmosphere', {'party_summary': party_summary})
        if not prompt_text:
            return {
                'success': False,
                'error': 'Failed to build entry atmosphere prompt'
            }
        
        # Generate using template configuration
        result = generation_service.text_generation_request(
            prompt=prompt_text,
            prompt_type='dungeon_generation',
            prompt_name='entry_atmosphere',
            parser_config=template_config['parser'],
            max_tokens=template_config['max_tokens'],
            temperature=template_config['temperature'],
            wait_for_completion=True
        )
        
        if result['success']:
            return {
                'success': True,
                'text': result['text'].strip()
            }
        else:
            return {
                'success': False,
                'error': result.get('error', 'LLM generation failed')
            }
            
    except Exception as e:
        return {
            'success': False,
            'error': str(e)
        }

def _generate_random_location() -> Dict[str, Any]:
    """Generate a random dungeon location using template system"""
    
    try:
        # Get template configuration
        template_config = get_template_config('random_location')
        if not template_config:
            return {
                'success': False,
                'error': 'Random location template not found'
            }
        
        # Build prompt (no variables needed for this template)
        prompt_text = build_prompt('random_location')
        if not prompt_text:
            return {
                'success': False,
                'error': 'Failed to build location prompt'
            }
        
        # Generate using template configuration
        result = generation_service.text_generation_request(
            prompt=prompt_text,
            prompt_type='dungeon_generation',
            prompt_name='random_location',
            parser_config=template_config['parser'],
            max_tokens=template_config['max_tokens'],
            temperature=template_config['temperature'],
            wait_for_completion=True
        )
        
        if result['success'] and result.get('parsing_success'):
            location_data = result['parsed_data']
            return {
                'success': True,
                'location': {
                    'name': location_data.get('name', 'Mysterious Chamber'),
                    'description': location_data.get('description', 'A place of unknown mysteries.')
                }
            }
        else:
            # Fallback location if LLM fails
            fallback_locations = [
                {"name": "Echoing Cavern", "description": "Ancient stone walls glisten with moisture as your footsteps echo endlessly into the darkness ahead."},
                {"name": "Crystal Grove", "description": "Luminescent crystals cast dancing shadows across twisted root formations that seem to pulse with inner life."},
                {"name": "Forgotten Sanctum", "description": "Weathered statues stand sentinel in this abandoned temple, their eyes seeming to follow your every movement."}
            ]
            
            location = random.choice(fallback_locations)
            print(f"⚠️ Using fallback location: {location['name']}")
            
            return {
                'success': True,
                'location': location
            }
            
    except Exception as e:
        return {
            'success': False,
            'error': str(e)
        }

def _generate_door_choices() -> Dict[str, Any]:
    """Generate 3 door choices (2 locations + 1 exit) using random_location template"""
    
    try:
        doors = []
        
        # Generate first location door
        location1_result = _generate_random_location()
        if location1_result['success']:
            location1 = location1_result['location']
            doors.append({
                'id': 'location_1',
                'type': 'location',
                'name': location1['name'],
                'description': location1['description']
            })
        else:
            print(f"⚠️ Failed to generate location 1, using fallback")
            doors.append({
                'id': 'location_1',
                'type': 'location',
                'name': 'Mysterious Chamber',
                'description': 'A dimly lit chamber with ancient stone walls and mysterious shadows.'
            })
        
        # Generate second location door
        location2_result = _generate_random_location()
        if location2_result['success']:
            location2 = location2_result['location']
            doors.append({
                'id': 'location_2',
                'type': 'location',
                'name': location2['name'],
                'description': location2['description']
            })
        else:
            print(f"⚠️ Failed to generate location 2, using fallback")
            doors.append({
                'id': 'location_2',
                'type': 'location',
                'name': 'Ancient Sanctum',
                'description': 'An old chamber filled with weathered statues and forgotten memories.'
            })
        
        # Always add the exit door
        doors.append({
            'id': 'exit',
            'type': 'exit',
            'name': 'Exit the Dungeon',
            'description': 'A familiar stone stairway leading back to the surface and safety of the outside world.'
        })
        
        print(f"✅ Generated doors: {[door['name'] for door in doors]}")
        
        return {
            'success': True,
            'doors': doors
        }
        
    except Exception as e:
        return {
            'success': False,
            'error': str(e)
        }

def _handle_location_choice(chosen_door: Dict[str, Any]) -> Dict[str, Any]:
    """Handle choosing a location door"""
    
    try:
        # Generate event text for this location
        location_name = chosen_door.get('name', 'Unknown Location')
        
        event_text_result = _generate_location_event_text(location_name)
        if not event_text_result['success']:
            event_text = f"You step through the {location_name} and find yourself in a new area of the dungeon."
        else:
            event_text = event_text_result['text']
        
        # Generate new location after the event
        new_location_result = _generate_random_location()
        if not new_location_result['success']:
            return {
                'success': False,
                'error': 'Failed to generate new location',
                'in_dungeon': True
            }
        
        # Generate new door choices
        new_doors_result = _generate_door_choices()
        if not new_doors_result['success']:
            return {
                'success': False,
                'error': 'Failed to generate new doors',
                'in_dungeon': True
            }
        
        # Update dungeon state
        new_state = {
            'current_location': new_location_result['location'],
            'available_doors': new_doors_result['doors'],
            'last_event_text': event_text,
            'party_summary': _get_dungeon_state().get('party_summary', 'Unknown party')
        }
        
        _set_dungeon_state(new_state)
        
        return {
            'success': True,
            'choice_made': chosen_door['name'],
            'event_text': event_text,
            'new_location': new_location_result['location'],
            'new_doors': new_doors_result['doors'],
            'continue_button': True,
            'in_dungeon': True
        }
        
    except Exception as e:
        return {
            'success': False,
            'error': str(e),
            'in_dungeon': True
        }

def _handle_dungeon_exit(chosen_door: Dict[str, Any]) -> Dict[str, Any]:
    """Handle choosing the exit door"""
    
    try:
        # Generate exit text
        party_summary = _get_dungeon_state().get('party_summary', 'your party')
        
        exit_text_result = _generate_dungeon_exit_text(party_summary)
        if not exit_text_result['success']:
            exit_text = f"You and {party_summary} emerge from the dungeon, glad to see daylight once again."
        else:
            exit_text = exit_text_result['text']
        
        # Clear dungeon state
        _clear_dungeon_state()
        
        return {
            'success': True,
            'choice_made': 'Exit the Dungeon',
            'exit_text': exit_text,
            'dungeon_completed': True,
            'in_dungeon': False,
            'return_to_home_button': True,
            'message': 'You have successfully exited the dungeon!'
        }
        
    except Exception as e:
        return {
            'success': False,
            'error': str(e),
            'in_dungeon': True
        }

def _generate_location_event_text(location_name: str) -> Dict[str, Any]:
    """Generate event text for a location using template system"""
    
    try:
        # Get template configuration
        template_config = get_template_config('location_event')
        if not template_config:
            return {
                'success': False,
                'error': 'Location event template not found'
            }
        
        # Build prompt with variables
        prompt_text = build_prompt('location_event', {'location_name': location_name})
        if not prompt_text:
            return {
                'success': False,
                'error': 'Failed to build location event prompt'
            }
        
        # Generate using template configuration
        result = generation_service.text_generation_request(
            prompt=prompt_text,
            prompt_type='dungeon_generation',
            prompt_name='location_event',
            parser_config=template_config['parser'],
            max_tokens=template_config['max_tokens'],
            temperature=template_config['temperature'],
            wait_for_completion=True
        )
        
        if result['success']:
            return {
                'success': True,
                'text': result['text'].strip()
            }
        else:
            return {
                'success': False,
                'error': result.get('error', 'LLM generation failed')
            }
            
    except Exception as e:
        return {
            'success': False,
            'error': str(e)
        }

def _generate_dungeon_exit_text(party_summary: str) -> Dict[str, Any]:
    """Generate exit text for leaving the dungeon using template system"""
    
    try:
        # Get template configuration
        template_config = get_template_config('exit_narrative')
        if not template_config:
            return {
                'success': False,
                'error': 'Exit narrative template not found'
            }
        
        # Build prompt with variables
        prompt_text = build_prompt('exit_narrative', {'party_summary': party_summary})
        if not prompt_text:
            return {
                'success': False,
                'error': 'Failed to build exit narrative prompt'
            }
        
        # Generate using template configuration
        result = generation_service.text_generation_request(
            prompt=prompt_text,
            prompt_type='dungeon_generation',
            prompt_name='exit_narrative',
            parser_config=template_config['parser'],
            max_tokens=template_config['max_tokens'],
            temperature=template_config['temperature'],
            wait_for_completion=True
        )
        
        if result['success']:
            return {
                'success': True,
                'text': result['text'].strip()
            }
        else:
            return {
                'success': False,
                'error': result.get('error', 'LLM generation failed')
            }
            
    except Exception as e:
        return {
            'success': False,
            'error': str(e)
        }

# Helper functions for dungeon state management
def _get_dungeon_state() -> Optional[Dict[str, Any]]:
    """Get current dungeon state from game_state_service"""
    game_state = game_state_service.get_game_state()
    return game_state.get('dungeon_state', {}).get('current_state')

def _set_dungeon_state(state: Dict[str, Any]) -> None:
    """Set dungeon state in game_state_service"""
    # This would update the global variables in game_state_service
    # For now, we'll use a simple approach
    import backend.services.game_state_service as gss
    gss._current_dungeon_state = state
    gss._in_dungeon = True

def _clear_dungeon_state() -> None:
    """Clear dungeon state when exiting"""
    import backend.services.game_state_service as gss
    gss._current_dungeon_state = None
    gss._in_dungeon = False