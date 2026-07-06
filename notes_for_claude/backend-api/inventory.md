# Inventory API

The party's possessions: **Items** (LLM-generated consumables the referee
adjudicates when used) and **CoCaToks** (unique keepsake card tokens
commemorating battle victories — view-only, never deleted).

See [Data Models](data-models.md) for `ItemObject` and `CoCaTokObject`.

## Where possessions come from
- **Treasure path events** (~9% of paths, `backend/game/dungeon/events.py`):
  the `choose_path` workflow generates an item fitting the location, emits
  `inventory.item_added`, streams discovery narration
  (`treasure_text_generation_id` in a `workflow.update` step), and returns
  `{ "event": "treasure", "item": ItemObject, ... }`.
- **Dialogue rewards**: the `reward` outcome of `respond_to_monster` grants
  an item themed on the granting monster and the conversation; the workflow
  result carries `"item": ItemObject`.
- **Battle victories**: every `victory` outcome of `battle_turn` mints a
  CoCaTok from the battle summary (emits `inventory.cocatok_added`); the
  result carries `"cocatok": CoCaTokObject` for the frontend pickup ceremony.

## Endpoints

### GET /inventory
Paged listing of one kind.
**Query params:**
- `kind?: string` — `items | cocatoks` (default `items`)
- `limit?: number` (1–1000), `offset?: number` (default 0)

**Success:**
```json
{
  "success": true,
  "kind": "items",
  "entries": [ItemObject | CoCaTokObject],
  "total": number,
  "count": number,
  "pagination": { "limit", "offset", "has_more", "next_offset", "prev_offset" }
}
```

### GET /inventory/counts
**Success:** `{ "success": true, "item_count": number, "cocatok_count": number }`

## Using items

One use is spent per use regardless of the outcome; at zero uses the item
is DELETED (emits `inventory.item_consumed`, otherwise `inventory.item_updated`).

### POST /dungeon/use-item (outside battle)
Queues a `use_dungeon_item` workflow. The referee reads the item's
description and judges the effect (`none|heal_light|heal_major|reveal`,
healing sticks only to party members — same rules as ability use).
**Request:** `{ "item_id": number, "target_type": "path"|"monster"|"location"|"custom", "target_id"?, "target_text"? }`
**Success:** `{ "success": true, "workflow_id": number }`
**Workflow result:** `{ "narration", "effect", "item_spend": { "consumed", "item_id", "name" }, "party_conditions" }`

### Battle: the `item` action (costs the turn)
`POST /battle/turn` accepts `{ "type": "item", "item_id": number, "target_id"?: string }`.
Target is optional — no target means the acting monster uses it on itself.
Resolved through the same referee/impact ladder as attacks and abilities.
