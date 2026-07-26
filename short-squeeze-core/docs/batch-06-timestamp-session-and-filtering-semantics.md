# Batch 06 — Timestamp, Session, and Filtering Semantics

## Timestamp

Resolved separately into three sub-questions:

1. **Representation (RESOLVED)** — Batch 05 requested `formatDate=2`. The installed official
   `ibapi` `reqHistoricalData` docstring (API) states values are "the number of seconds
   since 1/1/1970 GMT". The Batch 05 CSV carries both `timestamp_epoch` and a derived
   `timestamp_utc`; the epoch column is the canonical absolute instant.
2. **Event timezone (RESOLVED)** — epoch seconds are an absolute GMT instant → `event_timezone
   = "UTC"`, unambiguous and independent of the TWS login-screen timezone.
3. **Bar start/end (UNRESOLVED → UNKNOWN)** — Official docs (`historical_bars.html`) state
   only the **daily-bar** rule ("the date of the bar will correspond to the day on which the
   bar closes"). Intraday bar start/end is absent from official docs and from the installed
   API `BarData` contract, so `timestamp_semantics` is `UNKNOWN`. It is **not** inferred from
   bar spacing. Batch 05 declared `START` as an assumption; Batch 06 does not carry that
   assumption forward.

Consequence: `timestamp_semantics = UNKNOWN` triggers `MISSING_TIMESTAMP_SEMANTICS` in the
Batch 03 normalizer, contributing to the honest `PREFLIGHT_REJECTED` result.

## Session policy

Batch 05 requested `useRTH=0`. The installed `ibapi` docstring (API) states this returns
"all data ... even where the market ... was outside its regular trading hours". This
establishes the **requested** session policy only (`BarSession.EXTENDED` eligible). It is
kept strictly separate from:
- **observed** returned coverage (Batch 05: ~2026-07-16T16:00Z → 2026-07-17T23:59Z), and
- **provider filtering** (below).

No claim is made that every extended-hours trade is present or that a complete 24-hour
market session is contained in the artifact.

## Historical-feed filtering (disclosure)

`historical_data.html` (OD) states historical data is "filtered for trade types which occur
away from the NBBO such as combo legs, block trades, and derivative trades", and that
unfiltered real-time daily volume "will generally be larger than the (filtered) historical
volume".

Recorded verbatim in the private overlays as a **provenance/limitation** statement, never as
a rejection: *IBKR historical trade data is provider-filtered and may have lower volume than
an unfiltered feed; it is not complete consolidated-market volume.*

## Weekend-window behavior (observation, not a general rule)

Batch 05 empirically observed that both the Saturday-ended `DETECTION_CONTEXT` request
(endDateTime 20260718) and the Sunday-ended `FROZEN_FORWARD_24H` request (endDateTime
20260719) returned the **same** prior-Friday coverage. This is recorded as an observation
about **these** artifacts (`OBSERVED_REQUEST_WINDOW_COVERAGE_MISMATCH`), not a claim that
IBKR always behaves this way. Critically, the `FROZEN_FORWARD_24H` artifacts remain unusable
as forward-outcome evidence; no Batch 06 semantic resolution changes that.
