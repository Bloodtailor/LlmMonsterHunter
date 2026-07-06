# Inventory Service - TRUST BOUNDARY: Validation + Delegation
# Validates list parameters and delegates to the inventory manager

from typing import Dict, Any
from backend.core.utils import error_response
from backend.game import inventory

VALID_KINDS = ('items', 'cocatoks')

def get_inventory(kind: str = 'items', limit: int = None, offset: int = 0) -> Dict[str, Any]:
    """Paged inventory listing - validate parameters"""

    if kind not in VALID_KINDS:
        return error_response(f"Invalid kind '{kind}'. Valid: {list(VALID_KINDS)}")

    if limit is not None and (not isinstance(limit, int) or limit < 1 or limit > 1000):
        return error_response('limit must be between 1 and 1000')

    if not isinstance(offset, int) or offset < 0:
        return error_response('offset must be 0 or greater')

    return inventory.manager.get_inventory(kind, limit, offset)

def get_inventory_counts() -> Dict[str, Any]:
    """Item and CoCaTok counts for tab badges"""
    return inventory.manager.get_inventory_counts()
