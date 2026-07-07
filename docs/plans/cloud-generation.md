# Cloud Generation — 1M-Token Context Floor + Gemini Image API — Plan

**Status:** IMPLEMENTED (July 2026) — all five milestones landed, one
commit each (prefix `Cgn-M#`). Pending Aaron's live soak with a real
Gemini key: the verification checklist below.
**Branch:** `feature/cloud-generation`.

Aaron's July 7 2026 executive decision, refined by the same-day repo
split: **this repo is the API-first project** (the local-first pivot lives
in the sibling fork `LlmMonsterHunter-Local`). Two changes land here as
one initiative:

1. **Stop supporting models with <1M-token context windows.** Local GGUF
   models stay *possible* (the code path is untouched) but unsupported —
   the small-window engineering (detail tiers, window-relative budget
   shares, over-generation workarounds, CUDA-first onboarding) comes out.
2. **Image generation moves from local ComfyUI to the Gemini image API**
   ("Nano Banana" family), including passing the old card art as a
   reference image so Monster Evolution's regenerated art keeps the
   creature's identity — something the old blind txt2img regen could not.

## Locked decisions (Aaron, 2026-07-07)

1. **Hard 1M floor.** `MIN_CONTEXT_WINDOW = 1_000_000` — the settings
   panel refuses smaller context windows. `.env` remains the unsupported
   escape hatch for local models (no code removal there).
2. **70% ceiling.** Prompts never exceed 70% of the context window:
   `LLM_CONTEXT_FILL_PERCENT` defaults to `0.7` and is clamped to ≤ 0.7.
3. **Absolute token caps.** Flexible block budgets stop being fractions of
   the window and become absolute per-block token caps (cost + attention
   valves). Rolling summaries stay the compaction engine. Detail tiers are
   deleted — every prompt gets the full monster blocks.
4. **Gemini image suite only, default `gemini-3.1-flash-image`** (Nano
   Banana 2, ~$0.067 per 1K image). Model is a picker (live-discovered,
   like DeepSeek models); no per-purpose model mix in v1.
5. **ComfyUI support is removed entirely** (package, config, workflow
   JSONs, setup checks, env vars). Git history is the archive; local card
   art belongs to the -Local fork.
6. **Reference images become a first-class gateway parameter.** Evolution
   regen passes the old card art with a transformation instruction.
7. **Image prompts go natural-language.** The SD tag-soup + negative
   prompt dies; "no humans / no text / no watermark" folds into the
   instruction; the house style lives in config as a sentence; dimensions
   become aspect ratio `2:3` at `1K` resolution (was 896×1254).
8. **Gemini key handling mirrors DeepSeek** (locked decisions,
   [game-settings.md](game-settings.md)): stored in a `game_settings` row,
   write-only through the API, masked to last-4 on reads, plaintext-at-rest
   documented risk. Image generation is enabled by panel toggle +
   configured key — the `ENABLE_IMAGE_GENERATION` env var retires.
9. **Tests keep stubbing at the game layer**; the Gemini suite
   monkeypatches `requests` (no network in tests, `test_deepseek_provider`
   precedent). Offline suites run with image generation unconfigured.
10. **Out of scope (v1):** per-purpose model routing, style-reference
    images, portrait-from-upload references, Gemini Batch API, non-Gemini
    image providers, retuning `DEFAULT_MAX_TOKENS` (response length is a
    separate tuning pass).

## Milestones

### Cgn-M1 — Context floor + budget rework

- `backend/ai/llm/provider_settings.py`: `MIN_CONTEXT_WINDOW = 1_000_000`;
  drop deprecated `deepseek-chat` / `deepseek-reasoner` from the known
  map (ids removed by DeepSeek 2026-07-24); `_env_context_size()` default
  `1_000_000`. **Below-floor saved rows** resolve to the local floor (a
  stored 128K window must never be budgeted as 1M) until the player
  re-picks a v4 model in the panel.
- `backend/game/utils/context_limits.py`: fill percent default `0.7`,
  clamped `(0.3, 0.7)`; `FLEXIBLE_BLOCK_SHARES` →
  `FLEXIBLE_BLOCK_TOKEN_CAPS` (absolute tokens): dungeon_log 12_000,
  battle_log 8_000, chat_history 8_000, dialogue_history 6_000,
  last_run_log 4_000, turn_history 2_000, monster_memories 3_000,
  run_journal 2_000, location_description 1_500; caps scale down
  proportionally when their sum exceeds the 70% budget (tiny unsupported
  env windows degrade gracefully; `MIN_FLEXIBLE_CHARS` kept); delete
  `resolve_detail_tier()` and the bins.
