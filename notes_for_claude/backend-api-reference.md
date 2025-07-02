# Backend API Reference for Frontend - ENHANCED PAGINATION

## API Base URL
- Development: `http://localhost:5000/api`

## Standard Response Format
**Success:** `{success: true, ...data}`  
**Error:** `{success: false, error: string, ...context}`

## Core API Endpoints

### Monster Management

#### POST /monsters/generate
**Request:** `{prompt_name?, generate_card_art?}`  
**Success:** `{success: true, monster: MonsterObject, generation_stats: {tokens, duration, abilities_generated, card_art_generated}}`  
**Error:** `{success: false, error: string, monster: null}`

#### GET /monsters - ENHANCED WITH SERVER-SIDE FILTERING & SORTING
**Request:** Query params:
- `limit=12` (1-1000, default: 50) - Number of monsters per page
- `offset=24` (0+, default: 0) - Number of monsters to skip  
- `filter=with_art` (`all|with_art|without_art`, default: `all`) - Card art filter
- `sort=name` (`newest|oldest|name|species`, default: `newest`) - Sort order

**Examples:**
- `/monsters?limit=12&offset=0&filter=with_art&sort=name` - First 12 monsters with art, sorted by name
- `/monsters?limit=24&offset=48&sort=species` - Third page of 24 monsters, sorted by species
- `/monsters?filter=without_art&sort=oldest` - All monsters without art, oldest first

**Success Response:** 
```json
{
  "success": true,
  "monsters": [MonsterObject],
  "total": 101,
  "count": 12,
  "pagination": {
    "limit": 12,
    "offset": 24,
    "has_more": true,
    "next_offset": 36,
    "prev_offset": 12
  },
  "filters_applied": {
    "filter_type": "with_art",
    "sort_by": "name"
  }
}
```

**Error Response (400):** `{success: false, error: "Invalid filter parameter - must be: all, with_art, or without_art"}`

#### GET /monsters/:id
**Success:** `{success: true, monster: MonsterObject}`  
**Error:** `{success: false, error: "Monster not found", monster: null}`

#### POST /monsters/:id/abilities
**Success:** `{success: true, ability: AbilityObject, generation_stats}`

#### GET /monsters/:id/abilities
**Success:** `{success: true, abilities: [AbilityObject], count: number}`

#### POST /monsters/:id/card-art
**Success:** `{success: true, image_path: string, execution_time: number}`

#### GET /monsters/card-art/:path
Serves image files directly.

### Monster Statistics - ENHANCED

#### GET /monsters/stats - ENHANCED WITH FILTERING
**Request:** Query params:
- `filter=with_art` (`all|with_art|without_art`, default: `all`) - Apply same filtering as monsters list

**Examples:**
- `/monsters/stats` - All monsters statistics
- `/monsters/stats?filter=with_art` - Statistics for only monsters with card art
- `/monsters/stats?filter=without_art` - Statistics for only monsters without card art

**Success Response:**
```json
{
  "success": true,
  "filter_applied": "with_art",
  "stats": {
    "total_monsters": 67,
    "total_abilities": 134,
    "avg_abilities_per_monster": 2.0,
    "with_card_art": 67,
    "without_card_art": 0,
    "card_art_percentage": 100.0,
    "unique_species": 18,
    "species_breakdown": {
      "Fire Dragon": 5,
      "Forest Guardian": 3,
      "Ice Sprite": 2
    },
    "newest_monster": MonsterObject,
    "oldest_monster": MonsterObject
  },
  "context": {
    "all_monsters_count": 101,
    "all_monsters_with_art": 67,
    "overall_card_art_percentage": 66.3
  }
}
```

**Note:** When `filter != 'all'`, response includes `context` object showing overall database statistics for comparison.

### Generation System

#### GET /generation/status
**Success:** `{success: true, data: {llm_status, image_status, queue_info, generation_types_supported}}`

#### GET /generation/logs
**Request:** Query params: `limit?, type?, status?`  
**Success:** `{success: true, data: {logs: [GenerationLogObject], count, filters}}`

#### GET /generation/logs/:id
**Success:** `{success: true, data: GenerationLogObject}`

