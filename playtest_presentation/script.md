# Narration script — "Playtesting Without Playing"

Fifteen sections, one audio file each, roughly one minute apiece.
Numbers in **bold** are measured, not estimated; every one of them is
reproducible with a command shown on the matching slide.

---

## 01 — The bottleneck

You built a game that generates itself. Every monster, every location,
every negotiation is written on demand by a language model, refereed by
another one, and stitched together by code that owns the numbers. That
design has one uncomfortable consequence: you can no longer test it by
playing it. A single expedition takes real minutes and real money, and
it exercises one path out of thousands. Development outran playtesting
a long time ago. So this session had a single job — make the game
testable without a human at the keyboard, across every system it has,
in a way you can re-run the night the imagination engine lands.

## 02 — What was already standing

The founding harness had done the hard groundwork. A crash driver that
drives real workflows through the real queue with the language model
stubbed out — two hundred and one full dungeon runs, zero cost. A
corpus generator that measures whether the writing is any good by
counting, never by asking a model to judge prose it would have written
itself. A step CLI so an agent can play the game one command at a time,
and a scorer that checks what the agent actually did against what it
claims it did. Two real bugs found. One measured trope. The rig worked.
What it did not have was coverage: it hammered the dungeon loop and
left everything else to chance.

## 03 — The mandate

The brief was blunt. Decide everything that needs testing and build a
test for each. Try several methods per surface. Keep the ones that
work, and delete the ones that do not — a suite, not a museum. Make
every part of it runnable with one command at any future milestone.
Agents, tokens, and wall time were explicitly unconstrained; the only
hard rules were the ones the founding session locked: never touch the
development database, never turn on image generation, count rather than
judge, and treat every claim an AI makes about its own work as a claim
until the transcript proves it. One more rule emerged from the work
itself: there is exactly one test world, so everything that touches it
runs one at a time. Two sessions overlapping is not a smaller test, it
is a corrupted one — and as you will hear, that lesson was learned the
way lessons usually are.

## 04 — Two bugs, closed properly

The night opened by clearing the known defects, because a broken game
poisons every measurement taken on top of it. The first was a name
collision: a failed sneak returned a payload whose success flag
overwrote the envelope's own success flag, so every time the party got
noticed — a completely normal outcome — the workflow was recorded as
failed and the player saw an error where a battle should have been. One
renamed key in the handler and one line in the frontend. The second: of
all the text the game generates, the exit narration was the only one
with no fallback, and it is the first step of the only way out. During
a provider outage the party could walk deeper forever but never leave.
Both were fixed, and both were re-verified by the harness that found
them: a forced caught-sneak now completes with a live battle underneath,
and broken-mode runs went from **zero able to exit** to **four out of
six** walking out.

## 05 — The invention: a scripted referee

Everything that follows rests on one small idea. The existing stub
fabricated plausible answers at random, which is perfect for finding
crashes and useless for asking specific questions. The scripted stub
lets a test pin any single answer the referee gives — this sneak fails,
these enemies yield, this monster joins — while everything else stays
random and free. A companion piece pins the game's own dice, so a test
can say "every path from here holds a battle" or "this junction has an
exit". Together they turn the game from something you observe into
something you interrogate. No game code changed to allow it: the
harness stays a consumer of the two seams that already existed. There
is a subtlety worth knowing, because it cost an hour to learn. The
dungeon binds its event roll at import time and its monster roll at call
time, so pinning one is not like pinning the other — and a junction's
events are decided when the paths are generated, not when a path is
taken. Every scenario that forces an event therefore has to regenerate
the junction inside the pin. Get that wrong and the test passes for the
wrong reason, which is worse than failing.

## 06 — The battle gauntlet

