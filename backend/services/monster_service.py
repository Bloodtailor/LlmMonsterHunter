# Monster Service - TRULY SIMPLIFIED: Minimal Validation
# Only validates what routes can't handle
# Eliminates redundant checks

from typing import Dict, Any
from backend.game import MonsterGenerator, MonsterManager
from backend.utils import success_response, error_response

# Create singleton instances
_generator = MonsterGenerator()
_manager = MonsterManager()

def generate_monster(prompt_name: str = "detailed_monster", 
                    generate_card_art: bool = True) -> Dict[str, Any]:
    """Generate monster - only check template exists"""
    
    # Only validate what routes can't: template existence
    available_templates = _generator.get_available_templates()
    if prompt_name not in available_templates:
        return error_response(f"Template '{prompt_name}' not found", monster=None)
    
    # Everything else is trusted
    return _generator.generate_monster(prompt_name, generate_card_art)

def generate_card_art_for_existing_monster(monster_id: int) -> Dict[str, Any]:
    """Generate card art - only check monster exists"""
    
    # Only validate what routes can't: monster existence
    from backend.models.monster import Monster
    if not Monster.get_monster_by_id(monster_id):
        return error_response(f"Monster {monster_id} not found")
    
    return _generator.generate_card_art_for_existing_monster(monster_id)

def get_available_templates() -> Dict[str, str]:
    """Get templates - no validation needed"""
    return _generator.get_available_templates()

def get_all_monsters_enhanced(limit: int = 50, offset: int = 0, 
                            filter_type: str = 'all', sort_by: str = 'newest') -> Dict[str, Any]:
    """Get monsters - trust routes handled parameter validation"""
    return _manager.get_all_monsters_enhanced(limit, offset, filter_type, sort_by)

def get_enhanced_monster_stats(filter_type: str = 'all') -> Dict[str, Any]:
    """Get stats - trust routes handled parameter validation"""
    return _manager.get_enhanced_monster_stats(filter_type)

def get_monster_by_id(monster_id: int) -> Dict[str, Any]:
    """Get monster - trust routes handled integer validation"""
    return _manager.get_monster_by_id(monster_id)

def get_monster_card_art_info(monster_id: int) -> Dict[str, Any]:
    """Get card art info - trust routes handled integer validation"""
    from backend.models.monster import Monster
    
    monster = Monster.get_monster_by_id(monster_id)
    if not monster:
        return error_response(f"Monster {monster_id} not found", monster_id=monster_id)
    
    return success_response({
        'monster_id': monster_id,
        'card_art': monster.get_card_art_info()
    })

# LEGACY COMPATIBILITY
def get_all_monsters(limit: int = 50, offset: int = 0) -> Dict[str, Any]:
    """LEGACY: Basic pagination"""
    return get_all_monsters_enhanced(limit=limit, offset=offset)

def get_monster_stats() -> Dict[str, Any]:
    """LEGACY: Basic stats"""
    enhanced_stats = get_enhanced_monster_stats()
    if not enhanced_stats['success']:
        return enhanced_stats
    
    stats = enhanced_stats['stats']
    return success_response({
        'total_monsters': stats['total_monsters'],
        'total_abilities': stats['total_abilities'],
        'avg_abilities_per_monster': stats['avg_abilities_per_monster'],
        'monsters_with_card_art': stats['with_card_art'],
        'card_art_percentage': stats['card_art_percentage'],
        'newest_monster': stats['newest_monster'],
        'available_templates': list(get_available_templates().keys())
    })