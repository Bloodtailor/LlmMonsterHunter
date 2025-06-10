#!/usr/bin/env python3
"""
Test Monster Model Script
Tests that the Monster model works with the database
Run this to verify the database schema is correct
"""

import sys
import os

# Add backend directory to path so we can import our modules
backend_path = os.path.join(os.path.dirname(__file__), 'backend')
sys.path.append(backend_path)

from backend.app import create_app
from backend.config.database import db
from backend.models.monster import Monster

def test_monster_model():
    """Test that Monster model works with database"""
    print("🧪 Testing Monster Model...")
    
    # Create Flask app and test within app context
    app = create_app()
    
    with app.app_context():
        try:
            # Create all tables (including monsters table)
            print("Creating database tables...")
            db.create_all()
            print("✅ Tables created successfully")
            
            # Test creating a monster manually (without LLM for now)
            print("\nTesting monster creation...")
            test_monster_data = {
                'basic_info': {
                    'name': 'Rokk',
                    'species': 'Stone Guardian', 
                    'description': 'A sturdy creature made of ancient stone',
                    'backstory': 'Rokk was born in the deep caves of the mountain realm. After his colony was destroyed by an earthquake, he wandered into the outside world, seeking new allies and a new home.'
                },
                'stats': {
                    'health': 120,
                    'attack': 25,
                    'defense': 30,
                    'speed': 8
                },
                'personality': {
                    'traits': ['loyal', 'protective', 'slow to trust', 'wise']
                },
                'abilities': [
                    {'name': 'Stone Throw', 'description': 'Hurls a boulder at enemies'},
                    {'name': 'Rock Armor', 'description': 'Hardens skin for increased defense'}
                ]
            }
            
            # Create monster from test data
            monster = Monster.create_from_llm_data(test_monster_data)
            print(f"✅ Monster created: {monster.name} the {monster.species}")
            
            # Save to database
            if monster.save():
                print("✅ Monster saved to database")
                
                # Test retrieval
                saved_monster = Monster.get_monster_by_id(monster.id)
                if saved_monster:
                    print(f"✅ Monster retrieved: {saved_monster.name}")
                    
                    # Test JSON serialization
                    monster_json = saved_monster.to_dict()
                    print("✅ JSON serialization works")
                    print(f"   Name: {monster_json['name']}")
                    print(f"   Species: {monster_json['species']}")
                    print(f"   Stats: {monster_json['stats']}")
                    print(f"   Traits: {monster_json['personality_traits']}")
                    
                    # Test getting all monsters
                    all_monsters = Monster.get_all_monsters()
                    print(f"✅ Retrieved {len(all_monsters)} monster(s) from database")
                    
                else:
                    print("❌ Failed to retrieve monster from database")
                    return False
            else:
                print("❌ Failed to save monster to database")
                return False
                
        except Exception as e:
            print(f"❌ Monster model test failed: {e}")
            import traceback
            traceback.print_exc()
            return False
    
    print("\n🎉 Monster model test completed successfully!")
    print("Database schema is ready for AI monster generation!")
    return True

if __name__ == "__main__":
    if test_monster_model():
        print("\n📋 Next step: Create LLM service for monster generation")
    else:
        print("\n❌ Fix monster model issues before proceeding")