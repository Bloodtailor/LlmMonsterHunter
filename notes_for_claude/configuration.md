# Configuration Reference

This document describes backend configuration that affects frontend behavior and feature availability.

---

## Environment Variables

### Core Application Settings
- **`FLASK_ENV`**: `development` | `production`
- **`FLASK_DEBUG`**: `True` | `False` - affects error reporting detail
- **`SECRET_KEY`**: Flask secret key
- **Base URL**: Always `http://localhost:5000` in development

### Feature Flags

#### Image Generation
- **`ENABLE_IMAGE_GENERATION`**: `true` | `false` (default: `false`)
  - Controls whether image generation is available
  - Affects: monster card art generation, image generation endpoints
  - When `false`: Image generation endpoints return disabled error
  - Check via: `/api/game/status` → `features.image_generation`

#### Generation System  
- **`LLM_MODEL_PATH`**: Path to language model file
  - Affects: Whether LLM generation is available
  - Check via: `/api/generation/status` → `llm_status.loaded`

### ComfyUI Settings (Image Generation)
- **`COMFYUI_BASE_URL`**: ComfyUI server URL (default: `http://127.0.0.1:8188`)
- **`COMFYUI_TIMEOUT`**: Generation timeout in seconds (default: `300`)
- **`COMFYUI_CHECKPOINT`**: Model checkpoint name
- **`COMFYUI_STEPS`**: Generation steps (default: `8`)
- **`COMFYUI_CFG`**: CFG scale (default: `2.0`)

---

## Feature Detection

### Runtime Feature Checking
The frontend should check feature availability at runtime rather than assume configuration.

**Primary Check - Game Status:**
```javascript
fetch('/api/game/status')
  .then(r => r.json())
  .then(status => {
    const features = status.features;
    
    // Check feature availability
    if (features.monster_generation) {
      // Enable monster generation UI
    }
    
    if (features.image_generation) {
      // Enable card art generation features
    }
    
    if (features.gpu_acceleration) {
      // Show GPU performance indicators
    }
  });
```

**Secondary Check - Generation Status:**
```javascript
fetch('/api/generation/status')
  .then(r => r.json())
  .then(({data}) => {
    // LLM availability
    if (data.llm_status.loaded) {
      // LLM is ready for text generation
    }
    
    // Image generation availability
    if (data.image_status.available) {
      // ComfyUI is ready for image generation
    }
    
    // Queue status
    if (data.queue_info.worker_running) {
      // Generation queue is active
    }
  });
```

---

## Feature States

### Image Generation States
The frontend should handle different image generation states:

**Disabled State** (`ENABLE_IMAGE_GENERATION=false`):
- Hide card art generation buttons
- Show "Image generation disabled" in settings
- Card art section shows placeholder or "Not available"

**Enabled but Server Down** (`ENABLE_IMAGE_GENERATION=true` but ComfyUI not running):
- Show "ComfyUI server not running" error
- Provide help text: "Start ComfyUI with: python main.py --listen"
- Disable image generation temporarily

**Fully Available**:
- Show all image generation features
- Enable card art generation for monsters
- Display image generation queue status

### LLM Generation States

**Model Not Loaded**:
- Show loading indicator for LLM status
- Disable text generation features
- Display model loading error if applicable

**Model Loaded but Not GPU**:
- Show warning about slow performance
- Text generation works but slower

**Model Loaded with GPU**:
- Show GPU performance indicator
- Full speed text generation available

---

## Default Values

### API Defaults
These defaults are used when values aren't specified in requests:

**Monster Generation:**
- Default template: `"detailed_monster"`
- Auto-generate abilities: `true` (always 2 initial abilities)
- Auto-generate card art: depends on `ENABLE_IMAGE_GENERATION`

**LLM Parameters:**
- Max tokens: `256`
- Temperature: `0.8`
- Top P: `0.9`
- Retry attempts: `3`

**Image Generation:**
- Workflow: `"monster_generation"`
- Dimensions: `1024x1024`
- Steps: `8`
- CFG: `2.0`
- Retry attempts: `2`

**Pagination:**
- Default limit: `50`
- Maximum limit: `100`
- Default offset: `0`

---

## Error Handling

### Feature-Specific Errors
Different features can fail in different ways:

**Image Generation Disabled:**
```json
{
  "success": false,
  "error": "Image generation is disabled",
  "reason": "DISABLED",
  "help": "Set ENABLE_IMAGE_GENERATION=true to enable this feature"
}
```

**ComfyUI Server Down:**
```json
{
  "success": false,
  "error": "ComfyUI server is not running",
  "reason": "SERVER_DOWN",
  "help": "Start ComfyUI with: python main.py --listen"
}
```

**LLM Model Not Loaded:**
```json
{
  "success": false,
  "error": "Model instance not available",
  "reason": "MODEL_NOT_LOADED"
}
```

**Generation Queue Full:**
```json
{
  "success": false,
  "error": "Generation queue is full, try again later",
  "reason": "QUEUE_FULL"
}
```

### Frontend Error Handling Strategy
1. **Check feature availability** before showing UI elements
2. **Handle graceful degradation** when features are unavailable
3. **Provide helpful error messages** with actionable steps
4. **Retry mechanisms** for temporary failures
5. **Fallback options** when possible (e.g., monsters without card art)

---

## Performance Considerations

### Generation Performance
- **LLM with GPU**: ~50-100 tokens/second
- **LLM without GPU**: ~5-15 tokens/second  
- **Image generation**: 20-60 seconds depending on complexity
- **Queue processing**: Sequential, one item at a time

### Frontend Performance Tips
- **Use SSE** for real-time updates instead of polling
- **Buffer partial text** updates to avoid excessive re-renders
- **Cache generation status** to avoid repeated API calls
- **Show progress indicators** for long-running operations
- **Implement request debouncing** for user actions

---

## Development vs Production

### Development Configuration
- Debug mode enabled
- Detailed error messages
- CORS enabled for localhost:3000
- Verbose logging
- No authentication required

### Production Considerations
(When implemented)
- Debug mode disabled
- Generic error messages for security
- Proper CORS configuration
- Authentication/authorization
- Rate limiting
- Request validation

---

## URL Structure

### Static Asset Serving
When image generation is enabled:
- **Card art images**: `/api/monsters/card-art/{relative_path}`
- **Example**: `/api/monsters/card-art/monster_card_art/00000001.png`

### File Organization
Images are organized by prompt type:
- **Monster card art**: `monster_card_art/00000001.png`
- **Future image types**: `{prompt_type}/{sequential_number}.png`

---

## Monitoring and Health

### Health Checks
- **Basic health**: `/api/health` - Always available
- **Game status**: `/api/game/status` - Feature availability
- **Generation status**: `/api/generation/status` - AI system status
- **SSE connections**: `/api/streaming/connections` - Real-time connection count

### Status Indicators
The frontend should monitor:
- **Connection status**: SSE connection health
- **Generation queue**: Current queue size and processing status
- **AI systems**: LLM and image generation availability
- **Performance metrics**: Generation speed and success rates

### Debugging Endpoints
- **Test LLM**: `/api/generation/test/llm`
- **Test Image**: `/api/generation/test/image`
- **Run tests**: `/api/game_tester/run/{test_name}`
- **View logs**: `/api/generation/logs`

---

## Version Information

### API Version
- **Current**: `2.0`
- **Check via**: `/api/health` → `api_version`

### Game Version
- **Current**: `0.1.0-mvp`
- **Check via**: `/api/game/status` → `version`

### Compatibility
- Frontend should check API version for compatibility
- Version mismatches should show upgrade/downgrade warnings
- Breaking changes will increment major version