# Codebase Health — consolidation pass (Hth)

**Status: PLANNED** (not started)
**Branch:** `feature/codebase-health` · **Commit prefix:** `Hth-M#`
**Written:** 2026-07-07, from a full-repo review. Intended to be executable
by an AI assistant working autonomously — every task names its files, its
split seams, and its verification commands.

---

## Verdict from the review (read this first)

The architecture is in good shape. The layering documented in
`docs/architecture.md` (routes → services → game logic → `ai/gateway.py`)
is real in the code, one-file-per-domain holds in `routes/` and
`services/`, the workflow/SSE model is consistent, and `shared/ui` is a
genuine component library with per-component folders and barrel exports.
**This plan is a tidiness pass, not a redesign.** Nothing here changes
behavior, prompts, or the API surface.

The debt is concentrated and enumerable: the **15-entry grandfather list**
in `tools/check_file_sizes.py` (files predating the 500-line ceiling),
plus a few misplaced/duplicated dev surfaces on the frontend. The goal of
this initiative is simple: **empty the grandfather list and put every dev
surface in one obvious place.**

### Guardrails — do NOT touch these while executing

- **The step-name contract.** Frontend event hooks key off workflow
  `on_update` step strings. No renaming of step strings, workflow names,
  or event names.
- **Prompts.** No prompt text changes; this is a structure-only pass.
- **`ai/gateway.py`** stays the single generation entry point.
- **Public import behavior**: when splitting a module, update every
  call site to the new module paths (grep to find them all). Do not leave
  half-migrated imports; a thin re-export module is acceptable ONLY where
  the plan below says so.
- The grandfather list in `tools/check_file_sizes.py` may only shrink.
  Every milestone below deletes entries from it; never raise a ceiling.

### Verification commands (run after every milestone)

```bash
./venv/Scripts/python.exe -m pytest                              # all offline suites (MySQL must be running)
./venv/Scripts/python.exe -m ruff check backend setup tools
./venv/Scripts/python.exe tools/check_file_sizes.py              # must pass AND the grandfather list must have shrunk
cd frontend && npm test -- --watchAll=false && npx prettier --check src
```

Milestones Hth-M3+ change frontend rendering paths — also boot the game
(`start_game.bat` or backend `run.py` + `npm start`) and click through the
Developer screen sub-nav to confirm every dev screen still renders.

---

## Current grandfather list (the debt inventory)

From `tools/check_file_sizes.py` (line count when grandfathered):

| File | Lines | Handled in |
|---|---|---|
| `backend/game/dungeon/generator.py` | 685 | M1 |
| `backend/game/monster/evolution.py` | 556 | M1 |
| `backend/tests/test_chat_and_summaries.py` | 548 | M1 |
| `backend/tests/test_evolution.py` | 522 | M1 |
| `setup/user_messages.py` | 1092 | M2 |
| `frontend/src/screens/developer/BYOComponentTestScreen.js` | 1133 | M4 |
| `frontend/src/screens/developer/ExplosionDemo.js` | 801 | M3 |
| `frontend/src/screens/developer/StyleTestScreen.js` | 545 | M4 |
| `frontend/src/components/UiExamples/TableExample.js` | 808 | M4 |
| `frontend/src/components/UiExamples/ExplosionExamples.js` | 682 | M3 |
| `frontend/src/components/UiExamples/ButtonExample.js` | 663 | M4 |
| `frontend/src/components/UiExamples/CardExamples.js` | 603 | M4 |
| `frontend/src/components/UiExamples/ExpandableTableExample.js` | 592 | M4 |
| `frontend/src/components/UiExamples/PaginationExample.js` | 563 | M4 |
| `frontend/src/components/UiExamples/FeedbackExamples.js` | 536 | M4 |

End state after M4: the list is empty and the `GRANDFATHERED` dict in
`tools/check_file_sizes.py` can be deleted down to `{}` (keep the
mechanism — new debt should still be impossible to add).

---

## Hth-M1 — Backend splits (4 grandfather entries removed)

### 1a. Split `backend/game/dungeon/generator.py` (~685 lines)

The file already has clean section markers that ARE the split seams:

- `# ===== CONTEXT BUILDERS =====` (top) — `build_monster_dungeon_details`,
  `build_monsters_details`, `build_speaking_monsters_details`,
  `build_party_dungeon_details`, `_dungeon_log_text`
- Core location/path generation — `generate_entry_text`,
  `generate_random_location`, `generate_location_event_text`,
  `generate_exit_text`, `generate_paths`, `generate_arrival_location`,
  `generate_encounter_vanity_text`, and `build_door_choices` (currently
  at the bottom of the file; it belongs with paths)
