# Batch 06 — Official IBKR Historical-Data Semantics Evidence

Access date for all web sources: **2026-07-25**. Evidence classes are kept strictly
separate: an **official documented fact** (OD), the **installed API contract** (API),
a **local Batch 05 observation** (L5), a **local Gateway configuration observation**
(LGC), and a **project inference** (INF) are never blurred.

## Source table

| # | Source (canonical URL / path) | Section | Class | Rule (paraphrase) | Supports |
|---|---|---|---|---|---|
| 1 | https://interactivebrokers.github.io/tws-api/historical_bars.html | Historical Data Types | OD | "TRADES data is adjusted for splits, but not dividends." | `price_adjustment_semantics`, `corporate_action_handling` |
| 2 | https://interactivebrokers.github.io/tws-api/historical_bars.html | Historical Data Types | OD | "ADJUSTED_LAST data is adjusted for splits and dividends." (contrast; not the value requested) | price semantics contrast |
| 3 | https://interactivebrokers.github.io/tws-api/historical_data.html | Historical Market Data | OD | "Historical data at IB is filtered for trade types which occur away from the NBBO such as combo legs, block trades, and derivative trades"; unfiltered real-time daily volume "will generally be larger than the (filtered) historical volume." | filtered-feed disclosure |
| 4 | https://interactivebrokers.github.io/tws-api/market_data.html | Streaming Market Data | OD | US-stock size quotes were previously in round lots (of 100 shares); effective TWS 985+ displayed in shares, with a compatibility option. (Concerns market-data size, not historical bar volume unit directly.) | volume-unit context |
| 5 | C:/TWS API/source/pythonclient/ibapi/client.py :: `reqHistoricalData` | `formatDate` docstring | API | "formatDate=2 — dates are returned as a long integer specifying the number of seconds since 1/1/1970 GMT." | timestamp representation, `event_timezone` |
| 6 | C:/TWS API/source/pythonclient/ibapi/client.py :: `reqHistoricalData` | `useRTH` docstring | API | "useRTH=0 — all data is returned even where the market in question was outside its regular trading hours." | `session_coverage` (requested) |
| 7 | https://interactivebrokers.github.io/tws-api/historical_bars.html | Historical Bar Data | OD | Only the daily-bar rule is stated ("the date of the bar will correspond to the day on which the bar closes"); intraday bar start/end is **absent**. | `timestamp_semantics` stays UNKNOWN |

## Field-by-field conclusions

- **Price adjustment (RESOLVED)** — Source 1 (OD) establishes that `whatToShow=TRADES`
  is split-adjusted and not dividend-adjusted → existing enum
  `PriceAdjustmentSemantics.SPLIT_ADJUSTED`. TRADES is therefore **never**
  `RAW_UNADJUSTED` and **never** `SPLIT_AND_DIVIDEND_ADJUSTED`. No schema change.

- **Corporate-action handling (RESOLVED)** — Source 1 (OD): a split adjustment is
  applied → `CorporateActionHandling.ADJUSTMENTS_APPLIED`. Consistent with a
  non-raw price (no `CONTRADICTORY_ADJUSTMENT_SEMANTICS`).

- **Volume corporate-action adjustment (UNRESOLVED → UNKNOWN)** — Official docs state
  split adjustment for TRADES **price** only. There is no official statement isolating
  **volume** corporate-action treatment. Per project policy, volume adjustment is
  **not** inferred from price adjustment → `VolumeAdjustmentSemantics.UNKNOWN` (INF
  that the absence of OD leaves it unknown; not an OD claim either way).

- **Timestamp representation / event timezone (RESOLVED)** — Source 5 (API): `formatDate=2`
  returns epoch seconds since 1/1/1970 GMT — an absolute instant → `event_timezone = "UTC"`.

- **Bar start/end semantics (UNRESOLVED → UNKNOWN)** — Source 7 (OD): only the daily-bar
  close-date rule is documented; intraday start/end is absent, and the installed API
  `BarData.date` field carries no boundary contract → `timestamp_semantics = UNKNOWN`.
  Batch 05's `START` was an unverified assumption and is **not** carried forward.

- **Session policy (RESOLVED, request-only)** — Source 6 (API): `useRTH=0` means
  extended-hours data is eligible → requested `BarSession.EXTENDED`. This is the
  **requested** policy, kept separate from observed coverage and provider filtering.

- **Filtered feed (DISCLOSURE)** — Source 3 (OD): IBKR historical trade data is
  provider-filtered (trades away from the NBBO excluded) and generally shows lower
  volume than an unfiltered feed. Recorded as a limitation, never as complete
  consolidated volume, and never converted into a rejection.

## What official evidence does NOT establish

- Whether historical **volume** is split-adjusted (silent).
- Whether an intraday bar timestamp marks the **start or end** of its interval (silent).
- The **volume unit** (shares vs round lots) of the already-collected Batch 05 bars —
  see `batch-06-volume-unit-resolution.md`.

These remain honestly unresolved and are never fabricated to obtain a READY preflight.
