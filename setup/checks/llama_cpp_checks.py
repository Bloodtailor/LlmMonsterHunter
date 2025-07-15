#!/usr/bin/env python3
"""
LLama-cpp-python Checks Module
Pure detection logic for llama-cpp-python installation and functionality
Returns data instead of printing for clean UX flow
"""

import subprocess
import sys
import time
from pathlib import Path

def check_llama_cpp_installed():
    """
    Check if llama-cpp-python is installed in the virtual environment.
    
    Returns:
        tuple: (success, message) where success indicates if llama-cpp-python is installed
    """
    pip_path = Path("venv/Scripts/pip.exe")
    
    if not pip_path.exists():
        return False, "Virtual environment pip not found"

    try:
        result = subprocess.run([str(pip_path), "show", "llama-cpp-python"], 
                              capture_output=True, text=True, check=True)
        
        # Extract version information
        version_line = [line for line in result.stdout.split('\n') if line.startswith('Version:')]
        if version_line:
            version = version_line[0].split(':', 1)[1].strip()
            return True, f"llama-cpp-python installed: {version}"
        else:
            return True, "llama-cpp-python installed (version unknown)"
            
    except subprocess.CalledProcessError:
        return False, "llama-cpp-python not installed"

def test_llama_cpp_import():
    """
    Test if llama-cpp-python can be imported in the virtual environment.
    
    Returns:
        tuple: (success, message) where success indicates if import works
    """
    python_path = Path("venv/Scripts/python.exe")
    
    if not python_path.exists():
        return False, "Virtual environment Python not found"
    
    # First check if it's installed
    installed, _ = check_llama_cpp_installed()
    if not installed:
        return False, "llama-cpp-python not installed"
    
    try:
        # Test import
        test_code = """
try:
    from llama_cpp import Llama
    print("IMPORT_SUCCESS")
except ImportError as e:
    print(f"IMPORT_ERROR: {e}")
except Exception as e:
    print(f"OTHER_ERROR: {e}")
"""
        
        result = subprocess.run([str(python_path), "-c", test_code], 
                              capture_output=True, text=True, timeout=30)
        
        output = result.stdout.strip()
        
        if "IMPORT_SUCCESS" in output:
            return True, "llama-cpp-python imports successfully"
        elif "IMPORT_ERROR" in output:
            error_msg = output.split(':', 1)[1].strip() if ':' in output else "unknown import error"
            return False, f"Import failed: {error_msg}"
        else:
            return False, f"Import test failed: {output or result.stderr.strip()}"
            
    except subprocess.TimeoutExpired:
        return False, "Import test timed out"
    except Exception as e:
        return False, f"Import test error: {e}"

def test_llama_cpp_performance():
    """
    Test llama-cpp-python performance by loading the configured model and measuring tokens per second.
    Categorizes performance and determines if running on GPU or CPU.
    
    Returns:
        tuple: (success, message) with performance info and tokens/sec
    """
    python_path = Path("venv/Scripts/python.exe")
    
    if not python_path.exists():
        return False, "Virtual environment Python not found"
    
    # Check if it can import first
    import_ok, import_msg = test_llama_cpp_import()
    if not import_ok:
        return False, f"Cannot test performance: {import_msg}"
    
    # Get model path from .env
    from setup.utils.env_utils import load_env_config
    env_vars = load_env_config()
    model_path = env_vars.get('LLM_MODEL_PATH', '')
    
    if not model_path or model_path == 'models/your-model.gguf':
        return False, "Model path not configured in .env file"
    
    if not Path(model_path).exists():
        return False, f"Model file not found: {model_path}"
    
    try:
        # Performance test code with real model
        test_code = f"""
import time
import sys
import os
sys.path.insert(0, os.getcwd())

try:
    from llama_cpp import Llama
    
    # Load the model
    print("LOADING_MODEL")
    model = Llama(
        model_path=r"{model_path}",
        n_ctx=512,  # Small context for faster test
        n_gpu_layers=35,  # Try GPU acceleration
        verbose=False
    )
    
    # Generate text and measure performance
    prompt = "The quick brown fox"
    
    print("GENERATING_TEXT")
    start_time = time.time()
    
    response = model(
        prompt,
        max_tokens=50,  # Generate 50 tokens for test
        temperature=0.7,
        echo=False
    )
    
    end_time = time.time()
    
    # Calculate tokens per second
    generation_time = end_time - start_time
    tokens_generated = len(response['choices'][0]['text'].split())  # Rough token count
    tokens_per_second = tokens_generated / generation_time if generation_time > 0 else 0
    
    print(f"PERFORMANCE_RESULT: {{tokens_per_second:.1f}} tokens/sec")
    
except ImportError as e:
    print(f"PERFORMANCE_IMPORT_ERROR: {{e}}")
except FileNotFoundError as e:
    print(f"PERFORMANCE_MODEL_ERROR: Model file not found")
except Exception as e:
    print(f"PERFORMANCE_ERROR: {{e}}")
"""
        
        result = subprocess.run([str(python_path), "-c", test_code], 
                              capture_output=True, text=True, timeout=120)
        
        output = result.stdout.strip()
        
        if "PERFORMANCE_RESULT:" in output:
            # Extract tokens per second
            try:
                tokens_line = [line for line in output.split('\n') if 'PERFORMANCE_RESULT:' in line][0]
                tokens_per_sec = float(tokens_line.split('PERFORMANCE_RESULT:')[1].strip().split()[0])
                
                # Categorize performance
                if tokens_per_sec >= 50:
                    category = "very fast"
                    hardware = "high-end GPU acceleration"
                    success = True
                elif tokens_per_sec >= 20:
                    category = "fast" 
                    hardware = "good GPU acceleration"
                    success = True
                elif tokens_per_sec >= 10:
                    category = "decent"
                    hardware = "entry-level GPU acceleration"
                    success = False
                elif tokens_per_sec >= 3:
                    category = "slow"
                    hardware = "weak GPU or limited GPU offload"
                    success = True
                else:
                    # Below 3 tokens/sec - likely CPU-only
                    category = "very slow"
                    hardware = "CPU-only (no GPU acceleration)"
                    success = False
                
                message = f"{tokens_per_sec:.1f} tokens/sec ({category} - {hardware})"
                return success, message
                
            except (ValueError, IndexError):
                return False, f"Could not parse performance result: {output}"
                
        elif "PERFORMANCE_MODEL_ERROR" in output:
            return False, "Model file not found or inaccessible"
        elif "PERFORMANCE_IMPORT_ERROR" in output:
            error_msg = output.split('PERFORMANCE_IMPORT_ERROR:', 1)[1].strip() if ':' in output else "unknown import error"
            return False, f"Import failed: {error_msg}"
        else:
            return False, f"Performance test failed: {output or result.stderr.strip()}"
            
    except subprocess.TimeoutExpired:
        return False, "Performance test timed out (model may be too large or system too slow)"
    except Exception as e:
        return False, f"Performance test error: {e}"

def check_llama_cpp_requirements():
    """
    Check all llama-cpp-python related requirements (for orchestration).
    
    Returns:
        bool: True if llama-cpp-python is installed and working
    """
    
    # Check installation
    installed_ok, _ = check_llama_cpp_installed()
    if not installed_ok:
        return False
    
    # Check if it can import
    import_ok, _ = test_llama_cpp_import()
    
    return installed_ok and import_ok