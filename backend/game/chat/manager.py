# Chat Manager - Home-Base Conversations with Following Monsters
# Owns who can be talked to, the persistent per-monster thread (messages,
# rolling summaries, extraction watermark), and the composition of chat
# context blocks for prompts. The LLM calls themselves live in
# generator.py; the workflow lives in registered_workflows.py.

from typing import Any, Optional

# Developer knobs for the chat loop
CHAT_SETTINGS = {
    'extract_after_messages': 8,   # unreviewed lines that trigger a memory pass
    'extract_segment_max': 24,     # most lines one extraction pass reviews
    'max_memories_per_pass': 3,    # hard cap on memories saved per pass
    'history_page_size': 50,       # messages per history page (API)
    'player_text_max_chars': 500   # matches the dungeon dialogue cap
}

# ===== ELIGIBILITY =====

def chat_eligibility_error(monster_id: int) -> Optional[str]:
    """
    Why this monster cannot chat right now, or None if it can.
    Chat happens at home base: any fully-generated monster on the
    following list (the active party is drawn from it) qualifies,
    but never during a dungeon run.
    """
    try:
        from backend.game.dungeon import manager as dungeon
        from backend.models.active_party import ActiveParty
        from backend.models.following_monsters import FollowingMonster
        from backend.models.monster import Monster

        if dungeon.is_in_dungeon():
            return "The party is in the dungeon - conversations wait for home base"

        monster = Monster.get_monster_by_id(int(monster_id))
        if not monster:
            return f"Monster {monster_id} not found"
        if monster.generation_stage != 'complete':
            return f"{monster.name} is still taking shape - try again shortly"

        familiar_ids = set(FollowingMonster.get_following_monster_ids())
        familiar_ids.update(ActiveParty.get_party_monster_ids())
        if int(monster_id) not in familiar_ids:
            return f"{monster.name} is not following the party"

        return None
    except Exception as e:
        return f"Could not check chat eligibility: {e}"

# ===== THREAD ACCESS =====

def record_player_message(monster_id: int, text: str):
    """Store one line the adventurer typed. Returns the row or None."""
    from backend.models.chat_message import ChatMessage
    return ChatMessage.add(monster_id, 'player', text)

def record_monster_message(monster_id: int, text: str):
    """Store one line the monster spoke. Returns the row or None."""
    from backend.models.chat_message import ChatMessage
    return ChatMessage.add(monster_id, 'monster', text)

def get_history_page(monster_id: int, limit: int = None, before_id: int = None) -> dict[str, Any]:
    """One display page of the thread (oldest first) plus paging info"""
    from backend.models.chat_message import ChatMessage

    page_size = int(limit or CHAT_SETTINGS['history_page_size'])
    messages = ChatMessage.page_for_monster(monster_id, limit=page_size, before_id=before_id)
    oldest_id = messages[0].id if messages else None
    has_more = False
    if oldest_id:
        has_more = bool(ChatMessage.page_for_monster(monster_id, limit=1, before_id=oldest_id))
    return {
        'messages': [m.to_dict() for m in messages],
        'has_more': has_more,
        'total': ChatMessage.count_for_monster(monster_id)
    }

# ===== PROMPT CONTEXT =====

def speaker_display_name(role: str, monster_name: str) -> str:
    """How a stored chat role reads inside a prompt line"""
    return 'The adventurer' if role == 'player' else monster_name

def build_chat_history_block(monster_id: int, monster_name: str) -> str:
    """
    The whole relationship in one clamped block: condensed old stretches
    + recent lines verbatim (rolling summaries keep this affordable no
    matter how long the chats run).
    """
    from backend.game.utils.rolling_summary import compose_history
    from backend.models.chat_message import ChatMessage
    from backend.models.chat_summary import ChatSummary

    summaries = [
        {'through': s.through_message_id, 'text': s.text}
        for s in ChatSummary.for_monster(monster_id)
    ]
    covered_id = ChatSummary.last_through_id(monster_id)
    recent = ChatMessage.after_id(monster_id, covered_id)
    lines = [
        f'{speaker_display_name(m.role, monster_name)}: "{m.text}"'
        for m in recent
    ]
    return compose_history(
        'chat_history', summaries, lines, 'chat_history',
        empty_text="They have not talked at home base before - this is their first real conversation."
    )

def build_last_run_block() -> str:
    """The previous dungeon run's log as a clamped context block"""
    from backend.game.dungeon.manager import get_last_run_log
    from backend.game.utils.rolling_summary import compose_history, covered_count

    snapshot = get_last_run_log()
    if not snapshot or not snapshot.get('entries'):
        return "No dungeon run has finished yet."
    summaries = snapshot.get('summaries', [])
    entries = snapshot.get('entries', [])
    return compose_history(
        'dungeon_log', summaries, entries[covered_count(summaries):],
        'last_run_log',
        empty_text="No dungeon run has finished yet."
    )

def build_last_run_status() -> str:
    """One line naming the last run and how it ended"""
    from backend.game.dungeon.manager import get_last_run_log

    snapshot = get_last_run_log()
    if not snapshot:
        return "The party has not ventured into the dungeon yet."
    result_words = {
        'victory_exit': 'the party walked out alive',
        'defeat': 'the party was defeated and barely escaped',
        'abandoned': 'the run ended abruptly'
    }
    run_number = snapshot.get('run_number')
    run_name = f"run {run_number}" if run_number else "the last run"
    ending = result_words.get(snapshot.get('result'), 'the run ended')
    return f"What follows is the log of {run_name}, where {ending}:"

def last_run_number() -> Optional[int]:
    """The number of the most recently finished run (source stamping)"""
    from backend.game.dungeon.manager import get_last_run_log
    snapshot = get_last_run_log() or {}
    return snapshot.get('run_number')

# ===== HOUSEKEEPING TRIGGERS (extraction + summaries) =====

def extraction_due(monster_id: int) -> bool:
    """Enough unreviewed lines for a memory-extraction pass?"""
    from backend.models.chat_message import ChatMessage
    from backend.models.chat_thread import ChatThread

    watermark = ChatThread.extraction_watermark(monster_id)
    unreviewed = ChatMessage.after_id(
        monster_id, watermark, limit=CHAT_SETTINGS['extract_after_messages']
    )
    return len(unreviewed) >= CHAT_SETTINGS['extract_after_messages']

def summary_batch_due(monster_id: int) -> bool:
    """Enough old un-condensed lines for a rolling-summary batch?"""
    from backend.game.utils.rolling_summary import plan_batch
    from backend.models.chat_message import ChatMessage
    from backend.models.chat_summary import ChatSummary

    covered = ChatMessage.count_through_id(
        monster_id, ChatSummary.last_through_id(monster_id)
    )
    total = ChatMessage.count_for_monster(monster_id)
    return plan_batch('chat_history', total, covered) is not None

def queue_housekeeping_if_due(monster_id: int) -> None:
    """
    Queue a chat_housekeeping workflow (memory extraction + one summary
    batch) when thresholds are hit. The sequential worker runs it AFTER
    the reply the player is waiting on. Never raises.
    """
    try:
        if not (extraction_due(monster_id) or summary_batch_due(monster_id)):
            return
        from backend.workflow.workflow_gateway import request_workflow
        request_workflow('chat_housekeeping', context={'monster_id': int(monster_id)})
    except Exception as e:
        print(f"❌ Failed to queue chat housekeeping for monster {monster_id}: {e}")
