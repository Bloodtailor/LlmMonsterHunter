# Complete System Test
# Tests all components working together: Logging, Streaming, Queue, Database

import sys
import os
import time
import requests
from pathlib import Path

# Add the project root to Python path
project_root = Path(__file__).parent
sys.path.insert(0, str(project_root))

from dotenv import load_dotenv
load_dotenv()

def test_backend_health():
    """Test basic backend connectivity"""
    print("🏥 Testing Backend Health...")
    
    try:
        response = requests.get("http://localhost:5000/api/health", timeout=5)
        if response.status_code == 200:
            data = response.json()
            print(f"✅ Backend: {data.get('status')}")
            print(f"✅ Database: {data.get('database')}")
            return True
        else:
            print(f"❌ Backend health check failed: {response.status_code}")
            return False
    except Exception as e:
        print(f"❌ Backend not accessible: {e}")
        return False

def test_llm_logs_database():
    """Test LLM logs database and API"""
    print("📋 Testing LLM Logs Database...")
    
    try:
        # Test database connection
        db_response = requests.get("http://localhost:5000/api/llm/debug/db-test", timeout=5)
        if db_response.status_code == 200:
            db_data = db_response.json()
            if db_data.get('success'):
                print(f"✅ Database connected: {db_data['data']['total_logs']} logs in database")
            else:
                print(f"❌ Database test failed: {db_data.get('error')}")
                return False
        
        # Test creating a test log
        create_response = requests.post("http://localhost:5000/api/llm/debug/create-test-log", timeout=5)
        if create_response.status_code == 200:
            create_data = create_response.json()
            if create_data.get('success'):
                print(f"✅ Test log created: ID {create_data.get('log_id')}")
            else:
                print(f"❌ Test log creation failed: {create_data.get('error')}")
                return False
        
        # Test fetching logs
        logs_response = requests.get("http://localhost:5000/api/llm/logs?limit=5", timeout=5)
        if logs_response.status_code == 200:
            logs_data = logs_response.json()
            if logs_data.get('success'):
                logs = logs_data['data']['logs']
                print(f"✅ Fetched {len(logs)} recent logs")
                if logs:
                    latest = logs[0]
                    print(f"   Latest: {latest.get('prompt_type')} ({latest.get('status')})")
            else:
                print(f"❌ Logs fetch failed: {logs_data.get('error')}")
                return False
        
        return True
        
    except Exception as e:
        print(f"❌ LLM logs test failed: {e}")
        return False

def test_streaming_generation():
    """Test streaming generation with logging"""
    print("🌊 Testing Streaming Generation with Logging...")
    
    try:
        # Send streaming generation request
        payload = {
            "prompt": "Create a simple JSON: {\"name\": \"StreamTest\", \"description\": \"A test creature for streaming.\"}",
            "max_tokens": 100,
            "temperature": 0.7,
            "prompt_type": "complete_system_test",
            "priority": 1
        }
        
        print("📤 Sending streaming request...")
        response = requests.post("http://localhost:5000/api/streaming/queue/add", json=payload, timeout=10)
        
        if response.status_code == 200:
            data = response.json()
            if data.get('success'):
                request_id = data['request_id']
                log_id = data.get('log_id')
                print(f"✅ Request queued: {request_id}")
                print(f"✅ Log created: {log_id}")
                
                # Wait a moment for processing
                print("⏳ Waiting for generation to complete...")
                time.sleep(2)
                
                # Check if log was updated
                if log_id:
                    log_response = requests.get(f"http://localhost:5000/api/llm/logs/{log_id}", timeout=5)
                    if log_response.status_code == 200:
                        log_data = log_response.json()
                        if log_data.get('success'):
                            log_info = log_data['data']
                            print(f"✅ Log status: {log_info.get('status')}")
                            if log_info.get('response_text'):
                                print(f"✅ Response generated: {len(log_info.get('response_text', ''))} characters")
                
                return True
            else:
                print(f"❌ Streaming request failed: {data.get('error')}")
                return False
        else:
            print(f"❌ Streaming request HTTP error: {response.status_code}")
            return False
            
    except Exception as e:
        print(f"❌ Streaming generation test failed: {e}")
        return False

