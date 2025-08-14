# Monster Generator - TRULY SIMPLIFIED: No Validation
# Pure business logic - assumes all inputs are valid
# Eliminates defensive programming

from typing import Dict, Any
from backend.models.monster import Monster
from backend.game.utils import build_and_generate, IMAGE_GENERATION_ENABLED
from backend.core.utils import success_response, error_response, print_success
from backend.game.ability.generator import AbilityGenerator
from backend.ai import gateway

class MonsterGenerator:
    """Pure business logic - no validation"""
    
    def __init__(self):
        self.ability_generator = AbilityGenerator()
    
    def generate_monster(self, prompt_name: str = "detailed_monster") -> Dict[str, Any]:
        """Generate monster - assumes valid inputs"""
        
        print_success(f"Generating monster using template: {prompt_name}")
        
        # Generate monster via LLM
        llm_result = build_and_generate(prompt_name, 'monster_generation')
        if not llm_result['success'] or not llm_result.get('parsing_success'):
            return error_response("Monster generation failed", monster=None)
        
        # Create and save monster
        monster = Monster.create_from_llm_data(llm_result['parsed_data'])
        monster.save()
        
        print_success(f"Monster '{monster.name}' created with ID: {monster.id}")
        
        # Generate starting abilities
        abilities_result = self.ability_generator.generate_initial_abilities(
            monster.get_context_for_ability_generation(), monster.id
        )
        
        # Generate card art if requested
        card_art_result = {'success': False}
        if IMAGE_GENERATION_ENABLED:
            card_art_result = self._generate_card_art(monster)
        
        # Reload monster with abilities and card art
        monster = Monster.get_monster_by_id(monster.id)
        
        return success_response({
            'monster': monster.to_dict(),
            'generation_id': llm_result['generation_id'],
            'generation_stats': {
                'tokens': llm_result.get('tokens', 0),
                'duration': llm_result.get('duration', 0),
                'abilities_generated': abilities_result.get('abilities_created', 0),
                'card_art_generated': card_art_result['success']
            }
        })
    
    def generate_card_art_for_existing_monster(self, monster_id: int) -> Dict[str, Any]:
        """Generate card art - assumes monster exists"""
        
        monster = Monster.get_monster_by_id(monster_id)
        print_success(f"Generating card art for {monster.name}")
        
        return self._generate_card_art(monster)
    
    def _generate_card_art(self, monster: Monster) -> Dict[str, Any]:
        """Generate and connect card art"""
        
        prompt_text = monster.get_context_for_image_generation()
        
        image_result = gateway.image_generation_request(
            prompt_text=prompt_text,
            prompt_type="monster_card_art",
            prompt_name="monster_generation"
        )
        
        if not image_result['success']:
            return error_response("Image generation failed")
        
        monster.set_card_art(image_result.get('image_path'))
        
        print_success(f"Card art generated for {monster.name}")
        return success_response({
            'image_path': image_result.get('image_path'),
            'generation_id': image_result.get('generation_id')
        })
    
    def get_available_templates(self) -> Dict[str, str]:
        """Get available templates"""
        
        try:
            from backend.ai.llm.prompt_engine import get_prompt_engine
            
            engine = get_prompt_engine()
            templates = {}
            
            for name in engine.list_templates():
                template = engine.get_template(name)
                if template and template.category == 'monster_generation':
                    templates[name] = template.description
            
            return templates
            
        except Exception:
            return {}