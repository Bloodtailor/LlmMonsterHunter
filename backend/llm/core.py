# LLM Core Module
# Handles model loading, inference, and state management
# Ensures only one model is loaded and one generation runs at a time

import os
import threading
import time
from pathlib import Path
from datetime import datetime
from typing import Optional, Dict, Any

# Global state for model management
_model = None
_model_lock = threading.Lock()
_generation_lock = threading.Lock()
_current_generation = None
_model_info = {
    'loaded': False,
    'model_path': None,
    'load_time': None,
    'error': None
}

class LLMStatus:
    """Container for LLM status information"""
    def __init__(self):
        self.model_loaded = False
        self.model_path = None
        self.currently_generating = False
        self.current_prompt_type = None
        self.generation_progress = None
        self.error = None

def get_llm_status() -> Dict[str, Any]:
    """
    Get current LLM status for monitoring
    
    Returns:
        dict: Current status including model state and generation info
    """
    global _model_info, _current_generation
    
    with _model_lock:
        current_gen = _current_generation.copy() if _current_generation else None
    
    return {
        'model_loaded': _model_info['loaded'],
        'model_path': _model_info['model_path'],
        'load_time': _model_info['load_time'],
        'error': _model_info['error'],
        'currently_generating': current_gen is not None,
        'current_generation': current_gen
    }

def load_model() -> bool:
    """
    Load the LLM model from configuration
    Thread-safe, only loads if not already loaded
    
    Returns:
        bool: True if model loaded successfully, False otherwise
    """
    global _model, _model_info
    
    with _model_lock:
        # Check if already loaded
        if _model is not None and _model_info['loaded']:
            print("✅ Model already loaded")
            return True
        
        try:
            print("🔄 Loading LLM model...")
            
            # Get model path from environment
            model_path = os.getenv('LLM_MODEL_PATH')
            if not model_path:
                raise ValueError("LLM_MODEL_PATH not set in .env file")
            
            model_file = Path(model_path)
            if not model_file.exists():
                raise FileNotFoundError(f"Model file not found: {model_path}")
            
            # Import llama-cpp-python (only when needed)
            try:
                from llama_cpp import Llama
            except ImportError:
                raise ImportError("llama-cpp-python not installed. Run: pip install llama-cpp-python")
            
            # Load model with configuration
            print(f"📂 Loading model from: {model_path}")
            start_time = time.time()
            
            _model = Llama(
                model_path=str(model_file),
                n_ctx=int(os.getenv('LLM_CONTEXT_SIZE', '4096')),
                n_gpu_layers=int(os.getenv('LLM_GPU_LAYERS', '35')),
                verbose=False  # Reduce console output
            )
            
            load_duration = time.time() - start_time
            
            # Update model info
            _model_info.update({
                'loaded': True,
                'model_path': str(model_file),
                'load_time': datetime.utcnow().isoformat(),
                'load_duration': round(load_duration, 2),
                'error': None
            })
            
            print(f"✅ Model loaded successfully in {load_duration:.1f} seconds")
            return True
            
        except Exception as e:
            error_msg = f"Failed to load model: {str(e)}"
            print(f"❌ {error_msg}")
            
            _model_info.update({
                'loaded': False,
                'model_path': None,
                'load_time': None,
                'error': error_msg
            })
            
            return False

def unload_model():
    """
    Unload the current model to free memory
    Thread-safe
    """
    global _model, _model_info
    
    with _model_lock:
        if _model is not None:
            print("🗑️  Unloading model...")
            _model = None
            _model_info.update({
                'loaded': False,
                'model_path': None,
                'load_time': None,
                'error': None
            })
            print("✅ Model unloaded")
        else:
            print("⚠️  No model to unload")

