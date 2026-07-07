# Inventory Domain Events - Facts About the Party's Possessions
# Emitted from the inventory generator and the item-consumption flows, so
# every workflow that grants or spends possessions broadcasts them
print(f"🔍 Loading {__file__.split('LlmMonsterHunter', 1)[-1]}")

from typing import Any

from .event_registry import _emit_from_schema, register_events

# ===== INVENTORY EVENT DEFINITIONS =====

INVENTORY_EVENTS = {
    'inventory.item_added': {
        'data_fields': {'item': 'Complete item data (from item.to_dict())'},
        'send_to_frontend': True,
    },
    'inventory.item_updated': {
        'data_fields': {'item': 'Complete item data after a change (uses decremented)'},
        'send_to_frontend': True,
    },
    'inventory.item_consumed': {
        'data_fields': {
            'item_id': 'Database ID of the item that was used up and deleted',
            'name': 'The name of the consumed item (for narration)',
        },
        'send_to_frontend': True,
    },
    'inventory.cocatok_added': {
        'data_fields': {'cocatok': 'Complete CoCaTok data (from cocatok.to_dict())'},
        'send_to_frontend': True,
    },
}

# Register inventory events with the core registry
register_events(INVENTORY_EVENTS)

# ===== INVENTORY EVENT FUNCTIONS =====


def emit_inventory_item_added(item: dict[str, Any]) -> bool:
    """Emit when a new item lands in the party's inventory"""
    return _emit_from_schema('inventory.item_added', item=item)


def emit_inventory_item_updated(item: dict[str, Any]) -> bool:
    """Emit when an item changes (a use spent, but uses remain)"""
    return _emit_from_schema('inventory.item_updated', item=item)


def emit_inventory_item_consumed(item_id: int, name: str) -> bool:
    """Emit when an item's last use is spent and it is gone"""
    return _emit_from_schema('inventory.item_consumed', item_id=item_id, name=name)


def emit_inventory_cocatok_added(cocatok: dict[str, Any]) -> bool:
    """Emit when a victory mints a new CoCaTok keepsake"""
    return _emit_from_schema('inventory.cocatok_added', cocatok=cocatok)
