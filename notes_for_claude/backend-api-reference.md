# Backend API Reference for Frontend - ENHANCED WITH DUNGEON SYSTEM

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

### 🎮 Game State Management - NEW

#### GET /game-state
**Success:** `{success: true, game_state: GameStateObject}`  
**Error:** `{success: false, error: string}`

#### POST /game-state/reset
**Success:** `{success: true, message: "Game state reset to initial values", game_state: GameStateObject}`

#### POST /game-state/following/add
**Request:** `{monster_id: number}`  
**Success:** `{success: true, message: "Monster name is now following you", monster: MonsterObject, following_count: number}`  
**Error:** `{success: false, error: "Monster 123 not found", following_count: number}`

#### POST /game-state/following/remove  
**Request:** `{monster_id: number}`  
**Success:** `{success: true, message: "Monster name is no longer following you", following_count: number, party_count: number}`

#### GET /game-state/following
**Success:** `{success: true, following_monsters: {ids: [number], count: number, details: [MonsterObject]}}`

#### POST /game-state/party/set
**Request:** `{monster_ids: [number, number, number]}`  
**Success:** `{success: true, message: "Active party set: Monster1, Monster2, Monster3", active_party: PartyObject}`  
**Error:** `{success: false, error: "Active party cannot exceed 4 monsters", party_count: number}`

#### GET /game-state/party
**Success:** `{success: true, active_party: PartyObject}`

#### GET /game-state/party/ready
**Success:** `{success: true, ready_for_dungeon: boolean, party_summary: string, message: string}`

### 🏰 Dungeon System - NEW

#### POST /dungeon/enter
**Description:** Enter dungeon with current active party. Generates atmospheric entry text, initial location, and 3 door choices.  
**Requirements:** Must have active party set (at least 1 monster)  
**Success:** 
```json
{
  "success": true,
  "dungeon_entered": true,
  "entry_text": "Generated atmospheric text about entering the dungeon...",
  "location": {
    "name": "Crystal Cavern", 
    "description": "Glowing crystals illuminate the chamber..."
  },
  "doors": [
    {
      "id": "location_1",
      "type": "location", 
      "name": "Ancient Library",
      "description": "Dusty tomes line the walls of this forgotten archive..."
    },
    {
      "id": "location_2",
      "type": "location",
      "name": "Echoing Chamber", 
      "description": "Your footsteps echo endlessly in this vast space..."
    },
    {
      "id": "exit",
      "type": "exit",
      "name": "Exit the Dungeon",
      "description": "A familiar stone stairway leading back to the surface..."
    }
  ],
  "party_summary": "Tanner, Luna, and Sparkles",
  "message": "Welcome to the dungeon! Choose your path wisely."
}
```
**Error:** `{success: false, error: "No active party set. Add monsters to your party before entering the dungeon.", ready_for_dungeon: false}`

#### POST /dungeon/choose-door
**Request:** `{door_choice: "location_1" | "location_2" | "exit"}`  
**Description:** Choose a door in the dungeon. Location doors generate event text and new location. Exit door generates exit text and returns to home base.

**Location Door Success:**
```json
{
  "success": true,
  "choice_made": "Ancient Library",
  "event_text": "Generated text about exploring the Ancient Library...",
  "new_location": {
    "name": "Forgotten Shrine",
    "description": "Candles flicker mysteriously in this sacred space..."
  },
  "new_doors": [DoorObject, DoorObject, ExitDoor],
  "continue_button": true,
  "in_dungeon": true
}
```

**Exit Door Success:**
```json
{
  "success": true,
  "choice_made": "Exit the Dungeon",
  "exit_text": "Generated text about successfully leaving the dungeon...",
  "dungeon_completed": true,
  "in_dungeon": false,
  "return_to_home_button": true,
  "message": "You have successfully exited the dungeon!"
}
```

**Error:** `{success: false, error: "Invalid door choice. Available: ['location_1', 'location_2', 'exit']", in_dungeon: true}`

#### GET /dungeon/state
**Success (In Dungeon):** 
```json
{
  "success": true,
  "in_dungeon": true,
  "state": {
    "current_location": LocationObject,
    "available_doors": [DoorObject],
    "last_event_text": "Text from last door choice...",
    "party_summary": "Tanner, Luna, and Sparkles"
  },
  "party_summary": "Tanner, Luna, and Sparkles"
}
```

**Success (Not In Dungeon):** `{success: true, in_dungeon: false, state: null, message: "Not currently in a dungeon"}`

#### GET /dungeon/status
**Description:** Quick status check for UI  
**Success (In Dungeon):** `{success: true, in_dungeon: true, location_name: "Crystal Cavern", party_summary: "Tanner, Luna, and Sparkles", door_count: 3, message: "Currently in Crystal Cavern with Tanner, Luna, and Sparkles"}`  
**Success (Home Base):** `{success: true, in_dungeon: false, message: "Currently at home base"}`

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

