# Data Models

Shared object shapes referenced across the API. Field names are the
backend's `snake_case` JSON. (The frontend transforms these to camelCase in
`api/transformers/`, but the wire format is what's below.)

## MonsterObject
```json
{
  "id": number,
  "name": string,
  "species": string,
  "description": string,
  "backstory": string,
  "stats": {
    "max_health": number,
    "current_health": number,
    "attack": number,
    "defense": number,
    "speed": number
  },
  "personality_traits": string[],
  "abilities": [AbilityObject],
  "ability_count": number,
  "card_art": CardArtObject,
  "created_at": string,
  "updated_at": string
}
```
`stats.speed` is used by the battle system to weight turn order.

## AbilityObject
```json
{
  "id": number,
  "monster_id": number,
  "name": string,
  "description": string,
  "ability_type": string,
  "created_at": string
}
```
`ability_type` is free-form LLM text (e.g. `attack`, `support`, even
`attack; support`). The battle referee reads the ability's `description`,
not its type, so the type has no mechanical meaning.

## CardArtObject
```json
{
  "has_card_art": boolean,
  "relative_path": string|null,
  "exists": boolean,
  "url": string|null
}
```
Serve the image via `GET /api/monsters/card-art/{relative_path}`.

## GameStateObject
```json
{
  "following_monsters": FollowingMonstersObject,
  "active_party": PartyObject,
  "dungeon_state": { "in_dungeon": boolean, "current_state": object|null },
  "game_status": "home_base" | "in_dungeon"
}
```

## FollowingMonstersObject / PartyObject
```json
{ "ids": number[], "count": number, "details": [MonsterObject] }
```

## LocationObject
```json
{ "name": string, "description": string }
```

## PathObject
A path onward from a location. **Public** shape (what the client receives —
the hidden `event` and pre-generated `destination` are stripped server-side):
```json
{ "name": string, "description": string, "type": "path" | "exit" }
```
Paths are keyed `path_1`, `path_2`, … in the `paths` object. A path is a
*route* (a door, stair, tunnel), not the place it leads to.

## BattleSnapshot
Public battle state (nothing is hidden in battles).
```json
{
  "in_battle": boolean,
  "phase": "ready"|"awaiting_player_turn"|"awaiting_player_response"|"processing"|"victory"|"defeat",
  "turn_count": number,
  "pending_actor": string|null,     // ally monster id whose turn it is
  "pending_talk": { "speaker_id": string, "dialogue": string }|null,
  "resolution": "combat"|"joined"|"yielded"|"fled"|"spared"|null,
  "allies":  { "[monster_id]": BattleEntry },
  "enemies": { "[monster_id]": BattleEntry }
}
```

### BattleEntry
```json
{
  "name": string,
  "condition": "fresh"|"scuffed"|"wounded"|"battered"|"critical"|"incapacitated",
  "defending": boolean,
  "fled": boolean        // enemies only
}
```
The condition ladder is Python-owned. The LLM referee returns an **impact**
word per action — `none | light | heavy | devastating | heal_light |
heal_major` — and Python maps it to steps along the ladder (defending
softens incoming harm by one step). A side is beaten when every member is
`incapacitated` (enemies: or `fled`).

## GenerationLogObject
```json
{
  "id": number,
  "generation_type": "llm"|"image",
  "prompt_type": string,
  "prompt_name": string,
  "status": "pending"|"generating"|"completed"|"failed",
  "priority": number,
  "duration_seconds": number|null,
  "attempts_used": number,
  "max_attempts": number,
  "is_completed": boolean,
  "is_failed": boolean,
  "llm_data": object|null,    // includes parsed_data / response_text for llm
  "image_data": object|null
}
```
