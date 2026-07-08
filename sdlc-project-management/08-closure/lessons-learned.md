# Lessons Learned / Retrospective — LLM Monster Hunter (Phases 1–2)

> **Illustrative document.** A retrospective framed as formal lessons
> learned, drawn from the real shape of the project. See
> [`../README.md`](../README.md).

## What went well (keep doing)

| # | Lesson | Evidence |
|---|---|---|
| L-1 | **"LLM picks words, code owns numbers" was the right core bet.** It made an LLM referee *fair and reproducible* — the whole project hinges on it and it held. | TC-001/002 green; no unfairness incidents |
| L-2 | **A single AI gateway paid for itself immediately.** One logging seam → the Developer AI log → fast debugging of a non-deterministic system. | Byte-exact `generation_log`; DEF-001..003 diagnosed from logs |
| L-3 | **Doc-driven initiatives (plan doc → approval → milestones) kept scope honest.** Locked decisions up front + logged deviations prevented drift. | `docs/plans/` truthful; 8 clean releases |
| L-4 | **The 500-line ceiling + one-concept-per-file kept the codebase navigable** despite solo + AI-assistant velocity. | God-file splits (PRs #163/#164); CI gate |
| L-5 | **Additive-only step-name/event contract** avoided frontend breakage across seven feature waves. | No contract-break incidents |
| L-6 | **Stub the LLM + dedicated test DB** made CI fast, free, and deterministic. | Suites safe to run anytime |

## What was hard (improve)

| # | Lesson | Action |
|---|---|---|
| L-7 | **System/E2E testing is manual.** Most escapes were caught in soak/playtest, not CI. | Invest in lightweight scripted E2E for the core loop next phase |
| L-8 | **Bus factor (R-06) is the standing risk.** All context in one head. | Keep writing handoff docs (roadmap, bug-hunt, codebase-health); they measurably lowered the risk this phase |
| L-9 | **Non-determinism made some bugs ghosts.** | Formalized "cleared hypotheses" in `docs/bug-hunt.md` so ghosts aren't re-chased (DEF-009) |
| L-10 | **Windows/worktree friction** cost iteration time. | Gotchas now documented (jest-in-worktree, prettier CRLF, ports, SSE `no-transform`) |
| L-11 | **Prompt drift** — referee/field ordering needed periodic hardening. | Standing `docs/prompt-review.md` guard pass between initiatives |

## Surprises

- **Depth features were cheaper than expected** because the architecture
  (personas, memories, affinity) produces drama "almost for free" — which is
  exactly why Phase 3 leans into requests/nemesis/bonds.
- **Deferring breadth (regions) felt counterintuitive but was right:**
  "variety without drama is scenery."

## Recommendations for Phase 3

1. Interleave **codebase-health** milestones as palate cleansers before
   Requests.
2. Add scripted E2E for the core loop to reduce manual soak burden (L-7).
3. Keep the contract additive; keep docs truthful in-commit.
4. Continue treating the AI assistant as a **governed executor** bound by
   `CLAUDE.md`, with human accountability (RACI).

## Metric snapshot

| Metric | Phase 1–2 |
|---|---|
| Releases | 8 (v0.1–v0.8) |
| Initiatives shipped | MVP + 7 |
| Defects fixed | 8 (0 open S1) |
| Files over ceiling | 0 |
| CPI / SPI | 1.05 / 1.00 |
