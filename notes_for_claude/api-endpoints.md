# Backend API Endpoints Reference

## Base URL
- Development: `http://localhost:5000`
- All endpoints return JSON

## Standard Response Format
```json
{
  "success": boolean,
  "data": object,     // On success
  "error": string,    // On failure
  "message": string   // Optional additional info
}
```

---

## Health & Status

### GET /api/health
Basic health check endpoint.

**Response:**
```json
{
  "status": "healthy",
  "message": "Monster Hunter Game API is running",
  "api_version": "2.0"
}
```

### GET /api/game/status
Comprehensive game status with AI system info.

**Response:**
```json
{
  "game_name": "Monster Hunter Game",
  "version": "0.1.0-mvp",
  "status": "development",
  "features": {
    "monster_generation": true,
    "ability_generation": true,
    "image_generation": false,
    "streaming_display": true,
    "unified_queue": true,
    "gpu_acceleration": true,
    "battle_system": false,
    "chat_system": false,
    "save_system": true
  },
  "ai_systems": {
    "llm_ready": true,
    "image_ready": false,
    "gpu_enabled": true,
    "queue_running": true,
    "queue_size": 0,
    "generation_types_supported": ["llm"]
  }
}
```

---

## Monster Management

### POST /api/monsters/generate
Generate a new monster with automatic abilities and optional card art.

**Request:**
```json
{
  "prompt_name": "detailed_monster",  // "basic_monster" or "detailed_monster"
  "generate_card_art": true          // requires ENABLE_IMAGE_GENERATION=true
}
```

**Success Response:**
```json
{
  "success": true,
  "monster": {
    "id": 1,
    "name": "Thornwick the Wise",
    "species": "Forest Guardian",
    "description": "A mystical creature with emerald eyes...",
    "backstory": "Born in the ancient groves...",
    "stats": {
      "max_health": 120,
      "current_health": 120,
      "attack": 25,
      "defense": 18,
      "speed": 15
    },
    "personality_traits": ["wise", "protective", "mysterious"],
    "abilities": [
      {
        "id": 1,
        "name": "Nature's Blessing",
        "description": "Heals nearby allies using forest magic",
        "ability_type": "support",
        "created_at": "2025-01-15T10:30:00"
      }
    ],
    "ability_count": 2,
    "card_art": {
      "has_card_art": true,
      "relative_path": "monster_card_art/00000001.png",
      "exists": true,
      "url": "/api/images/monster_card_art/00000001.png"
    },
    "created_at": "2025-01-15T10:30:00",
    "updated_at": "2025-01-15T10:30:00"
  },
  "generation_id": 123,
  "generation_stats": {
    "tokens": 187,
    "duration": 2.3,
    "abilities_generated": 2,
    "card_art_generated": true
  }
}
```

**Error Response:**
```json
{
  "success": false,
  "error": "Template not found: invalid_template",
  "monster": null
}
```

### GET /api/monsters
Get all monsters with pagination.

**Query Parameters:**
- `limit`: Number of monsters to return (default: 50, max: 100)
- `offset`: Number of monsters to skip (default: 0)

**Response:**
```json
{
  "success": true,
  "monsters": [
    // Array of monster objects (same format as generate response)
  ],
  "total": 15,
  "count": 10,
  "pagination": {
    "limit": 10,
    "offset": 0,
    "has_more": true
  }
}
```

### GET /api/monsters/{id}
Get specific monster by ID.

**Response:**
```json
{
  "success": true,
  "monster": {
    // Monster object (same format as generate response)
  }
}
```

**Error Response:**
```json
{
  "success": false,
  "error": "Monster not found",
  "monster": null
}
```

### GET /api/monsters/templates
Get available monster generation templates.

**Response:**
```json
{
  "success": true,
  "templates": {
    "basic_monster": "Generate a basic monster with name and description only",
    "detailed_monster": "Generate a detailed monster with stats, personality, and backstory"
  }
}
```

### GET /api/monsters/stats
Get monster database statistics.

**Response:**
```json
{
  "success": true,
  "total_monsters": 25,
  "total_abilities": 78,
  "avg_abilities_per_monster": 3.1,
  "monsters_with_card_art": 15,
  "card_art_percentage": 60.0,
  "newest_monster": {
    // Monster object
  },
  "available_templates": ["basic_monster", "detailed_monster"]
}
```

---

## Ability Management

### POST /api/monsters/{id}/abilities
Generate a new ability for an existing monster.

**Request:**
```json
{
  "wait_for_completion": true  // optional, default: true
}
```

**Success Response:**
```json
{
  "success": true,
  "ability": {
    "id": 15,
    "monster_id": 5,
    "name": "Lightning Strike",
    "description": "Channels electricity to strike enemies with precise bolts",
    "ability_type": "attack",
    "created_at": "2025-01-15T10:30:00"
  },
  "monster_id": 5,
  "generation_id": 456,
  "generation_stats": {
    "tokens": 89,
    "duration": 1.2,
    "attempts_needed": 1
  }
}
```

### GET /api/monsters/{id}/abilities
Get all abilities for a specific monster.

**Response:**
```json
{
  "success": true,
  "monster_id": 5,
  "abilities": [
    // Array of ability objects
  ],
  "count": 3
}
```

---

## Card Art Management

### POST /api/monsters/{id}/card-art
Generate card art for an existing monster.

**Request:**
```json
{
  "wait_for_completion": true  // optional, default: true
}
```

