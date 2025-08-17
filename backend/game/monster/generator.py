# Monster Generator - TRULY SIMPLIFIED: No Validation
# Pure business logic - assumes all inputs are valid
# Eliminates defensive programming

from typing import Dict, Any
from backend.models.monster import Monster
from backend.game.utils import build_and_generate
from backend.game.ability.generator import AbilityGenerator
from backend.ai import gateway

class MonsterGenerator:
    """Pure business logic - no validation"""
    
    def __init__(self):
        self.ability_generator = AbilityGenerator()

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