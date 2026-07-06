# Monster Context Builder - ONE place a monster becomes LLM prompt text
# Replaces the near-duplicate builders that lived in the dungeon generator,
# battle generator, and state manager.
#
# Multi-monster blocks (party details, battle sides) are TIERED by the
# model's context window (resolve_detail_tier): compact / standard / full.
# Single-speaker dialogue prompts bypass the bin via build_speaker_block -
# one monster's full persona fits even a 4096 window, and chat is the game.
#
# The SECRET never enters tiered blocks (a battle narrator would leak it);
# it appears only in speaker blocks, where the prompt instructs the monster
# to guard it until trust is earned.

from backend.game.utils import resolve_detail_tier

def build_monster_block(monster, tier: str = None, condition: str = None,
                        defending: bool = False, side_label: str = None,
                        include_secret: bool = False, resources: dict = None,
                        memory_lines: list = None) -> str:
    """One monster as an LLM context block at the given detail tier
    (tier=None resolves from the model's context window)"""

    tier = tier or resolve_detail_tier()

    taxonomy = monster.taxonomy or {}
    ecology = monster.ecology or {}
    persona = monster.persona or {}

    side_tag = f" — {side_label}" if side_label else ""
    condition_tag = f", condition: {condition}" if condition else ""
    defending_tag = " [defending]" if defending else ""

    # Reserve levels (stamina/mana), shown only when the caller tracks them
    reserves_line = None
    if resources and (resources.get('stamina') or resources.get('mana')):
        reserves_line = (f"  Reserves: stamina {resources.get('stamina', 'unknown')}, "
                         f"mana {resources.get('mana', 'unknown')}")

    personality = ', '.join(monster.personality_traits or [])
    abilities = "; ".join(
        f"{a.name} ({a.description})" for a in (monster.abilities or [])
    ) or "none"

    # ----- compact: identity, stats, prose, traits, wish, abilities -----
    identity_bits = [bit for bit in (
        monster.rarity,
        ecology.get('size_class'),
        taxonomy.get('type_label') or monster.species
    ) if bit]
    race_label = taxonomy.get('race_label')
    identity_line = " ".join(identity_bits)
    if race_label and race_label != taxonomy.get('type_label'):
        identity_line += f" ({race_label})"
    if monster.party_role:
        identity_line += f", role: {monster.party_role}"

    lines = [
        f"- {monster.name} ({monster.species}){side_tag}{condition_tag}{defending_tag}",
        f"  Identity: {identity_line}" if identity_line else None,
        f"  Stats: health {monster.max_health}, attack {monster.attack}, "
        f"defense {monster.defense}, speed {monster.speed}",
        reserves_line,
        f"  Description: {monster.description}",
        f"  Backstory: {monster.backstory or 'Unknown'}",
        f"  Personality: {personality}" if personality else None,
        f"  Wish: {persona.get('core_wish')}" if persona.get('core_wish') else None,
        f"  Abilities: {abilities}"
    ]

    # What it remembers of the party (returning monsters and blend-ins)
    if memory_lines:
        lines.append("  Remembers the party:")
        lines += [f"    * {line}" for line in memory_lines[:3]]

    # ----- standard: + lineage, way of life, voice, tastes, persuasion rubric -----
    if tier in ('standard', 'full'):
        lines += [
            _lineage_line(taxonomy),
            _way_of_life_line(ecology),
            _mind_line(ecology),
            f"  Voice: {persona.get('speech_style')}" if persona.get('speech_style') else None,
            f"  Battle cry: \"{persona.get('battle_line')}\"" if persona.get('battle_line') else None,
            _pair_line('Likes', persona.get('likes'), 'Dislikes', persona.get('dislikes')),
            _pair_line('Responds well to', persona.get('responds_well_to'),
                       'poorly to', persona.get('responds_poorly_to')),
            f"  Toward strangers: {persona.get('attitude_toward_strangers')}"
            if persona.get('attitude_toward_strangers') else None,
            f"  Would join a party for: {persona.get('recruitment_lever')}"
            if persona.get('recruitment_lever') else None
        ]

    # ----- full: + inner life, bonds, class, origins -----
    if tier == 'full':
        bonds = persona.get('social_bonds') or {}
        goals = ", ".join(persona.get('goals') or [])
        fears = ", ".join(persona.get('fears') or [])
        hobbies = ", ".join(persona.get('hobbies') or [])
        lines += [
            _class_line(monster.class_taxonomy, persona.get('profession')),
            f"  Beliefs: {persona.get('beliefs')}" if persona.get('beliefs') else None,
            f"  Moral character: {persona.get('moral_character')}"
            if persona.get('moral_character') else None,
            f"  Motivations: {persona.get('motivations')}" if persona.get('motivations') else None,
            f"  Goals: {goals}" if goals else None,
            f"  Fears: {fears}" if fears else None,
            f"  Hobbies: {hobbies}" if hobbies else None,
            f"  Drawn to {bonds.get('drawn_to')}; clashes with {bonds.get('clashes_with')}"
            if bonds.get('drawn_to') or bonds.get('clashes_with') else None,
            _origins_line(ecology)
        ]

    if include_secret and persona.get('secret'):
        lines.append(f"  Secret (it guards this - never state it openly): {persona.get('secret')}")

    return "\n".join(line for line in lines if line)

