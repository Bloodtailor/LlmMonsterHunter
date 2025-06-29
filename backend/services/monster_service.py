# Monster Service - CLEANED UP
# Handles monster generation with automatic abilities and card art
# Uses generation_service for both text and image generation

from typing import Dict, Any, Optional, List
from backend.models.monster import Monster
from backend.ai.llm.prompt_engine import get_template_config, build_prompt
from . import generation_service
from . import ability_service

def generate_monster(prompt_name: str = "detailed_monster", 
                    wait_for_completion: bool = True,
                    generate_card_art: bool = True) -> Dict[str, Any]:
    """
    Generate a new monster with automatic abilities and card art
    
    Args:
        prompt_name (str): Template name to use
        wait_for_completion (bool): Whether to wait for generation
        generate_card_art (bool): Whether to generate card art image
        
    Returns:
        dict: Complete monster generation results
    """
    
    try:
        # Get template and build prompt
        template_config = get_template_config(prompt_name)
        if not template_config:
            return {'success': False, 'error': f'Template not found: {prompt_name}', 'monster': None}
        
        prompt_text = build_prompt(prompt_name)
        if not prompt_text:
            return {'success': False, 'error': f'Failed to build prompt: {prompt_name}', 'monster': None}
        
        # Generate monster via LLM
        llm_result = generation_service.text_generation_request(
            prompt=prompt_text,
            prompt_type='monster_generation',
            prompt_name=prompt_name,
            parser_config=template_config['parser'],
            max_tokens=template_config['max_tokens'],
            temperature=template_config['temperature'],
            wait_for_completion=wait_for_completion
        )
        
        if not llm_result['success']:
            return {
                'success': False,
                'error': llm_result['error'],
                'monster': None,
                'generation_id': llm_result.get('generation_id')
            }
        
        if not wait_for_completion:
            return {
                'success': True,
                'message': 'Monster generation started',
                'monster': None,
                'generation_id': llm_result['generation_id']
            }
        
        # Check parsing success
        if not llm_result.get('parsing_success'):
            return {
                'success': False,
                'error': "Parsing failed",
                'monster': None,
                'generation_id': llm_result['generation_id']
            }
        
        # Create and save monster
        monster = Monster.create_from_llm_data(llm_result['parsed_data'])
        if not monster or not monster.save():
            return {
                'success': False,
                'error': 'Failed to save monster',
                'monster': None,
                'generation_id': llm_result['generation_id']
            }
        
        print(f"🐉 Monster '{monster.name}' created with ID: {monster.id}")
        
        # Generate starting abilities
        abilities_result = ability_service.generate_initial_abilities(
            monster_data=monster.get_context_for_ability_generation(),
            monster_id=monster.id
        )
        
        # Generate card art if requested
        card_art_result = {'success': False}
        if generate_card_art:
            card_art_result = _generate_and_connect_card_art(monster)
        
        # Reload monster with abilities and card art
        monster = Monster.get_monster_by_id(monster.id)
        
        return {
            'success': True,
            'monster': monster.to_dict(),
            'generation_id': llm_result['generation_id'],
            'generation_stats': {
                'tokens': llm_result.get('tokens', 0),
                'duration': llm_result.get('duration', 0),
                'abilities_generated': abilities_result.get('abilities_created', 0),
                'card_art_generated': card_art_result['success']
            }
        }
        
    except Exception as e:
        return {'success': False, 'error': str(e), 'monster': None}

def _generate_and_connect_card_art(monster: Monster) -> Dict[str, Any]:
    """Generate and connect card art to monster"""
    
    try:
        prompt_text = monster.get_context_for_image_generation()
        
        image_result = generation_service.image_generation_request(
            prompt_text=prompt_text,
            prompt_type="monster_card_art",
            prompt_name="monster_generation",
            wait_for_completion=True
        )
        
        if not image_result['success']:
            return {'success': False, 'error': image_result.get('error', 'Image generation failed')}
        
        relative_path = image_result.get('image_path')
        if not relative_path or not monster.set_card_art(relative_path):
            return {'success': False, 'error': 'Failed to save card art path'}
        
        return {
            'success': True,
            'image_path': relative_path,
            'generation_id': image_result.get('generation_id')
        }
            
    except Exception as e:
        return {'success': False, 'error': str(e)}

def generate_card_art_for_existing_monster(monster_id: int, wait_for_completion: bool = True) -> Dict[str, Any]:
    """Generate card art for an existing monster"""
    
    try:
        monster = Monster.get_monster_by_id(monster_id)
        if not monster:
            return {'success': False, 'error': f'Monster {monster_id} not found'}
        
        return _generate_and_connect_card_art(monster)
            
    except Exception as e:
        return {'success': False, 'error': str(e)}

def get_all_monsters(limit: int = 50, offset: int = 0) -> Dict[str, Any]:
    """Get all monsters with pagination"""
    try:
        monsters = Monster.query.order_by(Monster.created_at.desc()).offset(offset).limit(limit).all()
        total_count = Monster.query.count()
        
        return {
            'success': True,
            'monsters': [monster.to_dict() for monster in monsters],
            'total': total_count,
            'count': len(monsters),
            'pagination': {
                'limit': limit,
                'offset': offset,
                'has_more': offset + len(monsters) < total_count
            }
        }
        
    except Exception as e:
        return {'success': False, 'error': str(e), 'monsters': [], 'total': 0, 'count': 0}

def get_monster_by_id(monster_id: int) -> Dict[str, Any]:
    """Get specific monster by ID"""
    try:
        monster = Monster.query.get(monster_id)
        
        if not monster:
            return {'success': False, 'error': 'Monster not found', 'monster': None}
        
        return {'success': True, 'monster': monster.to_dict()}
        
    except Exception as e:
        return {'success': False, 'error': str(e), 'monster': None}

def get_available_templates() -> Dict[str, str]:
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

def get_monster_stats() -> Dict[str, Any]:
    """Get monster database statistics"""
    try:
        total_monsters = Monster.query.count()
        newest_monster = Monster.query.order_by(Monster.created_at.desc()).first()
        
        from backend.models.ability import Ability
        total_abilities = Ability.query.count()
        avg_abilities_per_monster = total_abilities / total_monsters if total_monsters > 0 else 0
        
        monsters_with_art = Monster.query.filter(Monster.card_art_path.isnot(None)).count()
        card_art_percentage = (monsters_with_art / total_monsters * 100) if total_monsters > 0 else 0
        
        return {
            'success': True,
            'total_monsters': total_monsters,
            'total_abilities': total_abilities,
            'avg_abilities_per_monster': round(avg_abilities_per_monster, 1),
            'monsters_with_card_art': monsters_with_art,
            'card_art_percentage': round(card_art_percentage, 1),
            'newest_monster': newest_monster.to_dict() if newest_monster else None,
            'available_templates': list(get_available_templates().keys())
        }
        
    except Exception as e:
        return {
            'success': False,
            'error': str(e),
            'total_monsters': 0,
            'total_abilities': 0,
            'monsters_with_card_art': 0
        }