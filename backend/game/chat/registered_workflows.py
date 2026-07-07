print(f"🔍 Loading {__file__.split('LlmMonsterHunter', 1)[-1]}")

from typing import Any, Callable

from backend.core.utils.responses import error_response, success_response
from backend.core.utils.validation import require_keys
from backend.core.workflow_registry import register_workflow


@register_workflow()
def chat_with_monster(context: dict, on_update: Callable[[str, dict[str, Any]], None]) -> dict:
    """
    One exchange in the home-base chat: store the adventurer's line,
    stream the monster's in-character reply (the frontend follows
    chat_text_generation_id), store the reply, and queue housekeeping
    (memory extraction + rolling summaries) when thresholds are hit -
    housekeeping runs AFTER this workflow so the player never waits on it.
    """

    workflow_name = 'chat_with_monster'
    # "context" should have the following keys:
    required_keys = ["monster_id", "message"]

    step = "initialize_workflow"
    progress_data = {}

    try:
        from backend.game.chat import manager
        from backend.game.chat.generator import queue_chat_reply, wait_for_streamed_text
        from backend.models.monster import Monster

        # Step 0 - validate required keys and eligibility
        step = "validate_context"
        on_update(step, progress_data)
        require_keys(context, required_keys)

        monster_id = int(context['monster_id'])
        message = str(context['message']).strip()

        eligibility_error = manager.chat_eligibility_error(monster_id)
        if eligibility_error:
            raise Exception(eligibility_error)

        monster = Monster.get_monster_by_id(monster_id)

        # Step 1 - the adventurer's words join the thread
        step = "record_player_message"
        on_update(step, progress_data)
        manager.record_player_message(monster_id, message)

        # Step 2 - queue the streamed reply and hand its id to the frontend
        step = "queue_reply"
        on_update(step, progress_data)
        chat_text_generation_id = queue_chat_reply(monster, message, workflow_name)
        progress_data.update(
            {"chat_text_generation_id": chat_text_generation_id, "monster_id": monster_id}
        )

        step = "emit_generation_id"
        on_update(step, progress_data)

        # Step 3 - wait for the full reply (the player is already reading
        # the stream) and make it part of the thread
        step = "await_reply"
        on_update(step, progress_data)
        reply = wait_for_streamed_text(chat_text_generation_id)

        step = "record_monster_message"
        on_update(step, progress_data)
        manager.record_monster_message(monster_id, reply)

        # Step 4 - housekeeping (memory extraction, rolling summaries)
        # queues behind this workflow when due
        step = "queue_housekeeping"
        on_update(step, progress_data)
        manager.queue_housekeeping_if_due(monster_id)

        return success_response(
            {"monster_id": monster_id, "monster_name": monster.name, "reply": reply}
        )

    except Exception as e:
        return error_response({'failed_at': step, 'completed_work': progress_data, 'error': str(e)})


@register_workflow()
def chat_housekeeping(context: dict, on_update: Callable[[str, dict[str, Any]], None]) -> dict:
    """
    Behind-the-scenes pass over one monster's thread, queued by
    chat_with_monster when thresholds are hit:
    1. MEMORY EXTRACTION - review the unreviewed stretch and keep 0-3
       moments that will matter later (source recorded in details).
       The watermark advances even when nothing was worth keeping;
       a FAILED call leaves it put so the stretch retries next time.
    2. ROLLING SUMMARY - condense ONE batch of the oldest un-condensed
       lines so indefinite chats stay affordable on small windows.
    """

    workflow_name = 'chat_housekeeping'
    # "context" should have the following keys:
    required_keys = ["monster_id"]

    step = "initialize_workflow"
    progress_data = {}

    try:
        from backend.game.chat import manager
        from backend.game.chat.generator import extract_chat_memories
        from backend.game.chat.manager import CHAT_SETTINGS, speaker_display_name
        from backend.game.memory.manager import write_memory
        from backend.game.utils.rolling_summary import plan_batch, summarize_lines
        from backend.models.chat_message import ChatMessage
        from backend.models.chat_summary import ChatSummary
        from backend.models.chat_thread import ChatThread
        from backend.models.monster import Monster

        step = "validate_context"
        on_update(step, progress_data)
        require_keys(context, required_keys)

        monster_id = int(context['monster_id'])
        monster = Monster.get_monster_by_id(monster_id)
        if not monster:
            raise Exception(f"Monster {monster_id} not found")

        # ===== 1. MEMORY EXTRACTION =====
        memories_saved = []
        if manager.extraction_due(monster_id):
            step = "extract_memories"
            on_update(step, progress_data)

            watermark = ChatThread.extraction_watermark(monster_id)
            segment = ChatMessage.after_id(
                monster_id, watermark, limit=CHAT_SETTINGS['extract_segment_max']
            )
            extracted = extract_chat_memories(monster, segment, workflow_name)

            if extracted is not None:
                after_run = manager.last_run_number()
                for memory in extracted:
                    details = {
                        'source': 'home_chat',
                        'message_span': [segment[0].id, segment[-1].id],
                    }
                    if after_run:
                        details['after_run_number'] = after_run
                    write_memory(monster_id, memory['kind'], memory['content'], details)
                    memories_saved.append(memory)
                # Reviewed - even an empty result means "nothing worth keeping"
                ChatThread.advance_extraction_watermark(monster_id, segment[-1].id)

                # A talk that produced real memories deepens the bond
                if memories_saved:
                    from backend.game.monster.affinity import step_affinity

                    step_affinity(monster_id, 'campfire_chat')

        progress_data.update({"memories_saved": len(memories_saved)})

        # ===== 2. ROLLING SUMMARY (one batch at most) =====
        condensed = False
        covered = ChatMessage.count_through_id(monster_id, ChatSummary.last_through_id(monster_id))
        total = ChatMessage.count_for_monster(monster_id)
        batch = plan_batch('chat_history', total, covered)
        if batch:
            step = "condense_batch"
            on_update(step, progress_data)
            start, end = batch
            batch_messages = ChatMessage.slice_for_monster(monster_id, start, end - start)
            if batch_messages:
                prior_rows = ChatSummary.for_monster(monster_id)
                prior = prior_rows[-1].text if prior_rows else None
                lines = [
                    f'{speaker_display_name(m.role, monster.name)}: "{m.text}"'
                    for m in batch_messages
                ]
                summary_text = summarize_lines(
                    'chat_history', lines, workflow_name, prior_summary=prior
                )
                if summary_text:
                    ChatSummary.add(monster_id, batch_messages[-1].id, summary_text)
                    condensed = True

        return success_response(
            {"monster_id": monster_id, "memories": memories_saved, "condensed": condensed}
        )

    except Exception as e:
        return error_response({'failed_at': step, 'completed_work': progress_data, 'error': str(e)})
