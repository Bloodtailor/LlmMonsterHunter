# 03 — The hard problems (where it fights back)

Doc 02 makes it sound clean. Here's where it isn't. These are the places
a naive "just swap the words" implementation breaks, and the honest
design questions each one forces.

## 1. Taxonomy is a worldview, not a word list

`TAXONOMY_TREE` (Materium→Beast, Umbrium→Demonkind, family/genus/species)
is the deepest fantasy assumption in the codebase. It presumes entities
are *classifiable biological/metaphysical kinds*. That's true of
monsters and false of pirates (who have ranks, homeports, reputations)
and students (grade, clique, archetype).

Two ways out:

- **Generalize the shape, let the Setting fill it.** The *engine* keeps
  "there is a curated tree of N tiers; the LLM classifies an entity into
  one branch, then invents the lower tiers." The *Setting* provides the
  tree. Fantasy: Domain→Kingdom. Pirates: Allegiance→Faction. Highschool:
  Grade→Clique. This preserves the code (`normalize_taxonomy_pick`, the
  option-list builder) and just re-fills the data.
- **Admit some settings have no taxonomy** and make the classification
  stage *optional* per the schema (doc 02's honesty #1). A slice-of-life
  highschool setting might skip categorization entirely.

The design question: **is a "curated tree the LLM picks a branch from" a
universal generation primitive, or a fantasy-monster feature?** I lean
"universal primitive, optionally present" — categorization is a genre-
neutral way to give the LLM guardrails — but it's a real fork.

## 2. Battle physicality — the reskin/rewrite boundary

For pirates, a cutlass duel is still a physical fight; the ladders reskin
cleanly (`hale…out cold`, stamina→`vigor`, mana→`grit`). But
"highschool drama" exposes the boundary: a "battle" there is a *verbal or
social* confrontation. Vocabulary reskin gets you most of the way —
`incapacitated`→`humiliated`, `mana`→`composure`, "attack"→"cutting
remark" — **because the turn structure, initiative, abilities, and
consequences are all mechanically identical.** A social showdown *is*
turn-based attrition with a different paint job. That's the good news:
more settings than you'd expect fit the existing combat skeleton.

**Where it genuinely breaks:** a setting that wants *no combat at all*
(pure relationship sim) or *fundamentally different resolution* (a
courtroom, a cooking contest with judged rounds). That's not a lexicon
change — it's new mechanics, and it's **out of scope for a Setting
Engine.** The clean rule to hold:

> A Setting may re-*label* any mechanic and may *omit* an optional
> generation stage. It may **not** change how a mechanic *works*. The
> moment a setting needs different rules, it's a new game mode, not a
> setting.

Drawing that line early is what stops this initiative from becoming
infinite. "Everything is turn-based attrition between characters with
personas" is the engine's actual genre — and it's a surprisingly wide
one.

## 3. Non-verbal entities and the sapience gate

`SAPIENCE_LEVELS` gates chat: `feral` monsters can't talk, impressions
get narrated instead. That's real, load-bearing branching (the chat
system checks it), and it's fantasy-specific — in pirates/highschool
everyone talks.

Generalize to a Setting flag: `has_nonverbal_entities: bool` (+ the
labels if so). Fantasy sets it true and keeps the four-rung sapience
ladder; most settings set it false and every entity speaks, so the gate
short-circuits. Low effort, but it's a reminder that **some Layer-2 enums
carry behavior, not just flavor** — you can't blindly move them to data
without moving the branch that reads them.

## 4. Art direction has to move too, or the illusion is half-built

The card-art pipeline implies fantasy creature portraits. A photoreal
pirate on a painterly-fantasy card frame looks broken. Each Setting needs
an `art_direction` block (style, framing, palette, negative prompts)
feeding the Gemini prompt. This is mostly additive — the
reference-image-evolution machinery already exists — but it's easy to
forget and it's half the felt experience. Note: realistic styles raise
the bar on coherence (a wrong-era pirate ship reads as broken in a way a
weird monster never does), so "realistic world" settings are *harder* for
image gen, not easier.

## 5. The persona is portable — but its *examples* and tone aren't

`monster_inner_life` / `monster_social_self` fields are generic (good),
but the *prose the LLM writes into them* drifts toward fantasy by default
because that's the training-data prior for "a creature with a wish." A
Setting needs 1-2 **exemplar entities** in its pack to anchor tone (a
fleshed-out pirate, a fleshed-out student), injected as few-shot
context, or generation will smuggle fantasy back in through voice even
when the nouns are right. This is subtle and will only show up in
playtesting.

## 6. Naming, save-compat, and mixed worlds

- **Save/world state.** The Setting is chosen at New Game and wipes with
  the world. But existing saves have no setting — they're implicitly
  Fantasy. Migration must default a null setting to Fantasy everywhere
  (the acceptance test enforces this anyway).
- **No mid-game switching.** Changing setting mid-world would leave a
  party of monsters in a pirate world. Setting is immutable per world;
  switching = New Game. State this loudly.
- **Don't mix layers by accident.** The per-run `theme`
  (`expedition_brief`) still exists *inside* a Setting — a "haunted"
  voyage within the pirate setting. Setting and run-theme compose; keep
  them orthogonal and named differently (README's naming flag).

## The through-line

Every hard problem resolves the same way: **push the variation into data
where it's genuinely just vocabulary; keep it in code where it's behavior
or math; and refuse it entirely when it's new rules.** The skill is
sorting each knob into the right one of those three buckets. The audit
(doc 01) is really that sorting exercise; these six are the cases where
the sort is non-obvious.
