#!/usr/bin/env python3
"""
Test LLM System Script
Tests the complete LLM infrastructure:
- Model loading
- Monster generation
- Database logging
- Parsing
Run this to verify everything works before API integration
"""

import sys
import os

# Add current directory to path for imports
sys.path.append(os.getcwd())

from backend.app import create_app
from backend.config.database import db, create_tables
from backend.llm import (
    load_model, 
    get_llm_status, 
    generate_monster, 
    get_available_prompts,
    test_monster_generation
)
from backend.models.llm_log import LLMLog
from backend.models.monster import Monster

def test_database_setup():
    """Test that database tables are created properly"""
    print("🗄️  Testing database setup...")
    
    app = create_app()
    with app.app_context():
        try:
            # Create all tables including new LLMLog table
            create_tables()
            print("✅ Database tables created successfully")
            return True
        except Exception as e:
            print(f"❌ Database setup failed: {e}")
            return False

def test_model_loading():
    """Test model loading functionality"""
    print("\n🤖 Testing model loading...")
    
    # Check initial status
    status = get_llm_status()
    print(f"Initial model status: {status}")
    
    # Attempt to load model
    print("Loading model...")
    success = load_model()
    
    if success:
        print("✅ Model loaded successfully")
        
        # Check status after loading
        status = get_llm_status()
        print(f"Model loaded: {status['model_loaded']}")
        print(f"Model path: {status['model_path']}")
        return True
    else:
        print("❌ Model loading failed")
        status = get_llm_status()
        if status['error']:
            print(f"Error: {status['error']}")
        return False

def test_prompts_loading():
    """Test prompt configuration loading"""
    print("\n📄 Testing prompt loading...")
    
    try:
        prompts = get_available_prompts()
        print(f"✅ Loaded {len(prompts)} prompts:")
        for name, description in prompts.items():
            print(f"   - {name}: {description}")
        return len(prompts) > 0
    except Exception as e:
        print(f"❌ Prompt loading failed: {e}")
        return False

def test_basic_generation():
    """Test basic monster generation"""
    print("\n🎲 Testing basic monster generation...")
    
    app = create_app()
    with app.app_context():
        try:
            # Generate a basic monster
            result = generate_monster("basic_monster")
            
            if result['success']:
                print("✅ Monster generation successful!")
                print(f"   Monster: {result['monster']['name']}")
                print(f"   Description: {result['monster']['description']}")
                print(f"   Log ID: {result['log_id']}")
                
                # Verify monster was saved to database
                monster = Monster.get_monster_by_id(result['monster']['id'])
                if monster:
                    print("✅ Monster saved to database successfully")
                else:
                    print("❌ Monster not found in database")
                    return False
                
                # Verify log was saved
                log = LLMLog.query.get(result['log_id'])
                if log:
                    print("✅ LLM log saved successfully")
                    print(f"   Status: {log.status}")
                    print(f"   Parse success: {log.parse_success}")
                    print(f"   Duration: {log.duration_seconds}s")
                else:
                    print("❌ LLM log not found in database")
                    return False
                
                return True
            else:
                print(f"❌ Monster generation failed: {result['error']}")
                return False
                
        except Exception as e:
            print(f"❌ Generation test failed: {e}")
            import traceback
            traceback.print_exc()
            return False

def test_llm_monitoring():
    """Test LLM monitoring and statistics"""
    print("\n📊 Testing LLM monitoring...")
    
    app = create_app()
    with app.app_context():
        try:
            # Get recent logs
            recent_logs = LLMLog.get_recent_logs(limit=5)
            print(f"✅ Found {len(recent_logs)} recent logs")
            
            # Get statistics
            stats = LLMLog.get_stats()
            print("✅ LLM Statistics:")
            print(f"   Total generations: {stats.get('total_generations', 0)}")
            print(f"   Completed: {stats.get('completed', 0)}")
            print(f"   Failed: {stats.get('failed', 0)}")
            print(f"   Success rate: {stats.get('success_rate', 0)}%")
            print(f"   Parse success rate: {stats.get('parse_success_rate', 0)}%")
            
            return True
            
        except Exception as e:
            print(f"❌ Monitoring test failed: {e}")
            return False

def run_comprehensive_test():
    """Run all tests in sequence"""
    print("🧪 LLM System Comprehensive Test")
    print("=" * 50)
    
    test_results = []
    
    # Test 1: Database setup
    test_results.append(("Database Setup", test_database_setup()))
    
    # Test 2: Model loading
    test_results.append(("Model Loading", test_model_loading()))
    
    # Test 3: Prompts loading
    test_results.append(("Prompts Loading", test_prompts_loading()))
    
    # Test 4: Basic generation (requires database and model)
    if test_results[0][1] and test_results[1][1]:  # Only if database and model work
        test_results.append(("Monster Generation", test_basic_generation()))
        
        # Test 5: Monitoring (requires generation to have run)
        if test_results[-1][1]:  # Only if generation worked
            test_results.append(("LLM Monitoring", test_llm_monitoring()))
    
    # Print summary
    print("\n" + "=" * 50)
    print("TEST SUMMARY")
    print("=" * 50)
    
    passed = 0
    total = len(test_results)
    
    for test_name, result in test_results:
        status = "✅ PASS" if result else "❌ FAIL"
        print(f"{test_name:<20} {status}")
        if result:
            passed += 1
    
    print(f"\nPassed: {passed}/{total} tests")
    
    if passed == total:
        print("\n🎉 All tests passed! LLM system is ready!")
        print("📋 Next step: Create API endpoints for monster generation")
        return True
    else:
        print(f"\n❌ {total - passed} test(s) failed. Fix issues before proceeding.")
        return False

if __name__ == "__main__":
    success = run_comprehensive_test()
    
    if success:
        print("\n✅ LLM system test completed successfully!")
        print("Ready for API integration!")
    else:
        print("\n❌ LLM system test failed!")
        print("Check errors above and fix before proceeding.")