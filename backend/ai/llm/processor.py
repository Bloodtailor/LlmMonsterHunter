# LLM Processor - CLEANED UP
# Handles complete inference pipeline with automatic retries and parsing
# Works with normalized generation_log structure

from typing import Dict, Any, Optional, Callable
from .inference import generate_streaming
from .parser import parse_response
from backend.utils import error_response, success_response, print_success, print_error

def process_request(generation_id: int, callback: Optional[Callable[[str], None]] = None) -> Dict[str, Any]:
    """
    Complete LLM inference + parsing pipeline with automatic retries
    
    Args:
        generation_id (int): Database generation_logs.id
        callback (callable): Optional streaming callback
        
    Returns:
        dict: Final processing results
    """
    
    try:
        # Load generation log (service layer already validated it exists)
        from backend.models.generation_log import GenerationLog
        
        generation_log = GenerationLog.query.get(generation_id)
        if not generation_log:
            return error_response(f'Generation log {generation_id} not found', generation_id=generation_id)
        
        if generation_log.generation_type != 'llm':
            return error_response(
                f'Generation {generation_id} is not an LLM generation (type: {generation_log.generation_type})',
                generation_id=generation_id
            )
        
        # Get LLM-specific data
        llm_log = generation_log.llm_log
        if not llm_log:
            return error_response(f'LLM log not found for generation {generation_id}', generation_id=generation_id)
        
        # Extract parameters
        prompt_text = generation_log.prompt_text
        inference_params = llm_log.get_inference_params()
        parser_config = llm_log.parser_config
        
        # Mark as started
        generation_log.mark_started()
        generation_log.save()
        
        # Attempt generation + parsing loop
        while True:
            current_attempt = generation_log.generation_attempt
            print_success(f"LLM Generation attempt {current_attempt}/{generation_log.max_attempts}")
            
            # Generate text
            generation_result = generate_streaming(
                prompt=prompt_text,
                callback=callback,
                **inference_params
            )
            
            if not generation_result['success']:
                generation_log.mark_failed(generation_result['error'])
                generation_log.save()
                return error_response(
                    generation_result['error'],
                    generation_id=generation_id,
                    attempt=current_attempt
                )
            
            # Update LLM log with generation results
            llm_log.mark_response_completed(
                response_text=generation_result['text'], 
                response_tokens=generation_result.get('tokens', 0),
                tokens_per_second=generation_result.get('tokens_per_second', 0)
            )
            llm_log.save()
            
            # Attempt parsing (if parser config provided)
            if parser_config:
                parse_result = parse_response(generation_result['text'], parser_config)
                
                if parse_result.success:
                    # Parsing succeeded!
                    llm_log.mark_parsed(parse_result.data)
                    generation_log.mark_completed()
                    
                    # Save both logs
                    llm_log.save()
                    generation_log.save()
                    
                    print_success(f"LLM parsing succeeded on attempt {current_attempt}")
                    
                    return success_response({
                        'text': generation_result['text'],
                        'parsed_data': parse_result.data,
                        'tokens': generation_result.get('tokens', 0),
                        'duration': generation_result.get('duration', 0),
                        'tokens_per_second': generation_result.get('tokens_per_second', 0),
                        'generation_id': generation_id,
                        'attempt': current_attempt,
                        'parsing_success': True
                    })
                else:
                    # Parsing failed
                    llm_log.mark_parse_failed(parse_result.error)
                    llm_log.save()
                    
                    # Check if we can retry
                    if generation_log.can_retry():
                        generation_log.increment_attempt()
                        llm_log.reset_parse_status()  # Reset for next attempt
                        generation_log.save()
                        llm_log.save()
                        continue
                    else:
                        # No more retries
                        generation_log.mark_completed()
                        generation_log.save()
                        
                        return success_response({
                            'text': generation_result['text'],
                            'parsed_data': None,
                            'tokens': generation_result.get('tokens', 0),
                            'duration': generation_result.get('duration', 0),
                            'tokens_per_second': generation_result.get('tokens_per_second', 0),
                            'generation_id': generation_id,
                            'attempt': current_attempt,
                            'parsing_success': False,
                            'parsing_error': parse_result.error
                        })
            else:
                # No parsing needed, just return generation result
                generation_log.mark_completed()
                generation_log.save()
                
                return success_response({
                    'text': generation_result['text'],
                    'tokens': generation_result.get('tokens', 0),
                    'duration': generation_result.get('duration', 0),
                    'tokens_per_second': generation_result.get('tokens_per_second', 0),
                    'generation_id': generation_id,
                    'attempt': current_attempt,
                    'parsing_success': None  # No parsing attempted
                })
        
    except Exception as e:
        # Try to mark as failed in database
        try:
            from backend.models.generation_log import GenerationLog
            log = GenerationLog.query.get(generation_id)
            if log:
                log.mark_failed(str(e))
                log.save()
        except:
            pass  # Don't fail on database update failure
        
        return error_response(str(e), generation_id=generation_id)