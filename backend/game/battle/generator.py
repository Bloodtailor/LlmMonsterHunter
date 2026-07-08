# Battle Generator - LLM calls for battle narration and refereeing
# Small structured judgments only: the LLM never simulates the battle,
# it narrates one action at a time and picks an impact word.
# Every call has a deterministic fallback - a bad LLM response
# can never crash a battle.
# State-to-text composition lives in context_blocks.py; this file owns
# the calls that spend tokens.

from typing import Any, Optional

from backend.game.battle.constants import IMPACT_STEPS, RESOURCE_DELTAS
from backend.game.battle.context_blocks import build_battle_situation, build_recent_log
from backend.game.state.manager import get_party_summary
from backend.game.utils import build_and_generate, build_and_stream, clamp_context


def _validated_resource_delta(raw) -> Optional[str]:
    """
    Validate a referee cost/restore word. None means 'the referee stayed
    silent' - the workflow falls back to the code default for the action.
    """
    word = str(raw or '').strip().lower()
    return word if word in RESOURCE_DELTAS else None


# ===== LLM CALLS =====


def generate_battle_arrival_text(location: dict[str, Any], workflow_name: str) -> int:
    """Queue streamed hostile arrival text - returns generation_id"""

    variables = {
        'party_summary': get_party_summary(),
        'location_name': location.get('name', 'Unknown Location'),
        'location_description': location.get('description', ''),
    }
    return build_and_stream('battle_arrival', workflow_name, variables)


def generate_battle_intro(
    location: dict[str, Any], enemy_details: str, party_details: str, workflow_name: str
) -> str:
    """The enemy group's in-character challenge"""

    from backend.game.dungeon.manager import get_dungeon_log_text

    try:
        return build_and_generate(
            'battle_intro',
            workflow_name,
            {
                'location_name': location.get('name', 'Unknown Location'),
                'enemy_details': clamp_context('monster_details', enemy_details),
                'party_details': clamp_context('party_details', party_details),
                'dungeon_log': get_dungeon_log_text(),
            },
        )
    except Exception:
        return "The creatures block your path, and their intent is unmistakable: there will be a fight."


def generate_next_turn(
    combatant_details: str, state: dict[str, Any], workflow_name: str
) -> Optional[str]:
    """
    The turn director: pure LLM choice of who acts next
    Returns the raw chosen name (validation happens in the workflow)
    """
    from backend.game.battle.context_blocks import build_turn_history

    try:
        result = build_and_generate(
            'next_turn',
            workflow_name,
            {
                'combatant_details': combatant_details,
                'turn_history': build_turn_history(state),
                'recent_log': build_recent_log(state),
            },
        )
        return str(result.get('next', '')).strip() or None
    except Exception:
        return None


def generate_enemy_turn(
    actor_details: str,
    ally_details: str,
    enemy_details: str,
    state: dict[str, Any],
    workflow_name: str,
) -> dict[str, Any]:
    """
    One enemy chooses its action (attack/ability/defend/talk/flee)
    Returns the RAW LLM entry (validation happens in the workflow)
    """

    try:
        result = build_and_generate(
            'enemy_turn',
            workflow_name,
            {
                'actor_details': actor_details,
                'ally_details': ally_details,
                'enemy_details': enemy_details,
                'recent_log': build_recent_log(state),
            },
        )
        return result if isinstance(result, dict) else {}
    except Exception:
        return {}


def generate_ally_autonomous_turn(
    actor_details: str,
    ally_details: str,
    enemy_details: str,
    state: dict[str, Any],
    workflow_name: str,
) -> dict[str, Any]:
    """
    A WARY party monster chooses its own action (attack/ability/defend) -
    it fights beside the party, not for them (game/monster/affinity.py).
    Returns the RAW LLM entry (validation happens in turn/autonomy.py).
    """

    try:
        result = build_and_generate(
            'ally_autonomous_turn',
            workflow_name,
            {
                'actor_details': actor_details,
                'ally_details': ally_details,
                'enemy_details': enemy_details,
                'recent_log': build_recent_log(state),
            },
        )
        return result if isinstance(result, dict) else {}
    except Exception:
        return {}


def resolve_freeform_action(
    location: dict[str, Any],
    actor_details: str,
    player_action_text: str,
    player_target: str,
    player_info: str,
    state: dict[str, Any],
    workflow_name: str,
) -> dict[str, Any]:
    """
    THE REFEREE for player-typed custom actions
    Returns {'possible', 'narration', 'impact', 'impact_target'} - always
    """

    from backend.game.dungeon.run_context import referee_hint

    try:
        result = build_and_generate(
            'freeform_action_resolution',
            workflow_name,
            {
                'location_name': location.get('name', 'Unknown Location'),
                'actor_details': actor_details,
                'player_action_text': player_action_text,
                'player_target': player_target or 'none specified',
                'player_info': player_info or 'none',
                'battle_situation': build_battle_situation(state),
                'recent_log': build_recent_log(state),
                'referee_hint': referee_hint(),
            },
        )

        impact = str(result.get('impact', '')).strip().lower()
        if impact not in IMPACT_STEPS:
            impact = 'none'

        return {
            'possible': bool(result.get('possible')),
            'narration': str(
                result.get('narration')
                or 'The chaos of battle swallows the moment - nothing comes of it.'
            ),
            'impact': impact,
            'impact_target': result.get('impact_target'),
            'stamina_delta': _validated_resource_delta(result.get('stamina_cost')),
            'mana_delta': _validated_resource_delta(result.get('mana_cost')),
        }

    except Exception:
        # Can't judge what we can't parse - the moment passes safely
        return {
            'possible': False,
            'narration': 'The chaos of battle swallows the moment - nothing comes of it.',
            'impact': 'none',
            'impact_target': None,
            'stamina_delta': None,
            'mana_delta': None,
        }


