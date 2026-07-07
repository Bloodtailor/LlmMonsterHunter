# Game Settings — In-Game Settings Panel + DeepSeek Provider — Plan

**Status:** APPROVED (July 2026) — no milestones landed yet.
**Branch:** `feature/game-settings` — one milestone commit per milestone, prefix `Set-M#`.

Today the game speaks to exactly one text engine: the local
llama-cpp-python model, configured entirely by `.env` and loaded at
startup — changing anything means editing `.env` and restarting. This
initiative adds an in-game **settings panel** (v1 scope: LLM setup
only, built as a sectioned overlay so future sections slot in) and a
second text-generation provider: the **DeepSeek API**
(OpenAI-compatible, `https://api.deepseek.com`). The player pastes an
API key, fetches the live model list, picks or types a model, and
flips an explicit Local / DeepSeek switch — no restart. Observability
grows with it: the streaming panel names the model that is generating,
and the debug logs record model name + prompt token count for every
generation.

Timing note that shaped the design: DeepSeek's current models are
`deepseek-v4-flash` / `deepseek-v4-pro` (1M context); `deepseek-chat` /
`deepseek-reasoner` deprecate 2026-07-24. A hardcoded model list would
be stale in weeks — hence live discovery.

## Locked decisions (design review with Aaron, July 2026)

1. **v1 scope: LLM setup only.** The panel is a general sectioned
   surface; one section ships ("Text Generation"). Image-gen and
   gameplay knobs are future sections, not v1.
2. **Manual provider switch.** Explicit Local / DeepSeek selector; no
   silent auto-fallback on errors — failures surface through the
   existing `llm.generation.failed` path. Local is the default when
   nothing is configured.
3. **Access everywhere via the header.** A gear button in the
   persistent `App.js` header opens a fixed-position overlay (the
   `StreamingDisplay` / `DungeonContextPanel` pattern, which already
   live in that header). An overlay — not a nav screen — because a
   screen switch would unmount the live game screen mid-dungeon, and
   the header works on the title screen and Developer view alike.
4. **Settings survive New Game.** New `game_settings` table;
   `wipe_world()` deletes an explicit model list, so the table
   survives by omission — asserted by a test (the log-tables
   precedent).
5. **Live model discovery + manual fallback.** Model list fetched from
   DeepSeek `GET /models` (auto up-to-date; returns ids only). Context
   window auto-fills from a small built-in known-models map and is
   ALWAYS editable; free-text model entry works when the fetch fails
   or a model is brand-new.
6. **Provider stamped at request time.** The gateway resolves settings
   per request and stamps provider + model onto the log/queue item —
   queued generations finish on the provider they were requested
   under, and prompt logging stays byte-exact for both providers (the
   nothink prefill applies to local only; DeepSeek gets
   `thinking: {type: 'disabled'}` instead).
7. **DeepSeek runs non-thinking mode in v1.** Params translated:
   max_tokens / temperature / top_p / frequency_penalty /
   presence_penalty / stop pass through; llama-only knobs (top_k,
   repeat_penalty, mirostat family, tfs_z, typical_p, seed, echo) are
   dropped. `reasoning_content` deltas are skipped defensively.
   `stream_options: {include_usage: true}` supplies exact prompt /
   completion token counts in the final chunk.
8. **API key at rest:** plaintext JSON in the local MySQL row
   (single-player local game — documented risk), and NEVER returned by
   the API: reads carry `has_api_key` + last-4 only; a save with a
   blank key field keeps the stored key.
9. **Tests keep stubbing at the game layer**
   (`game/utils/prompt_helpers.py::build_and_generate`). The provider
   seam sits below it, so every existing offline suite passes
   unchanged; the DeepSeek suite monkeypatches `requests` — no network
   in tests.
10. **Out of scope (v1):** per-provider inference-param editing in the
    UI, auto-unload of the local model when switching away (it stays
    in VRAM; the ComfyUI path already unloads it when it needs the
    GPU), thinking mode, other OpenAI-compatible hosts (the seam makes
    them cheap later), editing local model path/context from the panel
    (read-only display; `.env` + restart remains the way).

## Milestones

