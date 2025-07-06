# Simple Test: Add 4 Random Monsters to Party
# Gets random monsters from database and sets them as active party

import requests
import random

BASE_URL = "http://localhost:5000/api"

def main():
    print("🎲 Adding 4 random monsters to party...")
    
    try:
        # Get available monsters
        monsters_response = requests.get(f"{BASE_URL}/monsters?limit=20", timeout=10)
        
        if monsters_response.status_code != 200:
            print("❌ Could not get monsters from database")
            return
        
        monsters_data = monsters_response.json()
        if not monsters_data.get('success'):
            print("❌ Failed to fetch monsters")
            return
        
        monsters = monsters_data.get('monsters', [])
        if len(monsters) < 4:
            print(f"⚠️ Only {len(monsters)} monsters available (need 4)")
            if len(monsters) == 0:
                print("💡 Generate some monsters first!")
                return
        
        # Select random monsters (up to 4)
        selected_count = min(4, len(monsters))
        selected_monsters = random.sample(monsters, selected_count)
        monster_ids = [monster['id'] for monster in selected_monsters]
        
        print(f"Selected {selected_count} monsters:")
        for monster in selected_monsters:
            print(f"   - {monster['name']} ({monster['species']})")
        
        # Add to following list
        for monster_id in monster_ids:
            requests.post(f"{BASE_URL}/game-state/following/add", 
                         json={'monster_id': monster_id}, timeout=10)
        
        # Set as active party
        party_response = requests.post(f"{BASE_URL}/game-state/party/set", 
                                     json={'monster_ids': monster_ids}, timeout=10)
        
        if party_response.status_code == 200:
            party_result = party_response.json()
            if party_result.get('success'):
                print(f"✅ Party set successfully!")
                print(f"   {party_result.get('message', 'Party ready')}")
            else:
                print(f"❌ Failed to set party: {party_result.get('error')}")
        else:
            print(f"❌ HTTP Error setting party: {party_response.status_code}")
            
    except Exception as e:
        print(f"❌ Error: {e}")

main()