# Defect Log — LLM Monster Hunter

> **Illustrative document.** Models a defect register. Grounded loosely in
> the real bug-tracking practice (`docs/bug-hunt.md` records verified bugs
> and cleared hypotheses). See [`../README.md`](../README.md).

## Severity scale

- **S1 Critical** — blocks play / data loss / unfair outcomes.
- **S2 Major** — significant feature broken, workaround exists.
- **S3 Minor** — cosmetic or edge-case.
- **S4 Trivial** — polish.

## Register

| ID | Summary | Sev | Found in | Status | Resolution |
|---|---|---|---|---|---|
| DEF-001 | Evolution regen produced a "basalt" art artifact / mismatch | S2 | Cloud gen soak | ✅ Fixed | Evolution basalt fix (commit `c7558e2`) |
| DEF-002 | Workflow waiter returned a misleading success on timeout | S2 | Queue review | ✅ Fixed | "Honest waiter errors" (commit `c7558e2`) |
| DEF-003 | Stale workflows accumulated in the queue table | S3 | Queue review | ✅ Fixed | Queue pruning (commit `c7558e2`) |
| DEF-004 | PartyDisplay React key collision after cloud-gen merge | S3 | PR #169 follow-up | ✅ Fixed | PartyDisplay key fix (PR #170) |
| DEF-005 | Developer screen flooded with events during heavy runs | S3 | PR #173 branch | ✅ Fixed | Event throttling on Developer screen |
| DEF-006 | jest reported "0 tests" when run from a git worktree | S3 | Windows worktree | ✅ Fixed | Worktree jest config fix (documented gotcha) |
| DEF-007 | prettier flagged CRLF noise on Windows checkouts | S4 | Windows dev | ✅ Fixed | Line-ending normalization |
| DEF-008 | SSE stream buffered under a proxy (no live tokens) | S2 | Dev env | ✅ Fixed | `no-transform` / port-trap fix (relaxed-satoshi branch) |
| DEF-009 | *Hypothesis:* affinity decay double-applied across runs | S2 | Bug hunt | ⚪ Cleared | Investigated; not reproducible — logged as cleared in `docs/bug-hunt.md` |
| DEF-010 | Verified bugs pending from bug hunt | S2/S3 | `docs/bug-hunt.md` | 🔶 Open | To be pulled into the backlog next iteration |

## Metrics (snapshot @ 2026-07-07, modeled)

| Metric | Value |
|---|---|
| Open S1 | 0 |
| Open S2 | (bug-hunt verified items) — being triaged |
| Open S3/S4 | few, backlogged |
| Fixed this phase | 8 |
| Defect escape (found in playtest vs CI) | mostly caught by soak/playtest — argues for more E2E automation |

## Practice note — "cleared hypotheses" as first-class records

A distinctive practice here (from `docs/bug-hunt.md`) is recording **cleared
hypotheses** (DEF-009) alongside real defects. For a solo, non-deterministic
project, *knowing what was investigated and ruled out* is as valuable as the
fix list — it stops the same ghost from being chased twice.