- `# ===== EXPLORE EVENT GENERATION =====` — `generate_look_around_text`,
  `generate_camp_scene`, `generate_reunion_scene`, `generate_camp_restore`,
  `judge_sneak_attempt`, `generate_ambush_intro`,
  `resolve_dungeon_ability`, `resolve_dungeon_item`
- `# ===== DIALOGUE ENCOUNTER GENERATION =====` —
  `generate_monster_question`, `generate_dialogue_turn`

**Do:** create a `backend/game/dungeon/generation/` package:

```
backend/game/dungeon/generation/
  __init__.py        # re-exports everything (see note)
  context.py         # the context builders
  locations.py       # entry/exit/paths/arrival/vanity + build_door_choices
  explore.py         # explore-event generation + sneak/ambush/ability/item
  dialogue.py        # riddle/dialogue encounter generation
```

The dungeon handlers (`backend/game/dungeon/handlers/`) import from
`generator.py` in many places — here the re-export `__init__.py` is the
right call (one import surface, many consumers). Delete the old
`generator.py`, grep for `dungeon.generator` and `from .generator` /
`from ..generator` and repoint every import to
`backend.game.dungeon.generation`. Keep each new file's WHY-comment
header explaining what its slice of generation covers.

### 1b. Split `backend/game/monster/evolution.py` (~556 lines)

The file is a staged pipeline with marked sections: CODE-OWNED MECHANICS,
STAGE 1 FORM DESIGN, STAGE 2 STREAMED NARRATION, STAGE 3 PERSONA SHIFT,
STAGE 4 PROSE + APPEARANCE, STAGE 5 ABILITY EVOLUTION, FINALE. It only
needs to lose ~60 lines, so make the **smallest coherent split**: move
the `# ===== CODE-OWNED MECHANICS =====` block (`next_stage_number`,
`boost_pct_for_stage`, `next_rarity`, `keep_name_root`, `clean_guidance`,
`build_transformation_facts`) into a sibling
`backend/game/monster/evolution_mechanics.py` and import it. That file
name also advertises the referee philosophy (code owns numbers). Do NOT
shatter the pipeline stages across files — reading the ceremony top to
bottom in one file is a feature.

### 1c. Split the two oversized test suites

Both follow the repo's suite pattern (`check(...)` assertions,
`main() -> failure count`, discovered by pytest AND runnable via
`python -m backend.tests.<name>`; the in-app Developer screen lists
suites too — check `backend/services/game_tester_service.py` or wherever
the suite registry lives, and update it if suites are enumerated there).

- `test_chat_and_summaries.py` (~548) → `test_chat.py` +
  `test_summaries.py` (the name says the seam; split shared fixtures into
  whichever file uses them or into `harness.py` if both do)
- `test_evolution.py` (~522) → keep `test_evolution.py` for the pipeline
  stages, move altar/service/endpoint-level checks to
  `test_evolution_service.py` (pick the actual seam after reading it;
  the requirement is two coherent suites, each under 500, both green)

### 1d. Bookkeeping

Remove the four entries from `GRANDFATHERED`, update the directory map in
`docs/architecture.md` (it lists `game/ … dungeon/` contents only at
directory level, so likely only the tests section needs a touch), and run
the full verification block. One commit: `Hth-M1 …`.

---

## Hth-M2 — Split `setup/user_messages.py` (~1092 lines)

This is a prose catalog (every message the interactive setup prints),
not logic — which is why it grew unbounded. Read `setup/` first to see
how messages are consumed (likely imported constants/functions used by
`setup/checks / flows / installation`). Split it **by setup phase** to
mirror the package layout, e.g.:

```
setup/messages/
  __init__.py        # re-export so existing `from setup.user_messages import X` maps cleanly
  welcome.py         # intro/outro/branding text
  checks.py          # prerequisite-check messages
  installation.py    # install-step messages
  flows.py           # walkthrough/flow prose
```

Choose the actual file boundaries after reading the file — the rule is:
a contributor looking for "the message shown when MySQL is missing" finds
it by filename. Update imports across `setup/`, delete the old file,
remove the grandfather entry, verify (`ruff` + file-size check + actually
run `python setup/…` entry point far enough to see it boots — the setup
walkthrough's first screen appearing is sufficient proof; don't complete
an installation).

---

## Hth-M3 — One home for every dev surface (frontend)

Today dev/demo code lives in four places with two duplications:

- `screens/developer/` — the Developer hub + its sub-screens (correct home)
- `components/UiExamples/` — 12 example files consumed ONLY by
  `screens/developer/UiExamplesScreen.js`. They are living documentation
  for `shared/ui`, not feature components; `docs/architecture.md`
  describes `components/` as "feature components", which this contradicts.
