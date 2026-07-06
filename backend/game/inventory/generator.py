# Inventory Generator - LLM calls that mint items and CoCaToks
# Every generator has a deterministic fallback: a failed LLM call produces
# a generic possession, never a failed workflow (treasure and victories
# must always pay out).

from typing import List
from backend.models.item import Item
from backend.models.cocatok import CoCaTok
from backend.game.utils import build_and_generate, build_and_stream
from backend.core.events import (
    emit_inventory_item_added,
    emit_inventory_cocatok_added
)

# Curated CoCaTok colors - every name exists in the frontend color system
# (frontend/src/shared/styles/theme.css --base-color-*) and uses a hue
# family the pickup explosion supports
COCATOK_COLORS = [
    'red-crimson', 'red-intense',
    'orange-flame', 'orange-amber',
    'yellow-golden', 'yellow-electric',
    'green-emerald', 'green-forest',
    'blue-electric', 'blue-ice', 'blue-ocean',
    'purple-mystic', 'purple-cosmic', 'purple-deep',
    'pink-vibrant', 'pink-electric'
]

ITEM_USES_RANGE = (1, 3)

# ===== ITEMS =====

def generate_treasure_item(location: dict) -> Item:
    """An item discovered on a treasure path - saved and announced"""

    try:
        data = build_and_generate('treasure_item', 'inventory_generation', {
            'location_name': location.get('name', 'Unknown Location'),
            'location_description': location.get('description', '')
        })
    except Exception:
        data = {}

    item = _build_item(data, source_note=f"Found at {location.get('name', 'a forgotten place')}")
    item.save()
    emit_inventory_item_added(item.to_dict())
    return item

def generate_reward_item(location: dict, monster, dialogue_history: str = '') -> Item:
    """The gift a monster grants after a dialogue 'reward' - fits the giver"""

    from backend.game.monster.context_builder import build_monster_block

    try:
        data = build_and_generate('reward_item', 'inventory_generation', {
            'location_name': location.get('name', 'Unknown Location'),
            'location_description': location.get('description', ''),
            'monster_details': build_monster_block(monster),
            'dialogue_history': dialogue_history or '(the conversation is not recorded)'
        })
    except Exception:
        data = {}

    item = _build_item(data, source_note=f"Gift from {monster.name}")
    item.save()
    emit_inventory_item_added(item.to_dict())
    return item

def generate_treasure_discovery_text(location: dict, item: Item, workflow_name: str) -> int:
    """Queue streamed narration of finding the (already generated) item
    - returns generation_id"""

    from backend.game.state.manager import get_party_summary
    from backend.game.dungeon.manager import get_dungeon_log_text

    return build_and_stream('treasure_discovery', workflow_name, {
        'location_name': location.get('name', 'Unknown Location'),
        'location_description': location.get('description', ''),
        'party_summary': get_party_summary(),
        'dungeon_log': get_dungeon_log_text(),
        'item_name': item.name,
        'item_description': item.description
    })

def _build_item(data: dict, source_note: str) -> Item:
    """Normalize LLM item data onto the model; a generic tonic on failure"""

    name = _clean_str(data.get('name'), 'Traveler\'s Tonic', 100)
    description = _clean_str(
        data.get('description'),
        'A small stoppered vial of restorative tonic. Drinking it mends '
        'minor wounds and steadies weary nerves.',
        None
    )

    try:
        uses = int(data.get('uses'))
    except (TypeError, ValueError):
        uses = 1
    uses = max(ITEM_USES_RANGE[0], min(ITEM_USES_RANGE[1], uses))

    return Item(
        name=name,
        description=description,
        emoji=_clean_str(data.get('emoji'), '🎁', 16),
        uses_remaining=uses,
        source_note=source_note[:255]
    )

# ===== COCATOKS =====

def generate_victory_cocatok(location: dict, battle_summary: str, defeated_names: List[str]) -> CoCaTok:
    """Mint the unique keepsake commemorating a battle victory"""

    location_name = location.get('name', 'a forgotten battlefield')
    defeated_text = ', '.join(defeated_names) or 'fearsome foes'

    try:
        data = build_and_generate('victory_cocatok', 'inventory_generation', {
            'location_name': location_name,
            'defeated_names': defeated_text,
            'battle_summary': battle_summary or 'A hard-fought battle ended in victory.',
            'color_options': " | ".join(COCATOK_COLORS)
        })
    except Exception:
        data = {}

    color = _match_color(data.get('color'))

    cocatok = CoCaTok(
        title=_clean_str(data.get('title'), f"Victory at {location_name}", 100),
        emoji=_clean_str(data.get('emoji'), '🏆', 16),
        color=color,
        commemoration=_clean_str(
            data.get('commemoration'),
            f"In memory of the day the party stood against {defeated_text} "
            f"at {location_name} - and prevailed.",
            None
        ),
        event_type='battle_victory',
        location_name=location_name[:100]
    )
    cocatok.save()
    emit_inventory_cocatok_added(cocatok.to_dict())
    return cocatok

def _match_color(value) -> str:
    """Snap an LLM color pick onto the curated list"""
    if isinstance(value, str):
        cleaned = value.strip().lower().replace('_', '-')
        if cleaned in COCATOK_COLORS:
            return cleaned
    return 'purple-mystic'

def _clean_str(value, default, max_length):
    if isinstance(value, str) and value.strip():
        cleaned = value.strip()
        return cleaned[:max_length] if max_length else cleaned
    return default
