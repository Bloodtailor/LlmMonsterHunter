# Dungeon & Battle API

The gameplay loop. Every endpoint here is **async** (queues a workflow,
returns a `workflow_id`, results arrive via SSE) except `GET .../state`.
Read the [index](README.md) workflow model first, and the
[Events & SSE](events-and-sse.md) catalog for how results are delivered.

## The loop at a glance

```
enter dungeon ─▶ arrive at a location with 2–4 PATHS (+ maybe an exit)
      ▲                     │  each path secretly holds a hidden EVENT and a
      │                     │  pre-generated destination (never sent to client)
      │                     ▼
  continue          choose a path ─▶ arrive at the destination, the hidden
  exploring                          event fires (weighted in events.py):
      ▲                                • location_explore (~60%) → look around,
      │                                  then: talk / surprise attack / sneak past
      │                                  monsters, or camp / continue if clear
      │                                • monster_dialogue (~20%) → a monster asks
      │                                  a question; the LLM decides the outcome
      │                                • monster_battle (~20%) → turn-based battle
      └───────────────────────────────┘
```
A dungeon run ends by taking an **exit path**, or by losing/being spared in
a battle. Party condition (battle damage) persists across the run and resets
on exit.

**The dungeon log.** Everything that happens in a run (arrivals, encounters,
exchanges, ability uses, camps, battle summaries) is recorded backend-side in
`dungeon_state.dungeon_log` and fed into every dungeon LLM generation, so the
story stays coherent across the run. Battles keep their own detailed rolling
log (turn-numbered); when a battle ends, the LLM writes a summary of it
(including lasting effects) into the dungeon log.

**Token-aware context budgets.** Prompt context blocks are clamped by
`backend/game/utils/context_limits.py`, which scales budgets from the loaded
model's `LLM_CONTEXT_SIZE` (.env): required blocks (party/monster details)
are never truncated; flexible blocks (dungeon log, battle log, dialogue,
turn history, chat history) each get a percentage share of the window and
keep their most recent content. Bigger models automatically get richer
prompts. `LLM_CONTEXT_FILL_PERCENT` (.env, default 1.0) treats only a
fraction of the window as usable, for models that degrade when nearly full.

**Rolling summaries.** Growing histories are no longer merely truncated:
when enough old entries pile up beyond a keep-verbatim window, ONE batch of
the oldest uncovered entries is condensed by the LLM into a rolling summary
(`backend/game/utils/rolling_summary.py`, per-source knobs in
`SUMMARY_SOURCES`). Raw entries are KEPT — single-source prompts can still
read far more verbatim. Prompt composition = summaries (oldest first) +
verbatim tail, then the normal budget clamp. The condensing runs as
self-queued workflows (`condense_dungeon_log` queued by the heavier dungeon
workflows, `condense_battle_log` queued by `battle_turn`,
`chat_housekeeping` for chats) BEHIND the workflow the player awaits, so it
never delays a result. When a run closes (victory OR defeat) the dungeon
log + its summaries are snapshotted to the `last_run_log` GlobalVariable —
home-base chats read it as context.

