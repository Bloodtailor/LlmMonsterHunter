# LLM Core Module
# Handles model loading, inference, and state management
# OPTIMIZED: Uses existing .env configuration with GPU optimizations

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
    'error': None,
    'gpu_layers': None,
    'load_duration': None
}

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
        'load_duration': _model_info['load_duration'],
        'gpu_layers': _model_info['gpu_layers'],
        'error': _model_info['error'],
        'currently_generating': current_gen is not None,
        'current_generation': current_gen
    }

def load_model() -> bool:
    """
    Load the LLM model using existing .env configuration with optimizations
    Only loads if not already loaded - avoids unnecessary reloads
    
    Returns:
        bool: True if model loaded successfully, False otherwise
    """
    global _model, _model_info
    
    with _model_lock:
        # 🔧 CHECK: If already loaded, don't reload
        if _model is not None and _model_info['loaded']:
            print("✅ Model already loaded, skipping reload")
            return True
        
        try:
            print("🔄 Loading LLM model with optimized settings...")
            
            # Get configuration from .env (verified by startup script)
            model_path = os.getenv('LLM_MODEL_PATH')
            gpu_layers = int(os.getenv('LLM_GPU_LAYERS', '35'))
            context_size = int(os.getenv('LLM_CONTEXT_SIZE', '4096'))
            
            print(f"📋 Configuration from .env:")
            print(f"   Model: {Path(model_path).name}")
            print(f"   GPU Layers: {gpu_layers}")
            print(f"   Context Size: {context_size}")
            
            # Import llama-cpp-python (CUDA support verified by startup)
            from llama_cpp import Llama
            
            # Load model with full optimizations
            print(f"🚀 Loading with optimizations...")
            start_time = time.time()
            
            _model = Llama(
                model_path=str(model_path),
                n_ctx=context_size,           # From .env
                n_gpu_layers=gpu_layers,      # From .env - ensures GPU usage
                n_threads=8,                  # 🔧 OPTIMIZED: 8 threads as requested
                n_batch=512,                  # 🔧 OPTIMIZED: Batch processing
                f16_kv=True,                  # 🔧 OPTIMIZED: FP16 key-value cache
                use_mlock=True,               # 🔧 OPTIMIZED: Lock model in memory
                use_mmap=True,                # 🔧 OPTIMIZED: Memory mapping
                verbose=False,                # Reduce console spam
                # Additional optimizations
                low_vram=False,               # We have good GPU, don't limit VRAM
                numa=False                    # Usually better performance on single GPU
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
            
            print(f"✅ Model loaded successfully in {load_duration:.1f} seconds")
            print(f"🎮 GPU Layers: {gpu_layers} (ensuring GPU acceleration)")
            
            return True
            
        except Exception as e:
            error_msg = f"Failed to load model: {str(e)}"
            print(f"❌ {error_msg}")
            
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
            print("🗑️  Unloading model...")
            _model = None
            _model_info.update({
                'loaded': False,
                'model_path': None,
                'load_time': None,
                'load_duration': None,
                'gpu_layers': None,
                'error': None
            })
            print("✅ Model unloaded")
        else:
            print("⚠️  No model to unload")

def generate_text(prompt: str, max_tokens: int = 256, temperature: float = 0.8, 
                 prompt_type: str = "unknown", stop_sequences: list = None) -> Dict[str, Any]:
    """
    Generate text using the loaded model with optimized settings
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
        
        # Configure stop sequences
        if stop_sequences is None:
            stop = ["</s>"]
        else:
            stop = stop_sequences
        
        # 🔧 OPTIMIZED: Generate with performance settings
        response = _model(
            prompt,
            max_tokens=max_tokens,
            temperature=temperature,
            stop=stop,
            echo=False,
            # 🔧 PERFORMANCE OPTIMIZATIONS:
            top_p=0.9,                    # Nucleus sampling for quality
            repeat_penalty=1.1,           # Reduce repetition
            tfs_z=1.0,                    # Tail free sampling
            typical_p=1.0,                # Typical sampling
            mirostat_mode=0,              # Disable mirostat for speed
            seed=-1                       # Random seed
        )
        
        end_time = time.time()
        duration = end_time - start_time
        
        # Extract response data
        try:
            generated_text = response['choices'][0]['text']
            tokens_generated = response['usage']['completion_tokens']
            
        except KeyError as e:
            print(f"❌ Response format error: {e}")
            return {
                'success': False,
                'error': f'Response format error: {e}',
                'text': None,
                'tokens': 0,
                'duration': duration
            }
        
        tokens_per_sec = tokens_generated / duration if duration > 0 else 0
        print(f"✅ Generated {tokens_generated} tokens in {duration:.1f}s ({tokens_per_sec:.1f} tok/s)")
        
        return {
            'success': True,
            'error': None,
            'text': generated_text,
            'tokens': tokens_generated,
            'duration': duration,
            'tokens_per_second': round(tokens_per_sec, 2)
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
    """Warm up the model with a quick generation"""
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
        tokens_per_sec = warm_up_result['tokens_per_second']
        if tokens_per_sec > 15:
            print(f"✅ Model warmed up successfully ({tokens_per_sec:.1f} tok/s - GPU performance)")
        else:
            print(f"⚠️  Model warmed up ({tokens_per_sec:.1f} tok/s - check GPU usage)")
        return True
    else:
        print(f"⚠️  Model warmup failed: {warm_up_result['error']}")
        return False

# Queue integration functions

def queue_generation(prompt: str, max_tokens: int = 256, temperature: float = 0.8,
                    prompt_type: str = "unknown", priority: int = 5) -> str:
    """Queue a generation request instead of executing immediately"""
    from backend.llm.queue import get_llm_queue
    
    queue = get_llm_queue()
    return queue.add_request(
        prompt=prompt,
        max_tokens=max_tokens,
        temperature=temperature,
        prompt_type=prompt_type,
        priority=priority
    )

def get_generation_result(request_id: str) -> Optional[Dict[str, Any]]:
    """Get the result of a queued generation request"""
    from backend.llm.queue import get_llm_queue
    
    queue = get_llm_queue()
    return queue.get_request_status(request_id)

def wait_for_generation(request_id: str, timeout: int = 300) -> Optional[Dict[str, Any]]:
    """Wait for a queued generation to complete"""
    from backend.llm.queue import get_llm_queue, QueueItemStatus
    
    queue = get_llm_queue()
    start_time = time.time()
    
    while time.time() - start_time < timeout:
        status = queue.get_request_status(request_id)
        
        if not status:
            return None
        
        if status['status'] in [QueueItemStatus.COMPLETED.value, QueueItemStatus.FAILED.value]:
            return status
        
        time.sleep(0.5)  # Poll every 500ms
    
    return None  # Timeout