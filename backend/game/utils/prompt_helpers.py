# Prompt Helpers - Extracted Repeated Code
# Consolidates the prompt building and generation request patterns
# Used across monster_service, ability_service, dungeon_service

from typing import Dict, Any, Optional
from backend.ai.llm.prompt_engine import get_template_config, build_prompt
from backend.services import generation_service
from backend.utils import success_response, error_response, print_error

def build_game_prompt(template_name: str, variables: Optional[Dict[str, Any]] = None) -> Dict[str, Any]:
    """
    Build a game prompt with variables and get template configuration
    
    Args:
        template_name (str): Template name (e.g., 'generate_ability')
        variables (dict): Variables to substitute in template
        
    Returns:
        dict: {success: bool, prompt_text: str, template_config: dict, error?: str}
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
            str(e),
            prompt_text=None,
            template_config=None
        )

def make_generation_request(prompt_text: str, 
                          prompt_type: str,
                          template_name: str,
                          template_config: Dict[str, Any]) -> Dict[str, Any]:
    """
    Make a standardized generation request using template configuration
    
    Args:
        prompt_text (str): Built prompt text
        prompt_type (str): Type of prompt (e.g., 'ability_generation')
        template_name (str): Template name (e.g., 'generate_ability')
        template_config (dict): Template configuration with parser, max_tokens, etc.
        
    Returns:
        dict: Generation service result
    """
    
    try:
        return generation_service.text_generation_request(
            prompt=prompt_text,
            prompt_type=prompt_type,
            prompt_name=template_name,
            parser_config=template_config['parser'],
            max_tokens=template_config['max_tokens'],
            temperature=template_config['temperature'],
            wait_for_completion=True  # Always wait since we removed async
        )
        
    except Exception as e:
        print_error(f"Generation request failed: {str(e)}")
        return error_response(f'Generation request failed: {str(e)}')

def build_and_generate(template_name: str,
                      prompt_type: str, 
                      variables: Optional[Dict[str, Any]] = None) -> Dict[str, Any]:
    """
    Complete helper that builds prompt and makes generation request
    Most common pattern across all game services
    
    Args:
        template_name (str): Template name
        prompt_type (str): Prompt type for logging
        variables (dict): Template variables
        
    Returns:
        dict: Complete generation result with enhanced error handling
    """
    
    # Build prompt
    prompt_result = build_game_prompt(template_name, variables)
    if not prompt_result['success']:
        return error_response(
            f"Prompt building failed: {prompt_result['error']}",
            stage='prompt_building'
        )
    
    # Make generation request
    generation_result = make_generation_request(
        prompt_text=prompt_result['prompt_text'],
        prompt_type=prompt_type,
        template_name=template_name,
        template_config=prompt_result['template_config']
    )
    
    # Add stage info for debugging
    if not generation_result.get('success'):
        generation_result['stage'] = 'generation'
    
    return generation_result