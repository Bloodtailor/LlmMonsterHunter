# Work Breakdown Structure (WBS) — LLM Monster Hunter

> **Illustrative document.** Effort estimates are modeled. The WBS leaves
> (work packages) map to real code areas and shipped initiatives. See
> [`../README.md`](../README.md).

## 1. WBS outline

```
1.0 LLM Monster Hunter
├── 1.1 Project Management
│   ├── 1.1.1 Charter, business case, stakeholder analysis
│   ├── 1.1.2 Planning (scope, WBS, schedule, risk, comms)
│   ├── 1.1.3 Status tracking & reporting
│   └── 1.1.4 Closure & lessons learned
│
├── 1.2 Requirements & Design
│   ├── 1.2.1 Business & software requirements (BRD/SRS)
│   ├── 1.2.2 Gameplay & story design (docs/design/)
│   ├── 1.2.3 System architecture (layers, workflows, SSE)
│   └── 1.2.4 Tuning model (word ladders, knobs)
│
├── 1.3 Platform & Architecture Spine
│   ├── 1.3.1 Flask app factory, routing, services layer
│   ├── 1.3.2 MySQL models & migrations/seed
│   ├── 1.3.3 AI gateway + generation logging
│   ├── 1.3.4 AI queue (serialized model calls)
│   ├── 1.3.5 Workflow registry + workflow queue
│   ├── 1.3.6 Event system + SSE stream
│   └── 1.3.7 Provider seam (local GGUF / DeepSeek)
│
├── 1.4 Frontend Shell
│   ├── 1.4.1 React app, contexts, hooks, api services
│   ├── 1.4.2 SSE client + event handler registry
│   ├── 1.4.3 Shared UI component library
│   └── 1.4.4 Screens (game/ + developer/)
│
├── 1.5 Core Gameplay (MVP)
│   ├── 1.5.1 Monster generation (persona + art)
│   ├── 1.5.2 Roster / Sanctuary persistence
│   ├── 1.5.3 Dungeon runs (goals, stakes, danger, paths)
│   ├── 1.5.4 Refereed battle system (word ladders + valves)
│   └── 1.5.5 Capture & negotiation
│
├── 1.6 Depth & Persistence (Phase 2 initiatives)
│   ├── 1.6.1 Monster memory & evolution
│   ├── 1.6.2 Campfire chat + rolling summaries
│   ├── 1.6.3 Evolution Altar
│   ├── 1.6.4 Game Loop v1 (title, themed runs, chronicle)
│   ├── 1.6.5 New Game + Player Character
│   ├── 1.6.6 Game Settings + provider switching
│   └── 1.6.7 Cloud generation (1M ctx floor + Gemini art)
│
├── 1.7 Quality & Tooling
│   ├── 1.7.1 Offline test suites (LLM stubbed, test DB)
│   ├── 1.7.2 CI (.github/workflows/ci.yml)
│   ├── 1.7.3 Lint + file-size ceiling tooling
│   └── 1.7.4 Developer AI log & workflow inspector
│
└── 1.8 Release & Ops
    ├── 1.8.1 Environment setup flows (setup/)
    ├── 1.8.2 Launch scripts (start_*.bat)
    ├── 1.8.3 Release/versioning & rollback
    └── 1.8.4 Maintenance & support
```

## 2. Work package register (selected leaves)

| WBS ID | Work package | Owner (RACI-R) | Est. effort (days) | Real artifact |
|---|---|---|---|---|
| 1.3.3 | AI gateway + logging | Architect | 6 | `backend/ai/gateway.py` |
| 1.3.5 | Workflow registry + queue | Architect | 5 | `core/workflow_registry.py`, `workflow/workflow_queue.py` |
| 1.3.6 | Event system + SSE | Architect | 5 | `backend/core/events/`, `docs/api/events-and-sse.md` |
| 1.5.4 | Refereed battle system | Dev | 10 | `game/battle/constants.py` + battle domain |
| 1.6.1 | Memory & evolution | Dev | 8 | `docs/plans/monster-memory-evolution.md` (PR #160) |
| 1.6.4 | Game Loop v1 | Dev | 12 | `docs/plans/game-loop-v1.md` (PR #165) |
| 1.6.7 | Cloud generation | Dev | 9 | `docs/plans/cloud-generation.md` (PR #169) |
| 1.7.2 | CI pipeline | Dev | 2 | `.github/workflows/ci.yml` |

## 3. WBS rules applied

- **100% rule:** the children of each node sum to the whole of that node's
  work; no work exists outside the WBS.
- **Work packages, not activities:** leaves are deliverable-oriented nouns.
- **8/80 heuristic:** each work package is sized between ~1 and ~10 days;
  larger ones (battle system, Game Loop) are decomposed further in their
  `docs/plans/` docs as milestones `Xxx-M1..Mn`.

## 4. Traceability

Each work package traces to one or more requirements in the
[RTM](../03-requirements/requirements-traceability-matrix.md) and to a
schedule milestone in
[schedule-and-milestones.md](schedule-and-milestones.md).
