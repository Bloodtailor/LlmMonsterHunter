# Battle Generator - LLM calls for battle narration and refereeing
# Small structured judgments only: the LLM never simulates the battle,
# it narrates one action at a time and picks an impact word.
# Every call has a deterministic fallback - a bad LLM response
# can never crash a battle.

import random
from typing import Dict, Any, List, Optional
from backend.game.utils import build_and_generate, build_and_stream, clamp_context
from backend.game.state.manager import get_party_summary
from backend.game.battle.constants import IMPACT_STEPS, INCAPACITATED

# ===== CONTEXT BUILDERS =====

# Explicit side tags baked into every monster detail block, so the LLM
# never has to cross-reference names to know who fights for whom
SIDE_LABELS = {
    'allies': "PLAYER'S PARTY",
    'enemies': "HOSTILE ENEMY"
}

def build_monster_battle_details(monster, entry: Dict[str, Any], side: str = None) -> str:
    """One monster as FULL LLM context: identity, SIDE, condition, stats,
    backstory, personality, and abilities - never truncated"""

    personality = ', '.join(monster.personality_traits or []) if monster else ''
    abilities = "; ".join(
        f"{a.name} ({a.description})" for a in (monster.abilities if monster else [])
    ) or "none"

    defending = " [defending]" if entry.get('defending') else ""
    side_tag = f" — {SIDE_LABELS[side]}" if side in SIDE_LABELS else ""

    return (
        f"- {monster.name} ({monster.species}){side_tag}, condition: {entry.get('condition', 'fresh')}{defending}\n"
        f"  Stats: health {monster.max_health}, attack {monster.attack}, defense {monster.defense}, speed {monster.speed}\n"
        f"  Description: {monster.description}\n"
        f"  Backstory: {monster.backstory or 'Unknown'}\n"
        f"  Personality: {personality}\n"
        f"  Abilities: {abilities}"
    )

def build_side_details(monsters: Dict[str, Any], entries: Dict[str, Dict[str, Any]], side: str = None) -> str:
    """A whole side as LLM context - monsters is {id(str): Monster}"""

    lines = []
    for monster_id, entry in entries.items():
        monster = monsters.get(monster_id)
        if monster:
            lines.append(build_monster_battle_details(monster, entry, side))
    return "\n".join(lines) if lines else "None"

def build_battle_situation(state: Dict[str, Any]) -> str:
    """Compact condition summary of both sides"""

    def side_line(side_name, side):
        return f"{side_name}: " + ", ".join(
            f"{m.get('name')} ({m.get('condition')}{', defending' if m.get('defending') else ''})"
            for m in side.values()
        )

    return (
        side_line("The player's party", state.get('allies', {})) + "\n" +
        side_line("The hostile enemies", state.get('enemies', {}))
    )

def build_recent_log(state: Dict[str, Any]) -> str:
    log = state.get('recent_log', [])
    if not log:
        return "The battle has just begun."
    return clamp_context('battle_log', "\n".join(log))

# ===== LLM CALLS =====

def generate_battle_arrival_text(location: Dict[str, Any], workflow_name: str) -> int:
    """Queue streamed hostile arrival text - returns generation_id"""

    variables = {
        'party_summary': get_party_summary(),
        'location_name': location.get('name', 'Unknown Location'),
        'location_description': location.get('description', '')
    }
    return build_and_stream('battle_arrival', workflow_name, variables)

def generate_battle_intro(location: Dict[str, Any], enemy_details: str, party_details: str, workflow_name: str) -> str:
    """The enemy group's in-character challenge"""

    from backend.game.dungeon.manager import get_dungeon_log_text

    try:
        return build_and_generate('battle_intro', workflow_name, {
            'location_name': location.get('name', 'Unknown Location'),
            'enemy_details': clamp_context('monster_details', enemy_details),
            'party_details': clamp_context('party_details', party_details),
            'dungeon_log': get_dungeon_log_text()
        })
    except Exception:
        return "The creatures block your path, and their intent is unmistakable: there will be a fight."

