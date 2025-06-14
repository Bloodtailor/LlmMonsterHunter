# LLM Service - NEW PIPELINE
# Creates log with all parameters, passes log_id to queue
# Single Responsibility: Service interface for LLM pipeline

import time
from typing import Dict, Any, Optional

def inference_request(prompt: str, 
                     prompt_type: str = None,
                     prompt_name: str = None,
                     parser_config: Optional[Dict[str, Any]] = None,
                     wait_for_completion: bool = True,
                     **inference_overrides) -> Dict[str, Any]:
    """
    THE ONLY WAY to request LLM inference
    Creates complete log entry and delegates to queue
    
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
        print(f"🎯 LLM Service: Creating inference request")
        
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
        
        print(f"✅ Prepared parameters (temp={inference_params['temperature']}, max_tokens={inference_params['max_tokens']})")
        
        # Step 2: Create complete log entry with ALL parameters
        from backend.llm import log as llm_log
        
        log_id = llm_log.create_log(
            prompt_type=prompt_type,
            prompt_name=prompt_name,
            prompt_text=prompt,
            inference_params=inference_params,
            parser_config=parser_config
        )
        
        if not log_id:
            return {
                'success': False,
                'error': 'Failed to create log entry'
            }
        
        print(f"✅ Created log entry {log_id}")
        
        # Step 3: Add to queue (just pass log_id)
        from backend.llm.queue import get_llm_queue
        queue = get_llm_queue()
        
        if not queue.add_request(log_id):
            return {
                'success': False,
                'error': 'Failed to add request to queue',
                'log_id': log_id
            }
        
        if not wait_for_completion:
            return {
                'success': True,
                'log_id': log_id,
                'message': 'Request queued for processing'
            }
        
        # Step 4: Wait for completion
        timeout = 600  # 10 minutes
        start_time = time.time()
        
        while time.time() - start_time < timeout:
            status = queue.get_request_status(log_id)
            
            if not status:
                break
            
            if status['status'] == 'completed':
                result = status['result']
                return {
                    'success': True,
                    'text': result.get('text', ''),
                    'tokens': result.get('tokens', 0),
                    'duration': result.get('duration', 0),
                    'log_id': log_id,
                    'parsing_success': result.get('parsing_success'),
                    'parsed_data': result.get('parsed_data'),
                    'attempt': result.get('attempt', 1)
                }
            
            if status['status'] == 'failed':
                return {
                    'success': False,
                    'error': status.get('error', 'Processing failed'),
                    'log_id': log_id
                }
            
            time.sleep(0.5)
        
        return {
            'success': False,
            'error': 'Request timed out',
            'log_id': log_id
        }
        
    except Exception as e:
        print(f"❌ LLM Service error: {e}")
        return {
            'success': False,
            'error': str(e)
        }