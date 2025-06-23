# LLM Processor - UPDATED FOR NORMALIZED DATABASE
# Handles complete inference pipeline with automatic retries and parsing
# Works with new generation_log + llm_log structure

from typing import Dict, Any, Optional, Callable
from .inference import generate_streaming
from .parser import parse_response

def process_request(generation_id: int, callback: Optional[Callable[[str], None]] = None) -> Dict[str, Any]:
    """
    Complete LLM inference + parsing pipeline with automatic retries
    UPDATED: Works with normalized generation_log structure
    
    Philosophy: Given a generation_id, do everything needed to get a parsed result
    - Load parameters from database (generation_log + llm_log)
    - Generate with retries (up to 3 attempts)
    - Parse each attempt
    - Update logs automatically
    - Return final result
    
    Args:
        generation_id (int): Database generation_logs.id
        callback (callable): Optional streaming callback
        
    Returns:
        dict: Final processing results
    """
    
    try:
        # Step 1: Load generation log and verify it's an LLM generation
        from backend.models.generation_log import GenerationLog
        
        generation_log = GenerationLog.query.get(generation_id)
        if not generation_log:
            return {
                'success': False,
                'error': f'Generation log {generation_id} not found',
                'generation_id': generation_id
            }
        
        if generation_log.generation_type != 'llm':
            return {
                'success': False,
                'error': f'Generation {generation_id} is not an LLM generation (type: {generation_log.generation_type})',
                'generation_id': generation_id
            }
        
        # Step 2: Get LLM-specific data
        llm_log = generation_log.llm_log
        if not llm_log:
            return {
                'success': False,
                'error': f'LLM log not found for generation {generation_id}',
                'generation_id': generation_id
            }
        
        # Step 3: Extract parameters
        prompt_text = generation_log.prompt_text
        inference_params = llm_log.get_inference_params()
        parser_config = llm_log.parser_config
        
        if not prompt_text or not inference_params:
            generation_log.mark_failed("Missing prompt or parameters")
            generation_log.save()
            return {
                'success': False,
                'error': 'Missing prompt or parameters',
                'generation_id': generation_id
            }
        
        print(f"✅ Loaded LLM parameters for {generation_log.prompt_type}")
        
        # Step 4: Mark as started
        generation_log.mark_started()
        generation_log.save()
        
        # Step 5: Attempt generation + parsing loop
        while True:
            current_attempt = generation_log.generation_attempt
            print(f"🎯 LLM Generation attempt {current_attempt}/{generation_log.max_attempts}")
            
            # Generate text
            generation_result = generate_streaming(
                prompt=prompt_text,
                callback=callback,
                **inference_params
            )
            
            if not generation_result['success']:
                generation_log.mark_failed(generation_result['error'])
                generation_log.save()
                return {
                    'success': False,
                    'error': generation_result['error'],
                    'generation_id': generation_id,
                    'attempt': current_attempt
                }
            
            # Update LLM log with generation results
            llm_log.mark_response_completed(
                response_text=generation_result['text'], 
                response_tokens=generation_result.get('tokens', 0),
                tokens_per_second=generation_result.get('tokens_per_second', 0)
            )
            llm_log.save()
            
            print(f"✅ Generated {generation_result.get('tokens', 0)} tokens")
            
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
                    
                    print(f"✅ LLM parsing succeeded on attempt {current_attempt}")
                    
                    return {
                        'success': True,
                        'text': generation_result['text'],
                        'parsed_data': parse_result.data,
                        'tokens': generation_result.get('tokens', 0),
                        'duration': generation_result.get('duration', 0),
                        'tokens_per_second': generation_result.get('tokens_per_second', 0),
                        'generation_id': generation_id,
                        'attempt': current_attempt,
                        'parsing_success': True
                    }
                else:
                    # Parsing failed
                    llm_log.mark_parse_failed(parse_result.error)
                    llm_log.save()
                    print(f"❌ LLM parsing failed on attempt {current_attempt}: {parse_result.error}")
                    
                    # Check if we can retry
                    if generation_log.can_retry():
                        generation_log.increment_attempt()
                        llm_log.reset_parse_status()  # Reset for next attempt
                        generation_log.save()
                        llm_log.save()
                        print(f"🔄 Retrying LLM generation... (attempt {generation_log.generation_attempt})")
                        continue
                    else:
                        # No more retries
                        generation_log.mark_completed()
                        generation_log.save()
                        print(f"⚠️ Max LLM attempts reached, returning last result")
                        
                        return {
                            'success': True,  # Generation succeeded, parsing failed
                            'text': generation_result['text'],
                            'parsed_data': None,
                            'tokens': generation_result.get('tokens', 0),
                            'duration': generation_result.get('duration', 0),
                            'tokens_per_second': generation_result.get('tokens_per_second', 0),
                            'generation_id': generation_id,
                            'attempt': current_attempt,
                            'parsing_success': False,
                            'parsing_error': parse_result.error
                        }
            else:
                # No parsing needed, just return generation result
                generation_log.mark_completed()
                generation_log.save()
                
                return {
                    'success': True,
                    'text': generation_result['text'],
                    'tokens': generation_result.get('tokens', 0),
                    'duration': generation_result.get('duration', 0),
                    'tokens_per_second': generation_result.get('tokens_per_second', 0),
                    'generation_id': generation_id,
                    'attempt': current_attempt,
                    'parsing_success': None  # No parsing attempted
                }
        
    except Exception as e:
        print(f"❌ LLM processing error for generation {generation_id}: {e}")
        
        # Try to mark as failed in database
        try:
            from backend.models.generation_log import GenerationLog
            log = GenerationLog.query.get(generation_id)
            if log:
                log.mark_failed(str(e))
                log.save()
        except:
            pass  # Don't fail on database update failure
        
        return {
            'success': False,
            'error': str(e),
            'generation_id': generation_id
        }

def quick_inference(prompt: str, **inference_overrides) -> Dict[str, Any]:
    """
    Quick LLM inference without parsing - for simple text generation
    UPDATED: Uses new generation_log structure
    
    Args:
        prompt (str): Text to generate
        **inference_overrides: Optional parameter overrides
        
    Returns:
        dict: Generation results
    """
    
    try:
        # Get defaults and apply overrides
        from backend.config.llm_config import get_all_inference_defaults
        from backend.models.generation_log import GenerationLog
        
        params = get_all_inference_defaults()
        params.update(inference_overrides)
        
        # Create generation log with LLM child
        generation_log = GenerationLog.create_llm_log(
            prompt_type='quick_inference',
            prompt_name='quick_inference',
            prompt_text=prompt,
            inference_params=params,
            parser_config=None  # No parsing
        )
        
        if not generation_log or not generation_log.save():
            return {'success': False, 'error': 'Failed to create generation log'}
        
        # Process without parsing
        return process_request(generation_log.id)
        
    except Exception as e:
        return {'success': False, 'error': str(e)}