def build_combatant_summary(monsters: Dict[str, Any], state: Dict[str, Any]) -> str:
    """
    Compact summary of everyone still in the fight for the turn director:
    side, speed, condition, and HOW LONG each has waited since acting
    (computed in Python - small models cannot infer this from history)
    """
    from backend.game.battle.manager import turns_waiting

    lines = []
    for side, label in (('allies', 'party'), ('enemies', 'hostile')):
        for monster_id, entry in state.get(side, {}).items():
            if entry.get('condition') == 'incapacitated' or entry.get('fled'):
                continue
            monster = monsters.get(monster_id)
            speed = monster.speed if monster else 10
            if str(monster_id) not in state.get('last_acted', {}):
                waiting = "has NOT acted yet this battle"
            else:
                waited = turns_waiting(state, monster_id)
                waiting = "acted just now" if waited == 0 else f"waited {waited} turn(s) since acting"
            lines.append(
                f"- {entry.get('name')} ({label}), speed: {speed}, "
                f"condition: {entry.get('condition')}, {waiting}"
            )
    return "\n".join(lines) if lines else "None"

def build_turn_history(state: Dict[str, Any]) -> str:
    history = state.get('turn_history', [])
    if not history:
        return "No turns have been taken yet."
    lines = []
    for t in history:
        turn_tag = f"Turn {t['turn']} — " if t.get('turn') else ""
        side_tag = f" ({t.get('side')})" if t.get('side') else ""
        lines.append(f"- {turn_tag}{t.get('actor')}{side_tag}: {t.get('action')}")
    return clamp_context('turn_history', "\n".join(lines))

def generate_next_turn(combatant_details: str, state: Dict[str, Any], workflow_name: str) -> Optional[str]:
    """
    The turn director: pure LLM choice of who acts next
    Returns the raw chosen name (validation happens in the workflow)
    """

    try:
        result = build_and_generate('next_turn', workflow_name, {
            'combatant_details': combatant_details,
            'turn_history': build_turn_history(state),
            'recent_log': build_recent_log(state)
        })
        return str(result.get('next', '')).strip() or None
    except Exception:
        return None

def generate_enemy_turn(actor_details: str, ally_details: str, enemy_details: str, state: Dict[str, Any], workflow_name: str) -> Dict[str, Any]:
    """
    One enemy chooses its action (attack/ability/defend/talk/flee)
    Returns the RAW LLM entry (validation happens in the workflow)
    """

    try:
        result = build_and_generate('enemy_turn', workflow_name, {
            'actor_details': actor_details,
            'ally_details': ally_details,
            'enemy_details': enemy_details,
            'recent_log': build_recent_log(state)
        })
        return result if isinstance(result, dict) else {}
    except Exception:
        return {}

def resolve_freeform_action(
    location: Dict[str, Any],
    actor_details: str,
    player_action_text: str,
    player_target: str,
    player_info: str,
    state: Dict[str, Any],
    workflow_name: str
) -> Dict[str, Any]:
    """
    THE REFEREE for player-typed custom actions
    Returns {'possible', 'narration', 'impact', 'impact_target'} - always
    """

    try:
        result = build_and_generate('freeform_action_resolution', workflow_name, {
            'location_name': location.get('name', 'Unknown Location'),
            'actor_details': actor_details,
            'player_action_text': player_action_text,
            'player_target': player_target or 'none specified',
            'player_info': player_info or 'none',
            'battle_situation': build_battle_situation(state),
            'recent_log': build_recent_log(state)
        })

        impact = str(result.get('impact', '')).strip().lower()
        if impact not in IMPACT_STEPS:
            impact = 'none'

        return {
            'possible': bool(result.get('possible')),
            'narration': str(result.get('narration') or 'The chaos of battle swallows the moment - nothing comes of it.'),
            'impact': impact,
            'impact_target': result.get('impact_target')
        }

    except Exception:
        # Can't judge what we can't parse - the moment passes safely
        return {
            'possible': False,
            'narration': 'The chaos of battle swallows the moment - nothing comes of it.',
            'impact': 'none',
            'impact_target': None
        }

VALID_TALK_DECISIONS = ('continue', 'enemies_join', 'enemies_yield', 'enemies_flee', 'party_spared')

