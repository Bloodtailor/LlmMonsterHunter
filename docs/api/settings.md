# Settings API

The in-game settings panel's backend (`/api/settings`). v1 covers text
generation only: which provider speaks (the local GGUF model or the
DeepSeek API), stored in the `game_settings` table — the one game table
that **survives the New Game wipe** (player setup is not world state;
locked decision, [docs/plans/game-settings.md](../plans/game-settings.md)).

Settings are resolved **per generation request**, so a save takes effect
on the next generation — no restart. A missing or half-configured row
always resolves to the local model exactly as the game behaved before
the panel existed.

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
    "context_window": 65536     // optional for known models
  }
}
```

**Success:** the GET shape plus `"message": "Settings saved"`.
**Error:** `400` with `{ "success": false, "error": string }`.

## Coming in later milestones (plan M3)
- `POST /settings/llm/fetch-models` — proxies DeepSeek `GET /models` with
  the provided-or-stored key (doubles as key validation).
- `POST /settings/llm/test` — fires a tiny generation through the normal
  gateway so the streaming panel and logs show the active model.
