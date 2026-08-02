# frontend/src/shared/ — the cross-feature layer

Rules for working in this directory. Repo-wide rules are in the root
`CLAUDE.md`.

## What belongs here

**Only things used by more than one feature.** If exactly one feature
needs it, it belongs in `components/<feature>/`. Moving something here
"because it might be reused" is how a shared layer turns into a second
components folder.

- `ui/` — the component library (presentational primitives only)
- `styles/` — theme, typography, colour, globals
- `hooks/` — cross-feature React hooks
- `constants/`, `utils/` — cross-feature values and helpers

## ui/ conventions

- One folder per primitive (`Button/`, `Card/`, `Form/`…), containing the
  component files, its `.css`, and an `index.js` barrel.
- Everything is re-exported from `ui/index.js`, which is the front door
  most features import from.
- **Primitives stay presentational.** No game vocabulary, no API calls,
  no context reads. A primitive that knows what a monster is belongs in
  `components/`.
- [`ui/ui.md`](ui/ui.md) is the prop reference for every primitive.
  Changing a component's props or its exported constants means updating
  it in the same change — nothing checks this, so it is on you.

## styles/

Components consume theme tokens rather than hardcoding colours or sizes.
When a value needs to exist in more than one component, it belongs in
`styles/`, not repeated in two `.css` files.

## Verification

```bash
npx prettier --check src     # from frontend/
npm test                     # jest
```

ESLint enforces the repo's `max-lines` ceiling here as well as in the
rest of `src/`.
