# LLM Module Package - CLEAN INTERFACE
# Exports core LLM functionality with simplified architecture

# Core model operations
from .core import (
    load_model, 
    unload_model, 
    get_model_status,
    is_model_loaded, 
    ensure_model_loaded,
    warm_up_model
)

# Inference (direct inference - use services for high-level operations)
from .inference import (
    generate_streaming,
    is_generating
)

# Prompt management
from .prompt_engine import (
    get_template_config,
    build_prompt
)

# Parser
from .parser import (
    parse_response,
    ParseResult
)

# Combined status function
def get_llm_status():
    """Get comprehensive LLM status"""
    status = get_model_status()
    status['currently_generating'] = is_generating()
    return status

__all__ = [
    # Core model operations
    'load_model',
    'unload_model', 
    'get_model_status',
    'get_llm_status',
    'is_model_loaded',
    'ensure_model_loaded',
    'warm_up_model',
    
    # Inference (use services for high-level operations)
    'generate_streaming',
    'is_generating',
    
    # Queue management
    'get_llm_queue',
    
    # Prompt and parsing utilities
    'get_template_config',
    'build_prompt',
    'parse_response',
    'ParseResult'
]