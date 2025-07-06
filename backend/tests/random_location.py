from backend.services.dungeon_service import _generate_random_location

print('\n🗺️ Testing Random Location Generation...')
result = _generate_random_location()

if result['success']:
    location = result['location']
    print(f'✅ Generated location: {location["name"]}')
    print(f'   Description: "{location["description"]}"')
else:
    print(f'❌ Failed: {result["error"]}')