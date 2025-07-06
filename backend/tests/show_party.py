# Simple Test: Show Current Party
# Displays current game state, following monsters, and active party

import requests

BASE_URL = "http://localhost:5000/api"

def main():
    print("👥 Current Party Status:")
    print("=" * 40)
    
    try:
        # Get complete game state
        response = requests.get(f"{BASE_URL}/game-state", timeout=10)
        
        if response.status_code != 200:
            print(f"❌ HTTP Error: {response.status_code}")
            return
        
        result = response.json()
        if not result.get('success'):
            print(f"❌ Failed: {result.get('error', 'Unknown error')}")
            return
        
        game_state = result.get('game_state', {})
        
        # Following monsters
        following = game_state.get('following_monsters', {})
        following_count = following.get('count', 0)
        following_details = following.get('details', [])
        
        print(f"\n🐾 Following Monsters: {following_count}")
        if following_details:
            for monster in following_details:
                print(f"   - {monster['name']} (ID: {monster['id']}) - {monster['species']}")
        else:
            print("   (No monsters following)")
        
        # Active party
        party = game_state.get('active_party', {})
        party_count = party.get('count', 0)
        party_details = party.get('details', [])
        
        print(f"\n⚔️ Active Party: {party_count}/4")
        if party_details:
            for monster in party_details:
                abilities_count = len(monster.get('abilities', []))
                print(f"   - {monster['name']} ({monster['species']}) - {abilities_count} abilities")
        else:
            print("   (No active party)")
        
        # Dungeon status
        dungeon = game_state.get('dungeon_state', {})
        in_dungeon = dungeon.get('in_dungeon', False)
        
        print(f"\n🏰 Location: {'In Dungeon' if in_dungeon else 'Home Base'}")
        
        # Ready status
        ready = party_count > 0
        print(f"\n🎯 Ready for Adventure: {'✅ Yes' if ready else '❌ No (need active party)'}")
        
    except Exception as e:
        print(f"❌ Error: {e}")

main()