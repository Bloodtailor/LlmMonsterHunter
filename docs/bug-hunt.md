# Latent-Bug Hunt — battle state machine, SSE/workflow lifecycle, context budgets

**Written 2026-07-07.** A skeptical, line-level read of the trickiest
correctness areas, hunting for bugs that only show up in play. Every
finding names file:line, the in-play scenario, and the fix. Findings are
ranked by (likelihood × pain). Section 2 lists hypotheses that were
**checked and cleared** — do not "fix" those.

**Overall verdict:** the defensive engineering is strong — every LLM
call has a deterministic fallback, `battle_turn` has an unstick-on-error
recovery handler, the fairness/softlock valves are real, and the
sequential workflow worker eliminates whole classes of races. The bugs
that survived scrutiny cluster in the *plumbing* (SSE identity, queue
retention, stream payloads), not the game rules.

---

## 1. Confirmed / high-confidence findings

### 1.1 SSE connection IDs collide within one millisecond → silently dead event streams
**[backend/services/sse_service.py:81](backend/services/sse_service.py:81)** — HIGH

`connection_id = f"sse_{int(time.time() * 1000)}"`. Two connections
created in the same millisecond get the SAME id, and the second
`self._connections[connection_id] = connection` overwrites the first.
React 18's StrictMode dev double-mount (connect → disconnect →
reconnect, back-to-back) and any reconnect storm make same-ms creation
realistic.

**What the player sees:** the orphaned stream stays open — its
generator keeps yielding keep-alive pings, so the browser believes it
is connected — but it was replaced in the dict, so `broadcast_event`
never reaches it again: **the UI silently stops receiving game events
until a refresh.** Worse, when the orphaned stream's client finally
disconnects, its `finally: sse_service.remove_connection(connection.id)`
([sse_routes.py:47](backend/routes/sse_routes.py:47)) deletes the id —
which now belongs to the *surviving* connection, killing that one's
registration too.

**Fix:** `connection_id = f"sse_{uuid.uuid4().hex}"`. One line. While
there: `SSEConnection.send_event`'s `except` branch (sse_service.py:30)
is dead code — `put_nowait` on an unbounded `Queue` never raises — so
`active` is never set False by send failures and
`cleanup_dead_connections` can never find anything; harmless today, but
delete the misleading branch or bound the queue.

### 1.2 An unparseable impact word becomes a WOUND — healing that hurts
**[backend/game/battle/generator.py:283](backend/game/battle/generator.py:283)** — HIGH (gameplay correctness)

In `resolve_action`, when the referee's impact word is not in
`IMPACT_STEPS`, it coerces to `'light'` — one step toward
incapacitated. `'light'` is the right anchor for attacks, but this is
the same referee that judges **healing abilities and items**: a model
answering `"heal"`, `"heal_minor"`, `"restore"`, or `"healed_light"`
(all plausible near-misses of `heal_light`) turns a potion or a
soothing ability into a blow against its own target.

**In play:** rare and bewildering — "I used the healing salve on Ember
and she got WORSE." Because it needs a malformed word, it will strike
maybe 1-in-50 heals, exactly rare enough never to be reproduced.

**Fix (keep it word-ladder-pure):** in the invalid-word branch, first
try `if impact.startswith('heal'): impact = 'heal_light'`; otherwise
coerce to `'none'`, not `'light'`. Leave the total-failure `except`
fallback as-is (its fallback narration IS a strike, so `'light'`
matches). Note `resolve_freeform_action` (line 177) already coerces to
`'none'` — this fix just makes `resolve_action` equally safe.

### 1.3 Token streaming is O(n²): every chunk re-sends the full text over SSE
**[backend/ai/queue.py:204-211](backend/ai/queue.py:204)** — MEDIUM (performance, visible in play)

`on_stream` fires per content chunk with the FULL accumulated text
(`emit_llm_generation_update(partial_text=streaming_data, ...)`), and
`tokens_so_far=len(streaming_data.split())` re-splits the whole text
every chunk. An 800-token camp scene emits ~hundreds of events whose
payloads total megabytes through the event bus, the SSE queues, and the
CRA dev proxy — per generation. Long streams (camp scenes, chronicles,
evolution narrations) visibly slow as they grow.

