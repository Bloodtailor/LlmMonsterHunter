# LLM Processor - Inference + Parsing Pipeline
# Handles complete inference pipeline with automatic retries and parsing
# Takes log_id, manages the entire process, updates log automatically

from typing import Dict, Any, Optional, Callable
from . import log as llm_log
from .inference import generate_streaming
from .parser import parse_response

def process_request(log_id: int, callback: Optional[Callable[[str], None]] = None) -> Dict[str, Any]:
    """
    Complete inference + parsing pipeline with automatic retries
    
    Philosophy: Given a log_id, do everything needed to get a parsed result
    - Load parameters from database
    - Generate with retries (up to 3 attempts)
    - Parse each attempt
    - Update log automatically
    - Return final result
    
    Args:
        log_id (int): Database log ID containing all parameters
        callback (callable): Optional streaming callback
        
    Returns:
        dict: Final processing results
    """
    
    try:
        # Step 1: Load all data from log
        log_entry = llm_log.get_log(log_id)
        if not log_entry:
            return {
                'success': False,
                'error': f'Log {log_id} not found',
                'log_id': log_id
            }
        
        prompt_text = llm_log.get_prompt_text(log_id)
        inference_params = llm_log.get_inference_params(log_id)
        parser_config = llm_log.get_parser_config(log_id)
        
        if not prompt_text or not inference_params:
            llm_log.mark_failed(log_id, "Missing prompt or parameters")
            return {
                'success': False,
                'error': 'Missing prompt or parameters',
                'log_id': log_id
            }
        
        print(f"✅ Loaded parameters for {log_entry.prompt_type}")
        
        # Step 2: Mark as started
        llm_log.mark_started(log_id)
        
        # Step 3: Attempt generation + parsing loop
        final_result = None
        
        while True:
            current_attempt = log_entry.generation_attempt
            print(f"🎯 Attempt {current_attempt}/{log_entry.max_attempts}")
            
            # Generate text
            generation_result = generate_streaming(
                prompt=prompt_text,
                callback=callback,
                **inference_params
            )
            
            if not generation_result['success']:
                llm_log.mark_failed(log_id, generation_result['error'])
                return {
                    'success': False,
                    'error': generation_result['error'],
                    'log_id': log_id,
                    'attempt': current_attempt
                }
            
            # Update log with generation results
            llm_log.mark_attempt_completed(
                log_id, 
                generation_result['text'], 
                generation_result.get('tokens', 0)
            )
            
            print(f"✅ Generated {generation_result.get('tokens', 0)} tokens")
            
            # Attempt parsing (if parser config provided)
            if parser_config:
                parse_result = parse_response(generation_result['text'], parser_config)
                
                if parse_result.success:
                    # Parsing succeeded!
                    llm_log.mark_parsed(log_id, parse_result.data)
                    llm_log.mark_completed(log_id)
                    
                    print(f"✅ Parsing succeeded on attempt {current_attempt}")
                    
                    return {
                        'success': True,
                        'text': generation_result['text'],
                        'parsed_data': parse_result.data,
                        'tokens': generation_result.get('tokens', 0),
                        'duration': generation_result.get('duration', 0),
                        'log_id': log_id,
                        'attempt': current_attempt,
                        'parsing_success': True
                    }
                else:
                    # Parsing failed
                    llm_log.mark_parse_failed(log_id, parse_result.error)
                    print(f"❌ Parsing failed on attempt {current_attempt}: {parse_result.error}")
                    
                    # Check if we can retry
                    if llm_log.can_retry(log_id):
                        llm_log.increment_attempt(log_id)
                        log_entry = llm_log.get_log(log_id)  # Refresh log entry
                        print(f"🔄 Retrying... (attempt {log_entry.generation_attempt})")
                        continue
                    else:
                        # No more retries
                        llm_log.mark_completed(log_id)
                        print(f"⚠️ Max attempts reached, returning last result")
                        
                        return {
                            'success': True,  # Generation succeeded, parsing failed
                            'text': generation_result['text'],
                            'parsed_data': None,
                            'tokens': generation_result.get('tokens', 0),
                            'duration': generation_result.get('duration', 0),
                            'log_id': log_id,
                            'attempt': current_attempt,
                            'parsing_success': False,
                            'parsing_error': parse_result.error
                        }
            else:
                # No parsing needed, just return generation result
                llm_log.mark_completed(log_id)
                
                return {
                    'success': True,
                    'text': generation_result['text'],
                    'tokens': generation_result.get('tokens', 0),
                    'duration': generation_result.get('duration', 0),
                    'log_id': log_id,
                    'attempt': current_attempt,
                    'parsing_success': None  # No parsing attempted
                }
        
    except Exception as e:
        print(f"❌ Processing error for log {log_id}: {e}")
        llm_log.mark_failed(log_id, str(e))
        
        return {
            'success': False,
            'error': str(e),
            'log_id': log_id
        }

def quick_inference(prompt: str, **inference_overrides) -> Dict[str, Any]:
    """
    Quick inference without parsing - for simple text generation
    
    Args:
        prompt (str): Text to generate
        **inference_overrides: Optional parameter overrides
        
    Returns:
        dict: Generation results
    """
    
    try:
        # Get defaults and apply overrides
        from backend.config.llm_config import get_all_inference_defaults
        params = get_all_inference_defaults()
        params.update(inference_overrides)
        
        # Create log
        log_id = llm_log.create_log(
            prompt_type='quick_inference',
            prompt_name='quick_inference',
            prompt_text=prompt,
            inference_params=params,
            parser_config=None  # No parsing
        )
        
        if not log_id:
            return {'success': False, 'error': 'Failed to create log'}
        
        # Process without parsing
        return process_request(log_id)
        
    except Exception as e:
        return {'success': False, 'error': str(e)}