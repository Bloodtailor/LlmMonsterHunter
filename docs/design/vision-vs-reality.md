# Vision vs. Reality — the Feb 2025 SDLC, read back in July 2026

A retrospective. It sets the original planning document
(`Monster Hunter Game.md` — the Feb 2025 Waterfall SDLC plus the June
2025 MVP pivot) against the game as it actually stands, and names what
was kept, what was thrown away, and what is still owed.

The short version: **the throwaway idea in "Thought 1" became the entire
architecture, the elaborate scaffolding that was documented most
carefully got thrown away, and the "central story" sketched last is the
thing only now being built.** That is a healthy pattern — it means the
build was driven by what actually worked, not by the paperwork.

Companion docs: [../architecture.md](../architecture.md) for how the
pieces fit today, [../roadmap.md](../roadmap.md) for what's next,
`docs/plans/` for the per-initiative history that got us here.

## 1. The methodology arc played out as predicted

The MVP doc (June 2025) diagnosed the Feb 2025 Waterfall attempt as a
motivation-killer and pivoted to MVP-first. Where the project is now
vindicates that call *and* has grown a third phase the doc didn't name:
a **lightweight-but-real process** (`review → plan doc → approval →
milestones`, one plan doc per initiative in `docs/plans/`).

Waterfall didn't come back — but neither did seat-of-the-pants MVP mode
stay. The middle path won: the plan docs are the "documentation
overhead" of Feb 2025, except each covers ~1 initiative and is written
*just before* building it, so it never goes stale enough to demoralize.

## 2. The least-developed idea became the spine

"Thought 1" is three sentences: *"Perhaps it is better to not do math at
all… the LLM could assign a state for each monster such as injured,
heavily injured, incapacitated."*

That is now the **referee philosophy** — the single most load-bearing
decision in the codebase (`game/battle/constants.py`):

```
CONDITION_LADDER = ['fresh', 'scuffed', 'wounded', 'battered', 'critical', 'incapacitated']
RESOURCE_LADDER  = ['brimming', 'steady', 'strained', 'drained', 'spent']
```

And the payoff: directly below Thought 1, the notes pose **"Battling
Option 1 (LLM calculates outcomes) vs Option 2 (convert to numbers, game
logic calculates)"** — and never resolve it. It got resolved by building
*both*. This API-first repo is Option 1; the sibling
`LlmMonsterHunter-Local` fork is Option 2 (math battles). The fork in the
road drawn in Feb 2025 is now two literal repositories.

## 3. Feature scorecard

Vision (Feb 2025) → MVP scope (June 2025) → today.

| Original vision | MVP scope | Where it is now |
|---|---|---|
| Every monster LLM-generated: persona, backstory, abilities, stats, image | simplified | **Shipped, at full vision** — plus CMDTS taxonomy data (`monster/cmdts_data.py`) |
| Evolution: 20+ trigger conditions, full regen of stats/art/persona | "title change only" | **Shipped past MVP, at full vision** — Evolution Altar: same monster id, regenerated persona/art, lineage table. The 20 triggers became one home-base ritual. |
| Battle: LLM processes outcomes, no explicit math | "basic math combat" | **Shipped at full vision** (Option 1) — word-ladder referee, not the MVP's math shortcut |
| Monster chat / roleplay | ✅ | **Shipped** — Campfire Chat, with memory extraction + rolling summaries |
| Memories affect battle/chat/evolution | (not in MVP) | **Shipped** — cross-run memories, returning monsters |
| Capture by consent (convince them) | simplified | **Shipped** — affinity ladder `wary → familiar → trusting → devoted`; a wary monster acts on its own |
| In-dungeon campsite (monster-to-monster narrative) | (not in MVP) | **Shipped** — `dungeon/handlers/camp.py` |
| Three-door dungeon, traps/treasure/monster | ✅ | **Shipped**, plus themed runs, goals, stakes, chronicle (Game Loop v1 — beyond original) |
| Central story: a wish-granting power every monster seeks | story was "framework, not player-facing" | **Only now becoming real** — the Wish Engine design doc |
| Save at home / load at startup | save/load | **Replaced** — continuous DB persistence; "New Game" wipes the world instead of save files |
| XP → level up → % chance new ability | simplified | **Dropped entirely** — no XP/leveling in code; growth is word-ladder + affinity driven |
| Player is an implicit camera | — | **Diverged/expanded** — the player is now a *character in the party* you chat as |

## 4. Where reality contradicted the plan

- **The tech stack specified most confidently is the part most wrong
  now.** Feb 2025 locked in Pygame, Llama-cpp-python, ComfyUI, "8GB VRAM
  NVIDIA required." Today: **Pygame was never used** (React-only), and
  generation is **cloud-first** — DeepSeek for text, Gemini for images —
  with local llama-cpp demoted to *one provider behind a seam*. The
  hardware-requirements section is obsolete in the best way: the
  1M-token context floor assumes a cloud model, not a specific GPU.

- **The taxonomy was over-engineered; the story was under-engineered.**
  CMDTS (the Comprehensive Multi-Dimensional Taxonomy System —
  Domain/Kingdom/Phylum… down to "Magic-dependent" diet) got the most
  elaborate treatment in the notes. It survives only as `cmdts_data.py`
  and a plan doc whose deep-persona direction was superseded by the
  local-first pivot. Meanwhile the **wish-granting story** — explicitly
  called "not a narrative for the player, but a framework" — turned out
  to be the most durable idea and is now getting its own engine. The
  abstract creative frame beat the concrete data schema.

- **The 20 evolution triggers collapsed into 1.** All those conditions
  (level 10 + 3 wins + Evolution Stone, meteor showers, weather,
  fusion…) were an idea-dump, and the build correctly ignored almost all
  of them for a single legible ritual. The clearest case of the MVP
  doc's "track enhancement ideas separately" discipline actually
  holding.

## 5. What the original vision still owes

The [roadmap](../roadmap.md) thesis — *"the engine rooms are built;
what's light is drama between the characters"* — maps almost 1:1 onto the
parts of Feb 2025 not yet reached:

- **"Monster Reactions" / monster agency** (the notes) → **Monster
  Requests** (roadmap #1): the cast starts driving the plot.
- **The wish-granting story** → the **Wish Engine** design doc.
- **"Emergent stories… monsters with their own choices"** → still the
  north star; now reachable *because* personas + memories + affinity
  already exist.

## Bottom line

Measured against Feb 2025, the project delivered **more than the MVP
promised and, on the systems that mattered (generation, battle,
evolution, memory, chat), essentially the full original vision** — while
discarding the RPG scaffolding (XP, levels, save files, Pygame, most
evolution triggers, the taxonomy) that felt essential on paper but
wasn't. The one genuine gap is the same one the original document itself
flagged under "future refinements": *why* the monsters do any of this.
The wish-granting premise written last is the piece that turns the
shipped mechanics into a story — and it's the next thing on deck.
