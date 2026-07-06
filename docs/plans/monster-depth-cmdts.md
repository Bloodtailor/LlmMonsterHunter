# Monster Depth: Expanded Persona + CMDTS — Implementation Plan

Branch: `feature/monster-depth-cmdts`
Status: IMPLEMENTED (M1–M5, July 2026). Curated trees approved as drafted; both
§10 flags resolved as planned (code-derived stats, progressive save). Verify
offline with `python -m backend.tests.test_monster_templates`; judge generation
quality with `python -m backend.tests.generate_monster_profiles` (backend running).
Wipe the dev DB once after checkout: `python -m backend.tests.reset_db`.

## 1. Goal and locked decisions

Deepen every monster so the chat/recruitment loop has real content: a fleshed-out persona
(wish, fears, secret, voice, social hooks) and a Comprehensive Multi-Dimensional Taxonomy
System (CMDTS) that game systems can consume.

Decisions already made:

1. **Context tiers are binned by context window**: ~4096 → compact (basic info),
   ~8192 → standard (most info), larger → full (everything).
2. **Upper taxonomy ranks are curated** (fixed trees the LLM selects from); lower ranks
   are LLM-invented. Draft trees in §3 for review.
3. **Role, Class, and Profession all kept**, with distinct meanings:
   Role = mechanical party slot · Class = trained discipline (hierarchical, 0:m) ·
   Profession = what the monster *considers* its job (self-identity; may disagree with Class).
4. **All missing dimensions added**: sapience/communication, elemental affinity,
   size class, lifecycle stage.
5. **Per-monster strings/JSON for taxonomy** (no shared node tables yet; canonicalize
   later if a kinship feature needs it).
6. **Dev database is wiped** — no data migration. A reset script is added.

## 2. Data model changes (`backend/models/monster.py`)

Existing columns stay untouched so current consumers (battle/dungeon generators, frontend)
keep working: `name`, `species`, `description`, `backstory`, stats, `personality_traits`,
`card_art_path`. `species` is set equal to `taxonomy.species`.

