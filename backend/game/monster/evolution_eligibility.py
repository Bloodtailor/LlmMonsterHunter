# Evolution Eligibility - WHO may step up to the altar
# One question, answered in one place for both the service (the trust
# boundary saying yes) and the workflow (re-checking long after the
# queue said yes): why can't this monster evolve right now?
# Split out of evolution.py, which holds the ceremony itself.

from typing import Optional


def evolution_eligibility_error(monster_id: int) -> Optional[str]:
    """
    Why this monster cannot evolve right now, or None if it can.
    Evolution happens at home base: any fully-generated monster on the
    following list (the active party is drawn from it) qualifies, but
    never during a dungeon run - and never the player character (v1
    scope, docs/plans/new-game-experience.md).
    """
    try:
        from backend.game.dungeon import manager as dungeon
        from backend.game.player.manager import is_player_monster
        from backend.models.active_party import ActiveParty
        from backend.models.following_monsters import FollowingMonster
        from backend.models.monster import Monster

        if dungeon.is_in_dungeon():
            return "The party is in the dungeon - evolution waits for home base"

        monster = Monster.get_monster_by_id(int(monster_id))
        if not monster:
            return f"Monster {monster_id} not found"
        if monster.generation_stage != 'complete':
            return f"{monster.name} is still taking shape - try again shortly"

        if is_player_monster(int(monster_id)):
            return f"{monster.name} is the adventurer - their story is not the altar's to rewrite"

        familiar_ids = set(FollowingMonster.get_following_monster_ids())
        familiar_ids.update(ActiveParty.get_party_monster_ids())
        if int(monster_id) not in familiar_ids:
            return f"{monster.name} is not following the party"

        return None
    except Exception as e:
        return f"Could not check evolution eligibility: {e}"
