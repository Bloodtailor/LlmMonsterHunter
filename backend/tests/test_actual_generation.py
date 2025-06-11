#!/usr/bin/env python3
"""
Test Actual Monster Generation Function
Tests our exact generate_monster() function to find where the bug is
"""

import sys
import os

# Add current directory to path for imports
sys.path.append(os.getcwd())

from backend.app import create_app
from backend.llm import generate_monster
from backend.models.llm_log import LLMLog

def test_our_actual_generation():
    """Test our actual generate_monster() function with debugging"""
    
    print("🧪 Testing Our Actual Monster Generation Function")
    print("=" * 70)
    
    app = create_app()
    with app.app_context():
        try:
            # Clear any existing generation status
            print("🔄 Starting monster generation...")
            
            # Call our actual function
            result = generate_monster("basic_monster")
            
            print("\n🔍 GENERATION RESULT:")
            print("=" * 40)
            print(f"Success: {result['success']}")
            print(f"Error: {result.get('error')}")
            print(f"Monster: {result.get('monster')}")
            print(f"Log ID: {result.get('log_id')}")
            
            if 'generation_stats' in result:
                stats = result['generation_stats']
                print(f"Generation stats: {stats}")
            
            # Get the log entry to see what was actually stored
            if result.get('log_id'):
                log_id = result['log_id']
                print(f"\n🔍 CHECKING DATABASE LOG ID: {log_id}")
                print("=" * 40)
                
                log = LLMLog.query.get(log_id)
                if log:
                    print(f"📝 Prompt text (first 100 chars): {repr(log.prompt_text[:100])}")
                    print(f"🤖 Response text: {repr(log.response_text)}")
                    print(f"📏 Response length: {len(log.response_text) if log.response_text else 'None'}")
                    print(f"📊 Response tokens: {log.response_tokens}")
                    print(f"⏱️  Duration: {log.duration_seconds}")
                    print(f"📊 Status: {log.status}")
                    print(f"❌ Error message: {repr(log.error_message)}")
                    print(f"✅ Parse success: {log.parse_success}")
                    print(f"❌ Parse error: {repr(log.parse_error)}")
                    
                    # Show raw response content for debugging
                    if log.response_text:
                        print(f"\n🔤 FULL RESPONSE TEXT:")
                        print("=" * 30)
                        print(repr(log.response_text))
                        print("=" * 30)
                    else:
                        print(f"\n❌ RESPONSE TEXT IS EMPTY/NULL")
                else:
                    print(f"❌ Could not find log entry {log_id}")
            
            return result['success']
            
        except Exception as e:
            print(f"❌ Error during generation test: {e}")
            import traceback
            traceback.print_exc()
            return False

def test_step_by_step_debugging():
    """Debug the generate_monster function step by step"""
    
    print("\n\n🔧 STEP-BY-STEP DEBUGGING")
    print("=" * 70)
    
    app = create_app()
    with app.app_context():
        try:
            # Test each component separately
            print("1. Testing prompt loading...")
            from backend.llm.monster_generation import load_prompts
            prompts = load_prompts()
            if prompts:
                print(f"   ✅ Loaded {len(prompts)} prompts")
                if 'basic_monster' in prompts:
                    print("   ✅ basic_monster prompt found")
                    prompt_config = prompts['basic_monster']
                    print(f"   📝 Max tokens: {prompt_config['max_tokens']}")
                    print(f"   🌡️  Temperature: {prompt_config['temperature']}")
                else:
                    print("   ❌ basic_monster prompt not found")
                    return False
            else:
                print("   ❌ Failed to load prompts")
                return False
            
            print("\n2. Testing model loading...")
            from backend.llm.core import ensure_model_loaded, get_llm_status
            if ensure_model_loaded():
                print("   ✅ Model loaded successfully")
                status = get_llm_status()
                print(f"   📊 Model status: {status}")
            else:
                print("   ❌ Model loading failed")
                return False
            
            print("\n3. Testing raw LLM generation...")
            from backend.llm.core import generate_text
            
            # Use the exact same parameters as generate_monster()
            generation_result = generate_text(
                prompt=prompt_config['prompt_template'],
                max_tokens=prompt_config['max_tokens'],
                temperature=prompt_config['temperature'],
                prompt_type=f'monster_generation_basic_monster',
                stop_sequences=['}', '\n\n']
            )
            
            print(f"   📊 Generation success: {generation_result['success']}")
            print(f"   📝 Generated text: {repr(generation_result.get('text', 'None'))}")
            print(f"   📏 Text length: {len(generation_result.get('text', '')) if generation_result.get('text') else 'None'}")
            print(f"   📊 Tokens: {generation_result.get('tokens', 'None')}")
            print(f"   ⏱️  Duration: {generation_result.get('duration', 'None')}")
            print(f"   ❌ Error: {generation_result.get('error', 'None')}")
            
            if generation_result['success'] and generation_result.get('text'):
                print("   ✅ Raw generation successful!")
                
                print("\n4. Testing parsing...")
                from backend.llm.parser import parse_response
                
                parse_result = parse_response(
                    response_text=generation_result['text'],
                    parser_config=prompt_config['parser']
                )
                
                print(f"   📊 Parse success: {parse_result.success}")
                print(f"   📝 Parsed data: {parse_result.data}")
                print(f"   ❌ Parse error: {parse_result.error}")
                print(f"   🔧 Parser used: {parse_result.parser_used}")
                
                return True
            else:
                print("   ❌ Raw generation failed")
                return False
            
        except Exception as e:
            print(f"❌ Error during step-by-step test: {e}")
            import traceback
            traceback.print_exc()
            return False

def main():
    """Main test function"""
    
    print("🚀 Testing Monster Generation Bug")
    print("=" * 70)
    
    # Test 1: Our actual function
    print("TEST 1: Our actual generate_monster() function")
    success1 = test_our_actual_generation()
    
    # Test 2: Step by step debugging
    print("\n" + "=" * 70)
    print("TEST 2: Step-by-step component testing")
    success2 = test_step_by_step_debugging()
    
    print("\n" + "=" * 70)
    print("SUMMARY")
    print("=" * 70)
    print(f"Actual function test: {'✅ PASS' if success1 else '❌ FAIL'}")
    print(f"Step-by-step test: {'✅ PASS' if success2 else '❌ FAIL'}")
    
    if not success1 and success2:
        print("\n🎯 CONCLUSION: Bug is in the generate_monster() function integration")
        print("   Raw components work, but the full function fails")
    elif success1:
        print("\n🎉 CONCLUSION: Bug might be fixed or was intermittent")
    else:
        print("\n❌ CONCLUSION: Deeper issue in the LLM system")

if __name__ == "__main__":
    main()