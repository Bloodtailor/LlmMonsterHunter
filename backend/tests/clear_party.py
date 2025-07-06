# Simple Test: Clear Party
# Clears all monsters from following list and active party

import requests

BASE_URL = "http://localhost:5000/api"

def main():
    print("🧹 Clearing party and following monsters...")
    
    try:
        # Reset entire game state
        response = requests.post(f"{BASE_URL}/game-state/reset", timeout=10)
        
        if response.status_code == 200:
            result = response.json()
            
            if result.get('success'):
                print("✅ Party cleared successfully!")
                print("   Following monsters: 0")
                print("   Active party: 0")
                print("   Dungeon state: Reset")
            else:
                print(f"❌ Failed: {result.get('error', 'Unknown error')}")
        else:
            print(f"❌ HTTP Error: {response.status_code}")
            
    except Exception as e:
        print(f"❌ Error: {e}")

main()