#### GET /generation/stats
**Success:** `{success: true, data: {overall, llm, image}}`

#### POST /generation/test/llm
**Request:** `{prompt: string}`  
**Success:** Standard text generation response

#### POST /generation/test/image
**Request:** `{description: string}`  
**Success:** Standard image generation response

### Streaming & SSE

#### GET /streaming/llm-events
Server-Sent Events endpoint. Returns event stream.

#### POST /streaming/add
**Request:** `{prompt: string}`  
**Success:** `{success: true, generation_id, message}`

#### POST /streaming/add-image
**Request:** `{monster_description, monster_name?, monster_species?}`  
**Success:** `{success: true, generation_id, message}`

#### GET /streaming/connections
Debug endpoint showing active connections and event types.

### Testing & System

#### GET /health
**Success:** `{status: "healthy", message: string, api_version: "2.0"}`

#### GET /game/status
**Success:** `{game_name, version, status, features: {monster_generation, ability_generation, image_generation, etc.}, ai_systems}`

#### GET /test/generation
**Success:** `{llm_test: "success"|"failed", image_test: "success"|"queued"|"disabled", overall_success: boolean}`

#### GET /game_tester/tests
**Success:** `[test_file_names]`

#### GET /game_tester/run/:test_name
**Success:** `{success: true, test_name, output, message}`

## Data Models

### MonsterObject
```json
{
  "id": 1,
  "name": "Thornwick",
  "species": "Forest Guardian", 
  "description": "A mystical creature...",
  "backstory": "Born in the ancient woods...",
  "stats": {"max_health": 120, "current_health": 120, "attack": 25, "defense": 18, "speed": 15},
  "personality_traits": ["wise", "protective"],
  "abilities": [AbilityObject],
  "ability_count": 2,
  "card_art": {"has_card_art": true, "relative_path": "monster_card_art/00000001.png", "exists": true, "url": "/api/monsters/card-art/monster_card_art/00000001.png"},
  "created_at": "2025-01-01T00:00:00",
  "updated_at": "2025-01-01T00:00:00"
}
```

### AbilityObject
```json
{
  "id": 1,
  "monster_id": 1,
  "name": "Nature's Blessing",
  "description": "Heals nearby allies with forest magic",
  "ability_type": "support",
  "created_at": "2025-01-01T00:00:00"
}
```

### GenerationLogObject
```json
{
  "id": 1,
  "generation_type": "llm|image",
  "prompt_type": "monster_generation|ability_generation|image_generation",
  "prompt_name": "detailed_monster|generate_ability|monster_generation",
  "status": "pending|generating|completed|failed",
  "priority": 5,
  "duration_seconds": 2.5,
  "attempts_used": 1,
  "max_attempts": 3,
  "is_completed": true,
  "is_failed": false,
  "llm_data": {"response_tokens": 150, "tokens_per_second": 45, "parse_success": true},
  "image_data": {"image_path": "monster_card_art/00000001.png", "has_image": true}
}
```

## SSE Event Types

**Connection Events:**
- `sse.connected`: `{message: "Connected to Monster Hunter Game"}`
- `ping`: `{timestamp: number}` (keep-alive every 30s)

**LLM Generation Events:**
- `generation_started`: `{item: QueueItemObject, generation_id: number}`
- `generation_update`: `{generation_id: number, partial_text: string, tokens_so_far: number}`  
- `generation_completed`: `{item: QueueItemObject, generation_id: number, result: object}`
- `generation_failed`: `{item: QueueItemObject, generation_id: number, error: string}`
- `queue_update`: `{action: "added", item: QueueItemObject, queue_size: number}`

**Image Generation Events:**
- `image.generation.started`: `{item: QueueItemObject, generation_id: number}`
- `image.generation.update`: `{generation_id: number, progress_message: string}`
- `image.generation.completed`: `{item: QueueItemObject, generation_id: number, result: object}`
- `image.generation.failed`: `{item: QueueItemObject, generation_id: number, error: string}`

### QueueItemObject
```json
{
  "generation_id": 1,
  "generation_type": "llm|image", 
  "priority": 5,
  "status": "pending|processing|completed|failed",
  "created_at": "2025-01-01T00:00:00",
  "started_at": "2025-01-01T00:00:00",
  "completed_at": "2025-01-01T00:00:00",
  "result": {},
  "error": "string"
}
```

