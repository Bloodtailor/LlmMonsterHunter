# Software Requirements Specification (SRS) — LLM Monster Hunter

> **Illustrative document.** Grounded where possible in the real
> architecture (`docs/architecture.md`). See [`../README.md`](../README.md).

## 1. Introduction

### 1.1 Purpose
Specifies the functional and non-functional requirements for LLM Monster
Hunter (LMH), an AI-native single-player monster-catching RPG.

### 1.2 Scope
See [scope-statement](../02-planning/scope-statement.md). This SRS covers
the MVP plus the depth initiatives shipped in Phase 2.

### 1.3 Definitions
See [glossary](../glossary.md).

## 2. Overall description

### 2.1 Product perspective
Three-tier web application:
- **Frontend:** React (screens → contexts → hooks → api services), SSE
  client.
- **Backend:** Flask (routes → services → game logic → AI gateway →
  queues), SQLAlchemy models, event system.
- **External:** text LLM (DeepSeek cloud / local GGUF) and Gemini image API,
  both reached only through `ai/gateway.py`.

### 2.2 User classes
- **Player** — plays the game.
- **Developer** — uses the Developer screen (AI log, workflow inspector,
  test runner).

### 2.3 Operating environment
Windows-primary dev (PowerShell, `./venv`), MySQL, Node/React dev server,
modern browser with EventSource support.

### 2.4 Design & implementation constraints
- All AI generation MUST route through `ai/gateway.py` (single seam).
- The LLM MUST NOT receive or emit game numbers; word ladders only.
- Source files ≤ 500 lines; one concept per file.
- Async actions return `{ workflow_id }`; results arrive over SSE.
- **Workflow step names & SSE payload keys are a stable contract.**

## 3. Functional requirements

### FR-1 Monster generation
- FR-1.1 The system shall generate a monster's identity and persona via the
  LLM through the gateway.
- FR-1.2 The system shall generate card art via the image API through the
  gateway.
- FR-1.3 Generation shall stream progress and tokens to the UI live over SSE.
- FR-1.4 Every generation shall produce a `generation_log` row visible in
  the Developer screen, byte-exact.

### FR-2 Roster / Sanctuary
- FR-2.1 Captured monsters shall persist in MySQL.
- FR-2.2 The Sanctuary shall auto-refresh as generation events arrive.
- FR-2.3 The player shall form a party from the roster; the player character
  is always in the party.

### FR-3 Dungeon runs
- FR-3.1 A run shall present a themed expedition with a goal and stakes.
- FR-3.2 A run shall have a danger level on the ladder `calm → risky →
  perilous`, mapped by code to difficulty knobs.
- FR-3.3 The player shall choose paths; choices queue workflows and stream
  results.

### FR-4 Refereed battle
- FR-4.1 Combat shall use word ladders (wellbeing, reserves, affinity), not
  numbers, in all prompts.
- FR-4.2 The LLM referee shall narrate an action and return a single impact
  word (`light/heavy/devastating/heal_*`) and cost word
  (`minor/moderate/heavy/restore_*`).
- FR-4.3 Code shall map those words to ladder steps and apply caps, softlock
  valves, and fairness guardrails (`game/battle/constants.py`).
- FR-4.4 A `wary` monster shall be able to act autonomously in battle
  (`game/monster/affinity.py`).

### FR-5 Capture & negotiation
- FR-5.1 The player shall attempt to recruit monsters, including hostile or
  wary ones, via a negotiation flow.

### FR-6 Persistence: memory, affinity, evolution
- FR-6.1 The system shall extract durable memories from logs/dialogue with
  cited sources.
- FR-6.2 Affinity shall progress on the ladder `wary → familiar → trusting →
  devoted` with code-owned movement.
- FR-6.3 A monster shall evolve at the home base, keeping the same monster
  id, updating lineage, and regenerating art.
- FR-6.4 Returning monsters shall reappear across runs (friendly/wary/
  hostile).

### FR-7 Campfire chat
- FR-7.1 The player shall converse with a monster at the home base.
- FR-7.2 Chat shall extract memories and maintain rolling summaries.

### FR-8 AI orchestration
- FR-8.1 Expensive actions shall queue a workflow and return `{workflow_id}`.
- FR-8.2 A single workflow worker (DB-backed) shall process workflows and
  emit queue/started/completed/failed events.
- FR-8.3 A single AI queue worker shall serialize model calls.
- FR-8.4 Every SSE event type shall be schema-declared and field-filtered at
  emit time.

### FR-9 Settings
- FR-9.1 The player shall change AI provider/model via a settings overlay;
  changes apply to the next generation without restart.

### FR-10 Developer tools
- FR-10.1 The Developer screen shall show the AI request log, workflow
  state, and a test runner.

## 4. Non-functional requirements

| ID | Category | Requirement |
|---|---|---|
| NFR-1 | Fairness | No numeric game values may appear in any prompt; 100% of caps/effects applied by code. |
| NFR-2 | Observability | 100% of AI requests logged, byte-exact, and inspectable. |
| NFR-3 | Performance/cost | Prompt context capped at 70% of the window; per-block absolute token caps; rolling summaries for long history. |
| NFR-4 | Reliability | Async work is DB-backed; queued work finishes on the provider it started under; no lost workflows on restart. |
| NFR-5 | Maintainability | Source files ≤ 500 lines; one concept per file; strict layering; enforced by CI. |
| NFR-6 | Compatibility | Step names & SSE payload keys are backward-compatible (additive changes only). |
| NFR-7 | Portability | Text generation runs on either local GGUF or cloud provider via one seam. |
| NFR-8 | Testability | Offline suites run with the LLM stubbed and a dedicated test DB, safe to run anytime. |
| NFR-9 | Usability | Live streaming feedback (token stream, progress steps, live card reveal). |
| NFR-10 | Security/privacy | Single-player, local data; secrets via env; no numbers/PII sent beyond what generation requires. |

## 5. External interfaces
- **HTTP API:** async endpoints return `{ workflow_id }`; see
  [`docs/api/README.md`](../../docs/api/README.md).
- **SSE:** `/api/sse/events`; catalog in
  [`docs/api/events-and-sse.md`](../../docs/api/events-and-sse.md).
- **LLM/image providers:** via the gateway/provider seam only.

## 6. Traceability
Every FR/NFR traces to a business requirement and to tests in the
[RTM](requirements-traceability-matrix.md).
