# Ability Service - TRULY SIMPLIFIED: Minimal Validation
# Only validates what routes can't handle
# Eliminates redundant checks

from typing import Dict, Any
from backend.game.ability.generator import AbilityGenerator
from backend.utils import error_response

# Create singleton generator instance
_generator = AbilityGenerator()

def generate_ability(monster_id: int) -> Dict[str, Any]:
    """Generate ability - only check monster exists"""
    
    # Only validate what routes can't: monster existence
    from backend.models.monster import Monster
    if not Monster.get_monster_by_id(monster_id):
        return error_response(f"Monster {monster_id} not found", ability=None, monster_id=monster_id)
    
    return _generator.generate_single_ability(monster_id)

def generate_initial_abilities(monster_data: Dict[str, Any], monster_id: int) -> Dict[str, Any]:
    """Generate initial abilities - trust the caller"""
    return _generator.generate_initial_abilities(monster_data, monster_id)

def get_abilities_for_monster(monster_id: int) -> Dict[str, Any]:
    """Get abilities - only check monster exists"""
    
    # Only validate what routes can't: monster existence
    from backend.models.monster import Monster
    if not Monster.get_monster_by_id(monster_id):
        return error_response(f"Monster {monster_id} not found", abilities=[], count=0, monster_id=monster_id)
    
    return _generator.get_abilities_for_monster(monster_id)