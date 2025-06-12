# LLM Inference Module
# ONLY handles actual text generation with streaming
# No queue, no logging - pure inference operations

import time
import threading
from typing import Dict, Any, Callable, Optional, List

# Generation lock to ensure only one generation at a time
_generation_lock = threading.Lock()
_current_generation = None

def generate_streaming(prompt: str, max_tokens: int = 256, temperature: float = 0.8,
                      callback: Optional[Callable[[str], None]] = None,
                      stop_sequences: Optional[List[str]] = None) -> Dict[str, Any]:
    """
    Generate text with real-time streaming using llama-cpp-python
    This is the ONLY function that actually talks to the model
    
    Args:
        prompt (str): Text prompt to generate from
        max_tokens (int): Maximum tokens to generate
        temperature (float): Sampling temperature (0.0-2.0)
        callback (callable): Function to call with partial text updates
        stop_sequences (list): Stop sequences to end generation
    
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
            'max_tokens': max_tokens
        }
        
        print(f"🌊 Starting streaming generation ({max_tokens} max tokens)")
        start_time = time.time()
        
        # Configure stop sequences
        if stop_sequences is None:
            stop = ["</s>"]
        else:
            stop = stop_sequences
        
        # Initialize streaming variables
        accumulated_text = ""
        token_count = 0
        
        # Call callback with initial empty state
        if callback:
            callback("")
        
        # Create the streaming generator
        stream = model(
            prompt,
            max_tokens=max_tokens,
            temperature=temperature,
            stop=stop,
            echo=False,
            stream=True,  # Enable streaming!
            # Performance optimizations
            top_p=0.9,
            repeat_penalty=1.1,
            tfs_z=1.0,
            typical_p=1.0,
            mirostat_mode=0,
            seed=-1
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
                            
                            # Small delay for visibility (optional)
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
            'tokens_per_second': round(tokens_per_sec, 2)
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

def generate_simple(prompt: str, max_tokens: int = 256, temperature: float = 0.8,
                   stop_sequences: Optional[List[str]] = None) -> Dict[str, Any]:
    """
    Simple non-streaming generation for cases where streaming isn't needed
    Just calls generate_streaming with a no-op callback
    
    Args:
        prompt (str): Text prompt
        max_tokens (int): Maximum tokens
        temperature (float): Sampling temperature
        stop_sequences (list): Stop sequences
    
    Returns:
        dict: Generation results
    """
    return generate_streaming(
        prompt=prompt,
        max_tokens=max_tokens,
        temperature=temperature,
        callback=None,  # No streaming callback
        stop_sequences=stop_sequences
    )