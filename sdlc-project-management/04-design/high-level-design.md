# High-Level Design (HLD) — LLM Monster Hunter

> **Illustrative summary.** The authoritative design lives in the real repo;
> this HLD summarizes it and points there. See [`../README.md`](../README.md).
>
> **Authoritative sources:**
> [`docs/architecture.md`](../../docs/architecture.md) (layers, async model,
> events, referee philosophy, context budgets),
> [`docs/tuning.md`](../../docs/tuning.md) (every knob),
> [`docs/api/`](../../docs/api/) (HTTP surface & SSE),
> [`docs/design/`](../../docs/design/) (gameplay/story design phase).

## 1. Architectural style

A **thin, strictly-layered** three-tier web app with an **event-driven,
asynchronous** core. One sentence (from `architecture.md`): *a thin Flask
backend orchestrates two AI engines (a text LLM and an image API) through a
single gateway and two queues, streams everything to a React frontend over
SSE — and the LLM only ever picks words, while Python owns every number.*

## 2. Layer model

```
React frontend  →  routes/ (thin)  →  services/ (trust boundary)
   →  game/ (managers=state, generators=LLM calls, workflows)
   →  ai/gateway.py (THE ONLY generation path)  →  ai/queue.py (1 worker)
       →  text provider (DeepSeek / local GGUF)
       →  Gemini image API
game/ <-> MySQL (models/)      game/ -.domain events.-> SSE -.-> frontend
```

**Layer rules:** routes parse/delegate/format only; services own validation
& business rules; game logic is split `manager.py` / `generator.py` /
`registered_workflows.py`; **all** AI generation goes through the gateway;
the provider seam resolves settings per request and stamps provider+model
onto each log.

## 3. Key design decisions (see decision log for rationale)

| # | Decision | Why |
|---|---|---|
| HLD-1 | **Single AI gateway** for all generation | One logging/observability seam; one place to enforce budgets & provider choice. |
| HLD-2 | **Word ladders, not numbers, in prompts** | LLM picks words; code owns effects/caps/valves → fairness + reproducibility (the thesis). |
| HLD-3 | **Async workflows + SSE**, not synchronous HTTP | Expensive AI actions return `{workflow_id}`; results stream live. |
| HLD-4 | **Two serialized queues** (workflow + AI) | One GPU/model → no concurrency; DB-backed for reliability. |
| HLD-5 | **Step names & event keys are a contract** | Frontend hooks key off them; additive-only changes. |
| HLD-6 | **Provider seam** (local/cloud) resolved per request | Cost control + portability without restart. |
| HLD-7 | **Context budgets** (70% cap, per-block caps, rolling summaries) | Spend tokens deliberately for cost & attention. |
| HLD-8 | **500-line ceiling, one concept per file** | Maintainability under solo + AI-assistant development. |

## 4. Data design (summary)

MySQL, one model file per table (`models/`). Core entities: monsters,
memories (with cited sources), lineage (evolution), party/roster, dungeon
runs & chronicle, `generation_log` (every AI request), `game_workflows`
(workflow queue state), `global_variables` (domain manager state),
`game_settings` (provider/model). Details in
[`docs/api/data-models.md`](../../docs/api/data-models.md).

## 5. Interface design (summary)

- **HTTP:** async endpoints return `{ workflow_id }`; sync endpoints return
  data. Catalog: [`docs/api/README.md`](../../docs/api/README.md).
- **SSE:** single `/api/sse/events` stream; every event schema-declared in
  `core/events/` and mirrored by a frontend handler. Catalog:
  [`docs/api/events-and-sse.md`](../../docs/api/events-and-sse.md).
- **Providers:** reached only via the gateway; uniform contract back (text,
  exact token counts, model name).

## 6. Cross-cutting concerns

| Concern | Mechanism |
|---|---|
| Observability | `generation_log` (byte-exact) + Developer screen |
| Reliability | DB-backed queues; work finishes on its origin provider |
| Cost | context budgets, rolling summaries, provider switch |
| Testability | LLM stubbed + dedicated test DB (`harness.py`) |
| Governance | `CLAUDE.md` hard rules; CI file-size + lint gates |
| Compatibility | additive step names / event keys |

## 7. Design-to-requirement trace

Each HLD decision supports specific NFRs: HLD-1→NFR-2, HLD-2→NFR-1,
HLD-3/4→NFR-4/9, HLD-5→NFR-6, HLD-6→NFR-7, HLD-7→NFR-3, HLD-8→NFR-5. Full
trace in the [RTM](../03-requirements/requirements-traceability-matrix.md).
