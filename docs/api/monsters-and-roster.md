# Monsters & Roster API

Monster generation and library, plus the two roster lists — **following
monsters** (everyone you've collected) and the **active party** (the up-to
handful you take into a dungeon).

See [Data Models](data-models.md) for `MonsterObject`, `AbilityObject`, etc.
Generation endpoints are async — see the workflow model in the
[index](README.md).

## Monster Management (`/api/monsters`)

### GET /monsters/generate
Queues a `generate_detailed_monster` workflow that creates a full monster in
STAGES (see `backend/game/monster/generator.py`): blueprint (taxonomy, ecology,
code-derived stats) → persona (wish, fears, secret, voice) → story
(description, backstory, appearance) → two abilities → card art.
**Success:** `{ "success": true, "workflow_id": number }`
**Error (500):** `{ "success": false, "error": string }`
Results arrive via SSE as the stages complete: `monster.created` (blueprint —
the card can render immediately) → `monster.updated` (persona) →
`monster.updated` (story, `generation_stage: "complete"`) →
`monster.ability_added` (×2) → `monster.art_ready`, then `workflow.completed`.

### GET /monsters
List monsters with paging, filtering, and sorting.
**Query params:**
- `limit?: number` (1–1000)
- `offset?: number` (default `0`)
- `filter?: string` — `all | with_art | without_art` (default `all`)
- `sort?: string` — `newest | oldest | name | species` (default `newest`)

**Success:**
```json
{
  "success": true,
  "monsters": [MonsterObject],
  "total": number,
  "count": number,
  "pagination": {
    "limit": number,
    "offset": number,
    "has_more": boolean,
    "next_offset": number|null,
    "prev_offset": number|null
  },
  "filters_applied": { "filter_type": string, "sort_by": string }
}
```
**Error (400):** invalid filter/sort/limit/offset.

### GET /monsters/:id
**Success:** `{ "success": true, "monster": MonsterObject }`
**Error (404):** `{ "success": false, "error": "Monster not found", "monster": null }`

### GET /monsters/:id/memories
The monster's permanent memories of the party, oldest first (its life in
order). Written by battles, dialogues, sneaks, camps, growth reflections,
returns — and home-base chats (kinds `confided`, `grew_closer`,
`shared_lore`, `learned_fact`, `voiced_wish`, extracted from conversation
with `details.source: "home_chat"`; see [Chat](chat.md)) — see the
*Memory & evolution* section in [Dungeon & Battle](dungeon-and-battle.md).
Live additions arrive via the `monster.memory_added` SSE event. Synchronous.
**Success:** `{ "success": true, "monster_id": number, "memories": [MemoryObject] }`
`MemoryObject`: `{ id, monster_id, run_id, kind, content, details: { run_number?, source?, by?, with?, location?, ... }, created_at }`
**Error (404):** `{ "success": false, "error": "Monster not found" }`

### POST /monsters/:id/evolve
Queues an `evolve_monster` workflow — the home-base evolution ceremony. The
monster must be FOLLOWING (or in the party), fully generated, and the party
must not be mid-run. Same monster id throughout: memories, chat thread,
abilities, and party status all survive; the prior form is snapshotted as an
`EvolutionObject` (see [Data Models](data-models.md)).
**Request:** `{ "guidance"?: string }` — optional whisper (≤200 chars)
steering the evolved form; blank = pure history.
**Success:** `{ "success": true, "workflow_id": number }`
**Error (400):** `{ "success": false, "error": string }` (mid-run, not
following, still generating, guidance too long)
Results arrive via SSE: `monster.updated` + `monster.evolved` (identity,
stats +25/15/10% by stage, rarity one tier up, healed) →
`workflow.update step: emit_generation_id` (`evolution_text_generation_id`
streams the ceremony narration) → `monster.updated` per later stage
(persona shift, prose/appearance, ability rewords) →
`monster.ability_added` (optional signature ability) →
`monster.memory_added` (kind `evolved`) → `monster.art_ready` (regenerated
card art; skipped if image gen is disabled or the prose stage failed), then
`workflow.completed` with `{ monster, evolution, narrative, new_ability,
reworded_abilities, art_regenerated }`.

### GET /monsters/:id/evolutions
The monster's evolution lineage, oldest first (its forms in order).
Synchronous.
**Success:** `{ "success": true, "monster_id": number, "evolutions": [EvolutionObject] }`
**Error (404):** `{ "success": false, "error": "Monster not found" }`

### GET /monsters/stats
Aggregate stats over the collection.
**Query params:** `filter?: string` — `all | with_art | without_art` (default `all`)
**Success:**
```json
{
  "success": true,
  "filter_applied": string,
  "stats": {
    "total_monsters": number,
    "total_abilities": number,
    "avg_abilities_per_monster": number,
    "with_card_art": number,
    "without_card_art": number,
    "card_art_percentage": number,
    "unique_species": number,
    "species_breakdown": { "[species]": number },
    "newest_monster": MonsterObject|null,
    "oldest_monster": MonsterObject|null
  }
}
```

