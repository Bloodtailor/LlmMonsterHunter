# Business Requirements Document (BRD) — LLM Monster Hunter

> **Illustrative document.** See [`../README.md`](../README.md).

## 1. Document control

| Field | Value |
|---|---|
| Version | 1.0 (baselined 2025-12-05) |
| Author | PM / Product Owner |
| Approved by | Sponsor |

## 2. Business background & vision

RPG content is traditionally hand-authored and therefore finite and
expensive. LMH's vision is a monster-catching RPG where **an LLM is the
content engine and referee at runtime**, code owns all state and numbers,
and the result is an effectively infinite, personalized, fair game built by
a very small team.

## 3. Business objectives (BO)

| ID | Business objective | Success measure |
|---|---|---|
| BO-1 | Prove LLM-generated content can replace hand-authoring | A unique monster is generated, captured, and battled with zero authored content. |
| BO-2 | Keep gameplay **fair and reproducible** despite an LLM referee | All numbers/caps owned by code; bugs reproducible from logged prompts. |
| BO-3 | Create **emotional attachment** to companions | Monsters persist, remember, and evolve across runs. |
| BO-4 | Sustain development by **one person + AI assistants** | Architectural rules + docs keep the codebase maintainable (500-line ceiling, single gateway). |
| BO-5 | Control **runtime AI cost** | Per-generation cost bounded by context budgets & caching; spend auditable. |

## 4. Business requirements (BR)

| ID | Requirement | Priority | Traces to |
|---|---|---|---|
| BR-1 | The game shall generate monsters (identity, persona, art) on demand without pre-authored content. | Must | BO-1 |
| BR-2 | Battles shall be narrated and adjudicated by the LLM but resolved numerically by code. | Must | BO-1, BO-2 |
| BR-3 | Monsters shall persist across sessions and runs, retaining memories and affinity. | Must | BO-3 |
| BR-4 | Monsters shall be able to grow and to transform (evolve) while keeping their identity. | Should | BO-3 |
| BR-5 | The player shall progress through themed "runs" with goals, stakes, and a chronicle. | Must | BO-1, BO-3 |
| BR-6 | Every AI request shall be logged and inspectable. | Must | BO-2, BO-5 |
| BR-7 | The system shall support both a local and a cloud text model, switchable without restart. | Should | BO-5 |
| BR-8 | AI cost per session shall be bounded and observable. | Must | BO-5 |
| BR-9 | The system shall be maintainable by one developer + AI assistants (enforced code standards). | Must | BO-4 |
| BR-10 | The player shall converse with monsters at the home base, producing durable memories. | Should | BO-3 |

## 5. Stakeholders

See [stakeholder-register](../01-initiation/stakeholder-register.md).

## 6. Constraints & assumptions

- **Constraint:** single-player, web-based, local-first, MySQL-backed.
- **Constraint:** solo delivery; standards substitute for peer review.
- **Assumption:** 1M-token context floor; cloud APIs remain affordable.

## 7. Out of scope

Multiplayer, mobile-native, monetization, sound, world map, and social
systems in Phase 1 (see [scope-statement](../02-planning/scope-statement.md)).

## 8. Acceptance

The BRD is satisfied when BR-1…BR-10 are each traced through the
[SRS](software-requirements-specification.md) to design and tests in the
[RTM](requirements-traceability-matrix.md), and the corresponding features
pass their acceptance criteria.
