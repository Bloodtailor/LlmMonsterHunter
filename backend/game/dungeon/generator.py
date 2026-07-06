# Dungeon Generator - SIMPLIFIED: No Validation
# Pure business logic - assumes all inputs are valid
# Eliminates defensive programming completely

from typing import Dict, Any, List
import random
from backend.game.utils import build_and_generate, build_and_stream, clamp_context
from backend.game.state.manager import get_party_summary, get_party_details
from backend.game.dungeon.events import (
    assign_random_event,
    roll_path_count,
    roll_include_exit,
    PATH_OVERGENERATE_COUNT
)

# ===== CONTEXT BUILDERS =====
# All monster-to-text conversion lives in game/monster/context_builder.py;
# these wrappers add dungeon decorations (run conditions) and block clamping.

def build_monster_dungeon_details(monster) -> str:
    """One monster as tiered LLM context for dungeon encounters"""
    from backend.game.monster.context_builder import build_monster_block
    return build_monster_block(monster)

def build_monsters_details(monsters: List[Any]) -> str:
    """Several monsters as one clamped, tier-binned LLM context block"""
    lines = [build_monster_dungeon_details(m) for m in monsters if m]
    return clamp_context('monster_details', "\n".join(lines)) if lines else "None"

def build_speaking_monsters_details(monsters: List[Any]) -> str:
    """Monsters that are about to SPEAK (dialogue encounters): always the
    FULL block including the guarded secret, regardless of the tier bin"""
    from backend.game.monster.context_builder import build_speaker_block
    lines = [build_speaker_block(m) for m in monsters if m]
    return clamp_context('monster_details', "\n".join(lines)) if lines else "None"

def build_party_dungeon_details() -> str:
    """
    The party as tiered LLM context for dungeon prompts, decorated with each
    member's current run condition - so encounter monsters can react to who
    these adventurers truly are (party details are never truncated)
    """
    from backend.game.state.manager import get_party_monster_ids
    from backend.game.dungeon.manager import get_party_conditions
    from backend.game.monster.context_builder import build_monster_block
    from backend.models.monster import Monster

    conditions = get_party_conditions()
    lines = []
    for monster_id in get_party_monster_ids():
        monster = Monster.get_monster_by_id(monster_id)
        if not monster:
            continue
        condition = conditions.get(str(monster_id), 'fresh')
        lines.append(build_monster_block(monster, condition=condition))

    if not lines:
        return "A lone, empty-handed adventurer"
    return clamp_context('party_details', "\n".join(lines))

def _dungeon_log_text() -> str:
    from backend.game.dungeon.manager import get_dungeon_log_text
    return get_dungeon_log_text()
    
def generate_entry_text(workflow_name) -> Dict[str, Any]:
    """Generate entry text - assumes valid party_summary"""
    
    party_summary = get_party_summary()
    variables = {'party_summary': party_summary}
    entry_text_generation_id = build_and_stream('entry_atmosphere', workflow_name, variables)
    
    return entry_text_generation_id

def generate_random_location(workflow_name) -> Dict[str, Any]:
    """Generate location - no validation, fallback on any error"""
    
    try:
        location = build_and_generate('random_location', workflow_name)
    except Exception:
        location = _get_fallback_location()
        
    return location

def generate_location_event_text(location_name: str, workflow_name) -> Dict[str, Any]:
    """Generate event text - assumes valid location_name"""
    
    variables = {'location_name': location_name}
    location_event_text = build_and_generate('location_event', workflow_name, variables)
    
    return location_event_text

def generate_exit_text(party_summary: str, workflow_name) -> Dict[str, Any]:
    """Generate exit text - assumes valid party_summary"""
    
    variables = {'party_summary': party_summary}
    dungeon_exit_text = build_and_generate('exit_narrative', workflow_name, variables)
    
    return dungeon_exit_text

