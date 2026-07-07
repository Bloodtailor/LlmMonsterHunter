# Monsters & Roster API

Monster generation and library, plus the two roster lists — **following
monsters** (everyone you've collected) and the **active party** (the up-to
handful you take into a dungeon).

See [Data Models](data-models.md) for `MonsterObject`, `AbilityObject`, etc.
Generation endpoints are async — see the workflow model in the
[index](../backend-api-reference.md).

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
Complete current game state.
**Success:** `{ "success": true, ...GameStateObject }`

### POST /game-state/reset
Clears the party, the following list, and all `global_variables` (dungeon
and battle state). Testing/dev convenience.
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
**Request:** `{ "monster_ids": number[] }`
**Success:** `{ "success": true, "message": string, "active_party": PartyObject }`
**Error (400):** `{ "success": false, "error": string, ... }` (e.g. party size limits, monsters not following)
