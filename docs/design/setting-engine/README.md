# The Setting Engine — musings

*Exploratory thinking, not a plan doc. Written 2026-07-07 in response to
an idea: "what if one central building block changed the theme of
absolutely everything — pirates instead of monsters, a highschool
instead of a dungeon — chosen at the start, rippling through every
prompt."*

Nothing here is committed. These docs are me thinking out loud about how
the idea would actually look, work, and hurt. If it graduates, it
follows the real process (review → plan doc → approval → milestones).

## The one-sentence version

The game is already, secretly, a **character-drama engine wearing a
fantasy costume**. The parts that make it good — personas with wishes
and secrets, memories, affinity, a word-ladder referee, runs with goals
and stakes — are genre-agnostic. The fantasy (monsters, taxonomy,
elements, dungeons) is a skin on top. The idea is to make that skin a
**swappable, first-class thing** — a *Setting* — so the same engine can
run pirates on a real ocean or drama in a highschool.

## A naming problem, up front

**"Theme" is already taken.** [run_context.py](../../../backend/game/dungeon/run_context.py)
has a per-*run* `theme` — the flavor of a single dungeon expedition
("a haunted grove," "a flooded ruin"). It's injected via
`expedition_brief()` and lives for one run.

What this idea wants is bigger and permanent: the frame around
*everything*, chosen once at New Game. Calling both "theme" will cause
real confusion in code and conversation. Throughout these docs I call
the new concept a **Setting** (the genre/world you're playing in), and
leave "theme" meaning the per-run flavor. Other candidate names:
*Genre*, *World*, *Frame*, *Motif*. Pick one and hold it.

## The acceptance test that keeps this honest

> **The current fantasy game must become "the Fantasy setting" — a data
> pack the engine loads — and play byte-for-byte identically.**

If fantasy can't be cleanly lifted out into a swappable pack, the
abstraction is wrong and we'd be building a second game instead of a
reusable engine. Every design choice below is measured against this.

## Reading order

1. **[01-audit-what-is-theme-locked.md](01-audit-what-is-theme-locked.md)**
   — where "fantasy" is actually welded in today, in three layers from
   shallow (nouns) to deep (the monster *ontology* and the combat
   ladders). The real scope.
2. **[02-design-the-setting-engine.md](02-design-the-setting-engine.md)**
   — the core insight (it's a one-level extension of the referee
   philosophy you already have), what a Setting *is* as a schema, three
   strategies (thin reskin → content pack → LLM-authored), a
   recommendation, and where it plugs into the layers.
3. **[03-hard-problems.md](03-hard-problems.md)** — taxonomy, combat
   physicality, non-verbal creatures, art direction, and the exact line
   where "reskin" stops and "new mechanics" begins.
4. **[04-migration-effort-and-roadmap-fit.md](04-migration-effort-and-roadmap-fit.md)**
   — the phased path (each phase a standalone win), honest effort, and
   why this *multiplies* the existing roadmap instead of competing with
   it.

## The one thing to take away

This isn't a feature. It's a **decision about what the product is**: an
AI fantasy monster game, or an AI ensemble-drama engine you can point at
any genre. The good news is the engine already leans the second way —
the roadmap's whole thesis ("drama between characters") is genre-neutral
— so the bet is smaller than it looks. The bad news is it touches nearly
every prompt and the two constants files that encode the monster's
nature. See doc 04 for whether that trade is worth it.
