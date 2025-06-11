#!/usr/bin/env python3
"""
Model Setup Module
Validates LLM model path from .env file
"""

import sys
from pathlib import Path

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

def check_model_directory_requirements():
    """Check that a valid model path is configured in .env."""
    print("Checking LLM model path...")

    if check_env_model_path():
        print("✅ Model is configured and accessible")
        return True

    print("❌ No valid model path found in .env file")
    return False

def setup_model_directory_interactive():
    """Interactive setup for configuring model path."""
    print("Setting up LLM model...")

    if check_env_model_path():
        print("✅ Model is already configured")
        choice = input("Do you want to change the model? (y/n): ").lower().strip()
        if choice not in ['y', 'yes']:
            return True

    while True:
        model_path = input("\nEnter full path to your model file: ").strip()

        if not model_path:
            choice = input("No path entered. Try again? (y/n): ").lower().strip()
            if choice not in ['y', 'yes']:
                return False
            continue

        model_path = model_path.strip('"').strip("'")

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

if __name__ == "__main__":
    if len(sys.argv) > 1 and sys.argv[1] == "setup":
        setup_model_directory_interactive()
    else:
        check_model_directory_requirements()
