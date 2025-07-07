# Ability Service - Thin Wrapper for Game Logic
# Delegates all business logic to backend/game/ability/generator.py

from typing import Dict, Any
from backend.game.ability.generator import AbilityGenerator

# Create singleton generator instance
_generator = AbilityGenerator()

def generate_ability(monster_id: int, wait_for_completion: bool = True) -> Dict[str, Any]:
    """
    Generate a single new ability for an existing monster
    Delegates to game logic layer
    """
    return _generator.generate_single_ability(monster_id, wait_for_completion)

def generate_initial_abilities(monster_data: Dict[str, Any], monster_id: int) -> Dict[str, Any]:
    """
    Generate 2 starting abilities for a newly created monster
    Delegates to game logic layer
    """
    return _generator.generate_initial_abilities(monster_data, monster_id)

def get_abilities_for_monster(monster_id: int) -> Dict[str, Any]:
    """
    Get all abilities for a specific monster
    Delegates to game logic layer
    """
    return _generator.get_abilities_for_monster(monster_id)