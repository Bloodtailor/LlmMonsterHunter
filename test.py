# Debug script to test .env loading
# Save this as debug_env.py in your git root and run it

import os
from pathlib import Path
from dotenv import load_dotenv

print("=== .env Loading Debug ===")
print()

# 1. Check current working directory
print(f"Current working directory: {os.getcwd()}")
print()

# 2. Check if .env file exists
env_file = Path(".env")
print(f".env file exists: {env_file.exists()}")
if env_file.exists():
    print(f".env file path: {env_file.absolute()}")
    print()

# 3. Check environment BEFORE loading .env
print("BEFORE load_dotenv():")
print(f"  ENABLE_IMAGE_GENERATION = {os.getenv('ENABLE_IMAGE_GENERATION', 'NOT FOUND')}")
print()

# 4. Load .env file
load_result = load_dotenv()
print(f"load_dotenv() returned: {load_result}")
print()

# 5. Check environment AFTER loading .env
print("AFTER load_dotenv():")
print(f"  ENABLE_IMAGE_GENERATION = {os.getenv('ENABLE_IMAGE_GENERATION', 'NOT FOUND')}")
print()

# 6. Test the actual logic from comfyui_config.py
raw_value = os.getenv('ENABLE_IMAGE_GENERATION', 'false')
lower_value = raw_value.lower()
final_result = lower_value == 'true'

print("Step-by-step evaluation:")
print(f"  os.getenv('ENABLE_IMAGE_GENERATION', 'false') = '{raw_value}'")
print(f"  .lower() = '{lower_value}'")
print(f"  == 'true' = {final_result}")
print()

# 7. Show the first few lines of .env file if it exists
if env_file.exists():
    print("Contents of .env file (first 10 lines):")
    try:
        with open(env_file, 'r') as f:
            lines = f.readlines()[:10]
            for i, line in enumerate(lines, 1):
                # Show raw line with escape characters visible
                print(f"  {i}: {repr(line)}")
    except Exception as e:
        print(f"  Error reading .env file: {e}")