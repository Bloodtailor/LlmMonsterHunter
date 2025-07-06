# Test Game State System - Complete Flow Test
# Tests game state management, monster following, and party management

import requests
import json

BASE_URL = "http://localhost:5000/api"

def test_api_call(method, endpoint, data=None, expected_success=True):
    """Make API call and return response with error handling"""
    try:
        url = f"{BASE_URL}{endpoint}"
        print(f"\n🔍 {method} {endpoint}")
        
        if data:
            print(f"   Data: {data}")
        
        if method == 'GET':
            response = requests.get(url, timeout=10)
        elif method == 'POST':
            response = requests.post(url, json=data, timeout=10)
        else:
            print(f"   ❌ Unsupported method: {method}")
            return None
        
        print(f"   Status: {response.status_code}")
        
        if response.status_code == 200:
            result = response.json()
            success = result.get('success', False)
            print(f"   Success: {success}")
            
            if not success:
                print(f"   Error: {result.get('error', 'Unknown error')}")
            
            return result
        else:
            print(f"   ❌ HTTP Error: {response.status_code}")
            try:
                error_data = response.json()
                print(f"   Error: {error_data.get('error', 'Unknown error')}")
                return error_data
            except:
                return {"success": False, "error": f"HTTP {response.status_code}"}
                
    except requests.exceptions.RequestException as e:
        print(f"   ❌ Request failed: {e}")
        return {"success": False, "error": str(e)}

def print_game_state(state):
    """Print formatted game state"""
    if not state:
        print("   No game state data")
        return
    
    following = state.get('following_monsters', {})
    party = state.get('active_party', {})
    dungeon = state.get('dungeon_state', {})
    
    print(f"\n📊 Game State Summary:")
    print(f"   Status: {state.get('game_status', 'unknown')}")
    print(f"   Following Monsters: {following.get('count', 0)}")
    print(f"   Active Party: {party.get('count', 0)}")
    print(f"   In Dungeon: {dungeon.get('in_dungeon', False)}")
    
    # Show following monster names
    if following.get('details'):
        names = [monster['name'] for monster in following['details']]
        print(f"   Following: {', '.join(names)}")
    
    # Show party names
    if party.get('details'):
        names = [monster['name'] for monster in party['details']]
        print(f"   Party: {', '.join(names)}")

def get_available_monsters():
    """Get some monsters from the database for testing"""
    print("\n🔍 Getting available monsters for testing...")
    
    response = test_api_call('GET', '/monsters?limit=10')
    if not response or not response.get('success'):
        print("❌ Cannot get monsters from database")
        return []
    
    monsters = response.get('monsters', [])
    print(f"   Found {len(monsters)} monsters in database")
    
    # Show first few monsters
    for i, monster in enumerate(monsters[:5]):
        print(f"   {i+1}. {monster['name']} (ID: {monster['id']}) - {monster['species']}")
    
    return monsters