**Fix (smallest safe):** throttle in `on_stream` — keep full-text
replace semantics (no frontend change) but emit at most every ~100ms
plus one final emit. Track `last_emit` in the closure. Optionally
replace the O(n) `split()` with a chunk counter. A delta-based protocol
is better long-term but touches the frontend event contract — do the
throttle first, it's 6 lines.

### 1.4 Both queues retain every item forever (memory + a misleading waiter)
**[backend/workflow/workflow_queue.py:72](backend/workflow/workflow_queue.py:72), [backend/ai/queue.py:82](backend/ai/queue.py:82)** — MEDIUM (long sessions)

`self._items` in BOTH the workflow queue and the AI queue only ever
grows. AI queue items keep their full `result` payloads — generated
text and image metadata — so a long play session accumulates every
generation ever made in process memory, and `get_queue_status()` walks
all of it on every call.

**Fix:** prune COMPLETED/FAILED items older than ~15 minutes on each
`add_*` (or every N adds). **Coupling to respect:**
`_wait_for_completion` ([backend/ai/gateway.py:199-237](backend/ai/gateway.py:199))
polls `get_request_status` every 0.5s for up to 600s and treats a
missing item as a fall-through to `TimeoutError` — so the prune
threshold must exceed the 600s waiter timeout (15 min is safe). While
in there: make the `if not status: break` path raise a distinct message
("generation record vanished") instead of the misleading
"timed out after 600 seconds".

### 1.5 A dropped DeepSeek stream returns partial text as success
**[backend/ai/llm/providers/deepseek.py:76-118](backend/ai/llm/providers/deepseek.py:76)** — MEDIUM

The stream loop catches all exceptions and keeps whatever arrived; only
EMPTY text fails. A connection dropped mid-generation therefore returns
`success: True` with half an answer. For JSON referee prompts the
downstream parser usually chokes and the caller's fallback saves the
day. But for **plain-text prompts the truncation is invisible**: a
battle summary cut mid-sentence gets appended to the dungeon log as
fact, a chronicle entry ends mid-thought and is persisted to the run's
history row forever.

**Fix:** the loop already knows the difference — set
`completed = True` when `payload == '[DONE]'` (or a chunk carries
`finish_reason`). If the loop exits without it, return
`_failure('DeepSeek stream ended early', ...)` — every caller already
has a fallback for failure, and a clean fallback beats a silently
truncated chronicle. (If you'd rather keep partials for streamed vanity
text, add `'truncated': True` to the result and let
`processor.py` decide per prompt type — but the simple fail is the
right default.)

### 1.6 The error-recovery path forfeits the player's turn
**[backend/game/battle/turn/player_phase.py:43-46](backend/game/battle/turn/player_phase.py:43) + [registered_workflows.py:38-52](backend/game/battle/registered_workflows.py:38)** — LOW-MEDIUM

`_resolve_player_turn` clears `pending_actor` and saves phase
`'processing'` BEFORE resolving anything. The recovery handler in
`battle_turn` correctly unsticks a failed turn — but by then
`pending_actor` is gone, so it lands on `phase = 'ready'`: the player's
monster loses its turn, and the next `battle_turn` runs the advance
loop, possibly handing the moment to an enemy. The referee LLM calls
can't raise (they have internal fallbacks), but DB hiccups, a missing
item id (`int(player_action.get('item_id'))` on a stale id,
player_phase.py:161), or a journal failure can.

**Fix:** don't clear `pending_actor` at entry — clear it after the
action resolves (just before the advance loop). Recovery then restores
`'awaiting_player_turn'` with the actor intact and the player simply
retries. Verify with the offline suite by making a stub referee raise
once.

### 1.7 Small defensive gaps (batch these)

- **[manager.py:314-318](backend/game/battle/manager.py:314)** —
  `derive_outcome` returns `'unresolved'` when the `allies` dict is
  EMPTY (the `if allies and ...` guard), and director.py:73-74 then
  `break`s, making `finish_battle` raise "ended without an outcome".
  Unreachable today (the player is always in the party), but one
  refactor away: make empty-allies mean `'defeat'`.
