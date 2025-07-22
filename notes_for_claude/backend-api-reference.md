# Backend API Reference - AI Consumption

## API Base URL
- Development: `http://localhost:5000/api`

## Standard Response Format
**Success:** `{success: true, ...data}`  
**Error:** `{success: false, error: string, ...context}`

## Monster Management

#### POST /monsters/generate
**Request:** `{prompt_name?: string}`  
**Default:** `prompt_name: "detailed_monster"`  
**Success:** 
```json
{
  "success": true,
  "monster": MonsterObject,
  "generation_id": number,
  "generation_stats": {
    "tokens": number,
    "duration": number,
    "abilities_generated": number,
    "card_art_generated": boolean
  }
}
```
**Error (500):** `{success: false, error: string, monster: null}`

#### GET /monsters
**Request:** Query parameters:
- `limit?: number` (1-1000, default: 50)
- `offset?: number` (0+, default: 0)
- `filter?: string` (`all|with_art|without_art`, default: `all`)
- `sort?: string` (`newest|oldest|name|species`, default: `newest`)

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
  "filters_applied": {
    "filter_type": string,
    "sort_by": string
  }
}
```
**Error (400):** `{success: false, error: "Invalid filter parameter - must be: all, with_art, or without_art"}`

#### GET /monsters/:id
**Parameters:** `id: number`  
**Success:** `{success: true, monster: MonsterObject}`  
**Error (404):** `{success: false, error: "Monster not found", monster: null}`

#### GET /monsters/templates
**Success:** `{success: true, templates: {[template_name: string]: string}}`

#### GET /monsters/stats
**Request:** Query parameters:
- `filter?: string` (`all|with_art|without_art`, default: `all`)

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
    "species_breakdown": {[species: string]: number},
    "newest_monster": MonsterObject|null,
    "oldest_monster": MonsterObject|null
  },
  "context": {
    "all_monsters_count": number,
    "all_monsters_with_art": number,
    "overall_card_art_percentage": number
  }
}
```

#### POST /monsters/:id/abilities
**Parameters:** `id: number`  
**Success:** `{success: true, ability: AbilityObject, generation_id: number, monster_id: number}`  
**Error (500):** `{success: false, error: string, ability: null, monster_id: number}`

#### GET /monsters/:id/abilities
**Parameters:** `id: number`  
**Success:** `{success: true, abilities: [AbilityObject], count: number, monster_id: number}`  
**Error (404):** `{success: false, error: "Monster not found", abilities: [], count: 0, monster_id: number}`

#### POST /monsters/:id/card-art
**Parameters:** `id: number`  
**Success:** `{success: true, image_path: string, generation_id: number}`  
**Error (500):** `{success: false, error: string}`

#### GET /monsters/:id/card-art
**Parameters:** `id: number`  
**Success:** `{success: true, monster_id: number, card_art: CardArtObject}`  
**Error (404):** `{success: false, error: string, monster_id: number}`

#### GET /monsters/card-art/:path
**Parameters:** `path: string`  
Serves image files directly.  
**Success:** Binary image data  
**Error (404):** `{success: false, error: "Image not found"}`  
**Error (400):** `{success: false, error: "Invalid image path"}`

## Game State Management

#### GET /game-state
**Success:** `{success: true, ...GameStateObject}`

#### POST /game-state/reset
**Success:** `{success: true, message: "Game state reset to initial values", game_state: GameStateObject}`

#### POST /game-state/following/add
**Request:** `{monster_id: number}`  
**Success:** `{success: true, message: string, monster: MonsterObject, following_count: number}`  
**Error (400):** `{success: false, error: string, following_count: number}`

#### POST /game-state/following/remove
**Request:** `{monster_id: number}`  
**Success:** `{success: true, message: string, following_count: number, party_count: number}`  
**Error (400):** `{success: false, error: string, following_count: number}`

#### GET /game-state/following
**Success:** `{success: true, following_monsters: FollowingMonstersObject}`

#### POST /game-state/party/set
**Request:** `{monster_ids: number[]}`  
**Success:** `{success: true, message: string, active_party: PartyObject}`  
**Error (400):** `{success: false, error: string, party_count: number}`

