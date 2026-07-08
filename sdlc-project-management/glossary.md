# Glossary — LLM Monster Hunter SDLC Suite

> Shared terms and acronyms used across this PM suite. Game/architecture
> terms are grounded in the real repo. See [`README.md`](README.md).

## Project-management terms

| Term | Meaning |
|---|---|
| **SDLC** | Software Development Life Cycle — the phased process (Initiation → Planning → Requirements → Design → Build → Test → Deploy → Closure) this folder models. |
| **BRD** | Business Requirements Document — what the business needs. |
| **SRS** | Software Requirements Specification — functional + non-functional requirements. |
| **RTM** | Requirements Traceability Matrix — links requirement → design → code → test. |
| **WBS** | Work Breakdown Structure — deliverable-oriented decomposition of all work. |
| **RACI** | Responsible / Accountable / Consulted / Informed — responsibility assignment. |
| **CR** | Change Request — a controlled change to a baseline. |
| **ADR** | Architecture Decision Record — a logged decision + rationale (here "ADR-lite"). |
| **RAG** | Red/Amber/Green status indicator. |
| **EVM / CPI / SPI** | Earned Value Management; Cost/Schedule Performance Index (>1 = good). |
| **BAC / EV / AC / PV** | Budget at Completion / Earned Value / Actual Cost / Planned Value. |
| **DoR / DoD** | Definition of Ready / Definition of Done. |
| **Milestone (`Xxx-M#`)** | One shippable increment; one commit; suites green before it lands. |
| **Initiative** | One feature effort = review → plan doc → approval → milestones → merge. |

## Game / architecture terms

| Term | Meaning |
|---|---|
| **Gateway** | `ai/gateway.py` — the single path all AI generation must go through; logs every request. |
| **Provider seam** | `ai/llm/providers/` — abstraction over text providers (DeepSeek cloud / local GGUF), resolved per request. |
| **Workflow** | An async game action: a `@register_workflow` function `(context, on_update) -> dict`; returns `{ workflow_id }` and streams results over SSE. |
| **SSE** | Server-Sent Events — the live stream carrying tokens, progress steps, and domain events to the frontend. |
| **Step name** | A workflow `on_update` progress string; part of a **stable contract** the frontend keys off (additive-only). |
| **Word ladder** | An ordered enum of words (e.g. wellbeing `fresh→…→incapacitated`) the LLM chooses from; code maps words to numeric effects/caps/valves. |
| **Referee** | The LLM acting as battle adjudicator — narrates and returns an impact/cost **word**, never a number. |
| **Valve / cap / guardrail** | Code-owned limits that keep LLM-chosen effects fair (e.g. softlock valve, movement caps). |
| **Affinity** | Player↔monster relationship ladder `wary → familiar → trusting → devoted`; low affinity = autonomous behavior. |
| **Chronicle** | The recorded story of a player's runs. |
| **Evolution / lineage** | Transformative home-base change keeping the **same monster id**, recording lineage and regenerating art. |
| **Rolling summary** | LLM-condensed history so long chats/runs stay affordable; raw entries never deleted. |
| **Context budget** | Deliberate token spend under a hard 70%-of-window cap, with per-block absolute caps. |
| **`generation_log`** | The DB table with every AI request, byte-exact, shown in the Developer screen. |
| **`DB_NAME_TEST`** | The dedicated, auto-built test database used by offline suites (LLM stubbed). |
| **500-line ceiling** | Hard max size for a source file; enforced by `tools/check_file_sizes.py` + eslint `max-lines`. |

## People / roles (as modeled in this suite)

| Role | Note |
|---|---|
| **Sponsor / Product Owner** | Owns vision, funding, go/no-go. (Reality: Aaron.) |
| **Project Manager** | Owns plan, risk, backlog. (Reality: Aaron.) |
| **Architect / Lead Dev** | Owns architecture & the hard rules. (Reality: Aaron.) |
| **AI Coding Assistant** | Governed executor bound by `CLAUDE.md`; never "Accountable". |
| **Playtesters** | Friends providing fun/fairness/stability feedback. |
