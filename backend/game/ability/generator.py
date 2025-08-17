# Ability Generator - TRULY SIMPLIFIED: No Validation
# Pure business logic - assumes all inputs are valid
# Eliminates defensive programming completely

from typing import Dict, Any
from backend.models.ability import Ability
from backend.models.monster import Monster
from backend.game.utils import build_and_generate

class AbilityGenerator:
    """Pure business logic - no validation"""

    def generate_ability(self, monster: Monster):
        
        variables = self._build_variables(monster.get_context_for_ability_generation())
        parsed_data = build_and_generate('generate_ability', 'ability_generation', variables)

        ability = Ability.create_from_llm_data(monster.id, parsed_data)
        ability.save()

        return ability
    
    def generate_ability_by_id(self, monster_id ):

        monster = Monster.query.get(monster_id)

        return self.generate_ability(monster)
    
    def _build_variables(self, monster_context: Dict[str, Any]) -> Dict[str, Any]:
        """Build prompt variables from monster context"""
        
        # Format existing abilities
        existing = monster_context.get('existing_abilities', [])
        abilities_text = "\n".join([
            f"- {a['name']} ({a.get('type', 'unknown')}): {a['description']}" for a in existing
        ]) if existing else "None (this will be their first ability)"
        
        # Format personality
        traits = monster_context.get('personality_traits', [])
        personality = ', '.join(traits) if traits else 'Mysterious'
        
        stats = monster_context.get('stats', {})
        return {
            'monster_name': monster_context.get('name', 'Unknown'),
            'monster_species': monster_context.get('species', 'Unknown Species'), 
            'monster_description': monster_context.get('description', 'A mysterious creature'),
            'monster_backstory': monster_context.get('backstory', 'Unknown origins'),
            'monster_health': stats.get('health', 100),
            'monster_attack': stats.get('attack', 20),
            'monster_defense': stats.get('defense', 15),
            'monster_speed': stats.get('speed', 10),
            'monster_personality': personality,
            'existing_abilities_text': abilities_text,
            'ability_count': monster_context.get('ability_count', 0)
        }