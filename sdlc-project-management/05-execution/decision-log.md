# Decision Log (ADR-lite) — LLM Monster Hunter

> **Illustrative document.** Architecture/product decisions with rationale.
> Many restate real, load-bearing choices from `CLAUDE.md` and
> `docs/architecture.md`. See [`../README.md`](../README.md).
>
> Format per entry: **Context → Decision → Consequences.**

## D-001 — Single AI gateway for all generation
- **Context:** AI calls scattered across the codebase would be
  unobservable and impossible to govern.
- **Decision:** every LLM and image request routes through `ai/gateway.py`;
  no exceptions. Each becomes a `generation_log` row.
- **Consequences:** one place for logging, budgets, provider choice;
  byte-exact Developer AI log; the rule is non-negotiable in `CLAUDE.md`.

## D-002 — The LLM picks words; code owns numbers
- **Context:** letting an LLM emit game numbers is unfair and irreproducible.
- **Decision:** mechanics define **word ladders/enums**; the LLM chooses a
  word; code maps words to effects, caps, and valves (`game/battle/constants.py`).
- **Consequences:** fairness + reproducibility (the thesis, NFR-1); new
  mechanics MUST follow this pattern.

## D-003 — Async workflows + SSE instead of synchronous HTTP
- **Context:** generation/battle turns are too slow for a request/response.
- **Decision:** expensive actions queue a `@register_workflow` function and
  return `{ workflow_id }`; results stream over SSE.
- **Consequences:** live UX; DB-backed reliability; a new contract surface
  (step names) to protect.

## D-004 — Step names & SSE payload keys are a public contract
- **Context:** the frontend keys event hooks off workflow step strings.
- **Decision:** treat step names and payload keys like an API — additive
  changes only; renames are breaking.
- **Consequences:** stability (NFR-6); new steps for new features are
  additive, avoiding contract breakage.

## D-005 — Two serialized queues (workflow + AI)
- **Context:** one GPU / one model can't handle concurrent calls.
- **Decision:** a workflow queue (one worker) above a serialized AI queue
  (one worker); both DB-backed.
- **Consequences:** predictable cost/latency; no lost work on restart;
  queued work finishes on its origin provider.

## D-006 — Provider seam, resolved per request
- **Context:** need both free local generation and higher-quality cloud.
- **Decision:** `ai/llm/provider_settings.py` resolves settings (DB over
  env) and stamps provider+model per request; processor dispatches to
  `local.py` / `deepseek.py`.
- **Consequences:** switch models without restart; uniform contract back
  (text + exact token counts + model name); cost control (CR-001).

## D-007 — 500-line file ceiling, one concept per file
- **Context:** solo + AI-assistant development risks god-files and sprawl.
- **Decision:** hard 500-line ceiling (CI-enforced), one concept per file,
  heavy WHY-comments, no abbreviations.
- **Consequences:** maintainability (NFR-5); split-before-you-hit-it;
  grandfather list never grows (CR-002).

## D-008 — Context budgets under a 1M-token floor
- **Context:** prompts fit, but tokens cost money and dilute attention.
- **Decision:** hard 70% window cap; per-block absolute caps; required
  identity blocks never truncated; rolling summaries for old history.
- **Consequences:** deliberate spend (NFR-3); long chats/runs stay
  affordable; raw entries never deleted (CR-006).

## D-009 — Offline suites stub the LLM and use a dedicated test DB
- **Context:** LLM non-determinism makes tests flaky and costly.
- **Decision:** suites run with the LLM (and image API) stubbed against
  `DB_NAME_TEST` (built by `harness.py`); every real request is logged for
  replay debugging.
- **Consequences:** fast, safe, deterministic CI (NFR-8); reproducible bug
  investigation despite runtime non-determinism (R-09).

## D-010 — Evolution keeps the same monster id
- **Context:** transformative evolution risks destroying the player's bond.
- **Decision:** evolution mutates in place (same id), records lineage, and
  regenerates art; cap-exempt.
- **Consequences:** identity/attachment preserved (BR-4); lineage table +
  art regen pipeline reused later (player evolution, nemesis growth).

## D-011 — Sequence Phase 3 as drama before structure
- **Context:** engine rooms are built; the game is light on inter-character
  drama.
- **Decision:** Requests → Nemesis → Bonds → Regions. Structural variety
  (regions) comes after the cast is alive.
- **Consequences:** "variety without drama is scenery"; regions get a
  populated world to live in (roadmap; CR-007).
