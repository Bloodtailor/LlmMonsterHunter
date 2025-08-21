# Prompt Helpers - UPDATED: Exception-Based for Workflow Clarity
# Simplified interface for game logic with clean exception handling
# Used across monster, ability, and dungeon generation with consistent error patterns

from typing import Dict, Any, Optional
from backend.ai import get_template_config, build_prompt, text_generation_request
from backend.core.utils import print_error, print_success

def build_and_generate(template_name: str, prompt_type: str, variables: Optional[Dict[str, Any]] = None) -> Dict[str, Any]:
    """
    Complete helper that builds prompt and makes generation request
    Main function used by all game asset generators
    
    Args:
        template_name (str): Template to use
        prompt_type (str): Type of prompt for logging
        variables (dict): Template variables
        
    Returns:
        dict: Parsed data from successful generation
        
    Raises:
        Exception: If any step fails (prompt building, generation, or parsing)
    """
    
    # Build prompt (raises exception on failure)
    prompt_text, template_config = _build_game_prompt(template_name, variables)
    
    # Make generation request (raises exception on failure)
    parsed_data = _make_generation_request(prompt_text, prompt_type, template_name, template_config)
    
    print_success(f"Generated {prompt_type} using {template_name}")
    return parsed_data

def build_and_stream(template_name: str, prompt_type: str, variables: Optional[Dict[str, Any]] = None) -> int:
    """
    Complete helper that builds prompt and makes streaming request
    Main function used by all game streaming generations
    
    Args:
        template_name (str): Template to use
        prompt_type (str): Type of prompt for logging
        variables (dict): Template variables
        
    Returns:
        int: generation_id of the queued text generation request
        
    Raises:
        Exception: If any step fails (prompt building or add to queue)
    """
    
    # Build prompt (raises exception on failure)
    prompt_text, template_config = _build_game_prompt(template_name, variables)
    
    # Make generation request (raises exception on failure)
    generation_id = _make_streaming_request(prompt_text, prompt_type, template_name, template_config)
    
    print_success(f"Generated {prompt_type} using {template_name}")
    return generation_id

def _build_game_prompt(template_name: str, variables: Optional[Dict[str, Any]] = None) -> tuple[str, Dict[str, Any]]:
    """
    Build a game prompt with variables and get template configuration
    Private function - only used internally by build_and_generate
    """
    
    try:
        # Get template configuration first
        template_config = get_template_config(template_name)
        if not template_config:
            raise Exception(f'Template not found: {template_name}')
        
        # Build prompt with variables
        prompt_text = build_prompt(template_name, variables or {})
        if not prompt_text:
            raise Exception(f'Failed to build prompt: {template_name}')
        
        return prompt_text, template_config
        
    except Exception as e:
        if "Template not found" in str(e) or "Failed to build prompt" in str(e):
            raise  # Re-raise our specific exceptions
        else:
            raise Exception(f'Prompt building error: {str(e)}')

def _make_generation_request(prompt_text: str, prompt_type: str, template_name: str, template_config: Dict[str, Any]) -> Dict[str, Any]:
    """
    Make a generation request using template configuration
    Private function - only used internally by build_and_generate
    """
    
    result = text_generation_request(
        prompt=prompt_text,
        prompt_type=prompt_type,
        prompt_name=template_name,
        parser_config=template_config['parser'],
        max_tokens=template_config['max_tokens'],
        temperature=template_config['temperature']
    )
    
    if not result['success']:
        raise Exception(f"Generation failed: {result.get('error', 'Unknown error')}")
    
    if not result.get('parsing_success'):
        raise Exception(f"Parsing failed: {result.get('parsing_error', 'Unknown parsing error')}")
    
    return result['parsed_data']
        
def _make_streaming_request(prompt_text: str, prompt_type: str, template_name: str, template_config: Dict[str, Any]) -> Dict[str, Any]:
    """
    Make a generation request using template configuration
    Private function - only used internally by build_and_generate
    """
    
    result = text_generation_request(
        prompt=prompt_text,
        prompt_type=prompt_type,
        prompt_name=template_name,
        parser_config=template_config['parser'],
        return_early=True,
        priority=1,
        max_tokens=template_config['max_tokens'],
        temperature=template_config['temperature']
    )
    
    return result['generation_id']
