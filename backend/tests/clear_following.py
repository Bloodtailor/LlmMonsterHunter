# Test Following List Management
# Simple tests to add random monsters and clear following list
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

def test_clear_following_list():
    """Clear all monsters from following list"""
    print('🧹 Clearing Following List...')
    
    # Get current following list
    following_result = api_call('GET', '/game-state/following')
    if not following_result.get('success'):
        print('❌ Failed to get current following list')
        return
    
    following_monsters = following_result.get('following_monsters', {})
    current_ids = following_monsters.get('ids', [])
    current_details = following_monsters.get('details', [])
    
    if not current_ids:
        print('   No monsters currently following - already clear!')
        return
    
    print(f'   Currently following {len(current_ids)} monsters:')
    for monster in current_details:
        print(f'      - {monster["name"]} ({monster["species"]})')
    
    # Remove each monster
    removed_count = 0
    for monster_id in current_ids:
        result = api_call('POST', '/game-state/following/remove', {'monster_id': monster_id})
        
        if result.get('success'):
            removed_count += 1
        else:
            print(f'   ❌ Failed to remove monster {monster_id}: {result.get("error")}')
    
    print(f'\n🎉 Successfully removed {removed_count} monsters from following list!')
    
    # Verify list is empty
    final_result = api_call('GET', '/game-state/following')
    if final_result.get('success'):
        final_count = final_result.get('following_monsters', {}).get('count', 0)
        if final_count == 0:
            print('   ✅ Following list is now empty')
        else:
            print(f'   ⚠️ {final_count} monsters still following (some removals failed)')

            
def main():
    print('🧪 FOLLOWING LIST MANAGEMENT TESTS')
    print('=' * 50)
    
    # Show initial state
    initial_result = api_call('GET', '/game-state/following')
    if initial_result.get('success'):
        initial_count = initial_result.get('following_monsters', {}).get('count', 0)
        print(f'📊 Initial following count: {initial_count}')
    
    print('\n2️⃣ TEST: Clear Following List')  
    test_clear_following_list()

main()