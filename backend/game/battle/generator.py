# Battle Generator - LLM calls for battle narration and refereeing
# Small structured judgments only: the LLM never simulates the battle,
# it narrates one action at a time and picks an impact word.
# Every call has a deterministic fallback - a bad LLM response
# can never crash a battle.

import random
from typing import Dict, Any, List, Optional
from backend.game.utils import build_and_generate, build_and_stream
from backend.game.state.manager import get_party_summary
from backend.game.battle.constants import IMPACT_STEPS, INCAPACITATED

# ===== CONTEXT BUILDERS =====

def build_monster_battle_details(monster, entry: Dict[str, Any]) -> str:
    """One monster as LLM context: identity, condition, and abilities"""

    personality = ', '.join(monster.personality_traits or []) if monster else ''
    abilities = "; ".join(
        f"{a.name} ({a.description})" for a in (monster.abilities if monster else [])
    ) or "none"

    defending = " [defending]" if entry.get('defending') else ""

    return (
        f"- {monster.name} ({monster.species}), condition: {entry.get('condition', 'fresh')}{defending}\n"
        f"  Description: {monster.description}\n"
        f"  Personality: {personality}\n"
        f"  Abilities: {abilities}"
    )

def build_side_details(monsters: Dict[str, Any], entries: Dict[str, Dict[str, Any]]) -> str:
    """A whole side as LLM context - monsters is {id(str): Monster}"""

    lines = []
    for monster_id, entry in entries.items():
        monster = monsters.get(monster_id)
        if monster:
            lines.append(build_monster_battle_details(monster, entry))
    return "\n".join(lines) if lines else "None"

def build_battle_situation(state: Dict[str, Any]) -> str:
    """Compact condition summary of both sides"""

    def side_line(side_name, side):
        return f"{side_name}: " + ", ".join(
            f"{m.get('name')} ({m.get('condition')}{', defending' if m.get('defending') else ''})"
            for m in side.values()
        )

    return (
        side_line("Party", state.get('allies', {})) + "\n" +
        side_line("Hostiles", state.get('enemies', {}))
    )

def build_recent_log(state: Dict[str, Any]) -> str:
    log = state.get('recent_log', [])
    return "\n".join(log) if log else "The battle has just begun."

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

    try:
        return build_and_generate('battle_intro', workflow_name, {
            'location_name': location.get('name', 'Unknown Location'),
            'enemy_details': enemy_details,
            'party_details': party_details
        })
    except Exception:
        return "The creatures block your path, and their intent is unmistakable: there will be a fight."

def generate_enemy_actions(state: Dict[str, Any], enemy_details: str, ally_details: str, workflow_name: str) -> List[Dict[str, Any]]:
    """
    Choose actions for the enemy side - returns RAW LLM action entries
    (validation and name resolution happen in the workflow, which knows
    the real monsters)
    """

    try:
        result = build_and_generate('enemy_actions', workflow_name, {
            'round': state.get('round', 1),
            'enemy_details': enemy_details,
            'ally_details': ally_details,
            'recent_log': build_recent_log(state)
        })
        actions = result.get('actions')
        return actions if isinstance(actions, list) else []
    except Exception:
        return []

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

def generate_battle_outcome_text(
    outcome: str,
    location: Dict[str, Any],
    party_details: str,
    enemy_details: str,
    state: Dict[str, Any],
    workflow_name: str
) -> str:
    """Victory or defeat narration"""

    template = 'battle_victory' if outcome == 'victory' else 'battle_defeat'
    fallback = (
        "The last of the hostile creatures falls, and the party stands victorious among the settling dust."
        if outcome == 'victory'
        else "Overwhelmed, the party gathers their fallen companions and retreats from the dungeon, alive but defeated."
    )

    try:
        return build_and_generate(template, workflow_name, {
            'location_name': location.get('name', 'Unknown Location'),
            'party_details': party_details,
            'enemy_details': enemy_details,
            'recent_log': build_recent_log(state)
        })
    except Exception:
        return fallback
