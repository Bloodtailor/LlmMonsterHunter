# Monster Memory & Evolution — Implementation Plan

**Status:** IMPLEMENTED (July 2026, branch `feature/monster-memory-evolution`,
Mem-M1…Mem-M7). Offline/stubbed test suites green; pending the user's live
soak with the LLM loaded (two full runs + one returning encounter per
disposition; watch the AI log for parse-retry rates on the new templates —
`camp_restore`, `returning_transform`, `growth_reflection`, `camp_spotlight`,
`defeat_reflection` — and tune wording/max_tokens if the local 7B struggles).
**Commit prefix:** `Mem-M#`

**Deviations from the original plan (all deliberate):**
- Enemy action costs ride the shared referee call (`enemy_turn` output
  unchanged — one cost path for both sides).
- Defeat reflection is ONE collective call, not per-monster (defeat must
  not stall on a local model).
- Camp/exit reflections return in workflow results instead of streaming
  (avoids per-monster generation-id plumbing).
- No `dungeon.resources_updated` SSE event — resources ride workflow
  results like `party_conditions`, and battle pools ride snapshots.
- Blend-ins are NOT transformed; only dedicated returning events are.

The world remembers the player's choices. Monsters keep permanent memories of
what the party did to them, come back changed in later runs, grow from what
they actually did and wished during a run, and spend stamina/mana reserves
that refill only when the party enters the dungeon.

## 1. Goal and locked decisions

1. **Monster memory** — every encountered monster permanently remembers what
   happened (defeated + *how/by whom*, joined, yielded, fled, spared,
   let-pass, rewarded, talked, avoided). Pure code writes memories; no new
   LLM calls during battles.
2. **Returning monsters** — remembered monsters that are NOT currently
   following the player can reappear:
   - Dedicated `returning_monster` path event (weight 0.12, only when the
     eligible pool is nonempty; degrades invisibly to `location_explore`).
     The monster is TRANSFORMED before the encounter (code-clamped stat
     boost, optional "answer" ability countering how it was beaten, reworded
     battle line, grudge/bond note) and its disposition routes the encounter:
     hostile → battle, friendly → dialogue, wary → explore standoff.
   - Blend-in: 25% of normal monster encounters swap ONE freshly-generated
     slot for a remembered monster (unchanged, memories ride prompt context).
3. **Growth from behavior** — a code-written per-monster run journal feeds
   reflections: at CAMP the LLM spotlights 1–2 party monsters to grow; at
   SAFE EXIT every party monster reflects; on DEFEAT one collective "lesson"
   reflection. Growth = clamped stat bump + optional justified new ability +
   optional ability description REWORDING (similar length, never longer) +
   a permanent memory.
4. **Stamina + mana** — 5-step word ladders per monster, BOTH sides, mirroring
   the condition ladder. The battle referee's existing JSON gains optional
   cost words; Python steps the ladders with code defaults on silence.
   Explicit costs/restores stated in ability descriptions are honored.
   Pools reset ONLY on dungeon entry; camp restores; defend restores minor.

Out of scope V1: card-art regeneration on return, evolution paths, XP/levels.

LLM discipline (7B/4096 ctx): flat JSON, word enums, optional fields with
code fallbacks, numbers always code-clamped, battle-turn call count UNCHANGED.

## 2. Data model (new tables only — NO new columns, NO DB reset)

- `backend/models/dungeon_run.py` — `dungeon_runs`: run_number, ended_at,
  result (NULL=active | victory_exit | defeat | abandoned), summary.
  `begin()` closes dangling actives as abandoned.
- `backend/models/monster_memory.py` — `monster_memories`: monster_id (FK),
  run_id (FK nullable), kind, content (prompt-ready past tense), details
  (JSON: by/with/run_number/stat/amount_pct/battle_summary…).
- Registered in `models/core.py:create_tables()` + `tests/reset_db.py`.
- Dungeon state (GlobalVariable JSON) gains: `party_resources`, `run_journal`,
  `run_id`, `seen_monster_ids`.
- Battle state entries gain `stamina`/`mana` words + `finishing_blows`.
- `persona['grudges_and_bonds']` (existing JSON column) — appended by
  transforms/growth, capped at 4 entries.

Memory kinds: `was_defeated, defeated_party, joined_party, yielded_to_party,
fled_from_party, spared_party, let_party_pass, gave_reward, punished_party,
talked_with_party, avoided, camp, growth, lesson, returned, run_complete`.

## 3. New modules

- `backend/game/memory/manager.py` — write_memory (never raises, stamps run
  number, emits `monster.memory_added`), memory→prompt blocks
  (`monster_memories` flexible share 0.06), eligibility pool, mark_seen.
- `backend/game/memory/journal.py` — per-monster run journal (30 lines × 160
  chars, dedupe-adjacent), `run_journal` flexible share 0.06.
