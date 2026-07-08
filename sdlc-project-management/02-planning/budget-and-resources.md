# Budget & Resources — LLM Monster Hunter

> **Illustrative document.** All figures are modeled. In reality this is one
> person's time plus modest personal API credits. See
> [`../README.md`](../README.md).

## 1. Staffing plan (modeled)

The real team is one person plus AI coding assistants. Modeled here as
distinct roles at a nominal blended rate of **USD 60/hr** for illustration.

| Role | Person | Allocation | Phase 1 hours (modeled) |
|---|---|---|---|
| Sponsor / Product Owner | A. Orelup | 5% | ~20 |
| Project Manager | A. Orelup | 10% | ~40 |
| Lead Developer / Architect | A. Orelup | 60% | ~240 |
| AI Coding Assistant | Claude et al. | on-demand | (tooling, not billed) |
| Playtester(s) | Friends | ad hoc | ~10 |
| **Total labor** | | | **~310 hrs** |

## 2. Phase 1 budget (MVP)

| Category | Modeled cost (USD) | Basis |
|---|---|---|
| Labor (310 hrs × $60, PM-loaded to ~$5,400) | 5,400 | Notional |
| LLM API (dev + test + play) | 300 | Cloud text provider |
| Image generation API | 200 | Card art |
| Infrastructure (MySQL/local) | 100 | Mostly $0 real |
| **Total** | **6,000** | |

## 3. Ongoing run-rate (post-MVP, per month, modeled)

| Category | Cost (USD/mo) | Notes |
|---|---|---|
| LLM API | 30–80 | Scales with play volume; managed by context budgets & caching |
| Image API | 20–50 | One image path; card art on generation/evolution |
| Infra | ~0 | Local-first |
| **Est. total** | **~50–130/mo** | Dominated by per-generation cost |

## 4. Cost-control mechanisms (real, architectural)

Because run-rate is dominated by per-generation API cost, cost control is
**designed into the system**, not managed by spreadsheet:

- **Context budgets** — hard ceiling of 70% of the context window; absolute
  token caps per flexible block; required identity blocks never truncated
  (`game/utils/context_limits.py`).
- **Rolling summaries** — old history condensed by the LLM so long chats and
  runs stay affordable (`game/utils/rolling_summary.py`).
- **Provider seam** — switch between local (free, GPU cost) and cloud
  (per-token) providers per request without restart; exact token counts are
  reported and logged for every call.
- **Serialized AI queue** — one worker, no runaway concurrency/cost spikes.
- **Full logging** — every request is a `generation_log` row, so spend is
  auditable via the Developer screen.

## 5. Budget tracking (modeled EVM snapshot @ 2026-07-07)

| Metric | Value | Meaning |
|---|---|---|
| Budget at Completion (BAC, Phase 1) | $6,000 | Planned Phase 1 |
| Planned Value (PV) | $6,000 | Phase 1 fully scheduled |
| Earned Value (EV) | $6,000 | Phase 1 delivered (MVP + 7 initiatives) |
| Actual Cost (AC) | $5,700 | Under on API spend |
| Cost Performance Index (CPI) | 1.05 | Slightly under budget |
| Schedule Performance Index (SPI) | 1.00 | On schedule |

*(EVM numbers are illustrative — a hobby project doesn't truly track these,
but this is what the report would say.)*

## 6. Tooling & infrastructure resources

| Resource | Purpose | Cost |
|---|---|---|
| MySQL | Persistence (prod + `DB_NAME_TEST`) | $0 (local) |
| GitHub | VCS, PRs, CI Actions | $0 (free tier) |
| Cloud LLM (DeepSeek) | Text generation | metered |
| Local GGUF (llama-cpp-python) | Offline/free text generation | GPU/electricity |
| Gemini image API | Card art | metered |
| Dev workstation (Windows 11) | Development | sunk |
