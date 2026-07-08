# Sprint / Iteration Plan — LLM Monster Hunter

> **Illustrative document.** Models the iterative delivery as sprints; the
> real cadence is "one initiative = plan doc + milestones on a feature
> branch." See [`../README.md`](../README.md).

## 1. Iteration model

- **Iteration length:** 1–2 weeks (an initiative may span several).
- **Unit of delivery:** a **milestone** (`Xxx-M#`) = one commit on a
  `feature/<initiative>` branch, suites green before it lands.
- **Iteration = one initiative** in the real process: *review → plan doc →
  approval → milestones → merge PR → keep the plan doc truthful.*

## 2. Definition of Ready (a story/initiative can start)

- Plan doc exists in `docs/plans/` with **locked decisions up front**.
- The right architectural layer is identified (architecture-first).
- Word ladders/enums defined for any new mechanic (LLM picks words).
- Acceptance criteria written; approved by the Product Owner.

## 3. Definition of Done (a milestone)

- Code merged via PR; offline suites green in CI.
- No source file > 500 lines; lint clean (ruff/eslint/prettier).
- Docs updated in the same change (plan doc `IN PROGRESS → IMPLEMENTED`,
  deviations logged; `architecture`/`tuning` updated if touched).
- Player-facing features: a manual playtest pass.

## 4. Sample sprint — "Monster Requests M1" (planned)

**Goal:** stand up the request data model + the request-forming workflow
(no UI yet). From [`docs/plans/monster-requests.md`](../../docs/plans/monster-requests.md)
and [roadmap #1](../../docs/roadmap.md).

| Task | Type | Est (pts) | Owner | Layer |
|---|---|---|---|---|
| `monster_requests` table + model | Build | 3 | Dev | models/ |
| Request-type enum + weight ladder (`whim→wish→need→vow`) | Design | 2 | Architect | game constants |
| Request-forming workflow (thin) + handler (sibling module) | Build | 5 | Dev | game/*/registered_workflows.py + handlers/ |
| Prompt: persona + memories → request-type/weight (words only) | Prompt | 3 | Architect | generator.py |
| Offline suite: forming, weight mapping, expiry of `whim` | Test | 3 | Dev | backend/tests/ |
| Plan doc → IN PROGRESS; step names documented | Docs | 1 | Dev | docs/plans/ |

**Sprint acceptance:** a workflow can give a party monster a chance to form
a request; code owns weight consequences; `whim` expires silently; suite
green; no step-name-contract breakage (additive step names only).

## 5. Ceremonies (modeled)

| Ceremony | Cadence | Real analogue |
|---|---|---|
| Planning | Start of initiative | Writing the plan doc + approval |
| Daily check-in | Daily | Solo work log / commit messages |
| Review/demo | End of milestone | PR + playtest |
| Retrospective | End of initiative | Lessons learned; codebase-health milestone as palate cleanser |

## 6. Velocity (modeled)

Phase 2 shipped ~7 initiatives in ~10 weeks — roughly **one initiative per
1–1.5 weeks**, averaging ~13 story points per iteration in the backlog's
Fibonacci scale. Used only for rough forecasting of the planned F-1..F-5
epics.