- **[ending.py:98](backend/game/battle/turn/ending.py:98)** — comment
  says a finished battle is a goal-check moment "won OR survived", but
  the code checks `if outcome == 'victory'` only. Decide which is true
  and align (the comment's version seems intended — a survived battle
  can satisfy "drive out what haunts the halls").
- **[workflow_queue.py DB rows]** — a backend restart mid-workflow
  leaves the `game_workflows` row `'pending'`/`'processing'` forever
  and the frontend waiting on an SSE completion that will never come.
  Cheap mitigation: on startup, mark all non-terminal rows `'failed'`
  with error "server restarted" (startup.py), so the dev table tells
  the truth after a crash.
- **[inference.py:101](backend/ai/llm/inference.py:101)** — the local
  provider sleeps 10ms per token ("for visibility"), capping the
  unsupported local path at ~100 tokens/s. Intentional once, silly on a
  fast GPU; make it 0/configurable if the escape hatch ever matters.
- **[context_limits.py:75-89](backend/game/utils/context_limits.py:75)**
  — `get_context_size_tokens()` resolves provider settings (a DB read)
  on EVERY `clamp_context` call, several times per prompt build.
  Correct but wasteful; a tiny TTL cache (even 5s) removes hundreds of
  reads per battle. LOW.

---

## 2. Hypotheses checked and CLEARED — do not "fix" these

1. **SQLAlchemy JSON in-place mutation loss (the big one).**
   `GlobalVariable.value` is a plain `JSON` column (no `MutableDict`),
   and the battle code mutates the loaded dict in place before
   `save_battle_state` reassigns the same object — the textbook
   identity-comparison gotcha. **Empirically disproved** with a live
   probe against the real DB (mutate in place → `set` → `expire_all` →
   re-read in a new session): the mutation PERSISTED both same-session
   and cross-session. The `set()`/reassign-through-`save()` pattern
   works. Leave it alone (but keep the pattern: any NEW mutation path
   must go through `GlobalVariable.set`, never rely on bare `commit`).
2. **Battle stuck in `'processing'` after a failed workflow.** Defused
   by design: `battle_turn`'s except block restores an awaiting phase
   (registered_workflows.py:38-52). Finding 1.6 is the only residue.
3. **The turn director acting for downed monsters.** `find_by_name`
   resolves only among `active_ids` (context.py:44-53); incapacitated
   and fled monsters cannot be picked, targeted fallbacks re-roll onto
   living monsters only.
4. **Rolling-summary index drift.** `condense_battle_log` re-plans its
   batch at execution time (housekeeping.py:18-30), the worker is
   sequential so nothing appends mid-condense, and `append_log`'s
   safety valve shifts summary `through` indexes when it drops entries
   (manager.py:253-259). The math holds.
5. **Same-priority queue ties crashing the PriorityQueue.** Tuples tie-
   break on the integer id — always comparable.
6. **Player free-text length abuse.** `PLAYER_TEXT_MAX_CHARS` is
   enforced at the service boundary for custom, talk, AND response
   text (battle_service.py:84-127). (Content-level injection is a
   different story — see docs/prompt-review.md §1.)
7. **SSE connections leaking on disconnect.** The route's generator
   removes its connection in `finally`; disconnect cleanup works —
   the problem is only the id collision (1.1).
8. **Double-submitting a turn racing the state machine.** The service
   validates phase, and even when two `battle_turn`s slip into the
   queue, the sequential worker runs them one at a time; the second
   fails cleanly on the phase check.

---

## 3. Suggested fix order

1. **1.1** SSE uuid (one line; kills a whole class of "UI went quiet" reports)
2. **1.2** impact-word coercion (one branch; protects heals)
3. **1.3** stream throttle (6 lines, biggest perceived-performance win)
4. **1.5** DeepSeek early-end detection (protects the chronicle)
5. **1.6** preserve pending_actor through failures
6. **1.4** queue pruning (+ waiter message)
7. **1.7** batch of small defensive fixes

Each fix is independent — separate commits. After 1.2/1.5/1.6, run the
offline suites; after 1.1/1.3, play one run with the browser dev tools
open and watch the SSE stream (one `events` connection, sane payload
sizes, no silent stalls after a React remount).
