# 04 — Hard problems, and how it fits

The honest doc. Where this bites, and whether it earns its place among
the initiatives already on the board.

---

## Hard problem 1 — mode collapse (the central risk)

Feeding past ideas back is the whole pitch *and* the whole danger. A
model handed its own history tends to **converge**: turn 40 is a
variation on turn 3, and the world narrows instead of widening. Every
mitigation is a governor on lever 3 (doc 01):

- **Dream layer** — the parent runs divergence briefs and periodic
  clean-slate turns (doc 03); temperature stays high; history injected is
  capped by the `fill-percent`-style knob (doc 02).
- **Draw layer** — prefer `fresh`/low-`drawn_count` sparks; retire a
  spark after N draws so the world keeps turning over (doc 02).
- **Measurement** — because every spark is a row, we can actually *watch*
  for collapse: track tag entropy and inter-spark similarity over time.
  If diversity trends down, the governor is losing and the knobs need
  turning. **Don't ship this blind** — the one thing worse than generic
  is generic that we *believe* is fixed.

If we can't keep diversity up over a long game, the accumulation half of
the idea fails and we fall back to "persona-primed batch generation with
no memory" — still a win (levers 1–2), just a smaller one. Good to know
the floor.

## Hard problem 2 — quality control on a system nobody watches

The pitch's charm ("the player never knows") is also its danger: a hidden
supply of ideas that no human eyes means **bad sparks silently poison the
pool**. Code-owned guards, none of which need a human:

- **Format/length validation** at harvest — a spark that won't parse or
  is just a restated brief is dropped.
- **Dedup** — near-duplicate sparks (tag + similarity) collapse to one,
  so the bank can't fill with fifteen phrasings of the same fox.
- **Setting-fit check** (optional) — a cheap yes/no that a spark belongs
  in the current world, so a pirate idea doesn't seed a fantasy monster.
- **Dev visibility as the backstop** — everything is a `generation_log`
  row and the sparks are DB rows, so the Developer screen can surface
  "recent dreams" and "the current bank." *Player-invisible, dev-visible.*
  Aaron tunes against what he can read.

## Hard problem 3 — cost and latency vs. the single queue

A three-voice conversation is the most expensive generation in the game,
and [ai/queue.py](../../../backend/ai/queue.py) serializes everything
through one worker. If dreaming ever blocks a player-facing generation,
the feature has made the game *worse*. Non-negotiables:

- Dreaming is **background, low-priority, watermark-triggered, batched**
  (doc 02). It runs when the bank is low and the queue is otherwise idle.
- One turn mints **several** sparks, amortizing the cost.
- The bank is a **buffer**: the player draws instantly from stock; they
  never wait on a dream. If the buffer runs dry, generation proceeds
  cold — never blocked.

The token budget is real money (cloud-API-first). A rough discipline:
dreaming should cost a small, bounded fraction of total generation, and
the Developer screen already reports exact token usage per call — so this
is measurable from day one, not a guess.

## Hard problem 4 — the novelty/coherence knob has two failure modes

Inject too little history → the world doesn't cohere (back to independent
samples). Inject too much → mode collapse. There's a sweet spot and it's
almost certainly **setting- and taste-dependent**, so it must be a
tunable knob (in [tuning.md](../../tuning.md) when it lands), not a
constant baked in. Expect to spend real soak time finding it. This is the
same lesson the chat/run summaries already taught with `fill-percent`.

## Hard problem 5 — does the conceit beat a plain brainstormer?

The unproven claim from doc 01's table. The three-voice conversation
costs ~3× a single wild-brainstormer prompt. Doc 03 argues the friction
(novelty pump) and the persistent-dreamers (authored voice) justify it —
but that's an argument, not a measurement. **This is the thing to A/B
first:** dream a batch three ways — (a) single wild brainstormer, (b) two
kids no parent, (c) full conceit — and compare the sparks blind. If (c)
doesn't clearly beat (a), keep the persona lever and drop the theater.
The idea should be willing to lose its own framing if the framing doesn't
pay.

## How it composes with what's already on the board

This doesn't compete with the roadmap; it **feeds** it.

- **The Setting Engine** ([../setting-engine/](../setting-engine/)) — a
  perfect complement. The Setting defines the *sandbox* (fantasy vs.
  pirates vs. highschool); the Imagination Engine *fills* it. Cleanest
  integration: the **Setting seeds the parent's briefs and the spark
  `tags`**, so a pirate setting dreams pirate sparks. Build the Setting's
  lexicon first and the Engine inherits its genre for free.
- **The Wish Engine** ([../wish-engine.md](../wish-engine.md)) — orthogonal
  but mutually enriching. Wishes are the emotional *payoff* of characters;
  richer, less generic characters (from better sparks) make wishes hit
  harder. And a monster's `core_wish` could itself be seeded from a
  `motif` spark, tying the two systems together.
- **The roadmap** (Requests → Nemesis → Bonds → Regions) — Regions
  especially wants distinctive, coherent places; a place-spark bank is
  exactly that. This is *infrastructure* several initiatives draw on.

## A phased sketch (not a commitment)

Smallest real win first, each phase standalone:

- **Phase 1 — batch generation, no memory.** Persona-primed dreaming
  (levers 1–2 only), sparks deposited and drawn, no history injection.
  Proves the seam and the draw policy. If genericness drops here, the
  cheap version already won. *This is where the A/B in problem 5 lives.*
- **Phase 2 — memory + coherence.** Add the rolling world-summary and
  tag-retrieval so the bank accumulates and the world starts to rhyme.
  Turn on the governors from problem 1. *This is where the pitch's real
  bet gets tested.*
- **Phase 3 — reach.** Extend sparks beyond monsters to run themes,
  places, names, lore defaults; wire the Setting Engine to seed the
  briefs; add the diversity instrumentation as a standing dev readout.

Phase 1 is a genuinely small change (one domain, one prompt file, one
optional context block per generator) and would tell us most of what we
need to know. If it doesn't move the needle, we've spent little and
learned the diagnosis was wrong. That's the right shape for a bet on a
hypothesis about *creativity* — cheap to falsify, honest about what would
prove it.

---

*The idea is good because it names a real disease and treats the cause,
not the symptom. The risk is that it treats the cause with a machine that
can quietly get sick the same way — so build it able to take its own
temperature.*
