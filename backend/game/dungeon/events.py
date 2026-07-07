# Dungeon Events - Random Event Assignment for Paths
# Events are chosen randomly in Python (NOT by the LLM) when paths are
# generated, stored in dungeon state, and hidden from the player until
# they choose the path.
# The constants below are the no-run defaults; an active expedition's
# danger word (dungeon/run_context.py) overrides the marked knobs.

import random

# Every event a path can hold, with its weight. Exploring is the bread
# and butter of a run - encounters punctuate it. Add new events here as
# they are built (future: 'trap', ...)
EVENT_WEIGHTS = {
    'location_explore': 0.55,  # arrive, look around, decide what to do
    'monster_dialogue': 0.18,  # a monster greets the party with a question
    'monster_battle': 0.18,  # hostile monsters attack on arrival
    'treasure': 0.09,  # a hidden item waits to be discovered
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

# Weight of the returning-monster event WHEN remembered monsters are
# eligible to return (the pool is checked at path-generation time and
# re-checked at dispatch; random.choices normalizes the weights)
RETURNING_EVENT_WEIGHT = 0.12


def assign_random_event(include_returning: bool = False) -> str:
    """Pick a weighted random event for a path from the available events.
    The active run's danger word (run_context) shifts the battle and
    returning weights; without a run this rolls exactly the table above.
    A guided FIRST RUN doesn't roll at all - every path at the junction
    carries the script's next beat (dungeon/first_run.py)."""
    from backend.game.dungeon.first_run import next_scripted_event
    from backend.game.dungeon.run_context import danger_knob

    scripted = next_scripted_event()
    if scripted:
        return scripted

    weight_map = dict(EVENT_WEIGHTS)
    weight_map['monster_battle'] = danger_knob(
        'battle_event_weight', weight_map['monster_battle']
    )
    events = list(weight_map.keys())
    weights = list(weight_map.values())
    if include_returning:
        events.append('returning_monster')
        weights.append(danger_knob('returning_event_weight', RETURNING_EVENT_WEIGHT))
    return random.choices(events, weights=weights, k=1)[0]


def roll_monsters_present() -> bool:
    """Roll whether an explore location has monsters in it (danger-aware)"""
    from backend.game.dungeon.run_context import danger_knob

    return random.random() < danger_knob('explore_monsters_chance', EXPLORE_MONSTERS_CHANCE)


def roll_explore_monster_count() -> int:
    """Roll how many monsters dwell in an explore location"""
    return random.randint(*EXPLORE_MONSTER_COUNT_RANGE)


def roll_path_count() -> int:
    """Roll how many paths this junction offers"""
    return random.randint(*PATH_COUNT_RANGE)


def roll_include_exit() -> bool:
    """Roll whether one of the paths is a dungeon exit. On a guided first
    run the exit appears exactly when the script is spent - never before."""
    from backend.game.dungeon.first_run import is_first_run, next_scripted_event

    if is_first_run():
        return next_scripted_event() is None
    return random.random() < EXIT_PATH_CHANCE
