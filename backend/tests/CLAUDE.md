# backend/tests/ — offline suites and dev utilities

Rules for working in this directory. Repo-wide rules are in the root
`CLAUDE.md`.

## Two kinds of file live here

- **Suites** (`test_*.py`) — readable scripts of `check(...)` assertions.
- **Dev utilities** (`add_*.py`, `reset_db.py`, `clear_following.py`,
  `random_location.py`, `generate_monster_profiles.py`) — one-off scripts
  run by hand. They are not suites and must not be registered as such.

## Suite shape

Copy an existing suite rather than inventing a shape. Every suite has:

- module-level `PASSED` / `FAILED` counters and a
  `check(name, condition, detail='')` helper that prints ✅ / ❌
- a `main()` that runs the checks, prints a summary, and **returns the
  failure count** (not a bool, not None)
- `if __name__ == '__main__': raise SystemExit(main())`
- a header comment ending in the standalone usage line

## Register it or pytest will not see it

`pyproject.toml` sets `python_files = ["test_offline_suites.py"]` —
pytest collects **only** the bridge file. A new suite must be added to
its `SUITES` list or it will pass silently by never running.

## Offline means offline

Suites run with the LLM stubbed, the image API stubbed, and the dedicated
test database (`DB_NAME_TEST`, built by `harness.py`). No network, no
local model, no image service. A test that needs a running game does not
belong here.

Two suites need no database at all — `test_event_parity.py` and
`test_step_contract.py` read source files and compare sets. When adding
that kind of tripwire, give it a scanner guard (a floor on how much it
expects to find) so a refactor makes it fail loudly instead of passing
vacuously on zero matches.

## Verification

```bash
PYTHONIOENCODING=utf-8 ./venv/Scripts/python.exe -m backend.tests.<suite>   # one suite
PYTHONIOENCODING=utf-8 ./venv/Scripts/python.exe -m pytest                  # all of them
```

MySQL must be running for any suite that touches the database.
