# 02 — The architecture

The core insight from doc 01: **decouple the supply of ideas from the
moment of need.** Everything below follows from that. The Engine is not a
chatbot you call when you need a monster; it's a *standing process* that
keeps a **seed bank** full, and generators *draw* from it.

---

## Two ways to wire it (and why one is obviously right)

**Strategy A — inline consultation.** At generation time, the monster
generator holds a turn of the kids' conversation, waits for a spark, then
builds the blueprint. *Rejected.* It puts a three-voice conversation on
the critical path of every monster, and our AI queue
([ai/queue.py](../../../backend/ai/queue.py)) is a **single serialized
worker** — one model, no concurrency. Inline consultation would triple
the latency and tokens of the thing players are actually waiting for.

**Strategy B — a seed bank, filled asynchronously, drawn from at
generation time.** *Recommended.* The kids dream on their own schedule
(idle time, background workflow, batched), depositing tagged **sparks**
into a store. When a monster/place/name is needed, code *draws* a
relevant spark — a cheap DB read — and injects it as one context block.
Creativity is expensive and slow; drawing from it is instant. This is the
whole design.

Everything else in this doc assumes B.

## The seam that keeps it honest: spark, not prose

A **spark** is a compact concept, not finished content. Shape sketch:

```
spark
  kind        'creature' | 'place' | 'name' | 'motif' | 'lore_fragment'
  text        the concept, one or two sentences in the kids' words
  tags        [free-text motifs] — for retrieval + coherence (see below)
  drawn_count int   — how many times it has seeded generation
  status      'fresh' | 'used' | 'retired'
  born_turn   which conversation turn minted it (provenance)
```

The generator draws a spark and injects its `text` as inspiration — it
does **not** copy it. The existing pipeline still owns rendering. A
`motif` spark ("everything here remembers being touched") isn't a
monster at all; it's a flavor the *next several* generations can share.
That shared-motif mechanic is how the world comes to rhyme (doc 01,
payoff #2).

## Where it plugs into existing generation

Minimal surgery, because the injection points already exist:

- **Monsters** — `generate_monster_blueprint` gains an optional
  `inspiration` variable in
  [monster_generation.json](../../../backend/ai/llm/prompts/monster_generation.json),
  filled from a drawn `creature`/`motif` spark. One new context block,
  exactly like `location_context`.
- **Run themes / locations** — the notice-board and location prompts
  ([dungeon_generation.json](../../../backend/ai/llm/prompts/dungeon_generation.json))
  draw `place`/`motif` sparks. This is the cleanest early win: a *run's
  whole theme* seeded from the shared imagination costs one draw and
  colors everything downstream via `expedition_brief()`.
- **World lore & names** — a naming/lore draw for anything that today
  gets a bland default (`"Uncharted Lineage"`, `"the untamed wilds"`).

Every one of these is "add one optional context block, fed from a
draw." No stage is rewritten; no step name changes; the frontend contract
is untouched.

## The new domain: `game/imagination/`

Following the domain layout in [architecture.md](../../architecture.md)
(manager owns state, generator calls the gateway, workflows are thin):

```
game/imagination/
  manager.py               # the seed bank: deposit / draw / tag / retire
  generator.py             # composes the conversation prompt, calls the gateway
  dreamers.py              # the two kids + parent as constants/personas (doc 03)
  registered_workflows.py  # thin: dream_a_while(context, on_update) -> dict
models/imagination_spark.py  # the store (one concept per file, like MonsterMemory)
ai/llm/prompts/imagination.json
```

- **Generation still goes through the gateway.** The kids' conversation
  is `build_and_generate` calls like everything else, so every dream turn
  becomes a `generation_log` row — **Aaron can read the dream on the
  Developer screen even though the player can't.** (Player-invisible,
  dev-visible: the right reading of "the user never knows.")
- **Code owns the numbers, the LLM owns the words.** Code owns: which
  sparks are drawn and when, dedup, tag indexing, retirement/aging,
  how-much-history-to-inject. The kids own: the concepts. Textbook house
  style.

## The conversation's own memory problem — already solved here

"A continuous conversation with all past ideas in history" cannot mean
an unbounded transcript; it would blow the context budget the same way a
long run or chat does. Reuse what exists:

- **[rolling_summary.py](../../../backend/game/utils/rolling_summary.py)** —
  condense old turns into "the world we've been dreaming so far," keep
  the last few turns raw. The summary *is* the world bible, grown by the
  same machinery that summarizes runs and chats.
- **[context_limits.py](../../../backend/game/utils/context_limits.py)** —
  the dream conversation is a flexible block with an absolute token cap;
  a `fill-percent`-style knob governs how much past to feed each turn.
  That knob is literally the novelty-vs-coherence dial from doc 01,
  lever 3.
- **Retrieval over recency** — better than "last N turns": when dreaming
  about water, draw *water-tagged* past sparks into context. The `tags`
  field does double duty (generation-time draw *and* dream-time recall).

## The draw policy (small, code-owned, matters a lot)

Drawing is where code quietly owns the outcome:

- **Relevance** — filter sparks by tag against the request's context
  (a fire-cavern run draws fire/heat/dark sparks).
- **Diversity** — prefer `fresh`, low-`drawn_count` sparks; a spark used
  three times gets `retired` so the world keeps moving. (Anti-collapse
  at the *draw* layer, complementing anti-collapse at the *dream* layer
  in doc 04.)
- **Graceful empty** — if the bank has nothing relevant, generation
  proceeds exactly as today (cold). The Engine is **strictly additive**;
  an empty bank is just the current game. This is the acceptance test:
  *with the Engine disabled or empty, the game plays byte-for-byte as it
  does now.*

## Scheduling against the single queue

The kids must not starve gameplay generation. Options, cheapest first:

- **Opportunistic top-up** — a low-priority background workflow that
  dreams a batch only when the bank dips below a watermark *and* the
  queue is idle. One conversation turn should mint **several** sparks, so
  fills are infrequent.
- **New-game priming** — dream an opening batch during the New Game
  flow (which already does heavy setup), so the world starts with a
  bank rather than warming up cold.

Either way the bank is a buffer that absorbs the latency the player must
never feel. That buffer *is* the architecture.