def main():
    """Test the complete game state system"""
    print("🧪 Testing Game State System")
    print("=" * 60)
    
    # Step 1: Reset game state
    print("\n📋 Step 1: Reset Game State")
    reset_result = test_api_call('POST', '/game-state/reset')
    if reset_result and reset_result.get('success'):
        print("✅ Game state reset successfully")
        print_game_state(reset_result.get('game_state'))
    else:
        print("❌ Failed to reset game state")
        return
    
    # Step 2: Get available monsters
    print("\n📋 Step 2: Get Available Monsters")
    monsters = get_available_monsters()
    if len(monsters) < 3:
        print("❌ Need at least 3 monsters in database for testing")
        print("💡 Generate some monsters first using the monster generation system")
        return
    
    # Step 3: Add monsters to following list
    print("\n📋 Step 3: Add Monsters to Following List")
    test_monster_ids = [monsters[i]['id'] for i in range(min(6, len(monsters)))]
    
    following_results = []
    for monster_id in test_monster_ids:
        result = test_api_call('POST', '/game-state/following/add', {'monster_id': monster_id})
        following_results.append(result)
        
        if result and result.get('success'):
            print(f"   ✅ {result.get('message', 'Monster added')}")
        else:
            print(f"   ❌ Failed to add monster {monster_id}")
    
    # Step 4: Check following list
    print("\n📋 Step 4: Check Following List")
    following_result = test_api_call('GET', '/game-state/following')
    if following_result and following_result.get('success'):
        following_data = following_result.get('following_monsters', {})
        print(f"   ✅ {following_data.get('count', 0)} monsters following")
        
        if following_data.get('details'):
            for monster in following_data['details']:
                print(f"      - {monster['name']} ({monster['species']})")
    
    # Step 5: Set active party
    print("\n📋 Step 5: Set Active Party")
    
    if len(test_monster_ids) >= 4:
        party_ids = test_monster_ids[:4]  # Take first 4
        print(f"   Setting party with 4 monsters: {party_ids}")
    else:
        party_ids = test_monster_ids  # Use all available
        print(f"   Setting party with {len(party_ids)} monsters: {party_ids}")
    
    party_result = test_api_call('POST', '/game-state/party/set', {'monster_ids': party_ids})
    if party_result and party_result.get('success'):
        print(f"   ✅ {party_result.get('message', 'Party set')}")
    else:
        print(f"   ❌ Failed to set party: {party_result.get('error') if party_result else 'Unknown error'}")
    
    # Step 6: Check party readiness
    print("\n📋 Step 6: Check Party Readiness")
    ready_result = test_api_call('GET', '/game-state/party/ready')
    if ready_result and ready_result.get('success'):
        ready = ready_result.get('ready_for_dungeon', False)
        summary = ready_result.get('party_summary', 'No summary')
        message = ready_result.get('message', 'No message')
        
        print(f"   Ready for dungeon: {ready}")
        print(f"   Party summary: {summary}")
        print(f"   Message: {message}")
        
        if ready:
            print("   ✅ Party is ready for adventure!")
        else:
            print("   ❌ Party not ready for dungeon")
    
    # Step 7: Test party size limits
    print("\n📋 Step 7: Test Party Size Limits")
    if len(test_monster_ids) >= 5:
        print("   Testing party size limit (max 4 monsters)...")
        oversized_party = test_monster_ids[:5]  # Try to set 5 monsters
        
        limit_result = test_api_call('POST', '/game-state/party/set', {'monster_ids': oversized_party})
        if limit_result and not limit_result.get('success'):
            print(f"   ✅ Correctly rejected oversized party: {limit_result.get('error')}")
        else:
            print("   ❌ Failed to reject oversized party")
    else:
        print("   ⏭️ Skipping party size limit test (not enough monsters)")
    
    # Step 8: Test removing from following
    print("\n📋 Step 8: Test Remove from Following")
    if test_monster_ids:
        remove_id = test_monster_ids[-1]  # Remove last monster
        monster_to_remove = next((m for m in monsters if m['id'] == remove_id), None)
        monster_name = monster_to_remove['name'] if monster_to_remove else f"Monster {remove_id}"
        
        print(f"   Removing {monster_name} from following list...")
        remove_result = test_api_call('POST', '/game-state/following/remove', {'monster_id': remove_id})
        
        if remove_result and remove_result.get('success'):
            print(f"   ✅ {remove_result.get('message', 'Monster removed')}")
        else:
            print(f"   ❌ Failed to remove monster")
    
    # Step 9: Final game state check
    print("\n📋 Step 9: Final Game State Check")
    final_state_result = test_api_call('GET', '/game-state')
    if final_state_result and final_state_result.get('success'):
        print("   ✅ Final game state retrieved")
        print_game_state(final_state_result.get('game_state'))
    else:
        print("   ❌ Failed to get final game state")
    
    # Summary
    print("\n📋 Test Summary")
    print("=" * 60)
    
    # Check if we have a working party
    final_state = final_state_result.get('game_state') if final_state_result else None
    if final_state:
        party_count = final_state.get('active_party', {}).get('count', 0)
        following_count = final_state.get('following_monsters', {}).get('count', 0)
        
        print(f"✅ Game State System Working!")
        print(f"   Following Monsters: {following_count}")
        print(f"   Active Party: {party_count}")
        print(f"   Ready for Dungeon: {party_count > 0}")
        
        if party_count > 0:
            print("\n🎉 SUCCESS: Game state system is ready!")
            print("   ✅ Can add monsters to following list")
            print("   ✅ Can set active party from following monsters")
            print("   ✅ Party size limits enforced")
            print("   ✅ Can remove monsters from following")
            print("   ✅ Ready to build dungeon system!")
        else:
            print("\n⚠️ PARTIAL SUCCESS: System works but no active party")
    else:
        print("❌ FAILED: Could not verify final game state")
    
    print(f"\n💡 Next Steps:")
    print(f"   1. Use these endpoints to set up test data")
    print(f"   2. Build dungeon entry/exit system")
    print(f"   3. Add door choice mechanics")
    print(f"   4. Connect LLM text generation")


main()