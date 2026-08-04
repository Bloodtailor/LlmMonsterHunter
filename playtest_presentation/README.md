# Playtesting Without Playing — the presentation

A fifteen-minute narrated walkthrough of the playtest-suite expansion
(`docs/plans/playtest-suite-expansion.md`), built as a keyframed web app.
Every slide links to the real file in this repository that produced its
numbers.

## Watching it

```bash
./venv/Scripts/python.exe playtest_presentation/serve.py
```

That opens <http://localhost:8088> in your browser. Use this rather than
`python -m http.server`: the built-in server does not answer Range
requests, so the scrubber moves but the audio does not seek. Opening
`index.html` straight from disk works too.

Controls: **Play** starts the narration and the deck advances itself as
each section's audio ends. **1× / 2× speed** toggles double speed
without re-generating anything — the audio element's playback rate is
the only clock. `space` plays and pauses, `←` `→` step between
sections, and the chapter rail on the left jumps anywhere.

## What is here

| File | What it is |
| --- | --- |
| `index.html` | The shell — rail, stage, transport |
| `data.js` | The deck: every slide's content, metrics, and file links |
| `player.js` | Builds the deck, keeps audio and slides in step |
| `app.css` | The visual world (single-theme by choice: a darkened room) |
| `script.md` | The narration, section by section — the source of the audio |
| `audio/NN.mp3` | One narration file per section |
| `generate_audio.py` | Rebuilds the audio from `script.md` |

## Changing the narration

Edit `script.md`, then re-run the generator with your ElevenLabs key in
the environment (it is never stored in this repo):

```bash
ELEVENLABS_API_KEY=your-key ./venv/Scripts/python.exe playtest_presentation/generate_audio.py
```

Unchanged sections are skipped, so fixing one paragraph re-bills one
section. `--only 10,11` limits it further; `--dry-run` prints the word
counts and running time without spending anything.
