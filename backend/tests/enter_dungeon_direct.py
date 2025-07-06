from backend.services.dungeon_service import enter_dungeon

print('ENTERING DUNGEON...')
dungeon = enter_dungeon()
print(f'dump: {dungeon}')

success = dungeon.get('success')
dungeon_entered = dungeon.get('dungeon_entered')
entry_text = dungeon.get('entry_text')
location = dungeon.get('location')
doors = dungeon.get('doors')
party_summary = dungeon.get('party_summary')
message = dungeon.get('message')


print(f'success: {success}')
print(f'dungeon_entered: {dungeon_entered}')
print(f'entry_text: {entry_text}')
print(f'doors: {doors}')
print(f'party_summary: {party_summary}')
print(f'message: {message}')

