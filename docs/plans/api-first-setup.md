# API-First Setup — Onboarding for Non-Technical Players — Plan

**Status:** IN PROGRESS (July 2026) — approved by Aaron; M1 implemented.
**Branch:** `feature/api-first-setup` — one milestone commit per milestone, prefix `Stp-M#`.

The setup system was built for the local-model era: it assumes the player
must conquer CUDA, Visual Studio Build Tools, and a GGUF download, and it
assumes they already have Python, Node, and MySQL installed. The
cloud-generation initiative flipped the game to API-first (DeepSeek text +
Gemini art, keys pasted in-game), but setup only got a partial retrofit:
the local chain moved behind one opt-in question, and everything else
stayed a terminal-heavy, jargon-dense walkthrough.

This initiative redesigns onboarding around a new target user: **someone
who has never opened a terminal.** The goal is one double-click from a
fresh Windows machine to the game running in a browser, with the only
manual step being "paste your API key into the gear-icon Settings."

## What's wrong today (setup review, July 2026)

1. **`check_requirements` still gates on all 8 components.** On a fresh
   API-first machine the GPU/CUDA/VS/model/llama checks all fail, so the
   launcher reports "Many requirements missing — Game likely won't work"
   even when everything the game actually needs is green. Actively
   misleading right now.
2. **Setup requires Python before it can help you install Python.**
   `start_game.bat` line 1 is `python -m setup...` — on a machine without
   Python it dies with `'python' is not recognized` (or worse, the
   Microsoft Store alias hijacks the command). The first thing a
   non-technical user sees is the exact failure setup exists to prevent.
3. **MySQL is the boss fight.** Manual MSI download, an installer wizard
   full of choices ("Developer Default or Server only?"), a root password
   they must invent and write down, Windows services. The current guidance
   is thorough but it's a wall of terminal text describing a process with
   a dozen failure modes.
4. **Node.js is a manual install** (link + wizard + restart-your-terminal),
   though `winget` can do it in one elevated click.
5. **The local-extras question still interrupts everyone.** To answer it
   you must read a paragraph about CUDA, GGUF, and 1M-token context
   windows — precisely the vocabulary the API-first edition was supposed
   to retire from the default path.
6. **`requirements.txt` still aggregates `llm.txt`**, so anyone following
   generic Python instructions gets a CPU-only llama-cpp-python build (or
   a failed source build) they never needed.
7. **The walkthrough's tone is developer-facing:** diagnostic tables,
   venv/PATH/pip jargon, ~dozen Y/n prompts on the happy path, and
   `user_messages.py` is ~70% GPU/CUDA/VS/model troubleshooting that no
   longer applies to the supported path.
8. **The finish line doesn't point at the keys.** Setup ends with a
   requirements recheck, not "the game will open — click the gear icon and
   paste your DeepSeek key," which is the one action the player must take.

## Proposed decisions (to lock at review)

1. **The target user has never used a terminal.** Every message in the
   default path is written for them: plain English, no jargon, no
   diagnostic tables, no vanishing windows. Developers get the detail via
   flags, not by default.
2. **One entry point: double-click `start_game.bat`.** It bootstraps
   everything (including Python itself), then starts the game. No
   separate "run setup first" step — the launcher runs whatever setup is
   missing, every time, silently when there's nothing to do.
3. **Happy path asks zero questions.** Setup auto-fixes everything it
   can; it stops only for things it genuinely cannot do (UAC consent
   clicks, an unfixable environment) and then says exactly one thing:
   what happened, what to do, and that it's safe to re-run.
4. **`winget` is the install mechanism** for Python and Node (it ships
   with Windows 10/11 App Installer), with a fallback that opens the
   official download page and gives copy-paste-free instructions. The
   `.bat` files are Windows-only already, so leaning on winget adds no
   new platform assumption.
5. **MySQL stays a guided install** (LOCKED — Aaron, July 2026, chose
   this over a bundled portable server and over a SQLite migration).
   The player still runs the official installer, but the guidance is
   redesigned for a first-timer: one short instruction card naming only
   the choices that matter, setup waits and verifies right after, and
   everything that can be automated around the install (service start,
   password capture into `.env`, database creation) already is.
   *Alternatives considered:* a bundled portable MySQL (auto-download,
   zero wizard) and a SQLite migration — both noted in Future work if
   the guided path proves to be where new players give up.
