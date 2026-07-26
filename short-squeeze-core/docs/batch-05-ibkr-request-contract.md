# Batch 05 — IBKR Request Contract

## Contract-details request (per frozen symbol)

```
symbol   = <frozen symbol>
secType  = STK
exchange = SMART
currency = USD
```

Preserved candidate fields: `conId, symbol, localSymbol, secType, currency, exchange,
primaryExchange, tradingClass, longName, timeZoneId, tradingHours, liquidHours,
validExchanges`.

Deterministic filter (structural only): `secType == STK`, `currency == USD`, requested
symbol equals `symbol` or `localSymbol` (case-insensitive), populated unique `conId`.
Result: `CONTRACT_RESOLVED` (one unique conId) / `CONTRACT_NOT_RESOLVED` (zero) /
`CONTRACT_AMBIGUOUS` (more than one). Ambiguity is never guessed.

## Historical requests (two per resolved contract)

Request A — `DETECTION_CONTEXT_PRECEDING_24H`:

```
endDateTime     = 20260718 13:37:55 UTC
durationStr     = 86400 S
barSizeSetting  = 1 min
whatToShow      = TRADES
useRTH          = 0
formatDate      = 2
keepUpToDate    = False
chartOptions    = []
```

Request B — `FROZEN_FORWARD_24H`:

```
endDateTime     = 20260719 13:37:55 UTC
durationStr     = 86400 S
barSizeSetting  = 1 min
whatToShow      = TRADES
useRTH          = 0
formatDate      = 2
keepUpToDate    = False
chartOptions    = []
```

The frozen boundary `2026-07-18T13:37:55.017661Z` carries fractional seconds; the API
`endDateTime` uses whole-second precision, so `REQUEST_TIME_PRECISION_TRUNCATED_TO_SECOND`
is recorded on every request. Requests are never shifted to a later trading day, never
broadened because a window is empty, and never substituted with adjusted or live data.
The boundary is on a weekend, so Request B (fully within the weekend) legitimately returns
`SUCCESS_EMPTY` for most or all symbols.

## Captured bar fields (`formatDate = 2`)

`request_id, request_name, requested_symbol, resolved_con_id, timestamp_epoch,
timestamp_utc, open, high, low, close, volume, wap, bar_count`. Values are echoed exactly
as returned — never rounded, cleaned, or inferred. Missing `volume`/`wap` (`UNSET_DECIMAL`)
become explicit nulls. A successful request with zero bars is `SUCCESS_EMPTY`, never a
fabricated zero-bar row.

## Pacing and retry

One active historical request at a time, in frozen source order; ≥2 s between completed
requests; no identical request within 15 s. At most one retry for a clearly transient
farm/connectivity condition after ≥20 s. No retry for missing permissions, unresolved or
ambiguous contracts, unsupported history, or an empty-but-successful response. Timeouts:
connection 15 s, contract details 30 s, historical 60 s. The connection is always
disconnected cleanly.

## Status classification

| Situation | Status |
|-----------|--------|
| Bars returned, request completed | `HISTORICAL_REQUEST_SUCCESS` |
| Completed with zero bars, or code 162 "no data" | `SUCCESS_EMPTY` |
| Missing market-data permission (354, 10167/8, 10187, 10197, 10225) | `HISTORICAL_PERMISSION_DENIED` |
| Series unavailable / bad query (162, 165/6, 200, 320-322, 366, 430) | `HISTORICAL_DATA_UNAVAILABLE` |
| No completion within timeout | `HISTORICAL_REQUEST_TIMEOUT` |
| Any other ending error | `HISTORICAL_REQUEST_ERROR` |

Farm/connectivity notifications (2100–2199, 1100–1102) are diagnostics, not failures.
