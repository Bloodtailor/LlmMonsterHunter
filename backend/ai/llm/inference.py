# LLM Inference Module
# CLEAN INTERFACE: Just takes prompt and loads everything else from database
# Single Responsibility: Pure model inference with streaming

import time
import threading
from typing import Dict, Any, Callable, Optional

# Generation lock to ensure only one generation at a time
_generation_lock = threading.Lock()
_current_generation = None

def generate_streaming(prompt: str, callback: Optional[Callable[[str], None]] = None, **params) -> Dict[str, Any]:
    """
    Generate text with real-time streaming using llama-cpp-python
    
    Args:
        prompt (str): Text to generate from
        callback (callable): Function to call with partial text updates
        **params: All inference parameters (passed directly to model)
    
    Returns:
        dict: Generation results with text, timing, and metadata
    """
    global _current_generation
    
    from .core import get_model_instance, is_model_loaded
    
    # Check if model is loaded
    if not is_model_loaded():
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
        # Get model instance
        model = get_model_instance()
        if not model:
            return {
                'success': False,
                'error': 'Model instance not available',
                'text': None,
                'tokens': 0,
                'duration': 0
            }
        
        # Set current generation status
        _current_generation = {
            'start_time': time.time(),
            'prompt': prompt[:100] + "..." if len(prompt) > 100 else prompt,
            'max_tokens': params.get('max_tokens', 256)
        }
        
        print(f"🌊 Starting streaming generation ({params.get('max_tokens', 256)} max tokens, temp={params.get('temperature', 0.8)})")
        start_time = time.time()
        
        # Initialize streaming variables
        accumulated_text = ""
        token_count = 0
        
        # Call callback with initial empty state
        if callback:
            callback("")
        
        # Create the streaming generator with all parameters
        stream = model(
            prompt,
            stream=True,  # Enable streaming!
            **params      # Pass all parameters
        )
        
        # Process the stream
        try:
            for output in stream:
                try:
                    # Extract the token from streaming output
                    if 'choices' in output and len(output['choices']) > 0:
                        choice = output['choices'][0]
                        
                        if 'text' in choice:
                            new_token = choice['text']
                            accumulated_text += new_token
                            token_count += 1
                            
                            # Send streaming update via callback
                            if callback:
                                callback(accumulated_text)
                            
                            # Small delay for visibility
                            time.sleep(0.01)  # 10ms delay
                        
                        # Check if generation is finished
                        if choice.get('finish_reason') is not None:
                            print(f"🏁 Generation finished: {choice.get('finish_reason')}")
                            break
                            
                except Exception as e:
                    print(f"⚠️ Error processing stream token: {e}")
                    continue
                    
        except Exception as e:
            print(f"❌ Error in streaming loop: {e}")
            # Continue with whatever we have so far
        
        end_time = time.time()
        duration = end_time - start_time
        tokens_per_sec = token_count / duration if duration > 0 else 0
        
        print(f"✅ Streaming completed: {token_count} tokens in {duration:.1f}s ({tokens_per_sec:.1f} tok/s)")
        
        # Send final callback update
        if callback:
            callback(accumulated_text)
        
        return {
            'success': True,
            'error': None,
            'text': accumulated_text,
            'tokens': token_count,
            'duration': duration,
            'tokens_per_second': round(tokens_per_sec, 2),
            'parameters_used': params  # For debugging
        }
        
    except Exception as e:
        error_msg = f"Streaming generation failed: {str(e)}"
        print(f"❌ {error_msg}")
        
        return {
            'success': False,
            'error': error_msg,
            'text': accumulated_text if 'accumulated_text' in locals() else None,
            'tokens': token_count if 'token_count' in locals() else 0,
            'duration': time.time() - start_time if 'start_time' in locals() else 0
        }
        
    finally:
        # Clear current generation status
        _current_generation = None
        
        # Release generation lock
        _generation_lock.release()

def is_generating() -> bool:
    """Check if generation is currently in progress"""
    return _current_generation is not None

def get_current_generation_info() -> Optional[Dict[str, Any]]:
    """Get information about current generation, if any"""
    return _current_generation.copy() if _current_generation else None