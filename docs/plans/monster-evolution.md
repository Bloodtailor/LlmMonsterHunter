# Monster Evolution — Implementation Plan

**Status:** IMPLEMENTED (July 2026, branch `feature/monster-evolution`,
Evo-M1…Evo-M4). Offline suites green (59-check evolution suite + template
regression + growth/returning regressions); UI verified against the running
app (altar renders, run-state gate and lineage endpoint live). Pending the
user's live soak — checklist in §8.
**Commit prefix:** `Evo-M#`

**Deviations from the original plan (all deliberate):**
- `monster.evolved` SSE event registration moved from Evo-M2 into Evo-M1 —
  `apply_evolution_form` emits it at the moment of the transform (domain
  facts are emitted where they happen, matching the generator layer).
- No separate `EvolutionMonsterPicker` component — `MonsterChatPicker`
  gained optional `title`/`emptyTitle`/`emptyDescription` props and is
  reused by the altar (one following-roster picker, two screens).

Evolution is the big, earned leap — distinct from the small in-run growth
nudges. A FOLLOWING monster is transformed at home base: same monster id
(memories, chat thread, abilities, party status all survive), new form
designed by the LLM from the monster's lived history plus optional player
guidance. Gameplay costs/requirements come later; V1 is a free home-base
ceremony.

## 1. Goal and locked decisions (user-approved)

1. **Form driver** — the LLM designs the evolved form from the monster's
   memories, growth, and persona + an OPTIONAL player guidance whisper
   (≤200 chars). Blank guidance = pure history.
2. **Power** — code-owned boost to all four stats, OUTSIDE the growth caps
   (`'evolved'` memories are invisible to `growth_total_pct`); rarity climbs
   one tier per stage (`None`→common, capped at legendary); body comes out
   healed. Diminishing per stage: **25% → 15% → 10% flat**, unlimited stages.
3. **Identity** — species ALWAYS transforms; the personal name MAY evolve but
   must keep a recognizable root (first 4 chars of the old first name must
   appear in the proposal: Rokk → Rokkarath), else the old name stays. Old
   identity snapshotted in the lineage table.
4. **Ceremony** — dedicated home-base screen (Campfire Chat pattern):
   picker → guidance → streamed narration → live card flip → card-art regen
   reveal (cashes in the art-regen idea deferred by the memory plan).
   Gated while a dungeon run is active (same gate as chat).
5. **Preserved soul** — `core_wish`, `secret`, `grudges_and_bonds`, and
   `social_bonds` are never written by evolution. Curated taxonomy
   `domain`/`kingdom` and the derived `type_label` never move; the invented
   lineage below them (family/genus/species/race_label) may evolve.

Out of scope V1: gameplay integration (costs/requirements), art-regen retry
endpoint, evolving items/CoCaToks.

LLM discipline (7B/4096 ctx): five small flat-JSON templates with 1–2
required fields each, keep-old fallbacks per optional field, numbers always
code-clamped, only the FIRST call may abort the ceremony.

## 2. Data model (new table only — NO new columns, NO DB reset)

- `backend/models/monster_evolution.py` — `monster_evolutions`: monster_id
  (FK, index), stage, guidance, narrative, old_name/old_species/old_rarity,
  new_name/new_species/new_rarity, old_stats (JSON), applied_boost_pct,
  old_card_art_path (art files are never deleted — past forms stay viewable
  via the existing `/api/monsters/card-art/<path>` route), details (JSON:
  form_theme, size_class change, reworded abilities, new ability).
- Registered in `models/core.py:create_tables()` + `tests/reset_db.py`.
- Stage number = `count_for_monster + 1`. Invariant: a lineage row exists
  ⇔ the identity/stat/rarity transform happened.
- New memory kind `'evolved'` (exempt from the lifetime caps by design —
  `growth_total_pct` only sums `growth`/`returned`).

## 3. The ceremony chain (`backend/game/monster/evolution.py`)

| # | Step | Call | On failure |
|---|------|------|-----------|
| 1 | `run_form_design` | `evolution_form` (JSON) | **ABORT** — nothing mutated yet |
| 2 | `apply_evolution_form` | code only | raise if lineage row can't be written |
| 3 | `queue_evolution_narration` | `evolution_narration` (streamed prose) | keep going; narrative stays empty |
| 4 | `run/apply_persona_shift` | `evolution_persona` (JSON) | keep old inner life |
| 5 | `run/apply_prose` | `evolution_prose` (JSON) | keep old words AND skip art regen |
| 6 | `run/apply_ability_evolution` | `evolution_abilities` (JSON) | keep old abilities |
| 7 | signature ability (workflow) | existing `generate_ability` | skip |
| 8 | `finalize_evolution` | code only | never raises |
| 9 | art regen (workflow) | existing `generate_card_art` | keep old art, `art_regenerated: false` |

