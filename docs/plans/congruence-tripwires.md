# Congruence Tripwires (Cng)

**Status: IN PROGRESS**
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

### Cng-M2 — The step-name contract — **IN PROGRESS**

Workflow `on_update` step strings are the contract `docs/architecture.md`
calls out as breaking-if-renamed, and they are the least protected thing
in the repo: bare literals assigned to a local `step` variable in each
workflow, hand-copied into label maps on the frontend — sometimes in a
different domain folder than the workflow that emits them.

Milestone: give the frontend's references a suite that proves every step
string it keys off is one the backend can actually emit.

### Cng-M3 — The docs map — **PLANNED**

`docs/` holds six kinds of document with different audiences and
different maintenance rules — binding, historical, aspirational, work
orders, for humans, for curiosity — with no signal about which is which.
The cost is not size, it is that everything reads as equally binding, so
nothing feels reliably current.

Milestone: a `docs/README.md` that names each category, lists what is in
it, and states its maintenance rule (must be true / must not be updated /
congruent with nothing).

### Cng-M4 — Contract docs for the unverifiable rules — **PLANNED**

The rules no test can enforce — routes never contain logic, services are
the trust boundary, the LLM picks words and code owns numbers — get
proximity as their only available lever: a short contract doc in the
directory where the temptation to violate them lives.

Scope to decide at the time: which directories earn one (`backend/game/`,
`frontend/src/shared/`, `frontend/src/components/`, `backend/tests/` are
the candidates), and whether they are named `AGENTS.md` or `CLAUDE.md` —
the latter is auto-loaded by Claude Code when working in that subtree,
which is most of the point. Test the loading behavior before choosing.

These files state rules only. Narrative explanation stays in
`docs/architecture.md`; enumerable facts stay tripwired. No duplication.
