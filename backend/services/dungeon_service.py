# Dungeon Service - TRUST BOUNDARY: Validation + Delegation
# Validates all inputs and delegates to game logic / workflows
# Single source of truth for dungeon business rules

from typing import Dict, Any, Optional
from backend.game.dungeon import manager
from backend.game.battle import manager as battle_manager
from backend.game.battle.constants import PLAYER_TEXT_MAX_CHARS
from backend.services.validators import validate_party_ready_for_dungeon
from backend.core.utils import error_response, success_response, validate_and_continue
from backend.workflow.workflow_gateway import request_workflow
from backend.models.monster import Monster

def _encounter_blocks_travel(encounter: Optional[Dict[str, Any]]) -> bool:
    """
    Does the active encounter demand resolution before the party moves on?
    A conversation in progress or unhandled monsters block travel; an
    explored (monster-free or resolved) area does not.
    """
    if not encounter:
        return False
    if encounter.get('event') == 'monster_dialogue':
        return True
    if encounter.get('event') == 'location_explore':
        return bool(encounter.get('monster_ids'))
    return True

def enter_dungeon() -> Dict[str, Any]:
    """
    Enter dungeon with validation
    Trust boundary: validates party readiness, then queues the workflow
    """

    # Validate party is ready
    party_validation = validate_party_ready_for_dungeon()
    error_check = validate_and_continue(party_validation)
    if error_check:
        return error_check

    success, workflow_id = request_workflow(workflow_type="enter_dungeon")

    if success:
        return success_response({'workflow_id': workflow_id})
    else:
        return error_response("Failed to queue enter dungeon workflow")

def choose_path(path_id: str) -> Dict[str, Any]:
    """
    Choose a path with validation
    Trust boundary: validates dungeon state and path id, then queues the workflow
    """

    if not manager.is_in_dungeon():
        return error_response("Not currently in a dungeon")

    if not path_id or not manager.get_path(path_id):
        available = list(manager.get_public_paths().keys())
        return error_response(f"Invalid path choice. Available: {available}")

    if _encounter_blocks_travel(manager.get_active_encounter()):
        return error_response("Cannot take a path while an encounter demands attention")

    success, workflow_id = request_workflow(
        workflow_type="choose_path",
        context={"path_id": path_id}
    )

    if success:
        return success_response({'workflow_id': workflow_id})
    else:
        return error_response("Failed to queue choose path workflow")

def respond_to_monster(message: str) -> Dict[str, Any]:
    """
    Speak to the encounter monsters (answer their question, keep a
    conversation going, or open talks with monsters found while exploring)
    Trust boundary: validates a talkable encounter and the message text
    """

    if not manager.is_in_dungeon():
        return error_response("Not currently in a dungeon")

    encounter = manager.get_active_encounter()
    if not encounter or not encounter.get('monster_ids'):
        return error_response("No monsters here to talk to")

    if encounter.get('event') not in ('monster_dialogue', 'location_explore'):
        return error_response("The monsters here are not in a talking mood")

    text = str(message or '').strip()
    if not text:
        return error_response("A message is required")
    if len(text) > PLAYER_TEXT_MAX_CHARS:
        return error_response(f"Message too long (max {PLAYER_TEXT_MAX_CHARS} characters)")

    success, workflow_id = request_workflow(
        workflow_type="respond_to_monster",
        context={"message": text}
    )

    if success:
        return success_response({'workflow_id': workflow_id})
    else:
        return error_response("Failed to queue respond to monster workflow")

def sneak_past() -> Dict[str, Any]:
    """
    Attempt to sneak past the monsters spotted while exploring
    Trust boundary: validates an explore encounter with monsters present
    """

    if not manager.is_in_dungeon():
        return error_response("Not currently in a dungeon")

    encounter = manager.get_active_encounter()
    if not encounter or encounter.get('event') != 'location_explore' or not encounter.get('monster_ids'):
        return error_response("There are no monsters to sneak past")

    success, workflow_id = request_workflow(workflow_type="sneak_past")

    if success:
        return success_response({'workflow_id': workflow_id})
    else:
        return error_response("Failed to queue sneak past workflow")

