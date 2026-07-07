# Battle Constants - The Condition Ladder and Impact System
# No HP math anywhere: monster wellbeing is a position on a fixed ladder,
# and the LLM referee's judgments move monsters along it.
# Python owns these rules - the LLM only ever picks an impact word.

# Monster wellbeing, best to worst. Bottom of the ladder = out of the fight.
CONDITION_LADDER = ['fresh', 'scuffed', 'wounded', 'battered', 'critical', 'incapacitated']

INCAPACITATED = 'incapacitated'
FRESH = 'fresh'

# How each referee impact judgment moves a monster on the ladder
# (positive = toward incapacitated, negative = toward fresh)
IMPACT_STEPS = {
    'none': 0,
    'light': 1,
    'heavy': 2,
    'devastating': 3,
    'heal_light': -1,
    'heal_major': -2,
}

# ===== RESOURCE POOLS (stamina and mana) =====
# Same philosophy as the condition ladder: no numbers, just positions on
# a word ladder. The referee picks a cost word per action; Python steps
# the ladder. Pools refill ONLY when the party enters the dungeon (plus
# whatever the referee grants: camp rest, defend stances, restoring
# abilities and items).

# Reserve levels, fullest to emptiest. Bottom = nothing left to give.
RESOURCE_LADDER = ['brimming', 'steady', 'strained', 'drained', 'spent']

RESOURCE_KEYS = ('stamina', 'mana')

BRIMMING = 'brimming'
SPENT = 'spent'

# How each referee cost/restore judgment moves a pool on the ladder
# (positive = toward spent, negative = toward brimming)
RESOURCE_DELTAS = {
    'none': 0,
    'minor': 1,
    'moderate': 2,
    'heavy': 3,
    'restore_minor': -1,
    'restore_major': -2,
}

# Which pool an ability drains BY DEFAULT when the referee stays silent,
# keyed by ability_type (see ability_generation.json). Unknown types
# default to stamina.
ABILITY_POOL_BY_TYPE = {
    'attack': 'stamina',
    'defense': 'stamina',
    'movement': 'stamina',
    'support': 'mana',
    'special': 'mana',
    'utility': 'mana',
}


def full_resources() -> dict:
    """A fresh set of pools - both reserves brimming"""
    return {key: BRIMMING for key in RESOURCE_KEYS}


# How many enemies a battle spawns (inclusive range)
# Design allows up to 7 - kept small while each enemy costs ~4 LLM calls + art
ENEMY_COUNT_RANGE = (1, 2)

# How many narrations/turns to KEEP IN STORAGE. A runaway safety valve
# only - old narrations are progressively condensed into rolling
# summaries (rolling_summary.py) while raw entries stay for the whole
# battle, and the token-aware budgets in context_limits.py decide how
# much actually fits in each prompt for the loaded model
RECENT_LOG_SIZE = 400
TURN_HISTORY_SIZE = 40

# Softlock valve: after this many consecutive enemy turns, the next turn
# is forced to an ally so the player is never locked out of acting
MAX_CONSECUTIVE_ENEMY_TURNS = 6

# Fairness guardrail: when a living monster has waited this many times the
# living-combatant count without acting, Python force-picks it directly
# (bypassing the LLM turn director) - no monster can ever be forgotten
OVERDUE_WAIT_MULTIPLIER = 2

# Cap on player free-text length for custom actions and talk
PLAYER_TEXT_MAX_CHARS = 500
