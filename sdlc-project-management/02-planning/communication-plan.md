# Communication Plan — LLM Monster Hunter

> **Illustrative document.** Cadences model a formal comms plan; the real
> project communicates mostly through commits, PRs, and `docs/`. See
> [`../README.md`](../README.md).

## 1. Communication matrix

| Communication | Audience | Purpose | Frequency | Channel | Owner |
|---|---|---|---|---|---|
| Weekly status report | Sponsor, PM | Progress, risks, next steps | Weekly (Fri) | Markdown ([template](../05-execution/status-report-template.md)) | PM |
| Initiative plan doc | All | Locked decisions + milestones for a feature | Per initiative | `docs/plans/*.md` | Architect |
| Milestone commit + PR | Team, GitHub audience | Ship & review a milestone | Per milestone | Git / GitHub PR | Dev |
| Decision record (ADR-lite) | Team, future maintainers | Capture an architecture/product decision | As decided | [decision-log](../05-execution/decision-log.md) | Architect |
| Risk review | PM, Architect | Re-score & re-plan risks | Weekly (High) / milestone (Med) | Risk register | PM |
| Playtest debrief | Dev, Playtesters | Fun/fairness/stability feedback | Per playable build | Chat / notes → backlog | Dev |
| Bug hunt log | Dev, PM | Verified bugs & cleared hypotheses | Ongoing | `docs/bug-hunt.md` | Dev |
| Roadmap update | Sponsor, audience | Re-rank fun-per-effort | Per phase | `docs/roadmap.md` | PM |
| Release notes | Players | What changed | Per release | Release tag / changelog | Dev |

## 2. Cadence summary

- **Daily:** individual work; commits with clear messages.
- **Weekly:** status report + high-risk review (Friday).
- **Per milestone:** milestone commit, PR, suites-green gate, plan-doc
  update, decision-log entries.
- **Per initiative:** review → plan doc → approval → milestones → merge.
- **Per phase:** roadmap re-rank, closure report, lessons learned.

## 3. Channels & tools

| Channel | Used for |
|---|---|
| Git commit messages | Fine-grained "what changed and why" |
| GitHub PRs | Milestone review + discussion |
| `docs/plans/` | Initiative-level plan & status (single source of truth) |
| `docs/architecture.md`, `docs/tuning.md` | Standing reference; updated in the same commit as the change |
| `docs/bug-hunt.md`, `docs/roadmap.md`, `docs/ideas.md` | Backlog & known-issue communication |
| This SDLC folder | Formal PM artifacts (illustrative) |

## 4. Documentation-as-communication principle

The project's core communication rule (from `CLAUDE.md`):

> *When something in the repo contradicts its docs, fix the docs in the
> same commit.*

Documentation is treated as a **live communication channel**, not an
afterthought. Plan docs move `IN PROGRESS → IMPLEMENTED` and log deviations
as they happen, so the docs always describe the *actual* system — the
primary way the solo developer (and any future maintainer or AI assistant)
stays in sync with reality.

## 5. Escalation path

`Dev/AI issue → PM (schedule/scope) → Sponsor (phase/budget/scope change)`.
Because these are one person, "escalation" in practice means switching
hats: a scope or phase-boundary change is consciously made as **Sponsor**,
recorded as a change request, and re-baselined.
