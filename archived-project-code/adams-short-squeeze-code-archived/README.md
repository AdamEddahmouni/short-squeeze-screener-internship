# short-squeeze-code

Workspace for the IST495 short-squeeze screener project (PSU).

Current reference and handoff documents:

- **[ADVISOR_SUMMARY.md](ADVISOR_SUMMARY.md)** — meeting-ready presentation brief with the opening,
  five-minute flow, before/after results, demo sequence, limitations, and decisions needed.
- **[PROJECT_NOTES.md](PROJECT_NOTES.md)** — technical notes: architecture, what works/broken,
  security issues, the engineering backlog. Start here for anything code-related.
- **[RESEARCH_LOG.md](RESEARCH_LOG.md)** — academic/internship notes: the advisor's standing goals
  and deadlines, meeting log, Kaltura recording notes, and weekly Activity Log tracking. Start here
  for anything advisor- or course-related.
- **[INTEGRATION_HANDOFF.md](INTEGRATION_HANDOFF.md)** — the schema-v1 API contract, examples,
  health/freshness semantics, configuration, and delivery checklist for the integration team.

## Layout

- **`app/ScreenerProject/`** — the active app (git submodule, own history/remote). Run this.
  See its own [ReadMe.md](app/ScreenerProject/ReadMe.md) for install/run instructions.
- **`data-workbooks/`** — Excel workbooks (RSI tables, options logs, short-interest templates) and
  the MySQL script/CSVs.
- **`diagrams/`** — Gantt/PERT/flow diagrams (draw.io format).
- **`docs/`** — misc reference docs (final reflections, etc).
- **`archive/`** — superseded prototypes, old weekly zip snapshots, legacy one-off scripts, and
  reference PDFs. Nothing here is wired into the active app; kept for history only. Includes
  `archive/prototypes/sentiment-rnd/` (formerly top-level `sentiment-rnd/`), a prior author's
  standalone sentiment prototyping folder — interactive headline labelers and a news-alert monitor,
  archived 2026-07-09 once confirmed nothing in the live app referenced it (PROJECT_NOTES.md §7).

## Working with the submodule

`app/ScreenerProject` is a separate git repo (remote: `wtg5058-byte/SHORTSQUEEZE`). Clone/update it
explicitly:

```
git submodule update --init --recursive
```

Commits inside `app/ScreenerProject` are tracked independently — `cd` into it to commit/push there,
and commit the resulting pointer bump from the top-level repo separately.
