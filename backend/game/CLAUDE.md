# backend/game/ — the game itself

Rules for working in this directory. Repo-wide rules (layering, the
gateway, the 500-line ceiling, word ladders) are in the root `CLAUDE.md`
and are not repeated here. The narrative explanation of *why* the layers
exist is [docs/architecture.md](../../docs/architecture.md).

## The domains

Nine, each owning one part of the game:

`battle` · `chat` · `dungeon` · `inventory` · `memory` · `monster` ·
`player` · `state` · `utils`

`state/` owns the world itself (new game, global state) and `utils/` is
shared machinery (context budgets, prompt helpers, rolling summaries) —
neither is a gameplay domain.

## File roles inside a domain

Every file name means something. Match the convention rather than
inventing a new shape:

- `manager.py` — owns the domain's state. Every domain has one.
  Persistent run state usually lives in the `global_variables` table
  (`dungeon_state`, `battle_state`), not in module globals.
- `generator.py` — composes prompts and calls the AI gateway. This is the
  only kind of file in a domain that talks to the LLM.
- `registered_workflows.py` — the async entry points. **Keep these thin:
  validate, delegate, return.** When logic outgrows the file it moves to
  a sibling package (`dungeon/handlers/`, `battle/turn/`), not into the
  workflow.
- `constants.py` — the word ladders and enums the LLM chooses among.
- Anything else is a named domain concern (`affinity.py`, `goal.py`,
  `spoils.py`, `evolution_eligibility.py`). One concept per file.

## Contracts that reach outside this directory

Both are enforced — breaking them fails a suite, not a review:

- **Step names.** Workflow `on_update` strings are a frontend contract.
  Renaming one breaks `tests/test_step_contract.py`. Steps come either
  from a local `step` variable or the shared `WorkflowStep` pointer
  (`core/workflow_steps.py`) when a workflow spans handler modules.
- **Events.** Declared in `core/events/<domain>_events.py`. A new event
  with `send_to_frontend: True` needs a frontend handler and a line in
  `docs/api/events-and-sse.md` in the same change, or
  `tests/test_event_parity.py` fails.

## Adding a domain

Register its workflows by importing the package in `game/__init__.py` —
`@register_workflow` validates signatures at import time, so a domain
that is never imported silently has no workflows.

## Verification

```bash
./venv/Scripts/python.exe -m ruff check backend
PYTHONIOENCODING=utf-8 ./venv/Scripts/python.exe -m pytest
./venv/Scripts/python.exe tools/check_file_sizes.py
```