**Party abilities anywhere.** While in the dungeon (outside battle), any party
monster can use any of its abilities on anything — a path, a monster, the
location, or free text — via `POST /dungeon/use-ability`. The LLM referee
decides if it does anything at all (heals genuinely heal; perceptive abilities
can hint at a path's true, hidden destination; most odd attempts fizzle).
During battles, abilities are used on the monster's turn and cost that turn.

## Dungeon (`/api/dungeon`)

### POST /dungeon/expedition-notices
Generates the entrance notice board: 2-3 expedition notices, each with an
LLM-written `title`, `pitch`, and `theme`, plus a **Python-rolled** danger
word (`calm | risky | perilous`). The chosen notice's id is passed to
`/dungeon/enter`; its theme threads into every location/path/monster
generation for the run and its danger maps to code knobs (enemy counts,
event weights, referee bias — see docs/tuning.md). Rejected while a run
is active.
**Success:** `{ "success": true, "workflow_id": number }`
**`workflow.completed` result:** `{ success, notices: [{ id, title, pitch, theme, danger }] }`

### GET /dungeon/enter
Requires a ready active party. Optional query param `notice_id` answers
one of the board's posted notices (validated against the stored board) —
its theme + danger become the run's context. Without `notice_id` the run
is an ordinary, unthemed expedition.
Streams entry text, generates a starting location and its paths (each
path is a *route onward*, not a destination — its true destination and
its hidden event are generated now but withheld).
Opens a `dungeon_runs` history row and refills the party's stamina/mana
pools — **entering is the only guaranteed reset of reserves**.
**Success:** `{ "success": true, "workflow_id": number }`
**`workflow.completed` result:** `{ success, current_location: LocationObject, paths: { [path_id]: PathObject }, party_conditions, party_resources: { "[monster_id]": { "stamina": word, "mana": word } }, expedition: { title, theme, danger } | null, goal: { text, status, progress_notes } | null }`
Reserve words ladder: `brimming > steady > strained > drained > spent`.
Also streams entry text via `workflow.update` step `emit_generation_id`
(`data.entry_text_generation_id`) + `llm.generation.update`.
Every run gets ONE goal (LLM-written, themed). After resolved events the
goal referee may emit `dungeon.goal_updated` with the updated snapshot;
a goal can only complete after `GOAL_MIN_EVENTS` resolved events.

### POST /dungeon/choose-path
**Request:** `{ "path_id": string }` (e.g. `"path_1"`)
Resolves the path's pre-generated destination (instant), then fires its
hidden event.
**Success:** `{ "success": true, "workflow_id": number }`
**`workflow.completed` result — explore event (the most common):**
```json
{ "success": true, "event": "location_explore",
  "current_location": LocationObject,
  "monsters_present": boolean, "monster_ids": number[],
  "party_conditions": { "[monster_id]": string } }
```
Look-around text streams (step `emit_generation_id`,
`data.look_text_generation_id`). If `monsters_present`, the area's monsters
reveal live (they have NOT noticed the party); the player then talks
(`/dungeon/respond`), ambushes (`/dungeon/surprise-attack`), or sneaks
(`/dungeon/sneak`). If the area is clear: camp (`/dungeon/camp`) or continue.
**`workflow.completed` result — dialogue event:**
```json
{ "success": true, "event": "monster_dialogue",
  "current_location": LocationObject, "monster_id": number,
  "greeting": string, "question": string,
  "party_conditions": { "[monster_id]": string } }
```
The monster asks a question of its own devising; answer via `/dungeon/respond`.
**`workflow.completed` result — battle event:**
```json
{ "success": true, "event": "monster_battle",
  "current_location": LocationObject, "enemy_ids": number[],
  "battle_intro": string, "battle_snapshot": BattleSnapshot,
  "party_conditions": { "[monster_id]": string } }
```
**`workflow.completed` result — exit path taken:**
```json
{ "success": true, "exited": true, "exit_text": string,
  "growth": [GrowthResult],
  "goal": { "text": string, "status": "pending"|"complete", "progress_notes": string[] } | null,
  "goal_reward": { "item": ItemObject, "growth": [GrowthResult] } | null }
```
The exit is the EXIT CEREMONY: every party member runs a growth reflection
over its run journal (see *Memory & evolution* below); a FULFILLED goal
adds the reward ceremony (one rare item + a code-owned `notable` growth
step per member — `goal_reward` is null for unfinished goals); the run's
history row closes as `victory_exit`.
**Returning-monster event** (`returning_monster`, weight 0.12 whenever
remembered monsters are eligible): a previously-met monster comes back
TRANSFORMED by its memories (code-clamped stat boost, possibly an answering
ability, reworded battle line). Its disposition routes the encounter — the
result mirrors the matching event shape (`monster_battle`/`monster_dialogue`/
`location_explore`) plus `"returning": true`, and the recognition scene
streams via `data.reunion_text_generation_id`. The monster's card arrives via
`dungeon.monster_revealed` (NOT `monster.created` — it already exists).
Blend-ins: ~25% of normal encounters swap one generated slot for a
remembered monster (unchanged, also revealed via `dungeon.monster_revealed`).
During the workflow: `workflow.update` step `location_generated`
(`data.current_location`); encounter monsters reveal live via
`monster.created` / `monster.ability_added` / `monster.art_ready`, and vanity
text streams (step `emit_generation_id`, `data.encounter_text_generation_id`
for dialogue/battle events, `data.look_text_generation_id` for explore).

### POST /dungeon/respond
**Request:** `{ "message": string }` (non-empty, ≤500 chars)
The party speaks to the encounter monster(s): answers the question, keeps a
conversation going, or opens talks with monsters found while exploring (an
explore encounter converts to a dialogue). The LLM responds in the monster's
voice and **decides the outcome** of every exchange.
**Success:** `{ "success": true, "workflow_id": number }`
**`workflow.completed` result:**
```json
{ "success": true, "outcome": string, "response": string,
  "joined_names?": string[], 
  "battle_intro?": string, "enemy_ids?": number[], "battle_snapshot?": BattleSnapshot }
```
`outcome` is one of:
- `continue_dialogue` — the conversation stays open; respond again
- `begin_battle` — the monster attacks (`battle_snapshot` + `battle_intro` included)
- `allow_passage` — the party may continue exploring
- `reward` — the monster grants a boon (narrative for now; mechanics hook in `outcomes.py`)
- `punish` — the monster exacts a price (narrative for now; mechanics hook in `outcomes.py`)
- `join_party` — the monster(s) join the following list (`joined_names`)

### POST /dungeon/sneak
Attempt to sneak past the monsters spotted while exploring. The LLM judges
success from the party's natures, the monsters, and the terrain.
**Success:** `{ "success": true, "workflow_id": number }`
**`workflow.completed` result:** `{ success, success: boolean, narration: string, ... }` —
on failure the monsters notice: `battle_intro`, `enemy_ids`, and
`battle_snapshot` are included and a battle begins.

### POST /dungeon/surprise-attack
Strike first at the monsters spotted while exploring. Always starts a battle,
opened on the party's terms (the ambush is seeded into the battle log).
**Success:** `{ "success": true, "workflow_id": number }`
**`workflow.completed` result:** `{ success, battle_intro, enemy_ids, battle_snapshot }`

### POST /dungeon/camp
Set up camp in a monster-free explore location (once per location). Streams a
vanity scene of the party's monsters talking around the fire (step
`emit_generation_id`, `data.camp_text_generation_id`), then:
1. **Rest restores reserves** — the camp referee judges per-monster restore
   words (parse failure = full rest for everyone).
