# User Stories & Product Backlog — LLM Monster Hunter

> **Illustrative document.** Story points and sprint tags are modeled; the
> epics map to real shipped initiatives. See [`../README.md`](../README.md).

## Format

`As a <role>, I want <capability>, so that <benefit>.`
Priority: **P0** (MVP-critical) → **P3** (nice-to-have). Estimate in story
points (Fibonacci). Status reflects the real shipping order.

---

## Epic A — Monster Generation (MVP)

| ID | Story | Pts | Pri | Status |
|---|---|---|---|---|
| A-1 | As a player, I want to encounter a **uniquely generated monster** so that every run feels new. | 8 | P0 | ✅ Done |
| A-2 | As a player, I want the monster to have **card art** so that it feels real. | 5 | P0 | ✅ Done |
| A-3 | As a player, I want to **watch it generate live** (streaming) so waiting feels alive. | 5 | P0 | ✅ Done |
| A-4 | As a developer, I want **every prompt logged byte-exact** so I can debug generation. | 3 | P0 | ✅ Done |

**Acceptance (A-1):** Given a run in progress, when an encounter triggers,
then a monster with a distinct name/persona is produced via the gateway,
persisted, and revealed on a card — with no pre-authored content.

---

## Epic B — Refereed Battle (MVP)

| ID | Story | Pts | Pri | Status |
|---|---|---|---|---|
| B-1 | As a player, I want battles **narrated by the AI** so combat is story, not stats. | 8 | P0 | ✅ Done |
| B-2 | As a player, I want outcomes to be **fair** so the AI can't cheat me. | 13 | P0 | ✅ Done |
| B-3 | As a player, I want a **wary monster to sometimes act on its own** so low affinity has stakes. | 5 | P1 | ✅ Done |

**Acceptance (B-2):** Given any battle turn, when the referee returns an
impact/cost word, then code maps it to ladder steps and applies caps and
softlock valves; **no numeric value ever appears in the prompt**.

---

## Epic C — Roster, Runs & Capture (MVP)

| ID | Story | Pts | Pri | Status |
|---|---|---|---|---|
| C-1 | As a player, I want to **capture** monsters so I can build a party. | 8 | P0 | ✅ Done |
| C-2 | As a player, I want a **Sanctuary** that persists my collection. | 5 | P0 | ✅ Done |
| C-3 | As a player, I want **themed runs with goals and stakes** so runs have purpose. | 8 | P0 | ✅ Done |
| C-4 | As a player, I want to **negotiate with hostile monsters** so recruiting is a choice. | 5 | P1 | ✅ Done |

---

## Epic D — Persistence & Attachment (Phase 2)

| ID | Story | Pts | Pri | Status |
|---|---|---|---|---|
| D-1 | As a player, I want monsters to **remember** past runs so they feel real. | 8 | P1 | ✅ Done (PR #160) |
| D-2 | As a player, I want monsters to **grow and evolve** while staying themselves. | 13 | P1 | ✅ Done |
| D-3 | As a player, I want to **chat with monsters at the campfire** so I bond with them. | 8 | P1 | ✅ Done |
| D-4 | As a player, I want a **chronicle** of my journey so runs become a story. | 5 | P1 | ✅ Done (PR #165) |

---

## Epic E — Platform, Settings & New Game (Phase 2)

| ID | Story | Pts | Pri | Status |
|---|---|---|---|---|
| E-1 | As a player, I want to **create a character** and be in the party. | 8 | P1 | ✅ Done (PRs #166/#167) |
| E-2 | As a player, I want a **settings overlay** to pick my AI model. | 5 | P2 | ✅ Done (PR #168) |
| E-3 | As a player, I want **higher-quality cloud art** and bigger context. | 8 | P2 | ✅ Done (PR #169) |
| E-4 | As a developer, I want **local or cloud text models** switchable without restart. | 5 | P2 | ✅ Done |

---

## Epic F — Phase 2 Drama Systems (Planned)

| ID | Story | Pts | Pri | Status |
|---|---|---|---|---|
| F-1 | As a player, I want monsters to **ask things of me** (requests) so the cast drives the plot. | 13 | P1 | ⏳ Planned (`monster-requests.md`) |
| F-2 | As a player, I want **recurring nemeses** that remember me. | 13 | P2 | ⏳ Planned |
| F-3 | As a player, I want **monsters to bond with each other**. | 21 | P2 | ⏳ Planned |
| F-4 | As a player, I want **distinct regions** to explore. | 21 | P3 | ⏳ Planned |
| F-5 | As a player, I want **my character to earn titles** and grow. | 8 | P3 | ⏳ Planned |

---

## Backlog health notes

- The backlog is ranked by **fun-per-effort**, not just priority — see
  [`docs/roadmap.md`](../../docs/roadmap.md).
- Deferred items with recorded reasons live in the roadmap **parking lot**
  (pack encounters, economy, sound, multi-save, model routing).
- Raw idea intake: [`docs/ideas.md`](../../docs/ideas.md).
