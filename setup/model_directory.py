#!/usr/bin/env python3
"""
Model Directory Setup Module
Checks for models directory and available LLM model files
"""

import os
import sys
from pathlib import Path

def check_models_directory_exists():
    """Check if models directory exists."""
    models_dir = Path("models")
    
    if models_dir.exists() and models_dir.is_dir():
        print("✅ Models directory exists")
        return True
    else:
        print("❌ Models directory not found")
        return False

def check_model_files():
    """Check for LLM model files in the models directory."""
    models_dir = Path("models")
    
    if not models_dir.exists():
        return []
    
    # Look for common model file extensions
    model_extensions = ['.gguf', '.ggml', '.bin', '.safetensors']
    model_files = []
    
    for ext in model_extensions:
        model_files.extend(models_dir.glob(f'*{ext}'))
    
    return model_files

def check_env_model_path():
    """Check if .env file has a valid model path."""
    env_file = Path(".env")
    
    if not env_file.exists():
        print("❌ .env file not found")
        return False
    
    try:
        with open(env_file, 'r') as f:
            content = f.read()
        
        # Look for LLM_MODEL_PATH
        for line in content.split('\n'):
            if line.strip().startswith('LLM_MODEL_PATH='):
                model_path = line.split('=', 1)[1].strip()
                
                if model_path and model_path != 'models/your-model.gguf':
                    model_file = Path(model_path)
                    if model_file.exists():
                        print(f"✅ Model path in .env is valid: {model_path}")
                        return True
                    else:
                        print(f"❌ Model path in .env not found: {model_path}")
                        return False
                else:
                    print("❌ Model path in .env not configured")
                    return False
        
        print("❌ LLM_MODEL_PATH not found in .env")
        return False
        
    except Exception as e:
        print(f"❌ Error reading .env file: {e}")
        return False

def get_model_file_info(model_path):
    """Get information about a model file."""
    try:
        size = model_path.stat().st_size
        size_gb = size / (1024 ** 3)
        
        return {
            'name': model_path.name,
            'size_bytes': size,
            'size_gb': size_gb,
            'extension': model_path.suffix
        }
    except Exception:
        return None

def check_model_directory_requirements():
    """Check all model directory requirements."""
    print("Checking model directory and LLM model files...")
    
    # Check directory exists
    if not check_models_directory_exists():
        return False
    
    # Check for model files
    model_files = check_model_files()
    if not model_files:
        print("❌ No model files found in models directory")
        return False
    
    print(f"✅ Found {len(model_files)} model file(s):")
    for model_file in model_files:
        info = get_model_file_info(model_file)
        if info:
            print(f"   {info['name']} ({info['size_gb']:.1f} GB)")
        else:
            print(f"   {model_file.name} (could not read size)")
    
    # Check .env configuration
    if not check_env_model_path():
        print("⚠️  Model path not configured in .env file")
        return False
    
    print("✅ Model directory and configuration are ready")
    return True

def create_models_directory():
    """Create the models directory."""
    models_dir = Path("models")
    
    try:
        models_dir.mkdir(exist_ok=True)
        print("✅ Models directory created")
        
        # Create a README file
        readme_content = """# LLM Models Directory

This directory contains local LLM models for the Monster Hunter Game.

## Setup
1. Download a compatible GGUF model (7B or 13B recommended)
2. Place the model file in this directory
3. Update the LLM_MODEL_PATH in your .env file

## Recommended Models
- Llama 2 7B Chat (llama-2-7b-chat.Q4_K_M.gguf)
- Mistral 7B Instruct (mistral-7b-instruct-v0.1.Q4_K_M.gguf)
- Code Llama 7B (codellama-7b-instruct.Q4_K_M.gguf)

## Where to Download
- Hugging Face: https://huggingface.co/models
- Search for models with "GGUF" format
- Look for quantized versions (Q4_K_M is a good balance of size/quality)

## CUDA Support
Make sure you have llama-cpp-python[cuda] installed for GPU acceleration.
"""
        
        readme_file = models_dir / "README.md"
        with open(readme_file, 'w') as f:
            f.write(readme_content)
        
        print("✅ Models directory README created")
        return True
        
    except Exception as e:
        print(f"❌ Failed to create models directory: {e}")
        return False

