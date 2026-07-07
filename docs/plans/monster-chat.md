# Monster Chat & Rolling Summaries — Implementation Plan

**Status:** IN PROGRESS (July 2026, branch `feature/monster-chat`).
**Commit prefix:** `Chat-M#`

The player can sit down with any monster that follows them — at home base,
outside the dungeon — and just talk. Conversations can run forever, so the
game learns to keep them affordable: old history gets condensed into
summaries by the LLM in batches while recent lines stay verbatim, and only
the moments that MATTER become permanent memories (with their source
recorded). Those memories then flow through the existing memory system into
battles, growth reflections, and future encounters.

## 1. Goal and locked decisions

1. **Home-base chat** — a new game screen, reachable from Home Base, where
   the player picks any monster from the following list (party included) and
   talks with it freely. One PERSISTENT thread per monster for the whole
   save — a relationship, not sessions. Replies stream token-by-token.
   Chatting is blocked while a dungeon run is active.
2. **Memories from conversation** — after every few exchanges an extraction
   pass (separate, low-temperature LLM call) reviews the unreviewed segment
   and saves 0–3 memories ONLY when something will matter later:
   valuable information, character/relationship development, or world
   building. Most exchanges produce NOTHING — the empty list is the
   expected answer. Each memory records its **source** in `details`
   (`source: 'home_chat'`, the covered message span, an excerpt, and the
   run number it followed). New memory kinds (monster's perspective):
   `confided`, `grew_closer`, `shared_lore`, `learned_fact`, `voiced_wish`.
3. **Memories change the game** — chat memories ride the SAME
   `monster_memories` rows the rest of the game reads:
   - growth reflections already receive the memory block → leveling;
   - party/ally prompt blocks NOW carry each member's freshest memories
     (tier-gated: 1/2/3 lines on compact/standard/full) → how they fight
     and how they meet other monsters;
   - encounter speaker blocks already carry memories → dialogue.
4. **Last run as context** — when a dungeon run closes (victory OR defeat)
   the run's dungeon log (raw entries + its rolling summaries) is
   snapshotted to the `last_run_log` GlobalVariable before the state wipe.
   Chats compose it into a budgeted context block, so the monster can talk
   about what just happened down there.
5. **Rolling summaries everywhere** — a generic utility upgrades ALL
   growing histories (chat thread, dungeon log, battle log): when enough
   entries pile up beyond the keep-verbatim window, ONE batch of the oldest
   uncovered entries is condensed into a summary by the LLM (at most one
   batch per workflow, so latency never stacks). Raw entries are KEPT —
   single-source prompts can still read far more verbatim than
   multi-source prompts. Prompt composition = all summaries (oldest first)
   + verbatim tail, then the usual budget clamp.
6. **Developer-tunable budgets** — everything lives in two dicts:
   `FLEXIBLE_BLOCK_SHARES` (context_limits.py, gains `chat_history` and
   `last_run_log`) and `SUMMARY_SOURCES` (rolling_summary.py: keep-recent /
   batch-min / batch-max per source). New env knob
   `LLM_CONTEXT_FILL_PERCENT` (default 1.0) shrinks the usable window for
   models that degrade when nearly full. Context sizes 4096 / 8192 / 1M
   all flow from the existing `LLM_CONTEXT_SIZE`.

Out of scope V1: chatting while inside the dungeon, group chats, monster-
initiated messages, memory browsing UI beyond what exists, retroactive
summarization of other saves' logs.

LLM discipline (7B/4096 ctx): replies are plain text; extraction and
summaries are flat JSON / short text with code validation and deterministic
fallbacks; a failed extraction or summary NEVER breaks the chat turn.

## 2. Data model (new tables only — NO new columns on existing tables, NO DB reset)

- `chat_messages` — one spoken line. `monster_id` (FK, idx), `role`
  (`player` | `monster`), `text` (Text). Ordered by id.
- `chat_summaries` — one condensed batch. `monster_id` (FK, idx),
  `through_message_id` (int: covers all messages with id ≤ this),
  `text` (Text).
- `chat_threads` — one row per monster ever chatted with. `monster_id`
  (FK, unique), `last_extracted_message_id` (int, default 0) — the
  memory-extraction watermark.

All three register in `models/core.py:create_tables()` and
`tests/reset_db.py:import_all_models()`; `db.create_all()` adds them to a
live save without touching existing tables.

GlobalVariable additions (no schema): `last_run_log`
(`{run_id, run_number, result, entries[], summaries[], saved_at}`);
`dungeon_state` gains `dungeon_log_summaries: [{'through': int, 'text'}]`;
`battle_state` gains `log_summaries` (same shape, `through` counts entries).

## 3. Rolling summary utility (`backend/game/utils/rolling_summary.py`)

- `SUMMARY_SOURCES = {'chat_history': {...}, 'dungeon_log': {...},
  'battle_log': {...}}` — per source: `keep_recent` (entries that stay
  verbatim), `batch_min` (uncovered entries beyond keep_recent needed to
  trigger), `batch_max` (entries condensed per call), `label` (prose flavor
  fed to the template).
- `plan_batch(source, total, covered) -> (start, end) | None` — pure math.
- `summarize_lines(source, lines, workflow_name) -> str | None` — one
  `condense_history` LLM call; None on failure (coverage does NOT advance —
  it simply retries at the next trigger).
- `compose_history(source, summary_texts, verbatim_lines, block_name) -> str`
  — `(earlier, condensed)` header + summaries + `(recent)` + verbatim tail,
  clamped by `clamp_context(block_name, ...)` (tail-keeping already
  prioritizes recency on tiny windows).

Wiring (max ONE batch per workflow, always inside try/except):
- dungeon log: end of `choose_path`, `continue_exploring`,
  `respond_to_monster`, `setup_camp`;
- battle log: end of `battle_turn` (battle storage stops slicing to
  `RECENT_LOG_SIZE`; a generous hard cap guards memory);
- chat: end of `chat_with_monster`.

## 4. Chat backend (`backend/game/chat/`)

- `manager.py` — eligibility (following ∪ active party, fully generated,
  not mid-run), message/thread/summary access, unextracted counting,
  context composition (chat block, last-run block).
- `generator.py` — `stream_chat_reply` (build_and_stream + poll the AI
  queue for the final text), `extract_chat_memories`
  (build_and_generate, JSON), block builders.
- `registered_workflows.py` — `chat_with_monster`:
  validate → store player line → `emit_generation_id`
  (`chat_text_generation_id`) → stream reply → store monster line →
  maybe extract memories (watermark advances even when 0 saved) →
  maybe summarize one batch → result
  `{reply, memories[], monster_id}`.

Templates: `chat_generation.json` (`home_chat_reply` text ~250tok t0.85;
`chat_memory_extraction` JSON t0.4, `{"memories": [{"kind", "content"}]}`,
hard-capped at 3, kinds code-validated) and `summary_generation.json`
(`condense_history` text ~200tok t0.4).

Routes/service: `chat_routes.py` + `chat_service.py` —
`GET /api/chat/<monster_id>/history?limit=&before_id=` (sync; messages +
thread info), `POST /api/chat/<monster_id>/message` (queues the workflow).
Registered in `app.py`; package imported in `game/__init__.py`.

Memory plumbing: the five chat kinds join `MEMORY_KINDS`;
`_format_memory_line` prefixes `[a talk at home]` (from `details.source`)
instead of `[before this journey]`; `write_memory` keeps stamping runs for
in-dungeon memories, chat stamps `after_run_number`.

## 5. Frontend

- `GameScreenRouter` gains `monster-chat`; Home Base gains a
  "💬 Campfire Chat" button.
- `screens/game/MonsterChatScreen.js` + `components/chat/`:
  partner picker (following monsters), thread view (mirrors
  MonsterDialogueBox speech styling), input form, token streaming via
  `useStreamedGeneration('chat_text_generation_id')`, memory toasts fed by
  the existing `monster.memory_added` SSE event, history loaded from the
  new endpoint (older pages via `before_id`).
- `api/services/chat.js` co-located service following `dungeon.js`.

## 6. Tests & docs

`backend/tests/test_chat_and_summaries.py` (offline, dev DB, LLM stubbed by
monkeypatching generator seams): plan_batch math, compose_history,
fill-percent knob, message/thread storage + pagination, extraction
validation (kind filtering, cap, empty-list path, source details), memory
line prefix, last-run snapshot on victory/defeat close paths, dungeon and
battle log composition with summaries, eligibility rules.

Docs: new `notes_for_claude/backend-api/chat.md`; index, events-and-sse
(workflow type + step key), data-models (ChatMessage/ChatThread), and
dungeon-and-battle (rolling summaries note) updated.

## 7. Deviations log

(recorded as they happen)
