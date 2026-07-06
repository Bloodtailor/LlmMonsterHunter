# Context Limits - Per-Block Character Budgets for LLM Prompts
# Local models have small context windows. Every block of context that goes
# into a prompt (the dungeon log, dialogue history, party details...) gets
# clamped to a budget here so no single block - especially the ever-growing
# logs - can crowd the rest of the prompt out of the window.

# Character budgets per context block. Tune freely - one place to balance
# how much of the prompt each kind of context is allowed to occupy.
CONTEXT_CHAR_LIMITS = {
    'dungeon_log': 3000,        # the rolling story of the run
    'dialogue_history': 1500,   # the active encounter conversation
    'battle_log': 1200,         # recent battle narrations
    'party_details': 1500,      # who the party is
    'monster_details': 1500,    # one monster or a side of monsters
    'location_description': 600
}

# Blocks that grow over time keep their TAIL (the most recent events matter);
# identity/description blocks keep their HEAD (the opening lines matter).
_TAIL_BLOCKS = ('dungeon_log', 'dialogue_history', 'battle_log')

TRUNCATION_MARKER = '(...earlier events trimmed...)'

def clamp_context(block_name: str, text: str) -> str:
    """
    Clamp a context block to its character budget.
    Unknown block names pass through untouched.
    """
    if not text:
        return text

    limit = CONTEXT_CHAR_LIMITS.get(block_name)
    if not limit or len(text) <= limit:
        return text

    if block_name in _TAIL_BLOCKS:
        # Keep the most recent events, cut on a line break where possible
        clipped = text[-limit:]
        newline_index = clipped.find('\n')
        if 0 <= newline_index < limit // 4:
            clipped = clipped[newline_index + 1:]
        return f"{TRUNCATION_MARKER}\n{clipped}"

    # Identity/description blocks: keep the start
    return text[:limit].rstrip() + '...'
