# 04 — Migration, effort, and how it fits the roadmap

## A phased path where each phase is a standalone win

The trap with a "change everything" idea is a giant unmergeable branch.
This decomposes into phases that each ship and each leave the game better
even if you stop there.

**Phase 0 — Free the word.** Rename the per-run `theme`
([run_context.py](../../../backend/game/dungeon/run_context.py)) to
something like `motif`/`run_flavor`, or firmly decide the new concept is
`setting` and never "theme." Tiny, but do it first so the vocabulary is
unambiguous forever.

**Phase 1 — Lexicon injection (Strategy A, Layer 1 only).** Stand up the
`game/setting/` module + one `GlobalVariable`. Extract the fantasy nouns
into `settings/fantasy.json`. Inject the lexicon through the prompt
engine's single `build_prompt` funnel. Rewrite the 12 prompt templates to
pull nouns from variables. **Result: the game plays identically, but all
flavor now lives in one file.** This is the acceptance test's first
checkpoint and a real legibility/tuning win on its own.

**Phase 2 — Entity frame + ladder canonicalization (Layer 2 + 3).** Split
`cmdts_data.py` and `battle/constants.py` into skeleton (code,
positional) and lexicon (data). Introduce canonical positions for the
ladders (doc 02's key trick). Move taxonomy/elements/class/origin into
the setting. Still 100% Fantasy, still identical play. **Result: the
Fantasy pack is now complete — the acceptance test passes.** No second
setting exists yet, and that's fine; you've proven the abstraction is
real and the code is dramatically more organized.

**Phase 3 — The second setting (the stress test).** Hand-author one
*very different* setting (I'd pick Highschool Drama over Pirates —
pirates are "fantasy minus magic" and won't stress the seams; highschool
breaks physical combat, taxonomy, elements, and sapience all at once, so
it finds every leak). This is where doc 03's hard problems get paid for
in real playtesting. **Result: the first genuinely new game the engine
produces.**

**Phase 4 — LLM-authored settings (the payoff, Strategy C).** A New Game
workflow that turns a one-line premise into a validated Setting pack.
Only attempt after Phase 3 has taught you which slots are load-bearing
and where auto-authoring goes wrong.

Stopping after Phase 2 leaves you strictly better off (organized, tunable
Fantasy game). Stopping after Phase 3 gives you a two-genre engine.
Phase 4 is the dream but it's optional dessert.

## Honest effort

This is **L-to-XL** — bigger than any single item on the current
roadmap. It touches:

- all 12 prompt templates (rewrite to variable-driven),
- the two densest constants files (`cmdts_data.py`,
  `battle/constants.py`) — the split is delicate because their strings
  are referenced by value across battle/monster/chat code,
- the prompt engine (injection seam),
- a new global + `game/setting/` module,
- the New Game flow (setting picker before character creation),
- the image prompt (art direction),
- and every offline test suite that asserts on fantasy strings
  (`test_*`) will need to assert on canonical positions instead.

The delicate part is Phase 2's canonicalization: anywhere code does
`== 'incapacitated'` or keys on `'stamina'/'mana'` has to move to
positions/ids first. That's careful, mechanical work, well-covered by the
existing offline suites — which is exactly why the test suites are an
asset here, not just a chore.

## Why this *multiplies* the roadmap instead of competing with it

Read [roadmap.md](../../roadmap.md) with this idea in mind and something
clicks: **its entire thesis is genre-neutral.** The roadmap's stated
next moves are Requests, Nemesis Arcs, Party Bonds, Regions — all
"drama between characters." Every one of them works unchanged in
pirates or highschool:

- **Monster Requests** → a crew member wants to revisit the island where
  they were marooned; a student wants you to confront the friend who
  betrayed them. Same request-type enum, same weight ladder.
- **Nemesis Arcs** → a rival captain who's been hunting you; the queen
  bee who's made your life hell. Same brooding→legend ladder.
- **Party Bonds** → deckhands who trust each other; students who become
  inseparable or feud. Same bond ladder.
- **Regions** → literal islands / different schools & hangouts.

So the two roadmaps *reinforce*: the drama systems are what make a
non-fantasy setting worth playing (otherwise a highschool with no
relationships is just a reskinned dungeon crawl), and the Setting Engine
is what proves those drama systems were never really about monsters. The
persona/memory/affinity spine you already built is the reason **both**
are cheap-ish.

## The strategic question this really poses

This isn't a feature request; it's a fork in what the product *is*:

- **Path A:** the best AI fantasy-monster game it can be. Setting Engine
  is a distraction; spend the L/XL on Requests + Nemesis + Bonds and make
  the fantasy *deep*.
- **Path B:** an AI **ensemble-drama engine** that happens to ship with a
  fantasy setting — and can become anything. Setting Engine is the
  headline feature; the roadmap's drama systems become its content.

Both are legitimate. The engine already leans B (that's the whole point
of doc 01's "already generic" list), so the marginal cost of B is lower
than it looks — but B is a *product* bet about audience and identity, not
an engineering call. That's the decision to actually make before any of
this gets a plan doc.

My honest read: **do Phase 1–2 regardless** — they're pure
organization/tuning wins that make the fantasy game better *and* keep
Path B open at low cost. Decide Path A vs. B only when you're standing at
the start of Phase 3, with the Fantasy pack proven and the real effort of
a second setting in front of you.
