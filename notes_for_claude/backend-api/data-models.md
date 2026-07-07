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
  "rarity": "common"|"uncommon"|"rare"|"epic"|"legendary",
  "party_role": "tank"|"striker"|"skirmisher"|"support"|"controller"|"trickster",
  "generation_stage": "blueprint"|"persona"|"complete",
  "taxonomy": TaxonomyObject,
  "class_taxonomy": [ClassEntryObject],
  "ecology": EcologyObject,
  "persona": PersonaObject,
  "appearance": AppearanceObject,
  "abilities": [AbilityObject],
  "ability_count": number,
  "card_art": CardArtObject,
  "created_at": string,
  "updated_at": string
}
```
`stats.speed` is used by the battle system to weight turn order. Stats are
CODE-derived from `party_role` × `rarity` × `ecology.size_class` (with jitter)
— the LLM never picks numbers. Rarity is code-rolled (weighted) and injected
into the generation prompt. `generation_stage` tracks staged generation:
the row exists from `blueprint` on and fills in via `monster.updated` events.

## TaxonomyObject
```json
{
  "domain": string,       // curated pick (8 domains, see cmdts_data.py)
  "kingdom": string,      // curated pick within the domain
  "family": string,       // LLM-invented lineage
  "genus": string,        // LLM-invented breed
  "species": string,      // LLM-invented; mirrored to the species column
  "type_label": string,   // display label, derived from kingdom
  "race_label": string    // plain-language look, e.g. "Beetle"
}
```

## ClassEntryObject
```json
{ "domain": string, "discipline": string, "specialization": string }
```
`domain` is a curated pick (Martial/Arcane/Primal/Divine/Cunning/Craft/Mystic);
the rest are LLM-invented. `class_taxonomy` is a list (0:m, empty = untrained).

## EcologyObject
```json
{
  "size_class": "tiny"|"small"|"medium"|"large"|"huge"|"colossal",
  "lifecycle_stage": "nascent"|"juvenile"|"adult"|"elder"|"timeless",
  "creation_mechanism": "born"|"hatched"|"summoned"|"constructed"|"risen"|"spawned"|"transformed"|"primordial",
  "habitat": { "primary": string, "secondary": string[], "biomes": string[] },
  "social_structure": { "primary": string, "notes": string },
  "diet": { "feeds": boolean, "sustenance": string[], "feeding_style": string, "notes": string },
  "sapience": "feral"|"bestial"|"sapient"|"erudite",
  "communication": string[],
  "elemental_affinities": string[],
  "activity_cycle": string
}
```
`sapience` gates dialogue: feral/bestial monsters cannot speak — encounter
prompts narrate their behavior instead. All enum values are normalized onto
the curated lists in `backend/game/monster/cmdts_data.py`.

## PersonaObject
```json
{
  "core_wish": string,          // THE driver - dialogue, recruitment, evolution
  "motivations": string,
  "goals": string[],
  "beliefs": string,
  "moral_character": string,
  "fears": string[],
  "secret": string,             // discovered through chat - never shown in UI or battle prompts
  "likes": string[], "dislikes": string[],
  "hobbies": string[],
  "profession": string,         // self-identity, may differ from class
  "attitude_toward_strangers": string,
  "responds_well_to": string[], "responds_poorly_to": string[],  // persuasion rubric
  "recruitment_lever": string,  // what would convince it to join a party
  "social_bonds": { "drawn_to": string, "clashes_with": string },
  "speech_style": string,       // the voice - drives all dialogue generation
  "battle_line": string         // signature confrontation line
}
```

## AppearanceObject
```json
{
  "visual_description": string,   // written for an artist - feeds card art prompts
  "primary_colors": string[],
  "distinguishing_features": string[]
}
```

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

## ItemObject
```json
{
  "id": number,
  "name": string,
  "description": string,      // referee-facing: what it IS and what it DOES
  "emoji": string,
  "uses_remaining": number,   // 1-3 at generation; item is DELETED at 0
  "source_note": string|null, // "Found at ..." / "Gift from ..."
  "created_at": string
}
```
The referee reads ONLY the description when the item is used — it must
carry the item's effect in prose.

## CoCaTokObject
```json
{
  "id": number,
  "title": string,
  "emoji": string,
  "color": string,            // curated frontend color-system name (e.g. "purple-mystic")
  "commemoration": string,    // collector's-card flavor text of the victory
  "event_type": "battle_victory",
  "location_name": string|null,
  "created_at": string
}
```
Keepsakes: view-only, no delete path. Rendered by the frontend CoCaTok
spinning-card component from color + emoji (no AI art).

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
  "fled": boolean,       // enemies only
  "stamina": "brimming"|"steady"|"strained"|"drained"|"spent",
  "mana":    "brimming"|"steady"|"strained"|"drained"|"spent"
}
```
The condition ladder is Python-owned. The LLM referee returns an **impact**
word per action — `none | light | heavy | devastating | heal_light |
heal_major` — and Python maps it to steps along the ladder (defending
softens incoming harm by one step). A side is beaten when every member is
`incapacitated` (enemies: or `fled`).

The reserve ladders work identically: the referee's optional
`stamina_cost`/`mana_cost` words — `none | minor | moderate | heavy |
restore_minor | restore_major` — step the pools (code defaults per action
type when the referee is silent). Ally pools persist across battles within
a run and refill on dungeon entry; enemy pools seed `brimming`.

## MemoryObject
One permanent remembered moment in a monster's life (table `monster_memories`).
```json
{
  "id": number,
  "monster_id": number,
  "run_id": number|null,             // the dungeon run it happened in
  "kind": "was_defeated"|"defeated_party"|"joined_party"|"yielded_to_party"|"fled_from_party"|"spared_party"|"let_party_pass"|"gave_reward"|"punished_party"|"talked_with_party"|"avoided"|"camp"|"growth"|"lesson"|"returned"|"run_complete"|"confided"|"grew_closer"|"shared_lore"|"learned_fact"|"voiced_wish",
  "content": string,                 // 1-2 past-tense sentences, prompt-ready
  "details": { "run_number?": number, "source?": string, "by?": string,
               "with?": string, "location?": string, "stat?": string,
               "amount_pct?": number, "battle_summary?": string,
               "exchange?": string, "message_span?": [number, number],
               "after_run_number?": number },
  "created_at": string
}
```
The last five kinds come from home-base chats (`details.source: "home_chat"`,
`message_span` = the chat_messages ids the extraction reviewed) — see
[Chat](chat.md).

## ChatMessageObject
One line of a monster's persistent home-base thread (table `chat_messages`).
```json
{
  "id": number,                      // ordering key (insertion order)
  "monster_id": number,
  "role": "player"|"monster",
  "text": string,
  "created_at": string,
  "updated_at": string
}
```

## DungeonRunObject
One row per journey into the dungeon (table `dungeon_runs`).
```json
{
  "id": number,
  "run_number": number,              // counts up over the whole save
  "ended_at": string|null,
  "result": null|"victory_exit"|"defeat"|"abandoned",  // null = active
  "summary": string|null,
  "created_at": string               // doubles as the start time
}
```

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
