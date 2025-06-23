# Monster Service - UPDATED WITH CARD ART INTEGRATION
# Now properly connects generated card art to monsters
# Uses generation_service for both monster text and card art image generation

from typing import Dict, Any, Optional, List
from backend.models.monster import Monster
from backend.ai.llm.prompt_engine import get_template_config, build_prompt
from . import generation_service  # 🔧 UPDATED: was llm_service
from . import ability_service

def generate_monster(prompt_name: str = "basic_monster", 
                    wait_for_completion: bool = True,
                    generate_card_art: bool = True) -> Dict[str, Any]:
    """
    Generate a new monster using AI with automatic parsing pipeline
    NOW INCLUDES: Automatic generation of 2 starting abilities + card art
    
    Args:
        prompt_name (str): Template name to use
        wait_for_completion (bool): Whether to wait for generation
        generate_card_art (bool): Whether to generate card art image
        
    Returns:
        dict: Complete monster generation results including abilities and card art
    """
    
    try:
        print(f"🐉 Monster Service: Generating monster with template '{prompt_name}'")
        
        # Step 1: Get template configuration
        template_config = get_template_config(prompt_name)
        if not template_config:
            return {
                'success': False,
                'error': f'Template not found: {prompt_name}',
                'monster': None
            }
        
        # Step 2: Build prompt from template
        prompt_text = build_prompt(prompt_name)
        if not prompt_text:
            return {
                'success': False,
                'error': f'Failed to build prompt from template: {prompt_name}',
                'monster': None
            }
        
        print(f"✅ Built prompt: {len(prompt_text)} characters")
        
        # Step 3: Use unified generation service for LLM inference
        llm_result = generation_service.text_generation_request(  # 🔧 UPDATED: new service
            prompt=prompt_text,
            prompt_type='monster_generation',
            prompt_name=prompt_name,
            parser_config=template_config['parser'],  # Automatic parsing!
            max_tokens=template_config['max_tokens'],
            temperature=template_config['temperature'],
            wait_for_completion=wait_for_completion
        )
        
        if not llm_result['success']:
            return {
                'success': False,
                'error': llm_result['error'],
                'monster': None,
                'generation_id': llm_result.get('generation_id')  # 🔧 UPDATED: was log_id
            }
        
        # If not waiting, return early
        if not wait_for_completion:
            return {
                'success': True,
                'message': 'Monster generation started',
                'monster': None,
                'generation_id': llm_result['generation_id']  # 🔧 UPDATED: was log_id
            }
        
        # Step 4: Check if parsing succeeded
        if not llm_result.get('parsing_success'):
            return {
                'success': False,
                'error': f"Automatic parsing failed after {llm_result.get('attempt', 1)} attempts",
                'monster': None,
                'generation_id': llm_result['generation_id'],  # 🔧 UPDATED: was log_id
                'raw_response': llm_result.get('text', '')
            }
        
        print(f"✅ Automatic parsing succeeded on attempt {llm_result.get('attempt', 1)}")
        
        # Step 5: TEMPLATE-SPECIFIC DATA TRANSFORMATION
        parsed_data = llm_result['parsed_data']
        transformed_data = _transform_parsed_data(prompt_name, parsed_data)
        
        # Step 6: Create and save monster
        monster = Monster.create_from_llm_data(transformed_data)
        
        if not monster or not monster.save():
            return {
                'success': False,
                'error': 'Failed to save monster to database',
                'monster': None,
                'generation_id': llm_result['generation_id'],  # 🔧 UPDATED: was log_id
                'parsed_data': transformed_data
            }
        
        print(f"✅ Monster saved with ID: {monster.id}")
        
        # Step 7: 🔧 NEW: Generate 2 starting abilities for the monster
        abilities_result = ability_service.generate_initial_abilities(
            monster_data=monster.get_context_for_ability_generation(),
            monster_id=monster.id
        )
        
        if abilities_result['success']:
            abilities_created = abilities_result['abilities_created']
            print(f"✅ Generated {abilities_created} starting abilities for {monster.name}")
        else:
            print(f"⚠️ Failed to generate starting abilities: {abilities_result['error']}")
            # Don't fail the entire monster creation if abilities fail
        
        # Step 8: 🔧 UPDATED: Generate and connect card art
        card_art_result = {'success': False, 'message': 'Card art generation disabled'}
        
        if generate_card_art:
            card_art_result = _generate_and_connect_card_art(monster)
            
            if card_art_result['success']:
                print(f"✅ Generated and connected card art for {monster.name}")
            else:
                print(f"⚠️ Card art generation failed: {card_art_result['error']}")
                # Don't fail monster creation if card art fails
        
        # Step 9: Reload monster to include the new abilities and card art
        monster = Monster.get_monster_by_id(monster.id)
        
        # Step 10: Return success with complete data
        return {
            'success': True,
            'monster': monster.to_dict(),  # Now includes abilities and card art!
            'generation_id': llm_result['generation_id'],  # 🔧 UPDATED: was log_id
            'generation_stats': {
                'tokens': llm_result.get('tokens', 0),
                'duration': llm_result.get('duration', 0),
                'template_used': prompt_name,
                'attempts_needed': llm_result.get('attempt', 1),
                'parsing_automatic': True,
                'data_transformed': prompt_name == 'basic_monster',
                'abilities_generated': abilities_result.get('abilities_created', 0),
                'abilities_success': abilities_result['success'],
                'card_art_generated': card_art_result['success'],
                'card_art_path': card_art_result.get('image_path')
            },
            'abilities_generation_id': abilities_result.get('generation_id'),  # 🔧 UPDATED: was log_id
            'card_art_generation_id': card_art_result.get('generation_id')
        }
        
    except Exception as e:
        print(f"❌ Monster Service error: {e}")
        return {
            'success': False,
            'error': f'Service error: {str(e)}',
            'monster': None
        }