def generate_paths(location: Dict[str, Any], workflow_name: str) -> Dict[str, Dict[str, Any]]:
    """
    Generate the paths leading onward from a location
    One batch LLM call over-generates paths (later entries are more
    creative) and we keep the LAST ones. Every non-exit path gets a
    hidden random event AND a pre-generated destination location, so
    arrival displays instantly when the player chooses it
    """

    paths = {}

    count = roll_path_count()
    include_exit = roll_include_exit()

    # An exit takes one of the rolled slots
    regular_count = count - 1 if include_exit else count

    # One batch call for all paths - over-generated for variety
    generated = []
    try:
        batch = build_and_generate('path_choices', workflow_name, {
            'location_name': location.get('name', 'Unknown Location'),
            'location_description': location.get('description', ''),
            'total_count': PATH_OVERGENERATE_COUNT
        })
        raw_paths = batch.get('paths') or []
        generated = [
            p for p in raw_paths
            if isinstance(p, dict) and p.get('name') and p.get('description')
        ]
    except Exception:
        generated = []

    # Small LLMs repeat themselves early - the later entries are the
    # creative ones, so take from the END of the batch
    chosen = generated[-regular_count:] if len(generated) >= regular_count else list(generated)
    while len(chosen) < regular_count:
        chosen.append(_get_fallback_path())

    for i, path in enumerate(chosen):
        # Pre-generate where this path leads (hidden from the player)
        destination = generate_arrival_location(location, path, workflow_name)

        paths[f'path_{i + 1}'] = {
            'name': path.get('name', 'Mysterious Passage'),
            'description': path.get('description', ''),
            'type': 'path',
            'event': assign_random_event(),
            'destination': destination
        }

    if include_exit:
        variables = {
            'location_name': location.get('name', 'Unknown Location'),
            'location_description': location.get('description', '')
        }

        try:
            exit_path = build_and_generate('exit_path', workflow_name, variables)
        except Exception:
            exit_path = {
                'name': 'Stone Stairway to the Surface',
                'description': 'A familiar stone stairway leading back to the surface and the safety of the outside world.'
            }

        paths[f'path_{regular_count + 1}'] = {
            'name': exit_path.get('name', 'Way Out'),
            'description': exit_path.get('description', ''),
            'type': 'exit',
            'event': None
        }

    return paths

def generate_arrival_location(previous_location: Dict[str, Any], path: Dict[str, Any], workflow_name: str) -> Dict[str, Any]:
    """Generate the location a chosen path leads to, based on where the party came from"""

    variables = {
        'previous_location_name': previous_location.get('name', 'Unknown Location'),
        'previous_location_description': previous_location.get('description', ''),
        'path_name': path.get('name', 'Mysterious Passage'),
        'path_description': path.get('description', '')
    }

    try:
        location = build_and_generate('arrival_location', workflow_name, variables)
    except Exception:
        location = _get_fallback_location()

    return location

def generate_encounter_vanity_text(location: Dict[str, Any], workflow_name: str) -> int:
    """Queue streamed vanity text for arriving where a monster waits - returns generation_id"""

    variables = {
        'party_summary': get_party_summary(),
        'location_name': location.get('name', 'Unknown Location'),
        'location_description': clamp_context('location_description', location.get('description', '')),
        'dungeon_log': _dungeon_log_text()
    }
    encounter_text_generation_id = build_and_stream('encounter_vanity', workflow_name, variables)

    return encounter_text_generation_id

# ===== EXPLORE EVENT GENERATION =====

def generate_look_around_text(location: Dict[str, Any], monsters_present: bool, workflow_name: str) -> int:
    """Queue streamed arrival/look-around text for an explore location - returns generation_id"""

    monsters_hint = (
        "IMPORTANT: There are other creatures in this area. The party SEES them - "
        "end with the party spotting the creatures, who have not noticed the party yet."
        if monsters_present else
        "The area holds no other creatures - the party has this place to themselves."
    )

    variables = {
        'party_summary': get_party_summary(),
        'location_name': location.get('name', 'Unknown Location'),
        'location_description': clamp_context('location_description', location.get('description', '')),
        'dungeon_log': _dungeon_log_text(),
        'monsters_hint': monsters_hint
    }
    return build_and_stream('look_around', workflow_name, variables)

def generate_camp_scene(location: Dict[str, Any], workflow_name: str) -> int:
    """Queue streamed camp vanity dialogue between the party's monsters - returns generation_id"""

    variables = {
        'location_name': location.get('name', 'Unknown Location'),
        'location_description': clamp_context('location_description', location.get('description', '')),
        'party_details': build_party_dungeon_details(),
        'dungeon_log': _dungeon_log_text()
    }
    return build_and_stream('camp_scene', workflow_name, variables)