## Enhanced Pagination Features

### Server-Side Benefits
- **Performance:** Only requested monsters loaded from database
- **Scalability:** Supports thousands of monsters efficiently  
- **Filtering:** Card art filtering done at database level
- **Sorting:** All sorting done server-side for consistency

### Query Parameter Validation
- **limit:** 1-1000 (defaults to 50, max enforced)
- **offset:** 0+ (negative values reset to 0)
- **filter:** Enum validation with clear error messages
- **sort:** Enum validation with clear error messages

### Pagination Response Fields
- **total:** Total monsters matching filter (important for UI)
- **count:** Monsters returned in this request
- **has_more:** Boolean for "Load More" buttons
- **next_offset:** Ready-to-use offset for next page (null if no more)
- **prev_offset:** Ready-to-use offset for previous page (null if first page)

### Frontend Implementation Patterns

#### Basic Pagination
```javascript
// Get first page of 12 monsters
const response = await fetch('/api/monsters?limit=12&offset=0');

// Get next page using returned next_offset
const nextResponse = await fetch(`/api/monsters?limit=12&offset=${response.pagination.next_offset}`);
```

#### With Filtering and Sorting
```javascript
// Monsters with card art, sorted by name, 24 per page
const response = await fetch('/api/monsters?limit=24&filter=with_art&sort=name');

// Count just monsters with card art
const stats = await fetch('/api/monsters/stats?filter=with_art');
```

#### Infinite Scroll Pattern
```javascript
let offset = 0;
const limit = 12;

async function loadMoreMonsters() {
  const response = await fetch(`/api/monsters?limit=${limit}&offset=${offset}`);
  
  // Add monsters to UI
  monsters.push(...response.monsters);
  
  // Update offset for next request
  if (response.pagination.has_more) {
    offset = response.pagination.next_offset;
  }
  
  return response.pagination.has_more;
}
```

## Error Patterns

**Enhanced Error Responses:**
- `"Invalid limit or offset parameter - must be integers"` (400)
- `"Invalid filter parameter - must be: all, with_art, or without_art"` (400) 
- `"Invalid sort parameter - must be: newest, oldest, name, or species"` (400)

**Common Errors:**
- `"Monster not found"` (404)
- `"Template not found: template_name"` 
- `"Failed to save to database"`
- `"Image generation is disabled"` (when ENABLE_IMAGE_GENERATION=false)
- `"ComfyUI server not running"`
- `"Parsing failed after N attempts"`
- `"Generation timed out after N seconds"`

**Error Response Variations:**
- Sometimes includes `generation_id` for tracking
- Sometimes includes `help` field with setup instructions
- Image errors may include `reason: "DISABLED"|"SERVER_DOWN"|"TIMEOUT"`

## Configuration Affecting Frontend

### Environment Variables
- `ENABLE_IMAGE_GENERATION`: `"true"|"false"` - Controls card art generation
- `FLASK_DEBUG`: `"true"|"false"` - Affects error verbosity

### Feature Flags (from /game/status)
```json
{
  "monster_generation": true,
  "ability_generation": true, 
  "image_generation": false,  // depends on ENABLE_IMAGE_GENERATION + ComfyUI
  "streaming_display": true,
  "unified_queue": true,
  "gpu_acceleration": true,  // depends on LLM config
  "battle_system": false,
  "chat_system": false,
  "save_system": true
}
```

## Development Notes

**Image Generation:**
- Requires `ENABLE_IMAGE_GENERATION=true` + ComfyUI server running
- Images saved to organized folders based on `prompt_type`
- Card art endpoint `/monsters/card-art/:path` serves files directly

**Async Behavior:**
- Most generation endpoints support `wait_for_completion` parameter
- Use SSE events to track progress when `wait_for_completion=false`
- Queue processes both LLM and image requests in priority order

**Enhanced Pagination:**
- Standard format: `{limit, offset, total, has_more, next_offset, prev_offset}`
- Server-side filtering and sorting for performance
- Query parameter validation with descriptive error messages
- Supports up to 1000 monsters per request for bulk operations