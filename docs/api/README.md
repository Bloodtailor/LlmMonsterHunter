# Backend API Reference

Index for the Monster Hunter Game backend API. The reference is split by
domain — this file covers the conventions that apply everywhere, then
links to the per-domain files.

## Reference files
- [Monsters & Roster](monsters-and-roster.md) — monster generation, listing, abilities, card art, following list, active party, New Game, and the player character (creation wizard + portrait)
- [Chat](chat.md) — home-base conversations with following monsters: persistent threads, streamed replies, memory extraction, and the rolling summaries that keep indefinite chats affordable
- [Inventory](inventory.md) — the party's items (LLM-adjudicated consumables) and CoCaTok victory keepsakes, where they come from, and how items are used
- [Dungeon & Battle](dungeon-and-battle.md) — the gameplay loop: entering dungeons, choosing paths, exploring locations, monster dialogues, free-form ability use, and turn-based battles
- [Generation & System](generation-and-system.md) — generation logs, health check, and the in-app test runner
- [Settings](settings.md) — the in-game settings panel's backend: LLM provider config (local vs DeepSeek), stored in the one table that survives New Game
- [Events & SSE](events-and-sse.md) — the SSE endpoint, the full event catalog, and how the frontend event registry consumes it
- [Data Models](data-models.md) — shared object shapes referenced across endpoints

## Base URL
- Development: `http://localhost:5000/api`

## Standard response format
Every JSON endpoint returns an envelope:
- **Success:** `{ "success": true, ...data }`
- **Error:** `{ "success": false, "error": string, ...context }`

## The async workflow model (read this first)

This is the single most important thing to understand about the API. Most
"do something expensive" endpoints — generating a monster, generating an
ability, entering a dungeon, choosing a path, taking a battle turn — do
**NOT** return the result in the HTTP response. They queue a **workflow**
and return immediately:

```json
{ "success": true, "workflow_id": number }
```

The actual work happens on a background queue, and results are pushed to
the client over **SSE** (Server-Sent Events). A consumer must:
1. Open the SSE connection (`GET /api/sse/events`) once, up front.
2. Call the action endpoint and get back a `workflow_id`.
3. Watch SSE for streamed tokens, domain events (e.g. `monster.created`),
   and the terminal `workflow.completed` / `workflow.failed` event.

The only endpoints that return data synchronously are the read-only ones
(listing monsters, fetching state, reading logs) and the roster mutations
(following/party changes). See [Events & SSE](events-and-sse.md)
for the event catalog and the workflow types.

## HTTP status conventions
- `200` — `success: true` (and also returned for handled `success: false`
  validation errors on some read endpoints; always check the `success` flag,
  not just the status code)
- `400` — validation / business-rule failure
- `404` — resource not found
- `500` — unhandled server error or a failed workflow *queue* request

## Notes
- `GET /api/health` → `{ "status": "healthy", "message": string, "api_version": "2.0" }`
- Backend state that persists across requests (dungeon run, active battle)
  lives in the `global_variables` table, keyed by `dungeon_state` and
  `battle_state`. Hidden information (a path's pre-assigned event and
  destination) is stored there but stripped from any response that reaches
  the client. The dungeon run's rolling `dungeon_log` also lives there and
  is fed (budget-clamped) into every dungeon LLM generation.
