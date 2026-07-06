# Generation & System API

Introspection endpoints for the AI generation queue, plus health and the
in-app test runner. These are read/debug tools — the gameplay endpoints that
*create* generations live in [Monsters & Roster](monsters-and-roster.md) and
[Dungeon & Battle](dungeon-and-battle.md).

## Generation logs (`/api/generation`)

Every LLM and image generation is recorded as a `GenerationLogObject`
(see [Data Models](data-models.md)). These endpoints read that log — useful
for debugging what the model actually produced.

### GET /generation/logs
**Query params (all optional):**
- `limit?: number` (hard cap 1000), `offset?: number`
- `generation_type?: string` — `llm | image`
- `status?: string` — `pending | generating | completed | failed`
- `prompt_type?: string` — exact match
- `prompt_name?: string` — substring match (case-insensitive); e.g. `monster_dialogue_turn`, `action_resolution`
- `priority?: number`
- `sort_by?: string` — default `id`; comma-separated fields allowed
- `sort_order?: string` — `asc | desc` (default `desc`)

**Success:**
```json
{
  "success": true,
  "data": {
    "logs": [GenerationLogObject],
    "count": number,          // total matching (for pagination)
    "returned_count": number, // in this page
    "filters": { ...echoed filter values }
  }
}
```
Tip: to inspect what a specific game prompt produced, filter by
`prompt_name` — every template name is usable here (`path_choices`,
`contextual_monster`, `monster_question`, `monster_dialogue_turn`,
`look_around`, `camp_scene`, `sneak_attempt`, `dungeon_ability_use`,
`next_turn`, `enemy_turn`, `freeform_action_resolution`, `battle_talk`,
`action_resolution`, `battle_victory`, `battle_defeat`, …).

### GET /generation/log-options
Available filter/sort options, with `prompt_type` and `prompt_name` queried
live from the database.
**Success:**
```json
{
  "success": true,
  "data": {
    "filter_options": {
      "generation_type": ["llm", "image"],
      "status": ["pending", "generating", "completed", "failed"],
      "priority": [1..10],
      "prompt_type": string[],
      "prompt_name": string[]
    },
    "sort_options": {
      "fields": ["id", "generation_type", "prompt_type", "prompt_name", "status", "priority", "duration_seconds", "start_time"],
      "orders": ["asc", "desc"]
    }
  }
}
```

## System

### GET /health
**Success:** `{ "status": "healthy", "message": string, "api_version": "2.0" }`
(Note: no `success` field — this is the one bare endpoint.)

## Test runner (`/api/game_tester`)

Runs Python test files from the backend test directory and returns their
captured output. Used by the developer screens in the frontend.

### GET /game_tester/tests
**Success:** `string[]` (available test file names) — raw array, not wrapped.

### GET /game_tester/run/:test_name
**Success:** `{ "success": true, "test_name": string, "output": string, "message": string }`
**Error (404):** `{ "success": false, "error": string, "output": "" }`
**Error (500):** `{ "success": false, "error": string, "traceback": string, "output": string }`
