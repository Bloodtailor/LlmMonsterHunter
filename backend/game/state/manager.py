# Game State Manager - REWRITTEN FOR SIMPLIFIED ARCHITECTURE
# Uses new simplified models: ActiveParty, FollowingMonster, GlobalVariable
# Contains game-specific convenience methods that were moved from GlobalVariable
#
# THE PARTY = the player character (when one exists) + the ActiveParty
# companion rows. The player is PREPENDED at read time, never stored in
# a party row - there is no "remove the player" state to guard against.
# Every party read below goes through get_party_monster_ids(), so
# battles, camps, journals, and prompts all see the player for free.

from typing import Any

from backend.core.utils.console import print_success
from backend.models.active_party import ActiveParty
from backend.models.following_monsters import FollowingMonster
from backend.models.global_variables import GlobalVariable
from backend.models.monster import Monster

# Combatants stay capped at 4 (the pre-player battle tuning): with a
# player character that leaves 3 companion slots; a pre-feature world
# without one keeps all 4 (locked decision, new-game-experience.md)
MAX_COMPANIONS_WITH_PLAYER = 3
MAX_COMPANIONS_WITHOUT_PLAYER = 4


def companion_cap() -> int:
    """How many companion monsters the active party may hold right now"""
    from backend.game.player.manager import player_exists

    return MAX_COMPANIONS_WITH_PLAYER if player_exists() else MAX_COMPANIONS_WITHOUT_PLAYER


def get_following_monsters():

    return FollowingMonster.get_all_following()


def add_following_monster(monster_id: int):

    FollowingMonster.add_follower(monster_id)

    return


def remove_from_party(monster_id: int):

    if ActiveParty.is_in_active_party(monster_id):
        ActiveParty.remove_from_party(monster_id)

    return


def remove_following_monster(monster_id: int):

    if FollowingMonster.is_following(monster_id):
        FollowingMonster.remove_follower(monster_id)
        remove_from_party(monster_id)

    return


def get_active_party():

    return ActiveParty.get_all_party_members()


def set_active_party(monster_ids: list[int]):
    """Replace the COMPANION rows. The player character is stripped
    quietly if handed in - they are always in the party already."""
    from backend.game.player.manager import is_player_monster

    companion_ids = [mid for mid in monster_ids if not is_player_monster(mid)]
    ActiveParty.set_party(companion_ids)

    return get_following_monsters()


def is_party_ready_for_dungeon() -> bool:
    """Ready for the dungeon: a player character alone is a real party;
    a pre-feature world still needs at least one companion"""
    from backend.game.player.manager import player_exists

    return player_exists() or ActiveParty.is_party_ready()


def get_party_summary() -> str:
    """Get a text summary of the current party for display/logging"""

    party_ids = get_party_monster_ids()

    if not party_ids:
        return "No active party"

    party_names = []
    for monster_id in party_ids:
        monster = Monster.get_monster_by_id(monster_id)
        if monster:
            party_names.append(monster.name)

    if len(party_names) == 1:
        return party_names[0]
    elif len(party_names) == 2:
        return f"{party_names[0]} and {party_names[1]}"
    else:
        return f"{', '.join(party_names[:-1])}, and {party_names[-1]}"


def get_party_monster_ids() -> list[int]:
    """IDs of everyone in the active party: the player character first
    (when one exists), then the companion rows in position order"""
    from backend.game.player.manager import get_player_monster_id

    companion_ids = ActiveParty.get_party_monster_ids()
    player_id = get_player_monster_id()
    if player_id is None:
        return companion_ids
    return [player_id] + [mid for mid in companion_ids if mid != player_id]


def get_party_details() -> str:
    """
    The active party as tiered LLM context (shared context builder;
    depth scales with the model's context window). The player character
    leads the block - the LLM should read the party as THEIR party.
    """

    from backend.game.monster.context_builder import build_monster_block
    from backend.game.player.manager import is_player_monster

    party_ids = get_party_monster_ids()

    if not party_ids:
        return "A lone, empty-handed adventurer"

    lines = []
    for monster_id in party_ids:
        monster = Monster.get_monster_by_id(monster_id)
        if monster:
            side_label = 'THE ADVENTURER themself' if is_player_monster(monster_id) else None
            lines.append(build_monster_block(monster, side_label=side_label))

    return "\n".join(lines) if lines else "A lone, empty-handed adventurer"


# ===== FIRST RUN (the guided opening - game/dungeon/first_run.py) =====

FIRST_RUN_COMPLETE_KEY = 'first_run_complete'


def is_first_run_complete() -> bool:
    """Has the guided opening ever been finished? (Gates the title
    screen's Continue button; New Game is always available)"""
    return bool(GlobalVariable.get(FIRST_RUN_COMPLETE_KEY, False))


def set_first_run_complete() -> None:
    GlobalVariable.set(FIRST_RUN_COMPLETE_KEY, True)


def reset_game_state() -> dict[str, Any]:
    """Reset all game state to initial values (for testing)"""

    ActiveParty.clear_party()
    FollowingMonster.clear_all_followers()
    GlobalVariable.clear_all()

    print_success("Game state reset to initial values")

    return