def generate_text(prompt: str, max_tokens: int = 256, temperature: float = 0.8, 
                 prompt_type: str = "unknown", stop_sequences: list = None) -> Dict[str, Any]:
    """
    Generate text using the loaded model
    Thread-safe, only one generation at a time
    
    Args:
        prompt (str): Text prompt to generate from
        max_tokens (int): Maximum tokens to generate
        temperature (float): Sampling temperature (0.0-2.0)
        prompt_type (str): Type of prompt for monitoring
        stop_sequences (list): Stop sequences to end generation
    
    Returns:
        dict: Generation results with text, timing, and metadata
    """
    global _model, _current_generation
    
    # Check if model is loaded
    if not _model_info['loaded'] or _model is None:
        return {
            'success': False,
            'error': 'Model not loaded',
            'text': None,
            'tokens': 0,
            'duration': 0
        }
    
    # Acquire generation lock (only one generation at a time)
    if not _generation_lock.acquire(blocking=False):
        return {
            'success': False,
            'error': 'Another generation is currently in progress',
            'text': None,
            'tokens': 0,
            'duration': 0
        }
    
    try:
        # Set current generation status
        _current_generation = {
            'prompt_type': prompt_type,
            'start_time': datetime.utcnow().isoformat(),
            'status': 'generating',
            'tokens_generated': 0
        }
        
        print(f"🔄 Generating {prompt_type} ({max_tokens} max tokens)...")
        start_time = time.time()
        
        # Configure stop sequences - FIX: Use simpler default stop sequences
        if stop_sequences is None:
            stop = ["</s>"]  # Only use model's end-of-sequence token
        else:
            stop = stop_sequences
        
        # 🔧 DEBUG: Print generation parameters
        print(f"🔧 DEBUG: max_tokens={max_tokens}, temperature={temperature}, stop={stop}")
        
        # Generate with the model
        response = _model(
            prompt,
            max_tokens=max_tokens,
            temperature=temperature,
            stop=stop,
            echo=False  # Don't include prompt in response
        )
        
        end_time = time.time()
        duration = end_time - start_time
        
        # 🔧 DEBUG: Print raw response structure
        print(f"🔧 DEBUG: Raw response type: {type(response)}")
        print(f"🔧 DEBUG: Raw response keys: {list(response.keys()) if isinstance(response, dict) else 'Not a dict'}")
        
        # Extract response data with better error handling
        try:
            generated_text = response['choices'][0]['text']
            tokens_generated = response['usage']['completion_tokens']
            
            # 🔧 DEBUG: Print extraction results
            print(f"🔧 DEBUG: Extracted text: {repr(generated_text)}")
            print(f"🔧 DEBUG: Extracted tokens: {tokens_generated}")
            print(f"🔧 DEBUG: Text length: {len(generated_text) if generated_text else 'None/Empty'}")
            
        except KeyError as e:
            print(f"❌ KeyError extracting response data: {e}")
            print(f"🔧 DEBUG: Full response: {response}")
            return {
                'success': False,
                'error': f'Response format error: {e}',
                'text': None,
                'tokens': 0,
                'duration': duration
            }
        except Exception as e:
            print(f"❌ Error extracting response data: {e}")
            return {
                'success': False,
                'error': f'Extraction error: {e}',
                'text': None,
                'tokens': 0,
                'duration': duration
            }
        
        print(f"✅ Generated {tokens_generated} tokens in {duration:.1f}s ({tokens_generated/duration:.1f} tok/s)")
        
        return {
            'success': True,
            'error': None,
            'text': generated_text,
            'tokens': tokens_generated,
            'duration': duration,
            'tokens_per_second': round(tokens_generated / duration, 2) if duration > 0 else 0
        }
        
    except Exception as e:
        error_msg = f"Generation failed: {str(e)}"
        print(f"❌ {error_msg}")
        
        return {
            'success': False,
            'error': error_msg,
            'text': None,
            'tokens': 0,
            'duration': time.time() - start_time if 'start_time' in locals() else 0
        }
        
    finally:
        # Clear current generation status
        _current_generation = None
        
        # Release generation lock
        _generation_lock.release()

def is_model_loaded() -> bool:
    """Check if model is currently loaded"""
    return _model_info['loaded'] and _model is not None

def is_generating() -> bool:
    """Check if generation is currently in progress"""
    return _current_generation is not None

def get_current_generation_info() -> Optional[Dict[str, Any]]:
    """Get information about current generation, if any"""
    return _current_generation.copy() if _current_generation else None

# Utility functions for model management

def ensure_model_loaded() -> bool:
    """
    Ensure model is loaded, load if necessary
    
    Returns:
        bool: True if model is ready, False if failed to load
    """
    if is_model_loaded():
        return True
    
    return load_model()

def warm_up_model():
    """
    Warm up the model with a simple generation to prepare for use
    This can reduce latency on the first real generation
    """
    if not ensure_model_loaded():
        return False
    
    print("🔥 Warming up model...")
    warm_up_result = generate_text(
        prompt="Hello", 
        max_tokens=5, 
        temperature=0.1,
        prompt_type="warmup"
    )
    
    if warm_up_result['success']:
        print("✅ Model warmed up successfully")
        return True
    else:
        print(f"⚠️  Model warmup failed: {warm_up_result['error']}")
        return False