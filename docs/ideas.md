# Ideas — the fun file

**Written 2026-07-07**, Fable 5's parting gift. Unranked-by-effort,
ranked-by-heart. These go BEYOND docs/roadmap.md (Requests, Nemesis,
Bonds, Regions are already there). Each idea names its mechanic in the
house style: the LLM picks words, code owns numbers.

---

## 1. The Wish Engine (the endgame the premise already promised)

The opening scene says it: somewhere deep sleeps a power that grants
ANY wish, and every monster carries one. **Nothing in the game pays
that off yet.** Make it real:

- Deep runs can surface **Wish Signs** — the goal system already knows
  how to judge progress; add a parallel, much rarer track that only
  advances on profound events (a nemesis forgiven, a vow fulfilled, a
  secret confessed). Code owns the counter; the LLM narrates each sign.
- When a monster's signs complete, a run can end at the **Wish Gate**:
  its core_wish is granted, on screen, streamed. And here is the knife:
  **a granted wish may mean goodbye.** The monster whose wish was "to
  see her lost sister again" might leave with her. The player chooses —
  walk your dearest friend to the gate, or keep walking past it
  together. Word ladder for outcomes: `transformed → freed → departed
  → stays, changed` (LLM picks from the wish's own nature; code makes
  departure real: roster removal, a permanent Chronicle entry, one
  final memory written to every party member).
- The player's own wish is the campaign's last door.

This is the emotional endgame this whole architecture was built to
deliver. No other game can do it, because no other game *knows* what
each creature wants.

## 2. Dreams at the campfire

When the party camps, one monster **dreams** — a short streamed scene
remixed from its actual memories, its secret (hinted, never stated),
and its wish. One LLM call, enormous character payoff. Mechanics: code
picks the dreamer (least-recently-dreamed — a fairness counter like
turn order), the dream mints a `dreamed` memory, and once in a while a
dream is **prophetic**: it references an entity that actually exists in
world state (a fled enemy, an unmet returning monster), planted by code
choosing the reference, the LLM weaving it. Players will screenshot
these.

## 3. Confession moments (the Secret system's payoff)

Every monster already carries a `secret` the prompts guard carefully.
Give that guarding a destination: when affinity crosses its top rungs
AND a trigger event fits (a battle where the player protected it, a
request fulfilled), a **confession scene** fires at the campfire — the
secret comes out, haltingly, in its own voice. Code owns the trigger
(affinity threshold + event type); the LLM owns the telling. The
confessed secret converts into a visible persona line and one
high-weight memory. Sometimes the secret *changes things* — a small
enum the LLM picks at creation time already implies it: a secret can be
`tender / haunted / dangerous`. A dangerous secret confessed might
spawn a run goal ("help me face what I did").

## 4. Counsel at the crossroads

Before the player picks a path, one or two party monsters **offer an
opinion** — a single line each, in voice, keyed to their persona and
the path descriptions ("Thornback sniffs the left tunnel: 'Water. I
hate water.'"). One small LLM call per fork, cached with the paths.
Choosing a monster's preferred path is a tiny affinity beat (code:
`followed_my_counsel`). Suddenly paths aren't doors — they're
conversations, and the party has opinions about your leadership.

## 5. The Rival Party

Somewhere in the same dungeon walks **another adventurer with their own
monsters**. You find their traces first — a still-warm campfire, a
treasure alcove already emptied, a monster that says someone else
already asked it the riddle. Meetings are rare and refereed like
encounters: talk, trade, race for the same goal, or (rarely) clash.
Their roster is generated once and PERSISTS — their monsters grow
between your runs just like nemeses. The dungeon stops feeling like it
was staged for you, which is the deepest immersion trick there is.
(Big initiative — after Bonds.)

## 6. Gifts that come back

Items flow one way today: world → party. Reverse one trickle: between
runs, a monster with high affinity occasionally **makes or finds you
something** — keyed to its hobbies and your player character's likes
(both already exist in personas!). A whittled figurine of the whole
party. A stone that matches the player's described eyes. Pure sentiment
items with one mechanical grace: holding a gift while its giver fights
lets the referee lean warm once per battle. Cheap to build (one
generation + inventory insert), devastating to the heart.

## 7. The Saga — your chronicle as a book

The run chronicles are already a saga; nobody can *hold* it. Bind them:
an in-game **Saga screen** styled as a book — each run a chapter with a
generated title, its chronicle text, the goal's fate, and the card art
of who joined/fell/evolved as plates. Then the killer feature:
**one-click export to a single self-contained HTML file** — your whole
playthrough as a shareable, beautiful artifact. For a portfolio
project, this IS the demo: people who never install the game will read
a saga and understand everything.

## 8. The Referee has a face

`referee_hint` already varies the expedition mood — promote it to a
**character the player chooses at the notice board**: The Grim
Adjudicator (stingy impacts, brutal honesty), The Merciful Chronicler
(leans warm, loves redemption), The Trickster (wild rulings, richer
loot). It's a difficulty setting wearing a persona — word-ladder
difficulty, zero new math, and players will develop loyalties and
grudges toward their referees. Referee flavor lines could even open
each battle ("The Adjudicator watches. It does not blink.").

## 9. Your first monster chooses YOU

Onboarding idea: the guided first run ends not with the player
recruiting a monster, but with a monster — generated to resonate with
the player character's stated wish — **stepping out and choosing
them**. ("You said you're looking for your brother. I'm looking for
mine. Walk together?") One conditioned generation, and the game's
thesis — bonds go both ways — lands in the first ten minutes.

## 10. UX quick wins (small, high-love)

- **Text-speed control + skip** for streamed narration — classic RPG
  respect for replayers. (SSE already delivers full text; the frontend
  just paces the reveal.)
- **Talk starters**: when the player opens the free-text talk box
  mid-battle, offer 2-3 generated suggestion chips drawn from the
  enemy's `responds_well_to` — trainer wheels for the shy, ignorable by
  the bold.
- **The Party Ribbon**: a persistent strip of party portraits with
  condition/reserve auras and a tiny mood glyph that reacts to events
  in real time (SSE already carries everything needed). Glanceable
  state, constant companionship.
- **Ambient sanctuary idle-chatter**: at the home base, occasional
  one-line exchanges between monsters float by (one cheap call, long
  cooldown) — the sanctuary breathes even when the player just looks.

---

*Build the Wish Engine last. End the saga the way it began — with a
wish, and a friend who walked the whole way for one.* 🐉
