# Generation Service - Coordinates LLM operations
# Lean orchestration between inference, queue, logging, and streaming

from typing import Dict, Any, Callable, Optional
from datetime import datetime
from .queue import QueueItem, QueueItemStatus

def process_queue_item(item: QueueItem, 
                      streaming_notify: Callable[[str, Dict[str, Any]], None],
                      log_update: Optional[Callable]):
    """
    Process a queue item from start to finish
    Used by the queue worker thread
    """
    from .core import ensure_model_loaded
    from .inference import generate_streaming
    
    # Ensure model loaded
    if not ensure_model_loaded():
        _fail_item(item, "Model not loaded", streaming_notify, log_update)
        return
    
    print(f"🎲 Processing: {item.prompt_type}")
    
    # Streaming callback
    def on_stream(partial_text):
        item.partial_response = partial_text
        streaming_notify("generation_update", {
            "request_id": item.id,
            "partial_text": partial_text,
            "tokens_so_far": len(partial_text.split()) if partial_text else 0
        })
    
    # Generate
    result = generate_streaming(
        prompt=item.prompt,
        max_tokens=item.max_tokens,
        temperature=item.temperature,
        callback=on_stream
    )
    
    # Handle result
    item.result = result
    item.completed_at = datetime.utcnow()
    
    if result['success']:
        item.status = QueueItemStatus.COMPLETED
        
        if log_update and item.log_id:
            log_update(item.log_id, 'completed', None, result.get('text', ''), result.get('tokens', 0))
        
        streaming_notify("generation_completed", {
            "item": item.to_dict(),
            "final_text": result.get('text', ''),
            "tokens_generated": result.get('tokens', 0),
            "duration": result.get('duration', 0)
        })
        
    else:
        _fail_item(item, result.get('error', 'Unknown error'), streaming_notify, log_update)

def _fail_item(item: QueueItem, error_msg: str, streaming_notify: Callable, log_update: Optional[Callable]):
    """Handle item failure"""
    item.status = QueueItemStatus.FAILED
    item.error = error_msg
    item.completed_at = datetime.utcnow()
    
    if log_update and item.log_id:
        log_update(item.log_id, 'failed', error_msg)
    
    streaming_notify("generation_failed", {
        "item": item.to_dict(),
        "error": error_msg
    })

def generate_with_logging(prompt: str, prompt_type: str, prompt_name: str,
                         max_tokens: int = 256, temperature: float = 0.8,
                         priority: int = 5, wait: bool = True) -> Dict[str, Any]:
    """
    Generate with automatic logging and queueing
    Main entry point for all LLM generation
    """
    from backend.models.llm_log import LLMLog
    from .queue import get_llm_queue
    
    # Create log
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
            'error': 'Could not create log',
            'log_id': None
        }
    
    # Queue request
    queue = get_llm_queue()
    request_id = queue.add_request(
        prompt=prompt,
        max_tokens=max_tokens,
        temperature=temperature,
        prompt_type=prompt_type,
        priority=priority,
        log_id=log.id
    )
    
    if not wait:
        return {
            'success': True,
            'request_id': request_id,
            'log_id': log.id
        }
    
    # Wait for completion
    import time
    timeout = 600  # 10 minutes
    start_time = time.time()
    
    while time.time() - start_time < timeout:
        status = queue.get_request_status(request_id)
        
        if not status:
            break
        
        if status['status'] == 'completed':
            return {
                'success': True,
                'request_id': request_id,
                'log_id': log.id,
                'text': status['result']['text'],
                'tokens': status['result']['tokens'],
                'duration': status['result']['duration']
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
        'error': 'Generation timed out',
        'request_id': request_id,
        'log_id': log.id
    }