2. **The spotlight** — the LLM picks the 1-2 members whose run journal shows
   the strongest story; only they run growth reflections at camp. Everyone
   else keeps a `camp` memory of the evening.
**Success:** `{ "success": true, "workflow_id": number }`
**`workflow.completed` result:** `{ success, camped: true, party_resources, growth: [GrowthResult] }`
`GrowthResult`: `{ monster_id, monster_name, reflection, stat|null, tier|null, new_ability|null, reworded_ability|null }`

### POST /dungeon/use-ability
**Request:**
```json
{ "monster_id": number, "ability_id": number,
  "target_type": "path"|"monster"|"location"|"custom",
  "target_id?": string|number, "target_text?": string }
```
A party monster uses an ability on anything, outside battle. `target_id` is a
path id for `path` targets or a monster id for `monster` targets;
`target_text` (≤500 chars) describes `custom` targets. The LLM referee
decides the effect: `none`, `heal_light`/`heal_major` (party members only —
moves them up the condition ladder), or `reveal` (true information woven
into the narration; path targets secretly include their hidden destination
so perceptive abilities can hint at what lies beyond).
**Error (400):** in battle, monster not in party, unowned ability, bad target.
Out-of-battle ability use drains reserves too: the referee's optional
`stamina_cost`/`mana_cost` words rule; when silent, the ability's type picks
the pool (attack/defense/movement → stamina, support/special/utility → mana)
at `moderate`.
**Success:** `{ "success": true, "workflow_id": number }`
**`workflow.completed` result:** `{ success, narration, effect, party_conditions, party_resources }`

