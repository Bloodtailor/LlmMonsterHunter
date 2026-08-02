# Congruence Tripwires (Cng)

**Status:** IMPLEMENTED (August 2026) — all four milestones landed.
Pending Aaron's live soak: the affinity badge updating mid-run, which
needs a real dungeon run and could not be driven from a dev session.
**Branch:** `feature/congruence-tripwires` · **Commit prefix:** `Cng-M#`
**Written:** 2026-08-01

---

## Why this exists

Several contracts in this repo are mirrored **by hand** across files that
no tool compares: a string in Python has to equal a string in JavaScript,
and nothing notices when they stop matching. `docs/architecture.md`
already states the most important of these contracts in prose, and the
drift happened anyway — because a document describes a contract, it
cannot detect a violation.

The first pass found exactly that, twice over: `monster.affinity_changed`
shipped with no frontend handler at all, and `game.party_updated` was
missing from the event catalog doc. Neither was noticeable by reading.

**The goal of this initiative is not more documentation. It is to make
the mirrors fail loudly.** Each milestone takes one hand-maintained
mirror and gives it a suite that goes red the moment the two sides
disagree.

## Locked decisions

1. **The backend is the source of truth** in every mirror. Suites assert
   that other surfaces agree with it, never the reverse.
2. **Tripwire suites are offline and cheap** — no DB, no LLM, no network.
   They read source files and compare sets. A suite that needs a running
   game is out of scope here.
3. **Verifiable and unverifiable contracts get different treatments.**
   Facts a machine can enumerate (event names, route lists, step names)
   get tripwires. Judgment rules ("routes never contain logic") cannot be
   tested and get proximity instead — a contract doc next to the code.
   Milestones M1–M2 are the first kind; M4 is the second.
4. **No renaming.** These suites observe existing contracts. Renaming an
   event, a step string, or a workflow is explicitly out of scope — the
   step-name contract in `docs/architecture.md` stays intact.
5. **Reference docs that can be checked, get checked.** `docs/api/` is
   only worth reading if it cannot quietly fall behind, so the parts of it
   that are enumerable are asserted against the code.

## Milestones

### Cng-M1 — Event parity — **IMPLEMENTED**

`backend/tests/test_event_parity.py` asserts four surfaces agree with the
event registry:

- every `send_to_frontend` event has a frontend handler, and every
  handler maps to a real event
- no handler listens for an internal-only event
- every `*EventHandlers.js` file is actually spread into `EventProvider.js`
  (an unwired handler file is inert no matter how correct it looks)
- `docs/api/events-and-sse.md` lists every SSE event and invents none

**Drift found and fixed on the first run:**

- `monster.affinity_changed` was declared, emitted from
  `game/monster/affinity.py`, and had no frontend handler — a monster's
  trust tier climbed mid-run and the party panel kept showing the old
  badge until an unrelated refetch. Handler added to
  `monsterEventHandlers.js`; `PartyProvider` patches the field in place.
- `game.party_updated` was fully wired in code but undocumented in the
  event catalog. Added.

Verification: `python -m backend.tests.test_event_parity` (11 checks),
registered in `test_offline_suites.py` so pytest and CI cover it.

### Cng-M2 — The step-name contract — **IMPLEMENTED**

`backend/tests/test_step_contract.py` asserts every step string the
frontend keys off is one the backend can actually emit.

The contract is **one-directional** by design. A backend step nothing
displays is ordinary — 76 of the 96 steps are progress pings with no
frontend reference. A frontend reference to a step the backend cannot
emit is the bug, because nothing errors: the label just stays blank or
the branch never runs.

Both emission styles are scanned — the older local `step = "name"`
variable and the `WorkflowStep` pointer (`step.emit/.mark/.emit_event`)
used by workflows split across handler modules — as are both reference
styles: `*_STEP_LABELS` maps and inline `step === 'name'` comparisons in
the event hooks.

