# Battle Service - TRUST BOUNDARY: Validation + Delegation
# Validates all inputs and delegates to game logic / workflows
# Single source of truth for battle business rules

from typing import Any, Optional

from backend.core.utils import error_response, success_response
from backend.game.battle import manager
from backend.game.battle.constants import INCAPACITATED, PLAYER_TEXT_MAX_CHARS
from backend.models.monster import Monster
from backend.workflow.workflow_gateway import request_workflow

VALID_ACTION_TYPES = ('attack', 'ability', 'defend', 'custom', 'talk', 'item')


def take_turn(action: Optional[dict[str, Any]]) -> dict[str, Any]:
    """
    Take a battle turn with validation
    Phase 'ready': no action needed (opening initiative)
    Phase 'awaiting_player_turn': an action for the pending ally is required
    """

    state = manager.get_battle_state()

    if not state.get('in_battle'):
        return error_response("Not currently in a battle")

    phase = state.get('phase')

    if phase == 'ready':
        # Opening initiative - no action expected
        pass

    elif phase == 'awaiting_player_turn':
        pending_actor = str(state.get('pending_actor'))
        allies = state.get('allies', {})
        enemies = state.get('enemies', {})

        if not action or not isinstance(action, dict):
            return error_response(
                f"It is {allies.get(pending_actor, {}).get('name', 'your monster')}'s turn - an action is required"
            )

        action_type = action.get('type')
        if action_type not in VALID_ACTION_TYPES:
            return error_response(
                f"Invalid action type '{action_type}'. Valid: {list(VALID_ACTION_TYPES)}"
            )

        if action_type == 'ability':
            monster = Monster.get_monster_by_id(int(pending_actor))
            if not monster or not any(a.id == action.get('ability_id') for a in monster.abilities):
                return error_response("That monster does not have that ability")

        if action_type == 'item':
            from backend.models.item import Item

            try:
                item = Item.get_item_by_id(int(action.get('item_id')))
            except (TypeError, ValueError):
                item = None
            if not item or item.uses_remaining < 1:
                return error_response("That item is not in the party's inventory")
            # Target is optional for items; if given it must be a combatant
            target_id = (
                str(action.get('target_id')) if action.get('target_id') is not None else None
            )
            if target_id and target_id not in enemies and target_id not in allies:
                return error_response("This action needs a valid target")

        if action_type in ('attack', 'ability'):
            target_id = (
                str(action.get('target_id')) if action.get('target_id') is not None else None
            )
            if not target_id or (target_id not in enemies and target_id not in allies):
                return error_response("This action needs a valid target")
            if action_type == 'attack':
                if target_id not in enemies:
                    return error_response("Attacks must target an enemy")
                enemy = enemies[target_id]
                if enemy.get('condition') == INCAPACITATED or enemy.get('fled'):
                    return error_response(f"{enemy.get('name')} is already out of the fight")

        if action_type in ('custom', 'talk'):
            text = str(action.get('text') or '').strip()
            if not text:
                return error_response(f"A {action_type} action needs text")
            if len(text) > PLAYER_TEXT_MAX_CHARS:
                return error_response(f"Text too long (max {PLAYER_TEXT_MAX_CHARS} characters)")
            info = str(action.get('info') or '')
            if len(info) > PLAYER_TEXT_MAX_CHARS:
                return error_response(
                    f"Additional info too long (max {PLAYER_TEXT_MAX_CHARS} characters)"
                )

    else:
        return error_response(f"Battle is not awaiting a turn (phase: {phase})")

    success, workflow_id = request_workflow(
        workflow_type="battle_turn", context={"player_action": action, "player_response": None}
    )

    if success:
        return success_response({'workflow_id': workflow_id})
    else:
        return error_response("Failed to queue battle turn workflow")


def respond_to_talk(response: str) -> dict[str, Any]:
    """
    Reply to an enemy's battlefield talk with validation
    Phase must be 'awaiting_player_response'
    """

    state = manager.get_battle_state()

    if not state.get('in_battle'):
        return error_response("Not currently in a battle")

    if state.get('phase') != 'awaiting_player_response':
        return error_response("No enemy is waiting for a response")

    text = str(response or '').strip()
    if not text:
        return error_response("A response is required")
    if len(text) > PLAYER_TEXT_MAX_CHARS:
        return error_response(f"Response too long (max {PLAYER_TEXT_MAX_CHARS} characters)")

    success, workflow_id = request_workflow(
        workflow_type="battle_turn", context={"player_action": None, "player_response": text}
    )

    if success:
        return success_response({'workflow_id': workflow_id})
    else:
        return error_response("Failed to queue battle turn workflow")


def get_battle_state() -> dict[str, Any]:
    """Public battle snapshot - nothing hidden in battles"""
    return success_response({'battle': manager.get_battle_snapshot()})
