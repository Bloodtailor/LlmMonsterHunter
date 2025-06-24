# Test Card Art Integration
# Tests the complete monster + card art generation pipeline

from backend.services import monster_service
from backend.models.monster import Monster
from pathlib import Path
import os

print("🎨 Testing Complete Card Art Integration...")
print("=" * 60)

# Step 1: Test generating a new monster with card art
print("\n🐉 Step 1: Generating new monster with automatic card art...")

try:
    result = monster_service.generate_monster(
        prompt_name='detailed_monster',
        wait_for_completion=True,
        generate_card_art=True  # Enable card art generation
    )
    
    print(f"📊 Monster Generation Result:")
    print(f"   Success: {result['success']}")
    
    if result['success']:
        monster_data = result['monster']
        stats = result['generation_stats']
        
        print(f"   Monster Name: {monster_data['name']}")
        print(f"   Monster Species: {monster_data['species']}")
        print(f"   Abilities Generated: {stats['abilities_generated']}")
        print(f"   Card Art Generated: {stats['card_art_generated']}")
        
        # Check card art details
        card_art = monster_data.get('card_art', {})
        print(f"\n🎨 Card Art Details:")
        print(f"   Has Card Art: {card_art.get('has_card_art', False)}")
        print(f"   Relative Path: {card_art.get('relative_path', 'None')}")
        print(f"   File Exists: {card_art.get('exists', False)}")
        
        if card_art.get('exists'):
            print(f"   ✅ Card art file found on disk!")
            print(f"   Full Path: {card_art.get('full_path', 'N/A')}")
        else:
            print(f"   ❌ Card art file not found on disk")
        
        # Check folder organization
        if card_art.get('relative_path'):
            relative_path = card_art['relative_path']
            folder_name = relative_path.split('/')[0] if '/' in relative_path else 'unknown'
            print(f"   Folder Organization: {folder_name}/")
            print(f"   Expected: monster_card_art/")
            print(f"   Correct: {'✅' if folder_name == 'monster_card_art' else '❌'}")
        
        monster_id = monster_data['id']
        
    else:
        print(f"   Error: {result['error']}")
        monster_id = None

except Exception as e:
    print(f"❌ Error during monster generation: {e}")
    monster_id = None

# Step 2: Test generating card art for existing monster (if we have one)
if monster_id:
    print(f"\n🖼️ Step 2: Testing card art generation for existing monster...")
    
    try:
        # Generate card art again (should create a new image)
        art_result = monster_service.generate_card_art_for_existing_monster(
            monster_id=monster_id,
            wait_for_completion=True
        )
        
        print(f"📊 Card Art Generation Result:")
        print(f"   Success: {art_result['success']}")
        
        if art_result['success']:
            print(f"   Image Path: {art_result['image_path']}")
            print(f"   Execution Time: {art_result['execution_time']}s")
            print(f"   Workflow Used: {art_result.get('workflow_used', 'N/A')}")
            print(f"   Prompt Type Used: {art_result.get('prompt_type_used', 'N/A')}")
        else:
            print(f"   Error: {art_result['error']}")
    
    except Exception as e:
        print(f"❌ Error during card art generation: {e}")

else:
    print(f"\n⏭️ Step 2: Skipped (no monster to test with)")

# Step 3: Test database card art info retrieval
if monster_id:
    print(f"\n🗄️ Step 3: Testing database card art info retrieval...")
    
    try:
        # Get monster from database
        monster = Monster.get_monster_by_id(monster_id)
        
        if monster:
            print(f"✅ Monster retrieved from database: {monster.name}")
            
            # Get card art info
            card_art_info = monster.get_card_art_info()
            
            print(f"📊 Database Card Art Info:")
            print(f"   Has Card Art: {card_art_info['has_card_art']}")
            print(f"   Relative Path: {card_art_info['relative_path']}")
            print(f"   File Exists: {card_art_info['exists']}")
            
            # Test API format
            monster_dict = monster.to_dict()
            api_card_art = monster_dict.get('card_art', {})
            
            print(f"📊 API Format:")
            print(f"   Has Card Art: {api_card_art.get('has_card_art', False)}")
            print(f"   Relative Path: {api_card_art.get('relative_path', 'None')}")
        else:
            print(f"❌ Monster not found in database")
    
    except Exception as e:
        print(f"❌ Error retrieving from database: {e}")

else:
    print(f"\n⏭️ Step 3: Skipped (no monster to test with)")

# Step 4: Check file organization
print(f"\n📁 Step 4: Checking file organization...")

try:
    # Check if outputs directory exists and has proper structure
    outputs_dir = Path(__file__).parent.parent / 'ai' / 'comfyui' / 'outputs'
    
    print(f"   Outputs Directory: {outputs_dir}")
    print(f"   Exists: {outputs_dir.exists()}")
    
    if outputs_dir.exists():
        # Check for monster_card_art folder
        card_art_dir = outputs_dir / 'monster_card_art'
        print(f"   Card Art Directory: {card_art_dir}")
        print(f"   Exists: {card_art_dir.exists()}")
        
        if card_art_dir.exists():
            # Count images
            images = list(card_art_dir.glob("*.png"))
            print(f"   Images Found: {len(images)}")
            
            if images:
                print(f"   Latest Image: {images[-1].name}")
                print(f"   File Size: {images[-1].stat().st_size} bytes")

except Exception as e:
    print(f"❌ Error checking file organization: {e}")

# Step 5: Test path storage format
print(f"\n💾 Step 5: Testing path storage format...")

try:
    # Get all monsters and check their card art paths
    all_monsters = Monster.get_all_monsters()
    monsters_with_art = [m for m in all_monsters if m.card_art_path]
    
    print(f"   Total Monsters: {len(all_monsters)}")
    print(f"   Monsters with Card Art: {len(monsters_with_art)}")
    
    if monsters_with_art:
        for monster in monsters_with_art[-3:]:  # Show last 3
            print(f"   Monster: {monster.name}")
            print(f"      Path: {monster.card_art_path}")
            print(f"      Format: {'✅ Relative' if not monster.card_art_path.startswith('/') and ':' not in monster.card_art_path else '❌ Absolute'}")

except Exception as e:
    print(f"❌ Error checking path storage: {e}")

# Summary
print(f"\n🏁 Card Art Integration Test Summary:")
print("=" * 60)

enabled = os.getenv('ENABLE_IMAGE_GENERATION', 'false').lower() == 'true'
if enabled:
    print("✅ Image generation is ENABLED")
    print("✅ Card art should be generated automatically for new monsters")
    print("✅ Card art paths should be stored as relative paths")
    print("✅ Images should be organized in prompt_type folders (monster_card_art/)")
    print("✅ API should include card art info in monster responses")
else:
    print("⚠️ Image generation is DISABLED")
    print("   Set ENABLE_IMAGE_GENERATION=true to enable card art generation")

print(f"\n💡 Next Steps:")
print("   1. Generate monsters and verify card art is created and connected")
print("   2. Check that paths are stored correctly in database")
print("   3. Verify file organization uses prompt_type folders")
print("   4. Test the new card art API endpoints")
print("   5. Update frontend to display card art images")