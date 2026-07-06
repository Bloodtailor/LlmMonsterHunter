# CMDTS Reference Data - Curated Taxonomy Trees, Dimension Enums, Stat Derivation
# The single source of truth for the Comprehensive Multi-Dimensional Taxonomy System.
# Upper taxonomy ranks are CURATED (the LLM selects from these); lower ranks
# (family/genus/species) are LLM-invented per monster.
# Design reference: docs/plans/monster-depth-cmdts.md §3

import random

# ===== TAXONOMY TREE (curated: Domain -> Kingdom) =====
# Each entry: gloss is a terse description injected into generation prompts.

TAXONOMY_TREE = {
    'Materium': {
        'gloss': 'natural mortal life',
        'kingdoms': {
            'Beast':     'furred, scaled, or feathered animals',
            'Insectoid': 'arthropods and swarming things',
            'Verdant':   'living plant-life',
            'Fungoid':   'fungal and spore life',
            'Oozekind':  'slimes and amorphs',
            'Draconid':  'dragons, drakes, and wyrms',
            'Kinfolk':   'goblinoid and humanoid peoples'
        }
    },
    'Elementum': {
        'gloss': 'element given will',
        'kingdoms': {
            'Primordial': 'raw element embodied',
            'Wispkind':   'minor elemental sprites',
            'Stormkind':  'living weather'
        }
    },
    'Aetherium': {
        'gloss': 'spirit and dream',
        'kingdoms': {
            'Spiritkind': 'nature spirits and ghosts of place',
            'Feykind':    'fey tricksters and courtiers',
            'Dreamborn':  'beings of dream and thought'
        }
    },
    'Caelium': {
        'gloss': 'celestial and astral',
        'kingdoms': {
            'Celestial': 'angelic guardians',
            'Starborn':  'astral and cosmic creatures'
        }
    },
    'Umbrium': {
        'gloss': 'shadow and abyss',
        'kingdoms': {
            'Demonkind': 'fiends of the abyss',
            'Shadekind': 'living shadow',
            'Nightmare': 'fear made flesh'
        }
    },
    'Mortuum': {
        'gloss': 'the risen dead',
        'kingdoms': {
            'Revenant':   'corporeal undead',
            'Wraithkind': 'incorporeal undead'
        }
    },
    'Artificium': {
        'gloss': 'made things',
        'kingdoms': {
            'Construct':  'built automatons and golems',
            'Animatum':   'objects given motion',
            'Simulacrum': 'imitation life'
        }
    },
    'Anomalium': {
        'gloss': 'the unclassifiable',
        'kingdoms': {
            'Aberrant':   'eldritch wrongness',
            'Unfathomed': 'beyond current knowledge'
        }
    }
}

# ===== CLASS TREE (curated: Domain; Discipline/Specialization are LLM-invented) =====

CLASS_DOMAINS = {
    'Martial': 'weapons, brawn, tactics',
    'Arcane':  'learned spellcraft',
    'Primal':  'nature and instinct magic',
    'Divine':  'faith, oaths, pacts',
    'Cunning': 'trickery, stealth, wit',
    'Craft':   'making, alchemy, engineering',
    'Mystic':  'mind, spirit, inner power'
}

# ===== FLAT DIMENSION ENUMS =====

RARITIES = ['common', 'uncommon', 'rare', 'epic', 'legendary']

PARTY_ROLES = ['tank', 'striker', 'skirmisher', 'support', 'controller', 'trickster']

SIZE_CLASSES = ['tiny', 'small', 'medium', 'large', 'huge', 'colossal']

# Sapience gates the chat system: feral monsters cannot converse (impressions
# are narrated), bestial ones read tone without speech, sapient speak freely,
# erudite carry scholarly or ancient knowledge.
SAPIENCE_LEVELS = ['feral', 'bestial', 'sapient', 'erudite']

COMMUNICATION_MODES = ['speech', 'telepathy', 'empathic', 'mimicry', 'none']

ELEMENTS = ['fire', 'water', 'earth', 'air', 'lightning', 'ice',
            'nature', 'metal', 'poison', 'light', 'shadow', 'arcane']

SOCIAL_STRUCTURES = ['solitary', 'pair-bonded', 'pack', 'colony', 'tribal']

CREATION_MECHANISMS = ['born', 'hatched', 'summoned', 'constructed',
                       'risen', 'spawned', 'transformed', 'primordial']

LIFECYCLE_STAGES = ['nascent', 'juvenile', 'adult', 'elder', 'timeless']

HABITAT_DOMAINS = ['land', 'air', 'subterrain', 'water']

BIOMES = ['jungle', 'forest', 'grassland', 'swamp', 'desert', 'tundra',
          'mountain', 'cavern', 'volcanic', 'coast', 'abyssal-sea', 'ruins',
          'settlement', 'skyrealm', 'astral', 'blighted']

SUSTENANCE_SOURCES = ['matter', 'sunlight', 'mana', 'elemental-energy',
                      'life-essence', 'emotion', 'none']

FEEDING_STYLES = ['carnivore', 'herbivore', 'omnivore', 'detritivore', 'lithovore', 'none']

ACTIVITY_CYCLES = ['diurnal', 'nocturnal', 'crepuscular', 'ever-waking']

