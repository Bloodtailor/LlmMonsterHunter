# Test Monster Generation Script
# Tests the complete monster generation pipeline:
# LLM model loading -> Queue system -> Monster creation -> Database storage

import sys
import os
import time
from pathlib import Path

# Add the project root to Python path so we can import backend modules
project_root = Path(__file__).parent
sys.path.insert(0, str(project_root))

# Load environment variables
from dotenv import load_dotenv
load_dotenv()

def test_environment_setup():
    """Test that all required environment variables are set"""
    print("🔧 Testing Environment Setup...")
    
    required_vars = [
        'LLM_MODEL_PATH',
        'DB_USER', 
        'DB_PASSWORD',
        'DB_HOST',
        'DB_NAME'
    ]
    
    missing_vars = []
    for var in required_vars:
        if not os.getenv(var):
            missing_vars.append(var)
    
    if missing_vars:
        print(f"❌ Missing environment variables: {missing_vars}")
        print("💡 Make sure your .env file is properly configured")
        return False
    
    # Check if model file exists
    model_path = os.getenv('LLM_MODEL_PATH')
    if not os.path.exists(model_path):
        print(f"❌ Model file not found: {model_path}")
        print("💡 Download a compatible GGUF model and update LLM_MODEL_PATH")
        return False
    
    print("✅ Environment setup looks good!")
    return True

def test_database_connection():
    """Test database connectivity and table creation"""
    print("🗄️  Testing Database Connection...")
    
    try:
        from backend.app import create_app
        
        # Create Flask app to test database
        app = create_app()
        
        with app.app_context():
            from backend.config.database import test_connection, create_tables
            
            # Test connection
            if not test_connection():
                print("❌ Database connection failed")
                return False
            
            # Create tables if needed
            if not create_tables():
                print("❌ Failed to create database tables")
                return False
            
            print("✅ Database connection and tables ready!")
            return True
            
    except Exception as e:
        print(f"❌ Database test failed: {e}")
        return False

def test_llm_model_loading():
    """Test LLM model loading"""
    print("🤖 Testing LLM Model Loading...")
    
    try:
        from backend.llm.core import load_model, get_llm_status
        
        # Load the model
        if not load_model():
            print("❌ Failed to load LLM model")
            return False
        
        # Check status
        status = get_llm_status()
        if not status['model_loaded']:
            print("❌ Model loaded but status shows not loaded")
            return False
        
        print("✅ LLM model loaded successfully!")
        print(f"   Model: {status['model_path'].split('/')[-1] if status['model_path'] else 'Unknown'}")
        print(f"   Load time: {status['load_time']}")
        
        return True
        
    except Exception as e:
        print(f"❌ LLM model loading failed: {e}")
        return False

def test_queue_system():
    """Test the LLM queue system"""
    print("📥 Testing Queue System...")
    
    try:
        from backend.llm.queue import get_llm_queue
        
        # Get queue instance (this starts the worker automatically)
        queue = get_llm_queue()
        
        # Check queue status
        status = queue.get_queue_status()
        if not status['worker_running']:
            print("❌ Queue worker not running")
            return False
        
        print("✅ Queue system running!")
        print(f"   Worker: {'Running' if status['worker_running'] else 'Stopped'}")
        print(f"   Queue size: {status['queue_size']}")
        print(f"   Total items: {status['total_items']}")
        
        return True
        
    except Exception as e:
        print(f"❌ Queue system test failed: {e}")
        return False