- `backend/game/memory/returning.py` (M4) — pick/transform/reveal returning
  monsters. Boost tiers slight/notable/fierce = 3/6/10% × return-count
  multiplier (cap 1.5×), lifetime return-boost cap 50% per stat.
- `backend/game/memory/growth.py` (M5) — reflect/apply growth. Tiers
  slight/notable = 2/5%, lifetime growth cap 30% per stat, max 6 abilities,
  reword length ≤ 1.15× original.
- `backend/core/events/dungeon_events.py` — `dungeon.monster_revealed`
  (existing monsters staged into encounters; `monster.created` only fires
  for new ones).

## 4. Resource rules (M2)

- `RESOURCE_LADDER = brimming → steady → strained → drained → spent`
- `RESOURCE_DELTAS = none 0, minor 1, moderate 2, heavy 3, restore_minor -1,
  restore_major -2` (positive deltas = costs → hit the ACTOR; negative =
  restores → hit the TARGET, so defend rests self and support items rest allies)
- Code defaults when the referee stays silent: attack → stamina minor;
  ability → `ABILITY_POOL_BY_TYPE[ability_type]` moderate; defend → stamina
  restore_minor; item/talk → none.
- Enemy pools seed `brimming` at battle start; ally pools ride dungeon state
  and battle snapshots (frontend needs no new battle events).
- `enemy_turn` prompt: guidance only ("drained/spent monsters should defend,
  talk, or flee") — enemy costs ride the shared referee call.

## 5. Prompt templates (all in `backend/ai/llm/prompts/memory_generation.json`
unless noted)

| Template | Parser | Purpose |
|---|---|---|
| `action_resolution` / `freeform_action_resolution` (battle_generation.json) | basic, required unchanged | + optional `stamina_cost`/`mana_cost` words |
| `dungeon_ability_use` (exploration_generation.json) | basic, required unchanged | same cost fields out of battle |
| `camp_restore` | basic, required `restores` | per-monster restore words at camp |
| `returning_transform` | basic, required `disposition`,`greeting` | how a remembered monster comes back |
| `reunion_scene` | none (streamed) | the moment the party recognizes it |
| `camp_spotlight` | basic, required `spotlight` | who grows at this camp |
| `growth_reflection` | basic, required `reflection` | stat/ability/reword decisions |
| `defeat_reflection` | basic, required `reflection` | collective lesson on defeat |

## 6. Critical ordering constraints

- **Defeat wipes state in the same battle_turn** (`end_battle()` +
  `exit_dungeon()`): defeat memories, the defeat reflection, and the run-row
  close all run BEFORE that block.
- Victory-exit ceremony runs in `choose_path`'s exit branch BETWEEN
  `generate_exit_text` and `manager.exit_dungeon()`.
- Returning-path eligibility is re-checked at dispatch (the pool can shrink
  between path generation and choice).
- `setup_camp` marks `camped=True` BEFORE growth calls: a failed reflection
  can never enable double-camping (that camp's growth is simply lost).

## 7. Milestones

- **Mem-M1** Foundation: tables, run lifecycle, journal, memory manager,
  context shares, events, this doc.
- **Mem-M2** Resources: ladders, referee cost fields, dungeon ability costs,
  camp restore.
- **Mem-M3** Memory writing: finishing blows, battle-end + dialogue + sneak
  memories, journal appends, memory context injection.
- **Mem-M4** Returning monsters: event + blend-in + transform + reunion.
- **Mem-M5** Growth: camp spotlight, exit ceremony, defeat lesson,
  generate_ability growth_context.
- **Mem-M6** Frontend: resource pips, memories on the card, reunion banner,
  growth display, party liveness.
- **Mem-M7** Docs (docs/api refs (formerly notes_for_claude)), test consolidation, soak.

## 8. Verification

- Offline: `python -m backend.tests.test_monster_templates` (render gate for
  every touched template); `test_memory_foundation` / `test_resources` /
  `test_growth` pure-logic checks.
- Live: full runs exercising enter → battle → sneak → camp → exit → re-enter →
  returning encounter (each disposition) → defeat run; watch the dev AI log
  for parse-retry rates on new templates; X-ray debug panel shows journals,
  pools, and hidden paths.
- No DB reset needed: only new tables, auto-created at startup.

## 9. Risks and flagged decisions

- Dialogue memory tone is derived from the outcome kind (no LLM tone call) —
  keeps the call budget flat; revisit if warm/sour reads feel wrong.
- Defeat reflection is one collective call, not per-monster (defeat should
  not stall on a local model).
- Camp reflections return in the workflow result instead of streaming
  (avoids per-monster generation-id plumbing; exit ceremony same).
- Blend-ins are NOT transformed (only dedicated returns are) — avoided
  monsters resurface as they were, which is the point.
