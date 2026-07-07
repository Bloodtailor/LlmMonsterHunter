# Memory Manager - Writing and Reading Monster Memories
# The single gateway for recording what a monster remembers and for
# turning those memories into LLM prompt context. Writing NEVER raises -
# a lost memory must never break the moment that created it.

from typing import Any

from backend.game.utils.context_limits import clamp_context

# Every kind of moment a monster can remember (monster's perspective)
MEMORY_KINDS = (
    'was_defeated',  # brought down in battle by the party
    'defeated_party',  # stood over the party's defeat
    'joined_party',  # chose to follow the party
    'yielded_to_party',  # conceded the battle
    'fled_from_party',  # ran from the battle
    'spared_party',  # the party spared it / it accepted their surrender
    'let_party_pass',  # allowed the party through peacefully
    'gave_reward',  # gifted the party something
    'punished_party',  # punished the party in a dialogue
    'talked_with_party',  # a conversation worth remembering
    'avoided',  # the party slipped past (vague awareness only)
    'camp',  # a campfire moment (party monsters)
    'growth',  # a growth reflection changed it
    'lesson',  # what defeat taught it (party monsters)
    'returned',  # it came back changed to face the party again
    'evolved',  # an evolution ceremony remade it (deliberately
    # invisible to growth_total_pct - evolution sits
    # outside the growth/return lifetime caps)
    'run_complete',  # it walked out of the dungeon with the party
    'bond_broken',  # it joined mid-run, but the party never carried the
    # bond out alive (defeat/abandonment released it - spoils.py)
    'affinity_grew',  # its trust in the party climbed a tier (affinity.py)
    # Home-base chat kinds (extracted from conversation, source recorded)
    'confided',  # it opened up about itself or its past
    'grew_closer',  # its bond with the adventurer/party deepened
    'shared_lore',  # it passed on knowledge of the world
    'learned_fact',  # valuable information surfaced in the talk
    'voiced_wish',  # a want or goal it spoke aloud (growth reads these)
)


def write_memory(monster_id: int, kind: str, content: str, details: dict[str, Any] = None) -> None:
    """
    Record one memory for a monster, stamped with the current run.
    Never raises - failures print and the game moves on.
    """
    try:
        from backend.game.dungeon import manager as dungeon
        from backend.models.monster_memory import MonsterMemory

        if kind not in MEMORY_KINDS:
            print(f"⚠️ Unknown memory kind '{kind}' - writing anyway")
        if not content or not str(content).strip():
            return

        run_id = dungeon.get_run_id()
        full_details = dict(details or {})

        # Stamp the run number into details so prompt lines can say
        # "[run 3]" without a join at read time
        if run_id and 'run_number' not in full_details:
            from backend.models.dungeon_run import DungeonRun

            run = DungeonRun.get_by_id(run_id)
            if run:
                full_details['run_number'] = run.run_number

        memory = MonsterMemory.add(
            monster_id=monster_id,
            kind=kind,
            content=content,
            details=full_details or None,
            run_id=run_id,
        )

        if memory:
            from backend.core.events.monster_events import emit_monster_memory_added

            emit_monster_memory_added(int(monster_id), memory.to_dict())
    except Exception as e:
        print(f"❌ Failed to write '{kind}' memory for monster {monster_id}: {e}")


def _format_memory_line(memory) -> str:
    """One memory as one prompt line: '[run 3] was_defeated: ...'
    The prefix names the memory's SOURCE: a run, a home-base talk, ..."""
    details = memory.details or {}
    run_number = details.get('run_number')
    if run_number:
        prefix = f"[run {run_number}] "
    elif details.get('source') == 'home_chat':
        after = details.get('after_run_number')
        prefix = f"[a talk at home, after run {after}] " if after else "[a talk at home] "
    else:
        prefix = "[before this journey] "
    return f"{prefix}{memory.kind}: {memory.content}"


def get_memory_lines(monster_id: int, cap: int = 12) -> list[str]:
    """The most recent memories as prompt lines, oldest first"""
    try:
        from backend.models.monster_memory import MonsterMemory

        memories = MonsterMemory.for_monster(monster_id, limit=cap)
        return [_format_memory_line(memory) for memory in memories]
    except Exception as e:
        print(f"❌ Failed to read memories for monster {monster_id}: {e}")
        return []


def build_memory_block(monster_id: int) -> str:
    """A monster's memories as a clamped LLM context block"""
    lines = get_memory_lines(monster_id)
    if not lines:
        return "It has no history with the party - they have never met."
    return clamp_context('monster_memories', "\n".join(f"- {line}" for line in lines))


def compact_memory_lines(monster_id: int, max_lines: int = 3) -> list[str]:
    """
    The few most recent memories, for inline injection into blocks that
    hold several monsters (battle sides, encounter details).
    """
    lines = get_memory_lines(monster_id, cap=max_lines)
    return [line[:220] for line in lines]


def party_memory_lines(monster_id: int) -> list[str]:
    """
    A PARTY member's freshest memories for multi-monster blocks (party
    details, ally battle blocks) - how what it lived and what was said
    at home shapes how it fights and meets other monsters. Tier-gated
    so small context windows stay lean.
    """
    from backend.game.utils.context_limits import resolve_detail_tier

    count_by_tier = {'compact': 1, 'standard': 2, 'full': 3}
    return compact_memory_lines(monster_id, max_lines=count_by_tier.get(resolve_detail_tier(), 1))


# ===== RETURNING-MONSTER ELIGIBILITY =====


def eligible_returning_ids() -> list[int]:
    """
    Monsters that could come back this run: they have at least one
    memory, are fully generated, and are NOT following the party, in
    the active party, or already staged this run.
    """
    try:
        from backend.game.dungeon import manager as dungeon
        from backend.models.active_party import ActiveParty
        from backend.models.following_monsters import FollowingMonster
        from backend.models.monster import Monster
        from backend.models.monster_memory import MonsterMemory

        exclude = set(FollowingMonster.get_following_monster_ids())
        exclude.update(ActiveParty.get_party_monster_ids())
        exclude.update(int(mid) for mid in dungeon.get_seen_monster_ids())

        # The player character has memories like anyone - but they are
        # not in the ActiveParty rows, and they must never walk out of
        # the dark as their own returning encounter
        from backend.game.player.manager import get_player_monster_id

        player_id = get_player_monster_id()
        if player_id is not None:
            exclude.add(player_id)

        candidate_ids = MonsterMemory.monster_ids_with_memories(exclude_ids=exclude)
        eligible = []
        for monster_id in candidate_ids:
            monster = Monster.get_monster_by_id(monster_id)
            if monster and monster.generation_stage == 'complete':
                eligible.append(monster_id)
        return eligible
    except Exception as e:
        print(f"❌ Failed to compute returning-monster pool: {e}")
        return []


def mark_seen(monster_ids: list[int]) -> None:
    """Exclude these monsters from this run's returning/blend-in pools"""
    try:
        from backend.game.dungeon import manager as dungeon

        dungeon.add_seen_monster_ids([int(mid) for mid in monster_ids])
    except Exception as e:
        print(f"❌ Failed to mark monsters as seen: {e}")
