# LLM Monster Hunter Game

![Project Header](docs/assets/images/moodboard/header_image.png)

*An AI-powered monster-catching adventure where every creature has a story to tell*

[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)
[![Python 3.9+](https://img.shields.io/badge/python-3.9+-blue.svg)](https://www.python.org/downloads/)
[![React 18+](https://img.shields.io/badge/react-18+-61dafb.svg)](https://reactjs.org/)
[![Flask 3.0](https://img.shields.io/badge/flask-3.0-green.svg)](https://flask.palletsprojects.com/)

---

## 🎮 **What is This?**

At its heart, this is the archetypal fantasy adventure of capturing, training, and battling creatures. But here, every monster, every encounter, every outcome is generated in real time by AI. It's an experiment in a new coding paradigm where the code itself doesn't define the gameplay — it only provides context management and data storage, while AI does the actual storytelling, balancing, and decision-making.

Where traditional games spend compute on rendering high-fidelity graphics, this project spends compute on LLMs and image models. Where most games ship with gigabytes of pre-made assets, here you download a model, and the monsters, visuals, personalities, and even battle outcomes are created as you play.

This is a **personal project**, built solo for **educational purposes** and as part of my **portfolio**. If you've somehow found this repo — welcome! There's an **interactive setup** to guide you through installation. That said, because of the number of dependencies (Python, Node, MySQL, CUDA, ComfyUI, etc.), even with the setup script it may take a few hours to get running.

---

## ✨ **Key Features**

- **Dynamic Monster Generation** — every creature is created by an LLM with a unique persona, taxonomy, backstory, and abilities, plus ComfyUI-generated card art
- **Text-Driven, LLM-Refereed Battles** — turn-based combat narrated by the LLM; monster wellbeing and stamina/mana are positions on *word ladders*, never HP math. Attack, defend, use abilities, or **type your own free-text action** — the referee decides if it's possible
- **Battlefield Negotiation & Recruitment** — monsters join only by their own will; bargain, threaten, or plead mid-battle, and enemies can talk, plead, or flee on their own turns too
- **Dungeon Exploration** — choose between mysterious paths that each secretly hold an event: explorable locations, riddle-posing monsters, battles, treasure, or a face from a previous run
- **Persistent Monster Memories** — monsters remember battles, conversations, defeats, and journeys across runs; defeated monsters can **return changed** — hostile, friendly, or wary
- **Growth & Evolution** — small journal-earned growth during runs, and a transformative home-base **Evolution Altar** ceremony: new form, new art, evolved persona — same monster, same memories
- **Campfire Chat** — open-ended home-base conversations with your monsters, with memory extraction and rolling summaries so chats can run indefinitely
- **Items & CoCaToks** — LLM-adjudicated consumables found in dungeons, gifted in dialogue, or earned as victory keepsakes
- **Real-Time Everything** — LLM tokens and domain events stream over SSE, so the UI updates the moment each datum exists (live card reveals, streaming narration)

---

## 🚧 **Development Status**

All core mechanics are implemented and playable. Each initiative below has a full plan doc in [docs/plans/](docs/plans/):

| Initiative | What shipped |
|---|---|
| Core loop | Monster generation, dungeon paths, riddle encounters, LLM-refereed battles, battlefield recruitment |
| [Monster depth + inventory](docs/plans/monster-depth-cmdts.md) | Persona/taxonomy depth (CMDTS), items, CoCaToks, pickup ceremonies |
| [Memories & growth](docs/plans/monster-memory-evolution.md) | Cross-run memories, returning monsters, growth reflections, stamina/mana ladders |
| [Campfire Chat](docs/plans/monster-chat.md) | Home-base conversations, memory extraction, rolling summaries for all logs |
| [Evolution Altar](docs/plans/monster-evolution.md) | Transformative evolution with lineage, art regen, evolved personas |

**What's next:** turning the mechanics into a *game* — title screen, guided first run, run goals and stakes, difficulty, and an affinity system. See [docs/plans/](docs/plans/) for the Game Loop v1 proposal.

![Monster Sanctuary](docs/assets/images/monster_sanctuary.png)

---

## 🏗️ **Architecture**

The short version: a strictly-layered Flask backend orchestrates a local LLM and ComfyUI through **one gateway and two queues**, streams tokens and domain events to React over **SSE**, and follows one philosophy everywhere: **the LLM only ever picks words — Python owns every number.**

- Expensive actions queue a **workflow** and return immediately; results stream over SSE
- Combat uses **word ladders** (`fresh → … → incapacitated`), not HP math
- Prompt budgets **scale with the model's context window**; old history is condensed by rolling summaries
- Every AI request is logged byte-exact and inspectable in the in-app developer tools

Read the full tour in [docs/architecture.md](docs/architecture.md), tweak anything via [docs/tuning.md](docs/tuning.md), and see the API in [docs/api/](docs/api/README.md).

### Tech Stack
- **Backend:** Python 3.9+, Flask 3.0, MySQL 8.0, SQLAlchemy
- **Frontend:** React 18 (CRA), custom component library, SSE
- **AI:** llama-cpp-python (local GGUF), ComfyUI (SDXL Turbo)

---

## 🚀 **Quick Start**

### Prerequisites
(You'll need all of these installed before setup will work.)

- Python 3.9+
- Node.js 16+ (includes npm)
- MySQL Server
- NVIDIA GPU Drivers (latest)
- CUDA Toolkit 12.x
- Visual Studio Build Tools (with C++ components)
- ComfyUI (installed separately)

### Required Models
- **Text Model:** 7B GGUF model (recommended: *kunoichi-7b*)
- **Image Model:** SDXL Turbo (recommended: [DreamShaper XL Turbo](https://civitai.com/models/112902/dreamshaper-xl))

### Starting the Game

- Run **`start_game.bat`** to launch the game.
  - This will guide you through the setup walkthrough on first run.
  - Make sure your **ComfyUI server is already running** before starting.
  - After the first setup, `start_game.bat` starts both the backend and frontend together.
- Or individually: **`start_backend.bat`** / **`start_frontend.bat`**

⚡ *With everything installed, the game will be available at:*
👉 `http://localhost:3000`

### For Developers

- Offline test suites (LLM stubbed, dedicated test DB): `python -m pytest` or the in-app Developer screen
- Every gameplay knob is cataloged in [docs/tuning.md](docs/tuning.md)
- Working with an AI assistant? Conventions live in [CLAUDE.md](CLAUDE.md)

---

## 🤝 **Contributing**

This is mostly a solo learning project, but feedback and suggestions are welcome. If you're trying to get it running yourself — good luck, and I'd love to hear about it.

---

## 📄 **License**

This project is licensed under the MIT License – see the [LICENSE](LICENSE) file for details.

---

## 🙏 **Acknowledgments**

- **Open Source Community** – Flask, React, llama.cpp, ComfyUI, and countless others
- **AI Research Community** – for advancing the tech that makes this experiment possible

---

## **Contact**

**Aaron Orelup** — [github.com/Bloodtailor](https://github.com/Bloodtailor)

---

**Ready to catch some AI-generated monsters?** 🐉✨
