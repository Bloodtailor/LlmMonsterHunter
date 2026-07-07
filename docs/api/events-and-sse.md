# Events & SSE

Because most action endpoints are async (see the
[index](README.md)), SSE is how the client learns what
actually happened. This file catalogs the events and how the frontend
consumes them.

## The SSE endpoint

### GET /api/sse/events
A `text/event-stream`. Open it once per session, up front. Emits a `ping`
event immediately and a keep-alive `ping` every 30 seconds of silence.
Every event is delivered as:
```
event: <event.type>
data: <JSON of event.data>
```
Any event registered with `send_to_frontend=True` in the backend event
registry (`backend/core/events/`) is forwarded here automatically.

## Event catalog

Event names are dotted (e.g. `llm.generation.started`). Fields listed are
the `data` payload.

### Connection
- `ping` — `{ timestamp: number }`

### LLM generation (token streaming)
- `llm.generation.started` — `{ item, generation_id }`
- `llm.generation.update` — `{ generation_id, partial_text, tokens_so_far }`
- `llm.generation.completed` — `{ item, generation_id, result }`
- `llm.generation.failed` — `{ item, generation_id, error }`

### Image generation
- `image.generation.started` — `{ item, generation_id }`
- `image.generation.update` — `{ item, generation_id, elapsed_seconds }`
- `image.generation.completed` — `{ item, generation_id, result }`
- `image.generation.failed` — `{ item, generation_id, error }`

### AI queue
- `ai.queue.update` — `{ all_items, trigger }`

### Workflows
- `workflow.started` — `{ item, workflow_id }`
- `workflow.update` — `{ workflow_id, workflow_type, step, data }` — progress within a workflow; the `step` string and `data` object are how mid-flight information (streamed-generation ids, a resolved battle turn, an arrival location) reach the client
- `workflow.completed` — `{ item, workflow_id, result }` — the terminal event carrying an action's result (see the per-endpoint result shapes in the other files)
- `workflow.failed` — `{ item, workflow_id, error }`
- `workflow.queue.update` — `{ all_items, trigger }`

### Monster domain events
Facts about the game world, emitted from the monster generator so any
workflow that creates a monster broadcasts them (used for live card reveal
and Sanctuary auto-refresh):
- `monster.created` — `{ monster }` (full `MonsterObject`, at the blueprint stage)
- `monster.updated` — `{ monster }` (full `MonsterObject` after a staged-generation
  update: persona, then story/`complete`; frontend replaces the monster in place.
  ALSO fires after growth reflections and returning-monster transforms — stat
  bumps, reworded abilities, and persona grudges arrive this way)
- `monster.ability_added` — `{ monster_id, ability }` (`AbilityObject`)
- `monster.art_ready` — `{ monster_id, image_path }` (initial generation AND
  evolution art regen — the frontend repoints the card image either way)
- `monster.memory_added` — `{ monster_id, memory }` (`MemoryObject` — the monster
  recorded a permanent memory of the party; see monsters-and-roster.md)
- `monster.evolved` — `{ monster, evolution }` (full `MonsterObject` +
  `EvolutionObject`): the evolution ceremony's transform moment — identity,
  stats, and rarity just flipped in place. The evolution record carries the
  old name/species/stats and `old_card_art_path` so the ceremony UI can show
  the before-form without a fetch. Later ceremony stages keep arriving as
  ordinary `monster.updated` patches.

### Dungeon domain events
- `dungeon.monster_revealed` — `{ monster }` (full `MonsterObject`): a
  PRE-EXISTING monster was staged into the current encounter (returning
  monsters and blend-ins). New monsters announce via `monster.created`;
  this event exists because existing monsters never re-fire creation events.
- `dungeon.goal_updated` — `{ goal: { text, status, progress_notes } }`:
  the goal referee recorded progress on (or completion of) the run's goal.
  `status` is `pending` or `complete`.

### Inventory domain events
Facts about the party's possessions, emitted from the inventory generator
and the item-consumption flows:
- `inventory.item_added` — `{ item }` (`ItemObject` — treasure or dialogue reward)
- `inventory.item_updated` — `{ item }` (a use was spent, uses remain)
- `inventory.item_consumed` — `{ item_id, name }` (last use spent OR the
  item was forfeited with the run's spoils; either way it is gone)
- `inventory.cocatok_added` — `{ cocatok }` (`CoCaTokObject` — a victory was minted)
- `inventory.cocatok_removed` — `{ cocatok_id, title }` (a keepsake minted
  mid-run was taken back — the run's spoils were forfeited on defeat/abandon)

`workflow_type` values seen in workflow events: `generate_detailed_monster`,
`generate_ability`, `evolve_monster`, `enter_dungeon`, `choose_path`,
`respond_to_monster`, `sneak_past`, `surprise_attack`, `setup_camp`,
`use_dungeon_ability`, `use_dungeon_item`, `continue_exploring`,
`battle_turn`, `chat_with_monster`, and the self-queued housekeeping workflows
`chat_housekeeping`, `condense_dungeon_log`, `condense_battle_log`
(rolling summaries / memory extraction — queued backend-side behind the
workflow the player is waiting on; the frontend can ignore their
completions except for the `monster.memory_added` events extraction fires).

Notable `workflow.update` steps:
- `emit_generation_id` — a streamed text generation just started; its id is
  in `data` (`entry_text_generation_id` for the dungeon entrance,
  `encounter_text_generation_id` for dialogue/battle encounters,
  `look_text_generation_id` for explore arrivals,
  `camp_text_generation_id` for camp scenes,
  `treasure_text_generation_id` for treasure discoveries,
  `turn_vanity_generation_id` for the acting party monster's inner
  monologue when a battle turn is handed to the player,
  `chat_text_generation_id` for the home-base chat reply,
  `evolution_text_generation_id` for the evolution ceremony narration). Match
  subsequent `llm.generation.update` events by `generation_id` to stream that text.
- `form_applied` — `data.monster` + `data.evolution` (the evolution
  ceremony's transform just landed; mirrors the `monster.evolved` event)
- `location_generated` — `data.current_location` (a path's arrival location)
- `action_resolved` — `data.action_result` (one resolved battle turn; see [Dungeon & Battle](dungeon-and-battle.md))
- `generate_treasure_item` — `data.item` (the treasure path's found item)
- `mint_victory_cocatok` — `data.cocatok` (the victory's minted keepsake)

## How the frontend consumes this

The React frontend does **not** put SSE events into component state
directly (that re-rendered the whole app on every token). Instead:

```
useSSE(handlers)  →  pure module handlers (aiEventHandlers,
                     workflowEventHandlers, monsterEventHandlers)
                 →  broadcastEvent(name, data)   [api/core/eventBroadcast.js]
                       ├─ domain stores (useSyncExternalStore slices)
                       └─ subscriber registry
```

Two consumption patterns:
- **`useEventSubscription(camelCaseName, handler)`** — react to a moment
  (broadcast names are camelCase: `monsterCreated`, `workflowCompleted`,
  `llmGenerationUpdate`, `imageGenerationCompleted`, …; `'*'` = wildcard).
- **Store slice hooks** — subscribe to computed status (queue, current LLM
  status, workflow status) for display.

The `EventContext` now carries only connection state (`isConnected`,
`connect`, `disconnect`). Reusable helper `useStreamedGeneration(idKey,
{ onText, onComplete })` implements the `emit_generation_id` → filtered
`llmGenerationUpdate` streaming pattern.
