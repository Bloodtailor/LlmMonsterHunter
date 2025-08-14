# LLM Core Module - CLEANED UP
# ONLY handles model loading, unloading, and status
# No queue, no streaming, no logging - pure model operations

import os
import threading
import time
from pathlib import Path
from datetime import datetime
from typing import Optional, Dict, Any
from backend.core.utils import print_success, print_info, print_error, print_warning

# Global state for model management ONLY
_model = None
_model_lock = threading.Lock()
_model_info = {
    'loaded': False,
    'model_path': None,
    'load_time': None,
    'error': None,
    'gpu_layers': None,
    'load_duration': None
}

def get_model_status() -> Dict[str, Any]:
    """
    Get current model status - ONLY model information
    
    Returns:
        dict: Model state and load information
    """
    global _model_info
    
    with _model_lock:
        return _model_info.copy()

def load_model() -> bool:
    """
    Load the LLM model using .env configuration
    Pure model loading - no side effects
    
    Returns:
        bool: True if model loaded successfully, False otherwise
    """
    global _model, _model_info
    
    with _model_lock:
        # Check if already loaded
        if _model is not None and _model_info['loaded']:
            print_success("Model already loaded, skipping reload")
            return True
        
        try:
            print_info("Loading LLM model...")
            
            # Get configuration from .env
            model_path = os.getenv('LLM_MODEL_PATH')
            gpu_layers = int(os.getenv('LLM_GPU_LAYERS', '35'))
            context_size = int(os.getenv('LLM_CONTEXT_SIZE', '4096'))
            
            if not model_path or not Path(model_path).exists():
                raise FileNotFoundError(f"Model file not found: {model_path}")
            
            print_info(f"Model: {Path(model_path).name}")
            print_info(f"GPU Layers: {gpu_layers}")
            print_info(f"Context Size: {context_size}")
            
            # Import and load model
            from llama_cpp import Llama
            
            start_time = time.time()
            
            _model = Llama(
                model_path=str(model_path),
                n_ctx=context_size,
                n_gpu_layers=gpu_layers,
                n_threads=8,
                n_batch=512,
                f16_kv=True,
                use_mlock=True,
                use_mmap=True,
                verbose=False,
                low_vram=False,
                numa=False
            )
            
            load_duration = time.time() - start_time
            
            # Update model info
            _model_info.update({
                'loaded': True,
                'model_path': str(model_path),
                'load_time': datetime.utcnow().isoformat(),
                'load_duration': round(load_duration, 2),
                'gpu_layers': gpu_layers,
                'error': None
            })
            
            print_success(f"Model loaded successfully in {load_duration:.1f} seconds")
            return True
            
        except Exception as e:
            error_msg = f"Failed to load model: {str(e)}"
            print_error(error_msg)
            
            _model_info.update({
                'loaded': False,
                'model_path': None,
                'load_time': None,
                'load_duration': None,
                'gpu_layers': None,
                'error': error_msg
            })
            
            return False

def unload_model():
    """Unload the current model to free memory"""
    global _model, _model_info
    
    with _model_lock:
        if _model is not None:
            _model = None
            _model_info.update({
                'loaded': False,
                'model_path': None,
                'load_time': None,
                'load_duration': None,
                'gpu_layers': None,
                'error': None
            })

def is_model_loaded() -> bool:
    """Check if model is currently loaded"""
    return _model_info['loaded'] and _model is not None

def get_model_instance():
    """
    Get the loaded model instance
    WARNING: Only use this from inference.py!
    
    Returns:
        Llama model instance or None if not loaded
    """
    global _model
    with _model_lock:
        return _model

def ensure_model_loaded() -> bool:
    """
    Ensure model is loaded, load if necessary
    
    Returns:
        bool: True if model is ready, False if failed to load
    """
    if is_model_loaded():
        return True
    
    return load_model()

def warm_up_model() -> bool:
    """
    Warm up the model with a quick generation
    Uses the inference module to avoid code duplication
    
    Returns:
        bool: True if warmup successful
    """
    if not ensure_model_loaded():
        return False
    
    try:
        from .inference import generate_streaming
        
        print_info("Warming up model...")
        
        # Quick warmup generation
        result = generate_streaming(
            prompt="Hello", 
            max_tokens=5, 
            temperature=0.1,
            callback=lambda text: None  # No-op callback
        )
        
        if result['success']:
            tokens_per_sec = result.get('tokens_per_second', 0)
            if tokens_per_sec > 15:
                print_success(f"Model warmed up successfully ({tokens_per_sec:.1f} tok/s - GPU performance)")
            else:
                print_warning(f"Model warmed up ({tokens_per_sec:.1f} tok/s - check GPU usage)")
            return True
        else:
            print_warning(f"Model warmup failed: {result['error']}")
            return False
            
    except Exception as e:
        print_warning(f"Warmup error: {e}")
        return False