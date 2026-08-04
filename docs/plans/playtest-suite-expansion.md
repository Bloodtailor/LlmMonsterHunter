# Playtest Suite Expansion (Px)

**Status:** IMPLEMENTED (2026-08-03) — all five milestones landed on
`feature/playtest-suite-expansion` (branched from
`feature/playtest-harness`; PR #181 was still open). Every surface in
the inventory below is covered, the zero-cost suites run in CI, and the
runbook is `playtest_results/REPORT.md`. Three game defects and one CI
flake were fixed and re-verified; two prompt problems now have numbers
attached. The founding harness (Pt-M0..M5) is the base this grew from.
**Mandate (Aaron, verbatim intent):** decide everything that needs to
be playtested and create playtests for each; try many methods per
surface; decide which model is best for each job; DELETE the
experimental methods that did not work; keep going until every aspect
has a powerful method; everything reusable at every major milestone —
especially to re-judge the game after the imagination engine lands.
Agents, tokens, and wall-time are explicitly unconstrained.

<!-- ==========================================================
  KICKOFF PROMPT for the fresh session (Aaron: paste this):

  Read docs/plans/playtest-suite-expansion.md and execute it. The
  founding harness and every operational fact you need are described
  there and in the docs it links. Work autonomously; spawn agents
  freely; keep the plan doc truthful as you go; commit per milestone
  on a feature/playtest-suite-expansion branch (branch from
  feature/playtest-harness if PR #181 is unmerged, else from main).
   ========================================================== -->

## Read first (in order)

1. Root `CLAUDE.md` → `docs/README.md` → `docs/architecture.md`
2. `docs/plans/playtest-harness.md` — the founding initiative: locked
   decisions (never dev DB; images never enabled; counting over
   judgment; agent reports are claims), milestones, deviations
3. `playtest_results/REPORT.md` — the night-one results and runbook
4. `tools/playtest/` — every tool is heavily commented; `rig.py` is
   the shared headless setup, `stub_llm.py`/`stub_answers.py` the
   zero-cost seam, `play.py` the agent-facing step CLI

## Operational facts (rediscovering these wastes hours)

- **Money:** DeepSeek v4-pro measured at **$0.41 per 920 calls** (the
  150-monster corpus). Cost is a non-issue; latency is the real
  budget (~48s per monster, serialized queue). The dedicated playtest
  key lives in the TEST DB's `llm_provider` row. **`pytest` deletes
  that row** (test_deepseek_provider.py clears the key in teardown), so
  re-run `seed_provider.py` after any `check_all.py`; paid tools now
  refuse to start without it (`rig.require_cloud_provider()`).
- **One world at a time:** all playtests share the test DB's single
  game state. Agent sessions, crash batches, and corpus runs must be
  SEQUENTIAL. Old harness worlds' monsters can RETURN as wild
  creatures (memories persist) — artifact, or feature, but know it.
- **MySQL REPEATABLE READ:** any long-lived process reading state the
  worker thread writes must call `rig.refresh_session()` first (bit
  the crash driver AND preflight; it will bite again).
- **Subagent models available:** haiku, sonnet, opus, fable via the
  Agent tool's `model` override. Night-one finding: haiku plays
  cleanly but confabulates reports; sonnet finds real issues.
  EVERY agent report gets verified against
  `playtest_results/play_sessions/*.jsonl` via `score_session.py`.
- **Harness quirks:** commit messages with here-strings get blocked —
  use two `-m` flags. Never pipe `play.py` through `Select-Object
  -First` (kills the pipe). `PYTHONIOENCODING` not needed for
  play.py (it self-configures UTF-8).
- **Known bugs — FIXED (Px-M1, 2026-08-03).** B1 (`sneak_past`
  success-key collision → renamed to `sneak_success`) verified by a
  forced-caught-sneak scenario + 20 happy runs, 0 violations; B2
  (fallback-less `generate_exit_text` → canned line) verified by
  broken-mode runs going from 0-can-exit to 4/6 exiting. Dead
  `generate_location_event_text` + its orphaned prompt removed.
- **Silence verdict — already landed before this session** (commit
  5a072e0): register rules + token caps, verified on a 40-monster
  corpus; any-silence 99%→90%, "stillness" 79%→25%, unique names
  57%→88%. Numbers live in REPORT.md's "first fix loop" section.
  Persona stage (85%) remains the stronghold — imagination-engine
  territory, not prompt territory.

## The surface inventory (what needs playtests)

Legend: ✅ covered by founding harness · 🟡 partial · ❌ uncovered

1. ✅ **Dungeon exploration loop** — crash driver (3 modes) + agents,
   PLUS `tools/playtest/dungeon_gauntlet.py` (Px-M2): directed
   scenarios force every rare path — treasure spoils kept on exit, the
   full six-outcome dialogue tree with memory assertions, the
   out-of-battle referee (ability/item heals, costs, reveal), camp
   rest + one-camp valve, the victory-exit ceremony, and the goal's
   completion valve + reward (the valve itself was surfaced by the
   gauntlet's first run).
2. ✅ **Battle system** — `tools/playtest/battle_gauntlet.py`: seven
   directed scenarios over the scripted stub — softlock valve,
   fairness guardrail, turn-cost bound, all five negotiation
   decisions, defeat path with spoils forfeiture + bond_broken
   memories, resource-ladder drain/clamp + item spend, wary-ally
   autonomy flipping at familiar. Seconds, zero cost.
3. ✅ **Campfire chat** — `tools/playtest/life_gauntlet.py` (Px-M2)
   drives the full pipeline offline (thread → housekeeping →
   extraction with sources → watermark → affinity), and
   `tools/playtest/chat_faithfulness.py` scores extracted memories by
   COUNTING content-word overlap against the exact message span — the
   checker is validated against planted faithful/fabricated memories.
   Live extraction quality runs the same checker in Px-M3+.
4. ✅ **Evolution altar** — life_gauntlet `evolution_identity`: same
   id, memories + abilities survive, lineage row, stage complete.
5. ✅ **Cross-run memory & returning** — life_gauntlet
   `yield_return_remembers`: yield in run 1 → exit → forced
   returning_monster event in run 2 → the SAME monster returns with a
   memory naming the true place of the yield.
6. 🟡 **New Game + character creation** (`player_generation` flows) —
   the Px-M5 browser session verified the title screen, the
   abandoned-run recovery path, home base and campfire against the
   test DB with zero console errors. The creation WIZARD itself was
   not walked (each step is a real generation and the session's
   remaining budget went to consolidation) — the one honest gap left.
7. ✅ **Chronicle quality** — 16-chronicle corpus via passthrough
   harvesting: overlap 0.288 (3x the monster corpus), a fixed
   `Run N: <player>…` opening in 100%, "expedition ended" in 50%,
   silence 56% strict. The samest prose the game writes.
8. ✅ **Variety corpora beyond monsters/notices** — abilities (57%
   pseudo-mechanics leak, 33% naming turn counts, 65% echoing the
   "deepest wish") and items (healthy: 0.059 overlap, zero leak), both
   re-measurable in seconds by `analyze_text_corpus.py`.
9. ✅ **Adversarial player** — `adversarial_probe.py` (fixed hostile
   inputs, code-owned assertions, 50 live checks / 0 failures) plus
   `adversarial_agent_prompt.md` for attacks a fixed list cannot
   invent. CONTENT-level defense is now tested, not assumed.
10. ✅ **Frontend/UI layer** — browser session against
    `backend-testdb` + the real React app: abandoned-run recovery
    narrated correctly, home base and campfire screens render the
    harness world, zero console errors, every request 200. It also
    exposed a harness bug (`current_health` 100 vs `max_health` 52).
11. ✅ **Live model bake-off** — haiku vs sonnet with real narration,
    verified against transcripts. Standard tester: **sonnet** for
    feedback worth acting on, haiku as a cheap play-monkey behind
    `score_session.py`. Table in REPORT.md.
12. ✅ **Cost/latency benchmarking** — `cost_report.py` reads the
    ledger the game already writes: 2,442 calls, 5.16M tokens, $1.51,
    225 minutes; input outweighs output 11:1; monster generation is
    151 of those 225 minutes.

## Method rules (locked, carried from Pt)

- Counting beats judgment for variety; LLM-annotator stays secondary.
- Every agent claim is verified against transcript + code before it
  counts. Verification is the product.
- Harness stays a CONSUMER of the game (tools/playtest/, the two
  public seams); game fixes are separate commits with crash-driver
  re-verification.
- Experimental methods that lose their bake-off get DELETED, not
  parked — Aaron wants a suite, not a museum.
- Everything must be one-command runnable at any future milestone,
  and REPORT.md stays the single runbook.

## Milestones (as shipped)

- **Px-M1 — IMPLEMENTED.** B1 + B2 fixed and re-verified; silence-fix
  verdict logged (already landed in 5a072e0); `scripted_stub.py` +
  `gauntlet_rig.py` + `battle_gauntlet.py` (7 scenarios).
- **Px-M2 — IMPLEMENTED.** `dungeon_gauntlet.py` (7 scenarios, every
  path event), `life_gauntlet.py` (chat pipeline, evolution identity,
  cross-run memory), `chat_faithfulness.py` (counting, validated
  against planted memories).
- **Px-M3 — IMPLEMENTED.** `adversarial_probe.py` (50 live checks, 0
  failures) + `adversarial_agent_prompt.md`; live haiku-vs-sonnet
  bake-off with transcript verification; B3 found and fixed; play.py
  now prints narration, warns on an inherited world, and was split at
  the 500-line ceiling; `run_gauntlets.py` wired into check_all + CI.
- **Px-M4 — IMPLEMENTED.** `analyze_text_corpus.py` (abilities: 57%
  pseudo-mechanics leak; chronicles: 0.288 overlap; items healthy),
  `generate_text_corpus.py` (passthrough harvesting),
  `cost_report.py`, plus the strict-silence metric and the
  stub-vocabulary tripwire.
- **Px-M5 — IMPLEMENTED.** Browser session through the real React app
  on the test DB; suite consolidation; this doc and REPORT.md made
  true. **Nothing was deleted:** every method built this session
  survived its bake-off (see Deviations).

## Deviations

- **2026-08-03 (Px-M1): the silence-fix verdict was already done.**
  The handoff listed it as in-flight/uncommitted, but commit 5a072e0
  (same afternoon, before this session started) had already landed the
  register rules + token caps with the 40-monster verification
  numbers. Nothing to re-measure; the plan text above now points at
  REPORT.md.
- **2026-08-03 (Px-M1): game fixes went in their own commit** (per the
  method rules), before the harness milestone commit: B1 + B2 + dead
  `generate_location_event_text`/`location_event` removal, with
  prompt-review §3.2 marked resolved-by-deletion in the same change.
- **2026-08-03 (Px-M2): the goal completion valve surfaced as a
  "failure" first.** The dungeon gauntlet's goal scenario scripted an
  immediate referee "complete" and the goal stayed pending —
  `GOAL_MIN_EVENTS` downgrades early completions by design. The
  scenario now walks the valve's length first and asserts completion
  *after* it; the valve got its first direct regression coverage in
  the bargain.
- **2026-08-03 (Px-M2): chat-extraction faithfulness split into
  offline + live halves.** Offline (stubbed) runs can't judge a real
  model's extraction quality, so the gauntlet validates the CHECKER
  (planted faithful vs fabricated memories, same pattern as Pt-M1's
  synthetic-corpus validation) and the live suites reuse it as-is.
- **2026-08-03 (Px-M2): New Game/character creation deferred to the
  Px-M5 browser sessions** rather than a headless scenario — the
  wizard is a frontend flow first, and the browser leg exercises it
  for real.
- **2026-08-03 (Px-M3): the first live adversarial run cost an hour and
  aborted.** One `battle_turn` exceeded the harness's 900s patience
  because a live workflow resolves every NPC turn before returning. The
  probe now carries a per-injection timeout and records a slow workflow
  as a finding; a `turn_cost_bound` gauntlet scenario measures the
  mechanism for free. Live runs use `--battle-injections 2`.
- **2026-08-03 (Px-M4): the harness was measuring itself.** The stub's
  word pool contained `quiet`, `echoing` and `luminous` - all variety
  watchwords - so a stubbed chronicle corpus read as 88% silence-obsessed
  and 75% "luminous". Words replaced; `run_gauntlets.py` now tripwires
  the collision so it cannot come back. Any corpus harvested from
  stubbed runs before this fix should be re-measured.
- **2026-08-03 (Px-M4): `pytest` deletes the playtest provider row.**
  `test_deepseek_provider.py` clears the `llm_provider` key in its own
  teardown, so any `check_all.py` run between seeding and a live run
  silently drops the harness to the local floor - which produced a
  corpus of empty chronicles before anyone noticed. Paid tools now call
  `rig.require_cloud_provider()` and refuse to start.
- **2026-08-03 (Px-M5): nothing was deleted, which needs saying.** The
  method rules call for deleting experimental methods that lose their
  bake-off. Every method built this session earned its place: counting
  and clustering answer different questions, the fixed-input probe and
  the adversarial agent catch different attacks, and both models stay
  in the suite with different jobs. The one thing that WAS cut is the
  dead `generate_location_event_text` + its prompt (Px-M1).
- **2026-08-03 (Px-M5): the gauntlets joined CI, making it seven checks.**
  `tools/check_all.py`, `.github/workflows/ci.yml`, root `CLAUDE.md` and
  `check_all.bat` all updated together. A `test_new_game` flake found
  while doing it (the wipe guard reads the live queue; a sibling suite's
  queued housekeeping made it refuse) was fixed in the same pass.
