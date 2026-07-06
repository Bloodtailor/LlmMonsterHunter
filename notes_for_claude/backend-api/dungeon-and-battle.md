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
  exploring                          event fires:
      ▲                                • monster_riddle → answer a riddle
      │                                • monster_battle → turn-based battle
      └───────────────────────────────┘
```
A dungeon run ends by taking an **exit path**, or by losing/being spared in
a battle. Party condition (battle damage) persists across the run and resets
on exit.

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
**`workflow.completed` result — riddle event:**
```json
{ "success": true, "event": "monster_riddle",
  "current_location": LocationObject, "monster_id": number,
  "greeting": string, "riddle": string }
```
**`workflow.completed` result — battle event:**
```json
{ "success": true, "event": "monster_battle",
  "current_location": LocationObject, "enemy_ids": number[],
  "battle_intro": string, "battle_snapshot": BattleSnapshot }
```
**`workflow.completed` result — exit path taken:**
```json
{ "success": true, "exited": true, "exit_text": string }
```
During the workflow: `workflow.update` step `location_generated`
(`data.current_location`); for battle/riddle events the encounter monsters
reveal live via `monster.created` / `monster.ability_added` /
`monster.art_ready`, and vanity text streams (step `emit_generation_id`,
`data.encounter_text_generation_id`).

### POST /dungeon/answer-riddle
**Request:** `{ "answer": string }`
Judges the answer semantically (lenient on spelling/synonyms, strict on
identity) and responds in the monster's voice.
**Success:** `{ "success": true, "workflow_id": number }`
**`workflow.completed` result:** `{ success, correct: boolean, response: string }`

### POST /dungeon/continue
Generates a fresh set of paths from the current location (the loop's back
edge; also used after resolving an encounter).
**Success:** `{ "success": true, "workflow_id": number }`
**`workflow.completed` result:** `{ success, current_location: LocationObject, paths: { [path_id]: PathObject } }`

### GET /dungeon/state
Public dungeon state (hidden path events/destinations and riddle answers
stripped). Synchronous.
**Success:**
```json
{ "success": true, "in_dungeon": boolean,
  "current_location": LocationObject|null,
  "paths": { "[path_id]": PathObject },
  "active_encounter": { "event": string, "monster_id": number, "riddle": string }|null }
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
