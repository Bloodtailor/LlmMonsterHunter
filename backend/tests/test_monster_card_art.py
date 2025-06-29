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
    
    
except Exception as e:
    print(f"❌ Unexpected error during generation: {e}")

