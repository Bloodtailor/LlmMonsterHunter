# Requirements Traceability Matrix (RTM) — LLM Monster Hunter

> **Illustrative document.** Links business needs → software requirements →
> design → code → tests → verification. See [`../README.md`](../README.md).

## How to read

Each row traces one requirement end-to-end. "Design/Code" points at the real
repo location; "Test" points at the offline suite or verification method;
"Status" reflects reality.

| BR | SRS (FR/NFR) | User story | Design / Code artifact | Test / Verification | Status |
|---|---|---|---|---|---|
| BR-1 | FR-1.1–1.4 | A-1..A-4 | `ai/gateway.py`; monster `generator.py`; `docs/architecture.md` | Generation offline suite (LLM stubbed); Dev AI log | ✅ |
| BR-2 | FR-4.1–4.4, NFR-1 | B-1..B-3 | `game/battle/constants.py`; `game/monster/affinity.py` | `test_battle` word-ladder/valve assertions | ✅ |
| BR-2 | NFR-1 (no numbers in prompts) | B-2 | Prompt composition in battle `generator.py` | Assertion: prompt contains no numeric ladder values | ✅ |
| BR-3 | FR-2.1, FR-6.1–6.2 | C-1,C-2,D-1 | `models/` (monsters, memories); `game/memory/` | `test_evolution` / memory suite | ✅ |
| BR-4 | FR-6.3–6.4 | D-2 | Evolution Altar; lineage table; art regen | `test_evolution` (same-id, lineage, cap-exempt) | ✅ |
| BR-5 | FR-3.1–3.3 | C-3 | `game/dungeon/run_context.py`; run workflows | Dungeon run suite; playtest | ✅ |
| BR-6 | FR-1.4, FR-10.1, NFR-2 | A-4 | `generation_log`; Developer screen | Manual: Dev AI log shows byte-exact prompt | ✅ |
| BR-7 | FR-9.1, NFR-7 | E-2, E-4 | `ai/llm/provider_settings.py`; `providers/local.py`, `deepseek.py` | Settings suite; provider switch verified per request | ✅ |
| BR-8 | NFR-3 | E-3 | `game/utils/context_limits.py`; `rolling_summary.py` | Context-budget suite; token counts in Dev log | ✅ |
| BR-9 | NFR-5 | (all) | `CLAUDE.md` rules; `tools/check_file_sizes.py`; eslint `max-lines` | `check_file_sizes.py` in CI; ruff/eslint | ✅ |
| BR-10 | FR-7.1–7.2 | D-3 | `game/chat/`; `game/utils/rolling_summary.py` | Chat suite; memory-extraction assertions | ✅ |
| — | FR-8.1–8.4, NFR-4, NFR-6 | (platform) | `core/workflow_registry.py`; `workflow/workflow_queue.py`; `core/events/` | Workflow/event suites; import-time signature validation | ✅ |
| — | NFR-8 | (platform) | `backend/tests/harness.py` (test DB) | `pytest` runs offline suites in CI | ✅ |
| — | NFR-9 | A-3 | SSE client; `useStreamedGeneration`, event handlers | Manual: live card reveal, token stream | ✅ |
| BR-1(future) | FR (Requests) | F-1 | `docs/plans/monster-requests.md` (planned) | TBD | ⏳ |

## Coverage summary

| Requirement set | Total | Traced & tested | Planned | Gaps |
|---|---|---|---|---|
| Business requirements (BR-1..10) | 10 | 10 | — | 0 |
| Functional (FR-1..10) | 10 groups | 10 | Requests/Nemesis/Bonds additive | 0 (MVP+P2) |
| Non-functional (NFR-1..10) | 10 | 10 | — | 0 |

**No orphan requirements** (every BR maps to ≥1 SRS item and ≥1 test) and
**no orphan features** (every shipped work package traces up to a
requirement — see [WBS §4](../02-planning/work-breakdown-structure.md)).

## Verification note on the flagship requirement

**NFR-1 ("no numbers in prompts")** is the project's defining constraint and
is verified two ways: (1) an automated assertion that battle prompts contain
no numeric ladder values, and (2) the byte-exact Developer AI log, where any
leaked number would be visible. This is the requirement most tightly
traced because it *is* the thesis (BO-1/BO-2).
