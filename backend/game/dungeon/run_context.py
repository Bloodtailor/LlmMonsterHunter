# Run Context - the active run's modifiers, in ONE place
# Theme, danger (and later: goal, first_run) chosen at the entrance ride
# here for the whole run. Every generator that should feel the run reads
# through expedition_brief() or danger_knob() - no scattered globals.
#
# WHY its own GlobalVariable key instead of dungeon_state: the theme must
# exist BEFORE the starting location generates, but the dungeon state row
# is only created (and wholly replaced) after generation. The lifecycle
# stays single-pointed: begin_run_context() at the top of enter_dungeon,
# clear_run_context() inside manager.exit_dungeon().

from typing import Any, Optional

from backend.models.global_variables import GlobalVariable

RUN_CONTEXT_KEY = 'run_context'

# Where the entrance's generated notices wait between the notice-board
# workflow and the player's choice (enter_dungeon validates against this)
PENDING_NOTICES_KEY = 'expedition_notices'

# ===== DANGER: the difficulty word ladder =====
# The LLM never sees these numbers - the danger WORD colors its prose
# (via expedition_brief and the referee hint) while Python turns the same
# word into the actual odds below. Catalogued in docs/tuning.md.

DANGER_LADDER = ('calm', 'risky', 'perilous')

# 'risky' matches the tuning defaults that existed before danger did -
# a run without a notice plays exactly like the game always played
DEFAULT_DANGER = 'risky'

DANGER_PROFILES = {
    'calm': {
        'enemy_count_range': (1, 1),
        'battle_event_weight': 0.12,
        'explore_monsters_chance': 0.4,
        'returning_event_weight': 0.10,
        'referee_hint': (
            "This expedition is a calm one. When in doubt, judge kindly: "
            "let typical blows stay light and reserve heavy results for "
            "truly earned moments."
        ),
    },
    'risky': {
        'enemy_count_range': (1, 2),
        'battle_event_weight': 0.18,
        'explore_monsters_chance': 0.5,
        'returning_event_weight': 0.12,
        'referee_hint': "Judge each action fairly on its merits.",
    },
    'perilous': {
        'enemy_count_range': (2, 3),
        'battle_event_weight': 0.26,
        'explore_monsters_chance': 0.65,
        'returning_event_weight': 0.16,
        'referee_hint': (
            "This expedition is a perilous one. Blows land harder here: "
            "judge impacts harshly, punish careless actions, and make "
            "every mistake cost something."
        ),
    },
}

# How the danger word reads inside the expedition brief (prose, not odds)
_DANGER_FLAVOR = {
    'calm': 'a gentle expedition - more wonder than teeth',
    'risky': 'a true expedition with real teeth',
    'perilous': 'a dangerous venture into openly hostile depths',
}


# ===== LIFECYCLE =====


def begin_run_context(
    theme: Optional[str] = None,
    danger: Optional[str] = None,
    first_run: bool = False,
) -> dict[str, Any]:
    """Open the run's context at the very start of enter_dungeon - BEFORE
    anything generates, so the starting location is already themed"""
    context = {
        'theme': str(theme).strip() if theme else None,
        'danger': danger if danger in DANGER_LADDER else None,
        'goal': None,  # set by the goal generation step (Game Loop M3)
        'first_run': bool(first_run),
    }
    GlobalVariable.set(RUN_CONTEXT_KEY, context)
    return context


def get_run_context() -> dict[str, Any]:
    return GlobalVariable.get(RUN_CONTEXT_KEY, {}) or {}


def save_run_context(context: dict[str, Any]) -> None:
    GlobalVariable.set(RUN_CONTEXT_KEY, context)


def clear_run_context() -> None:
    """Called from manager.exit_dungeon() - the single point where every
    run ends (victory, defeat, and abandonment all pass through it)"""
    GlobalVariable.set(RUN_CONTEXT_KEY, {})


# ===== DANGER ACCESSORS (code reads odds; prompts read words) =====


def active_danger() -> Optional[str]:
    danger = get_run_context().get('danger')
    return danger if danger in DANGER_LADDER else None


def danger_knob(name: str, default: Any) -> Any:
    """The active danger profile's value for a knob, or the caller's
    default when no run/danger is active (keeps every roll function
    working exactly as before outside themed runs)"""
    danger = active_danger()
    if not danger:
        return default
    value = DANGER_PROFILES[danger].get(name)
    return value if value is not None else default


def referee_hint() -> str:
    """The line that biases the battle referee's impact words"""
    danger = active_danger() or DEFAULT_DANGER
    return DANGER_PROFILES[danger]['referee_hint']


# ===== THE EXPEDITION BRIEF (the one block prompts receive) =====


def expedition_brief() -> str:
    """
    The run's modifiers as ONE prompt context block. Everything the
    LLM should keep in mind for the whole run: theme, danger, goal.
    Safe outside runs - callers never need to check first.
    """
    context = get_run_context()
    lines = []

    theme = context.get('theme')
    if theme:
        lines.append(f"Theme of this expedition (weave it into everything): {theme}")

    danger = context.get('danger')
    if danger in DANGER_LADDER:
        lines.append(f"Danger level: {danger} - {_DANGER_FLAVOR[danger]}.")

    goal = context.get('goal') or {}
    if goal.get('text'):
        status = (
            'already accomplished - let the remaining places feel like a road home'
            if goal.get('status') == 'complete'
            else 'not yet accomplished - let the dungeon hint toward it'
        )
        lines.append(f"The party's goal for this run: {goal['text']} ({status})")

    if not lines:
        return "An ordinary expedition - no special notice was posted for this run."
    return "\n".join(lines)


def themed_location_context(location: dict[str, Any]) -> str:
    """A location as monster-generation context, carrying the active
    expedition's theme - encounter monsters belong to their run, not just
    their room (used by game/monster/generator.py)"""
    context = f"{location.get('name', 'Unknown Location')}: {location.get('description', '')}"
    theme = get_run_context().get('theme')
    if theme:
        context += f"\nThe expedition's running theme (this creature should fit it): {theme}"
    return context


# ===== PENDING EXPEDITION NOTICES (entrance board) =====


def store_pending_notices(notices: list[dict[str, Any]]) -> None:
    GlobalVariable.set(PENDING_NOTICES_KEY, {'notices': notices})


def get_pending_notices() -> list[dict[str, Any]]:
    stored = GlobalVariable.get(PENDING_NOTICES_KEY, {}) or {}
    return stored.get('notices', [])


def get_pending_notice(notice_id: str) -> Optional[dict[str, Any]]:
    """The stored notice with this id - the enter_dungeon trust check"""
    for notice in get_pending_notices():
        if notice.get('id') == notice_id:
            return notice
    return None


def clear_pending_notices() -> None:
    GlobalVariable.set(PENDING_NOTICES_KEY, {})
