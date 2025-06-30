# Server-Sent Events (SSE) Reference

## Connection
- **Endpoint:** `GET /api/streaming/llm-events`
- **Type:** Server-Sent Events (EventSource)
- **Keep-alive:** 30-second ping intervals

## Connection Setup
```javascript
const eventSource = new EventSource('http://localhost:5000/api/streaming/llm-events');

eventSource.onmessage = function(event) {
    const data = JSON.parse(event.data);
    // Handle event
};

// Or listen for specific event types
eventSource.addEventListener('generation_started', function(event) {
    const data = JSON.parse(event.data);
    // Handle generation start
});
```

---

## Event Types

### ping
Keep-alive ping sent every 30 seconds when no other events occur.

**Event Data:**
```json
{
  "timestamp": 1705123456.789
}
```

### generation_started
Fired when any generation (LLM or image) begins processing.

**Event Data:**
```json
{
  "item": {
    "generation_id": 123,
    "generation_type": "llm",        // "llm" or "image"
    "priority": 5,
    "created_at": "2025-01-15T10:30:00.000Z",
    "status": "processing",
    "started_at": "2025-01-15T10:30:05.000Z"
  },
  "generation_id": 123
}
```

### generation_update
Fired during generation for real-time progress updates.

**LLM Generation Update:**
```json
{
  "generation_id": 123,
  "partial_text": "The ancient dragon known as Thornwick",
  "tokens_so_far": 7
}
```

**Image Generation Update:**
```json
{
  "generation_id": 456,
  "progress_message": "🔧 Initializing image generation..."
}
```

**Common Progress Messages for Images:**
- `"🔧 Initializing image generation..."`
- `"✅ ComfyUI server connected"`
- `"📋 Loaded workflow: monster_generation"`
- `"⚙️ Workflow configured with parameters"`
- `"📤 Queuing generation request..."`
- `"⏳ Generation in progress..."`
- `"💾 Downloading and organizing image..."`
- `"✅ Image generation completed!"`

### generation_completed
Fired when generation successfully completes.

**LLM Completion:**
```json
{
  "item": {
    "generation_id": 123,
    "generation_type": "llm",
    "status": "completed",
    "completed_at": "2025-01-15T10:30:08.000Z",
    "result": {
      "success": true,
      "text": "The ancient dragon known as Thornwick the Wise...",
      "tokens": 187,
      "duration": 2.3,
      "parsing_success": true,
      "parsed_data": {
        "basic_info": {
          "name": "Thornwick the Wise",
          "species": "Ancient Dragon"
        }
      }
    }
  },
  "generation_id": 123,
  "result": {
    // Same as item.result above
  }
}
```

**Image Completion:**
```json
{
  "item": {
    "generation_id": 456,
    "generation_type": "image",
    "status": "completed",
    "completed_at": "2025-01-15T10:35:15.000Z",
    "result": {
      "success": true,
      "image_path": "monster_card_art/00000001.png",
      "execution_time": 45.2,
      "workflow_used": "monster_generation",
      "prompt_type_used": "monster_card_art"
    }
  },
  "generation_id": 456,
  "result": {
    // Same as item.result above
  }
}
```

### generation_failed
Fired when generation fails.

**Event Data:**
```json
{
  "item": {
    "generation_id": 123,
    "generation_type": "llm",
    "status": "failed",
    "completed_at": "2025-01-15T10:30:08.000Z",
    "error": "Model instance not available"
  },
  "generation_id": 123,
  "error": "Model instance not available"
}
```

### queue_update
Fired when items are added/removed from the generation queue.

**Event Data:**
```json
{
  "action": "added",                    // "added" or "removed"
  "item": {
    "generation_id": 789,
    "generation_type": "image",
    "priority": 7,
    "status": "pending"
  },
  "queue_size": 3
}
```

---

## Event Flow Examples

### LLM Generation Flow
1. **queue_update** (action: "added")
2. **generation_started**
3. **generation_update** (multiple times with partial text)
4. **generation_completed** OR **generation_failed**

### Image Generation Flow
1. **queue_update** (action: "added")
2. **generation_started**
3. **generation_update** (multiple times with progress messages)
4. **generation_completed** OR **generation_failed**

### Example Timeline
```
10:30:00 - queue_update: {"action": "added", "generation_id": 123}
10:30:01 - generation_started: {"generation_id": 123, "generation_type": "llm"}
10:30:02 - generation_update: {"partial_text": "The ancient"}
10:30:03 - generation_update: {"partial_text": "The ancient dragon known"}
10:30:04 - generation_update: {"partial_text": "The ancient dragon known as Thornwick"}
10:30:08 - generation_completed: {"generation_id": 123, "result": {...}}
```

---

## Error Handling

### Connection Errors
If the SSE connection fails, the frontend should:
1. Show connection status to user
2. Attempt automatic reconnection
3. Fall back to polling `/api/generation/status` for updates

### Missing Events
Events are best-effort delivery. For critical state, always verify with REST API calls:
- Check `/api/generation/logs/{id}` for generation status
- Check `/api/generation/status` for queue state

---

## Testing SSE

### Manual Connection Test
```javascript
const eventSource = new EventSource('/api/streaming/llm-events');

eventSource.onopen = () => console.log('SSE Connected');
eventSource.onerror = (e) => console.log('SSE Error:', e);
eventSource.onmessage = (e) => console.log('Event:', e.data);

// Close when done
// eventSource.close();
```

### Trigger Events for Testing
```javascript
// Start LLM generation to see events
fetch('/api/streaming/add', {
    method: 'POST',
    headers: {'Content-Type': 'application/json'},
    body: JSON.stringify({prompt: "Hello world"})
});

// Start image generation to see events  
fetch('/api/streaming/add-image', {
    method: 'POST',
    headers: {'Content-Type': 'application/json'},
    body: JSON.stringify({
        monster_description: "A fire dragon",
        monster_name: "Test Dragon"
    })
});
```

### Check Active Connections
```javascript
fetch('/api/streaming/connections')
    .then(r => r.json())
    .then(data => {
        console.log('Active connections:', data.active_connections);
        console.log('Supported events:', data.event_types);
    });
```

---

## Frontend Integration Patterns

### React Hook Example
```javascript
useEffect(() => {
    const eventSource = new EventSource('/api/streaming/llm-events');
    
    const handlers = {
        generation_started: (data) => setGenerationStatus('processing'),
        generation_update: (data) => setPartialText(data.partial_text),
        generation_completed: (data) => {
            setGenerationStatus('completed');
            setFinalResult(data.result);
        },
        generation_failed: (data) => {
            setGenerationStatus('failed');
            setError(data.error);
        }
    };
    
    Object.entries(handlers).forEach(([event, handler]) => {
        eventSource.addEventListener(event, (e) => {
            handler(JSON.parse(e.data));
        });
    });
    
    return () => eventSource.close();
}, []);
```

### State Management
- Track connection status (connected/disconnected/error)
- Buffer partial text updates for smooth rendering
- Handle reconnection logic
- Fallback to polling when SSE unavailable