# Monster Requests — Implementation Plan

**Status: PLANNED** (not started)
**Branch:** `feature/monster-requests` · **Commit prefix:** `Req-M#`
**Written:** 2026-07-07, from `docs/roadmap.md` initiative #1 + a full read
of the run-end, memory, affinity, goal, and chat subsystems. Intended to be
executable by an AI assistant working autonomously — every milestone names
its files, its seams, and its verification commands, and needs no further
design decisions.

Roadmap source: [docs/roadmap.md](../roadmap.md) §1 "Monster Requests".
The one-initiative payoff: **the cast starts driving the plot.** A monster
comes to you at the campfire wanting something — sourced from its own
memories — and the player stops asking "what do I want to do?" and starts
asking "who do I want to do right by?"

This initiative converts infrastructure that already exists (memories,
affinity, run goals, the chronicle) into *motivation*. It adds almost no
new mechanics of its own; it wires the existing ones into a want.

---

## 1. Locked decisions (design intent — do not re-litigate)

These are settled. If the code forces a change, log it in the Deviations
section rather than quietly diverging.

1. **The request-type enum (LLM picks one word):**
   `revisit` (a place/monster from its past) · `seek` (a described thing it
   wants found) · `confront` (a remembered foe) · `accompany` (wants to be
   in the party next run) · `ritual` (wants an evolution / ceremony / talk).
   Code owns the enum; the LLM only chooses among these words. Unknown words
   fall back to `seek` (the most generic).

