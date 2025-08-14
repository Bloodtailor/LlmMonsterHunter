# LLM Configuration
# Complete default settings for all LLM operations and llama-cpp parameters

import os

# === Core Generation Parameters ===
DEFAULT_MAX_TOKENS = 256
DEFAULT_TEMPERATURE = 0.8
DEFAULT_TOP_P = 0.9
DEFAULT_TOP_K = 40
DEFAULT_REPEAT_PENALTY = 1.1
DEFAULT_FREQUENCY_PENALTY = 0.0
DEFAULT_PRESENCE_PENALTY = 0.0

# === Advanced Sampling Parameters ===
DEFAULT_TFS_Z = 1.0
DEFAULT_TYPICAL_P = 1.0
DEFAULT_MIROSTAT_MODE = 0
DEFAULT_MIROSTAT_TAU = 5.0
DEFAULT_MIROSTAT_ETA = 0.1

# === Performance Parameters ===
DEFAULT_SEED = -1  # -1 for random seed
DEFAULT_LOGITS_ALL = False
DEFAULT_VOCAB_ONLY = False
DEFAULT_USE_MMAP = True
DEFAULT_USE_MLOCK = True
DEFAULT_NUMA = False

# === Inference Control ===
DEFAULT_PRIORITY = 5
DEFAULT_TIMEOUT_SECONDS = 600
DEFAULT_STOP_SEQUENCES = ["</s>"]

# === Prompt Settings ===
DEFAULT_PROMPT_TYPE = "general"
DEFAULT_PROMPT_NAME = "user_request"
DEFAULT_ECHO = False  # Don't echo the prompt in response

# === Model Loading Parameters ===
DEFAULT_N_THREADS = 8
DEFAULT_N_BATCH = 512
DEFAULT_F16_KV = True
DEFAULT_LOW_VRAM = False

def get_max_tokens():
    """Get maximum tokens to generate"""
    return int(os.getenv('LLM_DEFAULT_MAX_TOKENS', DEFAULT_MAX_TOKENS))

def get_temperature():
    """Get sampling temperature (0.0-2.0)"""
    return float(os.getenv('LLM_DEFAULT_TEMPERATURE', DEFAULT_TEMPERATURE))

def get_top_p():
    """Get nucleus sampling parameter (0.0-1.0)"""
    return float(os.getenv('LLM_DEFAULT_TOP_P', DEFAULT_TOP_P))

def get_top_k():
    """Get top-k sampling parameter"""
    return int(os.getenv('LLM_DEFAULT_TOP_K', DEFAULT_TOP_K))

def get_repeat_penalty():
    """Get repetition penalty (1.0+ to penalize repetition)"""
    return float(os.getenv('LLM_DEFAULT_REPEAT_PENALTY', DEFAULT_REPEAT_PENALTY))

def get_frequency_penalty():
    """Get frequency penalty (-2.0 to 2.0)"""
    return float(os.getenv('LLM_DEFAULT_FREQUENCY_PENALTY', DEFAULT_FREQUENCY_PENALTY))

def get_presence_penalty():
    """Get presence penalty (-2.0 to 2.0)"""
    return float(os.getenv('LLM_DEFAULT_PRESENCE_PENALTY', DEFAULT_PRESENCE_PENALTY))

def get_tfs_z():
    """Get tail-free sampling parameter"""
    return float(os.getenv('LLM_DEFAULT_TFS_Z', DEFAULT_TFS_Z))

def get_typical_p():
    """Get typical sampling parameter"""
    return float(os.getenv('LLM_DEFAULT_TYPICAL_P', DEFAULT_TYPICAL_P))

def get_mirostat_mode():
    """Get mirostat mode (0=disabled, 1=mirostat, 2=mirostat 2.0)"""
    return int(os.getenv('LLM_DEFAULT_MIROSTAT_MODE', DEFAULT_MIROSTAT_MODE))

def get_mirostat_tau():
    """Get mirostat tau parameter"""
    return float(os.getenv('LLM_DEFAULT_MIROSTAT_TAU', DEFAULT_MIROSTAT_TAU))

def get_mirostat_eta():
    """Get mirostat eta parameter"""
    return float(os.getenv('LLM_DEFAULT_MIROSTAT_ETA', DEFAULT_MIROSTAT_ETA))

def get_seed():
    """Get random seed (-1 for random)"""
    return int(os.getenv('LLM_DEFAULT_SEED', DEFAULT_SEED))

def get_stop_sequences():
    """Get default stop sequences"""
    env_stops = os.getenv('LLM_DEFAULT_STOP_SEQUENCES')
    if env_stops:
        return [s.strip() for s in env_stops.split(',')]
    return DEFAULT_STOP_SEQUENCES.copy()

def get_echo():
    """Get whether to echo prompt in response"""
    return os.getenv('LLM_DEFAULT_ECHO', str(DEFAULT_ECHO)).lower() == 'true'

def get_priority():
    """Get queue priority"""
    return int(os.getenv('LLM_DEFAULT_PRIORITY', DEFAULT_PRIORITY))

def get_timeout():
    """Get request timeout in seconds"""
    return int(os.getenv('LLM_DEFAULT_TIMEOUT', DEFAULT_TIMEOUT_SECONDS))

def get_prompt_type():
    """Get default prompt type"""
    return os.getenv('LLM_DEFAULT_PROMPT_TYPE', DEFAULT_PROMPT_TYPE)

def get_prompt_name():
    """Get default prompt name"""
    return os.getenv('LLM_DEFAULT_PROMPT_NAME', DEFAULT_PROMPT_NAME)

def get_all_inference_defaults():
    """
    Get all inference parameters as a dictionary
    Perfect for passing to inference functions
    
    Returns:
        dict: All inference parameters with current defaults
    """
    return {
        # Core generation
        'max_tokens': get_max_tokens(),
        'temperature': get_temperature(),
        'top_p': get_top_p(),
        'top_k': get_top_k(),
        'repeat_penalty': get_repeat_penalty(),
        'frequency_penalty': get_frequency_penalty(),
        'presence_penalty': get_presence_penalty(),
        
        # Advanced sampling
        'tfs_z': get_tfs_z(),
        'typical_p': get_typical_p(),
        'mirostat_mode': get_mirostat_mode(),
        'mirostat_tau': get_mirostat_tau(),
        'mirostat_eta': get_mirostat_eta(),
        
        # Control
        'seed': get_seed(),
        'stop': get_stop_sequences(),
        'echo': get_echo(),
        
        # Metadata
        'prompt_type': get_prompt_type(),
        'prompt_name': get_prompt_name(),
        'priority': get_priority()
    }