**Deviation from the original plan:** no new registry was introduced. The
first sketch was to give workflows a declared step manifest, but
`backend/core/workflow_steps.py` already carries the pointer, and adding
a second place to name a step would have created one more mirror to keep
congruent — the exact problem this initiative exists to remove. The
workflow source stays the source of truth and the suite reads it.

**No drift found** — unlike M1, the step contract was intact. The suite
was therefore verified by mutation instead: renaming `designing_form` in
`game/monster/registered_workflows.py` turned it red and named the file
that would have broken (`useMonsterEvolution.js`). The rename was
reverted; a tripwire nobody has seen fail is not yet a tripwire.

The suite also guards its own scanners — if a refactor changes how steps
are written, the step counts fall below their floors and it fails loudly
rather than passing vacuously forever.

Verification: `python -m backend.tests.test_step_contract` (4 checks),
registered in `test_offline_suites.py`.

### Cng-M3 — The docs map — **IMPLEMENTED**

`docs/README.md` sorts every documentation surface into its six
categories and states each one's maintenance rule. Every file was
classified from its own header rather than from memory.

The headline it exists to deliver: **eleven of the 44 files in `docs/`
are binding** (`architecture.md`, `tuning.md`, the nine `api/` files),
plus root `CLAUDE.md`. The rest are records, plans, or daydreams, and
several — the Feb 2025 design deliverables, the retrospective — would be
damaged by being brought "up to date". The folder felt like a standing
debt because nothing said which was which.

Plan-doc status lines were also normalised to one markup, `**Status:**`
followed by the value. Three files wrapped the value inside the bold
(`**Status: PLANNED**`) and one had no bold at all, so any reader — or
future tripwire — scanning statuses would have missed them. All 13 now
match, which is what lets the map state the counts as fact.

**Correction found while classifying:** `CLAUDE.md` described
`docs/design/` as "the historical design phase". It is mixed — the Feb
2025 deliverables and `vision-vs-reality.md` are frozen history, while
`wish-engine.md`, `imagination-engine/`, and `setting-engine/` are
unbuilt proposals that are congruent with nothing. Reading them under the
wrong rule would have been misleading in both directions. Fixed, and
`CLAUDE.md` now points at the map first.

The map also records which docs are tripwired rather than trusted, so a
reader can tell at a glance which claims are enforced.

### Cng-M4 — Contract docs for the unverifiable rules — **IMPLEMENTED**

Four subtrees now carry a `CLAUDE.md` holding the rules no suite can
enforce: `backend/game/`, `backend/tests/`, `frontend/src/shared/`,
`frontend/src/components/`. Root `CLAUDE.md` indexes them and instructs
that the nearest one be read before editing in its subtree.

Each states rules only — the file-role conventions inside a game domain,
the suite shape and the registration trap in `test_offline_suites.py`,
what earns a place in `shared/` versus a feature folder, where component
state and live updates come from. Narrative explanation stays in
`docs/architecture.md`; repo-wide rules stay in root `CLAUDE.md`; nothing
is restated in two places.

**Naming: `CLAUDE.md`, and the deciding test was inconclusive.** Probe
files were planted at `backend/game/AGENTS.md` and
`backend/game/CLAUDE.md` and files in that subtree were read; neither
marker appeared in context. That does not prove nested auto-load is
unsupported — context files are plausibly discovered at session start, so
a file created mid-session would not be picked up either way, and the
test cannot tell those cases apart from inside one session.

The choice was therefore made on other grounds: this is a solo project
worked through Claude Code, `CLAUDE.md` is the name that toolchain is
built around, and cross-tool portability is speculative value. Because
auto-load could not be confirmed, **the root file names the four docs
explicitly** — the chain is read by instruction, not by hoping the
harness injects it. That holds whichever way auto-load actually behaves,
and the decision is a rename away from being reversed.

**Correction to M3:** the docs map listed only `docs/` and root
`CLAUDE.md` as binding. Five binding docs live in the code — these four
plus `frontend/src/shared/ui/ui.md`, the prop reference for the UI
primitives. The map now says so.
