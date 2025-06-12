# Monster Generation Module - ULTRA-LEAN
# One job: Generate monsters using templates
# No bloat, no legacy code, no unused functions

from typing import Dict, Any, Optional
from backend.models.monster import Monster
from .generation_service import generate_with_logging
from .prompt_engine import get_template_config, build_prompt
from .parser import parse_response

def generate_monster(prompt_name: str = "basic_monster") -> Dict[str, Any]:
    """
    Generate a monster. That's it.
    
    Args:
        prompt_name: Template name to use
        
    Returns:
        dict: Success/error and monster data
    """
    
    # Get template
    template_config = get_template_config(prompt_name)
    if not template_config:
        return {
            'success': False,
            'error': f'Template not found: {prompt_name}',
            'monster': None,
            'log_id': None
        }
    
    # Build prompt
    prompt_text = build_prompt(prompt_name)
    if not prompt_text:
        return {
            'success': False,
            'error': f'Failed to build prompt: {prompt_name}',
            'monster': None,
            'log_id': None
        }
    
    # Generate
    result = generate_with_logging(
        prompt=prompt_text,
        prompt_type='monster_generation',
        prompt_name=prompt_name,
        max_tokens=template_config['max_tokens'],
        temperature=template_config['temperature'],
        priority=3,
        wait=True
    )
    
    if not result['success']:
        return {
            'success': False,
            'error': result['error'],
            'monster': None,
            'log_id': result.get('log_id')
        }
    
    # Parse
    parse_result = parse_response(
        response_text=result['text'],
        parser_config=template_config['parser']
    )
    
    if not parse_result.success:
        return {
            'success': False,
            'error': f"Parse failed: {parse_result.error}",
            'monster': None,
            'log_id': result['log_id'],
            'raw_response': result['text']
        }
    
    # Create monster
    monster = Monster.create_from_llm_data(parse_result.data)
    
    if monster and monster.save():
        return {
            'success': True,
            'monster': monster.to_dict(),
            'log_id': result['log_id'],
            'generation_stats': {
                'tokens': result['tokens'],
                'duration': result['duration']
            }
        }
    else:
        return {
            'success': False,
            'error': 'Failed to save monster',
            'monster': None,
            'log_id': result['log_id']
        }

def get_available_prompts() -> Dict[str, str]:
    """Get available monster prompts"""
    from .prompt_engine import get_prompt_engine
    
    engine = get_prompt_engine()
    result = {}
    
    for name in engine.list_templates():
        template = engine.get_template(name)
        if template and template.category == 'monster_generation':
            result[name] = template.description
    
    return result