# Generation Service - UNIFIED FOR ALL AI GENERATION
# THE ONLY WAY to request any AI generation (LLM or Image)
# Creates normalized generation_log entries and delegates to unified queue

import time
from typing import Dict, Any, Optional

def text_generation_request(prompt: str, 
                           prompt_type: str = None,
                           prompt_name: str = None,
                           parser_config: Optional[Dict[str, Any]] = None,
                           wait_for_completion: bool = True,
                           **inference_overrides) -> Dict[str, Any]:
    """
    THE ONLY WAY to request LLM text generation
    Creates complete generation_log entry and delegates to unified queue
    
    Args:
        prompt (str): Text to generate from (ONLY REQUIRED parameter)
        prompt_type (str): Type of prompt (optional)
        prompt_name (str): Specific prompt name (optional)
        parser_config (dict): Parser configuration for automatic parsing (optional)
        wait_for_completion (bool): Whether to wait for completion
        **inference_overrides: Any inference parameter overrides
        
    Returns:
        dict: Results from pipeline processing
    """
    
    try:
        print(f"🎯 Generation Service: Creating LLM text generation request")
        
        # Step 1: Get all inference defaults and apply overrides
        from backend.config.llm_config import get_all_inference_defaults
        inference_params = get_all_inference_defaults()
        
        # Apply any user overrides
        for key, value in inference_overrides.items():
            if value is not None and key in inference_params:
                inference_params[key] = value
        
        # Apply prompt metadata defaults
        if prompt_type is None:
            prompt_type = inference_params['prompt_type']
        if prompt_name is None:
            prompt_name = inference_params['prompt_name']
        
        print(f"✅ Prepared LLM parameters (temp={inference_params['temperature']}, max_tokens={inference_params['max_tokens']})")
        
        # Step 2: Create complete generation_log entry with LLM child data
        from backend.models.generation_log import GenerationLog
        
        generation_log = GenerationLog.create_llm_log(
            prompt_type=prompt_type,
            prompt_name=prompt_name,
            prompt_text=prompt,
            inference_params=inference_params,
            parser_config=parser_config
        )
        
        if not generation_log or not generation_log.save():
            return {
                'success': False,
                'error': 'Failed to create generation log entry'
            }
        
        print(f"✅ Created LLM generation log {generation_log.id}")
        
        # Step 3: Add to unified queue
        from backend.ai.queue import get_ai_queue
        queue = get_ai_queue()
        
        if not queue.add_request(generation_log.id):
            return {
                'success': False,
                'error': 'Failed to add request to queue',
                'generation_id': generation_log.id
            }
        
        if not wait_for_completion:
            return {
                'success': True,
                'generation_id': generation_log.id,
                'generation_type': 'llm',
                'message': 'LLM generation request queued for processing'
            }
        
        # Step 4: Wait for completion
        return _wait_for_completion(queue, generation_log.id, 'llm')
        
    except Exception as e:
        print(f"❌ LLM Generation Service error: {e}")
        return {
            'success': False,
            'error': str(e)
        }

def image_generation_request(prompt_text: str,
                           prompt_type: str = "image_generation",
                           prompt_name: str = "monster_generation",
                           wait_for_completion: bool = True,
                           **image_overrides) -> Dict[str, Any]:
    """
    THE ONLY WAY to request image generation - COMPLETELY GENERIC
    Creates complete generation_log entry and delegates to unified queue
    
    Args:
        prompt_text (str): The unique part of the prompt (ONLY REQUIRED parameter)
        prompt_type (str): Type of prompt (for logging)
        prompt_name (str): Workflow name to use 
        wait_for_completion (bool): Whether to wait for completion
        **image_overrides: Any image parameter overrides
        
    Returns:
        dict: Results from image generation pipeline
    """
    
    try:
        print(f"🎨 Generation Service: Creating generic image generation request")
        
        # Check if image generation is enabled
        import os
        if not os.getenv('ENABLE_IMAGE_GENERATION', 'false').lower() == 'true':
            return {
                'success': False,
                'error': 'Image generation is disabled',
                'reason': 'DISABLED',
                'help': 'Set ENABLE_IMAGE_GENERATION=true in .env to enable image generation'
            }
        
        # Step 1: Prepare image parameters (generic)
        image_params = {
            'workflow_name': prompt_name,
            **image_overrides
        }
        
        print(f"✅ Prepared image parameters for workflow '{prompt_name}'")
        
        # Step 2: Create complete generation_log entry with image child data
        from backend.models.generation_log import GenerationLog
        
        generation_log = GenerationLog.create_image_log(
            prompt_type=prompt_type,
            prompt_name=prompt_name,
            prompt_text=prompt_text,  # Just store the unique prompt text directly
            image_params=image_params
        )
        
        if not generation_log or not generation_log.save():
            return {
                'success': False,
                'error': 'Failed to create image generation log entry'
            }
        
        print(f"✅ Created image generation log {generation_log.id}")
        
        # Step 3: Add to unified queue
        from backend.ai.queue import get_ai_queue
        queue = get_ai_queue()
        
        if not queue.add_request(generation_log.id):
            return {
                'success': False,
                'error': 'Failed to add image request to queue',
                'generation_id': generation_log.id
            }
        
        if not wait_for_completion:
            return {
                'success': True,
                'generation_id': generation_log.id,
                'generation_type': 'image',
                'message': 'Image generation request queued for processing'
            }
        
        # Step 4: Wait for completion
        return _wait_for_completion(queue, generation_log.id, 'image')
        
    except Exception as e:
        print(f"❌ Image Generation Service error: {e}")
        return {
            'success': False,
            'error': str(e)
        }


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
                    'success': True,
                    'text': result.get('text', ''),
                    'tokens': result.get('tokens', 0),
                    'duration': result.get('duration', 0),
                    'generation_id': generation_id,
                    'generation_type': 'llm',
                    'parsing_success': result.get('parsing_success'),
                    'parsed_data': result.get('parsed_data'),
                    'attempt': result.get('attempt', 1)
                }
            elif generation_type == 'image':
                return {
                    'success': True,
                    'image_path': result.get('image_path', ''),
                    'execution_time': result.get('execution_time', 0),
                    'generation_id': generation_id,
                    'generation_type': 'image',
                    'prompt_id': result.get('prompt_id'),
                    'cleanup_success': result.get('cleanup_success', True)
                }
        
        if status['status'] == 'failed':
            return {
                'success': False,
                'error': status.get('error', 'Processing failed'),
                'generation_id': generation_id,
                'generation_type': generation_type
            }
        
        time.sleep(0.5)
    
    return {
        'success': False,
        'error': f'{generation_type.upper()} generation timed out after {timeout} seconds',
        'generation_id': generation_id,
        'generation_type': generation_type
    }


# Export main functions
__all__ = [
    'text_generation_request',
    'image_generation_request'
]