def surprise_attack() -> Dict[str, Any]:
    """
    Spring a surprise attack on the monsters spotted while exploring
    Trust boundary: validates an explore encounter with monsters present
    """

    if not manager.is_in_dungeon():
        return error_response("Not currently in a dungeon")

    encounter = manager.get_active_encounter()
    if not encounter or encounter.get('event') != 'location_explore' or not encounter.get('monster_ids'):
        return error_response("There are no monsters to ambush")

    success, workflow_id = request_workflow(workflow_type="surprise_attack")

    if success:
        return success_response({'workflow_id': workflow_id})
    else:
        return error_response("Failed to queue surprise attack workflow")

def setup_camp() -> Dict[str, Any]:
    """
    Set up camp in a monster-free explore location
    Trust boundary: validates the location is safe and not already camped
    """

    if not manager.is_in_dungeon():
        return error_response("Not currently in a dungeon")

    encounter = manager.get_active_encounter()
    if not encounter or encounter.get('event') != 'location_explore':
        return error_response("This is no place to camp")
    if encounter.get('monster_ids'):
        return error_response("Cannot camp with creatures nearby")
    if encounter.get('camped'):
        return error_response("The party has already camped here")

    success, workflow_id = request_workflow(workflow_type="setup_camp")

    if success:
        return success_response({'workflow_id': workflow_id})
    else:
        return error_response("Failed to queue setup camp workflow")

def use_ability(monster_id: Any, ability_id: Any, target_type: str = None, target_id: Any = None, target_text: str = None) -> Dict[str, Any]:
    """
    A party monster uses an ability on anything, outside battle
    Trust boundary: validates ownership, party membership, and the target
    (during battle, abilities cost a turn - use the battle turn instead)
    """

    if not manager.is_in_dungeon():
        return error_response("Not currently in a dungeon")

    if battle_manager.is_in_battle():
        return error_response("During a battle, abilities are used on the monster's turn")

    try:
        monster_id = int(monster_id)
        ability_id = int(ability_id)
    except (TypeError, ValueError):
        return error_response("monster_id and ability_id must be numbers")

    from backend.game.state.manager import get_party_monster_ids
    if monster_id not in get_party_monster_ids():
        return error_response("Only monsters in the active party can act")

    monster = Monster.get_monster_by_id(monster_id)
    if not monster or not any(a.id == ability_id for a in (monster.abilities or [])):
        return error_response("That monster does not have that ability")

    target_type = str(target_type or 'location')
    if target_type not in ('path', 'monster', 'location', 'custom'):
        return error_response("Invalid target type. Valid: path, monster, location, custom")

    if target_type == 'path':
        if not target_id or not manager.get_path(str(target_id)):
            return error_response("This target needs a valid path")
    elif target_type == 'monster':
        try:
            target_id = int(target_id)
        except (TypeError, ValueError):
            return error_response("This target needs a valid monster id")
        if not Monster.get_monster_by_id(target_id):
            return error_response("Unknown target monster")
    elif target_type == 'custom':
        text = str(target_text or '').strip()
        if not text:
            return error_response("A custom target needs a description")
        if len(text) > PLAYER_TEXT_MAX_CHARS:
            return error_response(f"Target description too long (max {PLAYER_TEXT_MAX_CHARS} characters)")

    success, workflow_id = request_workflow(
        workflow_type="use_dungeon_ability",
        context={
            "monster_id": monster_id,
            "ability_id": ability_id,
            "target_type": target_type,
            "target_id": target_id,
            "target_text": str(target_text or '').strip()
        }
    )

    if success:
        return success_response({'workflow_id': workflow_id})
    else:
        return error_response("Failed to queue use ability workflow")

def continue_exploring() -> Dict[str, Any]:
    """
    Generate fresh paths from the current location
    Trust boundary: validates dungeon state, then queues the workflow
    """

    if not manager.is_in_dungeon():
        return error_response("Not currently in a dungeon")

    if _encounter_blocks_travel(manager.get_active_encounter()):
        return error_response("Cannot continue while an encounter demands attention")

    success, workflow_id = request_workflow(workflow_type="continue_exploring")

    if success:
        return success_response({'workflow_id': workflow_id})
    else:
        return error_response("Failed to queue continue exploring workflow")

