# Monster Service - NEW PIPELINE
# Uses automatic parsing pipeline - much simpler!
# Just builds prompt and passes parser config to LLM service

from typing import Dict, Any, Optional, List
from backend.models.monster import Monster
from backend.llm.prompt_engine import get_template_config, build_prompt
from . import llm_service

def generate_monster(prompt_name: str = "basic_monster", 
                    wait_for_completion: bool = True) -> Dict[str, Any]:
    """
    Generate a new monster using AI with automatic parsing pipeline
    
    Args:
        prompt_name (str): Template name to use
        wait_for_completion (bool): Whether to wait for generation
        
    Returns:
        dict: Complete monster generation results
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
        
        # Step 3: Use NEW pipeline with automatic parsing!
        llm_result = llm_service.inference_request(
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
                'log_id': llm_result.get('log_id')
            }
        
        # If not waiting, return early
        if not wait_for_completion:
            return {
                'success': True,
                'message': 'Monster generation started',
                'monster': None,
                'log_id': llm_result['log_id']
            }
        
        # Step 4: Check if parsing succeeded
        if not llm_result.get('parsing_success'):
            return {
                'success': False,
                'error': f"Automatic parsing failed after {llm_result.get('attempt', 1)} attempts",
                'monster': None,
                'log_id': llm_result['log_id'],
                'raw_response': llm_result.get('text', '')
            }
        
        print(f"✅ Automatic parsing succeeded on attempt {llm_result.get('attempt', 1)}")
        
        # Step 5: Create and save monster (parsing already done!)
        monster = Monster.create_from_llm_data(llm_result['parsed_data'])
        
        if not monster or not monster.save():
            return {
                'success': False,
                'error': 'Failed to save monster to database',
                'monster': None,
                'log_id': llm_result['log_id'],
                'parsed_data': llm_result['parsed_data']
            }
        
        print(f"✅ Monster saved with ID: {monster.id}")
        
        # Step 6: Return success
        return {
            'success': True,
            'monster': monster.to_dict(),
            'log_id': llm_result['log_id'],
            'generation_stats': {
                'tokens': llm_result.get('tokens', 0),
                'duration': llm_result.get('duration', 0),
                'template_used': prompt_name,
                'attempts_needed': llm_result.get('attempt', 1),
                'parsing_automatic': True
            }
        }
        
    except Exception as e:
        print(f"❌ Monster Service error: {e}")
        return {
            'success': False,
            'error': f'Service error: {str(e)}',
            'monster': None
        }

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
        print(f"❌ Error fetching monsters: {e}")
        return {
            'success': False,
            'error': str(e),
            'monsters': [],
            'total': 0,
            'count': 0
        }

def get_monster_by_id(monster_id: int) -> Dict[str, Any]:
    """Get specific monster by ID"""
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
            'monster': monster.to_dict(),
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
        from backend.llm.prompt_engine import get_prompt_engine
        
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
    """Get monster database statistics"""
    try:
        total_monsters = Monster.query.count()
        newest_monster = Monster.query.order_by(Monster.created_at.desc()).first()
        
        return {
            'success': True,
            'total_monsters': total_monsters,
            'newest_monster': newest_monster.to_dict() if newest_monster else None,
            'available_templates': list(get_available_templates().keys())
        }
        
    except Exception as e:
        print(f"❌ Error getting monster stats: {e}")
        return {
            'success': False,
            'error': str(e),
            'total_monsters': 0
        }