# Monster Generator - TRULY SIMPLIFIED: No Validation
# Pure business logic - assumes all inputs are valid
# Eliminates defensive programming

from backend.models.monster import Monster
from backend.models.ability import Ability
from backend.game.utils import build_and_generate
from backend.ai import gateway

class MonsterGenerator:
    """Pure business logic - no validation"""

    def generate_base_monster(self):
        """Generate monster - assumes valid inputs"""
        

        # Generate monster via LLM
        parsed_data = build_and_generate("detailed_monster", "monster_generation")
        
        # Create and save monster
        monster = Monster.create_from_llm_data(parsed_data)
        monster.save()

        # Reload monster with abilities and card art
        monster = Monster.get_monster_by_id(monster.id)
        
        return monster
    
    def generate_card_art(self, monster: Monster):
        """Generate and connect card art"""
        
        prompt_text = monster.get_context_for_image_generation()
        
        image_result = gateway.image_generation_request(
            prompt_text=prompt_text,
            prompt_type="monster_card_art",
            prompt_name="monster_generation"
        )

        image_path = image_result.get('image_path')
        
        monster.set_card_art(image_path)
        
        return image_path
    
    def generate_ability(self, monster: Monster):
        
        variables = self._build_ability_variables(monster)
        parsed_data = build_and_generate('generate_ability', 'ability_generation', variables)

        ability = Ability.create_from_llm_data(monster.id, parsed_data)
        ability.save()

        return ability
    
    def _build_ability_variables(self, monster: Monster):

        # Format existing abilities
        existing_abilities = monster.abilities
        abilities_text = "\n".join([
            f"- {ability.name} ({ability.ability_type}): {ability.description}" 
            for ability in existing_abilities
        ]) if existing_abilities else "None (this will be their first ability)"


        # Format personality
        personality = ', '.join(monster.personality_traits)

        return {
            'monster_name': monster.name,
            'monster_species': monster.species,
            'monster_description': monster.description,
            'monster_backstory': monster.backstory,
            'monster_health': monster.max_health,
            'monster_attack': monster.attack,
            'monster_defense': monster.defense,
            'monster_speed': monster.speed,
            'monster_personality': personality,
            'existing_abilities_text': abilities_text,
            'ability_count': len(monster.abilities)
        }
    
    def generate_ability_by_id(self, monster_id ):
        monster = Monster.query.get(monster_id)
        return self.generate_ability(monster)