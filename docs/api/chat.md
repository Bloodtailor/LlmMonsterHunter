# Chat API (home-base monster conversations)

Talk with any monster on the following list while OUTSIDE the dungeon.
One PERSISTENT thread per monster for the whole save — a relationship,
not sessions. Replies stream over SSE; the moments that matter become
permanent `monster_memories` rows (with their source recorded) that then
shape battles, growth, and future encounters. Design doc:
`docs/plans/monster-chat.md`.

Read the [index](README.md) workflow model first.

## POST /api/chat/:monster_id/message
**Request:** `{ "message": string }` (non-empty, ≤500 chars)
Queues a `chat_with_monster` workflow. Refused (400) while a dungeon run
is active **backend-side** (navigating the UI home does NOT end a run —
only exiting, defeat, re-entering, or `POST /dungeon/abandon` does; the
Campfire Chat screen checks `GET /dungeon/state` first and offers the
abandon action), for monsters not on the following list / active party,
and for monsters still generating.
**Success:** `{ "success": true, "workflow_id": number }`
**During the workflow:** step `emit_generation_id` carries
`data.chat_text_generation_id` — follow `llm.generation.update` events
with that id to stream the reply token by token.
**`workflow.completed` result:** `{ success, monster_id, monster_name, reply }`
On failure (`workflow.failed`) the player's line stays in the thread,
unanswered — resending is natural and nothing double-stores.

After the reply, when thresholds are hit, the backend queues a
`chat_housekeeping` workflow (the player never waits on it):
1. **Memory extraction** — a low-temperature pass reviews the unreviewed
   stretch (watermark in `chat_threads`) and saves **0–3** memories, only
   for things that will matter later: valuable information
   (`learned_fact`), self-revelation (`confided`), relationship shifts
   (`grew_closer`), world building (`shared_lore`), spoken wants
   (`voiced_wish`). An EMPTY result is the normal outcome and advances
   the watermark; a failed call leaves it put (the stretch retries).
   Each memory's `details` records the source:
   `{ source: "home_chat", message_span: [firstId, lastId], after_run_number? }`,
   and each fires `monster.memory_added` live.
2. **Rolling summary** — one batch of the oldest un-condensed lines is
   condensed into a `chat_summaries` row (see *Rolling summaries* in
   [Dungeon & Battle](dungeon-and-battle.md)); raw messages are never
   deleted.

Chat prompts also receive the **last dungeon run's log** (snapshotted at
run close, victory or defeat) so the monster can talk about what just
happened down there.

## GET /api/chat/:monster_id/history
**Query params:** `limit?` (1–200, default 50), `before_id?` (page older
than this message id — pages walk backward from the newest)
Synchronous.
**Success:**
```json
{ "success": true, "monster_id": number, "monster_name": string,
  "messages": [ { "id": number, "monster_id": number,
                  "role": "player"|"monster", "text": string,
                  "created_at": string, "updated_at": string } ],
  "has_more": boolean, "total": number }
```
**Error (400):** unknown monster, bad limit/before_id.

## Storage

- `chat_messages` — every line ever spoken (never deleted)
- `chat_summaries` — condensed old stretches; `through_message_id` marks
  coverage
- `chat_threads` — per-monster housekeeping (extraction watermark)

Developer knobs live in `backend/game/chat/manager.py` (`CHAT_SETTINGS`:
extraction cadence, per-pass memory cap, page size) and
`backend/game/utils/rolling_summary.py` (`SUMMARY_SOURCES.chat_history`).
