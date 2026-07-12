"""
User Messages Package
One dict per audience: default_path holds everything a new player on
the API-first path can ever be shown; the local_extras modules hold the
GPU/CUDA/Build-Tools/GGUF vocabulary that only surfaces when a
developer runs the walkthrough with --local-extras.
"""

from setup.messages.default_path import DEFAULT_PATH_MESSAGES
from setup.messages.local_extras_gpu import LOCAL_EXTRAS_GPU_MESSAGES
from setup.messages.local_extras_llm import LOCAL_EXTRAS_LLM_MESSAGES

MESSAGES = {
    **DEFAULT_PATH_MESSAGES,
    **LOCAL_EXTRAS_GPU_MESSAGES,
    **LOCAL_EXTRAS_LLM_MESSAGES,
}


def get_message(key):
    """
    Get user messages by key

    Args:
        key (str): Message key from MESSAGES dict

    Returns:
        list: List of message lines, or empty list if key not found
    """
    return MESSAGES.get(key, [])


def get_available_messages():
    """
    Get list of all available messages keys

    Returns:
        list: All message keys
    """
    return list(MESSAGES.keys())
