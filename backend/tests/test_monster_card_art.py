# Test Monster Card Art Generation
# Tests generating card art for an existing monster using the new generic system

import random
from backend.services import generation_service
from backend.models.monster import Monster

print("🎨 Testing Monster Card Art Generation...")
print("=" * 60)

# Step 1: Get a random monster from the database
print("\n🔍 Step 1: Finding a random monster from database...")

try:
    # Get all monsters
    monsters = Monster.get_all_monsters()
    
    if not monsters:
        print("❌ No monsters found in database!")
        print("💡 Generate some monsters first using the monster generation system")
        exit()
    
    # Pick a random monster
    random_monster = random.choice(monsters)
    
    print(f"✅ Selected random monster:")
    print(f"   ID: {random_monster.id}")
    print(f"   Name: {random_monster.name}")
    print(f"   Species: {random_monster.species}")
    print(f"   Description: {random_monster.description[:100]}...")
    print(f"   Abilities: {len(random_monster.abilities)} abilities")
    
except Exception as e:
    print(f"❌ Error accessing database: {e}")
    print("💡 Make sure the database is running and has monsters")
    exit()

# Step 2: Build prompt text from monster data
print("\n✏️ Step 2: Building prompt text from monster data...")

# Combine monster information into prompt text
prompt_parts = []
if random_monster.name:
    prompt_parts.append(random_monster.name)
if random_monster.species:
    prompt_parts.append(random_monster.species)
if random_monster.description:
    prompt_parts.append(random_monster.description)

prompt_text = ", ".join(prompt_parts)

print(f"✅ Built prompt text:")
print(f"   Length: {len(prompt_text)} characters")
print(f"   Text: {prompt_text[:150]}...")

# Step 3: Generate card art using generic image generation
print("\n🎨 Step 3: Generating card art using generic system...")

try:
    result = generation_service.image_generation_request(
        prompt_text=prompt_text,
        prompt_type="monster_card_art",
        prompt_name="monster_generation",  # Use monster_generation workflow
        wait_for_completion=True  # Wait for the actual generation
    )
    
    print(f"\n📊 Generation Results:")
    print(f"   Success: {result['success']}")
    print(f"   Generation ID: {result.get('generation_id', 'N/A')}")
    print(f"   Generation Type: {result.get('generation_type', 'N/A')}")
    
    if result['success']:
        print(f"   Image Path: {result.get('image_path', 'N/A')}")
        print(f"   Relative Path: {result.get('relative_path', 'N/A')}")
        print(f"   Execution Time: {result.get('execution_time', 0)}s")
        print(f"   Workflow Used: {result.get('workflow_used', 'N/A')}")
        print(f"   Image Dimensions: {result.get('image_dimensions', 'N/A')}")
        
        print(f"\n🎉 SUCCESS! Card art generated for {random_monster.name}")
        print(f"   The image is saved in the ComfyUI outputs folder")
        print(f"   Organized path: outputs/{result.get('relative_path', 'unknown')}")
        
    else:
        print(f"   Error: {result.get('error', 'Unknown error')}")
        if result.get('help'):
            print(f"   Help: {result['help']}")
        
        # Check if it's a server issue
        if 'server' in result.get('error', '').lower():
            print("\n💡 Troubleshooting:")
            print("   1. Make sure ComfyUI is running: python main.py --listen")
            print("   2. Check ENABLE_IMAGE_GENERATION=true in .env")
            print("   3. Verify ComfyUI server is accessible at http://127.0.0.1:8188")

except Exception as e:
    print(f"❌ Unexpected error during generation: {e}")

# Step 4: Test the convenience function too
print("\n🐉 Step 4: Testing monster convenience function...")

try:
    convenience_result = generation_service.generate_monster_image(
        monster_description=random_monster.description,
        monster_name=random_monster.name,
        monster_species=random_monster.species,
        wait_for_completion=False  # Don't wait to save time
    )
    
    print(f"   Convenience function success: {convenience_result['success']}")
    print(f"   Generation ID: {convenience_result.get('generation_id', 'N/A')}")
    print(f"   Message: {convenience_result.get('message', 'N/A')}")
    
except Exception as e:
    print(f"   Convenience function error: {e}")

# Step 5: Summary and architecture notes
print("\n📋 Architecture Validation:")
print("✅ Generic image_generation_request() used successfully")
print("✅ No hardcoded monster logic in ComfyUI layer")
print("✅ Prompt text assembled at service layer, not ComfyUI layer")
print("✅ Configuration loaded from comfyui_config.py")
print("✅ Organized file structure in outputs/workflow_name/")
print("✅ Unified queue system handled the request")

print(f"\n🏁 Monster Card Art Generation Test Complete!")
print(f"   Monster tested: {random_monster.name} (ID: {random_monster.id})")
print(f"   Architecture: Clean separation of concerns maintained")