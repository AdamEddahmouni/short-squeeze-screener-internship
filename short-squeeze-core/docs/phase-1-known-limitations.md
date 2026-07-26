# Phase 1 Known Limitations

The Phase 1 foundation is an **offline, deterministic evidence layer**. It deliberately models
only objective, provider-reported facts and their point-in-time availability. It does not yet
contain, and this release candidate does not add, any of the following:

- Live provider connections, historical downloads, or streaming.
- Databases, web APIs, GUIs, or alerting.
- Paper trading or live trading; order placement, cancellation, or routing.
- Order-book depth or synthetic NBBO construction.
- Derived metrics of any kind: relative-volume calculation, returns, gaps, ranges, volume
  baselines, moving averages, Bollinger Bands, Keltner Channels, TTM Squeeze, RSI, MACD, ATR,
  momentum, breakout/trend/gap classification.
- Order-flow imbalance, aggressor-side inference, spread analytics, or liquidity scoring.
- Sentiment or catalyst classification.
- Candidate scoring, Prime/Subprime tiers, ranking, recommendations, entries, exits, targets,
  stops, or backtesting.
- Machine learning of any kind.

## Deliberate scope boundaries carried forward

- Provider-published values (relative volume, VWAP, short-float percent, days-to-cover) are
  preserved verbatim and never recomputed.
- Missing values are distinct from zero across every domain; `TradePayload.size` is nullable so
  unavailable size is never fabricated as zero.
- Crossed/locked quote structure is objective and never forced to `INVALID`.
- Represented event time (settlement date, period of report, halt/resume time, bar_end, trade/quote
  event time) never substitutes for provider availability, local receipt, or effective time.
- The evidence layer never averages sources, selects an unexplained winner, or silently overwrites
  changed content; conflicts, duplicates, and temporal differences are preserved and classified.

## Environment / operational notes

- **Locked `.pytest-tmp` directory (INFORMATIONAL).** The repository's `pyproject.toml` configures
  pytest with `--basetemp=.pytest-tmp`. The working tree contains a pre-existing `.pytest-tmp` and
  several `.pytest-run-*` directories with restrictive ACLs (created by an earlier, different tool
  runtime) that the current user cannot delete. A bare `python -m pytest` therefore fails during
  temp-dir cleanup with `WinError 5`. This is an environment artifact, **not** a code or test
  defect: passing `--basetemp=.pytest-run-<name>` (a gitignored path) makes the full suite pass.
  The audit did not mutate `pyproject.toml`, because the collision is environmental and changing
  the configured invocation is out of scope for a compatibility audit. Future operators on a clean
  checkout are unaffected.

- **Timezone-database portability skip.** One test is skipped by design when the IANA timezone
  database is unavailable on the host; this is the established, expected single skip.

## Fixture / architecture notes (deferred, not defects)

- Fixture-metadata schema drifts across phases (inline per-case origins vs `families` vs
  `allowed_origins`). All shapes are honest and classified within the allowed set; converging the
  schema would alter fixture bytes and recorded content hashes, so it is deferred to preserve
  anchors. See [`phase-1-fixture-provenance-audit.md`](phase-1-fixture-provenance-audit.md).
- Adapters share conceptually similar timestamp/date-only/decimal-parsing/raw-hashing/diagnostic
  logic. Extracting a shared abstraction is deferred because the behaviors are not provably
  identical across providers and any refactor risks changing existing anchors. See the
  architecture-consistency section of
  [`phase-1-release-candidate-report.md`](phase-1-release-candidate-report.md).
