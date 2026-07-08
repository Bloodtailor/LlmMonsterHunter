# Where It's Going

## What's already built

This isn't a mockup — the whole core game is real and playable. Everything
in the [gameplay tour](02-what-you-do.md) actually works:

- ✅ AI monster generation with painted card art
- ✅ Dungeon exploration with mystery paths and events
- ✅ Text-driven, AI-refereed battles (including free-text actions)
- ✅ Talking monsters into joining you mid-battle
- ✅ Persistent memories, returning monsters, relationships that deepen
- ✅ Growth and the Evolution Altar
- ✅ Campfire conversations
- ✅ Items and keepsakes
- ✅ Character creation and playing as yourself
- ✅ In-game settings, provider choice, real-time streaming everywhere

Each of those was its own mini-project, planned and shipped one at a time.

## The two big recent leaps

**Going cloud-first.** The project originally leaned on AI models running on
your own computer, which meant a beefy GPU and a lot of setup pain. It was
rebuilt around **cloud AI** — bigger, smarter models, and a far lower bar to
actually run it. That's the version you're reading about.

**Better art with memory.** Monster cards moved to Google's Gemini image AI,
and evolution now repaints a monster using its *old* art as a reference — so
an evolved creature still looks like itself, just transformed.

## What's next

Two tracks:

- **Polish under the hood** — a "codebase health" cleanup pass, and lots of
  real-play tuning of how the AI spends its effort and what the art looks
  like.
- **New gameplay** — the sketched-out roadmap includes things like: monsters
  that make *requests* of you, recurring **nemesis** rivalries, deeper party
  **bonds**, and distinct **regions** to explore.

There are also some genuinely ambitious "big idea" design docs kicking
around — like making the whole game's *setting* swappable (what if it
weren't fantasy monsters at all?) and pushing the AI to be more wildly
imaginative instead of falling back on clichés.

## The story of the project

The short version: Aaron started this to learn — how to build real software,
how to work with AI models, how to architect something non-trivial from
scratch. It grew from a rough proof-of-concept into a genuinely
well-structured codebase with real engineering discipline (clean layering,
tests, documentation, file-size limits — the whole professional toolkit).

Along the way it split into two sibling experiments betting opposite ways on
the "cloud vs. local AI" question, which is a pretty interesting fork in the
road on its own.

It's a solo project, built in the open, as much about *learning how to build
things well* as about the game itself.

➡️ Next: **[FAQ](06-faq.md)**