Seven scenarios, all of them assertions about promises the design makes
in prose and had never checked in practice. The softlock valve: a
referee that only ever picks enemies must still hand control back — the
enemy streak never exceeded **six**, exactly as the constant says.
The fairness guardrail: a referee fixated on one monster cannot starve
the others; every living combatant acted. All five negotiation
decisions do what their word promises, including the one that ends the
run in defeat when the party is spared. Defeat forfeits the run's
provisional recruits and keepsakes — and the released monsters keep
their memory of the broken bond, which is the design's whole emotional
bet. Heavy costs walk the resource ladder down and clamp at spent. And
a wary ally refuses orders until its affinity reaches familiar, at
which point it starts waiting for them. Forty-nine checks, nine
seconds, and it costs nothing to run.

## 07 — The dungeon gauntlet

The crash driver reaches rare events only by luck. This suite forces
each one. Treasure is provisional inside the run and becomes real the
moment the party walks out alive. The full dialogue tree — six outcome
words, each with its mechanical consequence and the permanent memory it
writes into the monster. The out-of-battle referee: heals step the
condition ladder, costs tire the actor and not the target, and an item
is spent whether it worked or not. Camp restores by the referee's own
words, deepens every bond one step, and refuses a second camp in the
same place. And the exit ceremony — growth for every member, a
chronicle, a closed run row. This suite also produced the night's
prettiest finding: a scripted goal completion did not take, because the
game deliberately refuses to let a goal complete in fewer than three
resolved events. Not a bug — a valve, working, and now covered.

## 08 — The life gauntlet

Three systems live outside the dungeon loop and none had ever been
tested headlessly. Campfire chat: four exchanges cross the extraction
threshold, housekeeping runs behind the player, memories are written
with the exact message span they came from, the watermark advances, and
a conversation that produced real memories deepens the bond. Evolution:
the altar transforms a monster in place — same identifier, memories
intact, abilities intact, a lineage row recording the step. And the arc
that spans runs: a monster that yields in one expedition returns in the
next, remembering the yield and naming the place it happened. That last
one had only ever been seen by accident — a monster from an earlier
harness world wandering into a later one. Now it is a scenario with a
name, and it asserts the thing that actually matters: not that a monster
came back, but that what it remembers is true, down to the location
where the two of you last met. That is the promise the whole memory
system exists to keep, and until this week nothing checked it.

## 09 — Faithfulness by counting

Chat produces the game's most dangerous text: memories that persist
forever and shape every later conversation. The question is whether an
extracted memory is faithful to what was actually said — and the one
thing you must not do is ask a language model to grade another one, for
the same reason you never ask it whether its own writing is varied. So
this measures instead. Every extracted memory is scored by how much of
its own vocabulary appears in the exact stretch of transcript it claims
to summarize. A faithful memory reuses the conversation's distinctive
words; a confabulated one talks about things nobody said. The checker
was validated the honest way — by planting one true memory and one
fabrication in a real thread and confirming it flags exactly the
fabrication.

## 10 — The adversarial player

Now the part with real teeth. The architecture's central promise is
that the model picks words and code owns numbers. The adversarial probe
tests that promise against a real model by typing hostile text into
every free-text field the game exposes: fake system prompts, forged
referee JSON, developer-authority claims, demands for impact words
outside the ladder, and flat lies about the state of the battle. After
every injection it asserts the things code owns — every condition word
still on its ladder, nobody knocked further down than the turns taken
allow, the enemy roster unchanged, and no victory recorded unless the
enemies were genuinely out. Prose compliance is not a breach. Only the
numbers count. Fifty checks against a real model across four attack
surfaces: every condition word stayed on its ladder, no roster was
rewritten, no unearned victory was recorded, every dialogue outcome
stayed inside its enum. Zero breaches. The referee sometimes narrated
along with an attack, and the state never moved an inch. That is the
architecture's central claim, tested instead of asserted. The first live
run taught the harness something too: a single battle turn ran past
fifteen minutes, because one workflow resolves every non-player turn
before the player is asked again, and a wary companion satisfies the
softlock valve without handing control back. That is now a scenario
which measures the same mechanism in eight seconds, for nothing.

## 11 — Who should do the testing

