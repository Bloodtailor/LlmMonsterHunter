#!/usr/bin/env python3
"""
Backend Testing Script
Tests the Flask API endpoints and database connectivity
Run this after starting the backend server to verify everything works
"""

import requests
import json
import time
import sys

# Configuration
API_BASE_URL = "http://localhost:5000"
TIMEOUT = 5  # seconds

def print_header(text):
    """Print formatted header"""
    print(f"\n{'='*60}")
    print(f"{text:^60}")
    print(f"{'='*60}")

def print_test(test_name):
    """Print test name"""
    print(f"\n🧪 Testing: {test_name}")
    print("-" * 40)

def test_server_running():
    """Test if the Flask server is running and responsive"""
    print_test("Server Connectivity")
    
    try:
        response = requests.get(f"{API_BASE_URL}/api/health", timeout=TIMEOUT)
        
        if response.status_code == 200:
            print("✅ Server is running and responsive")
            return True
        else:
            print(f"❌ Server responded with status code: {response.status_code}")
            return False
            
    except requests.exceptions.ConnectionError:
        print("❌ Cannot connect to server")
        print("💡 Make sure you started the server with: python backend/run.py")
        return False
    except requests.exceptions.Timeout:
        print("❌ Server response timed out")
        return False
    except Exception as e:
        print(f"❌ Unexpected error: {e}")
        return False

def test_health_endpoint():
    """Test the /api/health endpoint"""
    print_test("Health Check Endpoint")
    
    try:
        response = requests.get(f"{API_BASE_URL}/api/health", timeout=TIMEOUT)
        
        if response.status_code == 200:
            data = response.json()
            print("✅ Health endpoint working")
            print(f"   Status: {data.get('status', 'unknown')}")
            print(f"   Message: {data.get('message', 'none')}")
            print(f"   Database: {data.get('database', 'unknown')}")
            
            # Check if database is connected
            if data.get('database') == 'connected':
                print("✅ Database connection confirmed via API")
                return True
            else:
                print("⚠️  Database not connected according to API")
                return False
        else:
            print(f"❌ Health endpoint failed with status: {response.status_code}")
            return False
            
    except Exception as e:
        print(f"❌ Health endpoint error: {e}")
        return False

def test_game_status_endpoint():
    """Test the /api/game/status endpoint"""
    print_test("Game Status Endpoint")
    
    try:
        response = requests.get(f"{API_BASE_URL}/api/game/status", timeout=TIMEOUT)
        
        if response.status_code == 200:
            data = response.json()
            print("✅ Game status endpoint working")
            print(f"   Game: {data.get('game_name', 'unknown')}")
            print(f"   Version: {data.get('version', 'unknown')}")
            print(f"   Status: {data.get('status', 'unknown')}")
            
            # Show feature status
            features = data.get('features', {})
            print("   Features:")
            for feature, enabled in features.items():
                status = "✅" if enabled else "⏳"
                print(f"     {status} {feature}")
            
            return True
        else:
            print(f"❌ Game status endpoint failed with status: {response.status_code}")
            return False
            
    except Exception as e:
        print(f"❌ Game status endpoint error: {e}")
        return False

def test_cors_headers():
    """Test that CORS headers are properly set for React frontend"""
    print_test("CORS Headers (for React frontend)")
    
    try:
        response = requests.get(f"{API_BASE_URL}/api/health", timeout=TIMEOUT)
        
        cors_header = response.headers.get('Access-Control-Allow-Origin')
        if cors_header:
            print(f"✅ CORS headers present: {cors_header}")
            return True
        else:
            print("⚠️  CORS headers not found")
            print("💡 React frontend might have trouble connecting")
            return False
            
    except Exception as e:
        print(f"❌ CORS test error: {e}")
        return False

def test_invalid_endpoint():
    """Test that invalid endpoints return proper 404 errors"""
    print_test("Invalid Endpoint Handling")
    
    try:
        response = requests.get(f"{API_BASE_URL}/api/nonexistent", timeout=TIMEOUT)
        
        if response.status_code == 404:
            print("✅ Invalid endpoints properly return 404")
            return True
        else:
            print(f"⚠️  Invalid endpoint returned status: {response.status_code}")
            return False
            
    except Exception as e:
        print(f"❌ Invalid endpoint test error: {e}")
        return False

def main():
    """Run all backend tests"""
    print_header("Monster Hunter Game - Backend API Tests")
    print("This script tests the Flask backend API to verify it's working correctly.")
    print("Make sure the backend server is running first: python backend/run.py")
    
    # Wait a moment for user to read
    time.sleep(2)
    
    # Run all tests
    tests = [
        ("Server Running", test_server_running),
        ("Health Endpoint", test_health_endpoint),
        ("Game Status Endpoint", test_game_status_endpoint),
        ("CORS Headers", test_cors_headers),
        ("404 Handling", test_invalid_endpoint)
    ]
    
    results = []
    
    for test_name, test_function in tests:
        try:
            result = test_function()
            results.append((test_name, result))
        except KeyboardInterrupt:
            print("\n\n⏹️  Tests interrupted by user")
            sys.exit(0)
        except Exception as e:
            print(f"❌ Test '{test_name}' crashed: {e}")
            results.append((test_name, False))
    
    # Summary
    print_header("Test Results Summary")
    
    passed = 0
    total = len(results)
    
    for test_name, success in results:
        status = "✅ PASS" if success else "❌ FAIL"
        print(f"{test_name:<25} {status}")
        if success:
            passed += 1
    
    print(f"\nResults: {passed}/{total} tests passed")
    
    if passed == total:
        print("\n🎉 All tests passed! Backend is working correctly.")
        print("💡 You can now start working on the React frontend.")
    elif passed >= total * 0.8:
        print(f"\n✅ Most tests passed ({passed}/{total})")
        print("💡 Backend should work but check failed tests.")
    else:
        print(f"\n❌ Several tests failed ({total-passed}/{total})")
        print("💡 Backend needs troubleshooting before proceeding.")
    
    print("\n📋 Next steps:")
    print("1. If tests failed, check the server console for error messages")
    print("2. Verify your .env file has correct database settings")
    print("3. Make sure MySQL server is running")
    print("4. If all tests pass, you're ready for React frontend development!")

if __name__ == "__main__":
    main()