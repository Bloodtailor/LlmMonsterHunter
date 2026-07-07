# Game Loop v1 — Plan

**Status:** IMPLEMENTED (July 2026) — all seven milestones landed;
pending live soak (full first run, a themed run with a goal completed
and one failed, a defeat losing provisional spoils, a wary recruit
acting on its own then earning trust).
**Branch:** `feature/game-loop-v1` — one milestone commit per milestone, prefix `Loop-M#`.

The July 2026 architecture review put it plainly: every verb exists —
explore, battle, talk, recruit, camp, chat, evolve — but there is no game
shell around them. Game Loop v1 is the smallest set of additions that
makes a complete, replayable arc: **title screen → guided first run →
runs with goals and stakes → a home base worth returning to.**

## Locked decisions (design review, July 2026)

1. **Single-world model** — no save profiles. New Game starts the guided
   opening against the existing database; Continue goes to home base.
2. **One goal per run** — no side-goals in v1.
3. **Affinity ladder** `wary → familiar → trusting → devoted`, stored on
   the monster. **Wary monsters act on their own in battle**: their turn
   auto-resolves like an enemy turn (LLM picks attack/ability/defend,
   personality-true) and the player watches. Devoted monsters get a
   friendlier referee note; affinity also rides chat and evolution
   context. This answers the design doc's disobedience question: yes —
   but as autonomy with personality, not command-refusal frustration.
4. **Recruits start at `wary`** — trust is earned through camps, heals,
   reunions, chats, and surviving runs together. Existing followers
   backfill to `trusting` so no current companion turns disobedient.