def generate_battle_talk(
    location: Dict[str, Any],
    enemy_details: str,
    ally_details: str,
    exchange: str,
    state: Dict[str, Any],
    workflow_name: str
) -> Dict[str, Any]:
    """
    The negotiation adjudicator - the enemies speak and the LLM decides
    whether the exchange changes the battle
    Returns {'response', 'decision'} with a validated decision - always
    """

    try:
        result = build_and_generate('battle_talk', workflow_name, {
            'location_name': location.get('name', 'Unknown Location'),
            'enemy_details': enemy_details,
            'ally_details': ally_details,
            'battle_situation': build_battle_situation(state),
            'recent_log': build_recent_log(state),
            'exchange': exchange
        })

        decision = str(result.get('decision', '')).strip().lower()
        if decision not in VALID_TALK_DECISIONS:
            decision = 'continue'

        return {
            'response': str(result.get('response') or 'The creatures answer only with bared teeth.'),
            'decision': decision
        }

    except Exception:
        return {
            'response': 'The creatures answer only with bared teeth.',
            'decision': 'continue'
        }

def resolve_action(
    location: Dict[str, Any],
    actor_details: str,
    action_description: str,
    target_details: str,
    state: Dict[str, Any],
    workflow_name: str,
    fallback_narration: str
) -> Dict[str, Any]:
    """
    THE REFEREE: narrate one action and judge its impact
    Returns {'narration': str, 'impact': valid impact key} - always
    """

    try:
        result = build_and_generate('action_resolution', workflow_name, {
            'location_name': location.get('name', 'Unknown Location'),
            'actor_details': actor_details,
            'action_description': action_description,
            'target_details': target_details,
            'battle_situation': build_battle_situation(state),
            'recent_log': build_recent_log(state)
        })

        narration = str(result.get('narration') or fallback_narration)
        impact = str(result.get('impact', '')).strip().lower()
        if impact not in IMPACT_STEPS:
            impact = 'light'

        return {'narration': narration, 'impact': impact}

    except Exception:
        # The battle must go on - deterministic fallback
        return {'narration': fallback_narration, 'impact': 'light'}

def generate_turn_vanity_text(actor_details: str, location: Dict[str, Any], state: Dict[str, Any], workflow_name: str) -> int:
    """
    Queue streamed inner-monologue vanity text for the party monster whose
    turn it is - what it feels, thinks, and wants to do (the player still
    decides its actual action). Returns generation_id.
    """
    return build_and_stream('turn_vanity', workflow_name, {
        'location_name': location.get('name', 'the dungeon'),
        'actor_details': actor_details,
        'battle_situation': build_battle_situation(state),
        'recent_log': build_recent_log(state)
    })

def generate_battle_summary(
    outcome: str,
    resolution: str,
    joined_names: List[str],
    location: Dict[str, Any],
    party_details: str,
    enemy_details: str,
    state: Dict[str, Any],
    workflow_name: str
) -> Optional[str]:
    """
    Summarize the whole battle for the DUNGEON log: what happened, who
    fell/fled/joined, and any lasting effects (injuries, lingering debuffs,
    promises made). Returns None on failure - the caller has a
    deterministic fallback.
    """
    try:
        summary = build_and_generate('battle_summary', workflow_name, {
            'location_name': location.get('name', 'Unknown Location'),
            'outcome': outcome,
            'resolution': resolution or 'combat',
            'joined_names': ', '.join(joined_names) if joined_names else 'none',
            'party_details': party_details,
            'enemy_details': enemy_details,
            'recent_log': build_recent_log(state)
        })
        return str(summary).strip() or None
    except Exception:
        return None

def generate_battle_outcome_text(
    outcome: str,
    resolution: str,
    location: Dict[str, Any],
    party_details: str,
    enemy_details: str,
    state: Dict[str, Any],
    workflow_name: str
) -> str:
    """Victory or defeat narration, shaped by how the battle actually ended"""

    from backend.game.dungeon.manager import get_dungeon_log_text

    template = 'battle_victory' if outcome == 'victory' else 'battle_defeat'
    fallback = (
        "The battle is over, and the party stands victorious among the settling dust."
        if outcome == 'victory'
        else "Overwhelmed, the party gathers their fallen companions and retreats from the dungeon, alive but defeated."
    )

    try:
        return build_and_generate(template, workflow_name, {
            'location_name': location.get('name', 'Unknown Location'),
            'resolution': resolution or 'combat',
            'party_details': clamp_context('party_details', party_details),
            'enemy_details': clamp_context('monster_details', enemy_details),
            'dungeon_log': get_dungeon_log_text(),
            'recent_log': build_recent_log(state)
        })
    except Exception:
        return fallback