VALID_TALK_DECISIONS = ('continue', 'enemies_join', 'enemies_yield', 'enemies_flee', 'party_spared')


def generate_battle_talk(
    location: dict[str, Any],
    enemy_details: str,
    ally_details: str,
    exchange: str,
    state: dict[str, Any],
    workflow_name: str,
) -> dict[str, Any]:
    """
    The negotiation adjudicator - the enemies speak and the LLM decides
    whether the exchange changes the battle
    Returns {'response', 'decision'} with a validated decision - always
    """

    try:
        result = build_and_generate(
            'battle_talk',
            workflow_name,
            {
                'location_name': location.get('name', 'Unknown Location'),
                'enemy_details': enemy_details,
                'ally_details': ally_details,
                'battle_situation': build_battle_situation(state),
                'recent_log': build_recent_log(state),
                'exchange': exchange,
            },
        )

        decision = str(result.get('decision', '')).strip().lower()
        if decision not in VALID_TALK_DECISIONS:
            decision = 'continue'

        return {
            'response': str(
                result.get('response') or 'The creatures answer only with bared teeth.'
            ),
            'decision': decision,
        }

    except Exception:
        return {'response': 'The creatures answer only with bared teeth.', 'decision': 'continue'}


def resolve_action(
    location: dict[str, Any],
    actor_details: str,
    action_description: str,
    target_details: str,
    state: dict[str, Any],
    workflow_name: str,
    fallback_narration: str,
) -> dict[str, Any]:
    """
    THE REFEREE: narrate one action and judge its impact
    Returns {'narration': str, 'impact': valid impact key} - always
    """

    from backend.game.dungeon.run_context import referee_hint

    try:
        result = build_and_generate(
            'action_resolution',
            workflow_name,
            {
                'location_name': location.get('name', 'Unknown Location'),
                'actor_details': actor_details,
                'action_description': action_description,
                'target_details': target_details,
                'battle_situation': build_battle_situation(state),
                'recent_log': build_recent_log(state),
                'referee_hint': referee_hint(),
            },
        )

        narration = str(result.get('narration') or fallback_narration)
        impact = str(result.get('impact', '')).strip().lower()
        if impact not in IMPACT_STEPS:
            # A garbled impact word must never turn a heal into a blow
            # ('heal', 'heal_minor'... land as heal_light; all else is none)
            impact = 'heal_light' if impact.startswith('heal') else 'none'

        return {
            'narration': narration,
            'impact': impact,
            'stamina_delta': _validated_resource_delta(result.get('stamina_cost')),
            'mana_delta': _validated_resource_delta(result.get('mana_cost')),
        }

    except Exception:
        # The battle must go on - deterministic fallback
        return {
            'narration': fallback_narration,
            'impact': 'light',
            'stamina_delta': None,
            'mana_delta': None,
        }


def generate_turn_vanity_text(
    actor_details: str, location: dict[str, Any], state: dict[str, Any], workflow_name: str
) -> int:
    """
    Queue streamed vanity text for the party monster whose turn it is -
    ONE sentence of what it is thinking at this moment (the player still
    decides its actual action). Returns generation_id.
    """
    return build_and_stream(
        'turn_vanity',
        workflow_name,
        {
            'location_name': location.get('name', 'the dungeon'),
            'actor_details': actor_details,
            'battle_situation': build_battle_situation(state),
            'recent_log': build_recent_log(state),
        },
    )


def generate_battle_summary(
    outcome: str,
    resolution: str,
    joined_names: list[str],
    location: dict[str, Any],
    party_details: str,
    enemy_details: str,
    state: dict[str, Any],
    workflow_name: str,
) -> Optional[str]:
    """
    Summarize the whole battle for the DUNGEON log: what happened, who
    fell/fled/joined, and any lasting effects (injuries, lingering debuffs,
    promises made). Returns None on failure - the caller has a
    deterministic fallback.
    """
    try:
        summary = build_and_generate(
            'battle_summary',
            workflow_name,
            {
                'location_name': location.get('name', 'Unknown Location'),
                'outcome': outcome,
                'resolution': resolution or 'combat',
                'joined_names': ', '.join(joined_names) if joined_names else 'none',
                'party_details': party_details,
                'enemy_details': enemy_details,
                'recent_log': build_recent_log(state),
            },
        )
        return str(summary).strip() or None
    except Exception:
        return None


def generate_battle_outcome_text(
    outcome: str,
    resolution: str,
    location: dict[str, Any],
    party_details: str,
    enemy_details: str,
    state: dict[str, Any],
    workflow_name: str,
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
        return build_and_generate(
            template,
            workflow_name,
            {
                'location_name': location.get('name', 'Unknown Location'),
                'resolution': resolution or 'combat',
                'party_details': clamp_context('party_details', party_details),
                'enemy_details': clamp_context('monster_details', enemy_details),
                'dungeon_log': get_dungeon_log_text(),
                'recent_log': build_recent_log(state),
            },
        )
    except Exception:
        return fallback
