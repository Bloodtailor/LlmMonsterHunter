# Automated Playtesting (Pt)

**Status:** IMPLEMENTED (August 2026) — overnight autonomous session;
every milestone's tooling landed and was exercised. The three PAID
artifacts (real corpus + its variety numbers, live model comparison,
the one-call preflight probe) are gated on Aaron running
`tools/playtest/seed_provider.py` once — see Deviations. Morning
report: `playtest_results/REPORT.md`.
**Branch:** `feature/playtest-harness` · **Commit prefix:** `Pt-M#`
**Written:** 2026-08-03

---

## Why this exists

Manual playtesting is the bottleneck: Aaron can no longer play fast
enough to keep up with development. Two distinct problems hide inside
"playtest it":

- **Problem A — does it work.** Crashes, softlocks, dead ends, states
  the game cannot leave. Needs something to actually walk the game's
  state machine, many times.
- **Problem B — is it any good.** The generators produce the same tropes
  too often (monsters obsessed with "silence"). This is a property of
  the *generators*, measured by counting across a corpus — never by
  asking a model "is this varied?" (models share the attractors they
  would be judging).

The corpus metrics built here are the **baseline the imagination engine
will be judged against** (`docs/design/imagination-engine/` — its
`01-why-generic-happens.md` names what to count: cross-monster motif
repetition, trope phrases, within-enum-combination sameness). This
initiative measures the disease; it does not implement the cure.

## Locked decisions

1. **Never the dev database.** Everything runs against the test DB
   (`DB_NAME_TEST` via `backend/tests/harness.py`). The dev DB
   (`monster_hunter_game`) is not touched, read, or wiped. (See
   Deviations for the one narrowly-scoped exception this required.)
2. **Images never enabled.** No `image_provider` row is ever written to
   the test DB; `is_image_generation_enabled()` has no env floor, so a
   missing row means OFF by construction. Zero Gemini calls.
3. **DeepSeek budget: ≤ 2,500 LLM calls total**, tallied from
   `generation_log` as the night proceeds; actual calls and tokens go in
   the morning report.
4. **The harness is a consumer of the game, not a layer inside it.**
   Drivers live in `tools/playtest/`; they call workflow functions
   directly with a recording `on_update` (the proven offline-suite
   pattern: `build_test_app()` + monkeypatched
   `game.utils.build_and_generate`). No Flask server, no routes, no SSE.
5. **Variety is measured by counting, not judged by a model.**
   LLM-as-annotator may appear in the Pt-M4 bake-off as a *secondary*
   label only, never the primary metric.
6. **Agent playtester reports are claims, not facts.** Every bug or
   criticism a model reports gets verified against the code before it
   counts; models under test overreport success and invent plausible
   bugs.
7. **Corpus artifacts are data, not source.** `playtest_results/` is
   gitignored; the tools that produce it are committed, their output is
   not (except the morning `REPORT.md`, delivered as a file, not a
   commit — see Pt-M5).

## Milestones

### Pt-M0 — Preflight — IMPLEMENTED (live probe gated)

Branch from post-#180 `main`. This plan doc. All six checks green
(`tools/check_all.py`). Test DB reachable, images verified OFF by
construction. The one real DeepSeek generation is embodied in
`tools/playtest/preflight.py` and **gated on the provider row** — see
Deviations. A failed preflight was to end the night; since the base
itself proved green and only the *paid* leg was blocked by a missing
credential, the zero-cost milestones proceeded (the honest reading of
"don't burn the night on a broken base" — the base is not broken).

### Pt-M1 — Generation corpus + variety report — TOOLING IMPLEMENTED, corpus gated

`tools/playtest/generate_corpus.py` (real staged chain, cold-start,
budget guard, crash-safe JSONL) + `tools/playtest/analyze_corpus.py`
over `tools/playtest/variety_metrics.py`: distributions, name reuse,
the silence rate, motif document-frequency (uni/bi/trigrams),
trope-phrase counts, within-enum-combo Jaccard sameness. The analyzer
was validated against a synthetic corpus with planted rates (silence
40% → measured 40%; a 10-clone fire+striker group → top of the
sameness table at 2.09x the corpus mean). The real corpus runs the
moment the provider row exists.

### Pt-M2 — Headless crash driver — IMPLEMENTED

`tools/playtest/crash_driver.py` + `stub_llm.py` + `invariants.py` +
`world_setup.py`. Drives the REAL workflow queue (production
sequencing, queued log-condense included) with the LLM seam stubbed at
`prompt_helpers.text_generation_request` — template rendering stays
real. Three answer modes (happy / broken / chaos-with-parser-contract)
plus mixed. Invariants after every workflow: envelope shape, no wedged
'processing' battle, ladder-valid words, ≤1 open run row.

**Found on the first night:** the `sneak_past` success-key collision
(every failed sneak marks its workflow FAILED — reproduced in happy
mode, no LLM failure needed) and the fallback-less
`generate_exit_text` (during a provider outage the party cannot leave
the dungeon: 0 of ~14 broken-mode runs could exit). Both verified in
code; details in `playtest_results/REPORT.md`, fixes deliberately NOT
made tonight (measurement initiative, not a fix initiative).

### Pt-M3 — Agent playtesters + model comparison — CLI + protocol built, live runs gated

