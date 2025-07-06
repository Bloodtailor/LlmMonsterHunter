# Simple Test: Quick Dungeon Run
# Sets up party and does a simple dungeon enter/exit

import requests

BASE_URL = "http://localhost:5000/api"

def main():
    print("⚡ Quick Dungeon Test...")
    
    try:
        
        # Enter dungeon
        print("\n🏰 Entering dungeon...")
        enter_response = requests.post(f"{BASE_URL}/dungeon/enter", timeout=20)
        
        if enter_response.status_code != 200:
            print(f"❌ Failed to enter dungeon: HTTP {enter_response.status_code}")
            return
        
        enter_result = enter_response.json()
        if not enter_result.get('success'):
            print(f"❌ Enter failed: {enter_result.get('error')}")
            return
        
        print("✅ Entered dungeon successfully!")
        print(f"   Location: {enter_result.get('location', {}).get('name', 'Unknown')}")
        
        doors = enter_result.get('doors', [])
        exit_door = next((d for d in doors if d.get('type') == 'exit'), None)
        
        if not exit_door:
            print("❌ No exit door found!")
            return
        
        # Exit immediately
        print("\n🚯 Exiting dungeon...")
        exit_response = requests.post(f"{BASE_URL}/dungeon/choose-door", 
                                    json={'door_choice': 'exit'}, timeout=20)
        
        if exit_response.status_code != 200:
            print(f"❌ Failed to exit: HTTP {exit_response.status_code}")
            return
        
        exit_result = exit_response.json()
        if not exit_result.get('success'):
            print(f"❌ Exit failed: {exit_result.get('error')}")
            return
        
        print("✅ Exited dungeon successfully!")
        print("🏠 Back at home base")
        
    except Exception as e:
        print(f"❌ Error: {e}")

main()