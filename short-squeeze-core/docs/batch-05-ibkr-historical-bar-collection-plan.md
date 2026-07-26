# Batch 05 — IBKR Historical-Bar Collection and Offline Preflight (Preregistration)

**Task name:** Phase 3D IBKR Historical-Bar Collection and Offline Preflight Batch 05
**Phase:** 3D controlled acquisition infrastructure. **This is not Phase 3E.**
**Schema:** `1.0.0` (unchanged)
**Branch:** `batch/phase-3d-ibkr-historical-bar-collection-05`
**Parent HEAD:** `437c596b0fa53a0a555053b066c9b1e7363d3205`

This document is committed **before** any IB Gateway socket connection or market-data
request, and before the exporter is implemented. It freezes every decision so the
subsequent collection is outcome-blind and deterministic. Returned bars are **never**
used to select, exclude, reorder, or reinterpret any case.

---

## 1. Cohort and source order (frozen)

Exact source order (never changed by returned data):

```
XNCR PESI SLS ZNTL GPRE SSPC LBGJ TRVI LMNX MGNX BHVN OBE AVTX
```

Corresponding case IDs (source organization only — no association is created):

```
BATCH01_XNCR_20260718  BATCH01_PESI_20260718  BATCH01_SLS_20260718
BATCH01_ZNTL_20260718  BATCH01_GPRE_20260718  BATCH01_SSPC_20260718
BATCH01_LBGJ_20260718  BATCH01_TRVI_20260718  BATCH01_LMNX_20260718
BATCH01_MGNX_20260718  BATCH01_BHVN_20260718  BATCH01_OBE_20260718
BATCH01_AVTX_20260718
```

## 2. Boundary (frozen)

- Frozen detection boundary: `2026-07-18T13:37:55.017661Z`
- Frozen 24-hour forward window end: `2026-07-19T13:37:55.017661Z`
- The boundary falls on a **weekend** (2026-07-18 is a Saturday). Empty exact-window
  results may therefore be correct and must remain empty. The window is never extended
  to obtain bars.

## 3. Official API (verified before this plan)

- Official IBKR TWS API installed from `https://interactivebrokers.github.io/` —
  `TWS API Install 1048.01.msi` (API 10.48, Authenticode signer *Interactive Brokers
  Group, Inc.*, DigiCert), to `C:\TWS API`.
- Python source: `C:\TWS API\source\pythonclient`, package **ibapi 10.48.1**.
- Referenced into the project venv (`.venv`, Python 3.12.13) by a `.pth` file; no IBKR
  source is copied into the repository.
