# Batch 05 — IBKR Historical Export: Architecture

The collection utility lives at `tools/ibkr_historical_export/` and is deliberately
**isolated** from the deterministic research runtime in `src/squeeze_core`. The runtime
never imports the tool and never gains a live IBKR read path. Only the session layer
imports `ibapi`.

## Module map

| Module | ibapi? | Responsibility |
|--------|:------:|----------------|
| `cohort.py` | no | Frozen 13-symbol order, case IDs, weekend boundary, the two frozen `HistoricalRequestSpec`s, whole-second `endDateTime` formatting. |
| `policy.py` | no | Localhost host, port probe order (`4002→4001`), client-ID sequence (`27185→27186→27187→27188`), timeouts, pacing/retry constants, `assert_localhost`. |
| `statuses.py` | no | `CollectionStatus`, `ContractStatus`, `HistoricalStatus`, `PreflightStatus`, `REQUEST_TIME_PRECISION_TRUNCATED_TO_SECOND`. |
| `models.py` | no | `ContractCandidate`, `ContractResolution`, `BarRecord`, `ApiDiagnostic`, `HistoricalRequestResult`. Provider numbers carried as strings verbatim. |
| `errors.py` | no | IBKR error-code classification; `is_request_ending`, `is_no_data_empty`, `classify_historical_error`, `is_transient`. |
| `resolution.py` | no | Outcome-blind contract resolution (secType/currency/symbol/conId only). |
| `serialization.py` | no | Deterministic JSONL + CSV, SHA-256/byte-length, canonical JSON. |
| `preflight_bundle.py` | no (imports runtime) | Builds the Batch 04 `IntakeManifest` + `ColumnMappingProfile` with honest UNKNOWN semantics and runs the existing offline preflight. |
| `paths.py` | no | Private Git-ignored output layout under `intake/local-bars/ibkr-batch-05/`. |
| `guard.py` | no | Static source scan proving forbidden order/account methods are absent from the tool. |
| `session.py` | **yes** | The only ibapi module: threaded `EWrapper`/`EClient` with blocking helpers for current-time, contract-details, and historical-bar requests. |
| `collector.py` | no (lazy) | Orchestration: probe → qualify → collect → persist → offline preflight → summary. |
| `cli.py` / `__main__.py` | no (lazy) | `connection-probe`, `qualify-contracts`, `collect-bars`, `verify-private-batch`, `run`. |

## Control flow (`run` / `collect-bars`)

1. `probe_and_connect` opens one localhost connection (port then client-ID fallback),
   records server version and current time.
2. For each frozen symbol in order: `reqContractDetails` → `resolve_contract`.
3. For each *uniquely resolved* contract: two serial historical requests (Request A then
   Request B), one active request at a time, ≥2 s between them.
4. Each response is serialized to JSONL + CSV, hashed, re-read, and re-verified.
5. Each nonempty CSV is passed to the Batch 04 offline preflight; empty windows are
   marked `PREFLIGHT_NOT_APPLICABLE_EMPTY`.
6. A sanitized aggregate summary and private provenance manifests are written.

## Threading

`session.py` runs `EClient.run()` on a daemon thread. Request helpers register a
`threading.Event`, issue the request, and block on the event (or a timeout). The reader
thread fills per-request buffers under a lock; `historicalDataEnd`/`contractDetailsEnd`
and request-ending errors set the event. Disconnect always joins the reader thread.

## Determinism

Cohort, boundary, request parameters, and status vocabulary are frozen constants. JSONL
and CSV bytes are a pure function of the captured `BarRecord`s (fixed column order, fixed
formatting, `\n` newlines, UTF-8). Retrieval timestamps are provenance only and never
enter any deterministic identity. Re-running serialization reproduces identical bytes and
hashes.