### POST /monsters/:id/abilities
Queues a `generate_ability` workflow that adds one new ability to the monster.
**Success:** `{ "success": true, "workflow_id": number }`
**Error (500):** `{ "success": false, "error": string }`
Result arrives via SSE: `monster.ability_added`, then `workflow.completed`.

### GET /monsters/card-art/:path
Serves a card-art image file directly (not JSON). `:path` is the monster's
`card_art.relative_path`, e.g. `monster_card_art/00000042.png`.
**Success:** binary image data.
**Error (400):** `{ "success": false, "error": "Invalid image path" }` (path traversal blocked)
**Error (404):** `{ "success": false, "error": "Image not found" }`

## Roster: Following & Party (`/api/game-state`)

### GET /game-state
The high-level save summary the title screen reads.
**Success:** `{ "success": true, "first_run_complete": boolean, "has_world_data": boolean, "has_player": boolean, "player_monster_id": number|null, "following_count": number, "party_count": number, "in_dungeon": boolean }`
`first_run_complete` gates the title screen's Continue button;
`has_world_data` drives New Game's erase-the-world confirmation.

### POST /game-state/new-game
The New Game promise: erases every game-domain table (monsters, chats,
memories, evolutions, items, keepsakes, runs, party, globals) in one
transaction. Developer log tables and art files on disk survive.
Refuses while any workflow is pending or processing. The frontend
confirms with the player BEFORE calling.
**Success:** `{ "success": true, "message": string, "deleted_rows": { table: count } }`
**Error (400):** `{ "success": false, "error": string }` (workflows still busy)

### POST /game-state/reset
Clears the party, the following list, and all `global_variables` (dungeon
and battle state). Testing/dev convenience — `new-game` above is the
player-facing full wipe.
**Success:** `{ "success": true, "message": string, "game_state": GameStateObject }`

### GET /game-state/following
**Success:** `{ "success": true, "following_monsters": FollowingMonstersObject }`

### POST /game-state/following/add
**Request:** `{ "monster_id": number }`
**Success:** `{ "success": true, "message": string, ... }`
**Error (400):** `{ "success": false, "error": string, ... }`
Note: battle recruitment (`enemies_join`) adds monsters to this list on the
backend directly — see [Dungeon & Battle](dungeon-and-battle.md).

### POST /game-state/following/remove
**Request:** `{ "monster_id": number }` (also removes them from the party if present)
**Success:** `{ "success": true, "message": string, ... }`

### GET /game-state/party
**Success:** `{ "success": true, "active_party": PartyObject }`

### POST /game-state/party/set
Sets the active party from monsters that are already following you.
The player character is filtered out quietly (always in the party
already); what remains must fit the companion cap (3 beside a player,
4 on a pre-character world).
**Request:** `{ "monster_ids": number[] }`
**Success:** `{ "success": true, "message": string, "active_party": PartyObject }`
**Error (400):** `{ "success": false, "error": string, ... }` (e.g. party size limits, monsters not following)

## Player Character (`/api/player`)

The player's own character: a real monster row that is always in the
party, chats AS the player, and is built by the character-creation
wizard. Async endpoints answer `{ workflow_id }`; results arrive over
SSE as `workflow.completed` events carrying the workflow result.

### GET /player
**Success:** `{ "success": true, "player": MonsterObject }`
**Error (404):** `{ "success": false, "error": "No player character exists yet", "player": null }`

### POST /player/options
Options for ONE creation field, conditioned on the choices so far.
**Request:** `{ "field": "kind"|"name"|"background"|"personality"|"wish"|"appearance", "choices": { field: string } }`
**Success:** `{ "success": true, "workflow_id": number }` — the workflow
result carries `{ field, options: string[] }`.

### POST /player/create
The finalize: the player's answers become their character (staged like
monster generation; the wish and appearance text are kept verbatim).
Refuses when a complete character exists; a half-built one from a
failed attempt is discarded and rebuilt.
**Request:** `{ "name", "kind", "background", "personality", "wish", "role", "appearance" }` (name + kind required)
**Success:** `{ "success": true, "workflow_id": number }` — steps
`building_identity → shaping_persona → writing_story →
adding_first_ability → adding_second_ability`, standard `monster.*`
events along the way.

### POST /player/portrait/generate
Paints ONE portrait candidate from the description (default: the
character's own appearance text). The result carries `image_path` as a
CANDIDATE — nothing becomes the portrait until selected.
**Request:** `{ "description": string }`
**Success:** `{ "success": true, "workflow_id": number }`
**Error (400):** image generation disabled (uploads still work).

### POST /player/portrait/select
**Request:** `{ "image_path": string }` (must live under
`player_card_art/` or `player_uploads/` and exist)
**Success:** `{ "success": true, "image_path": string, "monster": MonsterObject }`

### POST /player/portrait/upload
Multipart upload (`image` file field): png/jpg/webp, max 8MB,
magic-byte checked. Uploads auto-select as the portrait and are served
by the card-art route like any other image.
**Success:** `{ "success": true, "image_path": string, "monster": MonsterObject }`
