# Data Models Reference

This document defines the structure of objects returned by the Monster Hunter Game API.

---

## Core Models

### Monster Object
Complete monster data structure returned by monster endpoints.

```typescript
interface Monster {
  // Identifiers
  id: number;
  created_at: string;          // ISO 8601 timestamp
  updated_at: string;          // ISO 8601 timestamp
  
  // Basic Information
  name: string;
  species: string;
  description: string;         // Short description
  backstory?: string;          // Longer backstory (optional)
  
  // Combat Stats
  stats: {
    max_health: number;        // 80-150 range
    current_health: number;    // Usually equals max_health
    attack: number;            // 15-35 range  
    defense: number;           // 10-30 range
    speed: number;             // 5-25 range
  };
  
  // Personality
  personality_traits: string[]; // e.g., ["wise", "protective", "mysterious"]
  
  // Relationships
  abilities: Ability[];        // Array of associated abilities
  ability_count: number;       // Convenience field
  
  // Card Art
  card_art: {
    has_card_art: boolean;
    relative_path?: string;    // e.g., "monster_card_art/00000001.png"
    full_path?: string;        // Complete file system path (if exists)
    exists: boolean;           // Whether file actually exists on disk
    url?: string;              // API endpoint to serve image
  };
}
```

**Example:**
```json
{
  "id": 15,
  "name": "Shadowmere the Elusive",
  "species": "Shadow Cat",
  "description": "A sleek feline creature that phases between dimensions",
  "backstory": "Born in the twilight realm between worlds...",
  "stats": {
    "max_health": 95,
    "current_health": 95,
    "attack": 28,
    "defense": 12,
    "speed": 22
  },
  "personality_traits": ["elusive", "curious", "independent"],
  "abilities": [
    {
      "id": 45,
      "name": "Phase Step",
      "description": "Briefly becomes intangible to avoid attacks",
      "ability_type": "movement"
    }
  ],
  "ability_count": 3,
  "card_art": {
    "has_card_art": true,
    "relative_path": "monster_card_art/00000015.png",
    "exists": true,
    "url": "/api/images/monster_card_art/00000015.png"
  },
  "created_at": "2025-01-15T14:22:30.000Z",
  "updated_at": "2025-01-15T14:22:30.000Z"
}
```

---

### Ability Object
Individual monster ability data structure.

```typescript
interface Ability {
  // Identifiers
  id: number;
  monster_id: number;          // Foreign key to monster
  created_at: string;          // ISO 8601 timestamp
  updated_at: string;
  
  // Ability Information
  name: string;                // e.g., "Lightning Strike"
  description: string;         // What the ability does
  ability_type?: string;       // "attack", "defense", "support", "special", "movement", "utility"
}
```

**Example:**
```json
{
  "id": 45,
  "monster_id": 15,
  "name": "Phase Step",
  "description": "Briefly becomes intangible to avoid attacks and reposition behind enemies",
  "ability_type": "movement",
  "created_at": "2025-01-15T14:22:35.000Z",
  "updated_at": "2025-01-15T14:22:35.000Z"
}
```

---

## Generation System Models

### Generation Log Object
Parent log entry for any AI generation (LLM or image).

```typescript
interface GenerationLog {
  // Identifiers
  id: number;
  created_at: string;
  updated_at: string;
  
  // Generation Information
  generation_type: "llm" | "image";
  prompt_type: string;         // e.g., "monster_generation", "ability_generation"
  prompt_name: string;         // e.g., "detailed_monster", "generate_ability"
  
  // Status Tracking
  status: "pending" | "generating" | "completed" | "failed";
  priority: number;            // 1-10, lower = higher priority
  generation_attempt: number;  // Current attempt (1-based)
  max_attempts: number;        // Maximum allowed attempts
  
  // Timing
  start_time?: string;         // When generation started
  end_time?: string;           // When generation completed/failed
  duration_seconds?: number;   // Total execution time
  
  // Error Handling
  error_message?: string;      // Error description if failed
  
  // Computed Fields
  is_completed: boolean;
  is_failed: boolean;
  attempts_used: number;
  
  // Child Data (based on generation_type)
  llm_data?: LLMLogData;       // Present if generation_type === "llm"
  image_data?: ImageLogData;   // Present if generation_type === "image"
}
```

### LLM Log Data
LLM-specific generation results and parsing information.

```typescript
interface LLMLogData {
  generation_id: number;       // References parent generation log
  
  // Model Response
  response_tokens?: number;    // Number of tokens generated
  tokens_per_second?: number;  // Generation speed
  
  // Parsing Results
  parse_success: boolean;      // Did parsing succeed?
  parsed_data?: object;        // Successfully parsed JSON (if any)
  parse_error?: string;        // Parsing error message (if failed)
  
  // Computed Fields
  has_response: boolean;       // Whether response_text exists
  has_parsed_data: boolean;    // Whether parsed_data exists
  
  // Model Information
  model_name?: string;         // Model file name used
  
  // Inference Parameters (reference only)
  inference_params: {
    max_tokens: number;
    temperature: number;
    top_p: number;
    // ... other parameters
  };
}
```

### Image Log Data
Image-specific generation results.

