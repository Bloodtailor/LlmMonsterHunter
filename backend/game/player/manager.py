# Player Character Manager - WHO the player is
# The player character is a real monsters-table row (built by the
# character-creation workflows) plus the GlobalVariable pointer owned
# here. It is a monster like any other except for a short list of
# exemptions, each enforced at its own choke point:
#   - always in the party        (game/state/manager.py prepends it)
#   - never autonomous, no ladder (game/monster/affinity.py)
#   - not a chat target           (game/chat/manager.py)
#   - not followable              (services/game_state_service.py)
#   - not evolvable in v1         (game/monster/evolution.py)
#   - never a returning encounter (game/memory/manager.py)
# EVERY helper tolerates the pointer being unset - a world from before
# this feature keeps working untouched (locked decision,
# docs/plans/new-game-experience.md).

from typing import Optional

from backend.models.global_variables import GlobalVariable
from backend.models.monster import Monster

PLAYER_MONSTER_KEY = 'player_monster_id'


def get_player_monster_id() -> Optional[int]:
    """The player character's monster id, or None when no character
    exists yet (pre-feature worlds, mid-creation moments)"""
    value = GlobalVariable.get(PLAYER_MONSTER_KEY)
    try:
        return int(value) if value is not None else None
    except (TypeError, ValueError):
        return None


def set_player_monster(monster_id: int) -> None:
    """Point the world at its player character (creation workflow only)"""
    GlobalVariable.set(PLAYER_MONSTER_KEY, int(monster_id))


def get_player_monster() -> Optional[Monster]:
    """The player character's monster row, or None (unset pointer, or a
    pointer left dangling by a partial wipe - treated as no player)"""
    player_id = get_player_monster_id()
    return Monster.get_monster_by_id(player_id) if player_id else None


def is_player_monster(monster_id) -> bool:
    """Is this monster THE player character?"""
    player_id = get_player_monster_id()
    try:
        return player_id is not None and int(monster_id) == player_id
    except (TypeError, ValueError):
        return False


def player_exists() -> bool:
    """Does a living player character row exist?"""
    return get_player_monster() is not None
