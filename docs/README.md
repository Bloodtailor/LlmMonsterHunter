# The docs map

This folder holds six kinds of document with different audiences and
opposite maintenance rules. Without that distinction everything reads as
equally binding, which makes the whole folder feel perpetually out of
date — so before reading or updating anything here, find its category.

**Only the first category owns you.** Eleven of the 44 files in `docs/`
have to be true, plus root `CLAUDE.md` and five docs that live in the
code. The rest are records, plans, or daydreams, and several would be
damaged by being brought "up to date".

---

## 1. Binding — must be true

The working contract. If the code contradicts one of these, the doc is a
bug: fix it in the same commit.

| Doc | Covers |
| --- | --- |
| [architecture.md](architecture.md) | Layers, the async workflow/SSE model, the referee philosophy, context budgets, the directory map |
| [tuning.md](tuning.md) | Every gameplay knob, where it lives, its default |
| [api/](api/) (9 files) | The HTTP surface, as a reference for working the frontend without reading backend code |
| `CLAUDE.md` (repo root) | Conventions, commands, the hard rules |

Four more binding docs live **in the code**, not here — the rules for
working in a subtree, kept next to the subtree because nothing can test
them: `backend/game/CLAUDE.md`, `backend/tests/CLAUDE.md`,
`frontend/src/shared/CLAUDE.md`, `frontend/src/components/CLAUDE.md`.
`frontend/src/shared/ui/ui.md` is a fifth — the prop reference for every
UI primitive. Root `CLAUDE.md` indexes them all.

**Parts of this category are enforced, not trusted.**
`backend/tests/test_event_parity.py` asserts that the event catalog in
[api/events-and-sse.md](api/events-and-sse.md) matches the backend
registry exactly, and `test_step_contract.py` guards the step-name
contract. Those cannot silently fall behind. The prose around them still
can — see [plans/congruence-tripwires.md](plans/congruence-tripwires.md).

## 2. Work orders — the current queue

Deliberately diary-like: they carry a status line, log deviations as they
happen, and stay after shipping as the record of what was decided and
why. **Do not tidy the history out of them.**

- [plans/](plans/) — one doc per initiative, 15 of them. Every file states
  `**Status:**` at the top: IMPLEMENTED (12), PLANNED (2 —
  `codebase-health`, `monster-requests`), IN PROGRESS (1 —
  `playtest-suite-expansion`). The status line is the thing to keep
  truthful.
- [bug-hunt.md](bug-hunt.md) — verified bugs and cleared hypotheses from a
  line-level correctness read
- [prompt-review.md](prompt-review.md) — per-template critique of
  `backend/ai/llm/prompts/`

Check these before starting a new initiative; they are written to be
picked up and executed.

**The playtest suite is how these get verified.** `tools/playtest/` holds
the harness (every file heavily commented); its runbook is
`playtest_results/REPORT.md`, which stays the single list of what you can
run and what it found. Zero-cost suites (crash driver, three gauntlets)
run in seconds against the test DB; the corpus and live-model tools spend
real provider calls and say so.

## 3. Aspirational — what might be

Congruent with nothing. There is no such thing as one of these being out
of date, and no maintenance is owed. Update only when you change your mind.

- [roadmap.md](roadmap.md) — ranked gameplay direction (Requests →
  Nemesis → Bonds → Regions)
- [ideas.md](ideas.md) — unranked by effort, ranked by heart
- [design/wish-engine.md](design/wish-engine.md) — design-only proposal,
  no code written
- [design/imagination-engine/](design/imagination-engine/) and
  [design/setting-engine/](design/setting-engine/) — exploratory musings,
  self-labelled as not plan docs

## 4. Historical — must NOT be updated

Records of what was thought at the time. Correcting them destroys the
thing they are for.

- [design/gameplay_design.md](design/gameplay_design.md) and
  [design/story_design.md](design/story_design.md) — Feb 2025 design-phase
  deliverables from the original Waterfall SDLC
- [design/vision-vs-reality.md](design/vision-vs-reality.md) — the July
  2026 retrospective that reads those two back against what got built

## 5. For humans

- `README.md` (repo root) — the project's front door
- `LLM-Monster-Hunter-For-Friends/` — a plain-language explanation for
  friends, no technical background assumed

Update when the pitch, the screenshots, or the setup steps change.

## 6. For curiosity

- `sdlc-project-management/` — an educational reconstruction of what this
  project's paperwork would look like as a formal phased SDLC with a team,
  a sponsor, and a budget. Self-labelled as illustrative; the reality is a
  solo hobby project. Owes nothing to the code.

---

## Not documentation

- [assets/](assets/) — images used by the docs and the README (moodboard,
  diagrams, screenshots)

## Adding a doc

Put it in the category whose maintenance rule you are willing to honour,
and add it here. A binding doc you will not keep true is worse than no
doc — it costs a reader the same time to verify as reading the code, so
they will read the code and stop trusting the folder. If the fact is
enumerable from the source, prefer a tripwire over a sentence.