New columns (all JSON payloads are per-monster strings — decision #5):

```python
rarity           = Column(String(20))    # common|uncommon|rare|epic|legendary
party_role       = Column(String(50))    # tank|striker|skirmisher|support|controller|trickster
generation_stage = Column(String(20))    # blueprint|persona|complete (progressive reveal)
taxonomy         = Column(JSON)          # biological lineage + display labels
class_taxonomy   = Column(JSON)          # list of trained disciplines (0:m)
ecology          = Column(JSON)          # flat CMDTS dimensions
persona          = Column(JSON)          # expanded persona fields
appearance       = Column(JSON)          # structured visuals for art + display
```

### JSON shapes (Rokk as the worked example)

```jsonc
"taxonomy": {
  "domain": "Materium",              // curated pick
  "kingdom": "Insectoid",            // curated pick
  "family": "Stoneshell Burrowers",  // LLM-invented
  "genus": "Petrascarab",            // LLM-invented
  "species": "Cave Petrascarab",     // LLM-invented; mirrored to species column
  "type_label": "Insectoid",         // derived display label (from kingdom)
  "race_label": "Beetle"             // derived display label (common name)
},
"class_taxonomy": [
  { "domain": "Martial", "discipline": "Bulwark Arts", "specialization": "Stoneshell Bastion" }
],
"ecology": {
  "social_structure":  { "primary": "colony", "notes": "colony destroyed; seeks a new one" },
  "creation_mechanism": "hatched",
  "habitat":           { "primary": "subterrain", "secondary": ["land"], "biomes": ["cavern", "mountain"] },
  "diet":              { "feeds": true, "sustenance": ["matter"], "feeding_style": "lithovore",
                         "notes": "grazes mineral-rich lichen" },
  "sapience":          "sapient",
  "communication":     ["speech"],
  "elemental_affinities": ["earth"],
  "size_class":        "small",
  "lifecycle_stage":   "adult",
  "activity_cycle":    "nocturnal"
},
"persona": {
  "moral_character": "Loyal and honorable",
  "beliefs": "The strong exist to shelter the weak.",
  "motivations": "The ache of a lost colony; safety is something you build for others.",
  "goals": ["Become a legendary defender", "Find ground worth guarding"],
  "core_wish": "To find a new colony and never again fail to protect one",
  "fears": ["Being the last of its line", "Cave-ins it cannot hold back"],
  "secret": "Rokk froze in fear during the earthquake and believes the colony died for it.",
  "likes": ["interesting stones", "quiet places", "loyalty"],
  "dislikes": ["loud noises", "sudden movements", "betrayal"],
  "hobbies": ["collecting stones", "burrowing"],
  "profession": "Guardian",
  "attitude_toward_strangers": "Cautiously optimistic; watches before trusting",
  "recruitment_lever": "Proof the party protects its own; an offer of belonging",
  "responds_well_to": ["patience", "respect", "calm"],
  "responds_poorly_to": ["loud noises", "aggression", "sudden changes"],
  "speech_style": "Terse, formal; geological metaphors; refers to itself by name",
  "social_bonds": { "drawn_to": "patient, steadfast types", "clashes_with": "loud tricksters" },
  "battle_line": "Intruder detected. Prepare to be crushed under the weight of the mountain!"
},
"appearance": {
  "visual_description": "A dog-sized beetle whose rocky shell blends into stone; strong mandibles, deep earthy-brown eyes.",
  "primary_colors": ["slate grey", "earthy brown"],
  "distinguishing_features": ["rock-like exoskeleton", "heavy mandibles"]
}
```

Mutability contract (matters when memories/evolution land; documented, not enforced yet):

- **Immutable birth facts**: taxonomy, creation_mechanism, size/lifecycle at creation, secret's origin.
- **Slow-changing**: beliefs, moral_character, core_wish (resolving a wish is an evolution event).
- **Living document**: goals, likes/dislikes, attitude_toward_strangers, social_bonds, recruitment_lever.

`to_dict()` gains all new fields (nested under their own keys, snake_case like the rest of the API).

## 3. Curated CMDTS reference data — FOR REVIEW

New file `backend/game/monster/cmdts_data.py`: plain constants, injected into generation
prompts as terse option lists, and used to normalize LLM output. **Edit freely — this is the
part you asked to review.**

### 3.1 Taxonomy tree (curated: Domain → Kingdom; free: Family → Genus → Species)

| Domain | Meaning | Kingdoms |
|---|---|---|
| **Materium** | natural mortal life | Beast · Insectoid · Verdant (plant) · Fungoid · Oozekind · Draconid · Kinfolk (goblinoid/humanoid peoples) |
| **Elementum** | element given will | Primordial (element embodied) · Wispkind (minor sprites) · Stormkind (living weather) |
| **Aetherium** | spirit and dream | Spiritkind · Feykind · Dreamborn |
| **Caelium** | celestial and astral | Celestial · Starborn |
| **Umbrium** | shadow and abyss | Demonkind · Shadekind · Nightmare |
| **Mortuum** | the risen dead | Revenant (corporeal) · Wraithkind (incorporeal) |
| **Artificium** | made things | Construct · Animatum (animated objects) · Simulacrum (imitation life) |
| **Anomalium** | the unclassifiable | Aberrant · Unfathomed (explicit "unknown" — cooler than null) |

`type_label` is derived from the kingdom (usually identical); `race_label` is the free-form
common name (e.g. "Beetle"). Taxonomy is 1:1 — every monster gets one; eldritch things get
Anomalium, never NULL.

### 3.2 Class tree (curated Domain; Discipline/Specialization free, 3 levels, 0:m)

Martial · Arcane · Primal · Divine · Cunning · Craft · Mystic
(untrained = empty list; example: Martial → Bulwark Arts → Stoneshell Bastion)

### 3.3 Flat dimension enums

| Dimension | Values |
|---|---|
| Rarity | common, uncommon, rare, epic, legendary |
| Party role | tank, striker, skirmisher, support, controller, trickster |
| Size class | tiny, small, medium, large, huge, colossal |
| Sapience | feral (instinct only — no chat, impressions narrated), bestial (reads tone, no speech), sapient (full speech), erudite (scholarly/ancient) |
| Communication | speech, telepathy, empathic, mimicry, none (0:m) |
| Elements | fire, water, earth, air, lightning, ice, nature, metal, poison, light, shadow, arcane (0:m) |
| Social structure | solitary, pair-bonded, pack, colony, tribal (one primary + free-text notes) |
| Creation | born, hatched, summoned, constructed, risen, spawned, transformed, primordial |
| Lifecycle | nascent, juvenile, adult, elder, timeless |
| Habitat domain | land, air, subterrain, water (one primary + 0:m secondary) |
| Biomes | jungle, forest, grassland, swamp, desert, tundra, mountain, cavern, volcanic, coast, abyssal-sea, ruins, settlement, skyrealm, astral, blighted (0:m) |
| Sustenance | matter, sunlight, mana, elemental-energy, life-essence, emotion, none (0:m — split from feeding style per review) |
| Feeding style | carnivore, herbivore, omnivore, detritivore, lithovore, none |
| Activity cycle | diurnal, nocturnal, crepuscular, ever-waking |

Consumers each dimension is designed for: habitat/biomes → dungeon spawn matching;
social structure → future encounter group size; sapience/communication → dialogue and
negotiation presentation; elements → abilities and referee flavor; size → art prompts and
battle plausibility; creation/diet → lore, chat content, recruitment bribes.

## 4. Generation pipeline (staged, ordered facts → persona → prose)

Replaces the single 400-token `detailed_monster`/`contextual_monster` call. Each stage is a
small JSON call chained through the existing workflow pattern
(`backend/game/monster/registered_workflows.py`), same public workflow names so routes
don't change. `generate_base_monster` and `generate_contextual_monster` share the chain;
contextual passes `{location_context}` into stages A1/A2/D (habitat must fit the location).

| Stage | Template (monster_generation.json) | Output | ~max_tokens |
|---|---|---|---|
| A1 Identity & lineage | `monster_blueprint_identity` | name, taxonomy (pick curated, invent lower, labels), rarity, role, size, lifecycle, creation | 350 |
| A2 Ecology & powers | `monster_blueprint_ecology` | habitat+biomes, diet, social, sapience, communication, elements, class_taxonomy | 350 |
| B Inner life | `monster_inner_life` | core_wish, motivations, goals, beliefs, moral_character, fears, secret | 350 |
| C Social self | `monster_social_self` | traits, likes/dislikes, hobbies, profession, attitude, responds_well/poorly, recruitment_lever, social_bonds, speech_style, battle_line | 450 |
| D Creative text | `monster_creative_text` | description, backstory (weaves wish + lineage + place), appearance JSON | 450 |

Each stage's prompt receives the prior stages' facts as context — that's what keeps the
backstory agreeing with the taxonomy. Prompts constrain field lengths ("one sentence each")
so full-tier context blocks stay bounded. Field values are normalized post-parse (lowercase,
invalid enum → sensible default) in the generator — the one place defensive code is warranted,
since it guards LLM output, not our own.

**Stats become code-derived** (flagged decision, §10): base spread by role × rarity
multiplier × size nudge ± 10% jitter, in a small table in `cmdts_data.py`. The current LLM
call just picks numbers in a range — that's noise, not balancing; the referee still narrates
magnitudes. One fewer LLM call and zero parse failures.

**Progressive save + reveal** (leans on the SSE investment): save the row after A2 with
`generation_stage='blueprint'` and emit `monster.created` (card appears fast with
name/taxonomy), then emit a new `monster.updated` event after B/C (stage `persona`) and D
(stage `complete`). New event in `backend/core/events/monster_events.py`; handler added in
`frontend/src/api/events/monsterEventHandlers.js`. Total wall time rises (~5 small LLM calls
vs 1 big) but the card is on screen after the first two.

**Downstream calls enriched**: ability generation variables gain class_taxonomy, elements,
and persona summary; `_build_card_art_prompt` is rebuilt from `appearance` + size_class +
type_label instead of concatenating prose.

## 5. Tiered monster context (the binned battle cards)

New builder `backend/game/monster/context_builder.py` replaces the three near-duplicate
builders (`dungeon/generator.py:build_monster_dungeon_details` + party variant,
`battle/generator.py:build_monster_battle_details`, `state/manager.py:get_party_details`),
keeping their side-tag/condition/defending decorations as parameters.

Tier resolution lives in `context_limits.py` next to the budget math:

| LLM_CONTEXT_SIZE | Tier | Per-monster block contains |
|---|---|---|
| < 6144 | **compact** | today's block + one identity line (type/race, rarity, role, size) + core_wish |
| < 12288 | **standard** | compact + speech_style, battle_line, likes/dislikes, responds_well/poorly, attitude, taxonomy line, habitat/diet line, elements |
| ≥ 12288 | **full** | standard + beliefs, fears, hobbies, social_bonds, profession, full CMDTS |

Two overrides on top of the bins:

- **Single-speaker prompts** (monster_question, monster_dialogue_turn, riddle/negotiation
  judging) always get the FULL block for the speaking monster — one monster's full persona
  fits even at 4096, and chat is the whole point. The party block in those prompts stays binned.
- **`secret` never enters battle-narration prompts at any tier** (the referee would leak it).
  It appears only in single-speaker dialogue prompts, with an explicit instruction: the monster
  knows its secret and guards it until trust is earned.

Dialogue/negotiation templates in `encounter_generation.json` are updated to exploit the new
fields (speech_style drives voice; responds_well/poorly and recruitment_lever become the
judge's rubric; sapience/communication controls whether it speaks at all or the LLM narrates
body language). `contextual_monster` template is deleted (superseded by the staged chain).

## 6. Frontend

- **Transformers** (`frontend/src/api/transformers/monsters.js` and the `app/transformers`
  copy — determine during build which is live, update accordingly): pass through rarity,
  partyRole, taxonomy, classTaxonomy, ecology, persona, appearance, generationStage.
- **MonsterCardDetails**: rarity + role badges beside the species badge; species badge shows
  `race_label`/`type_label`.
- **MonsterCardViewer (XL)**: two new sections — "Persona" (grouped persona fields) and
  "Taxonomy & Ecology" (lineage line + dimension chips). Small/medium cards unchanged.
- **SSE**: handle `monster.updated` (merge by id) so cards fill in as stages complete.

## 7. Database reset (decision #6)

`backend/tests/reset_db.py` following the existing `tests/` script pattern:
`db.drop_all()` + `create_all()` inside app context, with a y/N confirm. Run once after
checking out the branch. No migration tooling added (out of scope; note for later).

## 8. Verification

1. **Template smoke script** (`backend/tests/test_monster_templates.py`): render every new
   template with sample variables; fail on missing/extra placeholders (catches `.format` KeyErrors).
2. **Quality eval script** (`backend/tests/generate_monster_profiles.py`): generate N monsters
   end-to-end, dump full profiles for coherence review (taxonomy ↔ backstory ↔ habitat).
3. **Budget check**: with a full party of 4 + 3 enemies, print battle-prompt char counts at
   each tier vs `get_prompt_char_budget()`; verify compact fits 4096 with headroom.
4. **Live run**: generate monsters via the game tester UI with the real model; inspect prompts
   in the debug panel; run a dungeon with dialogue + battle + negotiation.

## 9. Milestones (each a reviewable chunk)

- **M1 Foundations**: `cmdts_data.py` (post-review §3), Monster columns + `to_dict`,
  reset script, transformer passthrough. *(No behavior change — old generation still works.)*
- **M2 Generation**: new templates, staged generator + normalization, code-derived stats,
  `monster.updated` event, enriched ability/art prompts.
- **M3 Context tiers**: shared builder, integrate into battle/dungeon/state, tier thresholds,
  single-speaker + secret rules, dialogue template updates.
- **M4 Frontend**: badges, viewer sections, updated-event handling.
- **M5 Tuning & docs**: run verification suite, iterate prompt wording, update
  `notes_for_claude/backend-api/` (data-models, monsters-and-roster).

## 10. Risks and flagged decisions

- **7B JSON reliability across 5 calls** — mitigated by small flat schemas, minimal
  required_fields, enum normalization; workflow error handling already reports
  `failed_at` + partial work.
- **Generation time per monster roughly doubles** — mitigated by progressive reveal;
  accepted cost of depth.
- ⚑ **Stats: code-derived vs LLM** — plan says code-derived (rationale §4). Veto if you want
  the LLM to keep picking numbers.
- ⚑ **Progressive save (3 emits) vs single save at the end** — plan says progressive; single
  save is simpler but the card appears only after ~5 LLM calls.
