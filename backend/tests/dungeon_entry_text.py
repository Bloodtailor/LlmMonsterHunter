from backend.services.dungeon_service import _generate_dungeon_entry_text

print('Generating Dungeon Entry Text...')
entry_text = _generate_dungeon_entry_text('Tanner and Luna')

text = entry_text['text']
print(f'Generated text: {text}')