### POST /dungeon/continue
Generates a fresh set of paths from the current location (the loop's back
edge; also used after resolving an encounter). Blocked while an encounter
demands attention (an open conversation, or unhandled explore monsters).
**Success:** `{ "success": true, "workflow_id": number }`
**`workflow.completed` result:** `{ success, current_location: LocationObject, paths: { [path_id]: PathObject }, party_conditions }`

### GET /dungeon/debug-context
**DEVELOPER ONLY.** Full LLM-context X-ray, built by the same functions the
prompts use, so it shows exactly what the LLM receives: the dungeon log
(raw entries + budget-clamped text), party details text, encounter dialogue
and monster-details blocks, battle situation / combatant summary (with
per-monster waiting counts) / turn history / battle log, and paths
**including their hidden events and destinations**. Powers the left-side
debug panel in the frontend. Synchronous. Never use for game UI.

### POST /dungeon/abandon
Call the party home mid-run. Walking away is not exiting alive: **the
run's provisional spoils are forfeited first** (recruits joined this run
are released with a `bond_broken` memory; items and CoCaToks gained this
run are deleted, emitting `inventory.item_consumed` /
`inventory.cocatok_removed`). Then the active run closes as `abandoned` —
its log is snapshotted to `last_run_log` first so home-base chats can
still look back on it — any battle ends, and the run state wipes.
Synchronous, no LLM. A quiet no-op when not in a dungeon, so the frontend
can use it to clear stale run state (a run otherwise only ends by taking
an exit path, being defeated, or entering the dungeon again).
**Success:** `{ "success": true, "abandoned": boolean, "in_dungeon": false, "spoils_lost": { "released_names": string[], "lost_item_names": string[] } }`

### GET /dungeon/state
Public dungeon state (hidden path events/destinations stripped). Synchronous.
**Success:**
```json
{ "success": true, "in_dungeon": boolean,
  "current_location": LocationObject|null,
  "paths": { "[path_id]": PathObject },
  "party_conditions": { "[monster_id]": string },
  "party_resources": { "[monster_id]": { "stamina": string, "mana": string } },
  "active_encounter": { "event": string, "monster_ids": number[],
    "monsters_present": boolean|null, "camped": boolean|null,
    "dialogue": [{ "speaker": string, "text": string }] }|null }
```

## Battle (`/api/battle`)

Turn-based, one monster per turn. The **LLM directs turn order** and
narrates; **Python owns** the condition ladder, defending, and the
victory/defeat decision. There is no HP math — each monster sits on a
condition ladder (`fresh → scuffed → wounded → battered → critical →
incapacitated`) and the referee moves it by an impact word. See
`BattleSnapshot` in [Data Models](data-models.md).

**Reserves** work the same way: every combatant entry carries `stamina` and
`mana` words (`brimming → steady → strained → drained → spent`). The referee
judges each action's exertion in the SAME call as its impact (optional
`stamina_cost`/`mana_cost` words; code defaults per action type when silent:
attack → stamina minor, ability → its type's pool moderate, defend →
restores minor stamina). Costs hit the actor; restorative effects land on
the target. Explicit costs/restores in ability descriptions are honored.
Ally pools carry over between battles within a run and refill only on
dungeon entry; enemies start each battle brimming. Drained monsters falter
(the referee is told to weaken and narrate their exhaustion) and drained
ENEMIES prefer to defend, talk, or flee.

Battle phases (in `BattleSnapshot.phase`):
- `ready` — battle created; call `POST /battle/turn` with `action: null` to run opening initiative
- `awaiting_player_turn` — it is an ally's turn (`pending_actor`); submit an action
- `awaiting_player_response` — an enemy is talking (`pending_talk`); submit a reply via `POST /battle/respond`
- `processing` — a turn is resolving on the backend
- `victory` / `defeat` — the battle is over

### POST /battle/turn
Runs opening initiative (phase `ready`, no action) or takes the pending
ally's turn (phase `awaiting_player_turn`). One `battle_turn` workflow both
resolves the submitted action and advances the LLM-directed turn order until
it is an ally's turn again, an enemy starts talking, or the battle ends.