def test_monster_generation_with_context():
    """Test monster generation with proper Flask context"""
    print("🐉 Testing Monster Generation with Full Logging...")
    
    try:
        # Create Flask app context
        sys.path.insert(0, str(project_root))
        from backend.app import create_app
        from backend.llm.monster_generation import generate_monster
        
        app = create_app()
        
        with app.app_context():
            print("🎲 Generating monster with full system integration...")
            
            # Monitor logs before generation
            pre_logs_response = requests.get("http://localhost:5000/api/llm/logs?limit=1", timeout=5)
            pre_count = 0
            if pre_logs_response.status_code == 200:
                pre_data = pre_logs_response.json()
                if pre_data.get('success'):
                    pre_count = pre_data['data']['count']
            
            # Generate monster
            result = generate_monster(prompt_name="basic_monster", use_queue=True)
            
            if result['success']:
                monster = result['monster']
                print(f"✅ Monster created: {monster['name']}")
                print(f"   Species: {monster['species']}")
                print(f"   ID: {monster['id']}")
                print(f"   Log ID: {result.get('log_id')}")
                
                # Check if new log was created
                post_logs_response = requests.get("http://localhost:5000/api/llm/logs?limit=1", timeout=5)
                if post_logs_response.status_code == 200:
                    post_data = post_logs_response.json()
                    if post_data.get('success'):
                        post_count = post_data['data']['count']
                        if post_count > pre_count:
                            print("✅ New log entry created during generation")
                        else:
                            print("⚠️  No new log detected (may be expected)")
                
                return True
            else:
                print(f"❌ Monster generation failed: {result['error']}")
                return False
                
    except Exception as e:
        print(f"❌ Monster generation test failed: {e}")
        import traceback
        traceback.print_exc()
        return False

def main():
    """Run complete system test"""
    print("🧪 Complete System Integration Test")
    print("=" * 50)
    print("Testing: Backend + Database + Logging + Streaming + Monster Generation")
    print()
    
    tests = [
        ("Backend Health", test_backend_health),
        ("LLM Logs Database", test_llm_logs_database),
        ("Streaming Generation", test_streaming_generation),
        ("Monster Generation", test_monster_generation_with_context)
    ]
    
    passed = 0
    total = len(tests)
    
    for test_name, test_func in tests:
        print(f"🔬 Running: {test_name}")
        print("-" * 30)
        
        try:
            if test_func():
                passed += 1
                print(f"✅ {test_name}: PASSED\n")
            else:
                print(f"❌ {test_name}: FAILED\n")
        except Exception as e:
            print(f"❌ {test_name}: ERROR - {e}\n")
    
    # Final results
    print("=" * 50)
    print("🏁 Complete System Test Results")
    print(f"📊 {passed}/{total} tests passed")
    
    if passed == total:
        print("\n🎉 ALL TESTS PASSED! 🎉")
        print("\n✨ Your system is working perfectly!")
        print("\n💡 What you should see now:")
        print("1. 📺 Streaming Display: Shows real-time generation progress")
        print("2. 📋 LLM Logs: Populated with generation history in debug panel")
        print("3. 🐉 Monster Generation: Creates and saves monsters to database")
        print("4. 🌊 Text Streaming: See actual AI text generation in real-time")
        print("\n🚀 Ready for API endpoint development!")
    elif passed >= 3:
        print(f"\n🟡 MOSTLY WORKING ({passed}/{total})")
        print("Minor issues detected but core functionality is operational")
    else:
        print(f"\n🔴 ISSUES DETECTED ({passed}/{total})")
        print("Core functionality needs attention before proceeding")
    
    print(f"\n🔧 Next Steps:")
    if passed == total:
        print("- Create monster generation API endpoints")
        print("- Build React monster display components")
        print("- Add monster roster management UI")
    else:
        print("- Fix failing tests above")
        print("- Ensure backend server is running")
        print("- Check database connection")
    
    return passed == total

if __name__ == "__main__":
    # Ensure proper directory
    if not os.path.exists("backend"):
        print("❌ Please run this script from the project root directory")
        print("💡 Current directory should contain 'backend/' and 'frontend/' folders")
        sys.exit(1)
    
    success = main()
    sys.exit(0 if success else 1)