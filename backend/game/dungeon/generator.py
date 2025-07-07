# Dungeon Generator - Clean Text Generation Logic

from typing import Dict, Any
import random
from backend.game.utils import (
    build_and_generate,
    error_response, success_response, print_warning, print_success
)

class DungeonGenerator:
    """Clean dungeon text generation - handles all LLM-based content creation"""
    
    def generate_entry_text(self, party_summary: str) -> Dict[str, Any]:
        """Generate atmospheric dungeon entry text using template system"""
        
        try:
            variables = {'party_summary': party_summary}
            result = build_and_generate('entry_atmosphere', 'dungeon_generation', variables)
            
            if result['success']:
                return success_response({
                    'text': result['text'].strip(),
                    'generation_id': result.get('generation_id')
                })
            else:
                return error_response(result.get('error', 'Entry text generation failed'))
                
        except Exception as e:
            return error_response(str(e))
    
    def generate_random_location(self) -> Dict[str, Any]:
        """Generate a random dungeon location using template system"""
        
        try:
            result = build_and_generate('random_location', 'dungeon_generation')
            
            if result['success'] and result.get('parsing_success'):
                location_data = result['parsed_data']
                return success_response({
                    'location': {
                        'name': location_data.get('name', 'Mysterious Chamber'),
                        'description': location_data.get('description', 'A place of unknown mysteries.')
                    },
                    'generation_id': result.get('generation_id')
                })
            else:
                # Fallback location if LLM fails
                fallback_location = self._get_fallback_location()
                print_warning(f"Using fallback location: {fallback_location['name']}")
                
                return success_response({
                    'location': fallback_location,
                    'generation_id': None
                })
                
        except Exception as e:
            # Use fallback on any error
            fallback_location = self._get_fallback_location()
            print_warning(f"Error generating location, using fallback: {fallback_location['name']}")
            
            return success_response({
                'location': fallback_location,
                'generation_id': None
            })
    
    def generate_door_choices(self) -> Dict[str, Any]:
        """Generate 3 door choices (2 locations + 1 exit) using random_location template"""
        
        try:
            doors = []
            
            # Generate first location door
            location1_result = self.generate_random_location()
            if location1_result['success']:
                location1 = location1_result['location']
                doors.append({
                    'id': 'location_1',
                    'type': 'location',
                    'name': location1['name'],
                    'description': location1['description']
                })
            else:
                print_warning("Failed to generate location 1, using fallback")
                doors.append({
                    'id': 'location_1',
                    'type': 'location',
                    'name': 'Mysterious Chamber',
                    'description': 'A dimly lit chamber with ancient stone walls and mysterious shadows.'
                })
            
            # Generate second location door
            location2_result = self.generate_random_location()
            if location2_result['success']:
                location2 = location2_result['location']
                doors.append({
                    'id': 'location_2',
                    'type': 'location',
                    'name': location2['name'],
                    'description': location2['description']
                })
            else:
                print_warning("Failed to generate location 2, using fallback")
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
            
            print_success(f"Generated doors: {[door['name'] for door in doors]}")
            
            return success_response({'doors': doors})
            
        except Exception as e:
            return error_response(str(e))
    
    def generate_location_event_text(self, location_name: str) -> Dict[str, Any]:
        """Generate event text for a location using template system"""
        
        try:
            variables = {'location_name': location_name}
            result = build_and_generate('location_event', 'dungeon_generation', variables)
            
            if result['success']:
                return success_response({
                    'text': result['text'].strip(),
                    'generation_id': result.get('generation_id')
                })
            else:
                return error_response(result.get('error', 'Location event generation failed'))
                
        except Exception as e:
            return error_response(str(e))
    
    def generate_exit_text(self, party_summary: str) -> Dict[str, Any]:
        """Generate exit text for leaving the dungeon using template system"""
        
        try:
            variables = {'party_summary': party_summary}
            result = build_and_generate('exit_narrative', 'dungeon_generation', variables)
            
            if result['success']:
                return success_response({
                    'text': result['text'].strip(),
                    'generation_id': result.get('generation_id')
                })
            else:
                return error_response(result.get('error', 'Exit text generation failed'))
                
        except Exception as e:
            return error_response(str(e))
    
    def _get_fallback_location(self) -> Dict[str, str]:
        """Get a random fallback location when LLM generation fails"""
        
        fallback_locations = [
            {
                "name": "Echoing Cavern", 
                "description": "Ancient stone walls glisten with moisture as your footsteps echo endlessly into the darkness ahead."
            },
            {
                "name": "Crystal Grove", 
                "description": "Luminescent crystals cast dancing shadows across twisted root formations that seem to pulse with inner life."
            },
            {
                "name": "Forgotten Sanctum", 
                "description": "Weathered statues stand sentinel in this abandoned temple, their eyes seeming to follow your every movement."
            },
            {
                "name": "Whispering Chamber", 
                "description": "Strange murmurs drift through the air in this circular room, though no source can be seen."
            },
            {
                "name": "Moonlit Corridor", 
                "description": "Pale light filters down through cracks in the ceiling, illuminating dust motes that dance like tiny spirits."
            }
        ]
        
        return random.choice(fallback_locations)