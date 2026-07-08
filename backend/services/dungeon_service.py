# Dungeon Service - TRUST BOUNDARY: Validation + Delegation
# Validates all inputs and delegates to game logic / workflows
# Single source of truth for dungeon business rules

from typing import Any, Optional

from backend.core.utils import error_response, success_response, validate_and_continue
from backend.game.battle import manager as battle_manager
from backend.game.battle.constants import PLAYER_TEXT_MAX_CHARS
from backend.game.dungeon import manager
from backend.models.monster import Monster
from backend.services.validators import validate_party_ready_for_dungeon
from backend.workflow.workflow_gateway import request_workflow


def _encounter_blocks_travel(encounter: Optional[dict[str, Any]]) -> bool:
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


def generate_expedition_notices() -> dict[str, Any]:
    """
    Queue the entrance notice board: the LLM writes 2-3 themed expedition
    notices, Python rolls each one's danger word. The player's choice is
    passed back to enter_dungeon as notice_id.
    Trust boundary: the board is only for parties still at home.
    """

    if manager.is_in_dungeon():
        return error_response("Already on an expedition - the notice board is behind you")

    success, workflow_id = request_workflow(workflow_type="generate_expedition_notices")

    if success:
        return success_response({'workflow_id': workflow_id})
    else:
        return error_response("Failed to queue expedition notices workflow")


def begin_first_run() -> dict[str, Any]:
    """
    New Game: queue the opening scene (the wish-granting premise). Always
    available - replaying the opening wipes nothing, and a leftover run
    is NOT a blocker: entering the first dungeon abandons it properly
    (spoils forfeited, log snapshotted) exactly like any re-entry.
    The frontend follows the streamed text, then calls enter_dungeon
    with first_run=true.
    """

    success, workflow_id = request_workflow(workflow_type="begin_first_run")

    if success:
        return success_response({'workflow_id': workflow_id})
    else:
        return error_response("Failed to queue the opening scene workflow")


def enter_dungeon(notice_id: str = None, first_run: bool = False) -> dict[str, Any]:
    """
    Enter dungeon with validation
    Trust boundary: validates party readiness and (when given) that the
    chosen expedition notice is one the board actually posted, then
    queues the workflow with the full validated notice.
    A guided FIRST RUN is the one entry allowed with an EMPTY party -
    the first companion is recruited inside, not brought along.
    """

    if not first_run:
        # Validate party is ready (first runs may start empty-handed)
        party_validation = validate_party_ready_for_dungeon()
        error_check = validate_and_continue(party_validation)
        if error_check:
            return error_check

    context = {}
    if first_run:
        context['first_run'] = True
    elif notice_id:
        from backend.game.dungeon.run_context import get_pending_notice

        notice = get_pending_notice(str(notice_id))
        if not notice:
            return error_response("Unknown expedition notice - generate the board again")
        context['notice'] = notice

    success, workflow_id = request_workflow(workflow_type="enter_dungeon", context=context)

    if success:
        return success_response({'workflow_id': workflow_id})
    else:
        return error_response("Failed to queue enter dungeon workflow")


def choose_path(path_id: str) -> dict[str, Any]:
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
        workflow_type="choose_path", context={"path_id": path_id}
    )

    if success:
        return success_response({'workflow_id': workflow_id})
    else:
        return error_response("Failed to queue choose path workflow")


def respond_to_monster(message: str) -> dict[str, Any]:
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
        workflow_type="respond_to_monster", context={"message": text}
    )

    if success:
        return success_response({'workflow_id': workflow_id})
    else:
        return error_response("Failed to queue respond to monster workflow")


def sneak_past() -> dict[str, Any]:
    """
    Attempt to sneak past the monsters spotted while exploring
    Trust boundary: validates an explore encounter with monsters present
    """

    if not manager.is_in_dungeon():
        return error_response("Not currently in a dungeon")

    encounter = manager.get_active_encounter()
    if (
        not encounter
        or encounter.get('event') != 'location_explore'
        or not encounter.get('monster_ids')
    ):
        return error_response("There are no monsters to sneak past")

    success, workflow_id = request_workflow(workflow_type="sneak_past")

    if success:
        return success_response({'workflow_id': workflow_id})
    else:
        return error_response("Failed to queue sneak past workflow")


def surprise_attack() -> dict[str, Any]:
    """
    Spring a surprise attack on the monsters spotted while exploring
    Trust boundary: validates an explore encounter with monsters present
    """

    if not manager.is_in_dungeon():
        return error_response("Not currently in a dungeon")

    encounter = manager.get_active_encounter()
    if (
        not encounter
        or encounter.get('event') != 'location_explore'
        or not encounter.get('monster_ids')
    ):
        return error_response("There are no monsters to ambush")

    success, workflow_id = request_workflow(workflow_type="surprise_attack")

    if success:
        return success_response({'workflow_id': workflow_id})
    else:
        return error_response("Failed to queue surprise attack workflow")


def setup_camp() -> dict[str, Any]:
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


def use_ability(
    monster_id: Any,
    ability_id: Any,
    target_type: str = None,
    target_id: Any = None,
    target_text: str = None,
) -> dict[str, Any]:
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

    target_error, target_type, target_id = _validate_dungeon_target(
        target_type, target_id, target_text
    )
    if target_error:
        return target_error

    success, workflow_id = request_workflow(
        workflow_type="use_dungeon_ability",
        context={
            "monster_id": monster_id,
            "ability_id": ability_id,
            "target_type": target_type,
            "target_id": target_id,
            "target_text": str(target_text or '').strip(),
        },
    )

    if success:
        return success_response({'workflow_id': workflow_id})
    else:
        return error_response("Failed to queue use ability workflow")


