# Service Layer Validators - ENHANCED: All Service Validation Logic
# Consolidates validation logic at the service layer where it belongs
# Updated with game state validation for database-backed system

from typing import List, Dict, Any
from backend.models.monster import Monster
from backend.models.game_state import GameState
from backend.utils import error_response

# === Monster Validators ===

def validate_monster_exists(monster_id: int) -> Dict[str, Any]:
    """
    Validate that a monster exists in the database
    Used across monster and ability services
    """
    
    if not isinstance(monster_id, int) or monster_id <= 0:
        return {
            'valid': False,
            'error': 'Invalid monster ID - must be a positive integer',
            'monster': None
        }
    
    monster = Monster.get_monster_by_id(monster_id)
    if not monster:
        return {
            'valid': False,
            'error': f'Monster {monster_id} not found',
            'monster': None
        }
    
    return {'valid': True, 'monster': monster}

def validate_monster_template(template_name: str, available_templates: Dict[str, str]) -> Dict[str, Any]:
    """
    Validate monster generation template exists
    Used in monster service
    """
    
    if not template_name or template_name not in available_templates:
        return {
            'valid': False,
            'error': f"Template '{template_name}' not found",
            'available_templates': list(available_templates.keys())
        }
    
    return {'valid': True}

def validate_monster_list_params(limit: int, offset: int, filter_type: str, sort_by: str) -> Dict[str, Any]:
    """
    Validate monster list parameters
    Used in monster service
    """
    
    # Validate limit
    if not isinstance(limit, int) or limit < 1 or limit > 1000:
        return {
            'valid': False,
            'error': 'Limit must be between 1 and 1000'
        }
    
    # Validate offset
    if not isinstance(offset, int) or offset < 0:
        return {
            'valid': False,
            'error': 'Offset must be 0 or greater'
        }
    
    # Validate filter
    valid_filters = ['all', 'with_art', 'without_art']
    if filter_type not in valid_filters:
        return {
            'valid': False,
            'error': f'Invalid filter parameter - must be: {", ".join(valid_filters)}'
        }
    
    # Validate sort
    valid_sorts = ['newest', 'oldest', 'name', 'species']
    if sort_by not in valid_sorts:
        return {
            'valid': False,
            'error': f'Invalid sort parameter - must be: {", ".join(valid_sorts)}'
        }
    
    return {'valid': True}

# === Game State Validators - DATABASE-BACKED ===

def validate_party_size(monster_ids: List[int], max_size: int = 4) -> Dict[str, Any]:
    """
    Validate party size constraints
    Used in game_state_service
    """
    
    if not isinstance(monster_ids, list):
        return {'valid': False, 'error': 'monster_ids must be a list', 'unique_ids': []}
    
    # Remove duplicates while preserving order
    unique_ids = []
    for mid in monster_ids:
        if mid not in unique_ids:
            unique_ids.append(mid)
    
    if len(unique_ids) > max_size:
        return {
            'valid': False,
            'error': f'Active party cannot exceed {max_size} monsters',
            'unique_ids': unique_ids
        }
    
    return {'valid': True, 'unique_ids': unique_ids}

def validate_monsters_are_following(monster_ids: List[int]) -> Dict[str, Any]:
    """
    Validate that all monsters are in the following list
    Used in game_state_service - now checks database
    """
    
    try:
        game_state = GameState.get_current_game_state()
        following_ids = game_state.get_following_monster_ids()
        
        not_following = [mid for mid in monster_ids if mid not in following_ids]
        
        if not_following:
            return {
                'valid': False,
                'not_following': not_following,
                'error': f'Monsters {not_following} are not following you'
            }
        
        return {'valid': True}
        
    except Exception as e:
        return {
            'valid': False,
            'error': f'Error checking following status: {str(e)}'
        }

def validate_following_monster_addition(monster_id: int) -> Dict[str, Any]:
    """
    Validate adding a monster to the following list
    Used in game_state_service - now checks database
    """
    
    # First validate monster exists
    monster_validation = validate_monster_exists(monster_id)
    if not monster_validation['valid']:
        return monster_validation
    
    try:
        # Check if already following
        game_state = GameState.get_current_game_state()
        following_ids = game_state.get_following_monster_ids()
        
        if monster_id in following_ids:
            monster = monster_validation['monster']
            return {
                'valid': False,
                'error': f'Monster {monster.name} is already following you',
                'monster': monster
            }
        
        return {'valid': True, 'monster': monster_validation['monster']}
        
    except Exception as e:
        return {
            'valid': False,
            'error': f'Error checking following status: {str(e)}',
            'monster': monster_validation['monster']
        }

