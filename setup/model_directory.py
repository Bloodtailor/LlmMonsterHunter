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

def check_models_directory_exists():
    """Check if models directory exists."""
    models_dir = Path("models")
    
    if models_dir.exists() and models_dir.is_dir():
        print("✅ Models directory exists")
        return True
    else:
        print("❌ Models directory not found")
        return False

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
    """Validate that a file exists and appears to be a model file."""
    model_file = Path(model_path)
    
    if not model_file.exists():
        return False, "File does not exist"
    
    if not model_file.is_file():
        return False, "Path is not a file"
    
    # Check file extension
    valid_extensions = ['.gguf', '.ggml', '.bin', '.safetensors']
    if model_file.suffix.lower() not in valid_extensions:
        return False, f"Invalid file type. Expected: {', '.join(valid_extensions)}"
    
    # Check file size (should be at least 100MB for a real model)
    try:
        size = model_file.stat().st_size
        if size < 100 * 1024 * 1024:  # 100MB
            return False, "File seems too small to be a language model"
    except Exception:
        pass
    
    return True, "Valid model file"

def validate_model_file(model_path):
    """Validate that a file exists and appears to be a model file."""
    model_file = Path(model_path)
    
    if not model_file.exists():
        return False, "File does not exist"
    
    if not model_file.is_file():
        return False, "Path is not a file"
    
    # Check file extension
    valid_extensions = ['.gguf', '.ggml', '.bin', '.safetensors']
    if model_file.suffix.lower() not in valid_extensions:
        return False, f"Invalid file type. Expected: {', '.join(valid_extensions)}"
    
    # Check file size (should be at least 100MB for a real model)
    try:
        size = model_file.stat().st_size
        if size < 100 * 1024 * 1024:  # 100MB
            return False, "File seems too small to be a language model"
    except Exception:
        pass
    
    return True, "Valid model file"

def check_model_directory_requirements():
    """Check all model directory requirements."""
    print("Checking model directory and LLM model files...")
    
    # Check directory exists
    if not check_models_directory_exists():
        return False
    
    # Check for configured model path in .env
    if check_env_model_path():
        print("✅ Model is configured and accessible")
        return True
    
    # Check for model files in local directory
    model_files = find_model_files_anywhere()
    if model_files:
        print(f"✅ Found {len(model_files)} model file(s) in models directory")
        for model_file in model_files:
            info = get_model_file_info(model_file)
            if info:
                print(f"   {info['name']} ({info['size_gb']:.1f} GB)")
        print("⚠️  Model path not configured in .env file")
        return False
    
    print("❌ No model files found and no model path configured")
    return False

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
                # Use forward slashes for consistency, even on Windows
                normalized_path = str(model_path).replace('\\', '/')
                lines[i] = f'LLM_MODEL_PATH={normalized_path}\n'
                updated = True
                break
        
        if not updated:
            # Add the line if it doesn't exist
            normalized_path = str(model_path).replace('\\', '/')
            lines.append(f'\nLLM_MODEL_PATH={normalized_path}\n')
        
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
    
    # Check if model is already configured
    if check_env_model_path():
        print("✅ Model is already configured and working")
        
        choice = input("Do you want to change the model? (y/n): ").lower().strip()
        if choice not in ['y', 'yes']:
            return True
    
    # Give user options for model setup
    print("\n📋 Model Setup Options:")
    print("1. Use a model file from anywhere on your computer")
    print("2. Copy a model to the local models/ directory")
    print("3. Download a model (you'll need to do this manually)")
    
    while True:
        choice = input("\nChoose an option (1-3): ").strip()
        
        if choice == "1":
            return setup_custom_model_path()
        elif choice == "2":
            return setup_local_model()
        elif choice == "3":
            return show_download_instructions()
        else:
            print("Invalid choice. Please enter 1, 2, or 3.")

