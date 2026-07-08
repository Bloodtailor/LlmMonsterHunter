# Schedule & Milestones — LLM Monster Hunter

> **Illustrative document.** Dates are modeled to fit the real shipping
> order of initiatives. See [`../README.md`](../README.md).

## 1. Phase timeline

| Phase | Window | Key output |
|---|---|---|
| Initiation | 2025-11-01 → 2025-11-14 | Charter, business case, stakeholder register |
| Requirements | 2025-11-15 → 2025-12-05 | BRD, SRS, backlog |
| Design | 2025-12-06 → 2025-12-20 | Architecture, tuning model baselined |
| Build (MVP) | 2025-12-21 → 2026-03-31 | Core gameplay vertical slice |
| Test & Stabilize (MVP) | 2026-04-01 → 2026-04-25 | Suites green, playtest pass |
| MVP Release (v0.1) | 2026-04-30 | Playable loop shipped |
| Iterative initiatives | 2026-05-01 → 2026-07-07 | Depth features (see below) |
| Phase 2 planning | 2026-07-07 → | Requests / Nemesis / Bonds / Regions |

## 2. Milestone register

| Milestone | Target date | Status | Evidence |
|---|---|---|---|
| M0 — Charter approved | 2025-11-10 | ✅ Done | [charter](../01-initiation/project-charter.md) |
| M1 — Requirements baselined | 2025-12-05 | ✅ Done | SRS v1.0 |
| M2 — Architecture baselined | 2025-12-20 | ✅ Done | `docs/architecture.md` |
| M3 — Gateway + queues + SSE live | 2026-01-31 | ✅ Done | `ai/gateway.py` |
| M4 — Monster generation E2E | 2026-02-20 | ✅ Done | generation workflow |
| M5 — Refereed battles E2E | 2026-03-15 | ✅ Done | `game/battle/` |
| M6 — MVP feature-complete | 2026-03-31 | ✅ Done | vertical slice |
| M7 — MVP released v0.1 | 2026-04-30 | ✅ Done | tagged release |
| M8 — Monster memory & evolution | 2026-05-20 | ✅ Done | PR #160 |
| M9 — Campfire chat | 2026-05-31 | ✅ Done | monster-chat plan |
| M10 — Evolution Altar | 2026-06-10 | ✅ Done | evolution-altar |
| M11 — Game Loop v1 | 2026-06-20 | ✅ Done | PR #165 |
| M12 — New Game + Player Character | 2026-06-28 | ✅ Done | PRs #166/#167 |
| M13 — Game Settings + DeepSeek | 2026-07-01 | ✅ Done | PR #168 |
| M14 — Cloud generation | 2026-07-04 | ✅ Done | PR #169 |
| M15 — Phase 2: Monster Requests | 2026-08-15 | ⏳ Planned | `docs/plans/monster-requests.md` |
| M16 — Phase 2: Nemesis Arcs | 2026-09-30 | ⏳ Planned | roadmap #2 |
| M17 — Phase 2: Party Bonds | 2026-11-15 | ⏳ Planned | roadmap #3 |
| M18 — Phase 2: Regions | 2027-01-31 | ⏳ Planned | roadmap #4 |

## 3. Gantt (illustrative, month granularity)

```
2025           2026
 N  D | J  F  M  A  M  J  J  A  S  O  N  D | 2027 J
Init ▓
Req  ▓▓
Dsgn  ▓▓
Build   ▓▓▓▓▓▓▓▓
Test           ▓▓
MVP rel          ◆ (Apr 30)
Mem/Evo            ▓▓
Chat               ▓
Altar               ▓
Loop v1             ▓▓
NewGame              ▓
Settings              ▓
CloudGen              ▓
Requests(P2)            ▓▓▓
Nemesis(P2)                ▓▓▓
Bonds(P2)                     ▓▓▓▓
Regions(P2)                        ▓▓▓▓▓▓
```

`◆` = release milestone. `▓` ≈ one active month of work on that track.

## 4. Critical path (Phase 1)

`Charter → Requirements → Architecture → Gateway/Queues/SSE (M3) →
Generation (M4) → Refereed Battles (M5) → MVP complete (M6) → Release (M7)`.

The **gateway + workflow + SSE spine (M3)** is the critical predecessor for
almost everything — generation, battles, chat, and evolution all queue
workflows and stream over SSE. Slippage there cascades. This is why it was
scheduled first and hardened before feature work began.

## 5. Dependencies & sequencing notes

- Phase 2 initiatives are **deliberately ordered** (Requests → Nemesis →
  Bonds → Regions): drama before structure. "Variety without drama is
  scenery" — see [`docs/roadmap.md`](../../docs/roadmap.md).
- Codebase-health milestones (`docs/plans/codebase-health.md`) are
  interleaved between initiatives as palate cleansers.
