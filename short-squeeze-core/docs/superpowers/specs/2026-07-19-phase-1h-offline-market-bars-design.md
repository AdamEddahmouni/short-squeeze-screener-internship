# Phase 1H Offline Market-Bar Evidence Design

## Scope and evidence basis

Phase 1H adds deterministic offline normalization and point-in-time selection of objective market bars. It answers which partial, completed, corrected, cancelled, duplicated, or conflicting bars were available locally at a requested time, with their exact interval, boundaries, session, source, price, volume, and lifecycle metadata. It does not calculate returns, gaps, relative volume, rolling volume, indicators, momentum, breakouts, trends, scores, ranks, entries, exits, or recommendations.

The read-only archive review covered the three preserved Git repositories at `0897562e05d75b812dd284de81dfafdfa1dea916`, `6dbefd1a6b271bfc48106c4aa002f211735551cd`, and `84f770ddf33cf35bbe4ec3d8dfc12876d0068fd8`, including tracked and ignored data while excluding `.env`, token files, credentials, virtual environments, caches, and Git internals.

| Exact archived path | Fields and source shape | Evidence classification | Timing limitations | Fixture disposition |
|---|---|---|---|---|
| `archived-project-code/adams-short-squeeze-code-archived/app/ScreenerProject/core/ib_api.py` | IB `reqHistoricalDataAsync`, `30 D`, `1 day`, `TRADES`, `useRTH=True`; consumes bar `close`, `high`, `low`, `volume` | Recorded source code describing IB-shaped daily bars | No saved provider response, capture time, receipt time, provider record ID, or correction state | Representative shape basis only |
| `archived-project-code/adams-short-squeeze-code-archived/app/ScreenerProject/core/schwab_api.py` | Schwab `/pricehistory`, month/1/daily/1; candle `close`, `high`, `low`, `volume` | Recorded source code plus mocked samples | Tests omit timestamps, open, publication, capture, receipt, session, and identity | Representative shape basis only |
| `archived-project-code/adams-short-squeeze-code-archived/app/ScreenerProject/tests/test_schwab_api.py` | Constructed daily candle dictionaries | Mocked representative sample | Invented values and no delivery provenance | Representative shape basis only |
| `archived-project-code/adams-short-squeeze-code-archived/app/ScreenerProject/core/chart_data.py` and `tests/test_chart_data.py` | Yahoo-shaped 30-minute timestamp/close series with UTC test index | Recorded parser code plus mocked representative frame | No OHLCV, source publication, receipt, provider ID, session, or adjustment semantics | Representative timestamp/interval shape basis only |
| `data-workbooks/MySQL/Short_Interest_Prediction_Template.csv` | Date/ticker/price/volume snapshot rows | Historical derived/screener dataset | Not bars; no interval, OHLC, provider identity, capture, receipt, or correction provenance | Unusable as bar fixtures |
| `data/squeeze_score_history.csv` and `data/corroboration_history.csv` | Application timestamp, ticker, derived score | Historical application logs | Not price/volume bars | Unusable |

No defensible saved provider bar record exists. Every Phase 1H fixture is exactly `SANITIZED_REPRESENTATIVE_SAMPLE` or `SYNTHETIC_EDGE_CASE`; none is `SANITIZED_RECORDED_SAMPLE`.

## Canonical contract decision

The existing `EventType.BAR` and `BarPayload(timeframe, open, high, low, close, volume, trade_count, vwap)` are sufficient and remain unchanged. Schema stays `1.0.0`.

- `timeframe` uses a strict canonical interval name: `1_MINUTE`, `5_MINUTES`, `15_MINUTES`, `30_MINUTES`, `1_HOUR`, or `1_DAY` for Phase 1H fixtures.
- `open`, `high`, `low`, `close`, and `vwap` use exact `Decimal`; no missing price is calculated. Because canonical OHLC is required, a record missing any OHLC field is rejected, including a partial record.
- `volume` and `trade_count` are nullable non-negative integers. Missing remains null; observed zero remains zero. Share volume is supported for equity fixtures. Contract/unit ambiguity rejects.
- Envelope `source_timestamp` is provider publication/availability, `received_timestamp` is context ingestion, and `effective_timestamp` is their maximum. The represented bar interval never grants availability.
- Envelope `market_session` stores the objective supported session mapping. `OVERNIGHT` and `EXTENDED` remain explicit provider metadata and map to `UNKNOWN` and the supplied broader state respectively because changing the canonical enum would alter compatibility.
- Envelope `exchange`, `asset_class`, and `symbol` retain their canonical meanings.
- Structured provenance stores `bar_start`, exclusive `bar_end`, interval magnitude/unit/kind, provider timestamp and its declared meaning, publication and capture timestamps, session date, source session label, volume unit, completion/lifecycle status, revision number, superseded provider ID, boundary key, fixture origin, and provider metadata.
- `quality.completeness` distinguishes partial from complete; lifecycle status remains provenance because `CORRECTED` and `CANCELLED` describe immutable source records, not missing canonical fields.

This choice preserves every Phase 1A-1G observation and hash. A breaking change is neither required nor permitted.

## Provider record, aliases, and intervals

