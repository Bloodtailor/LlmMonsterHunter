# Prompt Helpers - UPDATED: Consistent Utility Function Usage
# Consolidates prompt building and generation request patterns
# Used across monster, ability, and dungeon services with consistent error handling
print(f"🔍 Loading {__file__}")
from typing import Dict, Any, Optional
from backend.ai import get_template_config, build_prompt
from backend.ai import text_generation_request
from backend.core.utils import success_response, error_response, print_error, print_success

def build_game_prompt(template_name: str, variables: Optional[Dict[str, Any]] = None) -> Dict[str, Any]:
    """
    Build a game prompt with variables and get template configuration
    Uses utility functions for consistent error handling
    """
    
    try:
        # Get template configuration first
        template_config = get_template_config(template_name)
        if not template_config:
            return error_response(
                f'Template not found: {template_name}',
                prompt_text=None,
                template_config=None
            )
        
        # Build prompt with variables
        prompt_text = build_prompt(template_name, variables or {})
        if not prompt_text:
            return error_response(
                f'Failed to build prompt: {template_name}',
                prompt_text=None,
                template_config=template_config
            )
        
        return success_response({
            'prompt_text': prompt_text,
            'template_config': template_config
        })
        
    except Exception as e:
        return error_response(
            f'Prompt building error: {str(e)}',
            prompt_text=None,
            template_config=None
        )

def make_generation_request(prompt_text: str, 
                          prompt_type: str,
                          template_name: str,
                          template_config: Dict[str, Any]) -> Dict[str, Any]:
    """
    Make a standardized generation request using template configuration
    Uses utility functions for consistent error handling
    """
    
    try:
        result = text_generation_request(
            prompt=prompt_text,
            prompt_type=prompt_type,
            prompt_name=template_name,
            parser_config=template_config['parser'],
            max_tokens=template_config['max_tokens'],
            temperature=template_config['temperature'],
            wait_for_completion=True
        )
        
        return result
        
    except Exception as e:
        print_error(f"Generation request failed: {str(e)}")
        return error_response(f'Generation request failed: {str(e)}')

def build_and_generate(template_name: str,
                      prompt_type: str, 
                      variables: Optional[Dict[str, Any]] = None) -> Dict[str, Any]:
    """
    Complete helper that builds prompt and makes generation request
    Most common pattern across all game services
    Uses utility functions for consistent error handling
    """
    
    # Build prompt using utility functions
    prompt_result = build_game_prompt(template_name, variables)
    if not prompt_result['success']:
        return error_response(
            f"Prompt building failed: {prompt_result['error']}",
            stage='prompt_building'
        )
    
    # Make generation request using utility functions
    generation_result = make_generation_request(
        prompt_text=prompt_result['prompt_text'],
        prompt_type=prompt_type,
        template_name=template_name,
        template_config=prompt_result['template_config']
    )
    
    # Add stage info for debugging if generation failed
    if not generation_result.get('success'):
        generation_result['stage'] = 'generation'
    else:
        print_success(f"Generated {prompt_type} using {template_name}")
    
    return generation_result

def validate_template_exists(template_name: str) -> Dict[str, Any]:
    """
    Validate that a template exists and is accessible
    Used by services for template validation
    """
    
    try:
        template_config = get_template_config(template_name)
        if not template_config:
            return {
                'valid': False,
                'error': f'Template not found: {template_name}',
                'template_config': None
            }
        
        return {
            'valid': True,
            'template_config': template_config
        }
        
    except Exception as e:
        return {
            'valid': False,
            'error': f'Template validation error: {str(e)}',
            'template_config': None
        }

def get_available_templates_by_category(category: str) -> Dict[str, str]:
    """
    Get available templates filtered by category
    Used by services to provide template lists
    """
    
    try:
        from backend.ai.llm.prompt_engine import get_prompt_engine
        
        engine = get_prompt_engine()
        templates = {}
        
        for name in engine.list_templates():
            template = engine.get_template(name)
            if template and template.category == category:
                templates[name] = template.description
        
        return templates
        
    except Exception as e:
        print_error(f"Failed to get templates for category '{category}': {str(e)}")
        return {}

def build_monster_context_variables(monster_context: Dict[str, Any]) -> Dict[str, Any]:
    """
    Build standardized variables from monster context
    Used across ability and monster generation
    """
    
    # Format existing abilities
    existing = monster_context.get('existing_abilities', [])
    abilities_text = "\n".join([
        f"- {a['name']} ({a.get('type', 'unknown')}): {a['description']}" for a in existing
    ]) if existing else "None (this will be their first ability)"
    
    # Format personality
    traits = monster_context.get('personality_traits', [])
    personality = ', '.join(traits) if traits else 'Mysterious'
    
    # Get stats with defaults
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