```typescript
interface ImageLogData {
  generation_id: number;       // References parent generation log
  
  // Image Results
  image_path?: string;         // Relative path to generated image
  image_filename?: string;     // Just the filename
  
  // Computed Fields
  has_image: boolean;          // Whether image_path exists
  image_exists: boolean;       // Whether file actually exists on disk
}
```

**Example Generation Log:**
```json
{
  "id": 123,
  "generation_type": "llm",
  "prompt_type": "monster_generation",
  "prompt_name": "detailed_monster",
  "status": "completed",
  "priority": 5,
  "generation_attempt": 1,
  "max_attempts": 3,
  "duration_seconds": 2.34,
  "is_completed": true,
  "is_failed": false,
  "attempts_used": 1,
  "created_at": "2025-01-15T14:22:30.000Z",
  "llm_data": {
    "generation_id": 123,
    "response_tokens": 187,
    "tokens_per_second": 79.9,
    "parse_success": true,
    "has_response": true,
    "has_parsed_data": true,
    "parsed_data": {
      "basic_info": {
        "name": "Thornwick the Wise",
        "species": "Forest Guardian"
      }
    }
  }
}
```

---

## Queue and Status Models

### Queue Item Status
Status information for items in the generation queue.

```typescript
interface QueueItem {
  generation_id: number;
  generation_type: "llm" | "image";
  priority: number;
  created_at: string;
  status: "pending" | "processing" | "completed" | "failed";
  
  // Timing
  started_at?: string;
  completed_at?: string;
  
  // Results (when completed)
  result?: GenerationResult;
  error?: string;              // Error message (when failed)
}
```

### Generation Result
Results returned when generation completes.

```typescript
// LLM Generation Result
interface LLMResult {
  success: true;
  text: string;                // Generated text
  tokens: number;              // Token count
  duration: number;            // Generation time in seconds
  tokens_per_second: number;   // Generation speed
  parsing_success?: boolean;   // Whether parsing succeeded
  parsed_data?: object;        // Parsed JSON (if applicable)
  attempt: number;             // Attempt number that succeeded
}

// Image Generation Result  
interface ImageResult {
  success: true;
  image_path: string;          // Relative path to generated image
  execution_time: number;      // Generation time in seconds
  workflow_used: string;       // ComfyUI workflow name
  prompt_type_used: string;    // Prompt type for organization
  cleanup_success: boolean;    // Whether VRAM cleanup succeeded
}

// Failed Result (both types)
interface FailedResult {
  success: false;
  error: string;               // Error description
  reason?: string;             // Error category (e.g., "DISABLED", "TIMEOUT")
}
```

---

## Statistics Models

### Monster Statistics
Aggregate statistics about monsters and abilities.

```typescript
interface MonsterStats {
  success: true;
  total_monsters: number;
  total_abilities: number;
  avg_abilities_per_monster: number;    // Decimal, e.g., 2.8
  monsters_with_card_art: number;
  card_art_percentage: number;          // Percentage with card art
  newest_monster?: Monster;             // Most recently created
  available_templates: string[];        // Template names
}
```

### Generation Statistics
Aggregate statistics about AI generations.

```typescript
interface GenerationStats {
  success: true;
  data: {
    overall: {
      total_generations: number;
      completed: number;
      failed: number;
      success_rate: number;           // Percentage
      by_type: {
        llm: number;
        image: number;
      };
    };
    llm: {
      total_with_responses: number;
      successful_parses: number;
      parse_success_rate: number;     // Percentage
      failed_parses: number;
    };
    image: {
      total_image_requests: number;
      successful_generations: number;
      success_rate: number;           // Percentage
      failed_generations: number;
    };
  };
}
```

---

## Error Response Format

### Standard Error Response
All endpoints use this format for errors.

```typescript
interface ErrorResponse {
  success: false;
  error: string;               // Human-readable error message
  
  // Optional additional fields based on context
  monster?: null;              // null for monster-related errors
  ability?: null;              // null for ability-related errors
  generation_id?: number;      // Present if generation was created
  reason?: string;             // Error category (e.g., "DISABLED", "NOT_FOUND")
  help?: string;               // Helpful suggestion for user
  details?: string[];          // Additional error details
}
```

**Common Error Types:**
```json
// Not Found
{
  "success": false,
  "error": "Monster not found",
  "monster": null
}

// Validation Error
{
  "success": false,
  "error": "Missing required field: name",
  "details": ["name is required", "description cannot be empty"]
}

// Feature Disabled
{
  "success": false,
  "error": "Image generation is disabled",
  "reason": "DISABLED",
  "help": "Set ENABLE_IMAGE_GENERATION=true to enable this feature"
}

// Processing Error
{
  "success": false,
  "error": "Generation failed after 3 attempts",
  "generation_id": 123,
  "reason": "PARSING_FAILED"
}
```

---

## Pagination Format

### Standard Pagination Response
Used by endpoints that return lists of items.

```typescript
interface PaginatedResponse<T> {
  success: true;
  data: T[];                   // Array of items
  total: number;               // Total count in database
  count: number;               // Count returned in this response
  pagination: {
    limit: number;             // Items per page
    offset: number;            // Items skipped
    has_more: boolean;         // Whether more pages exist
  };
}
```

**Example:**
```json
{
  "success": true,
  "monsters": [...],
  "total": 25,
  "count": 10,
  "pagination": {
    "limit": 10,
    "offset": 10,
    "has_more": true
  }
}
```