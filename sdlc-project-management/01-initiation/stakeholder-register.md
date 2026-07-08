# Stakeholder Register — LLM Monster Hunter

> **Illustrative document.** In reality most of these "roles" are one
> person (Aaron / Bloodtailor). They are separated here to model formal
> stakeholder analysis. See [`../README.md`](../README.md).

## Register

| ID | Stakeholder / Role | Interest in project | Influence | Interest level | Engagement strategy |
|---|---|---|---|---|---|
| S-01 | **Sponsor / Product Owner** (A. Orelup) | Owns vision, funding, and go/no-go | High | High | **Manage closely** — approves charter, scope, phase gates |
| S-02 | **Project Manager** (A. Orelup) | Delivery on time/scope | High | High | **Manage closely** — owns plan, risk, backlog |
| S-03 | **Lead Developer / Architect** (A. Orelup) | Technical soundness | High | High | **Manage closely** — owns architecture rules in `CLAUDE.md` |
| S-04 | **AI Coding Assistant(s)** (Claude, etc.) | Executes tasks under the rules | Medium | High | **Keep informed & governed** — bound by `CLAUDE.md` "hard rules"; work reviewed before merge |
| S-05 | **Players / Playtesters** ("for friends" build) | Fun, fairness, stability | Medium | High | **Keep satisfied** — playtest feedback → backlog |
| S-06 | **LLM API provider** (DeepSeek / local GGUF) | Usage, cost, availability | Medium | Low | **Monitor** — provider seam abstracts them; cost tracked |
| S-07 | **Image API provider** (Gemini image API) | Usage, content policy, cost | Medium | Low | **Monitor** — single image path; watch policy/cost |
| S-08 | **Open-source / GitHub audience** | Learning from the repo | Low | Medium | **Keep informed** — clean `docs/`, honest plan docs |
| S-09 | **Future maintainers** | Onboarding ease, code health | Low | Medium | **Keep informed** — architecture docs, 500-line ceiling, CI |

## Power / interest grid

```
        HIGH INTEREST                     LOW INTEREST
      ┌───────────────────────────┬───────────────────────────┐
 HIGH │ MANAGE CLOSELY            │ KEEP SATISFIED            │
POWER │ S-01 Sponsor              │ (none — solo project      │
      │ S-02 PM                   │  collapses these roles)   │
      │ S-03 Architect            │                           │
      ├───────────────────────────┼───────────────────────────┤
 LOW  │ KEEP INFORMED            │ MONITOR                   │
POWER │ S-04 AI assistant         │ S-06 LLM provider         │
      │ S-05 Playtesters          │ S-07 Image provider       │
      │ S-08 GitHub audience      │                           │
      │ S-09 Future maintainers   │                           │
      └───────────────────────────┴───────────────────────────┘
```

## Notes on the AI assistant as a governed stakeholder (S-04)

Unusually for this project, a primary "team member" is an AI coding
assistant. Governance is real and codified in
[`CLAUDE.md`](../../CLAUDE.md): architecture-first thinking, strict layering,
the "LLM picks words, code owns numbers" rule, and a 500-line file ceiling.
This register treats the assistant as a **high-execution, governed**
stakeholder whose output is bounded by those rules and verified by tests +
CI before it becomes part of the product.
