# 01 — Where "fantasy" is actually welded in

Before designing anything, I went looking for the enemy: every place the
game *assumes* it's a fantasy monster world. It sorts cleanly into three
layers, shallow to deep. The depth is the whole story — Layer 1 is a
find-and-replace; Layer 3 is a worldview.

---

## Layer 1 — Surface vocabulary (shallow, easy)

Plain nouns and framing sentences in the prompt templates. Things like
"You are a creature designer for a **fantasy monster-catching game**,"
"where this **monster dwells**," "the **deep places**," "the
**campfire**," "**expedition**," "**dungeon**."

**Scope:** ~70 occurrences of `fantasy|creature|monster-catching|dungeon`
across the 12 files in
[backend/ai/llm/prompts/](../../../backend/ai/llm/prompts/). Concentrated
in `dungeon_generation.json` (18), `exploration_generation.json` (9),
and `battle_generation.json` (8).

**Nature of the problem:** these are just *words*. A pirate setting wants
"crew member" for "monster," "voyage" for "expedition," "the depths of
the map" for "the deep places." Nothing structural changes. This is the
part that makes the idea *feel* easy — and it is, for this layer.

**How you'd solve it:** a **lexicon** — a flat dictionary of substitution
terms the Setting provides (`entity_singular`, `world_name`,
`run_noun`, `home_base`, …), injected into every template. See doc 02.

---

## Layer 2 — The conceptual scaffolding (medium-hard)

The curated enums the LLM picks from. These aren't words you can swap —
they encode a **fantasy ontology**. Living in
[cmdts_data.py](../../../backend/game/monster/cmdts_data.py):

- **`TAXONOMY_TREE`** — a biological classification (Domain → Kingdom:
  Materium/Beast, Elementum/Primordial, Umbrium/Demonkind…). Every
  monster gets a `family/genus/species`. A pirate does not have a
  *genus*. A highschool student does not have a *kingdom*.
- **`ELEMENTS`** — fire/water/earth/lightning/… An age-of-sail deckhand
  has no "elemental affinity."
- **`CLASS_DOMAINS`** — Martial/Arcane/Primal/Divine… magic schools.
- **`CREATION_MECHANISMS`** — born/hatched/**summoned**/**risen**/… How a
  student "came to exist" is not on this list.
- **`SAPIENCE_LEVELS`** — feral/bestial/sapient/erudite, and it *gates
  chat* (`feral` monsters can't talk). In most non-fantasy settings
  everyone talks; the gate is fantasy-specific.
- Plus `SIZE_CLASSES`, `SUSTENANCE_SOURCES`, `FEEDING_STYLES`,
  `HABITAT_DOMAINS`, `BIOMES`, `SOCIAL_STRUCTURES`, `LIFECYCLE_STAGES`.

**Nature of the problem:** this is the *shape of what an entity is*. The
monster-generation pipeline
([monster_generation.json](../../../backend/ai/llm/prompts/monster_generation.json))
is four stages — **identity → ecology → inner life → social self** — and
the first two are almost entirely this fantasy ontology (taxonomy,
habitat, diet, elements, lifecycle).

**The critical observation:** stages three and four —
`monster_inner_life` (core wish, motivations, beliefs, fears, secret) and
`monster_social_self` (traits, likes, speech style, how to win it over) —
are **completely genre-neutral already**. A pirate has a wish and a
secret. A student has a speech style and things they respond poorly to.
**The persona system is the portable core; the identity/ecology stages
are the fantasy shell.** That seam is a gift — it tells you exactly where
to cut.

---

## Layer 3 — Mechanical labels that read as physical combat (subtle,
deepest)

The word ladders in
[battle/constants.py](../../../backend/game/battle/constants.py) and the
danger ladder in
[run_context.py](../../../backend/game/dungeon/run_context.py):

- Wellbeing: `fresh → scuffed → wounded → battered → critical →
  incapacitated`
- Reserves (stamina/mana): `brimming → steady → strained → drained →
  spent`
- Impact words the referee picks: `light / heavy / devastating`
- Pools literally named **stamina** and **mana**.

**Nature of the problem:** these describe a *physical fight to the point
of collapse*. In a highschool-drama setting, a "battle" is an argument or
a social showdown; "incapacitated" means "runs off humiliated," not
"unconscious"; "mana" makes no sense — the reserve is *composure* or
*nerve*. The *mechanic* is perfectly universal (a degrading ladder + a
referee who picks a severity word). The *labels* are genre-locked.

**Why this is the interesting layer:** it's the one people forget. You
can rename "monster" to "student" all day, but if the student gets
"battered" and spends "mana," the illusion dies. And unlike Layer 2,
these words are **referenced by value in code** — `INCAPACITATED =
'incapacitated'`, `RESOURCE_KEYS = ('stamina', 'mana')`,
`ABILITY_POOL_BY_TYPE`, comparisons against the literal strings. So you
can't just swap the strings; code would break. The fix (canonical
positions vs. themed labels) is the neatest idea in doc 02.

---

## What is *already* generic (the encouraging half)

Not everything is fantasy-shaped. These are genre-neutral as-is and need
no work beyond maybe relabeling:

- **The persona fields** (Layer 2 note above): wish, motivations,
  secret, speech style, likes/dislikes, how to win them over.
- **Party roles** — `tank / striker / skirmisher / support / controller
  / trickster` map onto *any* ensemble (a bruiser pirate, a jock, a
  schemer). `ROLE_STAT_PROFILES` and the size/rarity math are just
  numbers; they don't care about genre.
- **Rarity** — common→legendary works anywhere (a legendary duelist, a
  legendary gossip).
- **The whole run structure** — goals, stakes, danger ladder, the
  chronicle. "A voyage with a goal and real danger" needs no fantasy.
- **Memories, affinity, growth, evolution, returning characters,
  requests/nemesis/bonds (roadmap)** — all pure character drama.

**The audit's verdict:** the genre-locked surface is real but *bounded*.
It's essentially (a) a bag of nouns, (b) the monster identity/ecology
ontology, and (c) the combat vocabulary. Everything that makes the game
*feel alive* is already sitting on a genre-neutral spine. That's why this
is a plausible idea and not a rewrite — continued in doc 02.
