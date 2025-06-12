# LLM Service - ULTRA-SIMPLE
# One function: inference_request(prompt) with smart defaults

import time
from typing import Dict, Any, Optional
from flask import current_app, has_app_context
from backend.config.llm_config import get_max_tokens, get_temperature, get_priority, get_timeout

def inference_request(prompt: str,
                     prompt_type: str = None,
                     prompt_name: str = None, 
                     max_tokens: int = None,
                     temperature: float = None,
                     priority: int = None,
                     wait_for_completion: bool = True) -> Dict[str, Any]:
    """
    THE ONLY WAY to request LLM inference
    
    Args:
        prompt (str): Text to generate from
        All other args optional with smart defaults
        
    Returns:
        dict: Results with success, text, etc.
    """
    
    # Use defaults from config if not provided
    if max_tokens is None:
        max_tokens = get_max_tokens()
    if temperature is None:
        temperature = get_temperature()
    if priority is None:
        priority = get_priority()
    if prompt_type is None:
        prompt_type = "general"
    if prompt_name is None:
        prompt_name = "user_request"
    
    print(f"🎯 LLM Service: {prompt_type} request")
    
    # Handle Flask app context properly
    if not has_app_context():
        print("⚠️ No Flask context - trying to get current app")
        try:
            from backend.app import create_app
            app = create_app()
            with app.app_context():
                return _do_inference_request(prompt, prompt_type, prompt_name, max_tokens, temperature, priority, wait_for_completion)
        except Exception as e:
            return {
                'success': False,
                'error': f'App context error: {str(e)}',
                'prompt': prompt[:50] + "..." if len(prompt) > 50 else prompt
            }
    else:
        return _do_inference_request(prompt, prompt_type, prompt_name, max_tokens, temperature, priority, wait_for_completion)

def _do_inference_request(prompt, prompt_type, prompt_name, max_tokens, temperature, priority, wait_for_completion):
    """Internal function that does the actual work within Flask context"""
    
    try:
        # Create log entry
        from backend.models.llm_log import LLMLog
        
        log = LLMLog.create_log(
            prompt_type=prompt_type,
            prompt_name=prompt_name,
            prompt_text=prompt,
            max_tokens=max_tokens,
            temperature=temperature
        )
        
        if not log.save():
            return {
                'success': False,
                'error': 'Failed to create log entry'
            }
        
        # Add to queue
        from backend.llm.queue import get_llm_queue
        queue = get_llm_queue()
        request_id = queue.add_request(
            prompt=prompt,
            max_tokens=max_tokens,
            temperature=temperature,
            prompt_type=prompt_type,
            priority=priority,
            log_id=log.id
        )
        
        # Update log
        log.entity_type = 'inference_request'
        log.entity_id = request_id
        log.save()
        
        if not wait_for_completion:
            return {
                'success': True,
                'request_id': request_id,
                'log_id': log.id,
                'message': 'Request queued'
            }
        
        # Wait for completion
        start_time = time.time()
        timeout = get_timeout()
        
        while time.time() - start_time < timeout:
            status = queue.get_request_status(request_id)
            
            if not status:
                break
            
            if status['status'] == 'completed':
                return {
                    'success': True,
                    'text': status['result']['text'],
                    'tokens': status['result']['tokens'],
                    'duration': status['result']['duration'],
                    'request_id': request_id,
                    'log_id': log.id
                }
            
            if status['status'] == 'failed':
                return {
                    'success': False,
                    'error': status.get('error', 'Generation failed'),
                    'request_id': request_id,
                    'log_id': log.id
                }
            
            time.sleep(0.5)
        
        return {
            'success': False,
            'error': 'Request timed out',
            'request_id': request_id,
            'log_id': log.id
        }
        
    except Exception as e:
        print(f"❌ LLM Service error: {e}")
        return {
            'success': False,
            'error': str(e)
        }

# Simple convenience function
def simple_generation(prompt: str) -> str:
    """Just returns the generated text or empty string if failed"""
    result = inference_request(prompt)
    return result.get('text', '') if result['success'] else ''