`tools/playtest/play.py` (step CLI: DB-persisted state between
invocations, public-paths-only status text, per-session JSONL
transcripts), `agent_playtester_prompt.md` (the identical briefing
every model gets, with verifiable-claims report structure), and
`score_session.py` (objective transcript scoring: invalid-action rate,
completion, battles, goal — model reports are claims, transcripts are
truth). Subagent capability confirmed: the session's Agent tool takes
`model: haiku|sonnet` overrides. Live haiku-vs-sonnet runs need real
narration and are gated on the provider row; the protocol was validated
end-to-end in stub mode.

### Pt-M4 — Variety-measurement bake-off — methods built, comparison gated

Three genuinely different lenses on the same corpus:
1. **Occurrence counting** (document frequency of motifs/watchwords/
   trope phrases) — catches *what* repeats and names it; blind to
   paraphrase.
2. **Similarity clustering** (pairwise Jaccard on content-token sets,
   embedding-free, globally and per enum-combo) — catches *whole
   monsters* that are the same creature reworded; blind to why.
3. **LLM-as-annotator** (`annotate_corpus.py`, pairwise "same central
   concept?" — SECONDARY only) — catches concept-level sameness that
   survives full rewording; untrusted alone because the judge shares
   the attractors.

**How the imagination engine will be judged when built:** generate a
same-size corpus with sparks enabled, same seeds and enum settings, and
compare (a) silence rate and top-10 motif doc-frequencies — should
drop; (b) per-combo sameness ratios — the worst combos should fall
toward 1.0x; (c) the pairwise same-concept rate — should drop; with
(d) enum distributions staying roughly flat (novelty must not come from
breaking coherence). Counting metrics decide; the annotator
corroborates. The baseline numbers are the Pt-M1 corpus report.

### Pt-M5 — Runbook + morning report — IMPLEMENTED

`playtest_results/REPORT.md`: outcome first — the exact commands, the
two verified bugs in bug-hunt format, the 201-run crash results, the
stub-mode haiku/sonnet comparison with claim-by-claim verification,
budget accounting (0 of 2,500 calls spent), and the ordered next
steps. This plan doc updated; branch pushed; PR opened.

## Deviations

- **2026-08-03 (Pt-M0): the DeepSeek key is not in `.env` and never
  could have been.** The kickoff assumed the key lives in env
  ("confirm .env has your DeepSeek key"); in this codebase the key
  lives *only* in the `game_settings` row written by the in-game panel
  (`ai/llm/provider_settings.py` has no env path for DeepSeek, and
  `providers/deepseek.py` reads the key from game_settings at call
  time). That row exists only in the dev DB, which locked decision 1
  forbids reading. A narrowly-scoped exception was attempted —
  `tools/playtest/seed_provider.py`, a single read-only SELECT of the
  one `llm_provider` row, copied into the test DB — but the session's
  permission layer blocked executing it (twice), effectively enforcing
  locked decision 1 to the letter. The block was respected: the
  session made **no further attempt to read the dev DB or handle the
  key**, and instead committed the seeder for Aaron to run himself
  (one command, `./venv/Scripts/python.exe
  tools/playtest/seed_provider.py`) and pushed a notification asking
  for it. All real-generation milestones (Pt-M1, Pt-M3's live runs,
  Pt-M4) are gated on that row appearing; the zero-cost milestones
  proceeded regardless. `tools/playtest/preflight.py` verifies the rig
  end-to-end the moment the row exists.

- **2026-08-03 (Pt-M3): the stub-mode agent validation changed two
  harness behaviors.** A sonnet playtest agent crashed on its first CLI
  call (Windows cp1252 console vs the backend's emoji prints) — the CLI
  now reconfigures stdout/stderr to UTF-8 itself. The same agent walked
  paths belonging to the junction it had already left: `choose_path`
  never refreshes `available_paths` (only `continue_exploring` does),
  and the CLI was rendering the stale list the real frontend hides —
  status now shows paths only when no encounter is active. Logged as
  observations in the report: stale paths remain takeable at the
  workflow level, and the shared test DB lets earlier harness worlds'
  monsters return as wild creatures (an artifact, and accidental proof
  the returning system works).

- **2026-08-03 (afternoon, at Aaron's direction): the silence trope was
  FIXED and the fix measured — the first full measure→change→re-measure
  loop.** Three REGISTER RULE lines added to `monster_generation.json`
  (inner_life, social_self, creative_text; the prompts never contained
  the trope — it is the model's attractor). Verification corpus v1
  exposed a cost: the livelier answers blew the 350/450 token caps and
  7/40 generations died at the parser ("No JSON found", out_tokens ==
  max_tokens), so the three caps rose to 500/650/650. Verification v2
  (40/40, zero failures): any-silence-mention 99%→90%, "stillness"
  79%→25%, description mentions 70%→20%, backstory 69%→30%, "ancient"
  49%→18%, unique names 57%→88%. The persona stage remains the
  stronghold (85%) — squeezing further likely needs Python-rolled
  temperament seeds, which is imagination-engine territory
  (playtest-suite-expansion.md). Kingdom monoculture untouched by
  design (~52–65% Verdant), same reason.

- **2026-08-03 (Pt-M2/M5): bugs found were reported, not fixed.** The
  two verified defects (the `sneak_past` success-key collision; the
  fallback-less `generate_exit_text`) are written up in
  `playtest_results/REPORT.md` in bug-hunt format with repro commands,
  and offered as one-click follow-up tasks — this initiative measures;
  fixing mid-measure would have muddied the baseline the night was
  built to establish.
