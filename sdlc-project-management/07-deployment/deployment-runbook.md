# Deployment / Operations Runbook — LLM Monster Hunter

> **Illustrative document.** Grounded in the real commands from `CLAUDE.md`.
> This is a local-first, single-player deployment. See
> [`../README.md`](../README.md).

## 1. Prerequisites

- **MySQL** running (prod DB + auto-created `DB_NAME_TEST`).
- **Python venv** at `./venv` with backend deps installed.
- **Node**/npm for the frontend.
- **Secrets** via environment: DB credentials, cloud LLM key (DeepSeek),
  image API key (Gemini). Never commit secrets.

## 2. Start the system

**From Explorer (simplest):** run `start_game.bat` (or `start_backend.bat`
+ `start_frontend.bat`).

**From a shell:**

```bash
# Backend (from repo root; venv at ./venv) — serves on :5000
./venv/Scripts/python.exe backend/run.py

# Frontend (from frontend/) — dev server on :3000
npm start
```

Then open the frontend at `http://localhost:3000`.

## 3. Health checks

- Backend up on `:5000`; SSE stream `/api/sse/events` connects.
- Frontend loads the title screen.
- **Developer screen:** AI request log populates on the first generation;
  workflow inspector shows queue state.
- Trigger one generation and confirm a live token stream + a
  `generation_log` row.

## 4. Configuration

- **AI provider/model:** set in-app via the **settings overlay** (applies to
  the next generation, no restart) — backed by the `game_settings` table
  over env (`ai/llm/provider_settings.py`).
- **Tuning knobs:** see [`docs/tuning.md`](../../docs/tuning.md).
- **Env:** DB name/creds, API keys, `PYTHONIOENCODING=utf-8` for suites on
  Windows.

## 5. Pre-release verification

```bash
# All offline suites (LLM + image stubbed, test DB)
./venv/Scripts/python.exe -m pytest

# One suite
PYTHONIOENCODING=utf-8 ./venv/Scripts/python.exe -m backend.tests.test_evolution

# Lint + file-size ceiling
./venv/Scripts/python.exe -m ruff check backend setup tools
./venv/Scripts/python.exe tools/check_file_sizes.py

# Frontend
cd frontend && npm test && npx prettier --check src
```

Green suites + 0 oversized files + clean lint = clear to merge/release.

## 6. Backup & restore (data)

- **Backup (before any MAJOR/migrating release):**
  `mysqldump <prod_db> > backup_YYYYMMDD.sql`
- **Restore:** `mysql <prod_db> < backup_YYYYMMDD.sql`
- Schema & seed of record live in `backend/database/schema.sql` /
  `seed_data.sql`.
- **Note:** the in-game **New Game** action intentionally wipes the world —
  it is a feature, not an incident.

## 7. Common operational issues

| Symptom | Likely cause | Action |
|---|---|---|
| No live tokens in UI | SSE buffered by a proxy | ensure `no-transform`; check port trap (documented fix) |
| Suites report "0 tests" | run from a git worktree | apply worktree jest/config fix (documented gotcha) |
| prettier CRLF noise | Windows line endings | normalize line endings |
| Generation fails / cost spike | provider/key/quota | check settings overlay + Dev AI log token counts; switch to local provider |
| Workflow stuck | queue worker wedged | inspect `game_workflows`; restart backend (DB-backed work resumes) |

## 8. Shutdown

Stop the frontend dev server and the backend process. In-flight,
DB-backed workflows resume on next start and finish on their origin
provider (NFR-4).