def setup_custom_model_path():
    """Set up a model using a custom file path."""
    print("\n📁 Using a model from anywhere on your computer")
    print("")
    print("💡 Examples of valid paths:")
    print("   C:/Users/soulo/.cache/lm-studio/models/TheBloke/Kunoichi-7B-GGUF/kunoichi-7b.Q6_K.gguf")
    print("   D:/AI_Models/llama-2-7b-chat.Q4_K_M.gguf")
    print("   C:/Downloads/mistral-7b-instruct.gguf")
    print("")
    print("💡 Tips:")
    print("   • You can copy-paste the full path")
    print("   • Use forward slashes (/) or backslashes (\\)")
    print("   • Make sure the file exists and is a .gguf model")
    
    while True:
        model_path = input("\nEnter the full path to your model file: ").strip()
        
        if not model_path:
            choice = input("No path entered. Try again? (y/n): ").lower().strip()
            if choice not in ['y', 'yes']:
                return False
            continue
        
        # Clean up the path (remove quotes if user copied from file explorer)
        model_path = model_path.strip('"').strip("'")
        
        # Validate the model file
        is_valid, message = validate_model_file(model_path)
        
        if is_valid:
            # Update .env file with the path
            if update_env_model_path(model_path):
                print(f"✅ Model configured successfully!")
                
                # Show model info
                model_file = Path(model_path)
                info = get_model_file_info(model_file)
                if info:
                    print(f"   Model: {info['name']}")
                    print(f"   Size: {info['size_gb']:.1f} GB")
                    print(f"   Path: {model_path}")
                
                return True
            else:
                print("❌ Failed to update configuration")
                return False
        else:
            print(f"❌ Invalid model file: {message}")
            print(f"   Path checked: {model_path}")
            
            choice = input("Try a different path? (y/n): ").lower().strip()
            if choice not in ['y', 'yes']:
                return False

def setup_local_model():
    """Set up a model in the local models directory."""
    # Check for existing models in local directory
    model_files = find_model_files_anywhere()
    
    if model_files:
        print(f"\n✅ Found {len(model_files)} model file(s) in models/ directory:")
        for i, model_file in enumerate(model_files):
            info = get_model_file_info(model_file)
            if info:
                print(f"   {i+1}. {info['name']} ({info['size_gb']:.1f} GB)")
            else:
                print(f"   {i+1}. {model_file.name}")
        
        # Let user choose a model
        while True:
            try:
                choice = input(f"\nEnter model number to use (1-{len(model_files)}): ")
                model_index = int(choice) - 1
                
                if 0 <= model_index < len(model_files):
                    selected_model = model_files[model_index]
                    relative_path = selected_model.relative_to(Path.cwd())
                    
                    if update_env_model_path(str(relative_path)):
                        print(f"✅ Model configured: {selected_model.name}")
                        return True
                    else:
                        print("❌ Failed to update model configuration")
                        return False
                else:
                    print("Invalid choice. Please try again.")
            except ValueError:
                print("Please enter a valid number.")
    
    else:
        print("\n❌ No model files found in models/ directory")
        print("📋 To use this option:")
        print("1. Copy your model file (.gguf) to the models/ directory")
        print("2. Run this setup again")
        print("")
        
        choice = input("Do you want to try option 1 (custom path) instead? (y/n): ").lower().strip()
        if choice in ['y', 'yes']:
            return setup_custom_model_path()
        
        return False

def show_download_instructions():
    """Show instructions for downloading models."""
    print("\n📥 Download Model Instructions")
    print("")
    print("📋 Recommended models (download and use option 1 or 2):")
    print("• Llama 2 7B Chat (4GB) - Good balance of speed and quality")
    print("• Mistral 7B Instruct (4GB) - Fast and efficient")
    print("• Code Llama 7B (4GB) - Good for technical conversations")
    print("")
    print("📋 Where to download:")
    print("• Hugging Face: https://huggingface.co/models")
    print("• Search for models with 'GGUF' format")
    print("• Look for 'Q4_K_M' or 'Q6_K' quantization")
    print("• Example: 'llama-2-7b-chat.Q4_K_M.gguf'")
    print("")
    print("📋 Popular model collections:")
    print("• TheBloke (high quality quantized models)")
    print("• Microsoft (Phi models)")
    print("• Meta (Llama models)")
    print("")
    print("📋 After downloading:")
    print("1. Run this launcher again")
    print("2. Choose option 1 to use the downloaded model from anywhere")
    print("3. Or copy it to models/ directory and use option 2")
    
    return False  # User needs to download first

if __name__ == "__main__":
    if len(sys.argv) > 1 and sys.argv[1] == "setup":
        setup_model_directory_interactive()
    else:
        check_model_directory_requirements()