# Monster Generator - Clean Monster Generation Logic

from typing import Dict, Any
from backend.models.monster import Monster
from backend.game.utils import (
    build_and_generate, validate_and_continue,
    error_response, success_response, print_success
)
from backend.game import AbilityGenerator
from backend.services import generation_service

class MonsterGenerator:
    """Clean monster generation - handles all creation logic"""
    
    def __init__(self):
        self.ability_generator = AbilityGenerator()
    
    def generate_monster(self, prompt_name: str = "detailed_monster", 
                        generate_card_art: bool = True) -> Dict[str, Any]:
        """
        Generate a new monster with automatic abilities and card art
        
        Args:
            prompt_name (str): Template name to use
            generate_card_art (bool): Whether to generate card art image
            
        Returns:
            dict: Complete monster generation results
        """
        
        try:
            print(f"🐉 Generating monster using template: {prompt_name}")
            
            # Generate monster via LLM using utils
            llm_result = build_and_generate(prompt_name, 'monster_generation')
            
            if not llm_result['success']:
                return error_response(llm_result['error'], monster=None, 
                                    generation_id=llm_result.get('generation_id'))
            
            # Check parsing success
            if not llm_result.get('parsing_success'):
                return error_response("Monster data parsing failed", monster=None,
                                    generation_id=llm_result['generation_id'])
            
            # Create and save monster
            monster = Monster.create_from_llm_data(llm_result['parsed_data'])
            if not monster or not monster.save():
                return error_response('Failed to save monster', monster=None,
                                    generation_id=llm_result['generation_id'])
            
            print_success(f"Monster '{monster.name}' created with ID: {monster.id}")
            
            # Generate starting abilities
            abilities_result = self.ability_generator.generate_initial_abilities(
                monster_data=monster.get_context_for_ability_generation(),
                monster_id=monster.id
            )
            
            # Generate card art if requested
            card_art_result = {'success': False}
            if generate_card_art:
                card_art_result = self._generate_and_connect_card_art(monster)
            
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
            
        except Exception as e:
            return error_response(str(e), monster=None)
    
    def generate_card_art_for_existing_monster(self, monster_id: int) -> Dict[str, Any]:
        """Generate card art for an existing monster"""
        
        try:
            from backend.game.utils import validate_monster_exists
            
            # Validate monster exists
            monster_validation = validate_monster_exists(monster_id)
            error_check = validate_and_continue(monster_validation)
            if error_check:
                return error_check
            
            monster = monster_validation['monster']
            print(f"🎨 Generating card art for {monster.name}")
            
            return self._generate_and_connect_card_art(monster)
                
        except Exception as e:
            return error_response(str(e))
    
    def _generate_and_connect_card_art(self, monster: Monster) -> Dict[str, Any]:
        """Generate and connect card art to monster - PRIVATE helper"""
        
        try:
            prompt_text = monster.get_context_for_image_generation()
            
            image_result = generation_service.image_generation_request(
                prompt_text=prompt_text,
                prompt_type="monster_card_art",
                prompt_name="monster_generation"
            )
            
            if not image_result['success']:
                return error_response(image_result.get('error', 'Image generation failed'))
            
            relative_path = image_result.get('image_path')
            if not relative_path or not monster.set_card_art(relative_path):
                return error_response('Failed to save card art path')
            
            print_success(f"Card art generated for {monster.name}")
            return success_response({
                'image_path': relative_path,
                'generation_id': image_result.get('generation_id')
            })
                
        except Exception as e:
            return error_response(str(e))
    
    def get_available_templates(self) -> Dict[str, str]:
        """Get available monster generation templates"""
        
        try:
            from backend.ai.llm.prompt_engine import get_prompt_engine
            
            engine = get_prompt_engine()
            templates = {}
            
            for name in engine.list_templates():
                template = engine.get_template(name)
                if template and template.category == 'monster_generation':
                    templates[name] = template.description
            
            return templates
            
        except Exception as e:
            return {}