# Playtest Suite Expansion (Px)

**Status:** IN PROGRESS — Px-M1 landed 2026-08-03 (B1/B2 fixed and
re-verified, battle gauntlet green, silence verdict logged). Branch:
`feature/playtest-suite-expansion` (from `feature/playtest-harness`;
PR #181 was still open). The founding harness (Pt-M0..M5,
`feature/playtest-harness`, PR #181) is built, exercised, and
documented; this initiative grows it into a comprehensive, reusable
suite covering EVERY aspect of the game.
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
  key lives in the TEST DB's `llm_provider` row; restore it after any
  `seed_provider.py` run with `tools/playtest/set_playtest_key.py
  <key>` (ask Aaron for the key; never store it in the repo).
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
2. ✅ **Battle system** — `tools/playtest/battle_gauntlet.py` (Px-M1):
   six directed scenarios over the scripted stub — softlock valve,
   fairness guardrail, all five negotiation decisions, defeat path
   with spoils forfeiture + bond_broken memories, resource-ladder
   drain/clamp + item spend, wary-ally autonomy flipping at familiar.
   42 checks, ~7s, zero cost.
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
6. ❌ **New Game + character creation** (`player_generation` flows) —
   deliberately deferred to the Px-M5 browser UI sessions, which
   exercise the wizard end-to-end through the real frontend.
7. ❌ **Chronicle quality** — a chronicle corpus (many runs → variety
   metrics over the chronicles themselves).
8. 🟡 **Variety corpora beyond monsters/notices** — abilities, items,
   locations/paths deserve the same counting treatment (ability text
   already shows pseudo-mechanics leakage: "next three turns" ×14 —
   also a prompt-fix candidate).
9. ❌ **Adversarial player** — the boundary-pusher persona: prompt
   injection via talk/custom text, referee exploit probing
   (docs/prompt-review.md §1 context). Cap text at the service
   boundary is tested; CONTENT-level defense is not.
10. ❌ **Frontend/UI layer** — browser computer-use sessions through
    the real React app with the backend pointed at the test DB
    (set DB_NAME env when launching; never the dev world).
11. ❌ **Live model bake-off** — haiku vs sonnet (vs opus?) as testers
    with REAL narration: completion, invalid-action rate, report
    actionability after verification. Pick the standard tester(s).
12. ❌ **Cost/latency benchmarking** — tokens and seconds per workflow
    from `llm_logs` (the data is already recorded; nobody reads it).

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

## Suggested shape (the fresh session may re-plan)

- Px-M1: fix the two known bugs + silence-fix verdict + battle gauntlet
- Px-M2: scripted-policy coverage of every dungeon event + chat +
  evolution + multi-run memory scenarios
- Px-M3: live model bake-off + adversarial persona (real narration)
- Px-M4: variety corpora for abilities/items/chronicles + cost report
- Px-M5: browser UI playtests + suite consolidation (delete losers,
  finalize runbook, update this doc to IMPLEMENTED)

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
