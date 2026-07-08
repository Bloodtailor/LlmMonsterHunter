# Risk Register — LLM Monster Hunter

> **Illustrative document.** Risks are real to a project of this kind; scores
> and owners are modeled. Scoring: Probability (1–5) × Impact (1–5) =
> Exposure (1–25). See [`../README.md`](../README.md).

## Heat legend

- 🟥 **High** (15–25) — active mitigation, tracked weekly.
- 🟧 **Medium** (8–14) — mitigation planned, tracked at milestones.
- 🟩 **Low** (1–7) — accept/monitor.

## Register

| ID | Risk | Cat. | P | I | Exp. | Level | Response | Owner |
|---|---|---|---|---|---|---|---|---|
| R-01 | LLM referee produces **unfair/incoherent battle outcomes** | Technical | 4 | 5 | 20 | 🟥 | **Mitigate:** word-ladder architecture — LLM picks words, code owns caps/valves/softlock guards; fairness guardrails in `game/battle/constants.py`. | Architect |
| R-02 | **Prompt/context brittleness** — renamed step names or event keys silently break the frontend | Technical | 3 | 4 | 12 | 🟧 | **Mitigate:** treat step names & SSE payload keys as a public contract; additive changes only; documented in `architecture.md`. | Architect |
| R-03 | **AI cost/latency** makes play unpleasant or expensive | Cost/Perf | 3 | 4 | 12 | 🟧 | **Mitigate:** context budgets (70% cap), rolling summaries, serialized queue, provider switch to local. | Dev |
| R-04 | **Provider dependency** — cloud LLM/image API changes pricing, policy, or availability | External | 3 | 3 | 9 | 🟧 | **Mitigate:** provider seam abstracts vendors; local GGUF fallback for text. **Transfer:** none. | Architect |
| R-05 | **Scope creep** from open-ended "AI can do anything" design | Scope | 4 | 3 | 12 | 🟧 | **Mitigate:** initiative gating (plan doc → approval → milestones); charter phase boundaries; roadmap parking lot. | PM |
| R-06 | **Solo bus factor** — one person holds all context | Resource | 4 | 4 | 16 | 🟥 | **Mitigate:** heavy WHY-comments, `docs/` kept truthful, one-concept-per-file, handoff docs (bug-hunt, roadmap, codebase-health). | PM |
| R-07 | **File/complexity sprawl** degrades maintainability | Technical | 3 | 3 | 9 | 🟧 | **Mitigate:** 500-line ceiling enforced in CI; split-before-you-hit-it; god-file splits already done (PRs #163/#164). | Architect |
| R-08 | **Content safety** — image/text API returns policy-violating output | Compliance | 2 | 4 | 8 | 🟧 | **Mitigate:** single logged image path; prompt constraints; provider policy reliance. **Accept residual.** | Dev |
| R-09 | **Non-determinism** makes bugs hard to reproduce | Technical | 4 | 3 | 12 | 🟧 | **Mitigate:** LLM stubbed in offline suites; every request logged byte-exact for replay; dedicated test DB. | Dev |
| R-10 | **Windows/worktree dev-env quirks** slow iteration | Tooling | 3 | 2 | 6 | 🟩 | **Monitor:** documented gotchas (jest-in-worktree, prettier CRLF, launch.json, ports). | Dev |
| R-11 | **Playtester attrition** — too few players for real feedback | Adoption | 3 | 2 | 6 | 🟩 | **Accept/Monitor:** "for friends" build; multi-save deferred until a second regular player. | PM |
| R-12 | **Data loss** — no formal backups of MySQL save state | Ops | 2 | 4 | 8 | 🟧 | **Mitigate:** schema + seed in repo; new-game wipe is intentional; add backup step to runbook. | Dev |

## Top risks & why they matter most

- **R-01 (20)** is the *thesis risk* — if refereeing can't be fair, the
  whole bet fails. It is retired to a residual level by the core
  architecture, which is why that architecture is non-negotiable.
- **R-06 (16)** is the *reality risk* — a single contributor. The entire
  `docs/` discipline (architecture, plans, handoff docs) exists largely as
  a bus-factor mitigation.

## Review cadence

Top (🟥) risks reviewed each week (see
[communication-plan](communication-plan.md)); 🟧 at each milestone; 🟩 at
phase boundaries. New risks enter via the
[change/decision logs](../05-execution/decision-log.md).
