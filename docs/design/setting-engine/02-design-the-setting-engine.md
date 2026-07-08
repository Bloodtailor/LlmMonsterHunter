# 02 — Designing the Setting Engine

## The core insight: it's a one-level extension of what you already do

The project's spine is *"the LLM picks words; code owns numbers."* Combat
doesn't do HP math — the referee picks an impact **word** (`light`,
`heavy`, `devastating`) and Python maps that word to a step on a
code-owned ladder, then applies caps and valves.

A Setting Engine adds exactly one level to that sentence:

> **The Setting owns the words. Code owns the positions and effects. The
> LLM picks which word.**

Concretely, for the wellbeing ladder:

- **Code owns** (universal, never changes per setting): there are 6
  rungs; rung 5 = out of the fight; an impact of `heavy` moves you 2
  rungs; the softlock valve; the fairness guardrail; the stat math.
- **The Setting owns** (the lexicon at each rung): fantasy says
  `fresh…incapacitated`; pirates say `hale…out cold`; highschool says
  `composed…humiliated`.
- **The LLM still just picks** which severity happened this turn.

This is beautiful because it means **the referee logic, the caps, the
valves, the guardrails — none of it is touched**. You're only swapping
the vocabulary the referee reads and writes. The entire "code owns the
rules" contract is preserved. That's the difference between a reskin and
a rewrite.

### The trick that makes it safe: canonical positions, themed labels

Layer 3 in the audit flagged the blocker: code compares against literal
strings (`if condition == 'incapacitated'`). If labels become
Setting-variable, those comparisons break.

The fix: **code works in canonical/positional terms; only the
presentation and prompt layers translate.**

- Internally the ladder is always positions `0..5`; "out of the fight"
  is always "position 5," never a string. `ABILITY_POOL_BY_TYPE` keys on
  canonical pool ids `pool_a / pool_b`, not `stamina / mana`.
- When building a **prompt**, a translation layer renders position 5 as
  the Setting's word (`incapacitated` / `out cold` / `humiliated`).
- When **parsing** the referee's reply, the same layer maps the themed
  word back to a canonical position (fuzzy-matched, exactly like
  `normalize_choice` already does).

So the setting is a **lexicon bolted onto a fixed skeleton**. The
skeleton is code; the flesh is data. This is the single most important
mechanism in the whole idea.

---

## What a "Setting" actually is (the schema)

A Setting is a structured content pack. Draft slots:

```
Setting
├─ id, display_name, one_line_premise
├─ lexicon/                 # Layer 1: the noun bag
│    entity_singular, entity_plural, world_name, run_noun,
│    home_base_noun, conflict_noun (battle→"duel"/"argument"),
│    recruit_verb, ...  (~20-30 terms)
├─ entity_frame/            # Layer 2: what an entity IS
│    ├─ classification_tree # replaces TAXONOMY_TREE (or omitted)
│    ├─ aspects             # replaces ELEMENTS (0-2 from a list, or none)
│    ├─ discipline_tree     # replaces CLASS_DOMAINS (training/craft)
│    ├─ origin_options      # replaces CREATION_MECHANISMS
│    ├─ categorical enums   # size, "habitat", "diet"... or dropped
│    └─ verbal: bool        # do non-speaking entities exist? (sapience)
├─ ladders/                 # Layer 3: labels only, positions are code
│    wellbeing_labels[6], reserve_pools[{id,label}], impact_words{},
│    danger_labels[3]
├─ art_direction/           # the Gemini style directive per setting
│    style ("oil painting" / "photoreal" / "anime"), framing, palette
└─ examples/                # 1-2 exemplar entities to anchor tone
```

The **contract** is: the engine defines the *slots and their shapes*;
every Setting must fill them; code only ever addresses slots, never
literal fantasy values. `Fantasy` becomes the reference implementation
of this schema (the acceptance test from the README).

Two honesties about the schema:

1. Some slots are legitimately **optional/absent** in some settings.
   Highschool has no `aspects` (elements) and no `classification_tree`
   in the biological sense. The engine must treat "this setting has no
   aspects" as first-class — the generation stage that asks for elements
   simply doesn't run, or asks for the setting's substitute. This is
   real branching, not pure substitution. (More in doc 03.)
2. The persona stages (inner life, social self) barely touch the schema
   — they're already generic. A Setting mostly reshapes the *identity /
   ecology* front half of entity generation, the *nouns* everywhere, and
   the *ladder labels* in battle.

---

## Where it plugs into the layered architecture

The good news: there are natural choke points, so this doesn't mean
threading a `setting` argument through 200 call sites.

- **One global for the active Setting.** Mirror
  [run_context.py](../../../backend/game/dungeon/run_context.py) exactly:
  a `GlobalVariable` key (or a small table if settings get
  saved/authored), set at New Game *before* character creation, cleared
  by nothing (it's game-lifetime). A `game/setting/` module with a
  manager + accessors — the equivalent of `expedition_brief()` — returns
  the lexicon block and the themed ladders.
- **The prompt engine is the injection seam.**
  [prompt_engine.py](../../../backend/ai/llm/prompt_engine.py) has a
  single `build_prompt(template, variables)` funnel. Merge the active
  Setting's lexicon into `variables` *there*, automatically, so every
  template can reference `{entity_singular}` etc. without any call site
  knowing. Templates get rewritten once to pull nouns from variables.
- **CMDTS and battle constants split** into "skeleton" (stays in code,
  positional) and "lexicon" (moves into the Setting). The option-list
  builders (`taxonomy_options_text()`, `options_line()`) read from the
  active Setting instead of module constants.
- **The New Game flow** already wipes the world and runs character
  creation; the Setting picker slots in as the *first* step, because the
  player character is themed by the setting.
- **The image prompt** gains the Setting's `art_direction` block.

---

## Three strategies (and my recommendation)

**A — Vocabulary Skin (thin).** Only Layer 1. A lexicon of nouns,
injected via the prompt engine. Enums stay fantasy. *Verdict: cheap, and
a good Phase 1, but on its own the illusion cracks the moment a pirate
has a "genus" and an "elemental affinity." Ship it as a step, not the
destination.*

**B — Setting Pack (thick / content pack).** All three layers as data: a
setting is a directory/JSON bundle with its own lexicon, entity frame,
ladder labels, art direction, examples. Basically a **mod system**.
*Verdict: the real thing. Most work. This is where the abstraction earns
its keep.*

**C — LLM-authored Setting (AI-native).** At New Game the player types a
premise ("age-of-sail pirates, no magic, realistic") and a generation
workflow *authors the Setting pack* — fills every schema slot — once,
stored as a global. *Verdict: the most on-brand thing imaginable for a
game whose whole pitch is "the LLM does the worldbuilding." Also the
riskiest: quality/consistency of an auto-authored ontology, and it must
be validated against the schema so required slots are always filled.*

**Recommendation: B as the foundation, C as the payoff.** Define the
schema (B's contract). Hand-author two settings to prove it (Fantasy =
the migration; one wildly different setting = the stress test). *Then*
let the LLM author settings against the same validated schema (C). C
without B is a house with no frame; B without C is a great engine you
manually feed. Do B, earn C.

Crucially, **Phase 1 (Strategy A, just the nouns) is worth shipping even
if you stop there** — it pulls all the flavor into one legible place and
makes the game far more tunable. See doc 04 for the staging.