def build_speaker_block(monster, condition: str = None) -> str:
    """The FULL block for a monster that is about to SPEAK in a dialogue
    prompt - always full tier, secret included, regardless of window bin"""

    return build_monster_block(monster, tier='full', condition=condition, include_secret=True)

# ===== LINE HELPERS =====

def _lineage_line(taxonomy: dict):
    if not taxonomy.get('domain'):
        return None
    return ("  Lineage: " + " > ".join(str(taxonomy.get(rank)) for rank in
            ('domain', 'kingdom', 'family', 'genus', 'species') if taxonomy.get(rank)))

def _way_of_life_line(ecology: dict):
    habitat = ecology.get('habitat') or {}
    diet = ecology.get('diet') or {}
    social = ecology.get('social_structure') or {}
    if not (habitat or diet or social):
        return None

    bits = []
    if habitat.get('primary'):
        biomes = ", ".join(habitat.get('biomes') or [])
        bits.append(f"dwells: {habitat['primary']}" + (f" ({biomes})" if biomes else ""))
    if diet.get('feeding_style'):
        note = f" - {diet.get('notes')}" if diet.get('notes') else ""
        bits.append(f"eats: {diet['feeding_style']}{note}")
    if social.get('primary'):
        bits.append(f"social: {social['primary']}")
    return "  Way of life: " + " | ".join(bits) if bits else None

def _mind_line(ecology: dict):
    if not ecology.get('sapience'):
        return None
    communication = ", ".join(ecology.get('communication') or []) or 'unknown'
    elements = ", ".join(ecology.get('elemental_affinities') or [])
    line = f"  Mind: {ecology['sapience']}, communicates by {communication}"
    if elements:
        line += f" | Elements: {elements}"
    return line

def _pair_line(label_a, values_a, label_b, values_b):
    a = ", ".join(values_a or [])
    b = ", ".join(values_b or [])
    if not (a or b):
        return None
    parts = []
    if a:
        parts.append(f"{label_a}: {a}")
    if b:
        parts.append(f"{label_b}: {b}")
    return "  " + " | ".join(parts)

def _class_line(class_taxonomy, profession):
    bits = []
    if class_taxonomy:
        chains = "; ".join(
            " > ".join(p for p in (entry.get('domain'), entry.get('discipline'),
                                   entry.get('specialization')) if p)
            for entry in class_taxonomy
        )
        if chains:
            bits.append(f"Class: {chains}")
    if profession:
        bits.append(f"sees itself as: {profession}")
    return "  " + " | ".join(bits) if bits else None

def _origins_line(ecology: dict):
    bits = [bit for bit in (
        f"came to be: {ecology.get('creation_mechanism')}" if ecology.get('creation_mechanism') else None,
        f"lifecycle: {ecology.get('lifecycle_stage')}" if ecology.get('lifecycle_stage') else None,
        f"active: {ecology.get('activity_cycle')}" if ecology.get('activity_cycle') else None
    ) if bit]
    return "  Origins: " + " | ".join(bits) if bits else None
