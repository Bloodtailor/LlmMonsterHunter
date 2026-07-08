# Change Request Log — LLM Monster Hunter

> **Illustrative document.** Models formal change control. In reality,
> in-initiative changes are recorded as "deviations logged" inside the
> relevant `docs/plans/` doc; this log captures the cross-cutting ones. See
> [`../README.md`](../README.md).

## Process

1. Anyone raises a CR (problem/opportunity + proposed change).
2. PM assesses impact on scope/schedule/cost/risk.
3. Sponsor approves/rejects scope, phase, or >10% budget changes; PM
   approves in-envelope changes.
4. Approved CRs re-baseline the affected plan; the change and its rationale
   are recorded here and (if architectural) in the
   [decision-log](decision-log.md).

## Register

| CR ID | Date | Title | Type | Impact | Decision | Notes |
|---|---|---|---|---|---|---|
| CR-001 | 2026-01-15 | Add **cloud text provider** alongside local model | Scope+ | +5 pts, provider seam | ✅ Approved | Became `ai/llm/providers/` seam; enabled cost/quality tradeoff |
| CR-002 | 2026-02-10 | Enforce **500-line file ceiling** in CI | Quality | +2 pts tooling | ✅ Approved | `tools/check_file_sizes.py`; god-file splits (PRs #163/#164) |
| CR-003 | 2026-05-05 | Elevate **memory & evolution** from "nice-to-have" to Phase 2 P1 | Scope | +13 pts | ✅ Approved | Core to attachment (BO-3); shipped PR #160 |
| CR-004 | 2026-06-02 | Add **player character in party** + new-game world wipe | Scope+ | +8 pts | ✅ Approved | PRs #166/#167; player is the "ninth party member" |
| CR-005 | 2026-06-25 | Swap image path **ComfyUI → Gemini** image API | Change | provider swap | ✅ Approved | Cloud-first; reference-image evolution regen (PR #169) |
| CR-006 | 2026-06-28 | Raise supported **context floor to 1M tokens** | Change | budgeting model shift | ✅ Approved | Budget now about cost/attention, 70% cap (not truncation) |
| CR-007 | 2026-07-01 | Defer **world map / regions** to Phase 3 | Scope− | −21 pts (deferral) | ✅ Approved | "Variety without drama is scenery" — sequence after drama systems |
| CR-008 | 2026-07-05 | Reject **gold economy / shops** | Scope (reject) | — | ❌ Rejected | Currency of the game is affinity & memories; fights the theme |

## Impact summary

- **Net scope:** grew during Phase 2 (memory/evolution, player character,
  cloud gen) while **deferring** structural breadth (regions) and
  **rejecting** theme-breaking additions (economy) — a deliberate "depth
  before breadth" posture.
- **Schedule:** absorbed within the iterative model; no phase re-baseline
  required (initiatives are independently scheduled).
- **Budget:** stayed within the Phase-2 envelope (CPI 1.05).
