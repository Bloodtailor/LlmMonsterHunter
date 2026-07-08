# Test Cases (representative) — LLM Monster Hunter

> **Illustrative document.** A sample of concrete cases across levels.
> Real assertions live in `backend/tests/`. See [`../README.md`](../README.md).

Legend: **Pri** P0=critical. **Type** U=unit, I=integration, C=contract,
S=system. Status reflects the shipped state.

---

### TC-001 — Battle prompt contains no numbers *(the flagship test)*
- **Req:** NFR-1, FR-4.1 · **Pri:** P0 · **Type:** U
- **Pre:** a battle in progress; party & foe on word ladders.
- **Steps:** compose a battle referee prompt; scan the exact prompt text.
- **Expected:** the prompt contains **no numeric game values** (wellbeing,
  reserves, caps expressed only as ladder words).
- **Status:** ✅ Pass

### TC-002 — Impact word maps to correct ladder step + cap
- **Req:** FR-4.2–4.3 · **Pri:** P0 · **Type:** U
- **Steps:** feed referee outputs `light`, `heavy`, `devastating`; apply.
- **Expected:** each maps to the code-defined ladder movement; movement is
  clamped by the cap; softlock valve prevents incapacitation past the valve.
- **Status:** ✅ Pass

### TC-003 — Wary monster acts autonomously
- **Req:** FR-4.4 · **Pri:** P1 · **Type:** I
- **Pre:** a party monster at affinity `wary`.
- **Steps:** run a battle turn where the player issues an order.
- **Expected:** the monster may act on its own (per affinity rules) rather
  than obeying; behavior is code-gated by the affinity ladder.
- **Status:** ✅ Pass

### TC-004 — Monster generation end-to-end (stubbed)
- **Req:** FR-1.1–1.4 · **Pri:** P0 · **Type:** I
- **Steps:** trigger generation; stubbed LLM/image return canned content.
- **Expected:** a persisted monster with persona + art ref; a
  `generation_log` row exists; SSE progress/token events emitted.
- **Status:** ✅ Pass

### TC-005 — Evolution preserves identity
- **Req:** FR-6.3, D-010 · **Pri:** P1 · **Type:** I
- **Steps:** evolve a monster at the altar.
- **Expected:** **same monster id**; lineage row added; new art regenerated;
  evolution is cap-exempt.
- **Status:** ✅ Pass

### TC-006 — Memory extracted with cited sources
- **Req:** FR-6.1, FR-7.2 · **Pri:** P1 · **Type:** I
- **Steps:** run a campfire chat; trigger memory extraction.
- **Expected:** memories are created with source references; rolling summary
  updated; raw entries not deleted.
- **Status:** ✅ Pass

### TC-007 — Context budget respects the 70% cap
- **Req:** NFR-3 · **Pri:** P1 · **Type:** U
- **Steps:** assemble a prompt with oversized flexible blocks.
- **Expected:** total ≤ 70% of window; required identity blocks intact;
  flexible blocks clamped to their newest content within per-block caps.
- **Status:** ✅ Pass

### TC-008 — Workflow signature validated at import (contract)
- **Req:** FR-8, NFR-6 · **Pri:** P0 · **Type:** C
- **Steps:** import a `registered_workflows.py` with a bad signature.
- **Expected:** import-time failure (fail fast); correctly-signed
  `(context, on_update) -> dict` functions register.
- **Status:** ✅ Pass

### TC-009 — Queued work resumes and finishes on origin provider
- **Req:** NFR-4 · **Pri:** P1 · **Type:** I
- **Steps:** enqueue work under provider X; simulate restart.
- **Expected:** no lost workflow; the request completes under provider X even
  if settings changed meanwhile.
- **Status:** ✅ Pass

### TC-010 — Provider switch applies to the next generation, no restart
- **Req:** FR-9.1, NFR-7 · **Pri:** P2 · **Type:** I
- **Steps:** change provider/model in settings; trigger a new generation.
- **Expected:** the new generation uses the new provider/model; the log
  stamps the new provider+model + exact token counts.
- **Status:** ✅ Pass

### TC-011 — File-size ceiling gate
- **Req:** NFR-5 · **Pri:** P1 · **Type:** C
- **Steps:** run `tools/check_file_sizes.py`.
- **Expected:** exit non-zero if any non-grandfathered source file > 500
  lines; CI fails the build.
- **Status:** ✅ Pass

### TC-012 — Full run E2E (manual)
- **Req:** FR-3, FR-5, BR-5 · **Pri:** P0 · **Type:** S (manual)
- **Steps:** start a themed run → encounter → refereed battle → capture →
  return home → confirm persistence + chronicle entry.
- **Expected:** loop completes; monster persists; chronicle records the run;
  no numbers leaked (verify via Developer AI log).
- **Status:** ✅ Pass (playtest)

---

## Summary

| Level | Cases shown | Pass |
|---|---|---|
| Unit | 4 | 4 |
| Integration | 6 | 6 |
| Contract | 2 | 2 |
| System (manual) | 1 | 1 |