def validate_following_monster_removal(monster_id: int) -> Dict[str, Any]:
    """
    Validate removing a monster from the following list
    Used in game_state_service - now checks database
    """
    
    # First validate monster exists
    monster_validation = validate_monster_exists(monster_id)
    if not monster_validation['valid']:
        return monster_validation
    
    try:
        # Check if monster is following
        game_state = GameState.get_current_game_state()
        following_ids = game_state.get_following_monster_ids()
        
        if monster_id not in following_ids:
            return {
                'valid': False,
                'error': f'Monster {monster_id} is not following you',
                'monster': monster_validation['monster']
            }
        
        return {'valid': True, 'monster': monster_validation['monster']}
        
    except Exception as e:
        return {
            'valid': False,
            'error': f'Error checking following status: {str(e)}',
            'monster': monster_validation['monster']
        }

# === Dungeon Validators ===

def validate_party_ready_for_dungeon() -> Dict[str, Any]:
    """
    Validate that active party is ready for dungeon entry
    Used in dungeon_service - now checks database
    """
    
    try:
        game_state = GameState.get_current_game_state()
        
        if not game_state.is_party_ready_for_dungeon():
            return {
                'valid': False,
                'error': 'No active party set. Add monsters to your party before entering the dungeon.',
                'ready_for_dungeon': False
            }
        
        return {'valid': True}
        
    except Exception as e:
        return {
            'valid': False,
            'error': f'Error checking party readiness: {str(e)}',
            'ready_for_dungeon': False
        }

def validate_door_choice(door_choice: str, available_doors: List[Dict[str, Any]]) -> Dict[str, Any]:
    """
    Validate door choice in dungeon
    Used in dungeon_service
    """
    
    if not door_choice:
        return {
            'valid': False,
            'error': 'door_choice is required',
            'valid_choices': [door['id'] for door in available_doors] if available_doors else []
        }
    
    if not available_doors:
        return {
            'valid': False,
            'error': 'No doors available',
            'valid_choices': []
        }
    
    valid_choices = [door['id'] for door in available_doors]
    
    if door_choice not in valid_choices:
        return {
            'valid': False,
            'error': f'Invalid door choice. Available: {valid_choices}',
            'valid_choices': valid_choices
        }
    
    # Find the chosen door
    chosen_door = next((door for door in available_doors if door['id'] == door_choice), None)
    
    return {'valid': True, 'door': chosen_door, 'valid_choices': valid_choices}

def validate_in_dungeon() -> Dict[str, Any]:
    """
    Validate that player is currently in a dungeon
    Used in dungeon_service - now checks database
    """
    
    try:
        game_state = GameState.get_current_game_state()
        
        if not game_state.in_dungeon or not game_state.dungeon_state:
            return {
                'valid': False,
                'error': 'Not currently in a dungeon',
                'in_dungeon': False
            }
        
        return {'valid': True, 'in_dungeon': True}
        
    except Exception as e:
        return {
            'valid': False,
            'error': f'Error checking dungeon status: {str(e)}',
            'in_dungeon': False
        }

# === Generation Validators ===

def validate_generation_result(result: Dict[str, Any], 
                             require_parsing: bool = True,
                             operation_name: str = "operation") -> Dict[str, Any]:
    """
    Validate generation service results with consistent error handling
    Used across monster, ability, and dungeon services
    """
    
    if not result.get('success'):
        return {
            'valid': False,
            'error': f"{operation_name} generation failed: {result.get('error', 'Unknown error')}",
            'stage': result.get('stage', 'unknown')
        }
    
    if require_parsing and not result.get('parsing_success'):
        attempts = result.get('attempt', 1)
        return {
            'valid': False,
            'error': f"{operation_name} parsing failed after {attempts} attempts",
            'stage': 'parsing'
        }
    
    return {'valid': True}