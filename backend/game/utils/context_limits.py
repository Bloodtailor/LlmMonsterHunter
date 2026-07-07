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

# Some models degrade when the window is nearly full - this knob treats
# only a fraction of LLM_CONTEXT_SIZE as usable. 1.0 = use it all.
# Override per model in .env: LLM_CONTEXT_FILL_PERCENT=0.85
DEFAULT_CONTEXT_FILL_PERCENT = 1.0

# Blocks that must arrive whole - clamp_context passes them through
REQUIRED_BLOCKS = ('party_details', 'monster_details')

# Flexible blocks: the share of the prompt budget each may occupy.
# Tune freely - one place to balance the prompt's composition.
FLEXIBLE_BLOCK_SHARES = {
    'dungeon_log': 0.25,        # the rolling story of the run
    'battle_log': 0.20,         # turn-by-turn battle narrations
    'chat_history': 0.20,       # the home-base conversation with one monster
    'dialogue_history': 0.15,   # the active encounter conversation
    'last_run_log': 0.10,       # what happened in the previous dungeon run
    'turn_history': 0.08,       # who acted when, for the turn director
    'monster_memories': 0.06,   # what a monster remembers of the party
    'run_journal': 0.06,        # what a party monster did this run
    'location_description': 0.05
}

# Even on tiny context windows, flexible blocks keep at least this much
MIN_FLEXIBLE_CHARS = 600

# Blocks that grow over time keep their TAIL (the most recent events
# matter); description blocks keep their HEAD (the opening lines matter)
_TAIL_BLOCKS = ('dungeon_log', 'battle_log', 'dialogue_history', 'turn_history',
                'monster_memories', 'run_journal', 'chat_history', 'last_run_log')

TRUNCATION_MARKER = '(...earlier events trimmed...)'

def get_context_size_tokens() -> int:
    """The loaded model's context window, from .env (same key core.py uses)"""
    try:
        return int(os.getenv('LLM_CONTEXT_SIZE', '4096'))
    except (TypeError, ValueError):
        return 4096

def get_context_fill_percent() -> float:
    """How much of the window prompts may fill (developer knob, .env)"""
    try:
        fill = float(os.getenv('LLM_CONTEXT_FILL_PERCENT',
                               str(DEFAULT_CONTEXT_FILL_PERCENT)))
    except (TypeError, ValueError):
        fill = DEFAULT_CONTEXT_FILL_PERCENT
    # Clamp to sanity - below 0.3 nothing useful fits, above 1.0 lies
    return min(max(fill, 0.3), 1.0)

# Monster detail tiers: how much of a monster's persona/CMDTS enters prompt
# blocks that hold SEVERAL monsters (party details, battle sides). Binned by
# the model's context window. Single-speaker dialogue prompts ignore the bin
# and always use the full block for the monster that is speaking.
#   compact  (< 6144)  - identity line, stats, description, traits, wish
#   standard (< 12288) - + voice, tastes, persuasion rubric, habitat/diet line
#   full     (>= 12288) - everything, including beliefs, fears, bonds, class
def resolve_detail_tier() -> str:
    """The monster-detail tier for multi-monster blocks on the CURRENT model"""
    context_size = get_context_size_tokens()
    if context_size < 6144:
        return 'compact'
    if context_size < 12288:
        return 'standard'
    return 'full'

def get_prompt_char_budget() -> int:
    """Characters available for the whole prompt after reserving the response"""
    filled_window = int(get_context_size_tokens() * get_context_fill_percent())
    usable_tokens = max(filled_window - RESERVED_RESPONSE_TOKENS, 512)
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
