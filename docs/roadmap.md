# Gameplay Roadmap — where the fun is

**Written 2026-07-07** after a full review of the shipped initiatives and
every "out of scope" list in `docs/plans/`. This is a *design* document:
each entry is sketched deeply enough that an assistant can expand it into
a proper plan doc (per the repo process: review → plan doc → approval →
milestones) without re-deriving the design intent.

## The thesis

The game's engine rooms are built: generation, battles, memories,
evolution, runs with goals and stakes, the chronicle. What the game is
still light on is **drama between the characters** — and drama is the
one thing this architecture produces almost for free, because the cast
already has personas, memories, and affinity. The next initiatives
should make the monsters *want things* and *know each other*, so runs
stop being a sequence of events and start being chapters in an ensemble
story. Structural variety (regions, packs) comes after the cast is alive.

Ranked by fun-per-effort. Effort scale: S ≈ a settings-panel initiative,
M ≈ Evolution Altar, L ≈ Game Loop v1.

---

## 1. Monster Requests — the cast starts driving the plot (M)

**Deferred seed:** "monster-initiated messages" (monster-chat plan).

**The fantasy.** You sit at the campfire and *a monster comes to you*:
Thornback wants to return to the cavern where she was defeated before
she joined you; Miremaw dreams of tasting a storm-fruit that only grows
in high places; someone wants to confront the rival who humiliated them
(see #2 — these two initiatives feed each other). Personal quests,
authored by the cast, sourced from their own memories.

**Mechanics.**
- After each run (chronicle time) and occasionally at the home base, a
  workflow gives 1–2 monsters a chance to form a **request**. The prompt
  gets the monster's persona + relevant memories and picks from a
  **request-type enum**: `revisit` (a place/monster from its past),
  `seek` (a described thing it wants found), `confront` (a remembered
  foe), `accompany` (wants to be in the party for the next run),
  `ritual` (wants an evolution / a ceremony / a talk).
- Each request carries a **weight ladder** the LLM chooses:
  `whim → wish → need → vow`. Code owns the consequences: fulfilling
  moves affinity up by a weight-scaled amount and mints a memory;
  ignoring a `need`/`vow` for several runs decays affinity and can push
  a wary monster toward leaving. Whims expire silently — no nagging.
- Fulfillment detection is **refereed, not scripted**: at chronicle
  time, an LLM judge sees the run log + the open requests and rules
  `unaddressed / progressed / fulfilled / betrayed` (another ladder).
  This avoids brittle quest-flag code entirely.
- Run integration: an open request can be offered as an optional
  **run goal variant** on the expedition notice ("Thornback watches you
  study the map…"), reusing the existing goals/stakes machinery.

**Why it's #1.** It converts existing infrastructure (memories,
affinity, goals, chronicle) into *motivation*. The player stops asking
"what do I want to do?" and starts asking "who do I want to do right
by?" — that's the emotional core this game is built to have.

**Architecture.** New workflow(s) in a `registered_workflows.py` beside
chat/dungeon ones, handlers in a sibling module; requests are a new
table (monster_id, type, weight, text, status, source memory ids);
judge runs inside the existing chronicle workflow as an extra step (new
step names — additive, so no step-name-contract breakage). Frontend: a
request indicator on monster cards + a campfire "someone approaches
you" moment (reuse chat panel).

---

## 2. Nemesis Arcs — enemies that remember you back (M)

**Deferred seed:** returning monsters already exist (hostile/friendly/
wary); this promotes the hostile branch into a system.

**The fantasy.** The monster that wiped your party doesn't just
reappear — it has *dwelt* on you. It evolved off-screen. It taunts you
with specifics ("your Thornback still favors her left side"). Beating a
nemesis is the best story a run can produce; being beaten by one twice
makes it a legend.

**Mechanics.**
- When a battle ends in defeat (or a foe flees victorious), code marks
  the foe a **rival candidate**. A post-run workflow promotes at most
  one to nemesis — scarcity is what makes it special.
- Nemesis state ladder, code-owned progression, LLM-narrated flavor:
  `brooding → emboldened → vengeful → infamous → legend`. Each rung
  grants a code-owned growth budget (reuse the growth system) and one
  LLM-chosen upgrade from a word menu (new ability variant, tactic,
  title). Off-screen time = number of runs since the encounter.
- Reappearance uses the existing returning-monster hook, weighted up
  for nemeses; the encounter intro prompt gets the full grudge history.
  Defeating a nemesis mints a high-weight memory for every party member
  present and a chronicle centerpiece; recruiting one (the existing
  negotiation system already allows it!) should be rare, hard, and the
  single best "get" in the game — a `vow`-weight event.
- Valve: max 1–2 active nemeses; a `legend` that is never fought again
  retires into the chronicle as lore rather than scaling forever.

**Why now.** It's the villain-shaped hole in the ensemble story, it
reuses returning-monsters + growth + negotiation nearly wholesale, and
it pairs with #1 (`confront` requests target nemeses).

---

## 3. Party Bonds — the monsters know each other (M–L)

**Deferred seeds:** group chats (monster-chat), social structure →
group size (CMDTS), affinity system (game-loop).

**The fantasy.** Affinity today is player↔monster. Add
monster↔monster: two creatures who survived three runs together banter
in the dungeon, defend each other in battle, and grieve if one falls.
A proud apex predator resents sharing a party with a chittering scavenger
— until a battle changes its mind.

**Mechanics.**
- Pairwise **bond ladder** (word ladder, stored per unordered pair):
  `strangers → wary → acquainted → comrades → bonded → inseparable`,
  with a parallel friction track: `friction → rivalry → feud`. LLM
  proposes movements at memory-extraction time (it already reads the
  logs); code clamps movement to ±1 rung per run — the valve.
- Code-owned effects: `bonded+` pairs unlock a battle **combo action**
  (a new battle option whose *narration* is LLM but whose availability
  is code); `feud` pairs occasionally refuse coordination (wary-autonomy
  machinery reused). Dungeon events and campfire scenes get the pair's
  bond word in context, which is where most of the fun actually lands —
  the prose changes.
- **Group campfire chat** ships here: pick 2–3 monsters, one shared
  conversation, one speaker per turn chosen by the LLM from a roster
  (enum choice, so code controls turn-taking). This is the deferred
  "group chats" item, and bonds give it a reason to exist.
- V1 valve: bonds only among current-party members + the player;
  no full N×N sanctuary matrix (cap the rows, prune `strangers`).

**Why it's worth L-ish effort.** It multiplies every existing surface
(battle, dungeon prose, chat, chronicle) instead of adding a new one.
This is the initiative that makes the party feel like a *cast*.

---

## 4. Regions & the World Map — structural variety (L)

**Deferred seeds:** multi-dungeon world map (game-loop), taxonomy/
biome depth (CMDTS), style-reference images (cloud-gen).

**The fantasy.** Runs stop being "a dungeon" and become "an expedition
*into the Emberfen*". 3–5 persistent regions, each with a biome, a
taxonomic bias (CMDTS taxonomy finally pays rent), a visual identity
(per-region style-reference for Gemini art — cashing the deferred
style-reference idea), and a **regional mystery** that reveals itself
across repeated visits.

**Mechanics.** Regions are rows, not content: name, biome words, danger
ladder position, style-ref image, a rolling regional summary (reuse the
summary system) of what you did there. The expedition notice becomes a
choice of destination; returning monsters and nemeses (#2) live in home
regions; `revisit` requests (#1) point at real places. Code owns the
region list and danger scaling; the LLM owns everything felt.

**Sequencing note.** Deliberately after #1–3: variety without drama is
scenery. With requests, nemeses, and bonds live, regions give all three
somewhere to live.

---

## 5. Player Arcs — the ninth party member grows too (S–M)

**Deferred seed:** player evolution / re-art (new-game plan).

The player is in the party but is the only member without growth. Small
version: at chronicle time the LLM may award a **title** from earned
deeds (word menu: `Riddle-Solver`, `Oathkeeper`, `Beast-Friend`…);
titles are context everywhere personas are, and monsters react to them.
Medium version: a home-base **player evolution** ceremony (reuse the
altar pipeline wholesale, guidance from the player) with portrait
re-paint via reference image — the tech shipped with monster evolution;
this is mostly wiring + prompts. Ship the small version inside any
nearby initiative; the ceremony can wait for a quiet milestone.

---

## Parking lot (real ideas, wrong decade — reasons recorded)

- **Pack encounters** (CMDTS social structure → group size): genuinely
  good, but battle UI + referee complexity is the game's most fragile
  area; do it after Bonds proves multi-actor scenes work. The
  negotiation-with-the-alpha version is the fun one.
- **Dungeon chat** (deferred in monster-chat): mostly subsumed by
  Bonds' dungeon banter + Requests' run integration; revisit only if
  players still want free-form mid-run talk after those ship.
- **Economy/shops/trading:** the game's currency is affinity and
  memories; a gold economy fights the theme. CoCaToks already cover
  "treasure." Revisit only with a design that trades in *stories*.
- **Sound/music:** high polish value, zero LLM leverage, real cost.
  After regions, an ambient-loop-per-biome cut could be cheap enough.
- **Per-purpose model routing** (cloud-gen deferred): engineering
  optimization, not gameplay; do it when cost data from real play says
  which purposes deserve a cheaper model.
- **Save profiles / multi-save:** wait for a second regular player.

## Suggested order

1. **Monster Requests** (#1) — one M initiative, immediate drama payoff.
2. **Nemesis Arcs** (#2) — pairs with requests; villains enter.
3. **Party Bonds** (#3) — the big ensemble upgrade (includes group chat).
4. **Regions** (#4) — structure, art identity, and a home for all of it.
5. **Player title track** (#5-small) folded into whichever of the above
   is in flight when it fits; the ceremony afterward.

Interleave `docs/plans/codebase-health.md` milestones between
initiatives as palate cleansers — M1/M2 before Requests would be a
clean start.
