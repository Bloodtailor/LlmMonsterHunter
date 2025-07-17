# Monster Service - GREATLY SIMPLIFIED: Minimal Trust Boundary
# Only validates what routes absolutely cannot handle
# Eliminates all redundant error checking
print(f"🔍 Loading {__file__}")
from typing import Dict, Any
from backend.core.utils import success_response, error_response, validate_and_continue
from backend.game.monster.generator import MonsterGenerator
from backend.game.monster.manager import MonsterManager
from .validators import (
    validate_monster_exists,
    validate_monster_template, 
    validate_monster_list_params
)


# Create singleton instances
_generator = MonsterGenerator()
_manager = MonsterManager()

def generate_monster(prompt_name: str = "detailed_monster") -> Dict[str, Any]:
    """Generate monster - only validate template exists"""
    
    available_templates = _generator.get_available_templates()
    template_validation = validate_monster_template(prompt_name, available_templates)
    error_check = validate_and_continue(template_validation, {'monster': None})
    if error_check:
        return error_check
    
    return _generator.generate_monster(prompt_name)

def generate_card_art_for_existing_monster(monster_id: int) -> Dict[str, Any]:
    """Generate card art - only validate monster exists"""
    
    monster_validation = validate_monster_exists(monster_id)
    error_check = validate_and_continue(monster_validation)
    if error_check:
        return error_check
    
    return _generator.generate_card_art_for_existing_monster(monster_id)

def get_available_templates() -> Dict[str, str]:
    """Get templates - no validation needed"""
    return _generator.get_available_templates()

def get_all_monsters(limit: int = 50, offset: int = 0, 
                    filter_type: str = 'all', sort_by: str = 'newest') -> Dict[str, Any]:
    """Get monsters - validate complex parameters"""
    
    params_validation = validate_monster_list_params(limit, offset, filter_type, sort_by)
    error_check = validate_and_continue(params_validation)
    if error_check:
        return error_check
    
    return _manager.get_all_monsters(limit, offset, filter_type, sort_by)

def get_monster_stats(filter_type: str = 'all') -> Dict[str, Any]:
    """Get stats - validate filter parameter"""
    
    valid_filters = ['all', 'with_art', 'without_art']
    if filter_type not in valid_filters:
        return error_response(f'Invalid filter parameter - must be: {", ".join(valid_filters)}')
    
    return _manager.get_monster_stats(filter_type)

def get_monster_by_id(monster_id: int) -> Dict[str, Any]:
    """Get monster - delegate directly (routes handle integer validation)"""
    return _manager.get_monster_by_id(monster_id)

def get_monster_card_art_info(monster_id: int) -> Dict[str, Any]:
    """Get card art info - delegate directly (routes handle integer validation)"""
    
    monster_validation = validate_monster_exists(monster_id)
    error_check = validate_and_continue(monster_validation, {'monster_id': monster_id})
    if error_check:
        return error_check
    
    monster = monster_validation['monster']
    
    return success_response({
        'monster_id': monster_id,
        'card_art': monster.get_card_art_info()
    })