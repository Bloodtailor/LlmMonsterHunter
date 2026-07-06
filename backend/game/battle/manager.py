# Battle Manager - Battle State (v2: individual turns)
# Owns the battle state stored in GlobalVariable ('battle_state')
# Python owns all battle truth: conditions, the ladder, defending,
# turn phases, and outcomes. The LLM narrates, judges impacts,
# directs turn order, and adjudicates negotiations.

from typing import Dict, Any, Optional, List
from backend.models.global_variables import GlobalVariable
from backend.game.battle.constants import (
    CONDITION_LADDER,
    INCAPACITATED,
    FRESH,
    IMPACT_STEPS,
    RECENT_LOG_SIZE,
    TURN_HISTORY_SIZE
)

BATTLE_STATE_KEY = 'battle_state'

_EMPTY_STATE = {
    'in_battle': False,
    'phase': None,          # 'ready'|'awaiting_player_turn'|'awaiting_player_response'|'processing'|'victory'|'defeat'
    'turn_count': 0,
    'turn_history': [],     # [{'actor', 'side', 'action'}] - context for the turn-order LLM
    'last_acted': {},       # monster_id(str): turn_count when it last acted - fairness tracking
    'pending_actor': None,  # ally monster_id whose turn awaits player input
    'pending_talk': None,   # {'speaker_id', 'dialogue'} - enemy talk awaiting player response
    'allies': {},           # monster_id(str): {'name', 'condition', 'defending'}
    'enemies': {},          # monster_id(str): {'name', 'condition', 'defending', 'fled'}
    'recent_log': [],
    'resolution': None      # 'combat'|'joined'|'yielded'|'fled'|'spared'
}

# ===== CORE STATE ACCESS =====

def get_battle_state() -> Dict[str, Any]:
    return GlobalVariable.get(BATTLE_STATE_KEY, dict(_EMPTY_STATE))

def save_battle_state(state: Dict[str, Any]) -> None:
    GlobalVariable.set(BATTLE_STATE_KEY, state)

def is_in_battle() -> bool:
    return get_battle_state().get('in_battle', False)

# ===== BATTLE LIFECYCLE =====

def start_battle(ally_conditions: Dict[str, Dict[str, Any]], enemy_entries: Dict[str, Dict[str, Any]]) -> Dict[str, Any]:
    """
    Begin a battle in the 'ready' phase - the first battle_turn call
    (with no player action) runs the opening initiative
    """
    state = dict(_EMPTY_STATE)
    state.update({
        'in_battle': True,
        'phase': 'ready',
        'turn_count': 0,
        'turn_history': [],
        'last_acted': {},
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
                'defending': False,
                'fled': False
            }
            for monster_id, info in enemy_entries.items()
        },
        'recent_log': [],
        'resolution': None
    })
    save_battle_state(state)
    return state

def end_battle() -> None:
    """Clear all battle state"""
    save_battle_state(dict(_EMPTY_STATE))

# ===== PARTICIPANT STATUS =====

def is_incapacitated(state: Dict[str, Any], side: str, monster_id: str) -> bool:
    monster = state.get(side, {}).get(str(monster_id))
    return not monster or monster.get('condition') == INCAPACITATED

def is_out(state: Dict[str, Any], side: str, monster_id: str) -> bool:
    """Out of the fight: incapacitated or fled"""
    monster = state.get(side, {}).get(str(monster_id))
    return not monster or monster.get('condition') == INCAPACITATED or monster.get('fled')

def active_ids(state: Dict[str, Any], side: str) -> List[str]:
    """Everyone on a side still in the fight"""
    return [mid for mid in state.get(side, {}) if not is_out(state, side, mid)]

def mark_fled(state: Dict[str, Any], monster_id: str) -> None:
    """An enemy escapes the battle (in place)"""
    monster = state.get('enemies', {}).get(str(monster_id))
    if monster:
        monster['fled'] = True

# ===== THE CONDITION LADDER =====

def apply_impact(state: Dict[str, Any], side: str, monster_id: str, impact: str) -> Optional[str]:
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

# ===== DEFENDING (lasts until the monster's next turn) =====

def clear_defending(state: Dict[str, Any], side: str, monster_id: str) -> None:
    """A monster's defending stance ends when its next turn begins (in place)"""
    monster = state.get(side, {}).get(str(monster_id))
    if monster:
        monster['defending'] = False

def set_defending(state: Dict[str, Any], side: str, monster_id: str) -> None:
    monster = state.get(side, {}).get(str(monster_id))
    if monster:
        monster['defending'] = True

# ===== TURN TRACKING =====

def record_turn(state: Dict[str, Any], actor_name: str, action: str, actor_id: Any = None, side: str = None) -> None:
    """
    Track who acted (in place): the rolling history for the turn-order
    LLM's context, and per-monster last-acted turns for fairness
    """
    state['turn_count'] = state.get('turn_count', 0) + 1
    history = state.get('turn_history', [])
    history.append({
        'actor': actor_name,
        'side': 'party' if side == 'allies' else 'hostile' if side == 'enemies' else None,
        'action': action
    })
    state['turn_history'] = history[-TURN_HISTORY_SIZE:]

    if actor_id is not None:
        last_acted = state.get('last_acted', {})
        last_acted[str(actor_id)] = state['turn_count']
        state['last_acted'] = last_acted

def turns_waiting(state: Dict[str, Any], monster_id: Any) -> int:
    """How many turns since this monster last acted (whole battle if never)"""
    return state.get('turn_count', 0) - state.get('last_acted', {}).get(str(monster_id), 0)

# ===== ROLLING LOG =====

def append_log(state: Dict[str, Any], narration: str) -> None:
    """Keep the last few narrations as context for the referee (in place)"""
    log = state.get('recent_log', [])
    log.append(narration)
    state['recent_log'] = log[-RECENT_LOG_SIZE:]

# ===== OUTCOME =====

def derive_outcome(state: Dict[str, Any]) -> str:
    """
    Python decides the battle outcome:
    victory when every enemy is incapacitated or fled,
    defeat when every ally is incapacitated
    """
    enemies = state.get('enemies', {})
    allies = state.get('allies', {})

    if enemies and all(
        m.get('condition') == INCAPACITATED or m.get('fled') for m in enemies.values()
    ):
        return 'victory'
    if allies and all(m.get('condition') == INCAPACITATED for m in allies.values()):
        return 'defeat'
    return 'unresolved'

# ===== SNAPSHOT =====

def get_battle_snapshot(state: Optional[Dict[str, Any]] = None) -> Dict[str, Any]:
    """Public battle snapshot for the frontend (nothing hidden in battles)"""
    if state is None:
        state = get_battle_state()
    return {
        'in_battle': state.get('in_battle', False),
        'phase': state.get('phase'),
        'turn_count': state.get('turn_count', 0),
        'pending_actor': state.get('pending_actor'),
        'pending_talk': state.get('pending_talk'),
        'resolution': state.get('resolution'),
        'allies': state.get('allies', {}),
        'enemies': state.get('enemies', {})
    }
