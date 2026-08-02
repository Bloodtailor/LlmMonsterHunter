# frontend/src/components/ — feature components

Rules for working in this directory. Repo-wide rules are in the root
`CLAUDE.md`.

## Folder shape

One folder per feature (`battle/`, `dungeon/`, `chat/`, `cards/`,
`evolution/`, `player/`, `inventory/`, `settings/`, `streaming/`,
`developer/`, `debug/`…). Each has an `index.js` barrel — that barrel is
the feature's public surface, and other features import through it rather
than reaching into files.

Larger features split further into `components/`, `screens/`, and
`hooks/`. Small ones stay flat. Follow the neighbours.

## Where state and data come from

- **Shared state** lives in `app/contexts/` (Navigation, Party, Dungeon,
  Battle, Event). Read it through the context, do not duplicate it here.
- **Server data** goes through `api/` services. Components do not build
  URLs or call `fetch` directly.
- **Live updates** arrive through `useEventSubscription` and
  `useStreamedGeneration`. Never open an `EventSource` in a component —
  there is one SSE connection, owned by `EventProvider`.

## String literals here are backend contracts

Two kinds of string in this directory are shared with Python and are
checked by suites:

- **Workflow step names** in `*_STEP_LABELS` maps and in
  `step === '...'` comparisons. Referencing a step the backend cannot
  emit fails `backend/tests/test_step_contract.py` — and silently shows
  nothing if it ever escapes the suite.
- **Event names** in `api/events/*EventHandlers.js`, checked against the
  backend registry by `backend/tests/test_event_parity.py`. A new handler
  file must also be spread into `EventProvider.js` or its events are
  never delivered.

## UI primitives

Import from `shared/ui` (the `ui/index.js` barrel, or a primitive's own
`index.js`). If something presentational is wanted by a second feature,
move it to `shared/ui/` rather than importing across feature folders.

## Verification

```bash
npx prettier --check src     # from frontend/
npm test                     # jest
```