def _generate_and_connect_card_art(monster: Monster) -> Dict[str, Any]:
    """
    Generate card art for a monster and connect it to the monster
    
    Args:
        monster (Monster): Monster instance to generate art for
        
    Returns:
        dict: Card art generation results
    """
    
    try:
        print(f"🎨 Generating card art for {monster.name}")
        
        # Step 1: Build prompt text from monster data
        prompt_text = monster.get_context_for_image_generation()
        
        print(f"✅ Built image prompt: {prompt_text[:100]}...")
        
        # Step 2: Generate card art using generic image generation
        image_result = generation_service.image_generation_request(
            prompt_text=prompt_text,
            prompt_type="monster_card_art",  # This will be the folder name
            prompt_name="monster_generation",  # This is the workflow to use
            wait_for_completion=True  # Wait for the actual generation
        )
        
        if not image_result['success']:
            return {
                'success': False,
                'error': image_result.get('error', 'Image generation failed'),
                'generation_id': image_result.get('generation_id'),
                'monster_id': monster.id
            }
        
        # Step 3: Connect the generated image to the monster
        relative_path = image_result.get('image_path')  # This is now the relative path
        
        if not relative_path:
            return {
                'success': False,
                'error': 'No image path returned from generation',
                'generation_id': image_result.get('generation_id'),
                'monster_id': monster.id
            }
        
        # Step 4: Update monster with card art path
        if monster.set_card_art(relative_path):
            print(f"✅ Connected card art to monster: {relative_path}")
            
            return {
                'success': True,
                'image_path': relative_path,
                'generation_id': image_result.get('generation_id'),
                'monster_id': monster.id,
                'execution_time': image_result.get('execution_time', 0),
                'workflow_used': image_result.get('workflow_used'),
                'prompt_type_used': image_result.get('prompt_type_used')
            }
        else:
            return {
                'success': False,
                'error': 'Failed to save card art path to monster',
                'image_path': relative_path,
                'generation_id': image_result.get('generation_id'),
                'monster_id': monster.id
            }
            
    except Exception as e:
        print(f"❌ Card art generation error for monster {monster.id}: {e}")
        return {
            'success': False,
            'error': str(e),
            'monster_id': monster.id
        }

def generate_card_art_for_existing_monster(monster_id: int, wait_for_completion: bool = True) -> Dict[str, Any]:
    """
    Generate card art for an existing monster
    Useful for adding card art to monsters created before this feature
    
    Args:
        monster_id (int): ID of monster to generate art for
        wait_for_completion (bool): Whether to wait for generation
        
    Returns:
        dict: Card art generation results
    """
    
    try:
        # Get the monster
        monster = Monster.get_monster_by_id(monster_id)
        if not monster:
            return {
                'success': False,
                'error': f'Monster {monster_id} not found',
                'monster_id': monster_id
            }
        
        print(f"🎨 Generating card art for existing monster: {monster.name}")
        
        # Generate and connect card art
        if wait_for_completion:
            return _generate_and_connect_card_art(monster)
        else:
            # For async generation, we'd need to modify _generate_and_connect_card_art
            # For now, just do synchronous generation
            result = _generate_and_connect_card_art(monster)
            
            if result['success']:
                result['message'] = 'Card art generation completed'
            
            return result
            
    except Exception as e:
        print(f"❌ Error generating card art for monster {monster_id}: {e}")
        return {
            'success': False,
            'error': str(e),
            'monster_id': monster_id
        }

