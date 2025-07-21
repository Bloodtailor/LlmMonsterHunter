# Test Following List Management
# Simple tests to add random monsters and clear following list
print(f"🔍 Loading {__file__}")
import requests
import random

BASE_URL = "http://localhost:5000/api"

def api_call(method, endpoint, data=None):
    """Simple API call helper"""
    try:
        url = f"{BASE_URL}{endpoint}"
        
        if method == 'GET':
            response = requests.get(url, timeout=10)
        elif method == 'POST':
            response = requests.post(url, json=data, timeout=10)
        
        if response.status_code == 200:
            return response.json()
        else:
            return {"success": False, "error": f"HTTP {response.status_code}"}
    except Exception as e:
        return {"success": False, "error": str(e)}
    
test_output = api_call('GET', '/monsters/random')

print(test_output)