`MarketBarRecord` is immutable, forbids unknown fields, and accepts only `MARKET_BAR_V1` / `MARKET_BAR`. Neutral fields include provider identity, symbol, asset class, exchange, interval, explicit start/end or a provider timestamp with declared `START`/`END` meaning, OHLCV, trade count, VWAP, session/session date/timezone, completion status, publication/capture time, volume unit, revision information, fixture origin, and sanitized metadata.

Documented aliases are limited to representative shapes:

- Schwab: `datetime`, `open`, `high`, `low`, `close`, `volume`; the fixture must add explicit interval, timestamp meaning, timezone/session, and availability fields.
- IBKR: `date`, `open`, `high`, `low`, `close`, `volume`, optional `barCount`, `average`; the fixture must declare interval and whether `average` is VWAP.
- Yahoo: `timestamp`, `Open`, `High`, `Low`, `Close`, `Volume`; the fixture must declare interval, timestamp meaning, timezone/session, and availability.

Alias collisions with unequal values reject. Ambiguous `1`, `5`, `daily`, and `minute` reject. Supported canonical intervals are fixed `1_MINUTE`, `5_MINUTES`, `15_MINUTES`, `30_MINUTES`, `1_HOUR`, and session-based `1_DAY`. Daily bars are not modeled as fixed 24-hour UTC intervals.

## Boundaries, timezone, DST, and sessions

Canonical boundaries are start-inclusive and end-exclusive. Fixed intervals derive the omitted boundary only when interval identity and provider timestamp meaning are explicit. Daily records require a session date and explicit session-based boundaries; a date-only daily label may be combined only with an explicit fixture timezone and documented local session window.

All instants become UTC. Offset-aware timestamps are portable. Naive full timestamps and time-only values require an IANA timezone or numeric offset. Time-only inputs also require session date. `zoneinfo` round-trip validation rejects nonexistent spring-forward times and ambiguous fall-back times unless a numeric offset disambiguates them. UTC is never silently assigned.

Supported objective source labels are `PREMARKET`, `REGULAR`, `AFTER_HOURS`, `OVERNIGHT`, `EXTENDED`, `CLOSED_SESSION`, and `UNKNOWN`. Phase 1H prefers the supplied label. A small fixture-only session policy may state expected or closed intervals; no comprehensive exchange calendar or hour-only inference is claimed.

## Numeric and lifecycle semantics

Complete, corrected, and cancelled records require valid OHLC. Partial records are accepted only when all required canonical OHLC fields remain available. Objective validation enforces `high >= open`, `high >= close`, `low <= open`, `low <= close`, and `high >= low`. Prices and VWAP are positive exact decimals. Volume and trade count are non-negative integers; negative or fractional counts reject. Missing volume/trade count/VWAP remains null, while zero volume is retained and diagnosed.

Statuses are `PARTIAL`, `COMPLETED`, `CORRECTED`, `CANCELLED`, and `UNKNOWN`. Each status produces an immutable observation. A completion or correction may explicitly supersede a prior provider record; batch normalization links both with parent IDs and a deterministic correlation ID. Missing links are diagnosed. No prior observation is mutated or removed.

Exact duplicate raw records emit once with a deterministic diagnostic. Same provider record ID with changed content is preserved as a conflict. Same symbol, interval, boundaries, asset class, venue scope, and units from different providers is comparable structural evidence; differing values are preserved with a stable conflict and no average or winner. Different boundaries are not treated as a direct value conflict.

## Point-in-time evidence and objective series

`MARKET_BARS` is an independent coverage domain. Eligibility requires source publication/availability, local receipt, and effective time all at or before `as_of`; bar end alone is irrelevant. Partial, completed, and corrected records may coexist in a later bundle. Historical bundles rebuilt from the complete lifecycle remain byte-identical.

Conditional bar ages are interval age, publication age, availability age, capture age, and correction age. Coverage distinguishes present, missing, partial, stale, delayed, unknown freshness, conflicted, and invalid. A bar never becomes bullish, bearish, neutral, or actionable.

`build_bar_series` selects eligible `BAR` observations for one symbol and optional interval/session, groups and orders them by start, then reports immutable observations, latest eligible observation, duplicate/overlap/missing diagnostics, and a stable series hash. Missing intervals are diagnosed only inside an explicit fixed-duration window with an explicit session policy. Closed intervals are distinguished from expected missing intervals and unknown expectation. No interpolation, filling, resampling, aggregation, or calculation occurs.

## Fixtures, replay, CLI, and determinism

Provider fixtures cover the required complete, partial, lifecycle, numeric, timestamp, session, duplicate, conflict, and rejection cases with complete provenance metadata. The `TESTA` lifecycle uses one one-minute interval: partial publication/receipt, completed publication/receipt, and later correction publication/receipt. Mixed replay extends the Phase 1G evidence fixture with bars while retaining all prior domains independently.

`normalize-provider --provider market-bars`, `build-bar-series`, existing `build-evidence`, and `build-evidence-timeline` use local files only and emit canonical machine-readable JSON. Rejection returns nonzero. All identities, diagnostics, relationships, coverage, series ordering, hashes, replay bytes, and bundles derive only from fixture/context/policy data.

Phase 1H adds no HTTP, FTP, WebSocket, provider SDK, credential or `.env` read, database, GUI, order API, wall clock, random ID, NumPy, pandas, indicator library, historical download, live stream, RVOL, technical indicator, momentum/breakout/gap/trend classification, score, rank, recommendation, or trading logic.
