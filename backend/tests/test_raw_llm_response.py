#!/usr/bin/env python3
"""
Test Raw LLM Response Structure
Tests what llama-cpp-python actually returns so we can fix our extraction
"""

import sys
import os
import json
from pathlib import Path

# Add current directory to path for imports
sys.path.append(os.getcwd())

def test_raw_llm_response():
    """Test raw llama-cpp-python response structure"""
    
    print("🧪 Testing Raw LLM Response Structure")
    print("=" * 60)
    
    try:
        # Load environment variables
        from dotenv import load_dotenv
        load_dotenv()
        
        # Get model path
        model_path = os.getenv('LLM_MODEL_PATH')
        if not model_path:
            print("❌ LLM_MODEL_PATH not set in .env file")
            return False
        
        model_file = Path(model_path)
        if not model_file.exists():
            print(f"❌ Model file not found: {model_path}")
            return False
        
        print(f"📂 Loading model from: {model_path}")
        
        # Import and load llama-cpp-python
        try:
            from llama_cpp import Llama
        except ImportError:
            print("❌ llama-cpp-python not installed")
            return False
        
        # Load model
        print("🔄 Loading model... (this may take 30-60 seconds)")
        llm = Llama(
            model_path=str(model_file),
            n_ctx=int(os.getenv('LLM_CONTEXT_SIZE', '4096')),
            n_gpu_layers=int(os.getenv('LLM_GPU_LAYERS', '35')),
            verbose=False
        )
        print("✅ Model loaded successfully")
        
        # Test simple generation
        print("\n🎲 Testing simple generation...")
        simple_prompt = "Hello"
        
        print(f"📝 Prompt: '{simple_prompt}'")
        print("🔄 Generating...")
        
        response = llm(
            simple_prompt,
            max_tokens=10,
            temperature=0.8,
            stop=["</s>", "\n\n\n"],
            echo=False
        )
        
        print("\n🔍 RAW RESPONSE STRUCTURE:")
        print("=" * 40)
        
        # Show response type and structure
        print(f"Response type: {type(response)}")
        print(f"Response: {response}")
        
        # Try to analyze structure
        if isinstance(response, dict):
            print(f"\n📋 Response keys: {list(response.keys())}")
            
            # Check for 'choices' key
            if 'choices' in response:
                print(f"✅ Found 'choices' key")
                choices = response['choices']
                print(f"   choices type: {type(choices)}")
                print(f"   choices length: {len(choices) if isinstance(choices, list) else 'not a list'}")
                
                if isinstance(choices, list) and len(choices) > 0:
                    first_choice = choices[0]
                    print(f"   first choice type: {type(first_choice)}")
                    print(f"   first choice: {first_choice}")
                    
                    if isinstance(first_choice, dict):
                        print(f"   first choice keys: {list(first_choice.keys())}")
                        
                        if 'text' in first_choice:
                            text_value = first_choice['text']
                            print(f"   ✅ Found 'text' key: {repr(text_value)}")
                            print(f"   text type: {type(text_value)}")
                            print(f"   text length: {len(text_value) if text_value else 'None/Empty'}")
                        else:
                            print(f"   ❌ No 'text' key in first choice")
                else:
                    print(f"   ❌ choices is not a non-empty list")
            else:
                print(f"❌ No 'choices' key in response")
            
            # Check for 'usage' key
            if 'usage' in response:
                print(f"✅ Found 'usage' key")
                usage = response['usage']
                print(f"   usage: {usage}")
                
                if isinstance(usage, dict) and 'completion_tokens' in usage:
                    tokens = usage['completion_tokens']
                    print(f"   ✅ completion_tokens: {tokens}")
                else:
                    print(f"   ❌ No 'completion_tokens' in usage")
            else:
                print(f"❌ No 'usage' key in response")
        
        else:
            print(f"❌ Response is not a dictionary: {type(response)}")
        
        print("\n" + "=" * 60)
        return True
        
    except Exception as e:
        print(f"❌ Error during test: {e}")
        import traceback
        traceback.print_exc()
        return False

def test_monster_prompt():
    """Test with the actual monster generation prompt"""
    
    print("\n🐉 Testing Monster Generation Prompt")
    print("=" * 60)
    
    try:
        # Load environment and model (same as above)
        from dotenv import load_dotenv
        load_dotenv()
        
        model_path = os.getenv('LLM_MODEL_PATH')
        model_file = Path(model_path)
        
        from llama_cpp import Llama
        
        llm = Llama(
            model_path=str(model_file),
            n_ctx=int(os.getenv('LLM_CONTEXT_SIZE', '4096')),
            n_gpu_layers=int(os.getenv('LLM_GPU_LAYERS', '35')),
            verbose=False
        )
        
        # Use the actual monster prompt
        monster_prompt = '''You are a creative monster designer for a fantasy game. Create a unique monster with the following format:

{"name": "Monster Name", "description": "A detailed description of the monster's appearance, personality, and background"}

Make the monster interesting and unique. The description should be 2-3 sentences long.

Generate only valid JSON, no additional text:'''
        
        print(f"📝 Using monster prompt...")
        print("🔄 Generating...")
        
        response = llm(
            monster_prompt,
            max_tokens=150,
            temperature=0.8,
            stop=["}"],  # Stop after JSON closes
            echo=False
        )
        
        print("\n🔍 MONSTER GENERATION RESPONSE:")
        print("=" * 40)
        
        # Extract text the same way our code does
        try:
            generated_text = response['choices'][0]['text']
            tokens_generated = response['usage']['completion_tokens']
            
            print(f"✅ Extraction successful!")
            print(f"📝 Generated text: {repr(generated_text)}")
            print(f"📊 Tokens: {tokens_generated}")
            print(f"📏 Text length: {len(generated_text) if generated_text else 'None/Empty'}")
            
            if generated_text:
                print(f"🔤 First 200 chars: {repr(generated_text[:200])}")
            
        except Exception as e:
            print(f"❌ Extraction failed: {e}")
            print(f"📋 Full response: {response}")
        
        return True
        
    except Exception as e:
        print(f"❌ Error during monster test: {e}")
        import traceback
        traceback.print_exc()
        return False

def main():
    """Main test function"""
    
    # Test 1: Simple response structure
    if not test_raw_llm_response():
        print("❌ Basic test failed")
        return
    
    # Test 2: Monster generation
    if not test_monster_prompt():
        print("❌ Monster test failed")
        return
    
    print("\n🎉 All tests completed!")
    print("Check the output above to see what llama-cpp-python actually returns.")

if __name__ == "__main__":
    main()