def use_item(
    item_id: Any, target_type: str = None, target_id: Any = None, target_text: str = None
) -> dict[str, Any]:
    """
    The party uses an inventory item on anything, outside battle
    Trust boundary: validates the item and the target
    (during battle, items cost a turn - use the battle turn instead)
    """

    if not manager.is_in_dungeon():
        return error_response("Not currently in a dungeon")

    if battle_manager.is_in_battle():
        return error_response("During a battle, items are used on a monster's turn")

    try:
        item_id = int(item_id)
    except (TypeError, ValueError):
        return error_response("item_id must be a number")

    from backend.models.item import Item

    item = Item.get_item_by_id(item_id)
    if not item or item.uses_remaining < 1:
        return error_response("That item is not in the party's inventory")

    target_error, target_type, target_id = _validate_dungeon_target(
        target_type, target_id, target_text
    )
    if target_error:
        return target_error

    success, workflow_id = request_workflow(
        workflow_type="use_dungeon_item",
        context={
            "item_id": item_id,
            "target_type": target_type,
            "target_id": target_id,
            "target_text": str(target_text or '').strip(),
        },
    )

    if success:
        return success_response({'workflow_id': workflow_id})
    else:
        return error_response("Failed to queue use item workflow")


def _validate_dungeon_target(target_type: str, target_id: Any, target_text: str):
    """Shared out-of-battle target validation for abilities and items.
    Returns (error_response|None, normalized_target_type, normalized_target_id)"""

    target_type = str(target_type or 'location')
    if target_type not in ('path', 'monster', 'location', 'custom'):
        return (
            error_response("Invalid target type. Valid: path, monster, location, custom"),
            target_type,
            target_id,
        )

    if target_type == 'path':
        if not target_id or not manager.get_path(str(target_id)):
            return error_response("This target needs a valid path"), target_type, target_id
    elif target_type == 'monster':
        try:
            target_id = int(target_id)
        except (TypeError, ValueError):
            return error_response("This target needs a valid monster id"), target_type, target_id
        if not Monster.get_monster_by_id(target_id):
            return error_response("Unknown target monster"), target_type, target_id
    elif target_type == 'custom':
        text = str(target_text or '').strip()
        if not text:
            return error_response("A custom target needs a description"), target_type, target_id
        if len(text) > PLAYER_TEXT_MAX_CHARS:
            return (
                error_response(
                    f"Target description too long (max {PLAYER_TEXT_MAX_CHARS} characters)"
                ),
                target_type,
                target_id,
            )

    return None, target_type, target_id


def continue_exploring() -> dict[str, Any]:
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


def get_dungeon_state() -> dict[str, Any]:
    """
    Get the PUBLIC dungeon state (no hidden path events or destinations)
    Safe for the frontend - used for state restoration
    """

    state = manager.get_dungeon_state()
    encounter = state.get('active_encounter') or {}

    return success_response(
        {
            'in_dungeon': state.get('in_dungeon', False),
            'current_location': state.get('current_location'),
            'paths': manager.get_public_paths(),
            'party_conditions': state.get('party_conditions', {}),
            'party_resources': state.get('party_resources', {}),
            'active_encounter': {
                'event': encounter.get('event'),
                'monster_ids': encounter.get('monster_ids', []),
                'monsters_present': encounter.get('monsters_present'),
                'camped': encounter.get('camped'),
                'dialogue': encounter.get('dialogue', []),
            }
            if encounter
            else None,
        }
    )


def abandon_run(interrupted: bool = False) -> dict[str, Any]:
    """
    Call the party home mid-run: the active run closes as 'abandoned'
    (its log is snapshotted first so home-base chats can still look back
    on it), any battle ends, and the run state is wiped. Synchronous -
    no LLM. Safe to call when not in a dungeon (quiet no-op), so the
    frontend can use it to clear stale run state.

    interrupted=True is the title screen's Continue sweeping a run the
    player never finished (the session died mid-run): same mechanics,
    but the story says an unknown force struck the party down.
    """

    from backend.game.battle import manager as battle_manager
    from backend.game.dungeon.spoils import forfeit_run_spoils
    from backend.models.dungeon_run import DungeonRun

    if not manager.is_in_dungeon():
        return success_response({'abandoned': False, 'in_dungeon': False})

    # The interruption joins the run's story BEFORE the forfeit adds its
    # costs and the snapshot freezes the log - chats can look back on it
    if interrupted:
        manager.append_dungeon_log(
            'An unknown force overwhelmed the expedition - the party\'s '
            'memory of the run ends abruptly, and they woke safe at the '
            'home base with empty hands.'
        )

    # Walking away is not exiting alive - this run's provisional
    # recruits and possessions stay behind (memories remain)
    spoils_lost = forfeit_run_spoils('abandoned')

    manager.snapshot_last_run_log('abandoned')
    DungeonRun.close('abandoned')
    battle_manager.end_battle()
    manager.exit_dungeon()

    return success_response({'abandoned': True, 'in_dungeon': False, 'spoils_lost': spoils_lost})
