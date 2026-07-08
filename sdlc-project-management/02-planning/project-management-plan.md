# Project Management Plan — LLM Monster Hunter

> **Illustrative document.** The master plan that ties the subsidiary plans
> together. See [`../README.md`](../README.md).

## 1. Overview

This plan governs delivery of LLM Monster Hunter across a **hybrid
lifecycle**: an initial **phased (waterfall-style) Phase 1** to baseline
requirements, design, and an MVP, followed by **iterative, initiative-based
delivery** (each new capability = one "initiative" with its own plan doc,
milestones, and feature branch). This mirrors the project's real process,
codified in [`CLAUDE.md`](../../CLAUDE.md):

> *Initiatives follow **review → plan doc → user approval → milestones**.*

## 2. Subsidiary plans (this suite)

| Knowledge area | Document |
|---|---|
| Scope | [scope-statement.md](scope-statement.md) + [work-breakdown-structure.md](work-breakdown-structure.md) |
| Schedule | [schedule-and-milestones.md](schedule-and-milestones.md) |
| Cost | [budget-and-resources.md](budget-and-resources.md) |
| Quality | [../06-testing/test-plan.md](../06-testing/test-plan.md) |
| Resources / roles | [raci-matrix.md](raci-matrix.md) |
| Communications | [communication-plan.md](communication-plan.md) |
| Risk | [risk-register.md](risk-register.md) |
| Requirements | [../03-requirements/](../03-requirements/) |
| Configuration / release | [../07-deployment/](../07-deployment/) |
| Change control | [../05-execution/change-request-log.md](../05-execution/change-request-log.md) |

## 3. Lifecycle & methodology

- **Phase 1 (Nov 2025 – Apr 2026):** phased — Initiation → Requirements →
  Design → Build → Test → MVP Release. Produces the baselined vertical
  slice proving O1–O5.
- **Phase 2+ (May 2026 →):** iterative initiatives. Each initiative:
  1. **Review** the codebase & prior "out of scope" lists.
  2. **Write a plan doc** in `docs/plans/` (locked decisions up front).
  3. **User approval.**
  4. **Milestones** (`Xxx-M1..Mn`), one commit per milestone on a
     `feature/<initiative>` branch, suites green before milestone commits.
  5. **Merge via PR;** keep the plan doc truthful (IN PROGRESS →
     IMPLEMENTED, deviations logged).

## 4. Governance & the "hard rules"

Because the delivery team is effectively one developer plus AI assistants,
governance is encoded as **enforceable rules** rather than committee
process (from `CLAUDE.md`):

1. **Architecture first** — decide the correct layer before coding.
2. **Strict layering** — routes → services → game logic → the single AI
   gateway. No AI call bypasses `ai/gateway.py`.
3. **The LLM picks words; code owns numbers** — new mechanics define word
   ladders/enums; code maps words to effects, caps, and valves.
4. **500-line file ceiling** — enforced by `tools/check_file_sizes.py` and
   eslint `max-lines`.
5. **One concept per file**, WHY-comments, no abbreviations.
6. **Workflows are thin** validate-and-delegate layers; heavy logic in
   sibling modules.
7. **Suites green before milestone commits.**

These substitute for the peer-review controls a larger team would use.

## 5. Baselines

| Baseline | Set at | Change control |
|---|---|---|
| Scope | End of Requirements (2025-12-20) | Change request (CR) + Sponsor sign-off for scope/phase changes |
| Schedule | Same | Re-baseline only on approved CR |
| Requirements | SRS v1.0 | RTM keeps trace; CRs amend |
| Architecture | `docs/architecture.md` | Decision log (ADR-lite) + doc update in the same commit |

## 6. Change management (summary)

All scope/requirement/architecture changes are logged. Small in-initiative
adjustments are recorded as **"deviations logged"** directly in the
relevant `docs/plans/` doc; cross-cutting changes go through the
[change-request-log](../05-execution/change-request-log.md). Architectural
choices are captured in the [decision-log](../05-execution/decision-log.md).

## 7. Definition of Done (project-level)

A deliverable is Done when: code merged to `main` via PR; offline test
suites green in CI; file-size ceiling respected; relevant docs
(`architecture`/`tuning`/`plans`) updated in the same change; and, for
player-facing features, a manual playtest pass.

## 8. Success measures

Tracked against charter objectives O1–O5 and the quality gates in the test
plan. Phase/initiative closure is reported in
[../08-closure/project-closure-report.md](../08-closure/project-closure-report.md).
