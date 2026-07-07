# Chat Generator - LLM Calls for Home-Base Conversations
# Two calls: the streamed in-character reply, and the low-temperature
# memory-extraction pass. Replies stream to the frontend token by token
# AND the final text is awaited here so it can be stored in the thread.
# Extraction output is strictly validated - the LLM proposes, code decides.

import time
from typing import Any, Optional

from backend.game.chat.manager import (
    CHAT_SETTINGS,
    build_chat_history_block,
    build_last_run_block,
    build_last_run_status,
)
from backend.game.utils import build_and_generate, build_and_stream

# Memory kinds an extraction pass may produce (anything else is dropped)
CHAT_MEMORY_KINDS = ('confided', 'grew_closer', 'shared_lore', 'learned_fact', 'voiced_wish')

# How long to wait for the streamed reply before giving up (the AI queue
# has its own 600s guard; this stays under it)
REPLY_TIMEOUT_SECONDS = 540

def build_chat_speaker_block(monster) -> str:
    """The monster as FULL context - a speaking monster always gets its
    whole persona, secret included (never shown to the player)"""
    from backend.game.monster.context_builder import build_speaker_block
    return build_speaker_block(monster)

def build_chat_memories_block(monster_id: int) -> str:
    """Everything the monster remembers, as its own clamped block"""
    from backend.game.memory.manager import build_memory_block
    return build_memory_block(monster_id)

def queue_chat_reply(monster, player_message: str, workflow_name: str) -> int:
    """
    Queue the streamed in-character reply. Returns the generation_id the
    frontend follows for token streaming (and wait_for_streamed_text
    resolves into the final text).
    """
    return build_and_stream('home_chat_reply', workflow_name, {
        'monster_details': build_chat_speaker_block(monster),
        'monster_memories': build_chat_memories_block(monster.id),
        'last_run_status': build_last_run_status(),
        'last_run_log': build_last_run_block(),
        'chat_history': build_chat_history_block(monster.id, monster.name),
        'player_message': player_message
    })

def wait_for_streamed_text(generation_id: int, timeout: int = REPLY_TIMEOUT_SECONDS) -> str:
    """
    Wait for a streamed generation to finish and return its final text.
    Raises on failure or timeout - the chat workflow surfaces that as a
    failed workflow (the player's line stays in the thread, unanswered).
    """
    from backend.ai.queue import get_ai_queue

    queue = get_ai_queue()
    started = time.time()
    while time.time() - started < timeout:
        status = queue.get_request_status(generation_id)
        if not status:
            raise Exception(f"Generation {generation_id} vanished from the AI queue")
        if status['status'] == 'completed':
            result = status.get('result') or {}
            if result.get('success') is False:
                raise Exception(result.get('error') or 'Generation failed')
            text = str(result.get('text') or '').strip()
            if not text:
                raise Exception('The reply came back empty')
            return text
        if status['status'] == 'failed':
            raise Exception(status.get('error') or 'Generation failed')
        time.sleep(0.5)

    raise TimeoutError(f"Chat reply timed out after {timeout} seconds")

def extract_chat_memories(monster, segment_messages: list[Any], workflow_name: str) -> Optional[list[dict[str, str]]]:
    """
    Run one memory-extraction pass over a stretch of conversation.
    Returns a validated list of {'kind', 'content'} (often EMPTY - most
    talk deserves no memory), or None when the LLM call itself failed
    (the caller must NOT advance the watermark then).
    """
    from backend.game.chat.manager import speaker_display_name
    from backend.game.memory.manager import get_memory_lines
    from backend.game.monster.context_builder import build_monster_block

    try:
        segment_lines = "\n".join(
            f'{speaker_display_name(m.role, monster.name)}: "{m.text}"'
            for m in segment_messages
        )
        existing = get_memory_lines(monster.id, cap=8)
        result = build_and_generate('chat_memory_extraction', workflow_name, {
            'monster_details': build_monster_block(monster),
            'existing_memories': "\n".join(f"- {line}" for line in existing) or "Nothing yet.",
            'conversation_segment': segment_lines
        })
    except Exception as e:
        print(f"❌ Chat memory extraction failed for monster {monster.id}: {e}")
        return None

    # The LLM proposes; code validates, then caps (garbage entries must
    # not consume one of the few slots)
    memories = []
    for entry in (result.get('memories') or []):
        if len(memories) >= CHAT_SETTINGS['max_memories_per_pass']:
            break
        if not isinstance(entry, dict):
            continue
        kind = str(entry.get('kind') or '').strip().lower()
        content = str(entry.get('content') or '').strip()
        if not content:
            continue
        if kind not in CHAT_MEMORY_KINDS:
            kind = 'confided'  # closest safe default for chat moments
        memories.append({'kind': kind, 'content': content[:600]})
    return memories
