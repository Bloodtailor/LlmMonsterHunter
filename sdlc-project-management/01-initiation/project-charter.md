# Project Charter — LLM Monster Hunter

> **Illustrative document.** Names, roles, dates, and authority levels below
> are invented to model a formal charter. The real project is solo work by
> Aaron (Bloodtailor). See [`../README.md`](../README.md).

| Field | Value |
|---|---|
| **Project name** | LLM Monster Hunter (LMH) |
| **Charter version** | 1.0 |
| **Date authorized** | 2025-11-10 |
| **Project sponsor** | A. Orelup (Product Owner / Sponsor) |
| **Project manager** | A. Orelup (acting; solo) |
| **Charter status** | Approved |
| **Projected close of Phase 1 (MVP)** | 2026-04-30 |

## 1. Purpose & justification

Existing monster-catching RPGs ship fixed content: a finite bestiary,
scripted dialogue, and hand-authored balance. LLM Monster Hunter tests a
different thesis — that a **large language model can be the game's content
engine and referee at runtime**, while conventional code owns state,
numbers, and fairness. If it works, the game produces effectively
unbounded, personalized narrative content (unique monsters, emergent
dialogue, refereed battles) at near-zero marginal authoring cost.

The project exists to **prove that thesis in a playable vertical slice**
and then grow it into a coherent single-player experience.

## 2. High-level project description

A web-based (React + Flask) single-player RPG in which:

- The player explores procedurally described dungeons and encounters
  monsters that are **generated on demand** by an LLM (identity, persona,
  art via an image API).
- **Battles are refereed by the LLM in words, not numbers** — the model
  narrates and chooses from code-defined word ladders; Python maps words
  to effects, caps, and fairness valves.
- Monsters **persist and grow**: cross-run memories, affinity, and
  transformative evolution.
- All AI generation flows through a single gateway with full logging and
  is streamed to the UI live over Server-Sent Events.

## 3. Objectives & success criteria

| # | Objective | Measurable success criterion |
|---|---|---|
| O1 | Prove LLM-as-content-engine | A player can generate, capture, and battle a unique monster end-to-end without hand-authored content. |
| O2 | Prove LLM-as-referee | Battles resolve via word-ladder refereeing with 0 numeric values in prompts; code enforces all caps/valves. |
| O3 | Persistence & attachment | Monsters retain memories and affinity across ≥3 runs; evolution preserves identity. |
| O4 | Architectural discipline | 100% of AI calls route through `ai/gateway.py`; source files ≤ 500 lines; layer rules enforced in CI. |
| O5 | Playable loop | A titled "run" with a goal, stakes, battles, and a chronicle entry is completable start-to-finish. |

## 4. High-level requirements

- Runtime monster generation (text persona + card art).
- Word-ladder battle system with an LLM referee and code-owned math.
- Async workflow + SSE streaming model for all expensive actions.
- Local **and** cloud text-model support; cloud-first image generation.
- Save state in MySQL; developer tooling to inspect every AI request.

## 5. High-level scope boundaries

**In scope (Phase 1 / MVP):** generation, roster/sanctuary, dungeons,
refereed battles, capture, core persistence, developer AI log.

**Out of scope (Phase 1):** multiplayer, mobile-native clients, monetization,
sound/music, a world map, and social systems (bonds, nemeses) — all
deferred to later phases (see [roadmap](../../docs/roadmap.md)).

## 6. Milestone summary

| Milestone | Target | Phase |
|---|---|---|
| Charter approved | 2025-11-10 | Initiation |
| Requirements & design baselined | 2025-12-20 | Planning |
| MVP feature-complete | 2026-03-31 | Execution |
| MVP released (v0.1) | 2026-04-30 | Deployment |
| Feature initiatives (Loop, Chat, Evolution, Cloud Gen, …) | 2026-05 → 2026-07 | Execution (iterative) |
| Next-phase planning (Requests/Nemesis/Bonds/Regions) | 2026-07-07 | Initiation (Phase 2) |

## 7. Summary budget

Modeled at **USD 6,000** for Phase 1 (see
[budget-and-resources.md](../02-planning/budget-and-resources.md)) —
dominated by notional labor plus real, small cloud-API spend for LLM and
image generation. (In reality: one person's time and personal API credits.)

## 8. Key risks (top 3)

1. **LLM produces unfair or incoherent battle outcomes.** → Mitigated by
   the word-ladder + code-valve architecture (O2). See
   [risk-register.md](../02-planning/risk-register.md) R-01.
2. **AI cost/latency makes play unpleasant.** → Context budgets, queueing,
   provider choice. R-03.
3. **Scope creep from an open-ended "AI can do anything" design.** →
   Initiative gating via plan docs and this charter's phase boundaries. R-05.

## 9. Authority

The Project Manager is authorized to plan iterations, approve changes
within the Phase 1 budget envelope, and manage the backlog. Changes to
scope, budget (>10%), or phase boundaries require Sponsor sign-off (which,
in this solo case, is the same person wearing a different hat).

## 10. Approval

| Role | Name | Signature | Date |
|---|---|---|---|
| Sponsor | A. Orelup | *(approved)* | 2025-11-10 |
| Project Manager | A. Orelup | *(approved)* | 2025-11-10 |
