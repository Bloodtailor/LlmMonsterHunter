# Ability Service - GREATLY SIMPLIFIED: Minimal Trust Boundary
# Only validates what routes absolutely cannot handle
# Eliminates all redundant error checking

from typing import Dict, Any
from backend.game.ability.generator import AbilityGenerator
from backend.services.validators import validate_monster_exists
from backend.core.utils import validate_and_continue

# Create singleton generator instance
_generator = AbilityGenerator()

def generate_ability(monster_id: int) -> Dict[str, Any]:
    """Generate ability - only validate monster exists"""
    
    monster_validation = validate_monster_exists(monster_id)
    error_check = validate_and_continue(monster_validation, {'ability': None, 'monster_id': monster_id})
    if error_check:
        return error_check
    
    ability = _generator.generate_ability(monster_id)
    return ability.to_dict()