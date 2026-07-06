# Inventory Manager - Pure Business Logic
# Paged listing of the party's items and CoCaTok keepsakes
# Assumes valid parameters (the service layer is the trust boundary)

from typing import Dict, Any
from backend.models.item import Item
from backend.models.cocatok import CoCaTok
from backend.core.utils import success_response

def get_inventory(kind: str, limit: int, offset: int) -> Dict[str, Any]:
    """One paged inventory kind ('items' or 'cocatoks'), newest first,
    in the same pagination shape as the monster list"""

    model = Item if kind == 'items' else CoCaTok
    query = model.query.order_by(model.created_at.desc())

    total_count = query.count()

    query = query.offset(offset)
    if limit is not None:
        query = query.limit(limit)

    entries = query.all()

    return success_response({
        'kind': kind,
        'entries': [entry.to_dict() for entry in entries],
        'total': total_count,
        'count': len(entries),
        'pagination': {
            'limit': limit,
            'offset': offset,
            'has_more': offset + len(entries) < total_count,
            'next_offset': offset + limit if limit is not None and offset + len(entries) < total_count else None,
            'prev_offset': max(0, offset - limit) if limit is not None and offset > 0 else None
        }
    })

def get_inventory_counts() -> Dict[str, Any]:
    """How many of each the party holds (for tab badges)"""

    return success_response({
        'item_count': Item.query.count(),
        'cocatok_count': CoCaTok.query.count()
    })

def spend_item_use(item: Item) -> Dict[str, Any]:
    """
    Spend one use of an item; the item is DELETED when its last use goes.
    Emits inventory.item_updated or inventory.item_consumed accordingly.
    Returns {'consumed': bool, 'item_id': int, 'name': str}
    """
    from backend.core.events import (
        emit_inventory_item_updated,
        emit_inventory_item_consumed
    )

    item.uses_remaining = max(0, (item.uses_remaining or 1) - 1)

    if item.uses_remaining <= 0:
        result = {'consumed': True, 'item_id': item.id, 'name': item.name}
        item.delete()
        emit_inventory_item_consumed(result['item_id'], result['name'])
        return result

    item.save()
    emit_inventory_item_updated(item.to_dict())
    return {'consumed': False, 'item_id': item.id, 'name': item.name}
