# Dungeon & Battle API

The gameplay loop. Every endpoint here is **async** (queues a workflow,
returns a `workflow_id`, results arrive via SSE) except `GET .../state`.
Read the [index](../backend-api-reference.md) workflow model first, and the
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
`dungeon_state.dungeon_log` and fed — clamped to a character budget
(`backend/game/utils/context_limits.py`) — into every dungeon LLM generation,
so the story stays coherent across the run. Battles keep their own detailed
rolling log; only a compact summary of each battle lands in the dungeon log.

**Party abilities anywhere.** While in the dungeon (outside battle), any party
monster can use any of its abilities on anything — a path, a monster, the
location, or free text — via `POST /dungeon/use-ability`. The LLM referee
decides if it does anything at all (heals genuinely heal; perceptive abilities
can hint at a path's true, hidden destination; most odd attempts fizzle).
During battles, abilities are used on the monster's turn and cost that turn.

## Dungeon (`/api/dungeon`)

### GET /dungeon/enter
Requires a ready active party. Streams entry text, generates a starting
location and its paths (each path is a *route onward*, not a destination —
its true destination and its hidden event are generated now but withheld).
**Success:** `{ "success": true, "workflow_id": number }`
**`workflow.completed` result:** `{ success, current_location: LocationObject, paths: { [path_id]: PathObject } }`
Also streams entry text via `workflow.update` step `emit_generation_id`
(`data.entry_text_generation_id`) + `llm.generation.update`.

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
{ "success": true, "exited": true, "exit_text": string }
```
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
`emit_generation_id`, `data.camp_text_generation_id`).
**Success:** `{ "success": true, "workflow_id": number }`
**`workflow.completed` result:** `{ success, camped: true }`

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
**Success:** `{ "success": true, "workflow_id": number }`
**`workflow.completed` result:** `{ success, narration, effect, party_conditions }`

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

### GET /dungeon/state
Public dungeon state (hidden path events/destinations stripped). Synchronous.
**Success:**
```json
{ "success": true, "in_dungeon": boolean,
  "current_location": LocationObject|null,
  "paths": { "[path_id]": PathObject },
  "party_conditions": { "[monster_id]": string },
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
`dialogue` for talk turns, and a `battle_snapshot`). The frontend queues
these for click-through. The `battle_turn` `workflow.completed` result is
one of:
- `{ pending: "player_turn", pending_actor, pending_actor_name, battle_snapshot }`
- `{ pending: "player_response", pending_talk: { speaker_name, dialogue }, battle_snapshot }`
- `{ outcome: "victory"|"defeat", resolution, joined_names: string[], outcome_text, battle_snapshot }`

`resolution` explains *how* it ended: `combat | joined | yielded | fled |
spared`. On `joined`, the surviving enemies are added to the following list
(`joined_names` lists them) — this is the capture mechanic. `defeat` clears
the dungeon run backend-side.
