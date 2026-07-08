# Business Case — LLM Monster Hunter

> **Illustrative document.** Financials and market figures are invented to
> model a business case. See [`../README.md`](../README.md).

## 1. Executive summary

LLM Monster Hunter (LMH) proposes to build a single-player monster-catching
RPG whose content and refereeing are produced at runtime by a large
language model, rather than authored by hand. The strategic bet: **content
that is normally the most expensive part of an RPG becomes marginal-cost**,
enabling an effectively infinite, personalized game from a small codebase.

This case recommends **Option C — build a vertical slice that proves the
LLM-as-referee architecture** before investing in breadth.

## 2. Problem / opportunity statement

Traditional creature-collector RPGs face a *content ceiling*: every
monster, line of dialogue, and balance number is hand-made. This caps
variety and replayability and makes content the dominant cost. Meanwhile,
LLMs can generate coherent characters and narrative cheaply — but naïvely
letting an LLM "run the game" produces unfair, incoherent, or unbounded
results.

**Opportunity:** a hybrid architecture where the *LLM picks words* and
*code owns numbers* could capture LLM creativity while retaining the
fairness and determinism games require.

## 3. Options considered

| Option | Description | Verdict |
|---|---|---|
| **A — Do nothing** | Don't build; the thesis stays untested. | Rejected: forgoes the learning and the product. |
| **B — Conventional RPG** | Hand-author a small bestiary and scripted battles. | Rejected: solves a solved problem; no differentiation; high content cost. |
| **C — LLM hybrid vertical slice** ✅ | Build the smallest playable loop that proves LLM-as-content + LLM-as-referee, code-owned math. | **Recommended.** Highest learning per dollar; de-risks the core bet before scaling. |
| **D — Full LLM-driven game (no guardrails)** | Let the LLM own state and numbers too. | Rejected: unfair, non-reproducible, uncontrollable cost. |

## 4. Benefits

**Strategic / learning (primary for a hobby R&D project):**
- Validates a reusable pattern: *LLM chooses among code-defined enums;
  code owns effects.* Applicable well beyond this game.
- Builds durable competence in async LLM orchestration, streaming UX, and
  prompt/state architecture.

**Product:**
- Near-infinite monster variety and emergent narrative from a small team.
- High replayability; every run is different.
- Emotional attachment via persistent, evolving companions.

## 5. Costs (modeled)

| Category | Phase 1 (MVP) | Notes |
|---|---|---|
| Labor (notional, 1 FTE-equiv @ modeled rate) | ~USD 5,400 | Real cost = personal time |
| LLM API usage (dev + play) | ~USD 300 | Cloud text provider |
| Image generation API | ~USD 200 | Card art |
| Infrastructure (local dev, MySQL) | ~USD 100 | Mostly $0 in reality |
| **Total Phase 1** | **~USD 6,000** | Illustrative |

Ongoing run-rate after launch is dominated by **per-generation API cost**,
which the architecture deliberately manages via context budgets, caching
of persona/identity, and queueing (see
[`docs/architecture.md`](../../docs/architecture.md) "Context budgets").

## 6. Cost/benefit & ROI

As a **hobby R&D** effort, ROI is measured in *capability and a playable
artifact*, not revenue. Break-even is defined as: **a completable play
loop that demonstrably could not have been hand-authored at the same
cost.** The vertical-slice approach (Option C) caps downside — if the
referee thesis fails, it fails cheaply and early.

## 7. Assumptions & constraints

- **Assumption:** a 1M-token context window is available, so prompts fit
  and budgeting is about *cost and attention*, not truncation.
- **Assumption:** cloud LLM + image APIs remain available at hobby-scale
  cost.
- **Constraint:** solo developer; therefore strict architectural rules
  (500-line ceiling, one concept per file, single gateway) substitute for
  team code review.
- **Constraint:** single-player, local-first deployment; no ops team.

## 8. Recommendation

Proceed with **Option C**. Fund Phase 1 (MVP) to prove O1–O5 in the
[charter](project-charter.md). Gate further investment on a working
refereed battle loop. Subsequent breadth (chat, evolution, cloud art,
social systems) is funded per-initiative only after the core bet holds —
which, per [`docs/roadmap.md`](../../docs/roadmap.md), it has.
