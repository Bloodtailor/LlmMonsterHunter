# The Wish Engine — Design

**Status:** Design-only proposal (no code written). Source: idea #1 in
[docs/ideas.md](../ideas.md). Read alongside
[architecture.md](../architecture.md) (layers, workflows, the referee
philosophy) and [tuning.md](../tuning.md) (every knob).

> The opening scene promises it: *somewhere below sleeps a power that
> grants any wish, and every creature carries one.* Character creation
> already makes it literal — the player's stated wish becomes
> `persona.core_wish` **verbatim** ([player/creation.py:119](../../backend/game/player/creation.py)),
> and every generated monster carries a `core_wish` of its own
> ([monster/generator.py:376](../../backend/game/monster/generator.py)).
> **Nothing pays that off yet.** The Wish Engine is the mechanic that
> does — the emotional endgame this architecture was built to deliver.

---

## 1. The pitch in one breath

Three linked systems, each in the house style (LLM picks words, code owns
numbers):

1. **Wish Signs** — a rare, per-monster progress track, parallel to run
   goals but far slower, that only advances on *profound* moments. Code
   owns the counter; the LLM judges each candidate moment and narrates
   the sign.
2. **The Wish Gate** — once a monster's signs complete, a run can end at
   the Gate. Its `core_wish` is granted, on screen, streamed. **The
   player chooses** whether to walk their friend to the Gate — and the
   wish's own nature decides whether granting it means *goodbye*.
3. **The player's wish** — the same machinery, pointed at the player
   character (who is already a monster row with a `core_wish`). Its Gate
   is the campaign's last door.

The design leans entirely on systems that already exist: the run-goal
referee ([dungeon/goal.py](../../backend/game/dungeon/goal.py)) is the
exact template for Wish Signs; the run chronicle
([dungeon/chronicle.py](../../backend/game/dungeon/chronicle.py)) is the
template for the streamed granting scene; the exit ceremony
([handlers/exit_run.py](../../backend/game/dungeon/handlers/exit_run.py))
is where a departure ceremony slots in beside the growth ceremony.

---

## 2. Wish Signs — the slow track

### 2.1 What it is

Every monster (and the player) has a `core_wish`. A **Wish Sign** is a
single profound moment, recognized by the referee, that moves that
creature one step closer to being *ready* for the Gate. Signs are
**rare by construction** — three independent gates must all pass:

1. **A code-eligible trigger fired.** Signs are only *considered* after a
   short list of already-meaningful events (see §2.3). Ordinary explore
   and treasure arrivals never qualify.
2. **An affinity floor is met.** A monster the party barely knows cannot
   surface its wish. Recommended floor: **`trusting`** (the wish stirs)
   for early signs, **`devoted`** for the final sign that opens the Gate.
   (Reads through `game/monster/affinity.py`.)
3. **The referee said yes.** Even after 1 and 2, a small LLM call judges
   whether *this specific moment* actually touched *this specific wish*.
   Most of the time the honest answer is "not yet."

The result: signs accrue across **many runs**, not within one. A wish is
a campaign-length arc, where a run goal is a single-run arc.

### 2.2 The word ladder (progress)

Mirrors `GOAL_ANSWERS`. The referee answers exactly one word:

```
WISH_SIGN_ANSWERS = ('none', 'stirring', 'sign')
```

