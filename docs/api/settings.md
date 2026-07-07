# Settings API

The in-game settings panel's backend (`/api/settings`). Two sections:
**text generation** (which provider speaks — the local GGUF model or the
DeepSeek API) and **images** (the Gemini painter,
[docs/plans/cloud-generation.md](../plans/cloud-generation.md)). Both
live in the `game_settings` table — the one game table that **survives
the New Game wipe** (player setup is not world state; locked decision,
[docs/plans/game-settings.md](../plans/game-settings.md)).

Settings are resolved **per generation request**, so a save takes effect
on the next generation — no restart. A missing or half-configured LLM
row always resolves to the local model exactly as the game behaved
before the panel existed; a missing image row means painting is off
(art is a bonus, never a blocker).

## LLM settings (`/api/settings/llm`)

### GET /settings/llm
Current configuration. The DeepSeek API key is **write-only**: reads
carry `has_api_key` + the last four characters, never the key.

**Success:**
```json
{
  "success": true,
  "provider": "local" | "deepseek",
  "local": {
    "configured": boolean,      // LLM_MODEL_PATH is set in .env
    "model_file": string|null,  // GGUF filename (read-only in v1 - .env owns it)
    "loaded": boolean,
    "error": string|null,       // last load failure, if any
    "context_size": number,     // LLM_CONTEXT_SIZE
    "gpu_layers": number
  },
  "deepseek": {
    "has_api_key": boolean,
    "api_key_last4": string|null,
    "model": string|null,
    "context_window": number|null
  },
  "known_models": { "deepseek-v4-flash": 1000000, ... }, // panel auto-fill
  "min_context_window": number  // smallest window the service accepts
}
```

### PUT /settings/llm
Save from the panel. Rules:
- `provider` must be `local` or `deepseek`.
- DeepSeek fields may be saved while staying on `local` (paste the key
  now, switch later); each field given must be valid.
- Switching **to** `deepseek` requires a complete config: an API key
  (stored or provided), a model, and a context window — auto-filled from
  `known_models` when the model is recognized, required manually for
  unknown models (their windows aren't published by the DeepSeek API).
- A blank/absent `api_key` keeps the stored key (the panel never holds
  the real key to echo back).
- `context_window` below `min_context_window` is refused — the game
  reserves response room out of the window, and a tiny window would
  starve every prompt block.

**Request:**
```json
{
  "provider": "deepseek",
  "deepseek": {
    "api_key": "sk-...",        // optional once stored
    "model": "deepseek-v4-flash",
    "context_window": 2000000   // optional for known models; min 1,000,000
  }
}
```

**Success:** the GET shape plus `"message": "Settings saved"`.
**Error:** `400` with `{ "success": false, "error": string }`.

### POST /settings/llm/fetch-models
Live model list, proxied through the backend so the key never
round-trips the panel. DeepSeek's `/models` endpoint requires auth, so a
successful fetch **is** key validation. New DeepSeek models appear here
the day they ship — nothing hardcoded.

**Request:** `{ "api_key": "sk-..." }` — optional; the stored key backs
an empty request.

**Success:**
```json
{
  "success": true,
  "models": ["deepseek-v4-flash", "deepseek-v4-pro"],
  "known_models": { "deepseek-v4-flash": 1000000, ... },
  "key_valid": true
}
```
**Error:** `400` with the mapped DeepSeek message (401 bad key /
402 balance / 429 rate limit / 5xx server / network unreachable).

### POST /settings/llm/test
Fires one tiny real generation through the normal gateway — it queues,
streams in the streaming panel (titled with the model name), and lands
in the developer log with prompt tokens. The whole path is the test.
Synchronous: the response waits for the generation.

**Success:**
```json
{
  "success": true,
  "text": string,            // the model's one-sentence answer
  "provider": "local"|"deepseek",
  "model_name": string,
  "prompt_tokens": number|null
}
```
**Error:** `400` with the provider's message (e.g. the 401 mapping) —
exactly what the panel should show. No silent fallback to the other
provider (locked decision).

## Image settings (`/api/settings/image`)

Painting is OFF until this section is configured — there is no env
switch anymore. The Gemini API key is **write-only**, same rules as the
DeepSeek key.

### GET /settings/image

**Success:**
```json
{
  "success": true,
  "enabled": boolean,
  "has_api_key": boolean,
  "api_key_last4": string|null,
  "model": string|null,        // saved pick; null = the default below
  "default_model": "gemini-3.1-flash-image"
}
```

### PUT /settings/image
Save from the panel. Rules:
- A blank/absent `api_key` keeps the stored key.
- Fields may be saved while `enabled` stays `false` (paste the key now,
  switch on later).
- `enabled: true` requires a key (stored or provided).
- A missing `model` falls back to `default_model` at paint time.

**Request:** `{ "enabled": true, "api_key": "AIza...", "model": "gemini-3.1-flash-image" }`
**Success:** the GET shape plus `"message": "Settings saved"`.
**Error:** `400` with `{ "success": false, "error": string }`.

### POST /settings/image/fetch-models
Live image-capable model list (ids containing `image` — the Nano Banana
family), proxied so the key never round-trips the panel. A successful
fetch **is** key validation.

**Request:** `{ "api_key": "AIza..." }` — optional; the stored key backs
an empty request.
**Success:** `{ "success": true, "models": ["gemini-3.1-flash-image", ...], "key_valid": true }`
**Error:** `400` with the mapped Gemini message (401/403 bad key /
429 rate limit / 5xx server / network unreachable).

### POST /settings/image/test
Fires one tiny real paint through the normal gateway — it queues, lands
in the developer log with its model, and files a real image under
`outputs/settings/`. Synchronous: the response waits for the paint.

**Success:**
```json
{
  "success": true,
  "image_path": "settings/00000001.png",  // serve via /api/monsters/card-art/<path>
  "model_name": "gemini-3.1-flash-image"
}
```
**Error:** `400` with the provider's message — exactly what the panel
should show.
