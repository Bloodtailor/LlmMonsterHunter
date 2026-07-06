# Battle Service - TRUST BOUNDARY: Validation + Delegation
# Validates all inputs and delegates to game logic / workflows
# Single source of truth for battle business rules

from typing import Dict, Any, List
from backend.game.battle import manager
from backend.game.battle.constants import INCAPACITATED
from backend.core.utils import error_response, success_response
from backend.workflow.workflow_gateway import request_workflow
from backend.models.monster import Monster

VALID_ACTIONS = ('attack', 'ability', 'defend')

def submit_round(actions: List[Dict[str, Any]]) -> Dict[str, Any]:
    """
    Submit the player's actions for this round with validation
    Trust boundary: validates battle phase, one action per able ally,
    action types, ability ownership, and living targets - then queues
    the battle_round workflow
    """

    state = manager.get_battle_state()

    if not state.get('in_battle'):
        return error_response("Not currently in a battle")

    if state.get('phase') != 'selecting':
        return error_response(f"Battle is not awaiting actions (phase: {state.get('phase')})")

    if not isinstance(actions, list):
        return error_response("actions must be a list")

    allies = state.get('allies', {})
    enemies = state.get('enemies', {})

    able_allies = {
        monster_id for monster_id, entry in allies.items()
        if entry.get('condition') != INCAPACITATED
    }

    seen = set()
    for raw in actions:
        monster_id = str(raw.get('monster_id'))

        if monster_id not in allies:
            return error_response(f"Monster {monster_id} is not in your party for this battle")
        if monster_id not in able_allies:
            return error_response(f"{allies[monster_id].get('name')} is incapacitated and cannot act")
        if monster_id in seen:
            return error_response(f"Duplicate action for {allies[monster_id].get('name')}")
        seen.add(monster_id)

        action = raw.get('action')
        if action not in VALID_ACTIONS:
            return error_response(f"Invalid action '{action}'. Valid: {list(VALID_ACTIONS)}")

        if action == 'ability':
            ability_id = raw.get('ability_id')
            monster = Monster.get_monster_by_id(int(monster_id))
            if not monster or not any(a.id == ability_id for a in monster.abilities):
                return error_response(f"{allies[monster_id].get('name')} does not have that ability")

        if action in ('attack', 'ability'):
            target_id = str(raw.get('target_id')) if raw.get('target_id') is not None else None
            if not target_id or (target_id not in enemies and target_id not in allies):
                return error_response(f"Action for {allies[monster_id].get('name')} needs a valid target")
            # Attacks must aim at living enemies
            if action == 'attack':
                if target_id not in enemies:
                    return error_response("Attacks must target an enemy")
                if enemies[target_id].get('condition') == INCAPACITATED:
                    return error_response(f"{enemies[target_id].get('name')} is already down")

    if seen != able_allies:
        missing = [allies[m].get('name') for m in able_allies - seen]
        return error_response(f"Every able party member needs an action. Missing: {missing}")

    success, workflow_id = request_workflow(
        workflow_type="battle_round",
        context={"actions": actions}
    )

    if success:
        return success_response({'workflow_id': workflow_id})
    else:
        return error_response("Failed to queue battle round workflow")

def get_battle_state() -> Dict[str, Any]:
    """Public battle snapshot - nothing hidden in battles"""
    return success_response({'battle': manager.get_battle_snapshot()})