**Success Response:**
```json
{
  "success": true,
  "image_path": "monster_card_art/00000015.png",
  "execution_time": 45.2,
  "workflow_used": "monster_generation",
  "prompt_type_used": "monster_card_art",
  "monster_id": 5
}
```

**Error Response (Image Generation Disabled):**
```json
{
  "success": false,
  "error": "Image generation is disabled",
  "reason": "DISABLED",
  "monster_id": 5
}
```

### GET /api/monsters/{id}/card-art
Get card art information for a specific monster.

**Response:**
```json
{
  "success": true,
  "monster_id": 5,
  "card_art": {
    "has_card_art": true,
    "relative_path": "monster_card_art/00000015.png",
    "exists": true,
    "url": "/api/images/monster_card_art/00000015.png"
  }
}
```

### GET /api/monsters/card-art/{path}
Serve card art images directly.

**Example:** `/api/monsters/card-art/monster_card_art/00000001.png`

**Response:** Binary image data (PNG)

**Error Response:**
```json
{
  "success": false,
  "error": "Image not found"
}
```

---

## Generation System

### GET /api/generation/status
Get comprehensive generation system status.

**Response:**
```json
{
  "success": true,
  "data": {
    "llm_status": {
      "loaded": true,
      "model_path": "kunoichi-7b.Q6_K.gguf",
      "gpu_layers": 35,
      "currently_generating": false
    },
    "image_status": {
      "enabled": true,
      "server_running": true,
      "available": true
    },
    "queue_info": {
      "worker_running": true,
      "queue_size": 2,
      "current_item": {
        "generation_id": 789,
        "generation_type": "llm",
        "status": "processing"
      },
      "total_items": 45,
      "type_counts": {"llm": 38, "image": 7},
      "status_counts": {"completed": 40, "processing": 1, "pending": 2, "failed": 2}
    },
    "generation_types_supported": ["llm", "image"]
  }
}
```

### GET /api/generation/logs
Get generation logs with filtering.

**Query Parameters:**
- `limit`: Number of logs to return (default: 20, max: 100)
- `type`: Filter by generation type ("llm" or "image")
- `status`: Filter by status ("pending", "processing", "completed", "failed")

**Response:**
```json
{
  "success": true,
  "data": {
    "logs": [
      {
        "id": 123,
        "generation_type": "llm",
        "prompt_type": "monster_generation",
        "status": "completed",
        "duration_seconds": 2.3,
        "attempts_used": 1,
        "max_attempts": 3,
        "is_completed": true,
        "is_failed": false,
        "created_at": "2025-01-15T10:30:00",
        "llm_data": {
          "response_tokens": 187,
          "parse_success": true,
          "has_parsed_data": true
        }
      }
    ],
    "count": 10,
    "filters": {
      "type": "llm",
      "status": null,
      "limit": 20
    }
  }
}
```

### GET /api/generation/logs/{id}
Get detailed generation log with child data.

**Response:**
```json
{
  "success": true,
  "data": {
    "id": 123,
    "generation_type": "llm",
    "prompt_type": "monster_generation",
    "prompt_name": "detailed_monster",
    "status": "completed",
    "duration_seconds": 2.3,
    "llm_data": {
      "generation_id": 123,
      "response_tokens": 187,
      "tokens_per_second": 81.3,
      "parse_success": true,
      "parsed_data": {
        // The actual parsed JSON from the LLM
      }
    }
  }
}
```

### GET /api/generation/stats
Get comprehensive generation statistics.

**Response:**
```json
{
  "success": true,
  "data": {
    "overall": {
      "total_generations": 45,
      "completed": 40,
      "failed": 2,
      "success_rate": 88.9,
      "by_type": {"llm": 38, "image": 7}
    },
    "llm": {
      "total_with_responses": 38,
      "successful_parses": 35,
      "parse_success_rate": 92.1,
      "failed_parses": 3
    },
    "image": {
      "total_image_requests": 7,
      "successful_generations": 5,
      "success_rate": 71.4,
      "failed_generations": 2
    }
  }
}
```

### POST /api/generation/test/llm
Test LLM generation with simple prompt.

**Request:**
```json
{
  "prompt": "Hello! Please respond with just the word 'hi'."
}
```

**Response:**
```json
{
  "success": true,
  "text": "Hi there!",
  "tokens": 3,
  "duration": 0.8,
  "generation_id": 999
}
```

### POST /api/generation/test/image
Test image generation.

**Request:**
```json
{
  "description": "A majestic fire dragon with golden scales"
}
```

**Response:**
```json
{
  "success": true,
  "image_path": "test_images/00000001.png",
  "execution_time": 23.4,
  "generation_id": 1000
}
```

---

## Testing System

### GET /api/game_tester/tests
Get list of available test files.

**Response:**
```json
[
  "test_monsters",
  "test_simple_inference_request",
  "test_image_generation",
  "test_card_art_integration"
]
```

### GET /api/game_tester/run/{test_name}
Run a specific test file and capture output.

**Response:**
```json
{
  "success": true,
  "test_name": "test_monsters",
  "output": "🧪 Running monster test...\n✔ Monster test passed\n",
  "message": "Test test_monsters completed successfully"
}
```

**Error Response:**
```json
{
  "success": false,
  "error": "Something went wrong!",
  "traceback": "Traceback (most recent call last)...",
  "output": "🧪 Running monster test...\n"
}
```