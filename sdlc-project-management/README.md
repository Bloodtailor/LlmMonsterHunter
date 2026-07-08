# LLM Monster Hunter — SDLC Project Management Suite

> **What this is.** An *educational, illustrative* reconstruction of what
> this project's documentation would look like if it had been run as a
> formal, phased Software Development Life Cycle (SDLC) with a small team,
> a sponsor, a schedule, and a budget.
>
> **The reality.** LLM Monster Hunter is a **solo hobby project** by Aaron
> (GitHub: `Bloodtailor`), built iteratively and documented as it goes in
> [`docs/`](../docs/). It has no sponsor, no team, no budget line, and no
> Gantt chart. Every role, name, date, dollar figure, and status number in
> this folder that is not backed by the real repo is **invented to make the
> example complete** — as the exercise asked. Where a document *can* be
> grounded in the actual codebase (architecture, tuning knobs, shipped
> initiatives, the real process in `CLAUDE.md`), it is.
>
> Read this suite as: *"here is the paperwork a PMO would have produced for
> a project that, in reality, produced working software and a tidy `docs/`
> tree instead."*

---

## How this maps to the real project

The real project already practices a lightweight, doc-driven lifecycle.
The formal-SDLC artifacts below are the "heavyweight" equivalents of
things that genuinely exist:

| Formal SDLC artifact (this folder)        | Real equivalent in the repo                          |
|-------------------------------------------|------------------------------------------------------|
| Requirements Spec (SRS)                   | [`docs/design/`](../docs/design/) design docs        |
| Design documents                          | [`docs/architecture.md`](../docs/architecture.md), [`docs/tuning.md`](../docs/tuning.md) |
| Work Breakdown Structure / Sprint plan    | [`docs/plans/`](../docs/plans/) one plan per initiative |
| Product backlog / roadmap                 | [`docs/roadmap.md`](../docs/roadmap.md), [`docs/ideas.md`](../docs/ideas.md) |
| Test Plan                                 | `backend/tests/` offline suites + `.github/workflows/ci.yml` |
| Change / decision log                     | Git history, PRs, plan-doc "deviations logged" convention |
| Coding standards / governance             | [`CLAUDE.md`](../CLAUDE.md) "The hard rules"          |
| Defect log / bug hunt                     | [`docs/bug-hunt.md`](../docs/bug-hunt.md)            |

## Folder map

```
sdlc-project-management/
├── README.md                       ← you are here
├── glossary.md                     shared terms & acronyms
│
├── 01-initiation/
│   ├── project-charter.md          why we exist, authority, high-level scope
│   ├── business-case.md            problem, options, cost/benefit, recommendation
│   └── stakeholder-register.md     who cares, and how much
│
├── 02-planning/
│   ├── project-management-plan.md  the master plan (ties everything together)
│   ├── scope-statement.md          in-scope / out-of-scope, deliverables, WBS dict
│   ├── work-breakdown-structure.md the WBS itself
│   ├── schedule-and-milestones.md  phases, milestones, the "Gantt"
│   ├── budget-and-resources.md     costs, staffing, run-rate
│   ├── risk-register.md            risks, scores, responses, owners
│   ├── raci-matrix.md              who is Responsible/Accountable/Consulted/Informed
│   └── communication-plan.md       meetings, reports, channels, cadence
│
├── 03-requirements/
│   ├── business-requirements-document.md   BRD — the "what business needs"
│   ├── software-requirements-specification.md  SRS — functional + non-functional
│   ├── user-stories-and-backlog.md         epics → stories → acceptance criteria
│   └── requirements-traceability-matrix.md RTM — requirement → design → test
│
├── 04-design/
│   └── high-level-design.md         architecture summary + pointers to real docs
│
├── 05-execution/
│   ├── sprint-plan.md               iteration structure and a sample sprint
│   ├── status-report-template.md    the weekly template
│   ├── sample-weekly-status-report.md  a filled-in example
│   ├── change-request-log.md        CR register
│   └── decision-log.md              architecture/product decisions (ADR-lite)
│
├── 06-testing/
│   ├── test-plan.md                 strategy, levels, environments, entry/exit
│   ├── test-cases.md                representative test cases
│   └── defect-log.md                sample defect register
│
├── 07-deployment/
│   ├── release-plan.md              versioning, release cadence, rollback
│   ├── deployment-runbook.md        step-by-step operational runbook
│   └── configuration-management-plan.md  branching, CI, environments, secrets
│
└── 08-closure/
    ├── project-closure-report.md    (phase-close) outcomes vs. plan
    ├── lessons-learned.md           retrospective
    └── maintenance-and-support-plan.md  post-release operations
```

## Suggested reading order

1. **Initiation** — charter → business case → stakeholders (the "why").
2. **Requirements** — BRD → SRS → backlog (the "what").
3. **Planning** — PM plan → scope → WBS → schedule → risk (the "how/when").
4. **Design → Execution → Testing → Deployment** (the "build").
5. **Closure** — closure report → lessons learned (the "what we learned").

---

*Document set version 1.0 — compiled 2026-07-07. Illustrative. Not a
governance record of the real project.*
