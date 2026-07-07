# Returning Monsters - Remembered Creatures Come Back Changed
# The dedicated 'returning_monster' path event stages a true reunion: the
# monster is TRANSFORMED by what it remembers (code-clamped stat growth,
# maybe an answering ability, a reworded battle line) and its disposition
# routes the encounter. Blend-ins are subtler: a remembered monster simply
# appears in a normal encounter, memories riding its prompt context.

import random
from typing import Any

# How often things return
RETURNING_EVENT_WEIGHT = 0.12   # path event weight, only when the pool is nonempty
BLEND_IN_CHANCE = 0.25          # per normal encounter: swap one fresh slot

# How much stronger a return makes a monster (percent of each stat).
# The LLM picks the WORD; these numbers are code-owned.
RETURN_STAT_TIERS = {
    'slight': 0.03,
    'notable': 0.06,
    'fierce': 0.10
}
# Repeated returns compound the boost... up to a point
RETURN_COUNT_MULTIPLIER_STEP = 0.25
RETURN_COUNT_MULTIPLIER_CAP = 1.5
# ...and a lifetime ceiling per stat keeps grudges from outscaling the game
LIFETIME_RETURN_BOOST_CAP = 0.50

VALID_DISPOSITIONS = ('hostile', 'friendly', 'wary')
MAX_ABILITIES = 6
GRUDGES_AND_BONDS_CAP = 4
BATTLE_LINE_MAX_RATIO = 1.3

def pick_returning_monster():
    """A random eligible remembered monster, or None"""
    from backend.game.memory.manager import eligible_returning_ids
    from backend.models.monster import Monster

    pool = eligible_returning_ids()
    if not pool:
        return None
    return Monster.get_monster_by_id(random.choice(pool))

def maybe_blend_in():
    """
    Roll the blend-in: on success, a remembered monster (as it was - no
    transform; its memories speak through prompt context) to slot into a
    normal encounter. None otherwise.
    """
    if random.random() >= BLEND_IN_CHANCE:
        return None
    return pick_returning_monster()

def stage_reveal(monster) -> None:
    """Announce an EXISTING monster to the frontend and mark it seen
    (new monsters announce themselves via monster.created instead)"""
    from backend.core.events.dungeon_events import emit_dungeon_monster_revealed
    from backend.game.memory.manager import mark_seen

    emit_dungeon_monster_revealed(monster.to_dict())
    mark_seen([monster.id])

def _fallback_disposition(monster_id: int) -> str:
    """When the LLM's disposition is unusable, the dominant memory decides"""
    from backend.models.monster_memory import MonsterMemory

    if MonsterMemory.count_kind(monster_id, 'was_defeated') > 0:
        return 'hostile'
    warm_kinds = ('gave_reward', 'let_party_pass', 'joined_party', 'talked_with_party')
    if any(MonsterMemory.count_kind(monster_id, kind) > 0 for kind in warm_kinds):
        return 'friendly'
    return 'wary'

