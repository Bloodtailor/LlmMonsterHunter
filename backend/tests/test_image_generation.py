# Updated basic test to use new unified generation_service
from backend.services import generation_service  # 🔧 UPDATED: was llm_service

print("🧪 Basic Generation Service Test...")

# THE ONLY WAY to do inference - automatic logging!
result = generation_service.image_generation_request(
    monster_description = "A funny looking dwarf with a fish helmet",
    monster_name = "Bubba",
    monster_species = "dwarf"
)

print(f"📊 Result: {result.get('text', 'No text generated')}")
print(f"✅ Success: {result['success']}")
print(f"🆔 Generation ID: {result.get('generation_id', 'Unknown')}")
print("🏁 Test complete!")