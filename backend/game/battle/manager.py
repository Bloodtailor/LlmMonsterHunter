# Battle Manager - Battle State
# Owns the battle state stored in GlobalVariable ('battle_state')
# Python owns all battle truth: conditions, the ladder, defending,
# turn phases, and victory/defeat. The LLM only narrates and judges impacts.

from typing import Dict, Any, Optional, List
from backend.models.global_variables import GlobalVariable
from backend.game.battle.constants import (
    CONDITION_LADDER,
    INCAPACITATED,
    FRESH,
    IMPACT_STEPS,
    RECENT_LOG_SIZE
)

BATTLE_STATE_KEY = 'battle_state'

_EMPTY_STATE = {
    'in_battle': False,
    'round': 0,
    'phase': None,          # 'selecting' | 'processing' | 'victory' | 'defeat'
    'allies': {},           # monster_id(str): {'name', 'condition', 'defending'}
    'enemies': {},
    'recent_log': []        # rolling narration context for the referee
}

# ===== CORE STATE ACCESS =====

def get_battle_state() -> Dict[str, Any]:
    return GlobalVariable.get(BATTLE_STATE_KEY, dict(_EMPTY_STATE))

def save_battle_state(state: Dict[str, Any]) -> None:
    GlobalVariable.set(BATTLE_STATE_KEY, state)

def is_in_battle() -> bool:
    return get_battle_state().get('in_battle', False)

# ===== BATTLE LIFECYCLE =====

def start_battle(ally_conditions: Dict[str, str], enemy_entries: Dict[str, Dict[str, Any]]) -> Dict[str, Any]:
    """
    Begin a battle
    ally_conditions: {monster_id: condition} carried in from the dungeon run
    enemy_entries: {monster_id: {'name': ...}} for the generated enemies
    """
    state = {
        'in_battle': True,
        'round': 1,
        'phase': 'selecting',
        'allies': {
            str(monster_id): {
                'name': info.get('name', f'Monster {monster_id}'),
                'condition': info.get('condition', FRESH),
                'defending': False
            }
            for monster_id, info in ally_conditions.items()
        },
        'enemies': {
            str(monster_id): {
                'name': info.get('name', f'Monster {monster_id}'),
                'condition': FRESH,
                'defending': False
            }
            for monster_id, info in enemy_entries.items()
        },
        'recent_log': []
    }
    save_battle_state(state)
    return state

def end_battle() -> None:
    """Clear all battle state"""
    save_battle_state(dict(_EMPTY_STATE))

def set_phase(phase: str) -> None:
    state = get_battle_state()
    state['phase'] = phase
    save_battle_state(state)

def next_round() -> None:
    state = get_battle_state()
    state['round'] = state.get('round', 0) + 1
    state['phase'] = 'selecting'
    save_battle_state(state)

# ===== THE CONDITION LADDER =====

def apply_impact(state: Dict[str, Any], side: str, monster_id: str, impact: str) -> str:
    """
    Apply a referee impact judgment to a monster's condition (in place)
    Defending downgrades harmful impacts one step. Clamped at ladder ends.
    Returns the monster's new condition.
    """
    monster = state.get(side, {}).get(str(monster_id))
    if not monster:
        return None

    steps = IMPACT_STEPS.get(impact, 0)

    # Defend rule: a defending monster shrugs off one step of harm
    if steps > 0 and monster.get('defending'):
        steps -= 1

    current_index = CONDITION_LADDER.index(monster.get('condition', FRESH))
    new_index = max(0, min(len(CONDITION_LADDER) - 1, current_index + steps))
    monster['condition'] = CONDITION_LADDER[new_index]

    return monster['condition']

def is_incapacitated(state: Dict[str, Any], side: str, monster_id: str) -> bool:
    monster = state.get(side, {}).get(str(monster_id))
    return not monster or monster.get('condition') == INCAPACITATED

# ===== DEFENDING =====

def clear_defending_all(state: Dict[str, Any]) -> None:
    """Defending lasts one round - clear everyone (in place)"""
    for side in ('allies', 'enemies'):
        for monster in state.get(side, {}).values():
            monster['defending'] = False

def set_defending(state: Dict[str, Any], side: str, monster_id: str) -> None:
    monster = state.get(side, {}).get(str(monster_id))
    if monster:
        monster['defending'] = True

# ===== ROLLING LOG =====

def append_log(state: Dict[str, Any], narration: str) -> None:
    """Keep the last few narrations as context for the referee (in place)"""
    log = state.get('recent_log', [])
    log.append(narration)
    state['recent_log'] = log[-RECENT_LOG_SIZE:]

# ===== OUTCOME =====

def derive_outcome(state: Dict[str, Any]) -> str:
    """
    Python decides the battle outcome from conditions:
    victory if all enemies are down, defeat if all allies are down
    """
    enemies = state.get('enemies', {}).values()
    allies = state.get('allies', {}).values()

    if enemies and all(m.get('condition') == INCAPACITATED for m in enemies):
        return 'victory'
    if allies and all(m.get('condition') == INCAPACITATED for m in allies):
        return 'defeat'
    return 'unresolved'

# ===== SNAPSHOT =====

def get_battle_snapshot(state: Optional[Dict[str, Any]] = None) -> Dict[str, Any]:
    """Public battle snapshot for the frontend (nothing hidden in battles)"""
    if state is None:
        state = get_battle_state()
    return {
        'in_battle': state.get('in_battle', False),
        'round': state.get('round', 0),
        'phase': state.get('phase'),
        'allies': state.get('allies', {}),
        'enemies': state.get('enemies', {})
    }
