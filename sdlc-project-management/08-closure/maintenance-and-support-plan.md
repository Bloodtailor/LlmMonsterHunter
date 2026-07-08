# Maintenance & Support Plan — LLM Monster Hunter

> **Illustrative document.** Models post-release operations for a
> local-first, single-player, hobby project. See [`../README.md`](../README.md).

## 1. Support model

Single developer + AI assistants; players are friends. "Support" = bug
triage, occasional API/provider maintenance, and iterative improvement — not
a 24/7 SLA.

## 2. Maintenance categories

| Type | Examples | Cadence |
|---|---|---|
| **Corrective** | Fix defects from playtest/bug-hunt (DEF-xxx) | As found; batched into iterations |
| **Adaptive** | Provider API/pricing/policy changes; model swaps | As vendors change (provider seam absorbs most) |
| **Perfective** | Codebase-health tidiness passes; prompt hardening | Interleaved between initiatives |
| **Preventive** | Keep suites green, ceiling respected, docs truthful | Continuous (CI + in-commit doc rule) |

## 3. Issue intake & triage

- **Sources:** playtest debriefs, `docs/bug-hunt.md`, the Developer AI log.
- **Triage:** severity (S1–S4) → backlog; S1 addressed immediately, others
  batched. "Cleared hypotheses" recorded so ghosts aren't re-investigated.
- **Non-determinism aid:** every failing case is reproducible from its
  byte-exact logged prompt.

## 4. Routine operational tasks

| Task | Frequency | Reference |
|---|---|---|
| Run offline suites before any change lands | Every change | [runbook §5](../07-deployment/deployment-runbook.md) |
| Check API spend / token counts | Weekly | Developer AI log |
| DB backup before a migrating release | Per MAJOR release | [runbook §6](../07-deployment/deployment-runbook.md) |
| File-size ceiling + lint | Every change (CI) | `tools/check_file_sizes.py` |
| Doc truthfulness sweep | Per initiative | `CLAUDE.md` in-commit rule |
| Prompt-review guard pass | Between initiatives | `docs/prompt-review.md` |

## 5. Cost management (ongoing)

Run-rate is dominated by per-generation API cost. Levers: context budgets
(70% cap), rolling summaries, and switching to the **local provider** for
free generation when quality allows. Spend is auditable per request.

## 6. Provider/vendor maintenance

The provider seam (`ai/llm/providers/`) isolates vendor changes. If DeepSeek
or the Gemini image API changes pricing/policy/availability (R-04), the
response is contained to the seam + a settings change — no core rewrite. A
local GGUF fallback exists for text.

## 7. Knowledge continuity (bus-factor mitigation)

The primary maintenance risk is single-contributor knowledge loss (R-06).
Mitigations, all real:
- `docs/architecture.md`, `docs/tuning.md`, `docs/api/` kept current.
- `docs/plans/` as the truthful record of each initiative.
- Handoff docs: `docs/roadmap.md`, `docs/bug-hunt.md`,
  `docs/codebase-health.md`, `docs/prompt-review.md`.
- Heavy WHY-comments; one concept per file; `CLAUDE.md` as the onboarding
  contract for any human or AI contributor.

## 8. End-of-life / handover

If handed to a new maintainer, onboarding path: `CLAUDE.md` →
`docs/architecture.md` → `docs/plans/` (what exists and why) →
`docs/roadmap.md` (what's next) → run the offline suites → play a run with
the Developer screen open.
