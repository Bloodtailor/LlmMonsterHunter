# Context Limits - Token-Aware Budgets for LLM Prompt Blocks
# Budgets scale with the loaded model's context window (LLM_CONTEXT_SIZE in
# .env): a 4096-token model gets lean prompts, an 8192-token model gets
# richer ones, a 1M-token model is effectively unclamped.
#
# Two kinds of blocks:
#   REQUIRED  - identity data the LLM must have whole (party and monster
#               details). NEVER truncated.
#   FLEXIBLE  - growing history (logs, dialogue). Each gets a percentage
#               share of the prompt budget and is truncated to fit,
#               keeping the most recent content.

import os

# Rough chars-per-token for English prose (conservative)
CHARS_PER_TOKEN = 4

# Tokens held back from the window for the model's RESPONSE plus the
# prompt's fixed instruction text
RESERVED_RESPONSE_TOKENS = 1200

# Blocks that must arrive whole - clamp_context passes them through
REQUIRED_BLOCKS = ('party_details', 'monster_details')

# Flexible blocks: the share of the prompt budget each may occupy.
# Tune freely - one place to balance the prompt's composition.
FLEXIBLE_BLOCK_SHARES = {
    'dungeon_log': 0.25,        # the rolling story of the run
    'battle_log': 0.20,         # turn-by-turn battle narrations
    'dialogue_history': 0.15,   # the active encounter conversation
    'turn_history': 0.08,       # who acted when, for the turn director
    'location_description': 0.05
}

# Even on tiny context windows, flexible blocks keep at least this much
MIN_FLEXIBLE_CHARS = 600

# Blocks that grow over time keep their TAIL (the most recent events
# matter); description blocks keep their HEAD (the opening lines matter)
_TAIL_BLOCKS = ('dungeon_log', 'battle_log', 'dialogue_history', 'turn_history')

TRUNCATION_MARKER = '(...earlier events trimmed...)'

def get_context_size_tokens() -> int:
    """The loaded model's context window, from .env (same key core.py uses)"""
    try:
        return int(os.getenv('LLM_CONTEXT_SIZE', '4096'))
    except (TypeError, ValueError):
        return 4096

def get_prompt_char_budget() -> int:
    """Characters available for the whole prompt after reserving the response"""
    usable_tokens = max(get_context_size_tokens() - RESERVED_RESPONSE_TOKENS, 512)
    return usable_tokens * CHARS_PER_TOKEN

def get_block_char_limit(block_name: str):
    """
    The character budget for one block.
    Required blocks return None (unlimited); unknown blocks return None too.
    """
    if block_name in REQUIRED_BLOCKS:
        return None
    share = FLEXIBLE_BLOCK_SHARES.get(block_name)
    if not share:
        return None
    return max(int(get_prompt_char_budget() * share), MIN_FLEXIBLE_CHARS)

def clamp_context(block_name: str, text: str) -> str:
    """
    Clamp a context block to its budget for the CURRENT model.
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
            clipped = clipped[newline_index + 1:]
        return f"{TRUNCATION_MARKER}\n{clipped}"

    # Description blocks: keep the start
    return text[:limit].rstrip() + '...'