5. **Location descriptions describe the location itself** — structures,
   light, sound, history — never the party arriving. (Arrival narration
   is `look_around`'s job.) **Battle turn vanity is ONE sentence**: what
   the monster is thinking at this exact moment.
6. **Run modifiers live in one place:** a `run_context` dict (theme,
   danger, goal, first_run) inside the existing `dungeon_state` global
   variable, with a single `expedition_brief()` context block that every
   dungeon prompt receives. No scattered per-feature globals.
7. **Schema:** one nullable column (`monsters.affinity`) added by an
   idempotent dev script — no DB wipe (sanctuary monsters carry memories
   and evolutions now). `reset_db.py` remains for full resets.
8. **Out of scope:** sound/music, new animations, save profiles,
   shops/economy, multi-dungeon world map, trap events.

## Milestones

### M1 — Prompt fixes — IMPLEMENTED
`random_location` + `arrival_location` prompts and the generator
fallbacks describe the location itself (no party, no arrival);
`turn_vanity` becomes one present-moment sentence (`max_tokens` 300→100).

### M2 — Expedition notices: themes + danger — IMPLEMENTED
New `game/dungeon/run_context.py`: run_context read/write helpers,
`expedition_brief()`, and `DANGER_PROFILES` (`calm/risky/perilous` →
enemy count range, battle event weight, explore-monster chance,
returning weight, referee hint line). `generate_expedition_notices`
workflow (LLM writes 2-3 themed notices; **Python rolls each notice's
danger word**); `enter_dungeon` accepts a validated `notice_id`; theme
threads into entry/location/path/encounter prompts via
`{expedition_brief}`. Entrance screen gets the notice picker. Danger
table added to `docs/tuning.md`.

### M3 — Run goals — IMPLEMENTED
One themed goal generated at entry, riding in `expedition_brief()`.
After each resolved path event and each in-dungeon battle victory, a
`goal_check` referee call answers `no / progress / complete`; Python
ignores `complete` before `GOAL_MIN_EVENTS` (default 3). Completing the
goal earns an exit ceremony: one rare themed item + a `notable` growth
tier for the party. Defeat forfeits the reward.

### M4 — Stakes: provisional spoils — IMPLEMENTED
Dungeon state tracks `run_recruits`, run items, and run CoCaToks at
their sources (battle joins, dialogue joins, reunion joins, treasure,
rewards, victory keepsakes). Defeat and abandonment release the
provisional recruits (each gets a parting memory — the memories REMAIN)
and delete the run's items. Victory exit keeps everything.

### M5 — Affinity v1 — IMPLEMENTED
`Monster.affinity` column + `backend/tests/add_affinity_column.py`
(idempotent ALTER; backfills followers to `trusting`). New
`game/monster/affinity.py`: ladder, `step_affinity` (+1, capped, writes
a memory, emits `monster.affinity_changed`), `is_autonomous`, context
line, step-event knobs (first ally heal per run, camp rest, reunion,
run exit together, memory-extracting chat, evolution — capped by
`MAX_AFFINITY_STEPS_PER_RUN`). New `game/battle/turn/autonomy.py`: wary
allies auto-resolve via a new `ally_autonomous_turn` prompt; turn
payloads gain `autonomous: true`. Devoted/wary lines enter ally battle
blocks and the referee prompts; affinity rides chat + evolution context.
Affinity badge in the frontend; tuning table; `test_affinity.py`.

### M6 — Title screen + guided first run — IMPLEMENTED
`first_run_complete` global; TitleScreen (New Game / Continue) as the
app's opening screen. New Game → `begin_first_run` workflow streams the
wish-granting-power opening scene, then enters a `calm` fixed-theme
dungeon with a scripted event sequence: a winnable `monster_dialogue`
(the first monster is RECRUITED, not generated), one `monster_battle`
with the new companion (wary → it fights on its own terms), then a
forced exit path. Empty-party entry is allowed only for the first run;
the recruit auto-joins the active party; the fixed goal ("leave with a
new companion") completes on recruitment.

### M7 — Post-run chronicle — IMPLEMENTED
After every run end (victory or defeat): a streamed chronicle scene —
the run's log condensed into a story beat with the goal outcome, growth,
monsters met/recruited/lost, and the run number. Inputs are captured
before the state wipes; the final text persists to `DungeonRun.summary`.

## Verification

Offline suites (LLM stubbed, test DB): affinity ladder math + autonomy,
goal bookkeeping + valve, defeat-path spoils enforcement, first-run flag
flow + scripted sequence, notice validation + danger profiles. Static:
ruff, file-size ceiling, prettier, jest. Live soak after merge: full
first run start to finish; a themed run with a goal completed and one
failed; a defeat losing a provisional recruit and treasure; a wary
recruit acting on its own, then earning `familiar` and taking commands.

## Deviations

- **M2:** `run_context` lives in its own GlobalVariable key rather than
  inside `dungeon_state` — the theme must exist before the dungeon state
  row is created (the starting location is themed), and `start_dungeon`
  wholly replaces the state dict. Lifecycle stays single-pointed:
  `begin_run_context()` in enter, `clear_run_context()` inside
  `manager.exit_dungeon()`.
- **M2 (file-size ceiling):** threading the brief pushed two files over
  their limits, so two concepts moved out: dungeon fallbacks →
  `game/dungeon/fallbacks.py`, and the developer X-ray →
  `services/dungeon_debug_service.py`. The entrance auto-enter effect
  (replaced by the notice board) was deleted.
- **M4:** CoCaToks were documented as "permanent — deliberately no delete
  path" (models/cocatok.py). Stakes overrules that for keepsakes minted
  MID-RUN: they are provisional spoils like everything else the run
  gathered and are taken back on defeat/abandonment (new
  `inventory.cocatok_removed` event). Keepsakes carried out alive remain
  permanent; the model comment was updated in the same commit.
- **M5 (file-size ceiling):** battle/generator.py crossed 500, so the
  state-to-text builders moved to `game/battle/context_blocks.py` (pure
  composition; generator keeps the LLM calls). The evolution ceremony's
  affinity step lives in the workflow orchestrator, not evolution.py
  (grandfathered file may only shrink). The test harness now REBUILDS the
  disposable test DB when its schema drifts behind the models
  (`_SCHEMA_MARKERS` in tests/harness.py) — create_all never ALTERs.