def get_debug_context() -> Dict[str, Any]:
    """
    DEVELOPER X-RAY: everything the dungeon/battle LLM prompts are built
    from, produced by the SAME builder functions the generators use - so
    the debug panel shows exactly what the LLM sees. Includes hidden
    information (path events, destinations); never use for game UI.
    """
    from backend.game.dungeon.generator import build_monsters_details, build_party_dungeon_details
    from backend.game.battle.generator import (
        build_battle_situation,
        build_combatant_summary,
        build_turn_history,
        build_recent_log
    )
    from backend.game.state.manager import get_party_summary
    from backend.models.monster import Monster

    dungeon_state = manager.get_dungeon_state()
    encounter = dungeon_state.get('active_encounter') or {}

    encounter_monsters = [
        m for m in (
            Monster.get_monster_by_id(int(mid)) for mid in encounter.get('monster_ids', [])
        ) if m
    ]

    battle_state = battle_manager.get_battle_state()
    battle_monsters = {}
    if battle_state.get('in_battle'):
        for side in ('allies', 'enemies'):
            for monster_id in battle_state.get(side, {}):
                battle_monsters[monster_id] = Monster.get_monster_by_id(int(monster_id))

    return success_response({
        'in_dungeon': dungeon_state.get('in_dungeon', False),
        'current_location': dungeon_state.get('current_location'),

        # The rolling story of the run: raw entries + the budget-clamped
        # text actually injected into every dungeon prompt
        'dungeon_log': {
            'entries': manager.get_dungeon_log_entries(),
            'clamped_text': manager.get_dungeon_log_text()
        },

        # The party exactly as dungeon prompts describe it
        'party': {
            'summary': get_party_summary(),
            'details_text': build_party_dungeon_details(),
            'conditions': dungeon_state.get('party_conditions', {})
        },

        # The active encounter's context blocks
        'encounter': {
            'event': encounter.get('event'),
            'monster_ids': encounter.get('monster_ids', []),
            'monsters_present': encounter.get('monsters_present'),
            'camped': encounter.get('camped'),
            'dialogue_entries': encounter.get('dialogue', []),
            'dialogue_clamped_text': manager.get_encounter_dialogue_text() if encounter else '',
            'monster_details_text': build_monsters_details(encounter_monsters) if encounter_monsters else ''
        } if encounter else None,

        # Paths WITH their hidden events and destinations (the X-ray part)
        'paths_full': dungeon_state.get('available_paths', {}),

        # The battle's context blocks, as the referee/director prompts see them
        'battle': {
            'in_battle': battle_state.get('in_battle', False),
            'phase': battle_state.get('phase'),
            'turn_count': battle_state.get('turn_count', 0),
            'situation_text': build_battle_situation(battle_state),
            'combatant_summary_text': build_combatant_summary(battle_monsters, battle_state),
            'turn_history_text': build_turn_history(battle_state),
            'recent_log_text': build_recent_log(battle_state),
            'recent_log_entries': battle_state.get('recent_log', [])
        } if battle_state.get('in_battle') else {'in_battle': False}
    })

def get_dungeon_state() -> Dict[str, Any]:
    """
    Get the PUBLIC dungeon state (no hidden path events or destinations)
    Safe for the frontend - used for state restoration
    """

    state = manager.get_dungeon_state()
    encounter = state.get('active_encounter') or {}

    return success_response({
        'in_dungeon': state.get('in_dungeon', False),
        'current_location': state.get('current_location'),
        'paths': manager.get_public_paths(),
        'party_conditions': state.get('party_conditions', {}),
        'active_encounter': {
            'event': encounter.get('event'),
            'monster_ids': encounter.get('monster_ids', []),
            'monsters_present': encounter.get('monsters_present'),
            'camped': encounter.get('camped'),
            'dialogue': encounter.get('dialogue', [])
        } if encounter else None
    })
