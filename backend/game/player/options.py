# Character Creation Options - the LLM proposes, the player decides
# Every creation field works the same way: one small LLM call offers a
# handful of distinct directions, conditioned on everything chosen so
# far, and the player picks one OR types their own (free text is always
# a first-class answer - options exist to spark, never to fence).
# Role is NOT here: it is a static code list (cmdts_data.PARTY_ROLES).

from backend.game.monster import cmdts_data
from backend.game.utils import build_and_generate

# One knob for how many options a field offers (kind gets one extra -
# it is the widest-open question in the game)
PLAYER_OPTION_COUNT = 3

# What the player may type per field (options are clipped to the same)
FIELD_MAX_CHARS = {
    'kind': 120,
    'name': 60,
    'background': 300,
    'personality': 300,
    'wish': 300,
    'appearance': 500,
}

# The creation fields, in wizard order. guidance frames the decision for
# the options prompt; shape tells the LLM what ONE option looks like.
OPTION_FIELDS = {
    'kind': {
        'count': PLAYER_OPTION_COUNT + 1,
        'guidance': (
            "WHAT the character is. Anything in this world is playable - an "
            "ordinary human, or any creature from the taxonomy below:\n"
            "{taxonomy_options}"
        ),
        'shape': (
            "a short phrase naming what they are, with one vivid hook "
            "(e.g. \"Human - a baker who walked away from the ovens\" or "
            "\"A soot-winged fey moth the size of a child\")"
        ),
    },
    'name': {
        'count': PLAYER_OPTION_COUNT,
        'guidance': "The character's personal name - what companions will call them.",
        'shape': "a single name (one or two words, no titles), fitting their kind",
    },
    'background': {
        'count': PLAYER_OPTION_COUNT,
        'guidance': (
            "Where the character comes from and what they left behind to "
            "chase the wish-granting power."
        ),
        'shape': "one sentence of concrete history (a place, a life, a departure)",
    },
    'personality': {
        'count': PLAYER_OPTION_COUNT,
        'guidance': "How the character carries themselves - temperament, manner, edge.",
        'shape': "one line: a few sharp adjectives plus one telling habit or quirk",
    },
    'wish': {
        'count': PLAYER_OPTION_COUNT,
        'guidance': (
            "THE wish. Somewhere below sleeps a power that grants any wish - "
            "this is the one that drives the character into the dark. It "
            "shapes their whole story."
        ),
        'shape': "one sentence naming a concrete, deeply personal wish",
    },
    'appearance': {
        'count': PLAYER_OPTION_COUNT,
        'guidance': (
            "What the character looks like. This text is ALSO the portrait "
            "brief - the image model paints from these exact words."
        ),
        'shape': "1-2 sentences written like an artist's brief: build, face, colors, attire, one memorable detail",
    },
}

# Display order for choices-so-far blocks (role rides along when chosen)
_CHOICE_ORDER = ('kind', 'name', 'background', 'personality', 'wish', 'role', 'appearance')


def clean_choices(raw) -> dict[str, str]:
    """Clip the player's answers to their field caps, dropping blanks and
    unknown keys (role is kept - it rides the choices block into prompts)"""
    if not isinstance(raw, dict):
        return {}
    cleaned = {}
    for field in _CHOICE_ORDER:
        value = raw.get(field)
        if isinstance(value, str) and value.strip():
            cleaned[field] = value.strip()[: FIELD_MAX_CHARS.get(field, 300)]
    return cleaned


def choices_so_far_text(choices: dict[str, str]) -> str:
    """The character-so-far context block, in wizard order"""
    lines = [
        f"{field.capitalize()}: {choices[field]}" for field in _CHOICE_ORDER if choices.get(field)
    ]
    return "\n".join(lines) if lines else "Nothing decided yet - this is the first choice."


def generate_options(field: str, choices: dict[str, str]) -> list[str]:
    """One LLM call: distinct options for ONE field, conditioned on the
    choices so far. Returns clipped option strings (the LLM proposes,
    code enforces count and length). Raises on LLM failure."""
    spec = OPTION_FIELDS[field]

    guidance = spec['guidance']
    if field == 'kind':
        guidance = guidance.format(taxonomy_options=cmdts_data.taxonomy_options_text())

    result = build_and_generate(
        'player_options',
        'player_generation',
        {
            'choices_so_far': choices_so_far_text(choices),
            'field_guidance': guidance,
            'option_count': spec['count'],
            'option_shape': spec['shape'],
        },
    )

    options = []
    for option in result.get('options') or []:
        if isinstance(option, str) and option.strip():
            options.append(option.strip()[: FIELD_MAX_CHARS[field]])
        if len(options) >= spec['count']:
            break
    if not options:
        raise Exception(f"The muse offered nothing for '{field}' - try again")
    return options
