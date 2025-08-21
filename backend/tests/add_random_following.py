# Test Script: Add 5 Random Monsters to Following List
# Uses the service layer directly to test the new simplified architecture

import random
import sys
import os

# Add backend to path so we can import modules
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

def test_add_random_following():
    """Add 5 random monsters from database to following list"""
    
    print('🧪 TESTING: Add 5 Random Monsters to Following List')
    print('=' * 60)
    
    try:
        # Import models and services
        from backend.models.monster import Monster
        from backend.models.following_monsters import FollowingMonster
        from backend.services import game_state_service
        
        # Get all monsters from database
        print('📊 Getting all monsters from database...')
        all_monsters = Monster.get_all_monsters()
        
        if len(all_monsters) < 5:
            print(f'❌ Only {len(all_monsters)} monsters in database, need at least 5')
            return
        
        print(f'   Found {len(all_monsters)} total monsters')
        
        # Get currently following monsters
        print('📊 Getting currently following monsters...')
        currently_following_ids = FollowingMonster.get_following_monster_ids()
        print(f'   Currently following: {len(currently_following_ids)} monsters')
        
        # Find monsters not currently following
        available_monsters = [m for m in all_monsters if m.id not in currently_following_ids]
        
        if len(available_monsters) < 5:
            print(f'⚠️ Only {len(available_monsters)} monsters available (not already following)')
            monsters_to_add = available_monsters
        else:
            monsters_to_add = random.sample(available_monsters, 5)
        
        print(f'\n🎯 Selected {len(monsters_to_add)} monsters to add:')
        for monster in monsters_to_add:
            print(f'   - {monster.name} ({monster.species}) [ID: {monster.id}]')
        
        print(f'\n🚀 Adding monsters using service layer...')
        
        # Add each monster using the service layer
        added_count = 0
        for monster in monsters_to_add:
            print(f'\n   Adding {monster.name}...')
            
            result = game_state_service.add_following_monster(monster.id)
            
            if result['success']:
                print(f'   ✅ {result["message"]}')
                print(f'      Following count: {result["following_count"]}')
                added_count += 1
            else:
                print(f'   ❌ Failed: {result["error"]}')
        
        print(f'\n🎉 Results:')
        print(f'   Successfully added: {added_count}/{len(monsters_to_add)} monsters')
        
        # Show final following list
        print(f'\n📋 Final Following List:')
        final_result = game_state_service.get_following_monsters()
        
        if final_result['success']:
            following_data = final_result['following_monsters']
            print(f'   Total following: {following_data["count"]} monsters')
            
            for monster_data in following_data['details']:
                print(f'   - {monster_data["name"]} ({monster_data["species"]})')
        else:
            print(f'   ❌ Error getting final list: {final_result["error"]}')
        
    except Exception as e:
        print(f'❌ Test failed with exception: {str(e)}')
        import traceback
        traceback.print_exc()


# Run the tests
test_add_random_following()

print(f'\n✨ Test completed!')