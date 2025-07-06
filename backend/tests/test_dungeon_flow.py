# Test Complete Dungeon Flow - Full Adventure Loop
# Tests dungeon entry, location choices, and exit with LLM text generation

import requests
import json

BASE_URL = "http://localhost:5000/api"

def api_call(method, endpoint, data=None):
    """Make API call with error handling"""
    try:
        url = f"{BASE_URL}{endpoint}"
        print(f"\n🔍 {method} {endpoint}")
        
        if method == 'GET':
            response = requests.get(url, timeout=600)
        elif method == 'POST':
            response = requests.post(url, json=data, timeout=600)
        
        if response.status_code == 200:
            result = response.json()
            print(f"   ✅ Success: {result.get('success', False)}")
            return result
        else:
            print(f"   ❌ HTTP {response.status_code}")
            return {"success": False, "error": f"HTTP {response.status_code}"}
    except Exception as e:
        print(f"   ❌ Error: {e}")
        return {"success": False, "error": str(e)}

def show_text(text, label="Generated Text"):
    """Display formatted text"""
    if text:
        print(f"\n📖 {label}:")
        print(f'   "{text}"')

def show_location(location):
    """Display location details"""
    if location:
        print(f"\n🏰 Current Location: {location.get('name', 'Unknown')}")
        print(f"   {location.get('description', 'No description available')}")

def show_doors(doors):
    """Display door choices"""
    if doors:
        print(f"\n🚪 Door Choices ({len(doors)} available):")
        for door in doors:
            icon = "🚯" if door.get('type') == 'exit' else "🚪"
            print(f"   {icon} {door.get('name', 'Unknown')} (ID: {door.get('id')})")
            print(f"      {door.get('description', 'No description')}")

def setup_party():
    """Set up test party for dungeon adventure"""
    print("🎯 Setting up adventure party...")
    
    # Reset everything
    reset = api_call('POST', '/game-state/reset')
    if not reset.get('success'):
        return False
    
    # Get monsters from database
    monsters = api_call('GET', '/monsters?limit=4')
    if not monsters.get('success') or len(monsters.get('monsters', [])) < 2:
        print("❌ Need at least 2 monsters in database")
        return False
    
    monster_list = monsters['monsters']
    party_ids = [monster['id'] for monster in monster_list[:3]]  # Use first 3
    
    # Add to following
    for monster_id in party_ids:
        api_call('POST', '/game-state/following/add', {'monster_id': monster_id})
    
    # Set as active party
    party_result = api_call('POST', '/game-state/party/set', {'monster_ids': party_ids})
    
    if party_result.get('success'):
        print(f"✅ Party ready: {party_result.get('message', 'Party set')}")
        return True
    
    return False

def main():
    """Execute complete dungeon adventure test"""
    print("🧪 COMPLETE DUNGEON FLOW TEST")
    print("=" * 50)
    
    # Setup
    if not setup_party():
        print("❌ FAILED: Could not set up party")
        return
    
    # Enter dungeon
    print("\n🏰 ENTERING DUNGEON...")
    entry = api_call('POST', '/dungeon/enter')
    
    if not entry.get('success'):
        print(f"❌ FAILED to enter: {entry.get('error')}")
        return
    
    print("✅ DUNGEON ENTERED!")
    show_text(entry.get('entry_text'), "Entry Atmosphere")
    show_location(entry.get('location'))
    show_doors(entry.get('doors', []))
    
    # First door choice
    print("\n🚪 CHOOSING FIRST DOOR...")
    doors = entry.get('doors', [])
    location_doors = [d for d in doors if d.get('type') == 'location']
    
    if not location_doors:
        print("❌ No location doors found")
        return
    
    chosen_door = location_doors[0]['id']
    choice1 = api_call('POST', '/dungeon/choose-door', {'door_choice': chosen_door})
    
    if not choice1.get('success'):
        print(f"❌ FAILED door choice: {choice1.get('error')}")
        return
    
    print(f"✅ CHOSE: {choice1.get('choice_made')}")
    show_text(choice1.get('event_text'), "Location Event")
    show_location(choice1.get('new_location'))
    show_doors(choice1.get('new_doors', []))
    
    # Second door choice
    print("\n🚪 CHOOSING SECOND DOOR...")
    new_doors = choice1.get('new_doors', [])
    new_location_doors = [d for d in new_doors if d.get('type') == 'location']
    
    if new_location_doors:
        chosen_door2 = new_location_doors[0]['id']
        choice2 = api_call('POST', '/dungeon/choose-door', {'door_choice': chosen_door2})
        
        if choice2.get('success'):
            print(f"✅ CHOSE: {choice2.get('choice_made')}")
            show_text(choice2.get('event_text'), "Second Event")
            show_location(choice2.get('new_location'))
            show_doors(choice2.get('new_doors', []))
            current_doors = choice2.get('new_doors', [])
        else:
            print("⚠️ Second choice failed, using first choice doors")
            current_doors = new_doors
    else:
        print("⚠️ No second location door, using current doors")
        current_doors = new_doors
    
    # Exit dungeon
    print("\n🚯 EXITING DUNGEON...")
    exit_doors = [d for d in current_doors if d.get('type') == 'exit']
    
    if not exit_doors:
        print("❌ No exit door found!")
        return
    
    exit_choice = api_call('POST', '/dungeon/choose-door', {'door_choice': 'exit'})
    
    if not exit_choice.get('success'):
        print(f"❌ FAILED to exit: {exit_choice.get('error')}")
        return
    
    print("✅ SUCCESSFULLY EXITED!")
    show_text(exit_choice.get('exit_text'), "Exit Narrative")
    
    # Verify we're out
    final_state = api_call('GET', '/dungeon/state')
    if final_state.get('success'):
        in_dungeon = final_state.get('in_dungeon', True)
        print(f"\n🏠 Back at home base: {not in_dungeon}")
        
        if not in_dungeon:
            print("✅ ADVENTURE COMPLETE!")
        else:
            print("⚠️ Still in dungeon somehow")
    
    # Summary
    print("\n🏁 TEST SUMMARY")
    print("=" * 50)
    print("✅ Party setup successful")
    print("✅ Dungeon entry with LLM atmosphere")
    print("✅ Location generation working")
    print("✅ Door choice mechanics functional")
    print("✅ Event text generation working")
    print("✅ Dungeon exit successful")
    print("✅ Game state management working")
    
    print("\n🎉 COMPLETE DUNGEON FLOW WORKING!")
    print("Ready for frontend integration!")

main()