# Monster Service - Business logic for monster creation and management
# Uses LLM service for generation, handles parsing and database operations

from typing import Dict, Any, Optional, List
from backend.models.monster import Monster
from backend.llm.prompt_engine import get_template_config, build_prompt
from backend.llm.parser import parse_response
from . import llm_service

def generate_monster(prompt_name: str = "basic_monster", 
                    wait_for_completion: bool = True) -> Dict[str, Any]:
    """
    Generate a new monster using AI
    
    Args:
        prompt_name (str): Template name to use ('basic_monster', 'detailed_monster', etc.)
        wait_for_completion (bool): Whether to wait for generation to complete
        
    Returns:
        dict: {
            'success': bool,
            'monster': dict or None,  # Monster data if successful
            'request_id': str,
            'log_id': int,
            'error': str or None
        }
    """
    
    try:
        print(f"🐉 Monster Service: Generating monster with template '{prompt_name}'")
        
        # Step 1: Get and validate template
        template_config = get_template_config(prompt_name)
        if not template_config:
            return {
                'success': False,
                'error': f'Template not found: {prompt_name}',
                'monster': None,
                'request_id': None,
                'log_id': None
            }
        
        # Step 2: Build prompt from template
        prompt_text = build_prompt(prompt_name)
        if not prompt_text:
            return {
                'success': False,
                'error': f'Failed to build prompt from template: {prompt_name}',
                'monster': None,
                'request_id': None,
                'log_id': None
            }
        
        print(f"✅ Built prompt from template: {len(prompt_text)} characters")
        
        # Step 3: Request LLM generation (ultra-simple now!)
        llm_result = llm_service.inference_request(
            prompt_text,
            prompt_type='monster_generation',
            prompt_name=prompt_name,
            max_tokens=template_config['max_tokens'],
            temperature=template_config['temperature'],
            wait_for_completion=wait_for_completion
        )
        
        if not llm_result['success']:
            return {
                'success': False,
                'error': llm_result['error'],
                'monster': None,
                'request_id': llm_result.get('request_id'),
                'log_id': llm_result.get('log_id')
            }
        
        # If not waiting for completion, return early
        if not wait_for_completion:
            return {
                'success': True,
                'message': 'Monster generation started',
                'monster': None,
                'request_id': llm_result['request_id'],
                'log_id': llm_result['log_id'],
                'queue_position': llm_result.get('queue_position')
            }
        
        # Step 4: Parse the generated response
        if 'text' not in llm_result:
            return {
                'success': False,
                'error': 'No text generated',
                'monster': None,
                'request_id': llm_result['request_id'],
                'log_id': llm_result['log_id']
            }
        
        print(f"✅ LLM generated {len(llm_result['text'])} characters")
        
        parse_result = parse_response(
            response_text=llm_result['text'],
            parser_config=template_config['parser']
        )
        
        if not parse_result.success:
            return {
                'success': False,
                'error': f"Failed to parse monster data: {parse_result.error}",
                'monster': None,
                'request_id': llm_result['request_id'],
                'log_id': llm_result['log_id'],
                'raw_response': llm_result['text']  # For debugging
            }
        
        print(f"✅ Successfully parsed monster data")
        
        # Step 5: Create and save monster to database
        monster = Monster.create_from_llm_data(parse_result.data)
        
        if not monster or not monster.save():
            return {
                'success': False,
                'error': 'Failed to save monster to database',
                'monster': None,
                'request_id': llm_result['request_id'],
                'log_id': llm_result['log_id'],
                'parsed_data': parse_result.data  # For debugging
            }
        
        print(f"✅ Monster saved to database with ID: {monster.id}")
        
        # Step 6: Return success with monster data
        return {
            'success': True,
            'monster': monster.to_dict(),
            'request_id': llm_result['request_id'],
            'log_id': llm_result['log_id'],
            'generation_stats': {
                'tokens': llm_result.get('tokens', 0),
                'duration': llm_result.get('duration', 0),
                'template_used': prompt_name
            }
        }
        
    except Exception as e:
        print(f"❌ Monster Service error: {e}")
        import traceback
        traceback.print_exc()
        
        return {
            'success': False,
            'error': f'Service error: {str(e)}',
            'monster': None,
            'request_id': None,
            'log_id': None
        }

def get_all_monsters(limit: int = 50, offset: int = 0) -> Dict[str, Any]:
    """
    Get all monsters from database with pagination
    
    Args:
        limit (int): Maximum number of monsters to return
        offset (int): Number of monsters to skip
        
    Returns:
        dict: {
            'success': bool,
            'monsters': list,
            'total': int,
            'count': int,
            'pagination': dict
        }
    """
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
    """
    Get specific monster by ID
    
    Args:
        monster_id (int): Monster ID
        
    Returns:
        dict: {
            'success': bool,
            'monster': dict or None,
            'error': str or None
        }
    """
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
    """
    Get available monster generation templates
    
    Returns:
        dict: {template_name: description}
    """
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
    """
    Get monster database statistics
    
    Returns:
        dict: Statistics about monsters in database
    """
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