6. **Local-LLM extras leave the default path entirely.** No question in
   the walkthrough; `python -m setup.setup_environment --local-extras`
   (developer-facing, documented in README's developer section) is the
   only way in. `requirements.txt` becomes base-only; `requirements/llm.txt`
   is installed only by that flow.
7. **Setup ends by pointing at the gear icon.** The final message (and
   the README) makes "paste your DeepSeek key in ⚙ Settings" the
   celebrated last step, with the cost ballpark stated plainly.
8. **Distribution is Download-ZIP, not git clone.** The README Quick
   Start assumes the green-button ZIP; git stays in the developer
   section.

## Milestones

### M1 — API-first gates and defaults — IMPLEMENTED

The correctness fixes, independent of any new machinery:

- Split the component registries into `REQUIRED_COMPONENTS` (Basic
  Backend, Node.js & npm, MySQL Server, Database Connection) and the
  existing `LOCAL_EXTRA_COMPONENTS`. `check_requirements` (and therefore
  `start_game.bat`) passes/fails on required components only; local
  extras appear only under `--local-extras`.
- Remove the local-extras question from the default interactive flow;
  wire the `--local-extras` flag through `setup_environment.py`.
- `requirements.txt` → base only (llm.txt referenced by comment, installed
  by the local-extras flow which already uses the CUDA wheel index).
- `.env` auto-creation generates a real `SECRET_KEY`
  (`secrets.token_hex`) instead of shipping the placeholder; LLM keys in
  `.env.example` are annotated as local-escape-hatch-only.
- Suites: new offline suite `backend/tests/test_setup_registry.py` — the
  "fresh API-first machine" scenario (local extras all failing) must
  report READY, and the registries/aggregator/.env-secret behavior are
  pinned.

*Deviations:* (1) The registry became a new `setup/components.py`
(single source of truth; required-ness is a property of the component
definition) rather than a tuple split inside the flows package.
(2) Found and fixed en route: `auto_setup_basic_backend` treated a bare
`venv/` FOLDER as a working venv, so an empty stub (fresh ZIP download,
half-deleted venv) wedged setup with "pip not found" — venv validity is
now judged by the interpreter inside it. (3) `setup_environment auto`
now exits nonzero on failure (the launcher gates on that exit code; it
previously always exited 0).

### M2 — Double-click bootstrap (before Python exists)

Rewrite `start_game.bat` so the machine that has nothing still gets a
friendly experience:

- Detect real Python: try `py -3`, then `python`, and treat the
  WindowsApps Store alias (exit code/output sniff) as "not installed."
- If missing: explain in one sentence, then offer to install via
  `winget install Python.Python.3.12` (per-user, no admin). If winget is
  missing or declined, open python.org in the browser with the two
  instructions that matter ("check *Add python.exe to PATH*", "then
  double-click start_game.bat again").
- Same treatment for Node LTS (`winget install OpenJS.NodeJS.LTS`; one
  UAC "Yes" click — the message says the popup is expected).
- Every failure path ends with `pause` and a plain-language message —
  no window ever flashes and vanishes.
- `start_backend.bat` / `start_frontend.bat` get the same detection.

### M3 — Guided MySQL, redesigned for a first-timer

The install stays manual (locked decision 5); everything around it gets
easier:

- Detection first, and broader: a working MySQL (server reachable, or a
  stopped service we can start) is used with no questions — the existing
  auto-service-start stays and runs before any instructions appear.
- The instruction card shrinks to the choices that actually matter, in
  plain English: which download button to click ("MySQL Community
  Server" MSI), "Server only" in the wizard, keep port 3306, "make up a
  password and keep it handy — the setup will ask for it in a minute."
  Everything else in the wizard: "accept what it suggests."
- The browser opens on the download page automatically instead of
  printing a URL to retype.
- Setup **waits at the card** ("press Enter when the installer says
  finished") and immediately verifies: service up → password prompt →
  connection test → database created — one continuous flow instead of
  "re-run the launcher and hope."
- The password prompt is reframed for the target user ("the password you
  just made up during the MySQL install"), stores to `.env` as today,
  and on a wrong password says so plainly and re-asks (that loop already
  exists — it gets the wording pass).
- Common failure modes (service didn't start, port occupied) get the
  short human version first, with the existing deep troubleshooting text
  demoted to "if that didn't work" detail.

### M4 — The zero-question walkthrough

Rework the interactive layer around auto-fix-first:

- Replace the per-component Q&A ("Do you want to set up X now? [Y/n]")
  with a linear narrated pass: "Step 2 of 5 — Getting the database
  ready…" that fixes silently and only surfaces unfixable problems.
- Rewrite every default-path message in `user_messages.py` for the
  non-technical reader; GPU/CUDA/VS/model messages move to the
  local-extras-only path (nothing deleted, just relocated).
- Final screen: "All set! The game will open in your browser. Click the
  ⚙ gear icon and paste your DeepSeek key (get one at
  platform.deepseek.com). Card art is optional — add a Gemini key
  whenever you like."
- Keep `--dry-run` working for every reworked flow.

### M5 — Docs for humans

- README Quick Start rewritten as three steps: **Download ZIP →
  double-click `start_game.bat` → paste your key in ⚙ Settings**, with
  the cost ballpark and "no GPU needed" kept prominent. Developer
  instructions (git, venv, suites, `--local-extras`) move to the
  developer section.
- `LLM-Monster-Hunter-For-Friends/04-try-it-yourself.md` updated to
  match (prerequisites section shrinks to "a Windows PC and a DeepSeek
  key").
- `docs/architecture.md` / CLAUDE.md command sections checked for
  contradictions and fixed in the same commit (per the docs rule).

## Risks / open questions

- **winget availability:** ancient Windows 10 builds lack App Installer.
  Mitigation: browser-link fallback path is fully written out, not an
  afterthought.
- **MySQL remains the likeliest drop-off point:** even redesigned, a
  first-timer must complete a third-party installer wizard and invent a
  password. If real-world onboarding stalls here, the fallbacks are in
  Future work.
- **The MySQL download page changes layout** over time; the instruction
  card should describe the target ("MySQL Community Server", the MSI)
  rather than pixel-level steps.

## Future work (explicitly out of scope)

- **Bundled portable MySQL** — auto-download the official ZIP,
  initialize with a generated password inside the project folder, no
  wizard. Considered and deferred (Aaron, July 2026) in favor of the
  guided install.
- **SQLite migration** — would remove the MySQL requirement entirely;
  the connection string is centralized in `backend/app.py`, but the test
  harness and migration scripts speak PyMySQL directly. Its own
  initiative if the guided install proves to be where new players give
  up.
- macOS/Linux launcher scripts.
- Packaged one-file installer (PyInstaller/Electron-style) — the ZIP +
  bat bootstrap gets 90% of the value at 5% of the maintenance.
