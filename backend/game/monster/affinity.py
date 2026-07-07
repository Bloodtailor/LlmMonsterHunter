# Affinity - how deeply a monster trusts the party (word ladder, naturally)
# Stored on the monster, moved ONE step at a time by code-visible events;
# the LLM never chooses affinity - it only reads the word. The headline
# effect: a WARY monster acts on its own in battle (battle/turn/autonomy.py)
# - trust is earned, not assumed. Devoted monsters get a friendlier
# referee; affinity also rides chat and evolution context.

from typing import Any, Optional

AFFINITY_LADDER = ('wary', 'familiar', 'trusting', 'devoted')

# New recruits start here: your newest companion fights beside you, not
# FOR you - the bond has to be earned (locked decision, game-loop-v1)
DEFAULT_AFFINITY = 'wary'

# THE VALVE: in-run events (heals, camp, exit) can move affinity at most
# this many steps per run - a single run never buys full devotion
MAX_AFFINITY_STEPS_PER_RUN = 2

# How each tier reads inside prompt context blocks
AFFINITY_FLAVOR = {
    'wary': (
        'wary - it fights beside the party on its own terms and does not '
        'yet take commands'
    ),
    'familiar': 'familiar - it has begun to trust the party\'s judgment',
    'trusting': 'trusting - it follows the party\'s lead readily',
    'devoted': 'devoted - it would give everything for this party',
}


def get_affinity(monster) -> str:
    """The monster's affinity tier (unset/unknown reads as wary)"""
    tier = getattr(monster, 'affinity', None)
    return tier if tier in AFFINITY_LADDER else DEFAULT_AFFINITY


def is_autonomous(monster) -> bool:
    """Does this monster ignore commands and act on its own in battle?"""
    return get_affinity(monster) == 'wary'


def affinity_context_line(monster) -> str:
    """One line for prompt context blocks"""
    tier = get_affinity(monster)
    return f"Affinity toward the party: {AFFINITY_FLAVOR[tier]}"


def speaker_block_with_affinity(monster) -> str:
    """A full speaker block + the affinity line - for prompts about a
    monster's OWN voice among the party (home chats, evolution narration)"""
    from backend.game.monster.context_builder import build_speaker_block

    return f"{build_speaker_block(monster)}\n{affinity_context_line(monster)}"


def step_affinity(monster_id: int, reason: str) -> Optional[str]:
    """
    Move a monster ONE step up the ladder for a code-visible event.
    Enforces the per-run valve while a run is active, writes the moment
    into the monster's memory, and announces the change over SSE.
    Returns the new tier, or None when nothing moved. Never raises.
    """
    try:
        from backend.models.monster import Monster

        monster = Monster.get_monster_by_id(int(monster_id))
        if not monster:
            return None

        current = get_affinity(monster)
        index = AFFINITY_LADDER.index(current)
        if index >= len(AFFINITY_LADDER) - 1:
            return None  # already devoted

        if not _consume_run_step_budget(int(monster_id)):
            return None  # this run has given all the trust it can

        new_tier = AFFINITY_LADDER[index + 1]
        monster.affinity = new_tier
        monster.save()

        from backend.game.memory.manager import write_memory

        write_memory(
            int(monster_id),
            'affinity_grew',
            f"Its trust in the party deepened ({_REASON_PROSE.get(reason, reason)}) - "
            f"it now feels {new_tier} toward them.",
            {'reason': reason, 'tier': new_tier},
        )

        from backend.core.events.monster_events import emit_monster_affinity_changed

        emit_monster_affinity_changed(int(monster_id), new_tier, reason)

        print(f"🤝 {monster.name}'s affinity grew: {current} -> {new_tier} ({reason})")
        return new_tier

    except Exception as affinity_error:
        print(f"❌ Affinity step failed for monster {monster_id}: {affinity_error}")
        return None


# How each step reason reads in the memory line
_REASON_PROSE = {
    'healed_by_ally': 'a companion healed it when it was hurting',
    'camp_rest': 'a night around the campfire with the party',
    'rejoined_after_memories': 'it chose the party again, remembering them',
    'survived_run_together': 'walking out of a dungeon alive, together',
    'campfire_chat': 'a long talk back home that meant something',
    'evolved_together': 'the party standing witness to its evolution',
}


def _consume_run_step_budget(monster_id: int) -> bool:
    """
    The per-run valve: while a run is active, each monster may gain at
    most MAX_AFFINITY_STEPS_PER_RUN steps. Outside runs (home-base chats,
    evolution ceremonies) steps are not budgeted.
    """
    from backend.game.dungeon import manager

    state = manager.get_dungeon_state()
    if not state.get('in_dungeon'):
        return True

    steps: dict[str, Any] = state.get('affinity_steps', {})
    used = int(steps.get(str(monster_id), 0))
    if used >= MAX_AFFINITY_STEPS_PER_RUN:
        return False
    steps[str(monster_id)] = used + 1
    state['affinity_steps'] = steps
    manager.save_dungeon_state(state)
    return True
