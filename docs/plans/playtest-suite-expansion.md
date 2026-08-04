# Playtest Suite Expansion (Px)

**Status:** PLANNED — written 2026-08-03 as the handoff for a fresh
session. The founding harness (Pt-M0..M5, `feature/playtest-harness`,
PR #181) is built, exercised, and documented; this initiative grows it
into a comprehensive, reusable suite covering EVERY aspect of the game.
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
- **Known bugs to fix FIRST** (they pollute playtest signal): the
  `sneak_past` success-key collision and the fallback-less
  `generate_exit_text` — both written up in REPORT.md with repro
  commands; task chips may already exist. Re-verify each fix with
  `crash_driver.py --runs 6`.
- **In flight at handoff:** the silence-trope fix (3 REGISTER RULE
  lines in `monster_generation.json`, uncommitted) with a 40-monster
  verification corpus at `playtest_results/corpus_after_register_fix.jsonl`
  — check its silence rate vs the 99% baseline
  (`corpus_20260803_variety_report.md`) and commit or revise the
  prompt accordingly.

## The surface inventory (what needs playtests)

Legend: ✅ covered by founding harness · 🟡 partial · ❌ uncovered

1. ✅ **Dungeon exploration loop** — crash driver (3 modes) + agents.
   Gap: rare paths (treasure, returning, use_dungeon_ability/item) get
   only random coverage → add SCRIPTED policies that force each event.
2. 🟡 **Battle system** — random actions only. Build a battle gauntlet:
   forced long battles (softlock valve + fairness guardrail
   assertions), item/ability-heavy policies, full negotiation trees
   (every talk decision), defeat path, stakes, autonomy (wary allies).
3. ❌ **Campfire chat** (`chat_with_monster`) — multi-turn chats with
   real narration; memory-extraction quality (are extracted memories
   faithful to the transcript? verify by comparison, not by asking).
4. ❌ **Evolution altar** (`evolve_monster`) — the ceremony end-to-end
   headless; identity-preservation checks (same id, memories survive).
5. 🟡 **Cross-run memory & returning** — observed accidentally; build a
   deliberate multi-run scenario: befriend → exit → re-enter → verify
   the returning monster remembers truthfully.
6. ❌ **New Game + character creation** (`player_generation` flows).
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

(none yet)