- Tier consumers: `backend/game/monster/context_builder.py` (always the
  full block), `backend/game/memory/manager.py` (tier-binned memory-line
  count → one constant), `backend/game/utils/__init__.py` exports.
- `backend/game/dungeon/events.py`: `PATH_OVERGENERATE_COUNT` 6 → 4.
- `backend/services/settings_service.py` local display default;
  frontend `min_context_window` fixtures; `.github/workflows/ci.yml`
  (`LLM_CONTEXT_SIZE: '1000000'`); `.env.example`.
- Tests: `test_monster_templates.py` tier loop → full-detail check;
  `test_game_settings.py` window boundaries at 1M.
- Docs in the same commit: `docs/tuning.md`, `docs/architecture.md`,
  README architecture bullet.

### Cgn-M2 — Gemini image provider (the seam swap)

New package `backend/ai/image/` (mirrors the LLM provider seam):

- `paths.py`: `IMAGE_OUTPUTS_DIR = backend/ai/image/outputs/` + one-time
  auto-migrate of the old `backend/ai/comfyui/outputs/` tree (DB art paths
  are relative — nothing else changes).
- `image_settings.py`: `resolve_image_settings()` — `image_provider`
  `game_settings` row over code defaults (provider `gemini`, api_key,
  model default `gemini-3.1-flash-image`, enabled flag); unconfigured →
  disabled; per-call resolution (no restart), replacing the import-time
  `IMAGE_GENERATION_ENABLED` constant.
- `gemini.py`: `generate_image(prompt, reference_image_paths, **params)`
  via plain `requests` (deepseek.py pattern) — `generateContent` REST,
  `x-goog-api-key`, base64 `inline_data` reference parts, aspect ratio +
  resolution config; HTTP status → player-readable errors;
  `list_models(api_key)` filtered to image-capable ids.
- `processor.py`: loads the log, resolves settings, reads reference
  bytes, calls the provider, saves the PNG with the existing sequential
  numbering, marks logs. All `image.generation.*` events stay
  byte-compatible — no SSE/step-name changes.
- `gateway.py::image_generation_request`: optional `reference_images`;
  enabled check via `image_settings`; `prompt_name` becomes a plain log
  label; `image_params = {model, aspect_ratio, resolution,
  reference_images}`; model stamped into the image log so
  `QueueItem.model_name` rides queue events for images too.
- `queue.py`: new processor; **delete the `unload_model()` VRAM dance**.
- Delete `backend/ai/comfyui/**`; `comfyui_config.py` →
  `image_config.py` (`HOUSE_STYLE_PROMPT`, `AVOID_INSTRUCTION`,
  `DEFAULT_ASPECT_RATIO`, `DEFAULT_RESOLUTION`, `DEFAULT_IMAGE_MODEL`,
  `TIMEOUT`).
- Consumers switch to `is_image_generation_enabled()`: `game/utils`,
  `card_art.py`, `registered_workflows.py`, `player_service.py`,
  `startup.py` (`_check_image_generation` reports provider/model/key).
- Serving unchanged: `monster_routes.py` + `portrait.py` read
  `paths.IMAGE_OUTPUTS_DIR`. `.env.example` drops `ENABLE_IMAGE_GENERATION`
  + `COMFYUI_*`; `.gitignore` outputs path moves.
- New suite `test_gemini_provider.py` (monkeypatched `requests`).

### Cgn-M3 — Natural-language prompts + evolution references

- `card_art.py::_build_card_art_prompt` and
  `portrait.py::compose_portrait_prompt` → descriptive sentences; house
  style + avoid-instruction appended from `image_config` in the processor.
- Evolution regen (`registered_workflows.py`): with card art present,
  `reference_images=[old_path]` + a transformation instruction built from
  the evolved appearance; without, plain generation. `art_regenerated`
  flag and keep-old-art-on-failure behavior unchanged.
- Enemy/dialogue/explore call sites untouched.

### Cgn-M4 — Settings panel Images section