#### GET /game-state/party
**Success:** `{success: true, active_party: PartyObject}`

#### GET /game-state/party/ready
**Success:** `{success: true, ready_for_dungeon: boolean, party_summary: string, message: string}`

## Dungeon System

#### POST /dungeon/enter
**Success:** 
```json
{
  "success": true,
  "dungeon_entered": true,
  "entry_text": string,
  "location": LocationObject,
  "doors": [DoorObject, DoorObject, ExitDoorObject],
  "party_summary": string,
  "message": string
}
```
**Error (400):** `{success: false, error: "No active party set. Add monsters to your party before entering the dungeon.", ready_for_dungeon: false}`

#### POST /dungeon/choose-door
**Request:** `{door_choice: string}`  
**Location Door Success:**
```json
{
  "success": true,
  "choice_made": string,
  "event_text": string,
  "new_location": LocationObject,
  "new_doors": [DoorObject, DoorObject, ExitDoorObject],
  "continue_button": true,
  "in_dungeon": true
}
```
**Exit Door Success:**
```json
{
  "success": true,
  "choice_made": "Exit the Dungeon",
  "exit_text": string,
  "dungeon_completed": true,
  "in_dungeon": false,
  "return_to_home_button": true,
  "message": string
}
```
**Error (400):** `{success: false, error: string, in_dungeon: boolean}`

#### GET /dungeon/state
**Success (In Dungeon):** 
```json
{
  "success": true,
  "in_dungeon": true,
  "state": {
    "current_location": LocationObject,
    "available_doors": [DoorObject],
    "last_event_text": string,
    "party_summary": string
  },
  "party_summary": string
}
```
**Success (Not In Dungeon):** `{success: true, in_dungeon: false, state: null, message: string}`

#### GET /dungeon/status
**Success (In Dungeon):** `{success: true, in_dungeon: true, location_name: string, party_summary: string, door_count: number, message: string}`  
**Success (Home Base):** `{success: true, in_dungeon: false, message: "Currently at home base"}`

## Generation System

#### GET /generation/status
**Success:** 
```json
{
  "success": true,
  "data": {
    "llm_status": object,
    "image_status": object,
    "queue_info": object,
    "generation_types_supported": string[]
  }
}
```

#### GET /generation/logs
**Request:** Query parameters:
- `limit?: number` (1-100, default: 20)
- `type?: string` (`llm|image`)
- `status?: string` (`pending|generating|completed|failed`)

**Success:** 
```json
{
  "success": true,
  "data": {
    "logs": [GenerationLogObject],
    "count": number,
    "filters": {
      "type": string|null,
      "status": string|null,
      "limit": number
    }
  }
}
```

#### GET /generation/logs/:id
**Parameters:** `id: number`  
**Success:** `{success: true, data: GenerationLogObject}`  
**Error (404):** `{success: false, error: "Generation log not found"}`

#### GET /generation/stats
**Success:** 
```json
{
  "success": true,
  "data": {
    "overall": object,
    "llm": object,
    "image": object
  }
}
```

## Streaming & SSE

#### GET /streaming/llm-events
Server-Sent Events endpoint. Returns event stream with 30-second keep-alive pings. Supports both LLM and image generation events.

#### GET /streaming/connections
**Success:**
```json
{
  "active_connections": number,
  "event_types": string[],
  "streaming_method": "event_driven_blocking",
  "efficiency": "Only sends data when events occur (no polling!)",
  "supported_generation_types": ["llm", "image"]
}
```

## Testing & System

#### GET /health
**Success:** `{status: "healthy", message: string, api_version: "2.0"}`

#### GET /game/status
**Success:** 
```json
{
  "game_name": "Monster Hunter Game",
  "version": string,
  "status": "development",
  "features": {
    "monster_generation": boolean,
    "ability_generation": boolean,
    "image_generation": boolean,
    "streaming_display": boolean,
    "unified_queue": boolean,
    "gpu_acceleration": boolean,
    "battle_system": boolean,
    "chat_system": boolean,
    "save_system": boolean
  },
  "ai_systems": object
}
```

