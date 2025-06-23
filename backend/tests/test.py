# Updated basic test to use new unified generation_service
from backend.services import generation_service  # 🔧 UPDATED: was llm_service

print("🧪 Basic Generation Service Test...")

# THE ONLY WAY to do inference - automatic logging!
result = generation_service.text_generation_request(  # 🔧 UPDATED: was inference_request
    prompt="please respond with just the word 'hi' and nothing else",
)

print(f"📊 Result: {result.get('text', 'No text generated')}")
print(f"✅ Success: {result['success']}")
print(f"🆔 Generation ID: {result.get('generation_id', 'Unknown')}")
print("🏁 Test complete!")