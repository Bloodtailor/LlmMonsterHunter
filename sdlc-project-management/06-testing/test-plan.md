# Test Plan — LLM Monster Hunter

> **Illustrative document.** Grounded in the real test approach (offline
> suites, stubbed LLM, dedicated test DB, CI). See [`../README.md`](../README.md).

## 1. Objectives

Verify that the game meets its functional and non-functional requirements —
above all the flagship constraint **NFR-1 ("no numbers in prompts; code owns
all effects")** — while remaining fast and deterministic despite an
inherently non-deterministic LLM.

## 2. Test strategy

The central testing problem is **LLM non-determinism** (R-09). Strategy:

- **Stub the LLM and image API** in all offline suites, so behavior is
  deterministic and free.
- **Dedicated test database** (`DB_NAME_TEST`, auto-built by
  `backend/tests/harness.py`) so suites are safe to run anytime and never
  touch real save state.
- **Byte-exact logging** of every real AI request (`generation_log`) so that
  when non-determinism *does* cause a bug in live play, it is reproducible.
- **Word-ladder assertions** — the most important tests assert that prompts
  contain no numbers and that code applies the correct ladder/cap/valve for
  each LLM-chosen word.

## 3. Test levels

| Level | What | Where | Automation |
|---|---|---|---|
| Unit | Word→effect mapping, caps, valves, context budgeting | `backend/tests/` suites | ✅ CI |
| Integration | Workflow → gateway → (stubbed) provider → events | `backend/tests/` | ✅ CI |
| Contract | Step names & SSE event schemas stable/additive | import-time signature validation; event registry | ✅ CI |
| Frontend | Component/hook behavior | `frontend/` jest | ✅ CI |
| System / E2E | A full run: generate → battle → capture → persist | manual playtest + Developer screen | 🧑 Manual |
| Exploratory | "Does it feel fair/fun?" | playtest debrief | 🧑 Manual |

## 4. Environments

| Env | Purpose | Data | AI |
|---|---|---|---|
| Offline test | CI + local suites | `DB_NAME_TEST` (ephemeral) | Stubbed |
| Local dev | Manual play/verify | Dev MySQL | Local GGUF or cloud |
| "For friends" build | Playtest | Player MySQL | Cloud (DeepSeek + Gemini) |

MySQL must be running for suites; nothing else is required (no local model
or image service needed offline).

## 5. Entry / exit criteria

**Entry (a milestone can be tested):** code compiles/lints; new mechanic has
its word ladder defined; test DB builds.

**Exit (a milestone can ship):**
- All offline suites green (`pytest`) — and the specific new suite passes.
- Frontend jest + prettier clean.
- `ruff` clean; `tools/check_file_sizes.py` reports 0 files > 500 lines.
- For player-facing features: one manual playtest pass with no P0/P1 defects
  open.

## 6. Key test types & representative coverage

| Requirement | Test focus | Suite (example) |
|---|---|---|
| NFR-1 (no numbers) | Battle prompt contains no numeric ladder values | battle suite |
| FR-4 (referee) | impact/cost word → correct ladder step + cap/valve | `test_battle` |
| FR-6 (evolution) | same monster id, lineage recorded, cap-exempt | `test_evolution` |
| FR-6 (memory) | memories extracted with cited sources | memory/chat suite |
| NFR-3 (budgets) | 70% cap respected; flexible blocks clamp to newest | context-limits suite |
| FR-8 (workflows) | signature/naming validated at import; events emitted | workflow suite |
| NFR-4 (reliability) | queued work resumes; finishes on origin provider | queue suite |

See [test-cases.md](test-cases.md) for concrete cases and
[defect-log.md](defect-log.md) for the defect register.

## 7. Roles

| Activity | Owner (RACI) |
|---|---|
| Write/maintain suites | Dev (A/R) |
| Keep CI green | Dev (A/R) |
| Word-ladder correctness | Architect (C) |
| Playtest & exploratory | Playtesters (R), Dev (A) |

## 8. Tooling

`pytest` (all suites), single-suite runner
(`python -m backend.tests.test_evolution`), the in-app **Developer screen**
test runner, `ruff`, `eslint (max-lines)`, `prettier`, jest,
`tools/check_file_sizes.py`, GitHub Actions (`.github/workflows/ci.yml`).

## 9. Risks to testing

- **Non-determinism (R-09):** mitigated by stubbing + logging.
- **Manual-only E2E:** system tests rely on playtests; mitigated by rich SSE
  observability and the Developer AI log.
- **Windows/worktree quirks (R-10):** documented (jest-in-worktree,
  prettier CRLF); watched.
