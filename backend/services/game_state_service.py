# Game State Service - TRUST BOUNDARY: Validation + Delegation
# Uses new simplified game state manager with thin business logic wrappers
# Handles validation, response formatting, and error handling

from typing import Any

from backend.core.utils import error_response, success_response, validate_and_continue
from backend.game.state import manager as state_manager
from backend.services.validators import (
    validate_monster_exists,
)

# ===== FOLLOWING MONSTERS MANAGEMENT =====


def get_following_monsters() -> dict[str, Any]:
    """Get all monsters currently following the player"""
    try:
        following_data = state_manager.get_following_monsters()

        # Convert to expected API format
        following_details = []
        following_ids = []

        for following_monster in following_data:
            if following_monster.monster:
                following_details.append(following_monster.monster.to_dict())
                following_ids.append(following_monster.monster_id)

        return success_response(
            {
                'following_monsters': {
                    'ids': following_ids,
                    'count': len(following_ids),
                    'details': following_details,
                }
            }
        )

    except Exception as e:
        return error_response(str(e))


def add_following_monster(monster_id: int) -> dict[str, Any]:
    """Add a monster to the following list"""

    # Trust boundary validation - monster exists and isn't already following
    monster_validation = validate_monster_exists(monster_id)
    error_check = validate_and_continue(monster_validation, {'following_count': 0})
    if error_check:
        return error_check

    monster = monster_validation['monster']

    try:
        # Check if already following (business rule)
        from backend.models.following_monsters import FollowingMonster

        if FollowingMonster.is_following(monster_id):
            return error_response(
                f'{monster.name} is already following you',
                following_count=FollowingMonster.get_following_count(),
            )

        # Business logic
        state_manager.add_following_monster(monster_id)

        return success_response(
            {
                'message': f'{monster.name} is now following you',
                'monster': monster.to_dict(),
                'following_count': FollowingMonster.get_following_count(),
            }
        )

    except Exception as e:
        return error_response(str(e))


def remove_following_monster(monster_id: int) -> dict[str, Any]:
    """Remove a monster from the following list"""

    # Trust boundary validation - monster exists
    monster_validation = validate_monster_exists(monster_id)
    error_check = validate_and_continue(monster_validation, {'following_count': 0})
    if error_check:
        return error_check

    monster = monster_validation['monster']

    try:
        # Business logic (idempotent - no error if not following)
        state_manager.remove_following_monster(monster_id)

        from backend.models.active_party import ActiveParty
        from backend.models.following_monsters import FollowingMonster

        return success_response(
            {
                'message': f'{monster.name} is no longer following you',
                'following_count': FollowingMonster.get_following_count(),
                'party_count': ActiveParty.get_party_count(),
            }
        )

    except Exception as e:
        return error_response(str(e))


# ===== ACTIVE PARTY MANAGEMENT =====


def get_active_party() -> dict[str, Any]:
    """Get current active party details"""
    try:
        party_data = state_manager.get_active_party()

        # Convert to expected API format
        party_details = []
        party_ids = []

        for party_member in party_data:
            if party_member.monster:
                party_details.append(party_member.monster.to_dict())
                party_ids.append(party_member.monster_id)

        return success_response(
            {'active_party': {'ids': party_ids, 'count': len(party_ids), 'details': party_details}}
        )

    except Exception as e:
        return error_response(str(e))


def set_active_party(monster_ids: list[int]) -> dict[str, Any]:
    """Set the active party from following monsters"""

    try:
        # Business logic - Note: Your manager returns get_following_monsters() but should probably return get_active_party()
        active_party = state_manager.set_active_party(monster_ids)

        party_names = []

        for party_member in active_party:
            if party_member.monster:
                party_names.append(party_member.monster.name)

        return success_response(
            {
                'message': f'Active party set: {", ".join(party_names)}',
                'active_party': {'ids': monster_ids, 'count': len(monster_ids)},
            }
        )

    except Exception as e:
        return error_response(str(e))


# ===== GLOBAL GAME STATE =====


def get_game_state() -> dict[str, Any]:
    """The high-level save-state summary the title screen reads: has the
    guided opening ever been finished, and what the world holds so far"""
    try:
        from backend.game.dungeon import manager as dungeon_manager
        from backend.models.active_party import ActiveParty
        from backend.models.dungeon_run import DungeonRun
        from backend.models.following_monsters import FollowingMonster
        from backend.models.monster import Monster

        # Anything a player could grieve losing: monsters, finished (or
        # abandoned) runs, or a completed opening. Drives the title
        # screen's erase-the-world confirmation on New Game.
        has_world_data = (
            Monster.query.first() is not None
            or DungeonRun.query.first() is not None
            or state_manager.is_first_run_complete()
        )

        return success_response(
            {
                'first_run_complete': state_manager.is_first_run_complete(),
                'has_world_data': has_world_data,
                'following_count': FollowingMonster.get_following_count(),
                'party_count': ActiveParty.get_party_count(),
                'in_dungeon': dungeon_manager.is_in_dungeon(),
            }
        )
    except Exception as e:
        return error_response(str(e))


def start_new_game() -> dict[str, Any]:
    """
    The New Game promise: erase the world so a new story can begin.
    Refuses while any workflow is queued or running - wiping state out
    from under the sequential worker would strand it mid-story. The
    frontend confirms with the player BEFORE calling this; by the time
    the request arrives, the decision is made.
    """
    try:
        from backend.game.state.new_game import wipe_world
        from backend.models.game_workflow import GameWorkflow

        busy_count = GameWorkflow.query.filter(
            GameWorkflow.status.in_(('pending', 'processing'))
        ).count()
        if busy_count:
            return error_response(
                f'{busy_count} workflow(s) still queued or running - '
                'let the story finish its sentence before starting over'
            )

        deleted = wipe_world()

        return success_response(
            {
                'message': 'The world has been erased - a new story can begin',
                'deleted_rows': deleted,
            }
        )
    except Exception as e:
        return error_response(str(e))


def reset_game_state() -> dict[str, Any]:
    """Reset all game state to initial values (for testing)"""
    try:
        state_manager.reset_game_state()

        return success_response(
            {
                'message': 'Game state reset to initial values',
                'game_state': 'Need to add game state implementation',
            }
        )

    except Exception as e:
        return error_response(str(e))
