# Game-State Events - the world itself changing shape
# Today just one: the New Game wipe. It is emitted AFTER the wipe
# transaction commits, so any listener that refetches on it reads the
# already-empty world - this is how app-level frontend state (the party
# roster, the player pointer) empties the moment the world does instead
# of waiting for a page refresh.

from typing import Any

from .event_registry import _emit_from_schema, register_events

# ===== GAME-STATE EVENT DEFINITIONS =====

GAME_STATE_EVENTS = {
    'game.world_erased': {
        'data_fields': {
            'deleted_rows': 'Per-table deleted-row counts from the wipe',
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
