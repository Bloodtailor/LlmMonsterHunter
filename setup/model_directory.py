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
        return True
    return False

def check_env_model_path():
    """Check if .env file has a valid model path."""
    env_file = Path(".env")
    if not env_file.exists():
        return False
    
    try:
        with open(env_file, 'r') as f:
            content = f.read()
        
        for line in content.split('\n'):
            if line.strip().startswith('LLM_MODEL_PATH='):
                model_path = line.split('=', 1)[1].strip()
                
                if model_path and model_path != 'models/your-model.gguf':
                    model_file = Path(model_path)
                    if model_file.exists() and model_file.is_file():
                        return True
        return False
    except Exception:
        return False

def find_local_models():
    """Find model files in the models directory."""
    models_dir = Path("models")
    if not models_dir.exists():
        return []
    
    model_files = []
    for ext in ['.gguf', '.ggml', '.bin', '.safetensors']:
        model_files.extend(models_dir.glob(f'*{ext}'))
    
    return model_files

def get_model_info(model_path):
    """Get basic info about a model file."""
    try:
        model_file = Path(model_path)
        size = model_file.stat().st_size
        size_gb = size / (1024 ** 3)
        return {
            'name': model_file.name,
            'size_gb': size_gb
        }
    except Exception:
        return None

def validate_model_file(model_path):
    """Check if a file is a valid model."""
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

def update_env_model_path(model_path):
    """Update the model path in .env file."""
    env_file = Path(".env")
    if not env_file.exists():
        return False
    
    try:
        with open(env_file, 'r') as f:
            lines = f.readlines()
        
        # Update existing line or add new one
        updated = False
        for i, line in enumerate(lines):
            if line.strip().startswith('LLM_MODEL_PATH='):
                normalized_path = str(model_path).replace('\\', '/')
                lines[i] = f'LLM_MODEL_PATH={normalized_path}\n'
                updated = True
                break
        
        if not updated:
            normalized_path = str(model_path).replace('\\', '/')
            lines.append(f'\nLLM_MODEL_PATH={normalized_path}\n')
        
        with open(env_file, 'w') as f:
            f.writelines(lines)
        
        return True
    except Exception:
        return False

def create_models_directory():
    """Create models directory if it doesn't exist."""
    models_dir = Path("models")
    try:
        models_dir.mkdir(exist_ok=True)
        return True
    except Exception:
        return False

def check_model_directory_requirements():
    """Check all model directory requirements."""
    print("Checking model directory and LLM model files...")
    
    # Check if model is already configured and working
    if check_env_model_path():
        print("✅ Model is configured and accessible")
        return True
    
    # Check if models directory exists
    if not check_models_directory_exists():
        print("❌ Models directory not found")
        return False
    
    # Check for local models
    local_models = find_local_models()
    if local_models:
        print(f"✅ Found {len(local_models)} model file(s) in models directory")
        print("⚠️  Model not configured in settings")
        return False
    
    print("❌ No model files found and no model configured")
    return False

def setup_model_directory_interactive():
    """Interactive setup for model directory."""
    print("Setting up model directory and LLM models...")
    
    # Create models directory if needed
    if not check_models_directory_exists():
        if not create_models_directory():
            print("❌ Failed to create models directory")
            return False
    
    # Check if already configured
    if check_env_model_path():
        print("✅ Model is already configured")
        choice = input("Do you want to change the model? (y/n): ").lower().strip()
        if choice not in ['y', 'yes']:
            return True
    
    # Show options
    print("\n📋 Model Setup Options:")
    print("1. Use existing model from models/ directory")
    print("2. Use model from anywhere on your computer")
    print("3. Skip setup (download model later)")
    
    while True:
        choice = input("\nChoose option (1-3): ").strip()
        
        if choice == "1":
            return setup_local_model()
        elif choice == "2":
            return setup_custom_model()
        elif choice == "3":
            print("⏭️  Skipping model setup")
            show_download_info()
            return False
        else:
            print("Invalid choice. Please enter 1, 2, or 3.")

def setup_local_model():
    """Set up a model from the models directory."""
    local_models = find_local_models()
    
    if not local_models:
        print("\n❌ No models found in models/ directory")
        print("Place a .gguf model file in the models/ directory and try again.")
        return False
    
    print(f"\n✅ Found {len(local_models)} model file(s):")
    for i, model_file in enumerate(local_models):
        info = get_model_info(model_file)
        if info:
            print(f"   {i+1}. {info['name']} ({info['size_gb']:.1f} GB)")
        else:
            print(f"   {i+1}. {model_file.name}")
    
    while True:
        try:
            choice = input(f"\nSelect model (1-{len(local_models)}): ")
            model_index = int(choice) - 1
            
            if 0 <= model_index < len(local_models):
                selected_model = local_models[model_index]
                relative_path = selected_model.relative_to(Path.cwd())
                
                if update_env_model_path(str(relative_path)):
                    print(f"✅ Model configured: {selected_model.name}")
                    return True
                else:
                    print("❌ Failed to update configuration")
                    return False
            else:
                print("Invalid selection. Please try again.")
        except ValueError:
            print("Please enter a valid number.")

def setup_custom_model():
    """Set up a model from a custom path."""
    print("\n📁 Using model from custom location")
    print("\n💡 Example:")
    print("   C:/Users/soulo/.cache/lm-studio/models/TheBloke/Kunoichi-7B-GGUF/kunoichi-7b.Q6_K.gguf")
    
    while True:
        model_path = input("\nEnter full path to your model file: ").strip()
        
        if not model_path:
            choice = input("No path entered. Try again? (y/n): ").lower().strip()
            if choice not in ['y', 'yes']:
                return False
            continue
        
        # Clean up path (remove quotes)
        model_path = model_path.strip('"').strip("'")
        
        # Validate the model
        is_valid, message = validate_model_file(model_path)
        
        if is_valid:
            if update_env_model_path(model_path):
                print(f"✅ Model configured successfully!")
                
                info = get_model_info(model_path)
                if info:
                    print(f"   Model: {info['name']}")
                    print(f"   Size: {info['size_gb']:.1f} GB")
                
                return True
            else:
                print("❌ Failed to update configuration")
                return False
        else:
            print(f"❌ {message}")
            print(f"   Path: {model_path}")
            
            choice = input("Try different path? (y/n): ").lower().strip()
            if choice not in ['y', 'yes']:
                return False

def show_download_info():
    """Show information about downloading models."""
    print("\n📥 Model Download Information")
    print("\n📋 Recommended models:")
    print("• Llama 2 7B Chat (4GB) - Good balance")
    print("• Mistral 7B Instruct (4GB) - Fast")
    print("• Code Llama 7B (4GB) - Technical")
    print("\n📋 Where to download:")
    print("• Hugging Face: https://huggingface.co/models")
    print("• Search for 'GGUF' format models")
    print("• Look for 'Q4_K_M' or 'Q6_K' versions")
    print("\n💡 After downloading, run setup again!")

if __name__ == "__main__":
    if len(sys.argv) > 1 and sys.argv[1] == "setup":
        setup_model_directory_interactive()
    else:
        check_model_directory_requirements()