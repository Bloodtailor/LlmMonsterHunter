# 03 — The conversation (two kids, one parent)

This is the heart of the user's idea and the part most worth
interrogating, because it's the part most easily dismissed as flavor.
The question to answer honestly: **is the three-voice conceit
load-bearing, or would a plain "wild brainstormer" prompt do the same
job for a third of the tokens?** My read: it's load-bearing — but for
specific mechanical reasons, not because it's charming.

---

## What each voice is actually *for*

Not cosmetics — each voice is a distinct control mechanism.

- **The two kids = the novelty pump.** Per doc 01, lever 2: their value
  is the *friction* between them. One proposes, the other subverts or
  escalates. That back-and-forth is combination-novelty a single voice
  can't reach. If they were identical, you'd have one voice typed twice
  and should cut one. So: **make them different on purpose** (below).
- **The parent = the creativity-referee.** This is the architectural
  payoff. The parent does exactly what the battle referee does for
  combat — it **constrains an open-ended generator toward what the
  system needs**. It poses the prompt ("let's dream up something that
  lives near water"), keeps the kids on-brief, decides when an idea is
  "done" enough to write down, and enforces output *shape* so code can
  parse sparks out. The parent is where the game's *needs* enter the
  imagination. Without it, the kids dream forever about nothing usable.

Frame it in the project's own terms: **the kids pick words freely; the
parent + code own what gets kept.** That's the referee philosophy, wearing
an apron.

## Persistent dreamers = an authored voice, emergently

The sleeper feature. If the two kids are **stable characters with fixed
tastes**, the world develops a **recognizable authorial fingerprint** —
not because we hand-authored it, but because everything was dreamed by
the same two imaginations.

- Give them opposed aesthetic pulls. E.g. one is drawn to the *gross,
  the scary, the underdog-that-bites*; the other to the *elegant, the
  sad, the beautiful-with-a-wound*. Every spark is a negotiation between
  those poles, so the world inherits a consistent tension — teeth *and*
  tenderness — that reads as *style*.
- This is cheap: two short personas in `dreamers.py`, plus the parent.
  It's the same "personas are the portable core" observation the Setting
  Engine audit made — applied to the *authors* instead of the cast.
- It also stabilizes tone across a long game. Random brainstorming drifts;
  two characters with fixed tastes drift *coherently*, which is what a
  world's voice *is*.

This is the answer to "why not just a wild brainstormer prompt": a
brainstormer is a slot machine; two dreamers are **authors**. A slot
machine can be novel per-pull and still produce a world with no voice.

## Tonal control: keep childishness upstream

The worry: a monster dreamed by an eight-year-old sounds like it was
dreamed by an eight-year-old. The fix is the doc-01 seam plus one dial:

- **The seam** — the kids produce the *spark* (concept), not the prose.
  The mature pipeline renders tone. "A birthday clown that got left in
  the woods and the woods kept him" is a child's sentence; the story
  stage turns it into something quietly horrifying or achingly sad.
- **The dial — the parent's register.** The parent can *lift* a raw idea
  before it's written down ("ooh, and think how lonely that would be")
  without sanding off its strangeness. The parent is the tonal governor;
  the kids are the strangeness reservoir.

Net: childlike *invention*, adult *rendering*. You get the weirdness kids
produce and the craft the game needs, and neither contaminates the other.

## Shape of a dream turn (illustrative, not a spec)

One turn should be **batch-productive** — mint several sparks — to keep
fills rare against the single queue (doc 02):

1. **Parent poses a brief**, seeded by what the bank is short on and
   (optionally) the active Setting: *"Let's dream up creatures for a cold,
   drowned place."*
2. **The kids riff** — a few exchanges, building and subverting. Raw,
   unfiltered, in voice.
3. **Parent + code harvest** — the parent names the two or three ideas
   worth keeping; code parses them into `spark` rows with `kind` + `tags`.
   Ideas that were just noise are dropped (that's fine — noise is the
   cost of range).

The transcript is logged (dev-visible) and rolled into the running world
summary. The player sees none of it — only the monsters and places that
grew from it.

## Divergence is a first-class job of the parent

Because history is the mode-collapse lever (doc 01/04), the parent must
sometimes **actively push away** from the accumulated world:

- Rotate briefs across domains so the bank doesn't pile up in one motif.
- Occasionally run a **clean-slate turn** — "forget everything we've
  made; dream something that has nothing to do with any of it" — with
  little or no history injected. This is the pressure valve that keeps a
  long-lived imagination from eating its own tail.

That the parent owns *both* "build on what we have" and "break from what
we have" is what makes accumulated history a spine instead of a rut.

## Do the kids need names? (a small, real question)

Probably yes, and they could even become a **quiet piece of the fiction
someday** — but that's a separate, later idea and explicitly out of scope
for a v1 that stays fully hidden. For now they're an implementation
detail with personas, living in `dreamers.py`. The temptation to show the
player the dreaming room is real and should be *resisted* until the
hidden version proves it lifts quality — otherwise we're building a
feature, not fixing genericness.
