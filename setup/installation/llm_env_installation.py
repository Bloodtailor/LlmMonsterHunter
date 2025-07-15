#!/usr/bin/env python3
"""
LLM Environment Installation Module
Pure installation logic for LLM configuration in .env file
"""

from pathlib import Path
from setup.utils.env_utils import update_env_config
from setup.checks.llm_env_checks import get_model_info

def update_env_model_path(model_path):
    """
    Update the model path in .env file.
    
    Args:
        model_path (str): Path to the model file
        
    Returns:
        tuple: (success, message) with update result
    """
    if not model_path:
        return False, "No model path provided"
    
    # Normalize path for cross-platform compatibility
    normalized_path = str(model_path).replace('\\', '/')
    
    # Update the .env file using env_utils
    success, message = update_env_config(LLM_MODEL_PATH=normalized_path)
    
    if success:
        # Get model info for success message
        model_info = get_model_info(normalized_path)
        if model_info:
            return True, f"Model path updated: {model_info['name']} ({model_info['size_gb']:.1f} GB)"
        else:
            return True, f"Model path updated: {Path(normalized_path).name}"
    else:
        return False, f"Failed to update .env file: {message}"