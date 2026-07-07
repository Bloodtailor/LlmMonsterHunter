# Game Loop v1 — Design Proposal

**Status:** PROPOSED (July 2026). Design only — nothing here is
implemented. This is the review document for the initiative that turns
the finished *mechanics* into an actual *game*. Milestones, commit
prefix, and locked decisions get written after the design review.

## Why this initiative

The July 2026 architecture review put it plainly: every verb exists —
explore, battle, talk, recruit, camp, chat, evolve — but there is no game
shell around them. No beginning, no goals, no stakes, no difficulty, no
session identity. A new player's first monster comes from a Sanctuary
generation button, which is a developer flow, not a game opening.

Game Loop v1 is the smallest set of additions that makes a complete,
replayable arc: **title screen → guided first run → runs with goals and
stakes → a home base worth returning to.**

## Proposed pieces (each with its open questions)

### 1. Title / continue screen
The game opens on a title screen: **New Game** (first-run experience
below) or **Continue** (straight to home base). New Game wipes nothing by
itself — it starts the guided opening against the existing database.

*Open question:* do we want named save profiles (a `profiles` table
scoping monsters/runs/chats), or is the single-world model fine for v1?
Single-world is dramatically cheaper and matches the solo-dev reality.

### 2. The guided first run
A scripted-but-generated opening that teaches by playing:

1. A short streamed intro scene (the wish-granting power premise from
   [story_design](../design/story_design.md), finally on screen).
2. The player is led into a **first dungeon** with a fixed first event:
   a `monster_dialogue` encounter tuned to be winnable by words — the
   player's first monster is RECRUITED, not generated from a button.
3. One guided path choice, one battle with the new companion, then the
   exit — home base unlocks with the full loop now open.

Mechanically this is a `first_run` flag in `global_variables` plus a
constrained path-event roll for that run; the LLM does everything else.

### 3. Run goals
Each run gets a **goal** rolled/generated at entry (e.g. "find the
moonlit spring", "recover a keepsake", "answer three riddles", "befriend
a creature of the deep halls"). The goal rides in the dungeon log
context; the LLM weaves locations toward it; Python checks completion
(the referee answers a completion question per event, same word-ladder
philosophy). Completing the goal earns a reward ceremony at exit —
bonus growth, a rare item, or an evolution-flavored keepsake.

*Open question:* one goal per run, or optional side-goals?

### 4. Stakes: exit with your spoils, or lose them
The design doc's tension, finally enforced end-to-end:

- Monsters recruited and items found **this run** are provisional until
  the party exits alive (they already mostly work this way — audit and
  enforce the defeat path: provisional recruits are released, run items
  are lost; memories of the defeat REMAIN, which is the fun part).
- Defeat already costs the run; with goals it also costs the reward.

### 5. Dungeon themes and a difficulty knob
At the entrance the player picks from 2-3 generated **expedition
notices** (theme + danger word: `calm / risky / perilous`). Theme feeds
every location/monster generation prompt for the run; danger maps to
code knobs (enemy count range, event weights, returning-monster odds,
impact-word bias in the referee prompt). One new tuning table in
`docs/tuning.md` when built.

### 6. Affinity v1 (the designed-but-unbuilt core mechanic)
A per-monster **affinity ladder** (word ladder, naturally:
`wary → familiar → trusting → devoted`), stored on the monster, moved by
code-visible events (recruited by words, campfire chats, growth
spotlights, being healed, reunions) with the LLM choosing among defined
step words where judgment is needed. V1 effects, deliberately small:

- Battle: a devoted monster's free-text custom actions get a friendlier
  referee note; a wary one may hesitate (flavor line, not a stat).
- Chat: affinity rides in the chat context (it already has memories).
- Evolution: affinity tier colors the evolution narration.

*Open question:* should low affinity ever mean disobedience (the design
doc's original idea), or is that frustration masquerading as depth?

### 7. Post-run summary ceremony
After every exit (victory or defeat): one streamed "chronicle" scene —
the run's log condensed into a story beat, the goal outcome, growth
earned, monsters met/recruited/lost, and the run number stamped into
history. Gives runs a *shape* and gives the Sanctuary timeline meaning.

## Explicitly out of scope for v1

Sound/music, animations beyond existing reveals, save profiles (pending
question 1), shops/economy, multi-dungeon world map, trap events (the
design doc lists them; they'd slot into `EVENT_WEIGHTS` later).

## Verification sketch

Offline suites for: first-run flag flow, goal completion bookkeeping,
affinity ladder math, defeat-path spoils enforcement. Live soak for the
feel: full first-run experience start to finish, then a themed run with
a goal completed and one failed.