def update_env_model_path(model_path):
    """Update the model path in .env file."""
    env_file = Path(".env")
    
    if not env_file.exists():
        print("❌ .env file not found")
        return False
    
    try:
        with open(env_file, 'r') as f:
            lines = f.readlines()
        
        # Update or add LLM_MODEL_PATH
        updated = False
        for i, line in enumerate(lines):
            if line.strip().startswith('LLM_MODEL_PATH='):
                lines[i] = f'LLM_MODEL_PATH={model_path}\n'
                updated = True
                break
        
        if not updated:
            lines.append(f'\nLLM_MODEL_PATH={model_path}\n')
        
        with open(env_file, 'w') as f:
            f.writelines(lines)
        
        print(f"✅ Model path updated in .env: {model_path}")
        return True
        
    except Exception as e:
        print(f"❌ Failed to update .env file: {e}")
        return False

def setup_model_directory_interactive():
    """Interactive setup for model directory."""
    print("Setting up model directory and LLM models...")
    
    # Create directory if needed
    if not check_models_directory_exists():
        if not create_models_directory():
            return False
    
    # Check for existing models
    model_files = check_model_files()
    
    if model_files:
        print(f"\n✅ Found {len(model_files)} existing model file(s):")
        for i, model_file in enumerate(model_files):
            info = get_model_file_info(model_file)
            if info:
                print(f"   {i+1}. {info['name']} ({info['size_gb']:.1f} GB)")
            else:
                print(f"   {i+1}. {model_file.name}")
        
        # Let user choose a model
        while True:
            try:
                choice = input(f"\nEnter model number to use (1-{len(model_files)}), or 0 to skip: ")
                if choice == '0':
                    print("⏭️  Skipping model configuration")
                    break
                
                model_index = int(choice) - 1
                if 0 <= model_index < len(model_files):
                    selected_model = model_files[model_index]
                    relative_path = selected_model.relative_to(Path.cwd())
                    
                    if update_env_model_path(str(relative_path)):
                        print(f"✅ Model configured: {selected_model.name}")
                        break
                    else:
                        print("❌ Failed to update model configuration")
                        return False
                else:
                    print("Invalid choice. Please try again.")
            except ValueError:
                print("Please enter a valid number.")
    
    else:
        print("\n❌ No model files found in models directory")
        print("📋 You need to download an LLM model to use the game")
        print("")
        print("📋 Recommended models (download and place in models/ directory):")
        print("1. Llama 2 7B Chat (4GB) - Good balance of speed and quality")
        print("2. Mistral 7B Instruct (4GB) - Fast and efficient")
        print("3. Code Llama 7B (4GB) - Good for technical conversations")
        print("")
        print("📋 Where to download:")
        print("• Hugging Face: https://huggingface.co/models")
        print("• Search for models with 'GGUF' format")
        print("• Look for 'Q4_K_M' quantization (good size/quality balance)")
        print("• Example: 'llama-2-7b-chat.Q4_K_M.gguf'")
        print("")
        print("📋 After downloading:")
        print("1. Place the .gguf file in the models/ directory")
        print("2. Run this setup again to configure the model path")
        print("")
        
        input("Press Enter after downloading a model file...")
        
        # Check again for new models
        new_model_files = check_model_files()
        if new_model_files:
            print("✅ Model files detected! Continuing setup...")
            return setup_model_directory_interactive()  # Recurse to handle model selection
        else:
            print("❌ No model files found. You can continue without models but the game won't work.")
            return False
    
    # Final verification
    if check_env_model_path():
        print("✅ Model directory and configuration completed")
        return True
    else:
        print("⚠️  Model directory setup incomplete")
        print("💡 You can run this setup again after downloading models")
        return False

if __name__ == "__main__":
    if len(sys.argv) > 1 and sys.argv[1] == "setup":
        setup_model_directory_interactive()
    else:
        check_model_directory_requirements()