# Dungeon Fallbacks - deterministic paths and locations for when the LLM
# fails. A broken generation must never block exploration: these are the
# hand-written stand-ins generator.py reaches for. Like all location
# descriptions, they describe the PLACE itself - never the party.

import random


def get_fallback_path() -> dict[str, str]:
    """A hand-written path - always works"""

    fallback_paths = [
        {
            "name": "Crumbling Archway",
            "description": "A stone archway whose carvings have long worn away, opening into darkness beyond.",
        },
        {
            "name": "Narrow Crawlspace",
            "description": "A tight gap between fallen slabs, just wide enough for one adventurer at a time.",
        },
        {
            "name": "Iron-Banded Door",
            "description": "A heavy wooden door reinforced with rusted iron bands, slightly ajar.",
        },
        {
            "name": "Rope Ladder",
            "description": "A frayed rope ladder descending into an unlit shaft below.",
        },
    ]

    return random.choice(fallback_paths)


def get_fallback_location() -> dict[str, str]:
    """A hand-written location - always works"""

    fallback_locations = [
        {
            "name": "Echoing Cavern",
            "description": "Ancient stone walls glisten with moisture, and the smallest sound echoes endlessly into the darkness beyond.",
        },
        {
            "name": "Crystal Grove",
            "description": "Luminescent crystals cast dancing shadows across twisted root formations that seem to pulse with inner life.",
        },
        {
            "name": "Forgotten Sanctum",
            "description": "Weathered statues stand sentinel in this abandoned temple, their carved eyes fixed on the doorway as if still keeping some ancient watch.",
        },
        {
            "name": "Whispering Chamber",
            "description": "Strange murmurs drift through the air in this circular room, though no source can be seen.",
        },
        {
            "name": "Moonlit Corridor",
            "description": "Pale light filters down through cracks in the ceiling, illuminating dust motes that dance like tiny spirits.",
        },
    ]

    return random.choice(fallback_locations)