### Streaming & SSE

#### GET /streaming/llm-events
Server-Sent Events endpoint. Returns event stream.


#### GET /streaming/connections
Debug endpoint showing active connections and event types.

### Testing & System

#### GET /health
**Success:** `{status: "healthy", message: string, api_version: "2.0"}`

#### GET /game/status
**Success:** `{game_name, version, status, features: {monster_generation, ability_generation, image_generation, etc.}, ai_systems}`

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

### GameStateObject - NEW
```json
{
  "following_monsters": {
    "ids": [1, 2, 3, 4, 5],
    "count": 5,
    "details": [MonsterObject]
  },
  "active_party": {
    "ids": [1, 2, 3],
    "count": 3, 
    "details": [MonsterObject]
  },
  "dungeon_state": {
    "in_dungeon": false,
    "current_state": null
  },
  "game_status": "home_base"
}
```

### PartyObject - NEW
```json
{
  "ids": [1, 2, 3],
  "count": 3,
  "details": [MonsterObject]
}
```

### LocationObject - NEW
```json
{
  "name": "Crystal Cavern",
  "description": "Luminescent crystals cast dancing shadows across the chamber walls, creating an otherworldly atmosphere."
}
```

### DoorObject - NEW
```json
{
  "id": "location_1",
  "type": "location",
  "name": "Ancient Library", 
  "description": "Dusty tomes and scrolls line the walls of this forgotten archive, promising secrets of ages past."
}
```

### GenerationLogObject
```json
{
  "id": 1,
  "generation_type": "llm|image",
  "prompt_type": "monster_generation|ability_generation|image_generation|dungeon_generation",
  "prompt_name": "detailed_monster|generate_ability|monster_generation|entry_atmosphere|random_location",
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

## 🎮 Complete Game Flow Implementation Guide

### Home Base Screen Implementation
1. **Load Following Monsters:** `GET /game-state/following` 
2. **Display Monster Cards:** Show monster card art, names, species for selection
3. **Party Selection:** Allow clicking up to 4 monsters for party
4. **Set Active Party:** `POST /game-state/party/set` with selected monster IDs
5. **Check Readiness:** `GET /game-state/party/ready` before showing "Enter Dungeon" button
6. **Enter Dungeon Button:** `POST /dungeon/enter` when clicked

### Dungeon Screen Implementation
1. **Show Entry Text:** Display `entry_text` from dungeon enter response
2. **Show Current Location:** Display location name and description
3. **Show Party:** Display active party monster cards/names
4. **Show Door Choices:** Render 3 buttons for door choices
5. **Handle Door Click:** `POST /dungeon/choose-door` with selected door ID
6. **Show Event Text:** Display event text or exit text based on choice
7. **Update Location:** Show new location and doors (if not exiting)
8. **Handle Exit:** Return to home base screen when exit is chosen

### Game State Management
- **Reset Game:** `POST /game-state/reset` for testing/debugging
- **Add Test Monsters:** `POST /game-state/following/add` for development
- **Check Dungeon Status:** `GET /dungeon/status` to know which screen to show
- **Persistent State:** Game state persists until server restart (no save files)

### Error Patterns

**Enhanced Error Responses:**
- `"No active party set. Add monsters to your party before entering the dungeon."` - Show party setup UI
- `"Active party cannot exceed 4 monsters"` - Limit party selection UI
- `"Invalid door choice. Available: ['location_1', 'location_2', 'exit']"` - Re-render door choices
- `"Not currently in a dungeon"` - Redirect to home base screen
- `"Monster 123 not found"` - Remove from UI selection

**Common Errors:**
- `"Monster not found"` (404) - When monster was deleted
- `"Failed to generate entry text: LLM generation failed"` - Show generic entry text
- `"Template not found: template_name"` - Backend configuration issue
- `"ComfyUI server not running"` - Image generation unavailable

### Configuration Affecting Frontend

### Environment Variables
- `ENABLE_IMAGE_GENERATION`: `"true"|"false"` - Controls card art generation and display
- `FLASK_DEBUG`: `"true"|"false"` - Affects error verbosity

### Feature Flags (from /game/status)
```json
{
  "monster_generation": true,
  "ability_generation": true, 
  "image_generation": true,  // depends on ENABLE_IMAGE_GENERATION + ComfyUI
  "streaming_display": true,
  "unified_queue": true,
  "gpu_acceleration": true,  // depends on LLM config
  "battle_system": false,     // not implemented yet
  "chat_system": false,       // not implemented yet
  "save_system": true         // via game state management
}
```