**Request:** `{ "action": ActionObject | null }` where `ActionObject` is one of:
- `{ "type": "attack", "target_id": string }`
- `{ "type": "defend" }`
- `{ "type": "ability", "ability_id": number, "target_id": string }`
- `{ "type": "custom", "text": string, "target_id"?: string, "info"?: string }` — a free-text action; the referee judges feasibility first, and an impossible attempt wastes the turn
- `{ "type": "talk", "text": string }` — negotiate with the enemies

`text` / `info` are capped at 500 characters.
**Success:** `{ "success": true, "workflow_id": number }`
**Error (400):** not this monster's turn, invalid/incapacitated target, unowned ability, empty text, etc.

### POST /battle/respond
Reply to an enemy that is talking (phase `awaiting_player_response`).
**Request:** `{ "response": string }` (non-empty, ≤500 chars)
**Success:** `{ "success": true, "workflow_id": number }`

### GET /battle/state
Public battle snapshot. Synchronous.
**Success:** `{ "success": true, "battle": BattleSnapshot }`

### Battle results over SSE
Each resolved turn is a `workflow.update` step `action_resolved` with
`data.action_result` (narration, actor/target, impact, an optional
`dialogue` for talk turns, `autonomous: boolean`, and a
`battle_snapshot`). The frontend queues these for click-through.
**Wary allies act on their own:** when the turn director picks a party
monster whose affinity is `wary`, control never reaches the player — the
LLM chooses its action (attack/ability/defend, never against the party),
the turn resolves with `autonomous: true`, and the loop continues. Its
one-sentence thought still streams first. The `battle_turn`
`workflow.completed` result is one of:
- `{ pending: "player_turn", pending_actor, pending_actor_name, battle_snapshot }`
- `{ pending: "player_response", pending_talk: { speaker_name, dialogue }, battle_snapshot }`
- `{ outcome: "victory"|"defeat", resolution, joined_names: string[], outcome_text, cocatok, defeat_reflection: string|null, spoils_lost: { released_names, lost_item_names } | null, battle_snapshot }`

`resolution` explains *how* it ended: `combat | joined | yielded | fled |
spared`. On `joined`, the surviving enemies are added to the following list
(`joined_names` lists them) — this is the capture mechanic; **recruits are
provisional until the party exits alive**. `defeat` clears the dungeon run
backend-side — but first the party takes ONE collective `defeat_reflection`
(the lesson of the loss; a shared `lesson` memory lands on every member),
**the run's spoils are forfeited** (`spoils_lost`: recruits joined this run
released with `bond_broken` memories — prime returning-monster fuel — and
this run's items/CoCaToks deleted with inventory events), and the run's
history row closes as `defeat`.

## Memory & evolution

The world remembers (design doc: `docs/plans/monster-memory-evolution.md`):
- **Every encounter writes permanent `monster_memories` rows** (pure code,
  no extra LLM calls): defeated (naming who landed the finishing blow and
  with what), defeated the party, joined/yielded/fled/spared, let-pass,
  rewarded/punished/talked (with the conversation excerpt), avoided
  (sneaked past — vague), camp/growth/lesson/returned/run_complete.
  Each fires `monster.memory_added`; read them back via
  `GET /api/monsters/<id>/memories`.
- **Prompts see memories**: encounter/dialogue/battle-enemy monster blocks
  carry each monster's freshest memories ("Remembers the party:").
- **The run journal** (dungeon state, per party monster, code-written)
  records what each member actually did and said; growth reflections read
  it as their evidence. Visible in `GET /dungeon/debug-context`.
- **Growth is clamped in code**: tiers slight/notable = 2/5%, 30% lifetime
  cap per stat; new abilities only when the journal shows a repeated
  wish/behavior (max 6); ability descriptions may be REWORDED to match how
  they were truly used (≤1.15× the old length, never longer).
- **Returning monsters** get 3/6/10% boosts × a return-count multiplier
  (cap 1.5×), 50% lifetime return cap, and may learn an ability that
  answers exactly how they once fell.
