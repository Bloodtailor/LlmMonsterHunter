# Tuning Guide — Every Knob in One Place

The game's balance lives in small, named constants, not scattered magic
numbers. This catalog lists every knob, where it lives, its default, and
what turning it does. The philosophy throughout: **the LLM only ever picks
words; Python code owns every number** — so these knobs are the numbers.

Related reading: [architecture.md](architecture.md) for how the systems
fit together, [api/README.md](api/README.md) for the API surface.

## Environment variables (`.env`)

Copy `.env.example` to `.env` and adjust. Restart the backend after changes.

| Variable | Default | Effect |
|---|---|---|
| `LLM_MODEL_PATH` | — | Path to the GGUF text model |
| `LLM_CONTEXT_SIZE` | `4096` | The model's context window. Drives every prompt budget and the monster-detail tier (see below) |
| `LLM_CONTEXT_FILL_PERCENT` | `1.0` | Fraction of the window prompts may fill (0.3–1.0). Lower it for models that degrade when nearly full |
| `LLM_GPU_LAYERS` | `35` | Layers offloaded to the GPU |
| `LLM_DISABLE_THINKING` | `true` | Prefill an empty `<think>` block so reasoning models answer directly |
| `LLM_DEFAULT_MAX_TOKENS` | `256` | Response length cap per generation |
| `LLM_DEFAULT_TEMPERATURE` | `0.8` | Sampling temperature (also `_TOP_P` `0.9`, `_TOP_K` `40`, `_REPEAT_PENALTY` `1.1`, `_SEED` `-1`, and the rest of the `LLM_DEFAULT_*` family — see `backend/core/config/llm_config.py`) |
| `ENABLE_IMAGE_GENERATION` | `false` | Master switch for ComfyUI card art |
| `COMFYUI_SERVER_URL` | `http://127.0.0.1:8188` | ComfyUI endpoint (also `COMFYUI_TIMEOUT` `300`) |
| `COMFYUI_CHECKPOINT` | DreamShaper XL Turbo | Image model; also `_STEPS` `8`, `_CFG` `2.0`, `_WIDTH` `896`, `_HEIGHT` `1254`, `_SAMPLER`, `_SCHEDULER`, `_NEGATIVE_PROMPT` — see `backend/core/config/comfyui_config.py` |
| `DB_NAME` / `DB_NAME_TEST` | `monster_hunter_game` / `monster_hunter_game_test` | Game database / offline-suite database (test DB auto-created) |
| `FLASK_DEBUG` | `True` | Debug mode; also gates the in-app test-runner routes |

## Prompt context budgets — `backend/game/utils/context_limits.py`

Token-aware budgets that scale with `LLM_CONTEXT_SIZE`.

| Knob | Default | Effect |
|---|---|---|
| `FLEXIBLE_BLOCK_SHARES` | dungeon_log `0.25`, battle_log `0.20`, chat_history `0.20`, dialogue_history `0.15`, last_run_log `0.10`, turn_history `0.08`, monster_memories `0.06`, run_journal `0.06`, location_description `0.05` | Each growing history's share of the prompt budget. **The one place to rebalance prompt composition** |
| `REQUIRED_BLOCKS` | party_details, monster_details | Never truncated — identity arrives whole |
| `RESERVED_RESPONSE_TOKENS` | `1200` | Held back for the model's answer + fixed instructions |
| `MIN_FLEXIBLE_CHARS` | `600` | Floor per flexible block on tiny windows |
| `resolve_detail_tier()` | compact `<6144` / standard `<12288` / full `≥12288` | How much of each monster's persona enters multi-monster blocks, binned by window size |

## Battle — `backend/game/battle/constants.py`

| Knob | Default | Effect |
|---|---|---|
| `CONDITION_LADDER` | fresh → scuffed → wounded → battered → critical → incapacitated | Monster wellbeing. No HP math anywhere |
| `IMPACT_STEPS` | light `1`, heavy `2`, devastating `3`, heal_light `-1`, heal_major `-2` | How far each referee impact word moves a monster on the ladder |
| `RESOURCE_LADDER` | brimming → steady → strained → drained → spent | Stamina/mana reserves (refill on dungeon entry, camp rest, restores) |
| `RESOURCE_DELTAS` | minor `1`, moderate `2`, heavy `3`, restore_minor `-1`, restore_major `-2` | Referee cost words → ladder steps |
| `ABILITY_POOL_BY_TYPE` | attack/defense/movement → stamina; support/special/utility → mana | Default pool an ability drains when the referee stays silent |
| `ENEMY_COUNT_RANGE` | `(1, 2)` *(danger)* | Enemies per battle (design allows up to 7; each enemy costs ~4 LLM calls + art). Overridden by the expedition's danger profile |
| `MAX_CONSECUTIVE_ENEMY_TURNS` | `6` | Softlock valve — forces an ally turn after this many enemy turns |
| `OVERDUE_WAIT_MULTIPLIER` | `2` | Fairness valve — a monster waiting 2× the combatant count is force-picked |
| `PLAYER_TEXT_MAX_CHARS` | `500` | Cap on free-text actions and talk |
| `RECENT_LOG_SIZE` / `TURN_HISTORY_SIZE` | `400` / `40` | Storage safety valves (prompts are budget-clamped separately) |

