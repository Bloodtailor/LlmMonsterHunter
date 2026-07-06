# Dungeon Events - Random Event Assignment for Paths
# Events are chosen randomly in Python (NOT by the LLM) when paths are
# generated, stored in dungeon state, and hidden from the player until
# they choose the path

import random

# Every event a path can hold - add new events here as they are built
# (future: 'treasure', 'trap', ...)
AVAILABLE_EVENTS = [
    'monster_riddle',
    'monster_battle'
]

# How many paths a junction offers (inclusive range)
PATH_COUNT_RANGE = (2, 4)

# Chance that one of the junction's paths is a dungeon exit
EXIT_PATH_CHANCE = 0.33

# How many paths the LLM generates per batch - more than we need, and we
# use the LAST ones. Small local LLMs repeat themselves early; asking for
# extra and taking the later entries plays to their strengths
PATH_OVERGENERATE_COUNT = 6

def assign_random_event() -> str:
    """Pick a random event for a path from the available events"""
    return random.choice(AVAILABLE_EVENTS)

def roll_path_count() -> int:
    """Roll how many paths this junction offers"""
    return random.randint(*PATH_COUNT_RANGE)

def roll_include_exit() -> bool:
    """Roll whether one of the paths is a dungeon exit"""
    return random.random() < EXIT_PATH_CHANCE
