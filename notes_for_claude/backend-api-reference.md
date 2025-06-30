# Backend API Reference for Frontend

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

#### GET /monsters
**Request:** Query params: `limit?, offset?`  
**Success:** `{success: true, monsters: [MonsterObject], total: number, pagination: {limit, offset, has_more}}`

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

## Error Patterns

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

## Development Notes

**Image Generation:**
- Requires `ENABLE_IMAGE_GENERATION=true` + ComfyUI server running
- Images saved to organized folders based on `prompt_type`
- Card art endpoint `/monsters/card-art/:path` serves files directly

**Async Behavior:**
- Most generation endpoints support `wait_for_completion` parameter
- Use SSE events to track progress when `wait_for_completion=false`
- Queue processes both LLM and image requests in priority order

**Pagination:**
- Standard format: `{limit, offset, has_more}`
- Default limit: 50, max limit: 100