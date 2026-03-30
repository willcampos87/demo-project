# YouTube niche intelligence → Slides → Gmail (one-pager)

**Goal:** Pull public data on AI / AI-automation YouTube (seed channels + recent uploads), compute what’s working, ship a **Google Slides** deck with charts, and **email** it via **Gmail**. Execution in `tools/`; instructions in `workflows/`; scratch in `.tmp/`; live deliverables in Google (see [CLAUDE.md](../CLAUDE.md)).

**Quota rule:** Avoid burning `search.list` (100 units/call). Use **channel → uploads playlist → `playlistItems.list` + `videos.list`** (~1 unit/call). Cache channel IDs; use search only for occasional discovery.

**Stack:** YouTube Data API v3, Google Slides API, Gmail API; OAuth `credentials.json` / `token.json` (gitignored); Python + pandas + chart lib → PNGs → Slides.

| Phase | Deliverable |
|-------|----------------|
| 0 | GCP project + APIs enabled; one verified read-only ingest of a single channel’s uploads |
| 1 | Raw ingest to `.tmp/` (jsonl/csv) |
| 2 | Metrics CSV (top performers, engagement; velocity = two snapshots later) |
| 3 | Chart PNGs |
| 4 | Slides deck (link) |
| 5 | Gmail send (link + optional PDF) |
| 6 | Schedule (e.g. weekly) + workflow doc |

**v1 out of scope:** Full transcripts, mass comment scrape, web UI scraping as core.

**Build order:** 1 → 2 → 3 → 4 → 5 → 6. **Commit only when each phase is verified.**

**Full detail:** [youtube-niche-intelligence.md](./youtube-niche-intelligence.md)