Form design runs FIRST so the streamed narration can name the evolved form.
Stage 2 emits `monster.updated` + `monster.evolved` (the ceremony trigger,
carrying the lineage record with the old art path). Stages 4/5/6 each emit
`monster.updated` when they change something.

Code-owned constants at the top of `evolution.py`: stage boosts, guidance cap
(200), name root chars (4), backstory addendum cap (800), reword cap (2) and
ratio (1.15, mirrors growth), battle-line ratio (1.3, mirrors returning).

## 4. Templates (`backend/ai/llm/prompts/evolution_generation.json`)

| Template | tokens/temp | required | notes |
|---|---|---|---|
| `evolution_form` | 300 / 0.8 | species, evolved_name | locked_lineage + stage_note + guidance |
| `evolution_narration` | 450 / 0.9 | (text) | ceremony text, saved as lineage narrative |
| `evolution_persona` | 350 / 0.8 | memory_note | battle_line/speech_style/goals/motivations optional |
| `evolution_prose` | 600 / 0.85 | description, visual_description | backstory ADDENDUM appended, appearance drives art |
| `evolution_abilities` | 400 / 0.8 | new_ability | ≤2 rewords (rename allowed), theme for signature |

Context per stage: `monster_details` = `build_speaker_block` (required,
never-truncated block), memories via the clamped `build_memory_block` share,
compact code-built `transformation_facts` (no numbers), `player_guidance`.

## 5. Workflow, routes, SSE (Evo-M2)

- `@register_workflow() evolve_monster(context, on_update)` in
  `game/monster/registered_workflows.py`; context `{monster_id, guidance?}`.
  Steps: `validate_context → designing_form → form_applied {monster,
  evolution} → emit_generation_id {evolution_text_generation_id} →
  await_narration → shifting_persona → rewriting_story → evolving_abilities
  → adding_signature_ability (conditional) → recording_memory →
  regenerating_art (guarded by `IMAGE_GENERATION_ENABLED` + prose success)`.
- `POST /api/monsters/<id>/evolve` `{guidance?}` → `{success, workflow_id}`;
  `GET /api/monsters/<id>/evolutions` → `{success, evolutions}` (oldest
  first). Service validates via `evolution_eligibility_error` (mirrors
  `chat_eligibility_error`: home base only, fully generated, following).
- SSE: `monster.evolved {monster, evolution}` + existing `monster.updated` /
  `monster.ability_added` / `monster.art_ready` / `monster.memory_added`.

## 6. Frontend (Evo-M3)

- `MonsterEvolutionScreen` ('monster-evolution' in `GameScreenRouter`,
  fourth Home Base button "Evolution Altar"): header + run-state banner
  (copied from `MonsterChatScreen`) + picker | ceremony panel grid.
- `components/evolution/`: `EvolutionMonsterPicker` (following list),
  `EvolutionCeremonyPanel` (idle: MonsterCard + guidance Textarea + Begin;
  ceremony: step checklist from workflow.update, streamed narration via
  `useStreamedGeneration('evolution_text_generation_id')`,
  `HueBasedExplosion` on `monsterEvolved`, art crossfade on
  `monsterArtReady`; complete: old→new strip from the before-snapshot +
  evolution payload, old art via the card-art route), `EvolutionLineage`
  (from `loadMonsterEvolutions`), `hooks/useMonsterEvolution` (state machine
  modeled on `useMonsterChat`; before-snapshot deep-copied at `begin()`).
- `PartyProvider` gains live patching for the FOLLOWING list on
  `monsterUpdated`/`monsterAbilityAdded`/`monsterArtReady` (also fixes the
  existing chat-picker staleness).

## 7. Tests

Offline (`python -m backend.tests.test_evolution`, dev MySQL, LLM stubbed):
stage boost math + rarity ladder + name-root rule; full form transform
(snapshot, taxonomy rules, size snap, heal, stage numbering); cap-exemption
regression (evolved memories move no growth totals; ordinary growth still
applies after); persona soul-field preservation (injected soul fields
ignored) + battle-line length rule; prose replace/append/800-cap/appearance;
ability reword clamps + rename + unknown-name; finale narrative + memory
shape; eligibility gates; form-failure abort leaves zero mutations.
`test_monster_templates` gains the five templates in `GENERATOR_VARIABLES`.

## 8. Live soak checklist (user, LLM loaded)

1. Evolve a stage-1 following monster with blank guidance — narration
   streams, card flips live, stats +25%, rarity climbs, art regenerates.
2. Evolve the same monster again WITH guidance — stage 2 = +15%, name root
   persists, lineage shows both rows with old-art thumbnails.
3. Chat with it afterwards — the `[a talk at home]`/memory line references
   the transformation.
4. Start a run — the altar shows the run-state banner and `POST /evolve`
   returns 400.
5. Evolve with `ENABLE_IMAGE_GENERATION=false` — ceremony completes, old art
   kept, result carries `art_regenerated: false`.
6. Watch the AI log for parse-retry rates on the five templates; tune
   wording/max_tokens if the local 7B struggles.