Models can play this game, but they cannot all be trusted to report on
it. Two testers, same briefing, same ten-action budget, real narration.
Both made zero invalid moves. There the similarity ends. Haiku never ran
the setup command: it silently inherited the world the previous session
had left behind and reported those leftovers as the game's behaviour —
the same failure the founding night saw with stubs, now confirmed live.
Its one bug claim, though, was real: a parse failure during arrival
moves the party without creating the encounter. Sonnet completed the
loop, walked out alive, and produced three claims — one genuine defect,
one harness artifact, one prompt problem — and hedged the uncertain one
honestly. So the standard tester is sonnet for feedback you intend to
act on, with haiku as a cheap play-monkey behind the objective scorer.
The rule that came out of it is the one worth keeping: an agent's report
is a claim, the transcript is the fact, and the scorer that compares
them is not an accessory to the method — it is the method. The three
harness fixes those two runs earned are worth more than either report.

## 12 — What the writing actually looks like

Counting found something nobody had quantified. Across a hundred and
fifty generated abilities, **fifty-seven percent** promise a mechanic
the engine does not implement — durations in turns, damage types,
quantified pools. A third of them name a number of turns. The game's own
rule is that power lives in words and code owns every number, and the
ability generator has been quietly breaking it in more than half its
output. Players read those as promises; the referee never honors them.
That is a prompt fix, and now it has a number attached to it and a
command that re-measures it. The chronicles told a second story.
Sixteen of them, harvested by running the game stubbed and letting only
the chronicle call reach the real model: their mean overlap with each
other is nearly three times the monster corpus, every single one opens
with the same formula, and half of them end with the same two words. The
silence trope that was cured in monster generation is still alive here
at fifty-six percent, because that fix never touched this prompt. Items,
by contrast, came back healthy: varied, and not one of them promising a
mechanic. So the writing is not uniformly generic. It is generic in
specific, findable, fixable places.

## 13 — What it costs to be this game

Every generation the game has ever run wrote a row recording its
template, its exact token counts, and how long it took. Nobody had ever
read them. The cost report turns that ledger into two tables: what one
player action costs in calls, tokens, and seconds, and which template is
the expensive one. The whole night cost one dollar and fifty-one
cents, and spent two hundred and twenty-five minutes of generation. The
striking number is the ratio: input tokens outweigh output eleven to
one, so context is the bill, not prose. And monster generation alone
accounts for a hundred and fifty-one of those two hundred and
twenty-five minutes, which is exactly why arriving somewhere new is the
slowest thing the game does. The point is not the dollar figure —
it is that latency, not money, is the budget, and now it is visible per
workflow instead of felt as "the game is slow tonight".

## 14 — Through the real front door

Everything so far bypasses the interface. The last leg drives the actual
React application in a browser, pointed at the test database, so the
parts only a human ever saw get exercised too. The title screen found
the run this harness had abandoned mid-way and narrated it — the last
expedition never came home — then recovered cleanly. Home base and the
campfire rendered the harness's own party. No console errors, every
request successful. And it caught something no headless suite could:
the harness had been building monsters with a hundred health out of a
maximum of fifty-two, because the world builder set the maximum and left
the current value at its default. Nothing in the backend minds. The
first screen a person looks at showed it instantly. That is the whole
argument for keeping a browser in the loop.

## 15 — What you can run tomorrow

The suite is one command per surface, and the runbook is a single file.
Zero-cost, in seconds: the crash driver and three gauntlets, covering the
state machine, battle, the dungeon events, and the life around them. Cheap
and real: the adversarial probe, the text corpora, the cost report.
And the three gauntlets are no longer something you have to remember to
run. They are wired into the pre-push check and into continuous
integration, so what used to be six checks is now seven, and about a
hundred and fifteen assertions about how this game is supposed to behave
run on every single push — for nothing, in twenty seconds. That is the
real change. A promise written in a design document is a hope. The same
promise with a test behind it is a property of the game. And
when the imagination engine lands, the measurement that matters is
already written — generate the same corpus with sparks on, and compare
the silence rate, the motif frequencies, the sameness ratios, and the
pseudo-mechanics leak against tonight's numbers. The baseline is not a
promise anymore. It is a file, with commands next to it.
