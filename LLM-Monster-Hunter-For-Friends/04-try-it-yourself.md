# Try It Yourself

Want to actually run it? Totally doable, but let's be honest about what's
involved. This is a developer's project running on your own machine — not a
polished app you download from a store.

## What you'll need

**On your computer:**

- **Python** (3.9 or newer) — a programming language runtime
- **Node.js** (16 or newer) — powers the web interface
- **MySQL** — a database to store your monsters and progress

If those words mean nothing to you, that's okay — they're free downloads,
and the game includes an **interactive setup walkthrough** that checks what
you have and guides you through the rest.

**Two API keys** (this is the part that costs a little money):

- A **DeepSeek** key — for all the text/story AI.
  Get one at [platform.deepseek.com](https://platform.deepseek.com/)
- A **Google Gemini** key — for the monster card artwork. *Optional!* The
  game plays fine without art if you'd rather not.
  Get one at [aistudio.google.com](https://aistudio.google.com/)

You paste both keys **inside the game** (gear icon → Settings). No fiddling
with config files.

## What it costs

Not much, but not nothing. The AI usage is pay-as-you-go:

- Card art is about **7 cents per image**.
- Text is cheaper still, billed by usage.

A long, heavy play session might run you a **dollar or two, mostly in
artwork.** If you skip the art, it's just pennies of text. There's no
subscription — you only pay the AI companies for what you actually use.

## What you do NOT need

Worth calling out, because people assume otherwise:

- ❌ No fancy graphics card / GPU
- ❌ No CUDA, no local AI models, no gigabytes of downloads
- ❌ No powerful computer — it all runs on the cloud AIs

## How to start it

The project is Windows-friendly with simple launch scripts:

- Double-click **`start_game.bat`** — it runs the setup walkthrough the
  first time, then launches everything together after that.
- The game opens in your browser at **`http://localhost:3000`**.
- Paste your API keys under **⚙️ Settings**, and you're playing.

## Getting the code

It lives on GitHub: **[github.com/Bloodtailor](https://github.com/Bloodtailor)**
(ask Aaron which repo — there are two sibling versions).

If you get it running, Aaron would genuinely love to hear how it went — the
whole thing is a bit of an experiment and real feedback is gold.

➡️ Next: **[Where It's Going](05-where-its-going.md)**
