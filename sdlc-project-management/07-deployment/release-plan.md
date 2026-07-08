# Release Plan — LLM Monster Hunter

> **Illustrative document.** Models formal release management over the real
> merge/PR/soak practice. See [`../README.md`](../README.md).

## 1. Release philosophy

Small, frequent, **initiative-sized releases**. Each initiative merges to
`main` via PR after its milestones are done and its offline suites are
green; player-facing initiatives get a **soak** (extended playtest) before
being considered released.

## 2. Versioning

Semantic-ish, single-player context:

- **MAJOR** — a change that wipes or migrates save state, or breaks the SSE
  step-name/event contract (avoided; contract is additive).
- **MINOR** — a new initiative/feature (memory, evolution, chat, cloud gen).
- **PATCH** — bug fixes and polish.

| Version | Date | Contents |
|---|---|---|
| v0.1 | 2026-04-30 | MVP: generation, runs, refereed battles, capture, persistence |
| v0.2 | 2026-05-20 | Monster memory & evolution (PR #160) |
| v0.3 | 2026-05-31 | Campfire chat |
| v0.4 | 2026-06-10 | Evolution Altar |
| v0.5 | 2026-06-20 | Game Loop v1 (PR #165) |
| v0.6 | 2026-06-28 | New Game + Player Character (PRs #166/#167) |
| v0.7 | 2026-07-01 | Game Settings + DeepSeek (PR #168) |
| v0.8 | 2026-07-04 | Cloud generation (PR #169, #170) |
| v0.9 (planned) | 2026-08 | Monster Requests |

## 3. Release readiness checklist

- [ ] All offline suites green in CI.
- [ ] `tools/check_file_sizes.py` → 0 files over 500 lines.
- [ ] Lint clean (ruff / eslint / prettier).
- [ ] Plan doc updated `IN PROGRESS → IMPLEMENTED`; deviations logged.
- [ ] `architecture`/`tuning`/`api` docs updated if surfaces changed.
- [ ] SSE step names & event keys verified **additive** (no breakage).
- [ ] Manual playtest / soak pass; no open S1/S2.
- [ ] DB schema/seed changes captured in `backend/database/`.

## 4. Release process

1. Finish milestones on `feature/<initiative>`; suites green.
2. Open PR; review against the checklist and `CLAUDE.md` hard rules.
3. Soak (player-facing): extended playtest on the branch build.
4. Merge to `main`; tag version.
5. Update roadmap/plan docs; open the next initiative.

## 5. Rollback

- **Code:** revert the merge commit / redeploy the previous tag (single
  deployable app; low blast radius).
- **Data:** if a release migrated save state (MAJOR), restore from the
  pre-release DB backup (see [runbook](deployment-runbook.md) §Backup). The
  intentional **new-game world wipe** is a player action, not a rollback
  path.
- **Config:** provider/model settings are per-request and revertible in the
  settings overlay without redeploy.

## 6. Communication

Release notes summarize the initiative (player-facing "what changed") and
link the PR + plan doc. See [communication-plan](../02-planning/communication-plan.md).
