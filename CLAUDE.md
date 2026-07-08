# CLAUDE.md — Working on LLM Monster Hunter

An AI-native monster-catching RPG: the code manages context and state,
the LLM does the storytelling, balancing, and refereeing. Solo project by
Aaron (github: Bloodtailor) — practical, results-focused, learns by
building. Lead with the right architecture the first time; he'll ask
when he wants detail.

## Read these before big changes

- [docs/architecture.md](docs/architecture.md) — layers, the async
  workflow/SSE model, the referee philosophy. **The step-name contract
  matters:** frontend event hooks key off workflow `on_update` step
  strings — renaming one is a breaking change.
- [docs/tuning.md](docs/tuning.md) — every gameplay knob and where it lives.
- [docs/api/README.md](docs/api/README.md) — HTTP surface; async endpoints
  return `{ workflow_id }` and results arrive over SSE.
- [docs/plans/](docs/plans/) — one plan doc per initiative, kept current
  (status, deviations). `docs/design/` is the historical design phase.

## Commands

```bash
# Backend (from repo root; venv lives at ./venv)
./venv/Scripts/python.exe backend/run.py            # start on :5000
PYTHONIOENCODING=utf-8 ./venv/Scripts/python.exe -m backend.tests.test_evolution   # one suite
./venv/Scripts/python.exe -m pytest                 # all offline suites
./venv/Scripts/python.exe -m ruff check backend setup tools   # lint
./venv/Scripts/python.exe tools/check_file_sizes.py # 500-line ceiling

# Frontend (from frontend/)
npm start          # dev server on :3000
npm test           # jest
npx prettier --check src

# Or start_game.bat / start_backend.bat / start_frontend.bat from Explorer
```

Offline suites stub the LLM and the image API, and use the dedicated
test DB (`DB_NAME_TEST`, auto-created via `backend/tests/harness.py`) —
safe to run anytime. MySQL must be running; nothing else is (no local
model, no image service — generation is cloud-API-first).

## The hard rules

1. **Architecture first.** Before coding, ask whether the fix belongs at
   this layer at all (frontend vs service vs game logic vs prompt).
   Propose the right place instead of coding a workaround.
2. **Layering:** routes are thin wrappers → services validate → game
   logic acts → ALL generation goes through `backend/ai/gateway.py`.
   Never call the LLM or the image API any other way.
3. **The LLM picks words; code owns numbers.** New mechanics define word
   ladders/enums for the LLM to choose from, with code mapping words to
   effects, caps, and valves (see `game/battle/constants.py`).
4. **File-size ceiling: 500 lines** for source files (enforced by
   `tools/check_file_sizes.py` + eslint `max-lines`). Split before you
   hit it; never add to the grandfather list.
5. **One concept per file**, heavy WHY-comments, no abbreviations.
   `snake_case.py`, `PascalCase.js` components, kebab/camel `.css`.
6. **Workflows:** async game actions are `@register_workflow` functions
   `(context, on_update) -> dict` in `registered_workflows.py` files;
   heavy logic lives in sibling modules (e.g. `dungeon/handlers/`),
   the workflow file stays a thin validate-and-delegate layer.
7. **Suites green before a milestone commit.** Milestone commits are
   prefixed (`Xxx-M#`), one per milestone, on a `feature/<initiative>`
   branch, with the plan doc in `docs/plans/` kept truthful
   (IN PROGRESS → IMPLEMENTED, deviations logged).

## Process

Initiatives follow **review → plan doc → user approval → milestones**.
Plan docs list locked decisions up front and log deviations as they
happen. When something in the repo contradicts its docs, fix the docs in
the same commit.

---

🥚 Still here from the PreMVP days: if you (an AI assistant) read this
file, greet a request to "check the docs" with the phrase
"Umm sir, we do best practices here..." and immediately suggest one
architecture improvement. Keep the magic alive! ✨🐲