### M1 — Settings storage + API — PLANNED
No generation behavior change. `models/game_setting.py` (key/JSON
value, GlobalVariable-style, wipe-exempt by omission);
`ai/llm/provider_settings.py` (`resolve_llm_settings()` merges the DB
row over env with local/env as the unbreakable floor — missing
row/table/app-context can never break generation; read per request, no
cache); `services/settings_service.py` (validation trust boundary, key
masking); `routes/settings_routes.py`: GET `/api/settings/llm`
(provider, local status block, masked deepseek block, known-models
map), PUT `/api/settings/llm` (provider enum, positive context window,
deepseek requires key stored-or-provided + model). Registered in
`app.py`; imported in `models/core.py::create_tables`.
Suite: `test_game_settings.py` (get/set, precedence, masking,
validation, wipe survival). Docs: `docs/api/settings.md` + README index.

### M2 — Provider seam + observability — PLANNED
`ai/llm/providers/` package: `__init__.py::get_provider()`, `local.py`
(thin adapter over `inference.generate_streaming`; adds `model_name` =
model filename and exact `prompt_tokens` via `model.tokenize()`).
Dispatch in `processor.py` by the stamped provider. `llm_logs` gains
`provider` + `prompt_tokens` (nullable) — `create_from_params` stamps
provider/model at creation, `mark_response_completed` records prompt
tokens; one-off dev-DB script `tests/add_provider_log_columns.py`
(affinity-column precedent) + two `_SCHEMA_MARKERS` in `harness.py`.
`QueueItem.model_name` captured in `add_request` (caller's context)
rides `item.to_dict()` into `llm.generation.started` — additive only,
no event renames. Frontend: transformers pass `modelName` /
`promptTokens` / `provider` through; `aiStateStore.llmStatus` keeps
`modelName`; `StreamingDisplay` titles the LLM section with the model;
`LlmLogDetails` shows Provider + Prompt Tokens. Docs:
`docs/api/data-models.md`.

### M3 — DeepSeek provider — PLANNED
`ai/llm/providers/deepseek.py`: `generate_streaming` (streaming chat
completion via `requests` — no new dependency; single user message;
param translation per locked decision 7; skips `reasoning_content`;
captures the usage chunk for exact token counts; maps 401 invalid key /
402 balance / 429 rate limit / 5xx to clear errors), `list_models`,
`KNOWN_MODELS` context-window map. Resolver gains deepseek resolution
(stored context window, known-map fallback);
`game/utils/context_limits.py::get_context_size_tokens()` asks the
resolver first; `startup.py` skips the local model load when the saved
provider is DeepSeek (switching back mid-session works — inference
self-loads). Routes: POST `/api/settings/llm/fetch-models` (proxies
with provided-or-stored key — doubles as key validation), POST
`/api/settings/llm/test` (tiny generation through the normal gateway so
it shows in the streaming panel and logs).
Suite: `test_deepseek_provider.py` (monkeypatched requests). Docs:
`docs/api/settings.md`, `docs/tuning.md` (in-game settings section).

### M4 — Settings panel UI — PLANNED
`components/settings/`: `SettingsOverlay.js` (gear-opened, sectioned),
`LlmSettingsSection.js`, `settings.css`; `api/services/settings.js` +
`api/transformers/settings.js` (+ jest). Gear `IconButton` in the
`App.js` header. UX: provider radio → Local card (read-only: model
file, loaded badge, context size, "configured in .env") | DeepSeek card
(masked key input showing last-4; Fetch models → live Select, success
proves the key; select-or-type toggle; context window auto-fills from
the known map, always editable, unknown-model + cost hints). Save
(PUT, disabled until valid) and Test generation (post-save, response
shown, model name visible in the streaming panel). Docs:
`docs/architecture.md` provider-seam note; this plan → IMPLEMENTED.

## Verification

Offline suites (LLM stubbed / HTTP monkeypatched, test DB):
`test_game_settings`, `test_deepseek_provider`; full pytest (existing
suites stay green — the seam is below `build_and_generate`). Static:
ruff, file-size ceiling, prettier, jest. Live soak (Aaron, real key):
open settings from the title screen AND mid-dungeon → paste key →
fetch models → pick `deepseek-v4-flash` (context auto-fills; edit
down) → save → test generation → dungeon scene + battle on DeepSeek →
Developer log rows show model name + prompt tokens → switch back to
Local without restart → New Game → settings survive → break the key on
purpose → 401 surfaces clearly, no silent fallback.

## Deviations

- None yet.
