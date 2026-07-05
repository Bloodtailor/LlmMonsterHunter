# Dungeon Service - TRUST BOUNDARY: Validation + Delegation
# Validates all inputs and delegates to game logic / workflows
# Single source of truth for dungeon business rules

from typing import Dict, Any
from backend.game.dungeon import manager
from backend.services.validators import validate_party_ready_for_dungeon
from backend.core.utils import error_response, success_response, validate_and_continue
from backend.workflow.workflow_gateway import request_workflow

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

    if manager.get_active_encounter():
        return error_response("Cannot take a path while an encounter is active")

    success, workflow_id = request_workflow(
        workflow_type="choose_path",
        context={"path_id": path_id}
    )

    if success:
        return success_response({'workflow_id': workflow_id})
    else:
        return error_response("Failed to queue choose path workflow")

def answer_riddle(player_answer: str) -> Dict[str, Any]:
    """
    Answer the active riddle with validation
    Trust boundary: validates an encounter is active and the answer is non-empty
    """

    if not manager.is_in_dungeon():
        return error_response("Not currently in a dungeon")

    if not manager.get_active_encounter():
        return error_response("No active encounter to answer")

    if not player_answer or not str(player_answer).strip():
        return error_response("Answer cannot be empty")

    success, workflow_id = request_workflow(
        workflow_type="answer_riddle",
        context={"player_answer": str(player_answer).strip()}
    )

    if success:
        return success_response({'workflow_id': workflow_id})
    else:
        return error_response("Failed to queue answer riddle workflow")

def continue_exploring() -> Dict[str, Any]:
    """
    Generate fresh paths from the current location
    Trust boundary: validates dungeon state, then queues the workflow
    """

    if not manager.is_in_dungeon():
        return error_response("Not currently in a dungeon")

    if manager.get_active_encounter():
        return error_response("Cannot continue while an encounter is active")

    success, workflow_id = request_workflow(workflow_type="continue_exploring")

    if success:
        return success_response({'workflow_id': workflow_id})
    else:
        return error_response("Failed to queue continue exploring workflow")

def get_dungeon_state() -> Dict[str, Any]:
    """
    Get the PUBLIC dungeon state (no hidden events or riddle answers)
    Safe for the frontend - used for state restoration
    """

    state = manager.get_dungeon_state()
    encounter = state.get('active_encounter') or {}

    return success_response({
        'in_dungeon': state.get('in_dungeon', False),
        'current_location': state.get('current_location'),
        'paths': manager.get_public_paths(),
        'active_encounter': {
            'event': encounter.get('event'),
            'monster_id': encounter.get('monster_id'),
            'riddle': encounter.get('riddle')
        } if encounter else None
    })
