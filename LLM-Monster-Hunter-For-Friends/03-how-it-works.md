# How It Works (No CS Degree Required)

You don't need to be a programmer to appreciate the clever bits. Here are
the ideas that make this project tick, in plain English. (If you *are*
technical, there's a "for the nerds" note at the bottom.)

## The one big rule: the AI picks words, the code owns the numbers

This is the heart of the whole design, and it solves a real problem.

AI language models are wonderful storytellers but **terrible
accountants.** Ask one to track hit points across a 20-turn battle and it'll
cheerfully cheat, forget, or hand out 9,000 damage because it sounded
dramatic. You can't trust it with math.

So the game splits the job:

- **The AI is the storyteller and judge.** It decides *what happens* — "the
  fire lizard lands a heavy blow" — and picks from a small menu of words
  the game gives it: was the hit `light`, `heavy`, or `devastating`?
- **The code is the accountant.** It takes that word and does the actual
  bookkeeping — moving the monster one notch down the health ladder,
  applying limits so nothing gets silly, making sure the game stays fair.

That's why a monster's health is `wounded` instead of `43/80`. The "ladder"
of words is something the code fully controls; the AI just chooses which
rung fits the story. You get AI creativity *and* a game that doesn't fall
apart. This same trick runs everything — battles, energy, growth,
relationships.

## The code is a librarian, not an author

The game's job is to remember things and hand the right context to the AI
at the right moment. Who's in your party, what happened last run, what this
monster remembers about you — the code organizes all of that and feeds a
tidy summary to the AI so its stories stay consistent.

Because these AI models can only "hold in mind" so much at once, there's
careful budgeting: the important stuff (who your monsters are) always gets
included in full, while long histories get **summarized** by the AI itself
so old adventures don't get forgotten but also don't overwhelm it. Nothing
is ever truly deleted — just condensed.

## Two AIs working together

- A **text AI** (currently a model called DeepSeek) handles all the
  writing, refereeing, and conversation.
- An **image AI** (Google's Gemini) paints the monster cards.

Everything funnels through a single "front desk" in the code — every
request to either AI goes through one door. That means every single thing
the AI was ever asked is logged and inspectable, which is great for
debugging and for understanding what the AI is actually doing.

## It's all real-time

Rather than making you wait for a monster to be fully created and then
showing it, the game streams everything as it happens — you literally watch
the AI's words appear and the card come to life. Under the hood this uses a
"live feed" from the server to your browser.

## Nothing blocks

When you ask for something expensive (generate a monster, take a battle
turn), the game doesn't freeze while it waits. It puts the job in a queue,
lets you keep going, and the result streams in when it's ready. Everything
is orderly — one AI request at a time, in line — so things stay consistent.

---

## For the nerds 🤓

If you write code, here's the actual shape of it:

- **Backend:** Python + Flask, MySQL database, SQLAlchemy. Strictly layered:
  thin HTTP routes → services (validation/trust boundary) → game logic →
  a single AI **gateway**. Two single-worker queues (one for workflows, one
  for AI calls) keep everything serialized and consistent.
- **Frontend:** React (18), with a custom component library, talking to the
  backend over HTTP for actions and **Server-Sent Events (SSE)** for the
  live token/event stream.
- **The "words not numbers" thing** is literally implemented as enums / word
  ladders in `game/battle/constants.py`, with Python mapping the AI's chosen
  word to capped numeric effects. The AI never sees a number in a prompt.
- **Async model:** expensive actions register a *workflow* that returns a
  `workflow_id` immediately; progress and results arrive over SSE. Step
  names in those workflows are treated as a contract the frontend keys off.
- **AI provider seam:** the gateway resolves settings per-request and can
  dispatch to a cloud API (DeepSeek) or a local GGUF model, stamping the
  provider/model onto every logged request.
- **Testing:** offline test suites stub out the AI and use a dedicated test
  database, so the whole thing is testable without spending a cent on API
  calls.

It's genuinely well-organized — there's a 500-line-per-file ceiling,
one-concept-per-file discipline, and a real architecture doc. Aaron cares
about this being a *clean* codebase, not just a working demo.

➡️ Next: **[Try It Yourself](04-try-it-yourself.md)**
