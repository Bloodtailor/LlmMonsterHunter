# Battle Constants - The Condition Ladder and Impact System
# No HP math anywhere: monster wellbeing is a position on a fixed ladder,
# and the LLM referee's judgments move monsters along it.
# Python owns these rules - the LLM only ever picks an impact word.

# Monster wellbeing, best to worst. Bottom of the ladder = out of the fight.
CONDITION_LADDER = [
    'fresh',
    'scuffed',
    'wounded',
    'battered',
    'critical',
    'incapacitated'
]

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
    'heal_major': -2
}

# How many enemies a battle spawns (inclusive range)
# Design allows up to 7 - kept small while each enemy costs ~4 LLM calls + art
ENEMY_COUNT_RANGE = (1, 2)

# How many recent narrations to keep as rolling context for the referee
RECENT_LOG_SIZE = 4

# How many recent turns to keep as context for the turn-order LLM
TURN_HISTORY_SIZE = 8

# Softlock valve: after this many consecutive enemy turns, the next turn
# is forced to an ally so the player is never locked out of acting
MAX_CONSECUTIVE_ENEMY_TURNS = 6

# Fairness guardrail: when a living monster has waited this many times the
# living-combatant count without acting, Python force-picks it directly
# (bypassing the LLM turn director) - no monster can ever be forgotten
OVERDUE_WAIT_MULTIPLIER = 2

# Cap on player free-text length for custom actions and talk
PLAYER_TEXT_MAX_CHARS = 500