# Rarity is CODE-ROLLED, never LLM-picked (a creative model asked to choose
# rarity drifts toward legendary); the rolled rarity is injected into the
# generation prompt so the LLM designs a monster AT that rarity.
RARITY_WEIGHTS = {'common': 45, 'uncommon': 30, 'rare': 15, 'epic': 7, 'legendary': 3}

def roll_rarity() -> str:
    """Weighted rarity roll for a newly generated monster"""
    return random.choices(list(RARITY_WEIGHTS.keys()),
                          weights=list(RARITY_WEIGHTS.values()))[0]

# ===== STAT DERIVATION (code-derived: role base x rarity x size, +/- jitter) =====
# Level-1 spreads centered on the old LLM guidance
# (health 80-150, attack 15-35, defense 10-30, speed 5-25).

ROLE_STAT_PROFILES = {
    'tank':       {'health': 130, 'attack': 18, 'defense': 26, 'speed': 9},
    'striker':    {'health': 100, 'attack': 30, 'defense': 14, 'speed': 16},
    'skirmisher': {'health': 90,  'attack': 24, 'defense': 12, 'speed': 22},
    'support':    {'health': 95,  'attack': 16, 'defense': 18, 'speed': 14},
    'controller': {'health': 105, 'attack': 20, 'defense': 16, 'speed': 12},
    'trickster':  {'health': 85,  'attack': 22, 'defense': 11, 'speed': 20}
}

RARITY_MULTIPLIERS = {
    'common': 1.0, 'uncommon': 1.08, 'rare': 1.18, 'epic': 1.3, 'legendary': 1.45
}

SIZE_STAT_NUDGES = {
    'tiny':     {'health': 0.85, 'attack': 0.95, 'defense': 0.90, 'speed': 1.20},
    'small':    {'health': 0.92, 'attack': 0.98, 'defense': 0.95, 'speed': 1.10},
    'medium':   {'health': 1.00, 'attack': 1.00, 'defense': 1.00, 'speed': 1.00},
    'large':    {'health': 1.10, 'attack': 1.05, 'defense': 1.05, 'speed': 0.92},
    'huge':     {'health': 1.20, 'attack': 1.10, 'defense': 1.10, 'speed': 0.85},
    'colossal': {'health': 1.30, 'attack': 1.15, 'defense': 1.20, 'speed': 0.75}
}

STAT_JITTER = 0.10  # +/- proportional randomness applied per stat

def derive_stats(party_role: str, rarity: str, size_class: str) -> dict:
    """Level-1 stats from role x rarity x size with jitter - the referee
    narrates magnitudes, so consistency beats randomness here"""

    base = ROLE_STAT_PROFILES.get(party_role, ROLE_STAT_PROFILES['striker'])
    rarity_mult = RARITY_MULTIPLIERS.get(rarity, 1.0)
    nudges = SIZE_STAT_NUDGES.get(size_class, SIZE_STAT_NUDGES['medium'])

    stats = {}
    for stat, value in base.items():
        jitter = random.uniform(1 - STAT_JITTER, 1 + STAT_JITTER)
        stats[stat] = max(1, round(value * rarity_mult * nudges[stat] * jitter))
    return stats

# ===== NORMALIZATION (guards LLM output, not our own code) =====

def normalize_choice(value, options, default):
    """Match a single LLM-returned value against an option list, forgiving
    case, whitespace, and hyphen/underscore differences"""

    if isinstance(value, str):
        cleaned = value.strip().lower().replace('_', '-')
        for option in options:
            if cleaned == option.lower().replace('_', '-'):
                return option
    return default

def normalize_multi(values, options, default=None):
    """Match a list of LLM-returned values against an option list,
    dropping anything unrecognized"""

    if isinstance(values, str):
        values = [part.strip() for part in values.split(',')]
    if not isinstance(values, list):
        return list(default or [])

    matched = []
    for value in values:
        choice = normalize_choice(value, options, None)
        if choice and choice not in matched:
            matched.append(choice)
    return matched if matched else list(default or [])

def normalize_taxonomy_pick(domain, kingdom):
    """Snap an LLM domain/kingdom pick onto the curated tree; unknown
    picks land in Anomalium/Unfathomed rather than NULL"""

    matched_domain = normalize_choice(domain, list(TAXONOMY_TREE.keys()), None)
    if matched_domain is None:
        return 'Anomalium', 'Unfathomed'

    kingdoms = list(TAXONOMY_TREE[matched_domain]['kingdoms'].keys())
    matched_kingdom = normalize_choice(kingdom, kingdoms, kingdoms[0])
    return matched_domain, matched_kingdom

# ===== PROMPT OPTION LISTS (terse - these cost tokens in every generation call) =====

def taxonomy_options_text() -> str:
    """The curated Domain -> Kingdom tree as compact prompt text"""

    lines = []
    for domain, entry in TAXONOMY_TREE.items():
        kingdoms = ", ".join(entry['kingdoms'].keys())
        lines.append(f"- {domain} ({entry['gloss']}): {kingdoms}")
    return "\n".join(lines)

def class_domain_options_text() -> str:
    """The curated class domains as compact prompt text"""

    return "\n".join(f"- {domain}: {gloss}" for domain, gloss in CLASS_DOMAINS.items())

def options_line(options) -> str:
    """A flat enum as a one-line prompt choice list"""

    return " | ".join(options)
