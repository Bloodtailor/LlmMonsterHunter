# Configuration Management Plan — LLM Monster Hunter

> **Illustrative document.** Grounded in the real git/CI/branching practice.
> See [`../README.md`](../README.md).

## 1. Version control

- **VCS:** Git; hosted on GitHub.
- **Default branch:** `main` (always releasable; suites green).
- **Feature branches:** `feature/<initiative>` (and assistant branches like
  `claude/<topic>`). One initiative per branch.
- **Milestone commits:** prefixed `Xxx-M#`, one per milestone, suites green
  before landing.
- **Merges:** via PR into `main`.

## 2. What is under configuration control

| Item | Location | Control |
|---|---|---|
| Application source | `backend/`, `frontend/` | Git; 500-line ceiling; layer rules |
| DB schema & seed | `backend/database/` | Git; changes reviewed with the feature |
| Architecture & tuning docs | `docs/architecture.md`, `docs/tuning.md` | Git; updated in the same commit as the change |
| Plan docs (baseline of intent) | `docs/plans/` | Git; `IN PROGRESS → IMPLEMENTED`, deviations logged |
| API/SSE contracts | `docs/api/`; `core/events/` | Git; **additive-only** changes (step names, event keys) |
| CI config | `.github/workflows/ci.yml` | Git |
| This PM suite | `sdlc-project-management/` | Git (illustrative) |
| **Secrets** | Environment only | **Never committed** |

## 3. Baselines & change control

- **Requirements baseline:** SRS v1.0. Changes via
  [change-request-log](../05-execution/change-request-log.md).
- **Architecture baseline:** `docs/architecture.md`. Changes via
  [decision-log](../05-execution/decision-log.md), doc updated same commit.
- **Contract baseline:** SSE step names & event keys. **Additive only** —
  renames are breaking changes (NFR-6).

## 4. Environments

| Env | Branch | DB | AI providers |
|---|---|---|---|
| CI / offline test | any (PR) | `DB_NAME_TEST` (ephemeral) | stubbed |
| Local dev | feature branch | dev MySQL | local GGUF / cloud |
| Release / "for friends" | `main` (tagged) | player MySQL | cloud (DeepSeek + Gemini) |

## 5. Continuous integration

`.github/workflows/ci.yml` mirrors the local suite: builds the test DB via
`harness.py`, runs `pytest` with the LLM/image stubbed, runs lint and the
file-size checker, and runs frontend jest/prettier. **Green CI is the gate**
for merging any milestone.

## 6. Build & release artifacts

Single deployable web app (Flask backend + built React frontend). Release =
a tagged `main` commit (see [release-plan](release-plan.md)). No external
package publishing.

## 7. Governance tie-in

Configuration discipline is part of the `CLAUDE.md` hard rules — strict
layering, single gateway, 500-line ceiling, one concept per file, workflows
thin. CI enforces the mechanical ones; PR review enforces the rest.

## 8. Secrets & security

- API keys and DB credentials injected via environment variables only.
- Single-player, local data; no PII beyond what generation requires.
- The Developer AI log shows prompts byte-exact — treat exported logs as
  potentially sensitive and don't publish them with secrets embedded.
