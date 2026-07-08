# RACI Matrix — LLM Monster Hunter

> **Illustrative document.** In reality one person holds most columns; the
> AI assistant is a governed executor. Separated here to model
> responsibility assignment. See [`../README.md`](../README.md).
>
> **R** = Responsible (does the work) · **A** = Accountable (owns the
> outcome, one per row) · **C** = Consulted (two-way) · **I** = Informed
> (one-way).

| Activity / Deliverable | Sponsor | PM | Architect | Dev | AI Assistant | Playtesters |
|---|:--:|:--:|:--:|:--:|:--:|:--:|
| Approve charter / phase gates | **A** | R | C | I | I | I |
| Business case | A | **R** | C | I | I | — |
| Requirements (BRD/SRS) | C | **A** | C | R | R | C |
| Architecture decisions | C | I | **A/R** | C | C | — |
| Initiative plan docs (`docs/plans/`) | C | A | **R** | R | R | I |
| Approve an initiative | **A** | C | C | I | I | I |
| Implement gameplay code | I | I | C | **A** | R | — |
| Enforce "hard rules" (layering, ceiling) | I | I | **A** | R | R (bound) | — |
| Write/maintain tests | I | I | C | **A/R** | R | — |
| Run CI / keep suites green | I | I | C | **A/R** | R | — |
| Prompt / word-ladder design | I | C | **A** | R | C | — |
| Release / deploy | C | A | C | **R** | I | I |
| Playtest & feedback | I | C | I | C | — | **R** |
| Bug triage (`docs/bug-hunt.md`) | I | A | C | **R** | R | C |
| Docs kept truthful | I | A | **R** | R | R | — |
| Risk management | C | **A/R** | C | C | I | I |
| Budget / cost tracking | **A** | R | I | C | — | — |
| Closure & lessons learned | A | **R** | C | C | I | C |

## Notes

- **One "A" per row.** Where the same human plays multiple roles in reality,
  the matrix still assigns a single accountable *role* to keep the model
  honest.
- **The AI Assistant is never "A".** It executes ("R") under governance and
  is *bound* by the architect's rules (`CLAUDE.md`). Accountability for its
  output always rests with a human role. This is the key control given the
  unusual team composition.
- **Architect owns the architecture ("A/R")** because the project's central
  risk (R-01, R-02) is architectural; that authority is deliberately
  concentrated.
