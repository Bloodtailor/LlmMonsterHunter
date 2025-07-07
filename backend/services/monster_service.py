# Monster Service - Thin Wrapper for Game Logic
# Delegates all business logic to backend/game/monster/

from typing import Dict, Any
from backend.game.monster.generator import MonsterGenerator
from backend.game.monster.manager import MonsterManager

# Create singleton instances
_generator = MonsterGenerator()
_manager = MonsterManager()

def generate_monster(prompt_name: str = "detailed_monster", 
                    generate_card_art: bool = True) -> Dict[str, Any]:
    """
    Generate a new monster with automatic abilities and card art
    Delegates to game logic layer
    """
    return _generator.generate_monster(prompt_name, generate_card_art)

def generate_card_art_for_existing_monster(monster_id: int) -> Dict[str, Any]:
    """Generate card art for an existing monster"""
    return _generator.generate_card_art_for_existing_monster(monster_id)

def get_available_templates() -> Dict[str, str]:
    """Get available monster generation templates"""
    return _generator.get_available_templates()

def get_all_monsters_enhanced(limit: int = 50, 
                            offset: int = 0,
                            filter_type: str = 'all',
                            sort_by: str = 'newest') -> Dict[str, Any]:
    """
    Get all monsters with enhanced server-side filtering, sorting, and pagination
    Delegates to game logic layer
    """
    return _manager.get_all_monsters_enhanced(limit, offset, filter_type, sort_by)

def get_enhanced_monster_stats(filter_type: str = 'all') -> Dict[str, Any]:
    """
    Get comprehensive monster statistics with optional filtering
    Delegates to game logic layer
    """
    return _manager.get_enhanced_monster_stats(filter_type)

def get_monster_by_id(monster_id: int) -> Dict[str, Any]:
    """Get specific monster by ID"""
    return _manager.get_monster_by_id(monster_id)

# LEGACY COMPATIBILITY: Keep existing methods for backward compatibility
def get_all_monsters(limit: int = 50, offset: int = 0) -> Dict[str, Any]:
    """
    LEGACY: Get all monsters with basic pagination
    Maintained for backward compatibility - new code should use get_all_monsters_enhanced
    """
    return _manager.get_all_monsters(limit, offset)

def get_monster_stats() -> Dict[str, Any]:
    """
    LEGACY: Get basic monster statistics
    Maintained for backward compatibility - new code should use get_enhanced_monster_stats
    """
    return _manager.get_monster_stats()