def judge_sneak_attempt(location: Dict[str, Any], monster_details: str, workflow_name: str) -> Dict[str, Any]:
    """
    THE REFEREE for sneaking past the monsters in an explore location
    Returns {'narration': str, 'success': bool} - always
    """

    try:
        result = build_and_generate('sneak_attempt', workflow_name, {
            'location_name': location.get('name', 'Unknown Location'),
            'location_description': clamp_context('location_description', location.get('description', '')),
            'party_details': build_party_dungeon_details(),
            'monster_details': monster_details,
            'dungeon_log': _dungeon_log_text()
        })
        return {
            'narration': str(result.get('narration') or 'The party slips through the shadows...'),
            'success': bool(result.get('success'))
        }
    except Exception:
        # Can't judge what we can't parse - the monsters notice the party
        return {
            'narration': 'The party creeps forward, but a loose stone betrays them - the creatures turn as one.',
            'success': False
        }

def generate_ambush_intro(location: Dict[str, Any], monster_details: str, workflow_name: str) -> str:
    """Narration for the party springing a surprise attack - always returns text"""

    try:
        return build_and_generate('ambush_intro', workflow_name, {
            'location_name': location.get('name', 'Unknown Location'),
            'party_details': build_party_dungeon_details(),
            'monster_details': monster_details,
            'dungeon_log': _dungeon_log_text()
        })
    except Exception:
        return "The party strikes without warning - the startled creatures whirl to defend themselves!"

def resolve_dungeon_ability(
    location: Dict[str, Any],
    actor_details: str,
    ability_name: str,
    ability_description: str,
    target_description: str,
    secret_knowledge: str,
    workflow_name: str
) -> Dict[str, Any]:
    """
    THE DUNGEON REFEREE for out-of-battle ability use on anything
    Returns {'narration': str, 'effect': validated str} - always
    """

    valid_effects = ('none', 'heal_light', 'heal_major', 'reveal')

    try:
        result = build_and_generate('dungeon_ability_use', workflow_name, {
            'location_name': location.get('name', 'Unknown Location'),
            'location_description': clamp_context('location_description', location.get('description', '')),
            'actor_details': actor_details,
            'ability_name': ability_name,
            'ability_description': ability_description,
            'target_description': target_description,
            'secret_knowledge': secret_knowledge or 'none',
            'dungeon_log': _dungeon_log_text()
        })

        effect = str(result.get('effect', '')).strip().lower()
        if effect not in valid_effects:
            effect = 'none'

        return {
            'narration': str(result.get('narration') or 'Nothing much seems to come of it.'),
            'effect': effect
        }

    except Exception:
        return {
            'narration': f"{ability_name} flares briefly, but the moment passes and nothing seems to change.",
            'effect': 'none'
        }

def resolve_dungeon_item(
    location: Dict[str, Any],
    item,
    target_description: str,
    secret_knowledge: str,
    workflow_name: str
) -> Dict[str, Any]:
    """
    THE DUNGEON REFEREE for out-of-battle ITEM use on anything
    Returns {'narration': str, 'effect': validated str} - always
    """

    valid_effects = ('none', 'heal_light', 'heal_major', 'reveal')

    try:
        result = build_and_generate('dungeon_item_use', workflow_name, {
            'location_name': location.get('name', 'Unknown Location'),
            'location_description': clamp_context('location_description', location.get('description', '')),
            'party_details': build_party_dungeon_details(),
            'item_name': item.name,
            'item_description': item.description,
            'uses_remaining': item.uses_remaining,
            'target_description': target_description,
            'secret_knowledge': secret_knowledge or 'none',
            'dungeon_log': _dungeon_log_text()
        })

        effect = str(result.get('effect', '')).strip().lower()
        if effect not in valid_effects:
            effect = 'none'

        return {
            'narration': str(result.get('narration') or 'Nothing much seems to come of it.'),
            'effect': effect
        }

    except Exception:
        return {
            'narration': f"The party uses {item.name}, but the moment passes and nothing seems to change.",
            'effect': 'none'
        }

# ===== DIALOGUE ENCOUNTER GENERATION =====

