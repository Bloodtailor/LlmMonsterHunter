# LLM Module Package
# Provides high-level interface for all LLM operations

from .core import (
    load_model, 
    unload_model, 
    generate_text, 
    get_llm_status, 
    is_model_loaded, 
    is_generating,
    ensure_model_loaded,
    warm_up_model
)

from .parser import (
    parse_response,
    get_available_parsers,
    ParseResult
)

from .monster_generation import (
    generate_monster,
    get_available_prompts
)

__all__ = [
    # Core functions
    'load_model',
    'unload_model', 
    'generate_text',
    'get_llm_status',
    'is_model_loaded',
    'is_generating',
    'ensure_model_loaded',
    'warm_up_model',
    
    # Parser functions
    'parse_response',
    'get_available_parsers',
    'ParseResult',
    
    # Monster generation
    'generate_monster',
    'get_available_prompts',
    'test_monster_generation'
]