# Battle Context Blocks - how battle STATE becomes LLM context text
# Pure text composition, no LLM calls (those live in generator.py).
# The debug X-ray uses these exact builders so the developer panel shows
# byte-for-byte what the referee and director prompts receive.

from typing import Any

from backend.game.utils import clamp_context

# Explicit side tags baked into every monster detail block, so the LLM
# never has to cross-reference names to know who fights for whom
SIDE_LABELS = {'allies': "PLAYER'S PARTY", 'enemies': "HOSTILE ENEMY"}


def build_monster_battle_details(monster, entry: dict[str, Any], side: str = None) -> str:
    """One monster as tiered LLM context with battle decorations: SIDE,
    condition, defending state, and reserve levels (block itself is never
    truncated). The secret never enters battle prompts - the narrator
    would leak it. ENEMIES that have met the party before carry their
    memories in; ALLIES carry a tier-gated line or three of their own
    (home-base talks and past runs shape how they fight - fuller ally
    history still lives in the run journal)."""

    from backend.game.monster.context_builder import build_monster_block

    memory_lines = None
    if side == 'enemies':
        from backend.game.memory.manager import compact_memory_lines

        memory_lines = compact_memory_lines(monster.id)
    elif side == 'allies':
        from backend.game.memory.manager import party_memory_lines

        memory_lines = party_memory_lines(monster.id)

    block = build_monster_block(
        monster,
        condition=entry.get('condition', 'fresh'),
        defending=bool(entry.get('defending')),
        side_label=SIDE_LABELS.get(side),
        resources={'stamina': entry.get('stamina'), 'mana': entry.get('mana')},
        memory_lines=memory_lines,
    )

    # Allies carry their affinity line - the referee reads how deeply
    # this monster trusts the party (devoted plans get the benefit of
    # the doubt; wary ones may hesitate)
    if side == 'allies':
        from backend.game.monster.affinity import affinity_context_line

        block += f"\n{affinity_context_line(monster)}"

    return block


def build_side_details(
    monsters: dict[str, Any], entries: dict[str, dict[str, Any]], side: str = None
) -> str:
    """A whole side as LLM context - monsters is {id(str): Monster}"""

    lines = []
    for monster_id, entry in entries.items():
        monster = monsters.get(monster_id)
        if monster:
            lines.append(build_monster_battle_details(monster, entry, side))
    return "\n".join(lines) if lines else "None"


def build_battle_situation(state: dict[str, Any]) -> str:
    """Compact condition summary of both sides"""

    def member_line(m):
        parts = [m.get('condition')]
        if m.get('defending'):
            parts.append('defending')
        if m.get('stamina') or m.get('mana'):
            parts.append(f"stamina {m.get('stamina')}, mana {m.get('mana')}")
        return f"{m.get('name')} ({', '.join(parts)})"

    def side_line(side_name, side):
        return f"{side_name}: " + ", ".join(member_line(m) for m in side.values())

    return (
        side_line("The player's party", state.get('allies', {}))
        + "\n"
        + side_line("The hostile enemies", state.get('enemies', {}))
    )


def build_recent_log(state: dict[str, Any]) -> str:
    """The battle so far: condensed old turns + recent turns verbatim"""
    from backend.game.utils.rolling_summary import compose_history, covered_count

    summaries = state.get('log_summaries', [])
    log = state.get('recent_log', [])
    return compose_history(
        'battle_log',
        summaries,
        log[covered_count(summaries) :],
        'battle_log',
        empty_text="The battle has just begun.",
    )


def build_combatant_summary(monsters: dict[str, Any], state: dict[str, Any]) -> str:
    """
    Compact summary of everyone still in the fight for the turn director:
    side, speed, condition, and HOW LONG each has waited since acting
    (computed in Python - small models cannot infer this from history)
    """
    from backend.game.battle.manager import turns_waiting

    lines = []
    for side, label in (('allies', 'party'), ('enemies', 'hostile')):
        for monster_id, entry in state.get(side, {}).items():
            if entry.get('condition') == 'incapacitated' or entry.get('fled'):
                continue
            monster = monsters.get(monster_id)
            speed = monster.speed if monster else 10
            if str(monster_id) not in state.get('last_acted', {}):
                waiting = "has NOT acted yet this battle"
            else:
                waited = turns_waiting(state, monster_id)
                waiting = (
                    "acted just now" if waited == 0 else f"waited {waited} turn(s) since acting"
                )
            lines.append(
                f"- {entry.get('name')} ({label}), speed: {speed}, "
                f"condition: {entry.get('condition')}, {waiting}"
            )
    return "\n".join(lines) if lines else "None"


def build_turn_history(state: dict[str, Any]) -> str:
    history = state.get('turn_history', [])
    if not history:
        return "No turns have been taken yet."
    lines = []
    for t in history:
        turn_tag = f"Turn {t['turn']} — " if t.get('turn') else ""
        side_tag = f" ({t.get('side')})" if t.get('side') else ""
        lines.append(f"- {turn_tag}{t.get('actor')}{side_tag}: {t.get('action')}")
    return clamp_context('turn_history', "\n".join(lines))
