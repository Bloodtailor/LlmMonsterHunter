# Dungeon Events - Random Event Assignment for Paths
# Events are chosen randomly in Python (NOT by the LLM) when paths are
# generated, stored in dungeon state, and hidden from the player until
# they choose the path

import random

# Every event a path can hold, with its weight. Exploring is the bread
# and butter of a run - encounters punctuate it. Add new events here as
# they are built (future: 'trap', ...)
EVENT_WEIGHTS = {
    'location_explore': 0.55,   # arrive, look around, decide what to do
    'monster_dialogue': 0.18,   # a monster greets the party with a question
    'monster_battle': 0.18,     # hostile monsters attack on arrival
    'treasure': 0.09            # a hidden item waits to be discovered
}

# When a location_explore fires, chance that monsters are in the area
# (they are not immediately hostile - talk, ambush, or sneak past them)
EXPLORE_MONSTERS_CHANCE = 0.5

# How many monsters an explore location can hold (inclusive range)
EXPLORE_MONSTER_COUNT_RANGE = (1, 2)

# How many paths a junction offers (inclusive range)
PATH_COUNT_RANGE = (2, 4)

# Chance that one of the junction's paths is a dungeon exit
EXIT_PATH_CHANCE = 0.33

# How many paths the LLM generates per batch - more than we need, and we
# use the LAST ones. Small local LLMs repeat themselves early; asking for
# extra and taking the later entries plays to their strengths
PATH_OVERGENERATE_COUNT = 6

def assign_random_event() -> str:
    """Pick a weighted random event for a path from the available events"""
    events = list(EVENT_WEIGHTS.keys())
    weights = list(EVENT_WEIGHTS.values())
    return random.choices(events, weights=weights, k=1)[0]

def roll_monsters_present() -> bool:
    """Roll whether an explore location has monsters in it"""
    return random.random() < EXPLORE_MONSTERS_CHANCE

def roll_explore_monster_count() -> int:
    """Roll how many monsters dwell in an explore location"""
    return random.randint(*EXPLORE_MONSTER_COUNT_RANGE)

def roll_path_count() -> int:
    """Roll how many paths this junction offers"""
    return random.randint(*PATH_COUNT_RANGE)

def roll_include_exit() -> bool:
    """Roll whether one of the paths is a dungeon exit"""
    return random.random() < EXIT_PATH_CHANCE
