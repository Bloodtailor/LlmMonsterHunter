# Scope Statement — LLM Monster Hunter

> **Illustrative document.** See [`../README.md`](../README.md).

## 1. Product scope description

A single-player, web-based monster-catching RPG in which an LLM generates
content and referees gameplay at runtime, while conventional code owns all
state, numbers, and fairness. Delivered as a React frontend + Flask backend
+ MySQL, integrating a text LLM (cloud DeepSeek or local GGUF) and a cloud
image API through a single logged gateway, streaming to the UI over SSE.

## 2. Project deliverables

| # | Deliverable | Description |
|---|---|---|
| D1 | Generation engine | Runtime monster generation: persona text + card art via the gateway. |
| D2 | Roster / Sanctuary | Persistent collection of captured monsters (MySQL). |
| D3 | Dungeon & run system | Themed runs with goals, stakes, danger ladder, path choices. |
| D4 | Refereed battle system | Word-ladder combat; LLM referee; code-owned caps/valves. |
| D5 | Capture & negotiation | Recruit monsters, including hostile/wary ones. |
| D6 | Persistence: memory, affinity, evolution | Cross-run memories, affinity ladder, transformative evolution. |
| D7 | Campfire chat | Home-base conversations with memory extraction & rolling summaries. |
| D8 | AI gateway + queues + SSE | The orchestration spine; every AI request logged. |
| D9 | Developer tooling | AI request log, workflow inspector, test runner UI. |
| D10 | Documentation suite | `docs/` architecture, tuning, api, plans; this SDLC folder is an add-on. |

## 3. In scope

- Everything in D1–D10 above.
- Local **and** cloud text-model support; cloud-first image generation.
- Player character in the party; new-game/world-wipe flow; settings overlay.
- Offline, LLM-stubbed test suites + CI.

## 4. Explicitly out of scope

| Excluded | Rationale / where it lives |
|---|---|
| Multiplayer / networking | Single-player thesis; deferred indefinitely. |
| Native mobile / desktop apps | Web-first; not needed to prove the thesis. |
| Monetization / economy / shops | Currency of the game is affinity & memories (roadmap parking lot). |
| Sound & music | High polish, zero LLM leverage; post-Regions maybe (roadmap). |
| World map / multiple regions | Deferred to **Phase 2 initiative #4** (roadmap). |
| Social systems (bonds, nemesis arcs, monster requests) | Deferred to **Phase 2 initiatives #1–3** (roadmap). |
| Save profiles / multi-save | "Wait for a second regular player" (roadmap parking lot). |
| Per-purpose model routing | Optimization, not gameplay (roadmap parking lot). |

## 5. Acceptance criteria (product-level)

- A player can start a run, encounter a **uniquely generated** monster,
  fight a **refereed** battle, capture the monster, and see it persist —
  with **no hand-authored content** for that monster.
- **Zero numeric values appear in battle prompts;** all effects/caps are
  applied by code from LLM-chosen words.
- Every AI request appears in the developer AI log, byte-exact.
- Offline suites pass in CI; no source file exceeds 500 lines.

## 6. Constraints

- Solo delivery; governance via `CLAUDE.md` rules, not team review.
- MySQL required; cloud-API-first (no bundled local model/image service).
- Windows-primary dev environment (PowerShell), venv at `./venv`.

## 7. Assumptions

- 1M-token context floor available (prompts always fit).
- Cloud LLM + image APIs remain hobby-affordable.
- Step names and SSE event payloads are treated as a **public contract**
  (renaming = breaking change).

## 8. WBS dictionary pointer

Work packages and their decomposition are detailed in
[work-breakdown-structure.md](work-breakdown-structure.md).