- `none` — the moment didn't touch the wish. Nothing changes.
- `stirring` — the wish was *near* the surface; record a flavor note,
  advance nothing. (Gives the player visible foreshadowing without
  spending a sign — the analogue of the goal's `progress`.)
- `sign` — a true Wish Sign. Code increments the counter (subject to the
  valve below) and writes a `wish_sign` memory to the monster.

### 2.3 Eligible triggers (code-owned)

A `WISH_SIGN_TRIGGERS` set names the event types allowed to *ask* the
referee. This is the rarity valve that keeps the LLM call cheap and the
signs meaningful. Grounded in what exists today, plus clean hooks for
the roadmap systems:

| Trigger | Exists today? | Where it fires |
|---|---|---|
| `goal_fulfilled` | ✅ | after `complete_goal_directly` / goal referee `complete` |
| `evolved` | ✅ | evolution ceremony ([monster/evolution.py](../../backend/game/monster/evolution.py)) |
| `affinity_devoted` | ✅ | when `step_affinity` reaches `devoted` |
| `secret_confessed` | 🔜 idea #3 | the confession scene |
| `nemesis_forgiven` | 🔜 roadmap | Nemesis resolution |
| `vow_fulfilled` | 🔜 roadmap (Bonds) | Bonds |

Only the first three are needed for a shippable v1. The set is designed
so each roadmap system adds *one line* to it later — no rework.

### 2.4 The valve (code owns the count)

```
WISH_SIGNS_TO_OPEN_GATE = 3     # like GOAL_MIN_EVENTS — the hard gate
MAX_WISH_SIGNS_PER_RUN  = 1     # a wish deepens at most once per run
```

`MAX_WISH_SIGNS_PER_RUN` is the direct analogue of
`MAX_AFFINITY_STEPS_PER_RUN` — it forces the arc to span runs and stops a
single lucky expedition from opening a Gate. However sure the referee
sounds, a second `sign` in the same run is downgraded to `stirring`.

### 2.5 The status ladder (per-wish lifecycle)

Stored on the monster (see §4), read by the frontend and the Gate offer:

```
WISH_STATUS = ('dormant', 'stirring', 'ready', 'granted', 'declined')
```

- `dormant` — signs = 0, wish unseen.
- `stirring` — ≥1 sign, or a `stirring` note recorded. The wish is
  *visible* to the player now (a soft glyph on the card).
- `ready` — signs ≥ `WISH_SIGNS_TO_OPEN_GATE` **and** affinity `devoted`.
  The Gate can now be offered while this monster is in the party.
- `granted` — the wish was granted at the Gate (terminal).
- `declined` — the player walked past the Gate *with* the monster
  (see §3.4). Not terminal — the Gate can be offered again on a later run.

---

## 3. The Wish Gate — the run's last door

### 3.1 When it appears

The Gate is offered when **all** hold:

- At least one **party** monster (or the player, see §5) is `ready`.
- The party is at a natural leaving-point. Two candidate surfacings
  (open question §7): **(a)** as a special path at a junction, rolled
  like `EXIT_PATH_CHANCE` but guaranteed when a ready monster is present;
  **(b)** as an extra choice on the existing exit path. Recommendation:
  **(a)** — the Gate should feel like a *place you walk to*, not a menu
  item, and a dedicated path lets the location prompt describe it.

Only **one** wish is resolved per Gate visit. If two monsters are
`ready`, the player picks whose wish they approach (or the referee
surfaces the one with the strongest recent signs — open question §7).

### 3.2 The player's choice — the knife

At the Gate the player is given exactly two options, and *the stakes are
stated but the outcome is not*:

- **Walk them to the Gate.** Grant the wish. The player commits *without
  knowing* whether granting it means the monster stays or leaves — that
  is decided by the wish's own nature (§3.3). This is the knife: you
  grant your dearest friend's deepest wish knowing it *might* be the wish
  to leave.
- **Keep walking, together.** Decline for now. The wish returns to
  `declined`; the party leaves as one. The Gate can be approached again
  on a future run — the choice is never spent, only deferred.

Code owns the branch. The LLM never decides whether the wish is granted —
the *player* does. The LLM only decides, once granted, *what granting it
looks like*.

### 3.3 The outcome word ladder (LLM picks, code makes it real)

Once the player grants, the referee reads the wish's nature and the
monster's full persona (secret included) and answers one word from:

```
WISH_OUTCOMES = ('transformed', 'freed', 'departed', 'stays_changed')
```

| Word | What the wish *was* | Code consequence | Roster |
|---|---|---|---|
| `transformed` | a wish to *become* something | evolution-adjacent remake: new persona line, optional art regen; wish → `granted` | **stays** |
| `freed` | a wish to be *rid* of a burden | the burden lifts: a fear/secret is resolved into a visible persona line; wish → `granted` | **stays** |
| `departed` | a wish that *lies elsewhere* ("to see her lost sister again") | **the goodbye:** roster removal, permanent Chronicle entry, one farewell memory to every party member | **leaves** |
| `stays_changed` | a wish granted *without* parting | a warm persona beat; wish → `granted` | **stays** |

The ladder is ordered by cost-to-the-player: three of four outcomes keep
the monster; `departed` is the rare, earned heartbreak. **Code owns
which words cause departure** — only `departed` removes the roster row.
The LLM only picks the word that honestly fits the wish it was handed.

Open question §7: does code *gate* which words are eligible per wish
(e.g. offer `departed` only when the wish text names a person/place the
monster would leave *for*), or does the referee choose freely from all
four? Recommendation: free choice, with a code guard that **only
`departed` is irreversible** and everything else is a persona edit.

### 3.4 Making departure real (the ceremony)

When the word is `departed`, a departure ceremony runs — modeled on the
exit ceremony in [exit_run.py](../../backend/game/dungeon/handlers/exit_run.py):

1. **The granting scene** streams (like the chronicle) — the wish comes
   true on screen, in the monster's voice, its secret finally allowed to
   surface.
2. **Farewell memories.** One `farewell` memory is written to **every
   remaining party member** (`write_memory`, new kind — §6), so the
   party *remembers* who walked to the Gate. One `wish_granted` memory is
   written to the departing monster itself.
3. **A permanent Chronicle entry.** The run's chronicle records the
   departure as its defining beat (the chronicle already reads live state
   before the wipes — the Gate slots in cleanly ahead of `close_run`).
4. **Roster removal.** `remove_following_monster` /`remove_from_party`
   ([state/manager.py:107](../../backend/game/state/manager.py)) pull the
   monster from the party. The monster row is **retired, not deleted**
   (open question §7): flagged `departed` so it stays in the Sanctuary
   history and the future Saga (idea #7), but is excluded from the active
   roster **and from the returning-monster pool** so it never wanders
   back into an encounter (that would cheapen the goodbye — unless a
   *prophetic dream*, idea #2, deliberately reprises it).

For the three staying outcomes, only steps 1–2 run (scene + a
`wish_granted` memory), plus the persona edit; no roster change.

---

## 4. Data-model sketch

Wish progress is **mechanical state — code owns these numbers** — so it
must **not** live inside the LLM-authored `persona` JSON (which evolution
rewrites). Two options:

**Option A (recommended): a dedicated `MonsterWish` table**, one row per
monster, mirroring how `MonsterMemory` and the journal are their own
tables. One concept per file, cleanly cross-run, survives evolution
untouched.

```
monster_wish
  monster_id        FK → monsters.id (unique)   # the player row qualifies too
  status            enum WISH_STATUS  default 'dormant'
  signs             int               default 0
  sign_notes        JSON (list[str])            # referee flavor, newest last
  outcome           enum WISH_OUTCOMES nullable  # set once granted
  granted_run_id    FK → dungeon_runs.id nullable
  updated_at        timestamp
```

`core_wish` text itself stays where it already is (`persona.core_wish`) —
the table only tracks *progress toward* it.

**Option B: a `global_variables` blob** keyed by monster id, like
`run_context`. Cheaper to build, but wish progress is durable per-monster
state, not per-run — Option A fits the existing model conventions far
better. Recommend A.

**Run-scoped touch:** `run_context` gains nothing structural — the Gate
offer is computed each junction by querying `MonsterWish` for `ready`
party members. (Optionally cache `wish_gate_available: bool` in
run_context for a cheap frontend flag.)

---

## 5. The player's own wish — the last door

The player character is a monster row whose `core_wish` is their stated
wish, verbatim. So **the same machinery applies with zero special-casing
of the mechanic** — only the *framing* differs:

- The player's Wish Signs accrue from campaign-scale milestones. Cleanest
  source: **each monster wish granted at a Gate is itself a sign toward
  the player's wish** (the player learns what wishes cost by granting
  them). Plus the existing triggers pointed at the player row.
- The player's Gate is the **campaign's last door** — not offered until
  the player is `ready`, and its granting scene is the ending. Because
  the player never "departs the roster," the player's outcome ladder
  collapses to the staying words (`transformed` / `freed` /
  `stays_changed`) — or a bespoke ending beat.

Recommendation: **ship the monster Wish Engine first (§2–4), design the
player's door as a fast-follow** once the monster loop feels right. It
reuses everything; it just needs an ending screen.

---

## 6. Workflow & prompt shapes

### 6.1 Workflows (`game/dungeon/registered_workflows.py`, thin)

Following rule 6 (workflows validate-and-delegate; logic in
`handlers/`). Step names are a **frontend contract** — listed here so the
event hooks can be built against them.

- **`open_wish_gate(context, on_update) -> dict`** — the player chose to
  approach a ready monster's Gate. Delegates to a new
  `handlers/wish_gate.py`. Steps:
  `offer_choice` → (on grant) `pick_outcome` → `grant_scene`
  (streamed generation id emitted like the chronicle) → `apply_outcome`
  → (if departed) `departure_ceremony` → `chronicle`/`close`. On decline,
  a short `decline_scene` and the run continues.

Wish **Sign** detection is **not** its own workflow. Like
`check_goal_progress`, it is a helper called *inside* the workflows whose
events are triggers — `check_wish_signs(monster_id, trigger, workflow_name)`
in a new `game/monster/wish.py` (or `game/dungeon/wish.py`). It never
raises, exactly like the goal referee.

### 6.2 New prompts (`ai/llm/prompts/wish.json`)

| Prompt key | Shape | Mirrors |
|---|---|---|
| `wish_sign_check` | in: `core_wish`, `recent_events`, `signs_so_far`, `trigger`; out: `answer` ∈ `WISH_SIGN_ANSWERS`, `note` | `goal_check` |
| `wish_outcome` | in: full persona (secret included), `core_wish`, party summary; out: `outcome` ∈ `WISH_OUTCOMES`, one-line `why` | new (structured, small) |
| `wish_gate_scene` | in: everything above + chosen `outcome`; out: streamed prose (the granting) | `run_chronicle` (`build_and_stream`) |
| `wish_farewell` | in: departing monster + one recipient; out: one in-world memory line | new (cheap, per party member — or template it in code) |

Keep `wish_outcome` a separate structured call *before* the streamed
scene, so **code owns the branch** and the scene is conditioned on a word
Python already validated (same discipline as goal `answer` → log line).

### 6.3 New memory kinds (`game/memory/manager.py` `MEMORY_KINDS`)

```
'wish_sign'      # a profound moment advanced this monster's wish
'wish_granted'   # its wish was granted at the Gate
'farewell'       # a party member walked to the Gate and left (written to those who stayed)
```

### 6.4 New tuning knobs (catalog in tuning.md)

A new **"Wish Engine — `game/monster/wish.py`"** section:
`WISH_SIGNS_TO_OPEN_GATE` `3`, `MAX_WISH_SIGNS_PER_RUN` `1`,
`WISH_SIGN_AFFINITY_FLOOR` `trusting`, `WISH_GATE_AFFINITY_FLOOR`
`devoted`, `WISH_SIGN_ANSWERS`, `WISH_OUTCOMES`, `WISH_STATUS`,
`WISH_SIGN_TRIGGERS`.

---

## 7. Open questions for Aaron

1. **The knife's sharpness.** Confirm the intended cruelty: the player
   grants *without* being told the outcome, and the wish's nature (LLM)
   decides stay-vs-leave? Or should `departed` be previewed ("this wish
   may take them from you") before the player commits? The design assumes
   the former — that's the whole emotional payload — but it's your call.

2. **Outcome eligibility.** Free referee choice from all four
   `WISH_OUTCOMES`, or does code gate `departed` behind a wish that names
   a person/place to leave *for*? (Recommend free choice + the guard that
   only `departed` is irreversible.)

3. **Retire vs delete a departed monster.** Recommend *retire* (kept for
   Sanctuary/Saga history, flagged `departed`, pulled from roster **and**
   the returning pool). Confirm — and: may a prophetic dream (idea #2) or
   the Rival Party (idea #5) ever reprise a departed friend, or is
   goodbye absolute?

4. **How many signs, and the affinity floors.** `3` signs / `devoted`
   Gate floor / `1` sign-per-run are first guesses. Too slow? Too fast?

5. **Which triggers count in v1.** Ship with `goal_fulfilled` + `evolved`
   + `affinity_devoted` only, and let idea #3's confession add
   `secret_confessed` when it lands? Or hold the Wish Engine until
   Confessions/Nemesis exist so signs feel richer?

6. **Gate surfacing.** A dedicated Wish-Gate *path* at a junction
   (recommended — it reads as a place) vs an extra option on the exit
   path (cheaper). And with two ready monsters: player picks, or the
   referee surfaces the ripest wish?

7. **The player's wish — now or fast-follow?** Recommend building the
   monster engine first and pointing the same machinery at the player
   row afterward, with a bespoke ending screen. Agree?

8. **Frontend ceremony.** Does the Gate reuse the streamed-chronicle
   presentation, or does it deserve its own bespoke screen (the
   design implies something more than a scroll of text for *the* ending
   moment of a companion arc)?

---

## 8. Milestone sketch (for a future plan doc — not a commitment)

A plausible `feature/wish-engine` breakdown, smallest shippable slices
first:

- **Wsh-M1 — Signs infrastructure.** `MonsterWish` model, `wish.py`
  constants + `check_wish_signs` helper, `wish_sign_check` prompt, the
  three v1 triggers wired, `wish_sign`/status memory + SSE. *Signs accrue
  and show on the card; no Gate yet.*
- **Wsh-M2 — The Gate (staying outcomes).** `open_wish_gate` workflow +
  `handlers/wish_gate.py`, `wish_outcome` + `wish_gate_scene` prompts,
  the three non-departure outcomes, the player's grant/decline choice.
  *Wishes can be granted; nobody leaves yet.*
- **Wsh-M3 — Departure.** The `departed` outcome: farewell memories,
  Chronicle beat, roster retirement, returning-pool exclusion. *The knife
  lands.*
- **Wsh-M4 — The player's door.** Point the machinery at the player row;
  the campaign's ending screen.

Each milestone keeps the offline suites green and the plan doc truthful
(rule 7).

---

*Build the Wish Engine last. End the saga the way it began — with a wish,
and a friend who walked the whole way for one.* 🐉
