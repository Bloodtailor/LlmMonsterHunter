# Architecture

How the pieces fit. The short version: **a thin, strictly-layered Flask
backend orchestrates two AI engines (a local LLM and ComfyUI) through a
single gateway and two queues, streams everything to a React frontend
over SSE — and the LLM only ever picks words, while Python owns every
number.**

Companion docs: [tuning.md](tuning.md) for every knob,
[api/README.md](api/README.md) for the HTTP surface, `CLAUDE.md` at the
repo root for conventions and commands.

## The layers

```mermaid
flowchart TD
    FE["React frontend<br/>(screens → contexts → hooks → api services)"]
    R["routes/ — thin HTTP wrappers<br/>parse request → call service → jsonify"]
    S["services/ — the trust boundary<br/>validation, business rules"]
    G["game/ — the game itself<br/>managers (state) + generators (LLM calls) + registered workflows"]
    AI["ai/gateway.py — THE ONLY WAY to request generation<br/>logs every request, delegates to the AI queue"]
    Q2["ai/queue.py — one worker<br/>LLM + image requests, serialized"]
    LLM["llama-cpp-python<br/>(local GGUF model)"]
    CUI["ComfyUI<br/>(card art)"]
    DB[("MySQL<br/>models/")]
    SSE["SSE stream<br/>core/events/"]

    FE -->|HTTP| R --> S --> G --> AI --> Q2
    Q2 --> LLM
    Q2 --> CUI
    G <--> DB
    G -.->|domain events| SSE
    Q2 -.->|token stream| SSE
    SSE -.->|EventSource| FE
```

Layer rules (enforced by review, soon by habit):

1. **Routes** never contain logic — parse, delegate, format. See any file
   in `backend/routes/`.
2. **Services** own validation and business rules; they are the trust
   boundary. Routes trust services; services trust nothing.
3. **Game logic** lives in `backend/game/<domain>/`, split by role:
   - `manager.py` — owns the domain's state (usually in the
     `global_variables` table)
   - `generator.py` — composes prompts and calls the AI gateway
   - `registered_workflows.py` — the async entry points (below)
   - domain extras (`constants.py`, `events.py`, `handlers/`, …)
4. **All AI generation goes through `ai/gateway.py`.** No exceptions.
   Every request becomes a `generation_log` row — the Developer screen's
   AI log table shows every prompt byte-exactly as the model received it.

## The async workflow model

Expensive actions (generate a monster, choose a path, take a battle turn)
do **not** answer over HTTP. They queue a *workflow* and return
`{ workflow_id }` immediately; results arrive over SSE.

```mermaid
sequenceDiagram
    participant FE as Frontend
    participant RT as Route/Service
    participant WQ as Workflow queue<br/>(workflow/workflow_queue.py)
    participant WF as Workflow fn<br/>(game/*/registered_workflows.py)
    participant GW as AI gateway + queue
    participant EV as Event bus → SSE

    FE->>EV: open /api/sse/events (once, up front)
    FE->>RT: POST /api/dungeon/choose-path
    RT->>WQ: add_workflow('choose_path', context)
    RT-->>FE: { workflow_id }
    WQ->>WF: handler(context, on_update)
    WF->>EV: on_update(step, data) — progress steps
    WF->>GW: text_generation_request(...)
    GW-->>EV: llm tokens stream live
    GW-->>WF: parsed result
    WF->>EV: domain events (monster.created, ...)
    WQ->>EV: workflow.completed / workflow.failed
    EV-->>FE: everything above, as SSE
```

The pieces:

- **`core/workflow_registry.py`** — `@register_workflow` decorator; any
  function in a `registered_workflows.py` file with the signature
  `(context, on_update) -> dict` becomes a queueable workflow. Signature
  and naming are validated at import time (fail fast).
- **`workflow/workflow_queue.py`** — single background worker, DB-backed
  (`game_workflows` table), emits queue/started/completed/failed events.
