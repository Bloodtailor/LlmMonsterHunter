# The Imagination Engine — musings

*Exploratory thinking, not a plan doc. Written 2026-07-07 in response to
an idea: "a lot of things in the game come out generic. What if there
were one central place where ideas are generated — a hidden, continuous
conversation between two kids and a parent facilitator — and everything
in the game (world lore, names, monster backstories) is seeded from what
they dream up. The player never knows it's happening."*

Nothing here is committed. These docs are me thinking out loud about how
the idea would actually look, work, and hurt. If it graduates, it
follows the real process (review → plan doc → approval → milestones).

## The one-sentence version

The game keeps coming out generic because we ask a cold model to "be
creative" at the exact moment we need a monster, and a cold model
answers with the **average of every monster it has ever read**. The
Imagination Engine moves creativity *off the request path* into a
standing, evolving **shared imagination** — dreamed up by characters
with tastes, accumulated over time, and drawn from as a *seed* whenever
the game needs something new. It doesn't write the monster; it hands the
monster generator a **spark** the average model would never have
reached for.

## Why this is a natural fit, not a bolt-on

This is the **referee philosophy pointed at creation instead of
combat.** The referee: the LLM picks a word from a ladder, code owns
what the word does. The Imagination Engine: the LLM (as two dreaming
kids) invents concepts freely, and code + a facilitator own *which
sparks are kept, how they're tagged, and where they get injected*. The
parent facilitator **is a referee for creativity** — same architecture,
new job. That's why this belongs in *this* codebase specifically.

And it fits the layers with almost no violence. Today
[monster/generator.py](../../../backend/game/monster/generator.py) builds
a blueprint from a `location_context` string and a bag of enum options.
The Engine adds **one more optional context block** — a drawn spark —
exactly the way [run_context.py](../../../backend/game/dungeon/run_context.py)
already threads the run `theme` through `expedition_brief()` and
`themed_location_context()`. The plumbing already exists; we're adding a
new *source* to feed it.

## The two payoffs (the second one is the sleeper)

1. **Novelty** — the obvious one. Priming + accumulated history + a
   facilitator push the model off the mean. See doc 01 for which of
   those three levers actually does the work (and which is hope).
2. **Coherence** — the sleeper. If *every* monster, place, and name is
   drawn from **one evolving shared imagination**, the world stops being
   a bag of independent samples and starts to *rhyme*. Two monsters
   generated a week apart can share a motif because both drank from the
   same dream. Genericness and incoherence have the same cure here: a
   single authored wellspring instead of N cold rolls.

## Reading order

1. **[01-why-generic-happens.md](01-why-generic-happens.md)** — the
   actual diagnosis. Why cold generation regresses to the mean, the
   three levers this idea pulls, and an honest split of what's evidence
   vs. wishful thinking.
2. **[02-the-architecture.md](02-the-architecture.md)** — the seed bank,
   async fill vs. inline consultation, the `concept-not-prose` seam, the
   new `game/imagination/` domain, and how it survives the single AI
   queue and the gateway.
3. **[03-the-conversation.md](03-the-conversation.md)** — the two kids
   and the parent. Is the conceit load-bearing or just cute? The parent
   as creativity-referee, tonal control, and why **persistent dreamers
   with fixed tastes** are how a world comes to feel *authored*.
4. **[04-hard-problems-and-fit.md](04-hard-problems-and-fit.md)** — mode
   collapse, quality control on a system nobody watches, cost against
   the serialized queue, the novelty-vs-coherence knob, how it composes
   with the Setting Engine and Wish Engine, and a phased sketch.

## The one thing to take away

The value isn't "a cute brainstorm chatbot." It's **decoupling the
supply of ideas from the moment of need**, and giving that supply a
*memory* and a *taste*. A monster generated on demand is a sample from
the mean. A monster grown from a spark that two imaginary children have
been circling for a week is something the mean can't produce — and it
belongs to a world that has been dreaming the whole time. Whether the
three-voice conceit earns its token cost is the real question; doc 03
argues it does, doc 04 says where it might not.
