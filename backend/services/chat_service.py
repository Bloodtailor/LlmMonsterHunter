# Chat Service - Trust Boundary for Home-Base Monster Chat
# Validates chat requests (eligible monster, sane message, not mid-run)
# before queueing the chat workflow; history reads are synchronous.

from typing import Any

from backend.core.utils.responses import error_response, success_response
from backend.game.chat import manager
from backend.game.chat.manager import CHAT_SETTINGS
from backend.workflow.workflow_gateway import request_workflow


def send_message(monster_id, message) -> dict[str, Any]:
    """
    Speak to a following monster at home base. Queues the
    chat_with_monster workflow; the reply streams over SSE.
    """

    try:
        monster_id = int(monster_id)
    except (TypeError, ValueError):
        return error_response("A valid monster_id is required")

    eligibility_error = manager.chat_eligibility_error(monster_id)
    if eligibility_error:
        return error_response(eligibility_error)

    text = str(message or '').strip()
    if not text:
        return error_response("A message is required")
    if len(text) > CHAT_SETTINGS['player_text_max_chars']:
        return error_response(
            f"Message too long (max {CHAT_SETTINGS['player_text_max_chars']} characters)"
        )

    success, workflow_id = request_workflow(
        workflow_type="chat_with_monster",
        context={"monster_id": monster_id, "message": text}
    )

    if success:
        return success_response({'workflow_id': workflow_id})
    return error_response("Failed to queue chat workflow")

def get_history(monster_id, limit=None, before_id=None) -> dict[str, Any]:
    """
    One page of a monster's chat thread (synchronous). Walks backward
    from the newest message; pass before_id to load older pages.
    """

    try:
        monster_id = int(monster_id)
    except (TypeError, ValueError):
        return error_response("A valid monster_id is required")

    try:
        page_limit = int(limit) if limit else None
        if page_limit is not None and not (1 <= page_limit <= 200):
            return error_response("limit must be between 1 and 200")
    except (TypeError, ValueError):
        return error_response("limit must be a number")

    try:
        before = int(before_id) if before_id else None
    except (TypeError, ValueError):
        return error_response("before_id must be a number")

    from backend.models.monster import Monster
    monster = Monster.get_monster_by_id(monster_id)
    if not monster:
        return error_response(f"Monster {monster_id} not found")

    page = manager.get_history_page(monster_id, limit=page_limit, before_id=before)
    return success_response({
        'monster_id': monster_id,
        'monster_name': monster.name,
        **page
    })
