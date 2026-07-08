# Context Limits - Absolute Token Caps for LLM Prompt Blocks
# The supported floor is a 1M-token context window (locked decision,
# docs/plans/cloud-generation.md), so prompts always FIT. What these
# budgets guard now is COST and ATTENTION: every prompt token is billed,
# and even long-context models answer better over curated history - so
# each growing block gets an ABSOLUTE token cap, and rolling summaries
# condense what the caps trim away.
#
# Two kinds of blocks:
#   REQUIRED  - identity data the LLM must have whole (party and monster
#               details). NEVER truncated.
#   FLEXIBLE  - growing history (logs, dialogue). Each gets an absolute
#               token cap and is truncated to fit, keeping the most
#               recent content.
#
# Unsupported sub-1M local windows (.env escape hatch) still degrade
# gracefully: when the caps together would overflow the prompt budget,
# every cap scales down proportionally.

import os

# Rough chars-per-token for English prose (conservative)
CHARS_PER_TOKEN = 4

# Tokens held back from the window for the model's RESPONSE plus the
# prompt's fixed instruction text
RESERVED_RESPONSE_TOKENS = 1200

# THE CEILING (locked decision): prompts never fill more than 70% of the
# context window, whatever the caps below add up to. Turn it DOWN per
# model in .env (LLM_CONTEXT_FILL_PERCENT=0.5); values above 0.7 clamp
# back to 0.7.
DEFAULT_CONTEXT_FILL_PERCENT = 0.7
MAX_CONTEXT_FILL_PERCENT = 0.7

# Blocks that must arrive whole - clamp_context passes them through
REQUIRED_BLOCKS = ('party_details', 'monster_details')

# Flexible blocks: the absolute token cap each may occupy. These are
# COST VALVES, not fit constraints - together ~46.5K tokens, a sliver of
# a 1M window. Tune freely: one place to balance the prompt's
# composition (and the token bill).
FLEXIBLE_BLOCK_TOKEN_CAPS = {
    'dungeon_log': 12_000,  # the rolling story of the run
    'battle_log': 8_000,  # turn-by-turn battle narrations
    'chat_history': 8_000,  # the home-base conversation with one monster
    'dialogue_history': 6_000,  # the active encounter conversation
    'last_run_log': 4_000,  # what happened in the previous dungeon run
    'turn_history': 2_000,  # who acted when, for the turn director
    'monster_memories': 3_000,  # what a monster remembers of the party
    'run_journal': 2_000,  # what a party monster did this run
    'location_description': 1_500,
}

# Even when caps scale down (unsupported small windows), flexible blocks
# keep at least this much
MIN_FLEXIBLE_CHARS = 600

# Blocks that grow over time keep their TAIL (the most recent events
# matter); description blocks keep their HEAD (the opening lines matter)
_TAIL_BLOCKS = (
    'dungeon_log',
    'battle_log',
    'dialogue_history',
    'turn_history',
    'monster_memories',
    'run_journal',
    'chat_history',
    'last_run_log',
)

TRUNCATION_MARKER = '(...earlier events trimmed...)'


def get_context_size_tokens() -> int:
    """The ACTIVE provider's context window - the settings resolver
    answers (DeepSeek: the per-model window saved in the panel; local:
    LLM_CONTEXT_SIZE in .env, the same key core.py loads with)"""
    try:
        from backend.ai.llm.provider_settings import resolve_llm_settings

        return int(resolve_llm_settings()['context_size'])
    except Exception:
        pass

    try:
        return int(os.getenv('LLM_CONTEXT_SIZE', '1000000'))
    except (TypeError, ValueError):
        return 1_000_000


def get_context_fill_percent() -> float:
    """How much of the window prompts may fill (developer knob, .env) -
    never above the 70% ceiling, never below a useful floor"""
    try:
        fill = float(os.getenv('LLM_CONTEXT_FILL_PERCENT', str(DEFAULT_CONTEXT_FILL_PERCENT)))
    except (TypeError, ValueError):
        fill = DEFAULT_CONTEXT_FILL_PERCENT
    return min(max(fill, 0.3), MAX_CONTEXT_FILL_PERCENT)


def get_prompt_char_budget() -> int:
    """Characters available for the whole prompt after reserving the response"""
    filled_window = int(get_context_size_tokens() * get_context_fill_percent())
    usable_tokens = max(filled_window - RESERVED_RESPONSE_TOKENS, 512)
    return usable_tokens * CHARS_PER_TOKEN


def _cap_scale() -> float:
    """1.0 on supported (1M+) windows. On an unsupported small window the
    caps could overflow the budget together, so every cap shrinks by the
    same factor - the old proportional behavior, kept as a safety net."""
    total_cap_chars = sum(FLEXIBLE_BLOCK_TOKEN_CAPS.values()) * CHARS_PER_TOKEN
    budget = get_prompt_char_budget()
    if total_cap_chars <= budget:
        return 1.0
    return budget / total_cap_chars


def get_block_char_limit(block_name: str):
    """
    The character budget for one block.
    Required blocks return None (unlimited); unknown blocks return None too.
    """
    if block_name in REQUIRED_BLOCKS:
        return None
    cap_tokens = FLEXIBLE_BLOCK_TOKEN_CAPS.get(block_name)
    if not cap_tokens:
        return None
    cap_chars = int(cap_tokens * CHARS_PER_TOKEN * _cap_scale())
    return max(cap_chars, MIN_FLEXIBLE_CHARS)


def clamp_context(block_name: str, text: str) -> str:
    """
    Clamp a context block to its absolute cap.
    Required and unknown blocks pass through untouched.
    """
    if not text:
        return text

    limit = get_block_char_limit(block_name)
    if limit is None or len(text) <= limit:
        return text

    if block_name in _TAIL_BLOCKS:
        # Keep the most recent events, cut on a line break where possible
        clipped = text[-limit:]
        newline_index = clipped.find('\n')
        if 0 <= newline_index < limit // 4:
            clipped = clipped[newline_index + 1 :]
        return f"{TRUNCATION_MARKER}\n{clipped}"

    # Description blocks: keep the start
    return text[:limit].rstrip() + '...'