## Dungeon events — `backend/game/dungeon/events.py`

Path events are rolled **in Python** at generation time and hidden from
the player (and from the LLM's narration) until a path is chosen.
Knobs marked *(danger)* are overridden by the active expedition's danger
profile — see the Expeditions section below.

| Knob | Default | Effect |
|---|---|---|
| `EVENT_WEIGHTS` | explore `0.55`, dialogue `0.18`, battle `0.18` *(danger)*, treasure `0.09` | What waits behind each path |
| `RETURNING_EVENT_WEIGHT` | `0.12` *(danger)* | Weight of a remembered monster returning (only when the pool is nonempty) |
| `EXPLORE_MONSTERS_CHANCE` | `0.5` *(danger)* | Chance an explore location has (non-hostile) monsters |
| `EXPLORE_MONSTER_COUNT_RANGE` | `(1, 2)` | How many dwell there |
| `PATH_COUNT_RANGE` | `(2, 4)` | Paths per junction |
| `EXIT_PATH_CHANCE` | `0.33` | Chance one path is a dungeon exit |
| `PATH_OVERGENERATE_COUNT` | `6` | Paths asked of the LLM per batch (the LAST ones are used — small local models repeat themselves early) |

## Expeditions — `backend/game/dungeon/run_context.py` + `handlers/notices.py`

The entrance notice board: the LLM writes each notice's title/pitch/theme,
**Python rolls its danger word**, and the chosen notice becomes the run's
`run_context`. The theme threads into every location/path/monster prompt
(one `expedition_brief` block); the danger word maps to the code knobs
below. `run_context.py` is also where the run's goal will live.

| Knob | Default | Effect |
|---|---|---|
| `NOTICE_COUNT` (notices.py) | `3` | Notices posted per board |
| `NOTICE_DANGER_WEIGHTS` (notices.py) | calm `0.30`, risky `0.45`, perilous `0.25` | Odds of each danger word per notice |
| `DEFAULT_DANGER` | `risky` | Danger assumed for the referee hint when no notice was answered |
| `DANGER_PROFILES` | ↓ | What each danger word turns into |

Danger word → code knobs (`DANGER_PROFILES`); a run without a notice
keeps every default, and `risky` **is** the defaults:

| Knob | calm | risky | perilous |
|---|---|---|---|
| `enemy_count_range` | (1, 1) | (1, 2) | (2, 3) |
| `battle_event_weight` | 0.12 | 0.18 | 0.26 |
| `explore_monsters_chance` | 0.4 | 0.5 | 0.65 |
| `returning_event_weight` | 0.10 | 0.12 | 0.16 |
| `referee_hint` | judge kindly | judge fairly | judge harshly |

## Run goals — `backend/game/dungeon/goal.py`

One goal per run, written at the entrance (themed). After each RESOLVED
event (explore/treasure arrival, dialogue outcome, battle victory) the
goal referee answers one word: `no / progress / complete`. The fulfilled
goal pays out at the exit (`handlers/exit_run.py`): one rare item + a
code-owned `notable` growth step per member. Defeat forfeits the reward.

| Knob | Default | Effect |
|---|---|---|
| `GOAL_MIN_EVENTS` | `3` | THE VALVE: `complete` is ignored before this many resolved events — no first-door wins |
| `GOAL_CHECK_LOG_TAIL` | `4` | How many recent dungeon-log entries the goal referee judges by |
| `GOAL_ANSWERS` | no / progress / complete | The referee's word ladder (anything else counts as `no`) |
| reward growth tier | `notable` (exit_run.py) | The bonus growth step each member gets for a fulfilled goal (caps still apply) |

## Affinity — `backend/game/monster/affinity.py`

How deeply a monster trusts the party. Moved ONE step at a time by
code-visible events; the LLM only ever reads the word. The headline
effect: a **wary monster acts on its own in battle**
(`battle/turn/autonomy.py`) — its turn auto-resolves like an enemy turn
and the player watches. Devoted monsters get a friendlier referee line;
the affinity line also rides chat and evolution-narration context.

| Knob | Default | Effect |
|---|---|---|
| `AFFINITY_LADDER` | wary → familiar → trusting → devoted | The trust word ladder (stored on `monsters.affinity`; NULL reads wary) |
| `DEFAULT_AFFINITY` | `wary` | Where new recruits start — your newest companion fights beside you, not FOR you |
| `MAX_AFFINITY_STEPS_PER_RUN` | `2` | THE VALVE: in-run events can deepen each bond at most this much per run |
| autonomy tier | `wary` only (`is_autonomous`) | Which tier ignores commands in battle |
| step events | first-heals by an ally, camp rest, rejoining with memories, surviving a run (exit), a memory-producing home chat, evolution | Each moves affinity +1 (in-run ones under the valve; home ones unbudgeted) |

Existing followers were backfilled to `trusting` by
`backend/tests/add_affinity_column.py` (idempotent dev-DB script).

## Growth — `backend/game/memory/growth.py`

In-run growth: small, journal-earned nudges (evolution is the big leap).

| Knob | Default | Effect |
|---|---|---|
| `GROWTH_STAT_TIERS` | slight `2%`, notable `5%` | The LLM's tier words → percent stat growth |
| `LIFETIME_GROWTH_CAP` | `0.30` | Max lifetime growth per stat from reflections |
| `MAX_ABILITIES` | `6` | Ability-count cap (mirrored in evolution + returning) |
| `REWORD_MAX_RATIO` | `1.15` | A reworded ability description may not outgrow the old one |
| `SPOTLIGHT_CAP` | `2` | Camp-spotlight reflections per camp |

## Returning monsters — `backend/game/memory/returning.py`

| Knob | Default | Effect |
|---|---|---|
| `BLEND_IN_CHANCE` | `0.25` | Per normal encounter: swap one fresh slot for a remembered monster |
| `RETURN_STAT_TIERS` | (see file) | Stat boost tiers for a returning monster |
| `RETURN_COUNT_MULTIPLIER_STEP` / `_CAP` | `0.25` / `1.5` | Each return compounds the boost, up to the cap |
| `LIFETIME_RETURN_BOOST_CAP` | `0.50` | Max lifetime boost from returning |
| `GRUDGES_AND_BONDS_CAP` | `4` | Persona grudge/bond lines kept |

## Evolution — `backend/game/monster/evolution.py`

| Knob | Default | Effect |
|---|---|---|
| `EVOLUTION_STAGE_BOOSTS` + `EVOLUTION_BOOST_FLAT` | `25% → 15% → 10%` flat | All-stat boost per stage, unlimited stages, **outside** the growth caps |
| `GUIDANCE_MAX_CHARS` | `200` | Player's optional guidance whisper |
| `NAME_ROOT_CHARS` | `4` | Old first name's prefix that must survive (Rokk → Rokkarath) |
| `BACKSTORY_ADDENDUM_MAX_CHARS` | `800` | Evolution chapter appended to the backstory |
| `ABILITY_REWORD_CAP` | `2` | Abilities reworded per evolution |

## Rolling summaries — `backend/game/utils/rolling_summary.py`

Old history is condensed by the LLM; recent history stays verbatim.
Per-source knobs in `SUMMARY_SOURCES` (keep_recent / batch_min / batch_max):
chat_history `16/12/30`, dungeon_log `12/10/25`, battle_log `14/12/25`.

## Chat — `backend/game/chat/manager.py` (`CHAT_SETTINGS`)

| Knob | Default | Effect |
|---|---|---|
| `extract_after_messages` | `8` | Unreviewed lines that trigger a memory-extraction pass |
| `extract_segment_max` | `24` | Most lines one pass reviews |
| `max_memories_per_pass` | `3` | Memories saved per pass |
| `history_page_size` | `50` | Messages per API history page |

## Journal — `backend/game/memory/journal.py`

`JOURNAL_MAX_LINES` `30` per monster (oldest dropped), `JOURNAL_LINE_CLIP`
`160` chars per line.

## Party size (two places — keep in sync)

- Frontend: `GAME_RULES.MAX_PARTY_SIZE = 4` in `frontend/src/shared/constants/constants.js`
- Backend: the max-4 check in `backend/models/active_party.py`

## Prompt templates — `backend/ai/llm/prompts/*.json`

Every LLM instruction the game sends, one JSON file per domain
(monster, dungeon, battle, chat, memory, evolution, inventory, …).
Edit the wording freely; the referee's *word ladders* above decide what
the answers are allowed to do. The Developer screen's AI log table shows
every prompt byte-exactly as the model received it.
