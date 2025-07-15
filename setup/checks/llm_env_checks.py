#!/usr/bin/env python3
"""
LLM Environment Checks Module
Pure detection logic for LLM configuration in .env file
Returns data instead of printing for clean UX flow
"""

import sys
from pathlib import Path
from setup.utils.env_utils import load_env_config

def check_env_model_path():
    """
    Check if .env file has a valid model path configured.
    
    Returns:
        tuple: (success, message) where success indicates if valid model path exists
    """
    env_vars = load_env_config()
    
    if not env_vars:
        return False, ".env file not found or unreadable"
    
    model_path = env_vars.get('LLM_MODEL_PATH', '')
    
    # Check if model path is set and not the default placeholder
    if not model_path:
        return False, "LLM_MODEL_PATH not set in .env file"
    
    if model_path == 'models/your-model.gguf':
        return False, "LLM_MODEL_PATH still set to placeholder value"
    
    # Check if the file actually exists
    model_file = Path(model_path)
    if not model_file.exists():
        return False, f"Model file not found: {model_path}"
    
    if not model_file.is_file():
        return False, f"Model path is not a file: {model_path}"
    
    # Get model info for the message
    model_info = get_model_info(model_path)
    if model_info:
        return True, f"Model configured: {model_info['name']} ({model_info['size_gb']:.1f} GB)"
    else:
        return True, f"Model configured: {model_file.name}"

def get_model_info(model_path):
    """
    Get basic information about a model file.
    
    Args:
        model_path (str): Path to model file
        
    Returns:
        dict or None: Model information or None if error
    """
    try:
        model_file = Path(model_path)
        if not model_file.exists():
            return None
            
        size = model_file.stat().st_size
        size_gb = size / (1024 ** 3)
        
        return {
            'name': model_file.name,
            'size_gb': size_gb
        }
    except Exception:
        return None

def validate_model_file(model_path):
    """
    Check if a file is a valid model.
    
    Args:
        model_path (str): Path to validate
        
    Returns:
        tuple: (success, message) with validation result
    """
    if not model_path:
        return False, "No model path provided"
    
    model_file = Path(model_path)
    
    if not model_file.exists():
        return False, "File does not exist"

    if not model_file.is_file():
        return False, "Path is not a file"

    valid_extensions = ['.gguf', '.ggml', '.bin', '.safetensors']
    if model_file.suffix.lower() not in valid_extensions:
        return False, f"Invalid file type. Expected: {', '.join(valid_extensions)}"

    try:
        size = model_file.stat().st_size
        if size < 100 * 1024 * 1024:  # 100MB minimum
            return False, "File too small to be a language model"
    except Exception:
        pass

    return True, "Valid model file"

def check_model_directory_requirements():
    """Check that a valid model path is configured in .env."""
    env_ok, _ = check_env_model_path()
    return env_ok

def get_diagnostic_info(include_overall=False):
    """
    Get comprehensive LLM environment diagnostic information.
    Used by flows to understand what specifically needs to be addressed.
    
    Args:
        include_overall (bool): Whether to include overall requirement check
    
    Returns:
        dict: All LLM environment check results for detailed analysis
    """
    model_path_ok, model_path_msg = check_env_model_path()
    
    result = {
        'model_path': (model_path_ok, model_path_msg),
    }
    
    if include_overall:
        overall_ok = check_model_directory_requirements()
        result['overall'] = (overall_ok, "All LLM environment requirements met" if overall_ok else "Some LLM environment requirements missing")
    
    return result