def test_monster_generation():
    """Test actual monster generation end-to-end"""
    print("🐉 Testing Monster Generation...")
    
    try:
        from backend.llm.monster_generation import generate_monster
        from backend.models.monster import Monster
        from backend.app import create_app
        
        print("🎲 Starting monster generation (this may take 15-30 seconds)...")
        print("   Using 'basic_monster' prompt for faster testing")
        
        # Create Flask app context for database operations
        app = create_app()
        
        with app.app_context():
            # Record start time
            start_time = time.time()
            
            # Generate a basic monster using the queue system
            result = generate_monster(prompt_name="basic_monster", use_queue=True)
            
            # Calculate duration
            duration = time.time() - start_time
            
            if not result['success']:
                print(f"❌ Monster generation failed: {result['error']}")
                if 'raw_response' in result:
                    print(f"   Raw response: {result['raw_response'][:200]}...")
                return False
            
            # Display results
            monster_data = result['monster']
            print("✅ Monster generation successful!")
            print(f"   Duration: {duration:.1f} seconds")
            print(f"   Monster ID: {monster_data['id']}")
            print(f"   Name: {monster_data['name']}")
            print(f"   Species: {monster_data['species']}")
            print(f"   Description: {monster_data['description']}")
            
            # Show stats
            stats = monster_data['stats']
            print(f"   Stats: HP={stats['max_health']}, ATK={stats['attack']}, DEF={stats['defense']}, SPD={stats['speed']}")
            
            # Show abilities
            abilities = monster_data['abilities']
            if abilities:
                print(f"   Abilities: {len(abilities)} abilities")
                for ability in abilities[:2]:  # Show first 2 abilities
                    print(f"     - {ability.get('name', 'Unknown')}: {ability.get('description', 'No description')}")
            
            # Show generation stats if available
            if 'generation_stats' in result:
                gen_stats = result['generation_stats']
                print(f"   Generation: {gen_stats['tokens']} tokens in {gen_stats['duration']:.1f}s ({gen_stats['tokens_per_second']} tok/s)")
            
            # Verify database storage
            print("🗄️  Verifying database storage...")
            saved_monster = Monster.get_monster_by_id(monster_data['id'])
            if not saved_monster:
                print("❌ Monster not found in database after generation")
                return False
            
            print("✅ Monster successfully saved to database!")
            return True
        
    except Exception as e:
        print(f"❌ Monster generation test failed: {e}")
        import traceback
        traceback.print_exc()
        return False

def test_multiple_monsters():
    """Test generating multiple monsters to stress test the system"""
    print("🎭 Testing Multiple Monster Generation...")
    
    try:
        from backend.llm.monster_generation import generate_monster
        from backend.app import create_app
        
        # Create Flask app context for database operations
        app = create_app()
        
        with app.app_context():
            monster_count = 3
            successful_generations = 0
            
            print(f"🎲 Generating {monster_count} monsters...")
            
            for i in range(monster_count):
                print(f"\n   🐉 Generating monster {i+1}/{monster_count}...")
                
                result = generate_monster(prompt_name="basic_monster", use_queue=True)
                
                if result['success']:
                    monster = result['monster']
                    print(f"   ✅ Created: {monster['name']} ({monster['species']})")
                    successful_generations += 1
                else:
                    print(f"   ❌ Failed: {result['error']}")
            
            print(f"\n📊 Multiple generation results: {successful_generations}/{monster_count} successful")
            
            if successful_generations >= monster_count // 2:  # At least half successful
                print("✅ Multiple monster generation test passed!")
                return True
            else:
                print("❌ Too many failures in multiple generation test")
                return False
        
    except Exception as e:
        print(f"❌ Multiple monster generation test failed: {e}")
        return False

def main():
    """Run all tests in sequence"""
    print("🧪 Monster Generation Test Suite")
    print("=" * 50)
    
    tests = [
        ("Environment Setup", test_environment_setup),
        ("Database Connection", test_database_connection),
        ("LLM Model Loading", test_llm_model_loading),
        ("Queue System", test_queue_system),
        ("Monster Generation", test_monster_generation),
        ("Multiple Monsters", test_multiple_monsters)
    ]
    
    passed_tests = 0
    total_tests = len(tests)
    
    for test_name, test_function in tests:
        print(f"\n🔬 Running: {test_name}")
        print("-" * 30)
        
        try:
            if test_function():
                passed_tests += 1
                print(f"✅ {test_name}: PASSED")
            else:
                print(f"❌ {test_name}: FAILED")
                # Continue with other tests even if one fails
        except Exception as e:
            print(f"❌ {test_name}: ERROR - {e}")
    
    # Final results
    print("\n" + "=" * 50)
    print("🏁 Test Suite Complete")
    print(f"📊 Results: {passed_tests}/{total_tests} tests passed")
    
    if passed_tests == total_tests:
        print("🎉 All tests passed! Monster generation system is working!")
        print("💡 Next steps:")
        print("   - Create monster generation API endpoints")
        print("   - Add React UI for monster generation")
        print("   - Implement monster display components")
    else:
        print(f"⚠️  {total_tests - passed_tests} tests failed. Check the output above for details.")
        print("💡 Fix the failing tests before proceeding to API development.")
    
    return passed_tests == total_tests

if __name__ == "__main__":
    # Ensure we're in the right directory
    if not os.path.exists("backend"):
        print("❌ Please run this script from the project root directory (LlmMonsterHunter/)")
        print("💡 Current directory should contain 'backend/' and 'frontend/' folders")
        sys.exit(1)
    
    success = main()
    sys.exit(0 if success else 1)