def transform_returning_monster(monster, workflow_name: str) -> dict[str, Any]:
    """
    The reunion transform: ONE LLM call decides how this monster returns
    (disposition, greeting, how hard it trained, whether it forged an
    answer to its defeat) - then CODE applies every number, clamped.
    Always returns {'disposition', 'greeting', 'monster'}.
    """
    from backend.core.events.monster_events import emit_monster_updated
    from backend.game.memory.manager import build_memory_block, write_memory
    from backend.game.monster.context_builder import build_speaker_block
    from backend.game.state.manager import get_party_summary
    from backend.game.utils import build_and_generate
    from backend.models.monster_memory import MonsterMemory

    return_count = MonsterMemory.count_kind(monster.id, 'returned')

    raw = {}
    try:
        raw = build_and_generate('returning_transform', workflow_name, {
            'monster_details': build_speaker_block(monster),
            'monster_memories': build_memory_block(monster.id),
            'return_count': return_count,
            'party_summary': get_party_summary(),
        })
    except Exception as e:
        print(f"❌ returning_transform failed for {monster.name} - deterministic return: {e}")

    disposition = str(raw.get('disposition', '')).strip().lower()
    if disposition not in VALID_DISPOSITIONS:
        disposition = _fallback_disposition(monster.id)

    greeting = str(raw.get('greeting') or '').strip()
    if not greeting:
        greeting = {
            'hostile': f"{monster.name} remembers you - and this time it is ready.",
            'friendly': f"{monster.name} brightens with recognition as you approach.",
            'wary': f"{monster.name} goes very still. It has not forgotten."
        }[disposition]

    # ----- stat growth: LLM word -> code-owned numbers, twice clamped -----
    tier_word = str(raw.get('stat_boost', '')).strip().lower()
    boost_pct = RETURN_STAT_TIERS.get(tier_word, RETURN_STAT_TIERS['slight'])
    multiplier = min(1 + RETURN_COUNT_MULTIPLIER_STEP * return_count, RETURN_COUNT_MULTIPLIER_CAP)
    boost_pct = boost_pct * multiplier

    applied_pct = 0.0
    lifetime = MonsterMemory.growth_total_pct(monster.id, 'all_stats')
    if lifetime < LIFETIME_RETURN_BOOST_CAP:
        applied_pct = min(boost_pct, LIFETIME_RETURN_BOOST_CAP - lifetime)
        for stat in ('max_health', 'attack', 'defense', 'speed'):
            old_value = getattr(monster, stat) or 0
            setattr(monster, stat, max(old_value + 1, round(old_value * (1 + applied_pct))))
        monster.current_health = monster.max_health

    # ----- battle line: reworded, never much longer -----
    persona = dict(monster.persona or {})
    new_line = str(raw.get('battle_line') or '').strip()
    old_line = str(persona.get('battle_line') or '')
    if new_line and (not old_line or len(new_line) <= int(max(len(old_line), 60) * BATTLE_LINE_MAX_RATIO)):
        persona['battle_line'] = new_line

    # ----- the grudge (or bond) becomes part of who it is -----
    grudge_note = str(raw.get('grudge_note') or '').strip()[:200]
    if grudge_note:
        notes = list(persona.get('grudges_and_bonds') or [])
        notes.append(grudge_note)
        persona['grudges_and_bonds'] = notes[-GRUDGES_AND_BONDS_CAP:]
    monster.persona = persona
    monster.save()

    # ----- an answering ability, when it earned one -----
    new_ability = None
    wants_ability = str(raw.get('new_ability', '')).strip().lower() in ('yes', 'true')
    theme = str(raw.get('ability_theme') or '').strip()
    if wants_ability and theme and len(monster.abilities or []) < MAX_ABILITIES:
        try:
            from backend.game.monster.generator import generate_ability
            defeat = next(
                (m for m in reversed(MonsterMemory.for_monster(monster.id))
                 if m.kind == 'was_defeated'), None
            )
            defeat_note = ''
            if defeat and (defeat.details or {}).get('by'):
                details = defeat.details or {}
                defeat_note = (f" It was once brought down by {details.get('by')} "
                               f"using {details.get('with', 'sheer force')} - "
                               f"it will not fall the same way twice.")
            new_ability = generate_ability(
                monster,
                growth_context=f"Returning to face the party changed: {theme}.{defeat_note}"
            )
        except Exception as e:
            print(f"❌ Answering ability failed for {monster.name}: {e}")

    # ----- the return itself becomes a memory -----
    write_memory(
        monster.id, 'returned',
        f"Returned to face the party, {disposition} and changed by what it remembered.",
        {
            'disposition': disposition,
            'stat': 'all_stats',
            'amount_pct': applied_pct,
            'new_ability': new_ability.name if new_ability else None
        }
    )

    emit_monster_updated(monster.to_dict())

    return {'disposition': disposition, 'greeting': greeting, 'monster': monster}