- **`ai/queue.py`** — a second single worker beneath the gateway that
  serializes actual model calls (one GPU, one model — no concurrency).
- **Step names are a contract.** The frontend's event hooks key off each
  workflow's `on_update` step strings (`useDungeonEvents.js`,
  `useBattleEvents.js`). Renaming a step is a breaking change; treat step
  names and payload keys like an API.

## The event system

- Every event type is declared with a schema in
  `backend/core/events/<domain>_events.py` and registered in
  `core/events/event_registry.py` (fields are filtered to the schema at
  emit time; `send_to_frontend` decides whether SSE carries it).
- The frontend mirrors this: `frontend/src/api/events/*EventHandlers.js`
  registers a handler per event type; components subscribe through
  `useEventSubscription` / `useStreamedGeneration` and update the moment
  their datum arrives (live card reveal, auto-refreshing Sanctuary).
- Catalog: [api/events-and-sse.md](api/events-and-sse.md).

## The referee philosophy (why there are no numbers in prompts)

Combat and resources use **word ladders**, not math
(`game/battle/constants.py`):

- Wellbeing: `fresh → scuffed → wounded → battered → critical → incapacitated`
- Reserves: `brimming → steady → strained → drained → spent`

The LLM referee narrates an action and answers with a single **word**
(impact: `light/heavy/devastating/heal_*`; cost: `minor/moderate/heavy/
restore_*`). Python maps the word to ladder steps, applies caps, softlock
valves, and fairness guardrails. The same pattern rules growth
(tier words → capped percents), returning monsters, and evolution.
**If you're adding a mechanic: let the LLM choose among words you define,
and let code own what the words do.**

## Context budgets (fitting a game into a small model)

`game/utils/context_limits.py` gives every prompt block a budget that
scales with `LLM_CONTEXT_SIZE`:

- **Required blocks** (party/monster identity) are never truncated;
  their *detail tier* (compact/standard/full) is binned by window size.
- **Flexible blocks** (logs, dialogue, memories) each get a percentage
  share and keep their most recent content when clamped.
- **Rolling summaries** (`game/utils/rolling_summary.py`) condense old
  history via the LLM so long chats and runs stay affordable — raw
  entries are never deleted.

## Directory map

```
backend/
  app.py, run.py, startup.py   Flask factory, runner, subsystem init
  routes/       thin HTTP wrappers (one file per domain)
  services/     validation + business rules (the trust boundary)
  game/         monster/ dungeon/ battle/ chat/ inventory/ memory/ state/ utils/
  ai/           gateway.py, queue.py, llm/ (core, prompts, parser), comfyui/
  workflow/     the workflow queue + gateway
  core/         events/, config/, utils/, workflow_registry.py
  models/       SQLAlchemy models (one file per table)
  tests/        offline suites (LLM stubbed, test DB) + dev utilities
frontend/src/
  api/          HTTP client, per-domain services, SSE + event handler registry, stores, transformers
  app/          contexts (Navigation, Party, Dungeon, Battle, Event), api-call hooks
  components/   feature components (battle/, dungeon/, cards/, chat/, evolution/, developer/)
  screens/      game/ (the player's screens) + developer/ (dev tools)
  shared/       ui/ (the component library — see ui.md), styles/, constants, hooks
docs/           architecture (this file), tuning.md, api/, design/ (historical), plans/
setup/          interactive environment setup (checks / flows / installation)
tools/          repo tooling (file-size checker, project stats)
```

## Testing

Offline suites in `backend/tests/` run with the **LLM stubbed** and a
**dedicated test database** (`DB_NAME_TEST`, built by `tests/harness.py`).
Each suite is a readable script of `check(...)` assertions with a
`main() -> failure count`; run one with
`python -m backend.tests.test_evolution`, everything via `pytest`, or
from the in-app Developer screen. CI mirrors this (see
`.github/workflows/ci.yml`).