- Hard runtime dependency `protobuf==5.29.5` (declared by ibapi's own `setup.py`)
  installed into the venv with explicit user authorization. `ib_insync`, custom socket
  clients, and unofficial packages are **not** used.

## 4. Allowed vs forbidden IBKR API methods

**Allowed (the only methods the exporter references):**

```
EClient.connect / eConnect      EClient.disconnect
EClient.reqCurrentTime          EClient.reqContractDetails
EClient.reqHistoricalData       EClient.cancelHistoricalData
EClient.run / isConnected / serverVersion
EWrapper callbacks: connectAck, nextValidId, managedAccounts (ignored, never stored),
  error, contractDetails, contractDetailsEnd, historicalData, historicalDataEnd,
  currentTime
```

**Forbidden (statically guarded — must never appear in exporter source):**

```
placeOrder cancelOrder reqOpenOrders reqAllOpenOrders reqAutoOpenOrders
reqPositions reqPositionsMulti reqAccountSummary reqAccountUpdates
reqAccountUpdatesMulti reqExecutions reqCompletedOrders reqPnL reqPnLSingle
reqMarketDataType reqMktData reqRealTimeBars reqScannerSubscription
```

Order/contract objects for trading are never imported or instantiated. `managedAccounts`
account identifiers are never stored or logged.

## 5. Connection policy

- Host: `127.0.0.1` only.
- Port probe order: `4002` then `4001`. The successful port is recorded as *observed
  configuration*, not an account-mode determination. Account/position/execution/order
  APIs are never used to infer mode.
- Client ID: `27185`, fixed fallback sequence `27186 → 27187 → 27188`. Never `0`.
- Timeouts: connection 15 s, contract details 30 s, historical request 60 s.
- Read-only Gateway settings are assumed; the exporter never alters Gateway settings.

## 6. Contract resolution (outcome-blind)

For each frozen symbol issue one `reqContractDetails` with:

```
symbol = frozen symbol   secType = STK   exchange = SMART   currency = USD
```

Preserve every returned candidate and these fields when present: `conId, symbol,
localSymbol, secType, currency, exchange, primaryExchange, tradingClass, longName,
timeZoneId, tradingHours, liquidHours, validExchanges`.

Deterministic candidate filter uses **only**: (1) `secType == STK`; (2) `currency ==
USD`; (3) exact case-insensitive match of the requested symbol against `symbol` or
`localSymbol`; (4) a populated unique `conId`. No prices, outcomes, company names, or
web lookups.

- exactly one candidate → `CONTRACT_RESOLVED` (frozen)
- zero → `CONTRACT_NOT_RESOLVED`
- more than one → `CONTRACT_AMBIGUOUS` (never guessed)

## 7. Historical requests (exactly two per resolved contract)

Serial, one active historical request at a time, in frozen source order.

**Request A — `DETECTION_CONTEXT_PRECEDING_24H`**

```
endDateTime = 20260718 13:37:55 UTC   durationStr = 86400 S   barSizeSetting = 1 min
whatToShow = TRADES   useRTH = 0   formatDate = 2   keepUpToDate = False   chartOptions = []
```

**Request B — `FROZEN_FORWARD_24H`**

```
endDateTime = 20260719 13:37:55 UTC   durationStr = 86400 S   barSizeSetting = 1 min
whatToShow = TRADES   useRTH = 0   formatDate = 2   keepUpToDate = False   chartOptions = []
```

The original boundary carries fractional seconds (`.017661`); the API request uses
whole-second precision. Both timestamps are preserved and the status
`REQUEST_TIME_PRECISION_TRUNCATED_TO_SECOND` is recorded. Requests are never shifted to a
later trading day, never broadened because a window is empty, never substituted with
adjusted or live data.

## 8. Pacing and retries

- ≥ 2 s fixed delay between completed historical requests; no identical request within
  15 s.
- At most one retry for a clearly transient connectivity/farm condition, after ≥ 20 s.
  No retry for missing permissions, unresolved/ambiguous/invalid contracts, unsupported
  history, or empty-but-successful responses. First and retry diagnostics preserved.
- Always disconnect cleanly.

## 9. Preserved bar fields

For every returned bar: `request_id, request_name, requested_symbol, resolved_con_id,
timestamp_epoch, timestamp_utc, open, high, low, close, volume, wap, bar_count`. Values
are used exactly as returned — never rounded, cleaned, or inferred. A successful request
with zero bars is recorded as `SUCCESS_EMPTY` (not an exception, not fabricated zero
bars). Farm-connection notifications are diagnostics, not automatic failures.

## 10. Private output structure (Git-ignored)

Root: `intake/local-bars/ibkr-batch-05/` (covered by `.gitignore` rule
`intake/local-bars/`). Layout:

```
collection-plan.json          connection/probe-result.json
contracts/<SYM>-contract-candidates.json
raw/<SYM>-detection-context.jsonl  raw/<SYM>-detection-context.csv
raw/<SYM>-frozen-forward-24h.jsonl raw/<SYM>-frozen-forward-24h.csv
requests/request-manifest.json     errors/api-diagnostics.jsonl
provenance/artifact-manifest.json  provenance/sha256-manifest.json
preflight/<SYM>/<request-name>/...
collection-summary.json
```

Raw JSONL and CSV are two deterministic representations of the same provider response,
generated after capture. Never committed: raw bars, contract candidate payloads, API
diagnostics with provider data, private manifests, normalized real bars, per-symbol real
preflight reports. No account identifiers anywhere.

## 11. Provenance and integrity

Per request record: provider, interface, host, observed_port, client_id,
gateway_server_version, retrieval start/complete, request parameters, requested symbol,
resolved contract metadata, response status, bar count, first/last returned timestamp,
API error codes, and the SHA-256 + byte length of the exact written JSONL and CSV bytes.
Retrieval timestamps are provenance, never deterministic identity inputs. Files are
hashed exactly as written, re-read and re-verified, and the verification command is run
twice to confirm identical hashes. Raw files are never rewritten after hashing.

## 12. Batch 04 preflight integration (honest semantics)

For each successful **nonempty** CSV, build a private Batch 04 intake bundle from the
exact raw CSV bytes, create an `IntakeManifest` + `ColumnMappingProfile`, and run the
existing `run_preflight_from_bytes`. No case association.

Honest declared semantics for IBKR TWS historical TRADES bars:

```
provider_name                    = Interactive Brokers
provider_product_or_export_name  = TWS API Historical Bars via IB Gateway
artifact_format                  = CSV
bar_interval                     = 1_MINUTE
event_timezone                   = UTC
timestamp_semantics              = START (IBKR documents historical bar time as bar start)
session_coverage                 = EXTENDED (regular + extended as returned with useRTH=0)
data_time_basis                  = HISTORICAL
value_authenticity               = VENDOR_SUPPLIED
intended_use                     = HISTORICAL_EVIDENCE
price_adjustment_semantics       = UNKNOWN
volume_adjustment_semantics      = UNKNOWN
corporate_action_handling        = UNKNOWN
```

**Known limitation, recorded honestly:** IBKR historical TRADES data may be split- and/or
dividend-affected and US-stock historical volume can be reported in shares or lots
depending on a Gateway API setting. None of this is verifiable from the allowed
(non-account) API surface. Declaring `RAW_UNADJUSTED` / `SHARES` / `SPLIT_ADJUSTED` /
`DIVIDEND_ADJUSTED` would be a false assertion, so price/volume/corporate-action
semantics are declared `UNKNOWN`.

**Expected honest preflight outcome:** the Batch 03 normalizer treats `UNKNOWN`
adjustment semantics as `MISSING_ADJUSTMENT_SEMANTICS` (a fatal bundle code), so preflight
returns `NOT_READY_REJECTED`. Per the handoff this is an honest result, not a failure to
be forced to `READY`. Batch 03 semantics are **not** changed to force acceptance. Preflight
statuses map to `PREFLIGHT_READY` / `PREFLIGHT_QUARANTINED` / `PREFLIGHT_REJECTED`; for a
`SUCCESS_EMPTY` request no CSV exists and the status is
`PREFLIGHT_NOT_APPLICABLE_EMPTY` (no fake rows are created).

## 13. Boundaries — no association, no outcomes

No `CaseAssociationMapping` is created or executed. Bars are never fed into Phase 3A,
Phase 3B labeling/publication, or Phase 3C analysis. No reference price, percentage
return, ±25% crossing, substantial-move label, TP/FP/TN/FN, or squeeze classification is
computed. Bars are not manually inspected to summarize price movement. Phase 3E is not
begun.

## 14. Exporter architecture and isolation

A small cohesive **collection tool** lives under `tools/ibkr_historical_export/`,
isolated from the deterministic runtime (`src/squeeze_core` never imports it and never
gains live IBKR reads). Stages: `connection-probe`, `qualify-contracts`, `collect-bars`,
`verify-private-batch`, with a single orchestrating `run` command. The only module that
imports `ibapi` is the connection/session layer; cohort constants, serialization,
hashing, and preflight-bundle construction are ibapi-free and unit-testable without a
live Gateway. Explicit type checks, timeouts, graceful disconnects, and structured error
handling throughout. No GUI.

## 15. Determinism

Cohort order, case IDs, boundary, request parameters, and status vocabulary are frozen
constants. JSONL and CSV serialization is byte-deterministic (fixed column order, fixed
number formatting that echoes provider strings verbatim, `\n` newlines, UTF-8). Re-running
serialization over the same captured bars yields identical bytes and hashes. Retrieval
timestamps are provenance only and never enter any deterministic identity.

## 16. Status taxonomy

```
CONNECTION_SUCCESS CONNECTION_FAILED OFFICIAL_API_CLIENT_MISSING
CONTRACT_RESOLVED CONTRACT_NOT_RESOLVED CONTRACT_AMBIGUOUS
HISTORICAL_REQUEST_SUCCESS SUCCESS_EMPTY HISTORICAL_REQUEST_TIMEOUT
HISTORICAL_PERMISSION_DENIED HISTORICAL_DATA_UNAVAILABLE HISTORICAL_REQUEST_ERROR
PREFLIGHT_READY PREFLIGHT_QUARANTINED PREFLIGHT_REJECTED PREFLIGHT_NOT_APPLICABLE_EMPTY
REQUEST_TIME_PRECISION_TRUNCATED_TO_SECOND
```

Original IBKR numeric error codes and messages are preserved in private diagnostics. The
committed summary carries codes, sanitized high-level messages, counts, and statuses —
never bar values, never account data.

## 17. Tests (synthetic only)

Static/unit coverage added before live execution: no order/account/portfolio/execution
methods referenced (source guard); localhost-only; port fallback `4002→4001`; client-ID
fallback `27185→27186→27187→27188`; frozen source order; exact case IDs and boundary;
exact request parameters; whole-second truncation recorded; serial sequencing; ≥2 s delay
policy; `SUCCESS_EMPTY`; unresolved contract; ambiguous contract; permission error;
timeout; deterministic JSONL/CSV serialization; hash + byte-length verification; no
account identifiers in outputs; private path Git-ignored; no real provider fixtures
committed; no case-association call; no outcome calculation. Synthetic wrapper callbacks
and fixtures only; no real bars replayed in committed tests.

## 18. Commit sequence

```
docs: preregister IBKR historical bar collection batch 05
feat: add read-only IBKR historical export utility
test: add IBKR collection safety and determinism coverage
docs: add IBKR collection operator and provenance guidance
chore: finalize IBKR historical bar collection batch 05
```

Plan committed before the first Gateway connection; code and tests committed before live
collection. No private data committed. No prior history amended or rewritten.

## 19. Completion and stop conditions

Completion follows the handoff Definition of Done. True stop conditions (report without
improvising): checkpoint mismatch; baseline irreproducible; prior canonical artifacts
already modified; official API client unavailable; no local port accepts a connection;
Gateway rejects the API connection; task would require disabling read-only mode,
credentials/account access, a nonofficial client, or web market-data retrieval; a
contract is ambiguous and would require guessing; honest adjustment/volume semantics
cannot be represented (collect and report, do not falsify); a genuine post-commit defect
(report before broadening scope); task would require case association or outcome access;
task would begin Phase 3E. A missing/permission-denied/unavailable/empty result for one
symbol is preserved and is not a batch-wide stop.
```
