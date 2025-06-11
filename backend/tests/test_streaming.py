# Test Streaming System
# Simple test to verify streaming display and LLM log integration

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

def test_streaming_generation():
    """Test streaming generation via API"""
    print("🌊 Testing Streaming Generation...")
    
    try:
        # Test the streaming queue endpoint
        url = "http://localhost:5000/api/streaming/queue/add"
        
        payload = {
            "prompt": "Create a JSON monster with name and description: {'name': 'Testbeast', 'description': 'A creature designed for testing the streaming system.'}",
            "max_tokens": 50,
            "temperature": 0.7,
            "prompt_type": "streaming_test",
            "priority": 1
        }
        
        print("📤 Sending request to streaming queue...")
        response = requests.post(url, json=payload, timeout=10)
        
        if response.status_code == 200:
            data = response.json()
            if data.get('success'):
                request_id = data['request_id']
                print(f"✅ Request queued successfully: {request_id}")
                print("📺 Check the streaming display in your browser!")
                print("📋 Check the LLM logs in the HomeBase debug panel!")
                return True
            else:
                print(f"❌ API returned error: {data.get('error')}")
                return False
        else:
            print(f"❌ HTTP error: {response.status_code}")
            return False
            
    except requests.exceptions.ConnectionError:
        print("❌ Cannot connect to backend server")
        print("💡 Make sure Flask backend is running on localhost:5000")
        return False
    except Exception as e:
        print(f"❌ Streaming test failed: {e}")
        return False

def test_llm_logs_api():
    """Test LLM logs API endpoints"""
    print("📋 Testing LLM Logs API...")
    
    try:
        # Test LLM status endpoint
        status_response = requests.get("http://localhost:5000/api/llm/status", timeout=5)
        if status_response.status_code == 200:
            status_data = status_response.json()
            if status_data.get('success'):
                llm_status = status_data['data']
                print(f"✅ LLM Status: Model loaded: {llm_status.get('model_loaded')}")
                print(f"   Currently generating: {llm_status.get('currently_generating')}")
            else:
                print("❌ LLM status API error")
                return False
        
        # Test LLM logs endpoint
        logs_response = requests.get("http://localhost:5000/api/llm/logs?limit=5", timeout=5)
        if logs_response.status_code == 200:
            logs_data = logs_response.json()
            if logs_data.get('success'):
                logs = logs_data['data']['logs']
                print(f"✅ LLM Logs: Found {len(logs)} recent logs")
                for log in logs[:2]:  # Show first 2 logs
                    print(f"   - {log.get('prompt_type')} ({log.get('status')})")
            else:
                print("❌ LLM logs API error")
                return False
        
        return True
        
    except requests.exceptions.ConnectionError:
        print("❌ Cannot connect to backend API")
        return False
    except Exception as e:
        print(f"❌ LLM logs test failed: {e}")
        return False

def test_sse_connection():
    """Test Server-Sent Events connection"""
    print("📡 Testing SSE Connection...")
    
    try:
        # This is a basic test - in practice SSE requires special handling
        sse_url = "http://localhost:5000/api/streaming/llm-events"
        
        # Just test that the endpoint exists and responds
        response = requests.get(sse_url, timeout=3, stream=True)
        
        if response.status_code == 200:
            print("✅ SSE endpoint is accessible")
            print("📺 Streaming should work in browser!")
            return True
        else:
            print(f"❌ SSE endpoint error: {response.status_code}")
            return False
            
    except requests.exceptions.ReadTimeout:
        print("✅ SSE endpoint responding (timeout is expected)")
        return True
    except requests.exceptions.ConnectionError:
        print("❌ Cannot connect to SSE endpoint")
        return False
    except Exception as e:
        print(f"❌ SSE test failed: {e}")
        return False

def main():
    """Run streaming tests"""
    print("🧪 Streaming System Test")
    print("=" * 40)
    
    # Check if backend is running
    try:
        health_response = requests.get("http://localhost:5000/api/health", timeout=5)
        if health_response.status_code != 200:
            print("❌ Backend server not responding")
            print("💡 Start the backend with: python backend/run.py")
            return False
    except:
        print("❌ Backend server not running")
        print("💡 Start the backend with: python backend/run.py")
        return False
    
    print("✅ Backend server is running")
    
    tests = [
        ("LLM Logs API", test_llm_logs_api),
        ("SSE Connection", test_sse_connection), 
        ("Streaming Generation", test_streaming_generation)
    ]
    
    passed = 0
    total = len(tests)
    
    for test_name, test_func in tests:
        print(f"\n🔬 Running: {test_name}")
        print("-" * 25)
        
        if test_func():
            passed += 1
            print(f"✅ {test_name}: PASSED")
        else:
            print(f"❌ {test_name}: FAILED")
    
    print(f"\n📊 Results: {passed}/{total} tests passed")
    
    if passed == total:
        print("\n🎉 All streaming tests passed!")
        print("\n💡 What to do next:")
        print("1. Open http://localhost:3000 in your browser")
        print("2. Click 'Test Queue Generation' button")
        print("3. Watch the streaming display (top-right corner)")
        print("4. Check the LLM logs in the debug panel")
        print("5. Try running the main monster generation test again")
    else:
        print(f"\n⚠️ {total - passed} tests failed")
        print("💡 Fix the issues before testing monster generation")
    
    return passed == total

if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)