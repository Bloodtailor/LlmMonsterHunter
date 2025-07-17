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

def test_add_5_random_monsters():
    """Add 5 random monsters from database to following list"""
    print('🎯 Adding 5 Random Monsters to Following List...')
    
    # Get all monsters from database
    monsters_result = api_call('GET', '/monsters?limit=100')
    if not monsters_result.get('success'):
        print('❌ Failed to get monsters from database')
        return
    
    all_monsters = monsters_result.get('monsters', [])
    if len(all_monsters) < 5:
        print(f'❌ Only {len(all_monsters)} monsters in database, need at least 5')
        return
    
    # Get currently following monsters
    following_result = api_call('GET', '/game-state/following')
    if not following_result.get('success'):
        print('❌ Failed to get current following list')
        return
    
    currently_following_ids = following_result.get('following_monsters', {}).get('ids', [])
    
    # Find monsters not currently following
    available_monsters = [m for m in all_monsters if m['id'] not in currently_following_ids]
    
    if len(available_monsters) < 5:
        print(f'⚠️ Only {len(available_monsters)} monsters available (not already following)')
        monsters_to_add = available_monsters
    else:
        monsters_to_add = random.sample(available_monsters, 5)
    
    print(f'   Selected {len(monsters_to_add)} monsters to add:')
    
    # Add each monster to following list
    added_count = 0
    for monster in monsters_to_add:
        result = api_call('POST', '/game-state/following/add', {'monster_id': monster['id']})
        
        if result.get('success'):
            print(f'   ✅ {monster["name"]} ({monster["species"]})')
            added_count += 1
        else:
            print(f'   ❌ Failed to add {monster["name"]}: {result.get("error")}')
    
    print(f'\n🎉 Successfully added {added_count} monsters to following list!')
    
    # Show final following list
    final_result = api_call('GET', '/game-state/following')
    if final_result.get('success'):
        final_count = final_result.get('following_monsters', {}).get('count', 0)
        print(f'   Total monsters now following: {final_count}')



def main():
    print('🧪 FOLLOWING LIST MANAGEMENT TESTS')
    print('=' * 50)
    
    # Show initial state
    initial_result = api_call('GET', '/game-state/following')
    if initial_result.get('success'):
        initial_count = initial_result.get('following_monsters', {}).get('count', 0)
        print(f'📊 Initial following count: {initial_count}')
    
    print('\n1️⃣ TEST: Add 5 Random Monsters')
    test_add_5_random_monsters()

main()