def generate_monster_question(location: Dict[str, Any], monster, workflow_name: str) -> Dict[str, Any]:
    """
    The encounter monster greets the party and asks its question
    Returns {'greeting': str, 'question': str} - always
    """

    try:
        result = build_and_generate('monster_question', workflow_name, {
            'location_name': location.get('name', 'Unknown Location'),
            'location_description': clamp_context('location_description', location.get('description', '')),
            'monster_details': build_speaking_monsters_details([monster]),
            'party_details': build_party_dungeon_details(),
            'dungeon_log': _dungeon_log_text()
        })
        greeting = str(result.get('greeting') or '').strip()
        question = str(result.get('question') or '').strip()
        if not question:
            raise Exception('No question generated')
        return {'greeting': greeting, 'question': question}
    except Exception:
        return {
            'greeting': f"{monster.name} blocks the way, eyes fixed on the party.",
            'question': "Why have you come to my domain, and what do you seek here?"
        }

def generate_dialogue_turn(location: Dict[str, Any], monster_details: str, dialogue_history: str, workflow_name: str) -> Dict[str, Any]:
    """
    The monster responds to the party's words and decides the outcome
    Returns {'response': str, 'outcome': validated outcome} - always
    """

    from backend.game.dungeon.outcomes import validate_outcome

    try:
        result = build_and_generate('monster_dialogue_turn', workflow_name, {
            'location_name': location.get('name', 'Unknown Location'),
            'location_description': clamp_context('location_description', location.get('description', '')),
            'monster_details': monster_details,
            'party_details': build_party_dungeon_details(),
            'dialogue_history': dialogue_history,
            'dungeon_log': _dungeon_log_text()
        })
        return {
            'response': str(result.get('response') or 'The monster regards the party in long silence.'),
            'outcome': validate_outcome(result.get('outcome'))
        }
    except Exception:
        # Keep the conversation alive - a broken generation never ends an encounter
        return {
            'response': 'The monster regards the party in long silence, as if weighing their words.',
            'outcome': 'continue_dialogue'
        }

def build_door_choices(loc1: Dict[str, Any], loc2: Dict[str, Any]) -> Dict[str, Dict[str, str]]:
    door_choices = {
        "door_1": {
            "type": "location",
            "name": loc1.get("name", "Unknown Location"),
            "description": loc1.get("description", ""),
        },
        "door_2": {
            "type": "location",
            "name": loc2.get("name", "Unknown Location"),
            "description": loc2.get("description", ""),
        },
        "door_3": {
            "type": "exit",
            "name": "Exit the Dungeon",
            "description": "A familiar stone stairway leading back to the surface and safety of the outside world.",
        },
    }

    return door_choices


def _get_fallback_path() -> Dict[str, str]:
    """Get fallback path - always works"""

    fallback_paths = [
        {
            "name": "Crumbling Archway",
            "description": "A stone archway whose carvings have long worn away, opening into darkness beyond."
        },
        {
            "name": "Narrow Crawlspace",
            "description": "A tight gap between fallen slabs, just wide enough for one adventurer at a time."
        },
        {
            "name": "Iron-Banded Door",
            "description": "A heavy wooden door reinforced with rusted iron bands, slightly ajar."
        },
        {
            "name": "Rope Ladder",
            "description": "A frayed rope ladder descending into an unlit shaft below."
        }
    ]

    return random.choice(fallback_paths)

def _get_fallback_location() -> Dict[str, str]:
    """Get fallback location - always works"""
    
    fallback_locations = [
        {
            "name": "Echoing Cavern", 
            "description": "Ancient stone walls glisten with moisture as your footsteps echo endlessly into the darkness ahead."
        },
        {
            "name": "Crystal Grove", 
            "description": "Luminescent crystals cast dancing shadows across twisted root formations that seem to pulse with inner life."
        },
        {
            "name": "Forgotten Sanctum", 
            "description": "Weathered statues stand sentinel in this abandoned temple, their eyes seeming to follow your every movement."
        },
        {
            "name": "Whispering Chamber", 
            "description": "Strange murmurs drift through the air in this circular room, though no source can be seen."
        },
        {
            "name": "Moonlit Corridor", 
            "description": "Pale light filters down through cracks in the ceiling, illuminating dust motes that dance like tiny spirits."
        }
    ]
    
    return random.choice(fallback_locations)