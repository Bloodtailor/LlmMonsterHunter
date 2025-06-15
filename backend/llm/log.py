# LLM Logging Helper - Simple and Clean
# Makes database logging operations simple and readable
# All functions work with log_id for clean interfaces

from typing import Dict, Any, Optional
from flask import current_app

def create_log(prompt_type: str, prompt_name: str, prompt_text: str, 
               inference_params: Dict[str, Any], parser_config: Optional[Dict[str, Any]] = None) -> Optional[int]:
    """
    Create a new LLM log entry with all parameters
    
    Args:
        prompt_type (str): Type of prompt
        prompt_name (str): Specific prompt name  
        prompt_text (str): Full prompt text
        inference_params (dict): All inference parameters
        parser_config (dict): Parser configuration
        
    Returns:
        int: Log ID if successful, None if failed
    """
    try:
        from backend.models.llm_log import LLMLog
        
        log = LLMLog.create_complete_log(
            prompt_type=prompt_type,
            prompt_name=prompt_name,
            prompt_text=prompt_text,
            inference_params=inference_params,
            parser_config=parser_config
        )
        
        if log.save():
            print(f"✅ Created LLM log {log.id} for {prompt_type}")
            return log.id
        else:
            print(f"❌ Failed to save LLM log for {prompt_type}")
            return None
            
    except Exception as e:
        print(f"❌ Error creating LLM log: {e}")
        return None

def get_log(log_id: int):
    """
    Get log by ID
    
    Args:
        log_id (int): Log ID
        
    Returns:
        LLMLog: Log instance or None
    """
    try:
        from backend.models.llm_log import LLMLog
        return LLMLog.query.get(log_id)
    except Exception as e:
        print(f"❌ Error getting log {log_id}: {e}")
        return None

def mark_started(log_id: int) -> bool:
    """Mark log as generation started"""
    try:
        log = get_log(log_id)
        if log:
            log.mark_started()
            return log.save()
        return False
    except Exception as e:
        print(f"❌ Error marking log {log_id} as started: {e}")
        return False

def mark_attempt_completed(log_id: int, response_text: str, response_tokens: int = None) -> bool:
    """Mark current attempt as completed"""
    try:
        log = get_log(log_id)
        if log:
            log.mark_attempt_completed(response_text, response_tokens)
            return log.save()
        return False
    except Exception as e:
        print(f"❌ Error marking attempt completed for log {log_id}: {e}")
        return False

def mark_parsed(log_id: int, parsed_data: Any) -> bool:
    """Mark parsing as successful"""
    try:
        log = get_log(log_id)
        if log:
            log.mark_parsed(parsed_data)
            return log.save()
        return False
    except Exception as e:
        print(f"❌ Error marking parse success for log {log_id}: {e}")
        return False

def mark_parse_failed(log_id: int, error_message: str) -> bool:
    """Mark parsing as failed"""
    try:
        log = get_log(log_id)
        if log:
            log.mark_parse_failed(error_message)
            return log.save()
        return False
    except Exception as e:
        print(f"❌ Error marking parse failure for log {log_id}: {e}")
        return False

def increment_attempt(log_id: int) -> bool:
    """Increment attempt counter and reset parse status"""
    try:
        log = get_log(log_id)
        if log:
            log.increment_attempt()
            print(f"🔄 Log {log_id} attempt {log.generation_attempt}/{log.max_attempts}")
            return log.save()
        return False
    except Exception as e:
        print(f"❌ Error incrementing attempt for log {log_id}: {e}")
        return False

def mark_completed(log_id: int) -> bool:
    """Mark entire generation as completed"""
    try:
        log = get_log(log_id)
        if log:
            log.mark_generation_completed()
            print(f"✅ Log {log_id} completed successfully")
            return log.save()
        return False
    except Exception as e:
        print(f"❌ Error marking log {log_id} as completed: {e}")
        return False

def mark_failed(log_id: int, error_message: str) -> bool:
    """Mark generation as failed"""
    try:
        log = get_log(log_id)
        if log:
            log.mark_failed(error_message)
            print(f"❌ Log {log_id} failed: {error_message}")
            return log.save()
        return False
    except Exception as e:
        print(f"❌ Error marking log {log_id} as failed: {e}")
        return False

def can_retry(log_id: int) -> bool:
    """Check if log can be retried"""
    try:
        log = get_log(log_id)
        return log.can_retry() if log else False
    except Exception as e:
        print(f"❌ Error checking retry status for log {log_id}: {e}")
        return False

def get_inference_params(log_id: int) -> Optional[Dict[str, Any]]:
    """Get inference parameters from log"""
    try:
        log = get_log(log_id)
        return log.get_inference_params() if log else None
    except Exception as e:
        print(f"❌ Error getting inference params for log {log_id}: {e}")
        return None

def get_parser_config(log_id: int) -> Optional[Dict[str, Any]]:
    """Get parser configuration from log"""
    try:
        log = get_log(log_id)
        return log.parser_config if log else None
    except Exception as e:
        print(f"❌ Error getting parser config for log {log_id}: {e}")
        return None

def get_prompt_text(log_id: int) -> Optional[str]:
    """Get prompt text from log"""
    try:
        log = get_log(log_id)
        return log.prompt_text if log else None
    except Exception as e:
        print(f"❌ Error getting prompt text for log {log_id}: {e}")
        return None