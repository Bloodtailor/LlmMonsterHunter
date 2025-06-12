# LLM Configuration
# Default settings for LLM operations

import os

# Default generation parameters
DEFAULT_MAX_TOKENS = 256
DEFAULT_TEMPERATURE = 0.8
DEFAULT_PRIORITY = 5

# Default prompt settings
DEFAULT_PROMPT_TYPE = "general"
DEFAULT_PROMPT_NAME = "user_request"

# Timeout settings
DEFAULT_TIMEOUT_SECONDS = 600

# Get from environment or use defaults
def get_max_tokens():
    return int(os.getenv('LLM_DEFAULT_MAX_TOKENS', DEFAULT_MAX_TOKENS))

def get_temperature():
    return float(os.getenv('LLM_DEFAULT_TEMPERATURE', DEFAULT_TEMPERATURE))

def get_priority():
    return int(os.getenv('LLM_DEFAULT_PRIORITY', DEFAULT_PRIORITY))

def get_timeout():
    return int(os.getenv('LLM_DEFAULT_TIMEOUT', DEFAULT_TIMEOUT_SECONDS))