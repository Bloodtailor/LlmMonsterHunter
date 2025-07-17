# Ability Generator - TRULY SIMPLIFIED: No Validation
# Pure business logic - assumes all inputs are valid
# Eliminates defensive programming completely
print(f"🔍 Loading {__file__}")
from typing import Dict, Any
from backend.models.ability import Ability
from backend.game.utils import build_and_generate
from backend.core.utils import success_response, error_response, print_success

class AbilityGenerator:
    """Pure business logic - no validation"""
    
    def generate_single_ability(self, monster_id: int) -> Dict[str, Any]:
        """Generate one ability - assumes monster exists"""
        
        # Get monster (assumes it exists)
        from backend.models.monster import Monster
        monster = Monster.get_monster_by_id(monster_id)
        
        print_success(f"Generating ability for {monster.name}")
        
        # Generate using utils
        variables = self._build_variables(monster.get_context_for_ability_generation())
        result = build_and_generate('generate_ability', 'ability_generation', variables)
        
        if not result['success']:
            return error_response("Ability generation failed", ability=None, monster_id=monster_id)
        
        # Create ability
        ability = Ability.create_from_llm_data(monster_id, result['parsed_data'])
        ability.save()
        
        print_success(f"Ability '{ability.name}' created for {monster.name}")
        return success_response({
            'ability': ability.to_dict(),
            'monster_id': monster_id,
            'generation_id': result.get('generation_id')
        })
    
    def generate_initial_abilities(self, monster_data: Dict[str, Any], monster_id: int) -> Dict[str, Any]:
        """Generate 2 starting abilities - assumes valid inputs"""
        
        print_success(f"Generating initial abilities for {monster_data['name']}")
        
        # Generate using utils
        variables = self._build_variables(monster_data)
        result = build_and_generate('generate_initial_abilities', 'ability_generation', variables)
        
        if not result['success']:
            return error_response("Initial abilities generation failed", abilities=[], abilities_created=0)
        
        # Create abilities
        abilities = []
        for key in ['ability1', 'ability2']:
            if key in result['parsed_data']:
                ability = Ability.create_from_llm_data(monster_id, result['parsed_data'][key])
                ability.save()
                abilities.append(ability.to_dict())
                print_success(f"Initial ability '{ability.name}' created")
        
        return success_response({
            'abilities': abilities,
            'abilities_created': len(abilities),
            'generation_id': result.get('generation_id')
        })
    
    def get_abilities_for_monster(self, monster_id: int) -> Dict[str, Any]:
        """Get all abilities - assumes monster exists"""
        
        abilities = Ability.get_abilities_for_monster(monster_id)
        return success_response({
            'abilities': [ability.to_dict() for ability in abilities],
            'count': len(abilities),
            'monster_id': monster_id
        })
    
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