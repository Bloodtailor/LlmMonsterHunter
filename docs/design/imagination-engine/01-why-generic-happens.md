# 01 — Why generic happens (the diagnosis)

Before designing anything, be honest about the disease. "Things come out
generic" is a symptom; the idea is a proposed cure. If we don't name the
mechanism, we'll build something that *feels* clever and changes nothing.

---

## The mechanism: cold generation samples the mean

When [monster/generator.py](../../../backend/game/monster/generator.py)
asks for a blueprint, it hands the model a `location_context` and a bag
of enum options and says, in effect, "invent a creature that fits." The
model answers with the **centroid of every creature description in its
training data that matches those constraints.** Tell it to "be creative"
and you nudge the temperature, not the *concept* — you get a slightly
more florid version of the same centroid. A wolf with crystals. A guardian
of the ancient something. A creature that is "surprisingly gentle despite
its fearsome appearance." These aren't failures of the prompt; they're
what *the average* looks like.

Three things make this worse in our pipeline specifically:

- **Each roll is independent.** Every monster is generated from a cold
  start with no knowledge of the other monsters. Nothing pulls two
  creatures toward a shared, specific idea, so they all fall toward the
  same *general* one. (This is why the world can feel generic even when
  any single monster is fine.)
- **The enums are a floor and a ceiling.** [cmdts_data.py](../../../backend/game/monster/cmdts_data.py)'s
  taxonomy/elements/roles guarantee *coherence* — a real win — but the
  model happily treats "fire + beast + striker" as a fill-in-the-blank
  and reaches for the most typical fire-beast-striker there is.
- **We ask for the finished thing in one breath.** Even staged, each
  stage asks the model to *both* have the idea and render it well. The
  idea half loses, because rendering-the-average is the safe play.

## The three levers this idea pulls

The Imagination Engine is a bet that you can push the model off the mean
with three levers. They are not equally strong — be clear-eyed about
which is doing the work.

### Lever 1 — Persona priming (strong, cheap)

Asking "a creature designer" to be creative gets you a designer's
average. Asking *an eight-year-old who loves gross bugs* gets you a
different distribution entirely — vivid, unselfconscious, un-sanitized,
trope-*breaking* rather than trope-serving. Kids' fantasy reaches for
"a knight made of all the armor of knights who gave up" without first
checking whether it's cool. This lever is well-supported: role framing
measurably shifts output register and specificity. **This is real, and
it's most of the value.**

### Lever 2 — Two voices in tension (strong, and the clever part)

One imaginer regresses to *their* mean. Two imaginers who **build on and
subvert each other** produce combination-novelty neither would alone: A
says "a fox that steals fire," B says "no — it steals *warmth*, so
everywhere it's been is cold forever." The dialectic is a novelty pump.
This is the actual engine inside the "conversation" framing — not the
cuteness, the *friction*. See doc 03.

### Lever 3 — Accumulated history (double-edged, needs a governor)

Feeding past ideas back is what the user's pitch leans on hardest, and
it's the **riskiest** lever. Done right, it's a consistency spine and a
springboard ("we already dreamed the Cold Fox — what lives in the lands
it froze?"). Done wrong, it's a **mode-collapse trap**: the model
converges, and everything becomes a variation on the first cool idea.
History gives you coherence *for free* and novelty *only if actively
governed* (divergence prompts, topic rotation, controlled forgetting).
Doc 04 treats this as the central hard problem.

## What's evidence vs. what's hope

Being honest so we don't oversell it to ourselves:

| Claim | Confidence |
|---|---|
| Persona priming shifts the output distribution off the generic centroid | **High** — well-established |
| Two-voice dialectic yields ideas single-voice doesn't | **Medium-high** — mechanically sound, framing-sensitive |
| A shared, persistent imagination makes the *world* cohere | **High** — it's structural, not a model trick |
| Long accumulated history keeps *raising* novelty over time | **Low** — likely the opposite without a governor |
| The three-kids conceit beats a plain "wild brainstormer" prompt enough to justify 3× the tokens | **Unproven** — the real open question (doc 03/04) |

## The reframe that makes it safe

The most important design decision falls out of this diagnosis: **the
Engine produces the *concept*, never the *prose*.** The kids don't write
the monster's backstory — the existing story stage
([generator.py](../../../backend/game/monster/generator.py) stage 3)
still does that, in tone. The kids supply the *spark* — "a lighthouse
keeper who is also the light" — and the mature pipeline renders it
eerie or tender or grand as the setting demands.

This resolves the obvious objection ("do we want a grimdark monster
dreamed up by a child?") — the childlike wonder lives **upstream**, as
raw idea-supply; the tonal rendering stays where it already is. Novelty
from the kids, register from the pipeline. Keep that seam sacred; doc 02
builds on it.