def _transform_parsed_data(prompt_name: str, parsed_data: Dict[str, Any]) -> Dict[str, Any]:
    """
    Transform parsed data based on template type
    Handles differences between template output formats and Monster model expectations
    
    Args:
        prompt_name (str): Template name that was used
        parsed_data (dict): Raw parsed data from LLM
        
    Returns:
        dict: Transformed data ready for Monster.create_from_llm_data()
    """
    
    if prompt_name == 'basic_monster':
        # Basic monster returns flat JSON: {"name": "...", "description": "..."}
        # But Monster model expects: {"basic_info": {"name": "...", "description": "..."}}
        print(f"🔄 Wrapping basic_monster data in basic_info structure")
        
        return {
            'basic_info': {
                'name': parsed_data.get('name', 'Unnamed Monster'),
                'description': parsed_data.get('description', 'A mysterious creature.')
            }
        }
    
    elif prompt_name == 'detailed_monster':
        # Detailed monster should already be in the correct nested format
        # Just pass it through as-is
        print(f"✅ Using detailed_monster data as-is (nested format)")
        return parsed_data
    
    else:
        # Unknown template - assume it's in correct format
        print(f"⚠️ Unknown template '{prompt_name}', using data as-is")
        return parsed_data

def get_all_monsters(limit: int = 50, offset: int = 0) -> Dict[str, Any]:
    """Get all monsters with pagination - NOW INCLUDES ABILITIES AND CARD ART"""
    try:
        monsters = Monster.query.order_by(Monster.created_at.desc()).offset(offset).limit(limit).all()
        total_count = Monster.query.count()
        
        return {
            'success': True,
            'monsters': [monster.to_dict() for monster in monsters],  # Now includes abilities and card art!
            'total': total_count,
            'count': len(monsters),
            'pagination': {
                'limit': limit,
                'offset': offset,
                'has_more': offset + len(monsters) < total_count
            }
        }
        
    except Exception as e:
        print(f"❌ Error fetching monsters: {e}")
        return {
            'success': False,
            'error': str(e),
            'monsters': [],
            'total': 0,
            'count': 0
        }

def get_monster_by_id(monster_id: int) -> Dict[str, Any]:
    """Get specific monster by ID - NOW INCLUDES ABILITIES AND CARD ART"""
    try:
        monster = Monster.query.get(monster_id)
        
        if not monster:
            return {
                'success': False,
                'error': 'Monster not found',
                'monster': None
            }
        
        return {
            'success': True,
            'monster': monster.to_dict(),  # Now includes abilities and card art!
            'error': None
        }
        
    except Exception as e:
        print(f"❌ Error fetching monster {monster_id}: {e}")
        return {
            'success': False,
            'error': str(e),
            'monster': None
        }

def get_available_templates() -> Dict[str, str]:
    """Get available monster generation templates"""
    try:
        from backend.ai.llm.prompt_engine import get_prompt_engine  # 🔧 UPDATED: ai folder path
        
        engine = get_prompt_engine()
        templates = {}
        
        for name in engine.list_templates():
            template = engine.get_template(name)
            if template and template.category == 'monster_generation':
                templates[name] = template.description
        
        return templates
        
    except Exception as e:
        print(f"❌ Error getting templates: {e}")
        return {}

def get_monster_stats() -> Dict[str, Any]:
    """Get monster database statistics - NOW INCLUDES ABILITY AND CARD ART STATS"""
    try:
        total_monsters = Monster.query.count()
        newest_monster = Monster.query.order_by(Monster.created_at.desc()).first()
        
        # Get ability statistics
        from backend.models.ability import Ability
        total_abilities = Ability.query.count()
        avg_abilities_per_monster = total_abilities / total_monsters if total_monsters > 0 else 0
        
        # Get card art statistics
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
        print(f"❌ Error getting monster stats: {e}")
        return {
            'success': False,
            'error': str(e),
            'total_monsters': 0,
            'total_abilities': 0,
            'monsters_with_card_art': 0
        }