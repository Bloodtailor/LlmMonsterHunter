# New Game Experience — Wipe + Player Character — Plan

**Status:** IMPLEMENTED (July 2026) — all five milestones landed. The
creation flow was soaked end-to-end on the real model + ComfyUI against
the test DB (New Game → wizard with mixed picked/typed answers → forge
→ paint + upload + select → personalized opening). Still on Aaron's
soak list: the full guided first run as a created character, a
home-base chat where the monster uses the character's name, and a
battle with the player fighting as a commanded ally.
**Branch:** `feature/new-game-experience` — one milestone commit per milestone, prefix `Ngx-M#`.

Today "New Game" wipes nothing (game-loop-v1 locked decision #1: the
single-world model) and the player exists only as the phrase "the
adventurer" inside prompts. This initiative makes New Game a true fresh
start and gives the player a **created character** — a real `monsters`
row that is always in the party, is the voice the player chats as, and
is built through a guided creation screen: LLM-offered options + free
text for every field, portrait candidates + upload for the face.

**Supersedes game-loop-v1 locked decision #1** (noted there): New Game
now erases the world; Continue remains the way back into the one world.

## Locked decisions (design review with Aaron, July 2026)

1. **Wipe scope: game data only.** New Game deletes every game-domain
   table; the Developer screen's `generation_logs`/`llm_logs`/`image_logs`
   and art files on disk survive (observability, not world state).
2. **Party cap: player + 3 companions** (4 combatants total — battle
   tuning untouched). `ActiveParty` keeps holding companions only; the
   player is prepended at read time, never stored in a party row.
3. **Player down = just another ally.** Defeat still means the whole
   party falls. No referee special-casing.
4. **Player kind: anything.** Kind options come from the same CMDTS
   taxonomy monsters use (human among them), plus type-your-own.
5. **Player = a monster row + `GlobalVariable('player_monster_id')`.**
   No new tables or columns — no test-harness schema rebuild. New domain
   package `backend/game/player/`.
6. **Graceful absence:** every integration point no-ops when no player
   exists — a pre-initiative world keeps working exactly as today.
7. **Player rarity fixed at `common`** (stats via `cmdts_data.derive_stats`);
   role chosen at creation from `PARTY_ROLES`. Growth applies; evolution,
   affinity, chat-as-target, and following-list membership are excluded.
8. **Out of scope (v1):** player evolution, renaming/re-art after
   creation, save profiles, player-specific battle verbs, mid-game edits.

## Milestones

### M1 — New Game actually starts a new game — IMPLEMENTED
`game/state/new_game.py` `wipe_world()`: deletes all game-domain rows in
FK-safe order (party, following, chat messages/summaries/threads,
memories, evolutions, abilities, monsters, runs, items, cocatoks,
workflows, globals) in one transaction; log tables survive.
`start_new_game()` service refuses while any workflow is pending or
processing. `POST /api/game-state/new-game`; `get_game_state()` gains
`has_world_data`. TitleScreen shows a destructive-confirm step when the
world holds anything, then erases and proceeds (to `first-run-opening`
until M4 reroutes through creation). Suite: `test_new_game.py`.

### M2 — The player domain: always in the party — IMPLEMENTED
`game/player/manager.py` (pointer helpers). Party reads in
`state/manager.py` prepend the player; companion cap 4→3;
`set_active_party` filters the player id and enforces the cap.
Exemptions via `is_player_monster`: never autonomous, no affinity steps,
not a chat target, not followable, not evolvable. Battle inherits the
player through party ids (test-covered, no battle code changes).
Suite: `test_player_character.py`.

### M3 — Creation backend: options, finalize, portrait — IMPLEMENTED
`ai/llm/prompts/player_generation.json`: `player_options` (3–4 option
texts for one field, conditioned on choices so far; fields kind/name/
background/personality/wish/appearance — role is a static code list),
plus staged `player_blueprint` / `player_persona` / `player_story`
(mirroring monster generation, conditioned on the player's answers; the
chosen appearance text is kept verbatim as `appearance.visual_description`).
Workflows in `game/player/`: `generate_player_options`,
`create_player_character` (saves the row, sets the pointer, reuses
`generate_ability` twice, emits the standard monster.* events),
`generate_player_portrait` (image gateway call whose result is a
CANDIDATE path — `card_art_path` untouched until selection).
Routes `routes/player_routes.py` + `services/player_service.py`:
GET `/api/player`, POST `options`/`create`/`portrait/generate`
(→ `{workflow_id}`), POST `portrait/select` (path must live under
`player_card_art/` or `player_uploads/` and exist), POST
`portrait/upload` (multipart png/jpg/webp ≤ 8MB, magic-byte sniff,
saved to `outputs/player_uploads/`, auto-selected). Existing card-art
route serves everything under outputs.

### M4 — Character development screen — IMPLEMENTED
`screens/game/CharacterCreationScreen.js` + `components/player/` wizard:
per-field option cards + always-editable free text; portrait stage with
candidate gallery, paint-another, upload, and skip (art never blocks);
finalize plays the staged card reveal through the existing monster event
handlers; navigation `character-creation` between Title's New Game and
`first-run-opening`; sanctuary/party pin the player card with a "You"
badge and hide follow/release/chat-with-self controls.

### M5 — The world knows the player — IMPLEMENTED
Chat: `speaker_display_name` returns the player's name for role
`player`; `home_chat_reply` + `chat_memory_extraction` gain a
`{player_details}` block and name the player instead of "the adventurer";
chat UI attributes the player's lines. `opening_scene` gains player
context. Docs: api docs, tuning rows (companion cap, option count,
upload limits, player rarity), architecture directory map, this plan →
IMPLEMENTED.

## Verification

Offline suites (LLM stubbed, test DB): `test_new_game`,
`test_player_character`, updated `test_first_run`; full pytest. Static:
ruff, file-size ceiling, prettier, jest. Live soak (Aaron, real model):
Title → New Game (confirm wipe of an existing world) → create a
character (mixing picked options and typed answers; two painted portrait
candidates, then an upload) → guided first run start to finish →
home-base chat where the monster uses the character's name → a battle
with the player fighting as a commanded ally.

## Deviations

- **M2 (file-size ceiling):** the player exemption pushed grandfathered
  `evolution.py` over its shrink-only cap, so eligibility moved out to
  its own concept file: `game/monster/evolution_eligibility.py` (used
  by both the service and the workflow re-check). `evolution.py` now
  holds only the ceremony itself.
- **M2:** the returning-monster pool (`memory/manager.py`) needed an
  explicit player exclusion the plan hadn't listed - the player is not
  in the ActiveParty rows, so without it the player could have walked
  out of the dark as their own returning encounter.
- **M2:** the first-run recruit auto-join (`dungeon/outcomes.py`) now
  checks for empty COMPANION rows instead of an empty party - with a
  player character the party is never empty, and the old check would
  have blocked the guided opening's first companion.
- **M3:** a creation that fails midway leaves a half-built row; the
  finalize workflow DISCARDS a partial player (stage != complete) and
  rebuilds fresh, while a complete one still refuses (New Game is the
  way to start over). The plan hadn't specified retry semantics.
- **M3:** uploads auto-select as the portrait (the player chose that
  file on purpose); painted candidates still require an explicit
  select. Player sapience is pinned to sapient/speech so chat gating
  can never bite the player's own voice.
- **M4:** a `backend-testdb` launch config (cmd sets DB_NAME to the
  test database) was added so the full creation flow can be soaked
  end-to-end on the real model + ComfyUI without touching the dev
  world. The whole wizard was verified live this way (options → forge
  → paint → upload guardrails → select → opening).
