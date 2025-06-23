# Updated test to use new unified generation_service
from backend.services import generation_service  # 🔧 UPDATED: was llm_service

print("🧪 Starting Unified Generation Service Test...")

# THE ONLY WAY to do LLM inference - through generation_service!
result = generation_service.text_generation_request(  # 🔧 UPDATED: new method name
    prompt="Time to get kicking",
)

print("📊 Generation Result:")
print(f"   Success: {result['success']}")
print(f"   Text: {result.get('text', 'N/A')}")
print(f"   Tokens: {result.get('tokens', 0)}")
print(f"   Duration: {result.get('duration', 0)}s")
print(f"   Generation ID: {result.get('generation_id', 'N/A')}")
print(f"   Generation Type: {result.get('generation_type', 'N/A')}")

print("🏁 Unified Generation Service Test complete!")