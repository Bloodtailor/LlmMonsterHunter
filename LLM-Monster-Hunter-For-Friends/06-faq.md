# FAQ

**Is this on Steam / an app I can download?**
No. It's a personal project you run on your own computer from the source
code. See [Try It Yourself](04-try-it-yourself.md).

**Is it like Pokémon?**
In spirit, yes — catch, train, battle creatures. But nothing is pre-made;
an AI invents every monster and every battle live. Closer to "Pokémon
crossed with an AI dungeon master."

**Do I need to be good with computers to play it?**
To *play* it, once it's set up, no — it runs in your web browser. To *set it
up*, a little comfort with installing developer tools helps, though there's
a guided walkthrough. Realistically: easy if you code, a fun afternoon
project if you don't.

**Does it cost money?**
The game is free. But it uses paid cloud AIs behind the scenes, so you pay
those companies for usage — roughly a dollar or two for a heavy session,
mostly artwork. Skip the art and it's pennies. No subscription.

**Why does the AI decide who wins battles? Doesn't that make it random or
unfair?**
Good instinct, but no — this is the cleverest part. The AI only *narrates*
and picks descriptive words ("heavy hit"); the actual game rules, limits,
and fairness are enforced by ordinary code. You get AI creativity without AI
math errors. There's a whole explanation in
[How It Works](03-how-it-works.md).

**Are the monsters really unique, or is it faking it?**
Genuinely unique. There's no monster list in the game — each one is written
and painted fresh. Two players will never see the same creature.

**Do the monsters actually "remember" me?**
Yes. Their memories are stored and fed back to the AI, so a monster recalls
your shared battles and conversations across sessions, and its feelings
toward you evolve.

**What AI does it use?**
Text/story: **DeepSeek**. Artwork: **Google Gemini**. Everything routes
through one place in the code, so it's swappable.

**Can I see the code?**
Yep — it's open source on GitHub at
[github.com/Bloodtailor](https://github.com/Bloodtailor). It's MIT-licensed
and, honestly, pretty cleanly written if you want to poke around.

**What's the "two versions" thing?**
There are sibling projects: this **cloud** edition (big smart AIs, small
cost) and a **local** edition (tries to run a small AI on your own machine
for free, which forces a very different design). Same core idea, opposite
bets.

**Who made this and why?**
Aaron, solo, as a learning project and portfolio piece — to get good at
building real software and working with AI. Not a company, not a product,
just an idea he couldn't put down.

**How do I get in touch / give feedback?**
Through GitHub: [github.com/Bloodtailor](https://github.com/Bloodtailor).
Feedback is very welcome.

---

⬅️ Back to the **[start](README.md)**
