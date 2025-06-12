# LLM Module Package - LEAN INTERFACE
# No legacy code, no bloat, only what we need now

# Core model operations
from .core import (
    load_model, 
    unload_model, 
    get_model_status,
    is_model_loaded, 
    ensure_model_loaded,
    warm_up_model
)

# Inference
from .inference import (
    generate_streaming,
    is_generating
)

# Queue
from .queue import (
    get_llm_queue,
    shutdown_queue
)

# Generation service
from .generation_service import (
    generate_with_logging
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

# Monster generation
from .monster_generation import (
    generate_monster,
    get_available_prompts
)

# Combined status function
def get_llm_status():
    """Get comprehensive LLM status"""
    status = get_model_status()
    status['currently_generating'] = is_generating()
    return status

__all__ = [
    'load_model',
    'unload_model', 
    'get_model_status',
    'get_llm_status',
    'is_model_loaded',
    'ensure_model_loaded',
    'warm_up_model',
    'generate_streaming',
    'is_generating',
    'get_llm_queue',
    'shutdown_queue',
    'generate_with_logging',
    'get_template_config',
    'build_prompt',
    'parse_response',
    'ParseResult',
    'generate_monster',
    'get_available_prompts'
]