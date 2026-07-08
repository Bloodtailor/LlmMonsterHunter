# Game-State Events - the world itself changing shape
# The New Game wipe (emitted AFTER the transaction commits, so listeners
# that refetch on it read the already-empty world) and roster changes
# the BACKEND makes on its own (a new follower auto-seated into the
# party) - both exist so app-level frontend state (the party roster, the
# player pointer) tracks the world without a page refresh.

from typing import Any, Optional

from .event_registry import _emit_from_schema, register_events

# ===== GAME-STATE EVENT DEFINITIONS =====

GAME_STATE_EVENTS = {
    'game.world_erased': {
        'data_fields': {
            'deleted_rows': 'Per-table deleted-row counts from the wipe',
        },
        'send_to_frontend': True,
    },
    'game.party_updated': {
        'data_fields': {
            'monster_id': 'The monster whose roster place changed',
            'monster_name': 'Its name (display convenience)',
            'joined_party': 'True when it stepped into an open party seat',
            'party_ids': 'The party lineup after the change (player first)',
        },
        'send_to_frontend': True,
    },
}

# Register game-state events with the core registry
register_events(GAME_STATE_EVENTS)

# ===== GAME-STATE EVENT FUNCTIONS =====


def emit_game_world_erased(deleted_rows: dict[str, Any]) -> bool:
    """Emit after New Game wiped the world (post-commit only)"""
    return _emit_from_schema('game.world_erased', deleted_rows=deleted_rows)


def emit_party_updated(
    monster_id: int,
    monster_name: Optional[str],
    joined_party: bool,
    party_ids: list[int],
) -> bool:
    """Emit when the backend reshapes the roster on its own (a new
    follower, possibly auto-seated into an open party slot)"""
    return _emit_from_schema(
        'game.party_updated',
        monster_id=monster_id,
        monster_name=monster_name,
        joined_party=joined_party,
        party_ids=party_ids,
    )
