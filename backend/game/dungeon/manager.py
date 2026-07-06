# Dungeon Manager - Dungeon Run State
# Owns the persistent dungeon state stored in GlobalVariable ('dungeon_state')
# Hidden information (path events, riddle answers) lives ONLY here -
# use get_public_paths() for anything that leaves the backend

from typing import Dict, Any, Optional
from backend.models.global_variables import GlobalVariable

DUNGEON_STATE_KEY = 'dungeon_state'

_EMPTY_STATE = {
    'in_dungeon': False,
    'current_location': None,
    'available_paths': {},
    'active_encounter': None,
    'party_conditions': {}   # monster_id: condition - battle damage persists in the run
}

# ===== CORE STATE ACCESS =====

def get_dungeon_state() -> Dict[str, Any]:
    """Get the full dungeon state (includes hidden info - backend use only)"""
    return GlobalVariable.get(DUNGEON_STATE_KEY, dict(_EMPTY_STATE))

def save_dungeon_state(state: Dict[str, Any]) -> None:
    """Persist the full dungeon state"""
    GlobalVariable.set(DUNGEON_STATE_KEY, state)

def is_in_dungeon() -> bool:
    return get_dungeon_state().get('in_dungeon', False)

# ===== DUNGEON RUN LIFECYCLE =====

def start_dungeon(location: Dict[str, Any], paths: Dict[str, Any]) -> None:
    """Begin a dungeon run at a starting location with its first paths"""
    save_dungeon_state({
        'in_dungeon': True,
        'current_location': location,
        'available_paths': paths,
        'active_encounter': None
    })

def exit_dungeon() -> None:
    """End the dungeon run and clear all state"""
    save_dungeon_state(dict(_EMPTY_STATE))

# ===== LOCATION =====

def get_current_location() -> Optional[Dict[str, Any]]:
    return get_dungeon_state().get('current_location')

def set_current_location(location: Dict[str, Any]) -> None:
    state = get_dungeon_state()
    state['current_location'] = location
    save_dungeon_state(state)

# ===== PATHS =====

def get_path(path_id: str) -> Optional[Dict[str, Any]]:
    """Get a single path INCLUDING its hidden event (backend use only)"""
    return get_dungeon_state().get('available_paths', {}).get(path_id)

def set_available_paths(paths: Dict[str, Any]) -> None:
    state = get_dungeon_state()
    state['available_paths'] = paths
    save_dungeon_state(state)

# Fields the player must never see - what waits behind each path
_HIDDEN_PATH_FIELDS = ('event', 'destination')

def get_public_paths() -> Dict[str, Any]:
    """
    Get available paths SAFE to send to the frontend
    Strips the hidden 'event' and 'destination' fields - the player
    must not know what waits behind each path
    """
    paths = get_dungeon_state().get('available_paths', {})
    return {
        path_id: {key: value for key, value in path.items() if key not in _HIDDEN_PATH_FIELDS}
        for path_id, path in paths.items()
    }

# ===== PARTY CONDITIONS (battle damage persists within the run) =====

def get_party_conditions() -> Dict[str, str]:
    """Current conditions of the party for this dungeon run {monster_id: condition}"""
    return get_dungeon_state().get('party_conditions', {})

def set_party_conditions(conditions: Dict[str, str]) -> None:
    state = get_dungeon_state()
    state['party_conditions'] = conditions
    save_dungeon_state(state)

# ===== ACTIVE ENCOUNTER =====

def get_active_encounter() -> Optional[Dict[str, Any]]:
    """Get the active encounter INCLUDING the riddle answer (backend use only)"""
    return get_dungeon_state().get('active_encounter')

def set_active_encounter(encounter: Dict[str, Any]) -> None:
    state = get_dungeon_state()
    state['active_encounter'] = encounter
    save_dungeon_state(state)

def clear_active_encounter() -> None:
    state = get_dungeon_state()
    state['active_encounter'] = None
    save_dungeon_state(state)