2. **The weight ladder (LLM picks one word):**
   `whim → wish → need → vow`. This is the request's felt importance. Code
   owns every consequence of weight (see #4/#5); the LLM never sees a number.

3. **The fulfillment ladder (the run-end judge picks one word per open
   request):** `unaddressed → progressed → fulfilled → betrayed`.
   `betrayed` means the run actively did the opposite of the want (fought a
   `confront` target and let it flee; left the `accompany` monster behind).
   Refereed, never scripted — no quest-flag code, no per-type completion
   logic. The judge sees the last run's log + the open requests and rules.

4. **Fulfillment consequences are code-owned and weight-scaled — but
   affinity still moves ONE rung at a time.** Affinity is a 4-rung ladder
   (`wary → familiar → trusting → devoted`) moved one step per event by
   design (the referee philosophy — `game/monster/affinity.py`). So:
   - `fulfilled` → **one** `step_affinity(monster_id, 'fulfilled_request')`
     step (unbudgeted, because the workflow runs at home base, not in a
     run) + a minted `request_fulfilled` memory + the request closes.
   - Weight scales the *significance*, not the step count: it drives the
     memory prose, whether ignoring the request has teeth (whim/wish: none;
     need/vow: the decay track in Req-M5), and run-goal eligibility
     (wish-and-up only — see #6).
   - `progressed` → a progress note appended to the request; it stays open.
   - `betrayed` → mint a `request_betrayed` memory, mark the request
     `betrayed` (closed); need/vow betrayals feed the decay track (M5).
   - `unaddressed` → nothing changes; the request ages one cycle.

5. **`whim` requests expire silently.** A `whim` that is still open and
   unaddressed after `WHIM_EXPIRY_RUNS` (2) run-cycles closes as `expired` —
   **no nagging, no penalty, no memory.** Whims are ambient colour; the
   cast should feel alive, not needy.

6. **Run integration reuses the goals machinery wholesale.** An open
   request of weight `wish` or higher can be offered at the expedition board
   as an optional **run-goal variant**. Choosing it sets the run goal via
   the EXISTING `set_fixed_goal` path (no `generate_run_goal` call) and
   stamps the request id onto the run context so the judge (which reads the
   run log at run-end) naturally rules it `fulfilled` when the goal is met.
   No new goal-completion code.

7. **Caps and valves (code-owned, top of `requests/constants.py`):**
   - `MAX_OPEN_REQUESTS_PER_MONSTER = 1` — a monster wants one thing at a
     time; scarcity is what makes a request land.
   - `REQUESTS_FORMED_PER_CYCLE = (1, 2)` — the post-run cycle gives at most
     1–2 monsters (chosen from the FOLLOWING roster) a *chance* to form a
     request; monsters already at their cap are skipped.
   - `FORM_CHANCE = 0.6` — even a chosen, capacity-having monster only
     sometimes forms one. Requests are precious, not a per-run tax.
   - `WHIM_EXPIRY_RUNS = 2`; decay thresholds live in M5.

8. **The trigger is the post-run cycle.** "Chronicle time" in the roadmap is
   the moment both run-end paths already fire the chronicle. Requests do NOT
   run inline there (that would make the player wait); they run in a
   **separate queued workflow** enqueued at run-end, exactly as chat queues
   `chat_housekeeping` behind `chat_with_monster`. The "occasionally at the
   home base" trigger from the roadmap is **out of scope for V1** (post-run
   is enough drama); revisit after soak.

**Out of scope for V1:** the home-base idle trigger; requests targeting a
specific *returning* monster/nemesis by id (needs Nemesis Arcs, roadmap #2 —
`confront` targets a remembered foe by description only for now); group /
party-wide requests; the leaving mechanic beyond the single decay-to-wary
step scoped in M5.

---

## 2. Guardrails — do NOT touch these while executing

- **The step-name contract.** Frontend event hooks key off workflow
  `on_update` step strings (`docs/architecture.md`). This initiative is
  purely ADDITIVE — a brand-new workflow with brand-new step names and
  brand-new event names. Do not rename any existing step, workflow, or
  event. Do not add steps to `enter_dungeon`, `exit_run`'s chain, or the
  battle-ending chain beyond the single `queue_*` emit noted in M2.
- **All generation goes through `ai/gateway.py`** via the existing
  `build_and_generate` / `build_and_stream` helpers (`game/utils`). No new
  path to the model.
- **The LLM picks words; code owns numbers.** Every weight, cap, chance,
  and expiry is a Python constant. The templates never contain a number and
  never receive one.
- **Writing never blocks the moment that created it.** The post-run
  workflow, like the chronicle and housekeeping, must never raise into a
  run's ending. Every consequence helper follows the `write_memory` /
  `step_affinity` "never raises, prints and moves on" contract.
- **No new columns on existing tables, no DB reset.** Requests are a new
  table only (§Req-M1), registered the same way `monster_evolutions` was.
- **File-size ceiling: 500 lines.** Split before you hit it; never add to
  the grandfather list in `tools/check_file_sizes.py`.

---

## 3. Verification commands (run after every milestone)

```bash
# Backend (repo root; MySQL must be running)
./venv/Scripts/python.exe -m backend.tests.test_requests          # this initiative's suite
./venv/Scripts/python.exe -m pytest                               # all offline suites
./venv/Scripts/python.exe -m ruff check backend setup tools
./venv/Scripts/python.exe tools/check_file_sizes.py
./venv/Scripts/python.exe -m backend.tests.test_monster_templates # once templates exist (M2)

# Frontend (from frontend/) — only for the milestones that touch it (M3, M4)
npm test -- --watchAll=false
npx prettier --check src
```

Milestones that change rendering (M3, M4) also boot the game
(`start_game.bat`) and exercise the flow named in that milestone's
verification block. Offline suites stub the LLM and use the test DB, so
they prove wiring and code-owned rules but NOT prose quality — each
LLM-facing milestone carries a short **live soak** checklist for Aaron
(model loaded) at the end.

---

## 4. Data model (Req-M1) — new table only

`backend/models/monster_request.py` — table `monster_requests`, modeled on
`backend/models/monster_evolution.py` (same registration ritual):

| Column | Type | Notes |
|---|---|---|
| `monster_id` | Integer FK→monsters, indexed | who wants it |
| `request_type` | String(20) | one of the enum (§1.1) |
| `weight` | String(10) | one of the ladder (§1.2) |
| `text` | Text | the want, in the monster's voice, LLM-written |
| `status` | String(12), indexed | `open` / `fulfilled` / `betrayed` / `expired` |
| `source_memory_ids` | JSON (nullable) | the memory ids the want grew from |
| `progress_notes` | JSON (nullable) | judge notes from `progressed` rulings |
| `created_run_number` | Integer (nullable) | for the whim-expiry + decay clocks |
| `resolved_run_number` | Integer (nullable) | stamped when it closes |
| `details` | JSON (nullable) | type-specific extras (e.g. `target_desc`) |

Classmethods to provide (mirror `MonsterMemory`'s style — every one wrapped
in try/except that prints and returns a safe default, never raises):

- `add(monster_id, request_type, weight, text, source_memory_ids, details, run_number)`
- `open_for_monster(monster_id) -> list` and `count_open(monster_id) -> int`
- `all_open() -> list` (the judge + the board read this)
- `open_of_weight_at_least(min_weight) -> list` (run-goal eligibility, M4)
- `close(request_id, status, run_number, note=None)` — sets status +
  `resolved_run_number`, appends a final progress note if given.
- `to_dict()` including all columns above.

Registration (do all four, or the table silently won't exist in one of the
environments):
1. `backend/models/core.py:create_tables()` — add the `from .monster_request
   import MonsterRequest  # noqa: F401` line beside `monster_memory`.
2. `backend/tests/reset_db.py:import_all_models()` — add the import.
3. Grep for any other place `monster_evolution` is imported for table
   creation and match it.

New memory kinds (append to `MEMORY_KINDS` in
`backend/game/memory/manager.py`, with WHY-comments matching the existing
block): `request_fulfilled` (a want the party made real) and
`request_betrayed` (a want the party trampled). Both are ordinary memories —
**do NOT** add them to `growth_total_pct`'s summed kinds; requests move
affinity, not stats.

---

## Req-M1 — The requests domain: table, constants, manager (backend-only)

Stand up the data layer and the code-owned rules with zero LLM and zero
workflow, so the ladders/caps/valves are unit-tested before anything calls
a model.

**Create `backend/game/requests/`** (new domain package beside `chat/`,
`memory/`, `monster/`), one concept per file:

- `__init__.py` — package marker + the `print(f"🔍 Loading …")` line the
  other packages use.
- `constants.py` — the enum tuple `REQUEST_TYPES`, the ladders
  `WEIGHT_LADDER` and `FULFILLMENT_LADDER`, all caps/chances/expiries from
  §1.7, a `weight_rank(weight) -> int` helper (for `open_of_weight_at_least`
  and the wish+ gate), and `REQUEST_TYPE_FLAVOR` / `WEIGHT_FLAVOR` dicts
  (how each word reads inside a prompt context block — mirror
  `AFFINITY_FLAVOR`). Heavy WHY-comments; this file IS the referee contract
  for requests.
- `manager.py` — the single gateway for reading/writing requests and for
  applying the code-owned consequences (`step 4`). Functions:
  - `form_request(monster_id, request_type, weight, text, source_memory_ids,
    details)` — validate the words against the enums (coerce unknowns per
    §1.1/§1.2), enforce `MAX_OPEN_REQUESTS_PER_MONSTER`, write the row,
    stamp `created_run_number` from `last_run_number()`, emit
    `monster.request_formed`. Never raises.
  - `apply_ruling(request, ruling_word, note)` — the consequence switch
    from §1.4: `fulfilled`→`step_affinity(..., 'fulfilled_request')` +
    `write_memory(..., 'request_fulfilled', …)` + close; `progressed`→note;
    `betrayed`→`write_memory(..., 'request_betrayed', …)` + close;
    `unaddressed`→no-op. Emits `monster.request_resolved` on any close.
    Never raises.
  - `expire_stale_whims(current_run_number)` — close `whim`s older than
    `WHIM_EXPIRY_RUNS` as `expired`, silently (no memory, no event payload
    beyond the resolve event so the card badge clears).
  - `open_requests_view()` — a frontend-facing list (M3/M4 read this).
  - `request_context_line(request)` — one prompt line for the judge/goal
    blocks (`f"[{weight}] {type}: {text}"`).

**Add `'fulfilled_request'` to `_REASON_PROSE`** in
`backend/game/monster/affinity.py` (one line, matching the existing
entries) so the affinity-grew memory reads well.

**Add the two SSE event types.** In
`backend/core/events/monster_events.py`, declare `monster.request_formed`
and `monster.request_resolved` with schemas (fields: `monster_id`,
`request` dict) and `emit_monster_request_formed` /
`emit_monster_request_resolved` helpers, registered in
`core/events/event_registry.py`. Match the shape of
`emit_monster_memory_added` exactly (including its `send_to_frontend`
choice). Backend-only this milestone — the frontend handler lands in M3.

**Verification.**
- New offline suite `backend/tests/test_requests.py` (repo suite pattern:
  `check(...)` assertions, `main() -> failure count`, pytest-discoverable
  AND `python -m backend.tests.test_requests`). No LLM. Cover:
  - enum/ladder coercion (unknown type→`seek`, unknown weight→`whim`);
  - `MAX_OPEN_REQUESTS_PER_MONSTER` (a second `form_request` while one is
    open is refused);
  - `apply_ruling` consequences: `fulfilled` steps affinity exactly one
    rung + mints one `request_fulfilled` memory + closes with
    `resolved_run_number`; `betrayed` mints one `request_betrayed` memory +
    closes; `progressed` appends a note and leaves it open; `unaddressed`
    is a no-op;
  - `expire_stale_whims` closes an aged whim as `expired` and mints NO
    memory; a `need` of the same age is untouched;
  - `open_of_weight_at_least('wish')` excludes whims.
  - If the suite registry enumerates suites (check
    `backend/services/game_tester_service.py`), register this one.
- Run the full backend verification block. Shippable: the data layer and
  every code-owned rule, proven, with nothing yet calling it.

---

## Req-M2 — The engine: forming + judging at run-end (the post-run workflow)

One new queued workflow does the whole loop: judge last run's open requests
against what just happened, then give 1–2 following monsters a chance to
form a new one. It runs AFTER the player has their chronicle, so nobody
waits on it.

**Templates** — new `backend/ai/llm/prompts/request_generation.json`, two
small flat-JSON templates (follow `evolution_generation.json`'s structure:
`description`, `max_tokens`, `temperature`, `parser` with
`expected_fields`/`required_fields`, `prompt_template` with `{placeholders}`
and a literal `RESPONSE FORMAT` JSON example). NO numbers in any template.

| Template | ~tokens/temp | required fields | context blocks |
|---|---|---|---|
| `form_request` | 300 / 0.85 | `request_type`, `weight`, `want` | `{monster_details}` (`speaker_block_with_affinity`), `{monster_memories}` (`build_memory_block`), `{type_menu}` + `{weight_menu}` (code-built word menus from `constants.py` flavor dicts), `{source_hint}` |
| `judge_requests` | 400 / 0.6 | `rulings` (list of `{request_id, ruling, note}`) | `{last_run_log}`, `{open_requests}` (one `request_context_line` per row, id-tagged), `{ruling_menu}` |

`form_request` also asks the model to echo which memory lines inspired the
want (so `source_memory_ids` is populated); if it can't, `source_memory_ids`
is null — non-fatal. `judge_requests` is ONE batch call over all open
requests (not one call per request) — cheaper and lets the judge weigh the
run as a whole.

**Generator** — `backend/game/requests/generator.py` (composes prompts +
calls the gateway, per the layer rules):
- `run_form_request(monster, workflow_name) -> dict | None` — builds the
  context, calls `build_and_generate('form_request', …)`, returns the parsed
  words (or None on failure).
- `run_judge_requests(open_requests, last_run_log_text, workflow_name) ->
  list[dict]` — one `build_and_generate('judge_requests', …)` call; returns
  a list of `{request_id, ruling, note}`, ruling-words coerced to the
  fulfillment ladder (unknown → `unaddressed`, the safe no-op). Never
  raises; returns `[]` on failure so the cycle degrades to "nothing ruled".

**The workflow** — `backend/game/requests/registered_workflows.py`, a new
`@register_workflow() process_monster_requests(context, on_update)` in the
thin validate-and-delegate style of the chat workflows. Context is empty
(it reads live home-base state). Steps (all NEW names — additive):
`validate_context → judging_requests → forming_requests →
expiring_whims → done`. Sequence inside:
1. `current_run_number = chat.manager.last_run_number()` (the run that just
   ended); `last_log = dungeon.manager.get_last_run_log()` (survives the
   state wipe — this is the same snapshot home chats read).
2. **Judge first.** `open = MonsterRequest.all_open()`; if any and we have a
   `last_log`, call `run_judge_requests` and `manager.apply_ruling(...)` per
   row. Judge-then-form ordering matters: a request formed THIS cycle must
   not be judged against a run it could not have influenced.
3. **Form next.** Pick up to `REQUESTS_FORMED_PER_CYCLE` monsters from
   `FollowingMonster.get_following_monster_ids()` (the home-base roster,
   excluding the player via `player.manager.get_player_monster_id()` and any
   monster already at its open-request cap), roll `FORM_CHANCE` each, and
   for winners call `run_form_request` → `manager.form_request(...)`.
4. `manager.expire_stale_whims(current_run_number)`.
   Return a `success_response` summarizing counts. Wrap the body in the same
   `try/except → error_response({failed_at, completed_work, error})` shape
   the chat workflows use.

**Enqueue it at run-end (both paths).** Add a tiny helper
`backend/game/requests/manager.py:queue_post_run_requests()` that calls
`request_workflow(workflow_type="process_monster_requests")` (the same
gateway `monster_service` uses) and never raises. Call it once at the very
END of each run-end path, AFTER the state is snapshotted/wiped so the
workflow runs at home base (unbudgeted affinity, §1.4):
- `backend/game/dungeon/handlers/exit_run.py` — after `manager.exit_dungeon()`
  (last thing before the return). Add one `step.emit("queue_requests")`
  then the call.
- `backend/game/battle/turn/ending.py:finish_battle` — the defeat path, in
  the same block that queues the chronicle, AFTER the run row is closed. Add
  one `ctx.step.emit("queue_requests")` then the call.
  These two single-emit additions are the ONLY changes to existing
  step-name-bearing chains, and they are additive (new trailing steps),
  which the contract permits.

**Verification.**
- Extend `test_requests.py` with stubbed-LLM coverage: a fake
  `form_request` result flows through the workflow and creates a row with
  the coerced words; a fake `judge_requests` batch drives `apply_ruling` for
  each open row (fulfilled/betrayed/progressed/unaddressed all exercised);
  monsters at cap are skipped by the former; the player id is never chosen.
- `test_monster_templates.py` — add `form_request` and `judge_requests` to
  its `GENERATOR_VARIABLES` coverage (this suite checks every template's
  placeholders resolve), then run it.
- Full backend verification block.
- **Live soak (Aaron, model loaded):** run a dungeon to a victory exit and
  to a defeat; watch the AI log for the two new templates firing after the
  chronicle; confirm a `monster_requests` row appears with a sensible want
  in the monster's voice; run a SECOND dungeon whose events plainly satisfy
  that want and confirm the judge rules it `fulfilled`, affinity steps up,
  and a `request_fulfilled` memory is written; watch parse-retry rates and
  tune wording/`max_tokens` if needed.

Shippable: the entire want→judge→consequence loop works headless. Requests
form, resolve, and shape affinity/memory with no UI yet.

---

## Req-M3 — Frontend surfaces: the indicator + "someone approaches you"

Make the loop visible and give the campfire moment its payoff. Reuse the
chat panel per the roadmap; do not build a new conversation UI.

- **Event handler.** In `frontend/src/api/events/monsterEventHandlers.js`,
  register handlers for `monster.request_formed` / `monster.request_resolved`
  mirroring the memory-added handler. Surface open-request state through the
  same store/context path the party uses (`PartyProvider` already live-patches
  the following list on `monsterUpdated` etc. — extend it to hold each
  following monster's open request, patched on these two events so the badge
  appears/clears without a refetch).
- **API service.** Add `GET /api/monsters/requests` (open requests) and, if
  a per-monster read is cleaner for the card, `GET /api/monsters/<id>/requests`
  — thin route → `monster_service` → `requests.manager.open_requests_view()`,
  following the `get_monster_evolutions` route/service pair exactly. Add the
  matching client function beside `loadMonsterEvolutions`.
- **Card indicator.** `frontend/src/components/cards/MonsterCard.js` (or the
  overview sub-component) gains a small badge when the monster has an open
  request — icon + weight word, tooltip = the want text. Code owns the
  colour ramp by weight; keep it a `shared/ui` primitive if one fits.
- **The campfire "someone approaches you" moment.** On the home-base screen,
  when a following monster has a fresh open request, show a gentle prompt
  ("Thornback approaches you…") that opens the EXISTING `MonsterChatPanel`
  pre-seeded to that monster, so the player can talk about the want
  immediately. This is presentation only — it reuses chat wholesale and
  invents no new backend. Model the trigger on how `MonsterChatScreen`
  already selects a monster; the request text rides in as the opener's
  context.

**Verification.** `npm test`, `npx prettier --check src`, then boot
`start_game.bat`: after a run that forms a request, confirm the badge
renders on the right card, the tooltip shows the want, tapping the campfire
prompt opens the chat panel to that monster, and fulfilling the request in a
later run clears the badge live (no manual refresh). Screenshot the badge +
the approach moment for the PR.

---

## Req-M4 — Run integration: a request as the run's goal

Let a want become the reason for the next expedition, reusing the goals
machinery end to end.

- **Offer at the board.** When `generate_expedition_notices`
  (`game/dungeon/handlers/notices.py`) returns the board, also surface
  `requests.manager.open_of_weight_at_least('wish')` to the frontend (add
  the list to the notices workflow's result payload — additive key, no
  step-name change). Whims never appear here (§1.5); they are ambient only.
- **Choosing it sets a fixed goal.** The expedition screen shows eligible
  requests as optional goal variants ("Thornback watches you study the
  map…"). When the player picks one, the enter-dungeon request carries the
  chosen `request_id`; `run_enter_dungeon`
  (`game/dungeon/handlers/run_lifecycle.py`) — in the `else` branch where it
  currently calls `generate_run_goal` — instead calls
  `set_fixed_goal(<the request's want, phrased as a goal>)` and stamps the
  `request_id` into the run context (`run_context`) so it rides the whole
  run. No new goal-referee code: the existing `check_goal_progress` referee
  already scores the goal as events resolve.
- **The judge closes the loop.** Because the request text became the goal
  and the goal's fulfilment is logged into the run log
  (`THE RUN'S GOAL WAS FULFILLED: …`), the M2 `judge_requests` call at
  run-end sees it plainly and rules `fulfilled` — no special-casing. Belt
  and suspenders: if the run context still carries the `request_id` and its
  goal completed, `apply_ruling` may be invoked directly for that row so a
  fulfilled goal-request never depends on the judge's prose alone. Decide at
  implementation time which is cleaner; the direct path is more robust.

**Verification.** Backend suite: a request chosen as a goal sets a fixed
goal (no `generate_run_goal` call) and the run context carries the id;
completing that goal closes the request `fulfilled` at run-end. Frontend:
`npm test` + prettier. Live (Aaron): form a `wish`+ request, start a run and
pick it at the board, complete the goal, confirm the reward ceremony fires
AND the request closes fulfilled with the affinity step. Screenshot the
board variant.

---

## Req-M5 — Teeth for ignored needs (decay toward leaving) — sequenced last

The one genuinely new mechanic: ignoring a `need`/`vow` has a cost. Last on
purpose — it introduces DOWNWARD affinity movement and a leaving path, which
nothing else in the game does, so it ships only once the additive core
(M1–M4) is proven and soaked.

**Locked decisions (code-owned, `requests/constants.py`):**
- `NEED_DECAY_RUNS = 3` — a `need` open and `unaddressed` for this many
  run-cycles decays affinity ONE rung (never below `wary`) and mints an
  `affinity_grew`-style memory in reverse (a new `_REASON_PROSE` entry, e.g.
  `'need_ignored'`, and a new `step_affinity_down` in `affinity.py` that
  mirrors `step_affinity` but moves down — never below `wary`, never on the
  player, never raises). The request then closes as `expired`.
- `VOW_ABANDON_RUNS = 4` — a `vow` open and `unaddressed`/`betrayed` this
  long on an already-`wary` monster triggers the **leaving** path:
  `FollowingMonster.remove_follower(monster_id)` + a `bond_broken`-adjacent
  memory + a prominent SSE event so the frontend can mark the departure.
  Cap the drama: at most ONE monster may leave per cycle. A monster above
  `wary` never leaves from a vow — it decays toward wary first (a vow is a
  slow burn, not a trapdoor).
- These clocks read `created_run_number` vs the current run number; the
  decay/expiry pass lives in `expire_stale_whims`'s sibling
  `age_open_requests(current_run_number)`, called in the workflow's
  `expiring_whims` step (rename that step? NO — it's a new workflow, but the
  step name is already shipped from M2; keep the string, broaden what it
  does, and note it in comments).

**Frontend.** A leaving monster needs a dignified moment, not a silent
disappearance from the roster — a small home-base notice ("Miremaw has left
the party") driven by the departure event. Reuse existing notice UI.

**Verification.** Backend suite: an aged unaddressed `need` decays affinity
one rung and expires; a decay never drops below `wary`; a vow on a `wary`
monster past `VOW_ABANDON_RUNS` removes the follower and mints the memory;
at most one departure per cycle; the player is never decayed or removed.
Live (Aaron): deliberately ignore a `need` across several runs and watch the
affinity slip + the request expire; ignore a `vow` on a wary monster and
watch it leave with a notice. Full verification block + prettier.

Shippable independently: M1–M4 stand without it (ignored needs simply linger
harmlessly); this milestone only ADDS consequences.

---

## 5. How this reuses what already exists (the payoff-per-effort receipts)

- **Memories** — `form_request` reads `build_memory_block`; fulfillment
  mints memories via the existing `write_memory` gateway. No new memory
  plumbing.
- **Affinity** — fulfillment reuses `step_affinity` (one new reason). Only
  M5 adds the mirror-image `step_affinity_down`.
- **Run goals** — M4 reuses `set_fixed_goal` + `check_goal_progress`
  untouched.
- **The chronicle precedent** — the post-run workflow is enqueued exactly
  like `chat_housekeeping` is queued behind chat, and reads the same
  `get_last_run_log()` snapshot the chronicle and home chats already use.
- **The chat panel** — the campfire "someone approaches" moment (M3) is the
  existing `MonsterChatPanel`, pre-seeded. No new conversation UI.
- **Returning monsters / Nemesis Arcs (roadmap #2)** — `confront` requests
  describe a foe in prose today; once Nemesis Arcs land, they can target a
  nemesis by id. This plan deliberately leaves that seam open (`details`
  JSON has room) rather than building half of #2 here.

---

## 6. Milestone summary

| Milestone | Ships | Player-visible? |
|---|---|---|
| **Req-M1** | requests table + constants + manager + events; offline suite | no (foundation) |
| **Req-M2** | the post-run form+judge workflow + templates; run-end wiring | via AI log / DB (no UI) |
| **Req-M3** | card badge + "someone approaches you" campfire moment | yes |
| **Req-M4** | requests offered as optional run goals at the board | yes |
| **Req-M5** | decay + leaving for ignored needs/vows (new downward affinity) | yes |

Per repo process: this doc's Status flips PLANNED → IN PROGRESS → IMPLEMENTED
as milestones land; every deviation from the locked decisions above is logged
below in the same commit that causes it.

## 7. Deviations log

*(none yet — log them here as they happen, per repo process)*