- `settings_service.py` get/update image settings (write-only key,
  last-4 masking, model select-or-type, enabled toggle); routes GET/PUT
  `/api/settings/image`, POST `/api/settings/image/fetch-models`, POST
  `/api/settings/image/test` (one tiny paint through the normal gateway).
- Frontend `ImageSettingsSection.js` in the sectioned `SettingsOverlay`;
  `api/services/settings.js` + `api/transformers/settings.js` + jest.
- `test_game_settings.py`: image row validation + New Game wipe survival.
  Docs: `docs/api/settings.md`, tuning.md settings table.

### Cgn-M5 — Onboarding + docs sweep

- README rewrite: API-first identity (+ -Local fork pointer), Gemini card
  art, prerequisites shrink to Python/Node/MySQL + two API keys (local
  extras become a short optional appendix), Quick Start without ComfyUI,
  tech stack, acknowledgments, initiative table row.
- `setup/`: `gpu_cuda_flow` / `vs_flow` / `llama_cpp_flow` behind an
  optional "local extras" branch; API-keys guidance is the golden path;
  ComfyUI copy removed; walkthrough runs end-to-end on base deps.
- `CLAUDE.md` commands note reworded (no local AI required; offline
  suites stub LLM + image). `start_game.bat` ComfyUI reminders dropped.
- `docs/architecture.md` full pass; `docs/api/` generation params; final
  tuning.md pass; this plan → IMPLEMENTED.

## Verification

Per milestone (suites green before each `Cgn-M#` commit):
`PYTHONIOENCODING=utf-8 ./venv/Scripts/python.exe -m pytest` (offline
suites, MySQL running), `ruff check backend setup tools`,
`tools/check_file_sizes.py`; frontend `npm test` + `npx prettier --check
src`.

Live soak (Aaron, real keys, after M5): Settings → Images → paste Gemini
key → fetch models → pick Nano Banana 2 → test paint → generate a monster
(art arrives; dev log shows model + params) → dungeon run (enemy art) →
**evolve a monster with existing art and confirm the new art is
recognizably the same creature** (the reference payoff) → portrait paint +
upload → New Game (settings survive) → break the key (401 surfaces
cleanly) → DeepSeek context field refuses < 1M → re-pick
`deepseek-v4-flash` if an old 128K row was saved.

Cost sanity: NB2 at 1K ≈ $0.067/image → a heavy session (~20–30 images)
≈ $1.30–2.00.

## Risks / notes

- Gemini REST field names are pinned to the official docs and encoded in
  the provider test suite during M2.
- A pre-existing saved DeepSeek row pointing at a deprecated 128K model
  resolves to the local floor until re-picked — surfaced in the panel,
  covered in the soak.
- Existing art survives via the one-time outputs-tree move; relative DB
  paths never change.

## Deviations

- **Pre-M1 (format sweep):** 14 files on main failed the pinned ruff
  0.15.20's format check — CI on main had been red since PR #166. Swept
  mechanically in their own commit before Cgn-M1 so milestone diffs stay
  clean and the branch's CI can go green.
- **M1 (below-floor rows, refined):** a below-floor stored window on a
  KNOWN 1M-class model heals to the known-models map instead of falling
  local (the model really has the window; only the stale number was
  wrong). Only legacy/unknown models with no supported size resolve
  local. The service also treats a below-floor STORED window as absent
  on save, so old rows self-heal through auto-fill.
- **M2 (Gemini API shape):** the 3.1-generation image models speak the
  new **Interactions API** (`POST /v1beta/interactions`, typed `input`
  blocks, `response_format` carrying `aspect_ratio`/`image_size`,
  image bytes in `output_image` with a `steps` fallback) rather than
  `generateContent`. The provider and its suite pin that shape.
- **M3 (art_regenerated honesty):** evolution's `art_regenerated` flag
  now reports the actual paint result — the old code marked it true
  whenever the attempt ran, even if the paint quietly failed.
- **M4 (live-boot verification):** backend boot with the real dev DB
  confirmed the legacy outputs tree migrated (monster_card_art,
  player_card_art, player_uploads) and the panel's Images section
  renders with the enable-requires-key gate working; the saved DeepSeek
  row was already `deepseek-v4-pro` (1M), so the soak's re-pick step
  should be a no-op. A stale LLM-section hint ("65536 is plenty") was
  corrected to the 1M floor while in the panel.
