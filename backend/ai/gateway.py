# AI gateway - formerly generation_service.py
# THE ONLY WAY to request any AI generation (LLM or Image)
# Creates normalized generation_log entries and delegates to unified queue
import os
import time
from typing import Dict, Any, Optional
from backend.core.utils import print_success, print_warning
from backend.core.config.llm_config import get_all_inference_defaults
from backend.models.generation_log import GenerationLog
from .queue import get_ai_queue


def text_generation_request(prompt: str, 
                           prompt_type: str = None,
                           prompt_name: str = None,
                           parser_config: Optional[Dict[str, Any]] = None,
                           return_early: bool = False,
                           **inference_overrides) -> Dict[str, Any]:
    """
    THE ONLY WAY to request LLM text generation
    Creates complete generation_log entry and delegates to unified queue
    
    Args:
        prompt (str): Text to generate from (ONLY REQUIRED parameter)
        prompt_type (str): Type of prompt (optional)
        prompt_name (str): Specific prompt name (optional)
        parser_config (dict): Parser configuration for automatic parsing (optional)
        retrun_early (bool): Return without waiting for completion (optional)
        **inference_overrides: Any inference parameter overrides
        
    Returns:
        dict: Results from pipeline processing
    """

    # Get inference defaults and apply overrides
    inference_params = get_all_inference_defaults()
    
    for key, value in inference_overrides.items():
        if key not in inference_params:
            print_warning(f"Unknown override: {key}")
        elif value is not None:
            inference_params[key] = value
    
    if prompt_type is None:
        prompt_type = inference_params['prompt_type']
    if prompt_name is None:
        prompt_name = inference_params['prompt_name']
    
    # Show simplified request info
    truncated_prompt = prompt[:50] + "..." if len(prompt) > 50 else prompt
    print_success(f"Text generation request: {prompt_type}/{prompt_name} - \"{truncated_prompt}\"")
    
    # Create generation log entry
    generation_log = GenerationLog.create_llm_log(
        prompt_type=prompt_type,
        prompt_name=prompt_name,
        prompt_text=prompt,
        inference_params=inference_params,
        parser_config=parser_config
    )
    
    if not generation_log or not generation_log.save():
        raise Exception('Failed to create generation log entry')
    
    # Add to unified queue
    queue = get_ai_queue()
    
    if not queue.add_request(generation_log.id):
        raise Exception('Failed to add request to queue', generation_id=generation_log.id)
    
    if return_early:
        return {'generation_id': generation_log.id}
    # Wait for completion
    return _wait_for_completion(queue, generation_log.id, 'llm')

def image_generation_request(prompt_text: str,
                           prompt_type: str = "image_generation",
                           prompt_name: str = "monster_generation",
                           return_early: bool = False,
                           **image_overrides) -> Dict[str, Any]:
    """
    THE ONLY WAY to request image generation - COMPLETELY GENERIC
    Creates complete generation_log entry and delegates to unified queue
    
    Args:
        prompt_text (str): The unique part of the prompt (ONLY REQUIRED parameter)
        prompt_type (str): Type of prompt (for logging)
        prompt_name (str): Workflow name to use 
        **image_overrides: Any image parameter overrides
        
    Returns:
        dict: Results from image generation pipeline
    """
    
    # Check if image generation is enabled
    if not os.getenv('ENABLE_IMAGE_GENERATION', 'false').lower() == 'true':
        raise Exception('Image generation is disabled', reason='DISABLED')
    
    # Show simplified request info
    truncated_prompt = prompt_text[:50] + "..." if len(prompt_text) > 50 else prompt_text
    print_success(f"Image generation request: {prompt_name} - \"{truncated_prompt}\"")
    
    # Prepare image parameters
    image_params = {
        'workflow_name': prompt_name,
        **image_overrides
    }
    
    # Create generation log entry
    generation_log = GenerationLog.create_image_log(
        prompt_type=prompt_type,
        prompt_name=prompt_name,
        prompt_text=prompt_text,
        image_params=image_params
    )
    
    if not generation_log or not generation_log.save():
        raise Exception('Failed to create image generation log entry')
    
    # Add to unified queue
    
    queue = get_ai_queue()
    
    if not queue.add_request(generation_log.id):
        raise Exception('Failed to add image request to queue', generation_id=generation_log.id)
    
    if return_early:
        return {'generation_id': generation_log.id}
    
    # Wait for completion
    return _wait_for_completion(queue, generation_log.id, 'image')


def _wait_for_completion(queue, generation_id: int, generation_type: str, timeout: int = 600) -> Dict[str, Any]:
    """
    Wait for generation completion with unified handling
    
    Args:
        queue: AI generation queue instance
        generation_id (int): Generation ID to wait for
        generation_type (str): 'llm' or 'image'
        timeout (int): Timeout in seconds
        
    Returns:
        dict: Completion results
    """
    start_time = time.time()
    
    while time.time() - start_time < timeout:
        status = queue.get_request_status(generation_id)
        
        if not status:
            break
        
        if status['status'] == 'completed':
            result = status['result']
            
            if generation_type == 'llm':
                return {
                    'generation_id': generation_id,
                    'success': result.get('success', None),
                    'error': result.get('error', None),
                    'text': result.get('text', ''),
                    'parsing_success': result.get('parsing_success', None),
                    'parsing_error': result.get('parsing_error', None),
                    'parsed_data': result.get('parsed_data', None)
                }
            elif generation_type == 'image':
                return {
                    'generation_id': generation_id,
                    'success': result.get('success', None),
                    'error': result.get('error', None),
                    'image_path': result.get('image_path', '')
                }
        
        if status['status'] == 'failed':
            raise Exception(
                status.get('error', 'Processing failed'),
                generation_id=generation_id,
                generation_type=generation_type
            )
        
        time.sleep(0.5)
    
    raise TimeoutError(
        f'{generation_type.upper()} generation timed out after {timeout} seconds',
        generation_id=generation_id,
        generation_type=generation_type
    )

# Export main functions
__all__ = [
    'text_generation_request',
    'image_generation_request'
]