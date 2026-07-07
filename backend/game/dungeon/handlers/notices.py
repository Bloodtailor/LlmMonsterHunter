# Expedition notices - the posted expeditions the player chooses from at
# the dungeon entrance. The LLM writes each notice's title, pitch, and
# theme; PYTHON rolls its danger word - code owns the stakes. The chosen
# notice's theme + danger become the run_context for the whole run.

import random
from typing import Any

from backend.core.utils.responses import success_response
from backend.core.workflow_steps import WorkflowStep

# How many notices the board offers per visit
NOTICE_COUNT = 3

# The odds of each danger word when a notice is stamped (docs/tuning.md)
NOTICE_DANGER_WEIGHTS = {'calm': 0.30, 'risky': 0.45, 'perilous': 0.25}

# When the LLM fails, the board still has something pinned to it
_FALLBACK_NOTICES = [
    {
        'title': 'The Quiet Depths',
        'pitch': 'A gentle survey of the upper halls. Old stone, older air, and room to breathe.',
        'theme': 'worn stone halls and small, shy creatures that keep to the shadows',
    },
    {
        'title': 'Where the Water Sings',
        'pitch': 'Flooded passages have opened below. Bring something that can swim.',
        'theme': 'drowned corridors and things that learned to hunt in the dark water',
    },
    {
        'title': 'The Ember Vaults',
        'pitch': 'Heat rises from the deep vaults. Whatever stokes those fires has been busy.',
        'theme': 'scorched vaults, ash-choked air, and creatures forged by heat',
    },
]


def roll_notice_danger() -> str:
    """Stamp a danger word on a notice - weighted, in Python"""
    words = list(NOTICE_DANGER_WEIGHTS.keys())
    weights = list(NOTICE_DANGER_WEIGHTS.values())
    return random.choices(words, weights=weights, k=1)[0]


def run_generate_notices(context: dict, step: WorkflowStep) -> dict[str, Any]:
    """Generate the entrance board's notices and store them for the
    enter_dungeon trust check"""
    workflow_name = 'generate_expedition_notices'

    from backend.game.dungeon import run_context
    from backend.game.utils import build_and_generate

    step.emit("validate_context")

    # One batch call writes every notice - themes should contrast
    step.emit("generate_notices")
    generated = []
    try:
        batch = build_and_generate(
            'expedition_notices', workflow_name, {'notice_count': NOTICE_COUNT}
        )
        raw = batch.get('notices') or []
        generated = [
            n for n in raw if isinstance(n, dict) and n.get('title') and n.get('theme')
        ][:NOTICE_COUNT]
    except Exception:
        generated = []

    # Top up from the fallbacks (skipping any title already on the board)
    for fallback in _FALLBACK_NOTICES:
        if len(generated) >= NOTICE_COUNT:
            break
        if not any(n.get('title') == fallback['title'] for n in generated):
            generated.append(dict(fallback))

    # Python stamps ids and rolls each notice's danger word
    notices = [
        {
            'id': f'notice_{i + 1}',
            'title': str(notice.get('title', 'An Unmarked Expedition')).strip()[:80],
            'pitch': str(notice.get('pitch', '')).strip()[:400],
            'theme': str(notice.get('theme', '')).strip()[:300],
            'danger': roll_notice_danger(),
        }
        for i, notice in enumerate(generated)
    ]

    step.emit("store_notices")
    run_context.store_pending_notices(notices)

    return success_response({'notices': notices})