#### GET /game_tester/tests
**Success:** `string[]`

#### GET /game_tester/run/:test_name
**Parameters:** `test_name: string`  
**Success:** `{success: true, test_name: string, output: string, message: string}`  
**Error (404):** `{success: false, error: string, output: ""}`  
**Error (500):** `{success: false, error: string, traceback: string, output: string}`

## Data Models

### MonsterObject
```json
{
  "id": number,
  "name": string,
  "species": string,
  "description": string,
  "backstory": string,
  "stats": {
    "max_health": number,
    "current_health": number,
    "attack": number,
    "defense": number,
    "speed": number
  },
  "personality_traits": string[],
  "abilities": [AbilityObject],
  "ability_count": number,
  "card_art": CardArtObject,
  "created_at": string,
  "updated_at": string
}
```

### AbilityObject
```json
{
  "id": number,
  "monster_id": number,
  "name": string,
  "description": string,
  "ability_type": string,
  "created_at": string
}
```

### CardArtObject
```json
{
  "has_card_art": boolean,
  "relative_path": string|null,
  "exists": boolean,
  "url": string|null
}
```

### GameStateObject
```json
{
  "following_monsters": FollowingMonstersObject,
  "active_party": PartyObject,
  "dungeon_state": {
    "in_dungeon": boolean,
    "current_state": object|null
  },
  "game_status": "home_base"|"in_dungeon"
}
```

### FollowingMonstersObject
```json
{
  "ids": number[],
  "count": number,
  "details": [MonsterObject]
}
```

### PartyObject
```json
{
  "ids": number[],
  "count": number,
  "details": [MonsterObject]
}
```

### LocationObject
```json
{
  "name": string,
  "description": string
}
```

### DoorObject
```json
{
  "id": string,
  "type": "location"|"exit",
  "name": string,
  "description": string
}
```

### GenerationLogObject
```json
{
  "id": number,
  "generation_type": "llm"|"image",
  "prompt_type": string,
  "prompt_name": string,
  "status": "pending"|"generating"|"completed"|"failed",
  "priority": number,
  "duration_seconds": number|null,
  "attempts_used": number,
  "max_attempts": number,
  "is_completed": boolean,
  "is_failed": boolean,
  "llm_data": object|null,
  "image_data": object|null
}
```

## SSE Event Types

**Connection Events:**
- `sse.connected`: `{message: string}`
- `ping`: `{timestamp: number}`

**LLM Generation Events:**
- `generation_started`: `{item: object, generation_id: number}`
- `generation_update`: `{generation_id: number, partial_text: string, tokens_so_far: number}`
- `generation_completed`: `{item: object, generation_id: number, result: object}`
- `generation_failed`: `{item: object, generation_id: number, error: string}`
- `queue_update`: `{action: string, item: object, queue_size: number}`

**Image Generation Events:**
- `image.generation.started`: `{item: object, generation_id: number}`
- `image.generation.update`: `{generation_id: number, progress_message: string}`
- `image.generation.completed`: `{item: object, generation_id: number, result: object}`
- `image.generation.failed`: `{item: object, generation_id: number, error: string}`

## Common Error Patterns

**Parameter Validation:**
- `"Invalid monster ID - must be a positive integer"`
- `"Invalid filter parameter - must be: all, with_art, or without_art"`
- `"Invalid sort parameter - must be: newest, oldest, name, species"`
- `"monster_ids must be a list"`
- `"Limit must be between 1 and 1000"`
- `"Offset must be 0 or greater"`

**Business Logic:**
- `"Monster not found"`
- `"Monster {name} is already following you"`
- `"Monster {id} is not following you"`
- `"Active party cannot exceed 4 monsters"`
- `"Monsters [ids] are not following you"`
- `"No active party set. Add monsters to your party before entering the dungeon."`
- `"Not currently in a dungeon"`
- `"Invalid door choice. Available: [choices]"`

**Generation Errors:**
- `"Monster generation failed"`
- `"Ability generation failed"`
- `"Image generation failed"`
- `"Template not found"`
- `"Generation log not found"`