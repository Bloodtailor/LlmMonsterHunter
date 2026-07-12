# Try It Yourself

Want to actually run it? Totally doable — even if you've never used a
terminal in your life. It's still a developer's project running on your own
machine, not a polished app from a store, but the setup now does almost
everything itself.

## What you'll need

**On your computer:** a Windows 10 or 11 PC. That's genuinely it — the
game's launcher installs the free software it's built on (Python, Node.js)
by itself, and walks you step-by-step through the one install that needs
you (MySQL, the free database that stores your monsters). You never type a
command.

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

Three steps, honestly:

1. **Get the game folder** — on the GitHub page, click the green **Code**
   button → **Download ZIP**, then unzip it anywhere (right-click →
   Extract All).
2. **Double-click `start_game.bat`** in that folder. The first run sets
   everything up — just do what the window says. (If it asks you to close
   it and double-click again after installing something, that's normal.)
   Every run after that, the same double-click just starts the game.
3. **Paste your key.** The game opens in your browser at
   `http://localhost:3000` — click the **⚙️ gear icon**, paste your
   DeepSeek key, and you're playing.

## Getting the code

It lives on GitHub: **[github.com/Bloodtailor](https://github.com/Bloodtailor)**
(ask Aaron which repo — there are two sibling versions).

If you get it running, Aaron would genuinely love to hear how it went — the
whole thing is a bit of an experiment and real feedback is gold.

➡️ Next: **[Where It's Going](05-where-its-going.md)**
