# Rolling Summary - Condense Old History, Keep Recent History Verbatim
# The upgrade over plain tail-truncation for every growing history in the
# game (chat threads, the dungeon log, the battle log): once enough old
# entries pile up beyond a keep-verbatim window, ONE batch of the oldest
# uncovered entries is condensed into a short summary by the LLM. Raw
# entries are never deleted - prompts that draw from a single source can
# still read far more verbatim than prompts juggling many sources.
#
# Prompt composition = every summary so far (oldest first) + the verbatim
# tail, clamped to the block's normal budget - so on tiny context windows
# the tail-keeping clamp naturally sheds the oldest summaries first.
#
# This module is deliberately storage-agnostic: callers own WHERE entries
# and summaries live (database tables, dungeon_state, battle_state) and
# pass plain lists in. Summarization itself never raises - a failed
# condense simply retries at the next trigger.

from typing import Any, Dict, List, Optional, Tuple
from backend.game.utils.context_limits import clamp_context

# Per-source developer knobs. 'covered' below always means "how many of
# the oldest entries the summaries already condense".
#   keep_recent - entries that must stay verbatim (never summarized)
#   batch_min   - uncovered entries beyond keep_recent needed to trigger
#   batch_max   - most entries condensed per LLM call (bounds the prompt)
#   label       - what the lines ARE, spoken into the condense template
SUMMARY_SOURCES = {
    'chat_history': {
        'keep_recent': 16,
        'batch_min': 12,
        'batch_max': 30,
        'label': 'a long conversation between an adventurer and the monster companion who travels with them',
    },
    'dungeon_log': {
        'keep_recent': 12,
        'batch_min': 10,
        'batch_max': 25,
        'label': "the running log of an adventuring party's journey through a dungeon",
    },
    'battle_log': {
        'keep_recent': 14,
        'batch_min': 12,
        'batch_max': 25,
        'label': 'the turn-by-turn record of an ongoing monster battle',
    },
}

# Summaries stored next to their entries share this shape:
#   {'through': int, 'text': str} - condenses entries[0:through]
def covered_count(summaries: List[Dict[str, Any]]) -> int:
    """How many of the oldest entries the summaries already condense"""
    if not summaries:
        return 0
    try:
        return max(int(s.get('through', 0)) for s in summaries)
    except (TypeError, ValueError):
        return 0

def plan_batch(source: str, total_entries: int, covered: int) -> Optional[Tuple[int, int]]:
    """
    Decide whether a batch is due and which entries it covers.

    Returns (start, end) as indexes into the FULL entry list (end is
    exclusive), or None when nothing needs condensing yet.
    """
    settings = SUMMARY_SOURCES.get(source)
    if not settings:
        return None

    uncovered_old = total_entries - covered - settings['keep_recent']
    if uncovered_old < settings['batch_min']:
        return None

    return covered, covered + min(uncovered_old, settings['batch_max'])

def summarize_lines(source: str, lines: List[str], workflow_name: str,
                    prior_summary: str = None) -> Optional[str]:
    """
    Condense one batch of lines with the LLM. Returns the summary text,
    or None on any failure (the caller must NOT advance coverage then -
    the same batch simply retries at the next trigger).
    """
    settings = SUMMARY_SOURCES.get(source)
    if not settings or not lines:
        return None

    try:
        from backend.game.utils.prompt_helpers import build_and_generate
        result = build_and_generate('condense_history', workflow_name, {
            'source_label': settings['label'],
            'prior_summary': (prior_summary or '').strip() or 'Nothing has been condensed yet.',
            'batch_lines': "\n".join(f"- {line}" for line in lines)
        })
        text = str(result or '').strip()
        return text or None
    except Exception as e:
        print(f"❌ Failed to condense {source} batch: {e}")
        return None

def compose_history(source: str, summaries: List[Dict[str, Any]],
                    verbatim_lines: List[str], block_name: str,
                    empty_text: str) -> str:
    """
    The full history as one clamped LLM context block: summaries of the
    old (oldest first), then the recent lines verbatim.
    """
    parts = []
    ordered = sorted(summaries or [], key=lambda s: int(s.get('through', 0)))
    summary_texts = [str(s.get('text', '')).strip() for s in ordered if s.get('text')]
    if summary_texts:
        parts.append("(earlier, condensed) " + " ".join(summary_texts))
    parts.extend(f"- {line}" for line in verbatim_lines)

    if not parts:
        return empty_text
    return clamp_context(block_name, "\n".join(parts))