- `components/debug/` — a single component (`DungeonContextPanel.js` +
  `debugPanel.css`), stranded alone.
- `components/developer/` — AiLogTable + GameTestRunner (fine, but see
  merge below).
- **Explosion is documented twice**: `screens/developer/ExplosionDemo.js`
  (~801 lines, an interactive playground) AND
  `components/UiExamples/ExplosionExamples.js` (~682 lines, gallery
  examples). ~1,500 lines of demo for one engine whose single production
  consumer is `components/evolution/EvolutionCeremonyPanel.js`.

**Do:**

1. Move `components/UiExamples/` → `screens/developer/uiExamples/`
   (folder casing per repo convention for non-component dirs — check how
   `screens/game/` names things and match). Update imports in
   `UiExamplesScreen.js`. `components/` is now feature-only.
2. Merge `components/debug/` into `components/developer/` (find
   `DungeonContextPanel`'s consumer via grep first — if its only consumer
   is a dev screen, it may belong under `screens/developer/` instead;
   put it where its consumer says it belongs).
3. Consolidate the two Explosion demo surfaces into ONE. Keep the
   interactive playground (`ExplosionDemo`) as the canonical home since
   it demonstrates more; fold anything `ExplosionExamples` shows that the
   playground doesn't into it as a "gallery" section, then delete
   `ExplosionExamples.js` and its entry in `UiExamplesScreen`. While
   doing this, split the survivor to get under 500 lines (engine controls
   panel vs preset gallery vs preview stage are the natural seams) —
   that removes BOTH Explosion grandfather entries in this milestone.
4. Update the directory map in `docs/architecture.md` and
   `shared/ui/ui.md` if it points at example file paths, in the same
   commit.
5. Verify: full command block, plus boot the app and click through every
   Developer sub-screen (the sub-nav lives in
   `screens/developer/DeveloperScreen.js`).

---

## Hth-M4 — Hold the example/demo files to the ceiling (empties the list)

The remaining grandfathered files are all `shared/ui` documentation
screens. Policy decision (locked): **examples are real code and obey the
same 500-line ceiling** — they're the first thing a contributor reads to
learn the library, so they should model the standards.

Mechanical pattern for each `*Example(s).js` file (post-M3 they live in
`screens/developer/uiExamples/`): they're big because one file demos many
variants/sections of a component. Split by variant into a subfolder,
keeping one entry file that composes the sections, e.g.:

```
uiExamples/table/
  TableExample.js          # composes the sections (small)
  BasicTableExamples.js
  TableStylingExamples.js  # actual seams = the section headers already in the file
  ...
```

Apply to: `TableExample` (808), `ButtonExample` (663), `CardExamples`
(603), `ExpandableTableExample` (592), `PaginationExample` (563),
`FeedbackExamples` (536). Read each file's section structure first and
split along its existing headings — do not invent new organization.

Then the two remaining dev screens:

- `BYOComponentTestScreen.js` (1133) — the "build your own component"
  playground. Natural seams: the prop-control panel definitions (large
  config data), the preview renderer, and the screen shell. Extract the
  per-component control configs into a sibling data module (or one per
  component family) and the control-panel UI into its own component.
- `StyleTestScreen.js` (545) — barely over; extract its largest section
  (likely the typography or color swatch blocks) into a sibling.

Finish by deleting the now-empty `GRANDFATHERED` entries (the dict should
be `{}`), and update the comment in `tools/check_file_sizes.py` to say
the list was retired but the mechanism stays. Update `README.md`'s
Development Status if it references this plan as in-progress. Full
verification block + click-through of the Developer screens.

---

## Hth-M5 (optional, judgment required) — `shared/ui` usage audit

Only do this after M1–M4 are merged. For each `shared/ui` component
family, grep for consumers outside `shared/`, `screens/developer/`, and
tests. Produce a short table in this doc (component → production
consumers). Then:

- **Single-consumer multi-file abstractions**: e.g. if
  `Pagination/` (8 files: primitive, presets, jumper, info, per-page
  selector, utils, hook) has one production consumer, collapse the
  unused presets/subcomponents. Same test for `FilterControls`,
  `ColorSelection`, `ToggleButton`.
- **Zero-consumer components**: propose deletion to Aaron in the PR
  description rather than deleting silently — some exist deliberately as
  library inventory for future screens.
- Keep `Explosion/` regardless (production consumer:
  EvolutionCeremonyPanel) — it's the ceremony's centerpiece.
- Update `shared/ui/ui.md` to match whatever survives.

This milestone is deliberately last because it deletes capability rather
than reorganizing it — smallest, most reviewable diff possible, and every
deletion listed in the commit message.

---

## Deviations log

*(none yet — log them here as they happen, per repo process)*
