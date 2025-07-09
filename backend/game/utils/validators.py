# Game Validators - CONSOLIDATED: Simplified Validation Logic
# Used only by service layer (trust boundary)
# Returns consistent validation dictionaries for easy consumption

from typing import List, Dict, Any
from backend.models.monster import Monster

def validate_party_size(monster_ids: List[int], max_size: int = 4) -> Dict[str, Any]:
    """
    Validate party size constraints
    Used in game_state_service.set_active_party()
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

def validate_monster_exists(monster_id: int) -> Dict[str, Any]:
    """
    Validate that a monster exists in the database
    Used across multiple services for monster ID validation
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

def validate_monsters_are_following(monster_ids: List[int], following_list: List[int]) -> Dict[str, Any]:
    """
    Validate that all monsters are in the following list
    Used in game_state_service.set_active_party()
    """
    
    not_following = [mid for mid in monster_ids if mid not in following_list]
    
    if not_following:
        return {
            'valid': False,
            'not_following': not_following,
            'error': f'Monsters {not_following} are not following you'
        }
    
    return {'valid': True}

def validate_door_choice(door_choice: str, available_doors: List[Dict[str, Any]]) -> Dict[str, Any]:
    """
    Validate door choice in dungeon
    Used in dungeon_service.choose_door()
    """
    
    if not door_choice:
        return {
            'valid': False,
            'error': 'door_choice is required',
            'valid_choices': [door['id'] for door in available_doors]
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

def validate_following_monster_addition(monster_id: int, following_list: List[int]) -> Dict[str, Any]:
    """
    Validate adding a monster to the following list
    Used in game_state_service.add_following_monster()
    """
    
    # First validate monster exists
    monster_validation = validate_monster_exists(monster_id)
    if not monster_validation['valid']:
        return monster_validation
    
    # Check if already following
    if monster_id in following_list:
        monster = monster_validation['monster']
        return {
            'valid': False,
            'error': f'Monster {monster.name} is already following you',
            'monster': monster
        }
    
    return {'valid': True, 'monster': monster_validation['monster']}

# SIMPLIFIED: Common validation patterns
def validate_positive_integer(value: Any, field_name: str) -> Dict[str, Any]:
    """Validate that a value is a positive integer"""
    
    if not isinstance(value, int) or value <= 0:
        return {
            'valid': False,
            'error': f'{field_name} must be a positive integer'
        }
    
    return {'valid': True}

def validate_string_not_empty(value: Any, field_name: str) -> Dict[str, Any]:
    """Validate that a value is a non-empty string"""
    
    if not isinstance(value, str) or not value.strip():
        return {
            'valid': False,
            'error': f'{field_name} must be a non-empty string'
        }
    
    return {'valid': True}

def validate_choice_in_list(value: Any, choices: List[str], field_name: str) -> Dict[str, Any]:
    """Validate that a value is in a list of valid choices"""
    
    if value not in choices:
        return {
            'valid': False,
            'error': f'{field_name} must be one of: {choices}'
        }
    
    return {'valid': True}