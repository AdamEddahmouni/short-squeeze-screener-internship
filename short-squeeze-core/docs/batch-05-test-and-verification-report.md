# Batch 05 — Test and Verification Report

## Test suite

- **Baseline (pre-change):** 2,126 passed, 1 skipped, 0 failed.
- **Batch 05 added:** 71 synthetic tests under `tests/tools/ibkr_historical_export/`
  (no socket, no ibapi live calls, no real bars replayed).
- **Final:** 2,197 passed, 1 skipped, 0 failed (2,126 + 71).

The exporter tests are packaged (`tests/tools/ibkr_historical_export/` has `__init__.py`)
to avoid basename collisions with existing top-level tests (e.g. `test_serialization.py`);
`tests/tools/conftest.py` puts the repo root on `sys.path` so `import tools.*` resolves.

### Coverage highlights

- Forbidden-method static guard (order/account/portfolio absent from tool source) +
  allowed/forbidden disjointness + an injected-violation detection test.
- Localhost-only; port fallback `4002→4001`; client-ID fallback `27185→27186→27187→27188`;
  precheck-skips-filtered-port.
- Frozen source order, case IDs, boundary, exact request parameters, whole-second
  truncation.
- Outcome-blind contract resolution (resolved / not-resolved / ambiguous / conId dedupe /
  localSymbol match / non-USD / non-STK / zero-conId).
- Deterministic JSONL/CSV serialization, hashing, empty sets, None→empty, no account
  identifiers.
- IBKR error classification (permission / unavailable / timeout / 162-no-data-empty /
  transient).
- Synthetic ibapi callbacks: contract + bar conversion, UNSET decimals → null,
  request-ending vs farm notifications, `managedAccounts` never stored, `nextValidId`.
- Honest preflight → `PREFLIGHT_REJECTED` (`MISSING_ADJUSTMENT_SEMANTICS`).
- End-to-end collector run over a fake session: artifacts, hashes, determinism,
  `SUCCESS_EMPTY`, preflight N/A, no account identifiers.
- Runtime↔tool isolation (runtime never imports ibapi or the tool; tool imports ibapi only
  in `session.py`; tool references no case-association/outcome path).

### Note on a transient full-run flake

One intermediate full-suite run reported 3 transient failures in
`tests/metrics/test_normalized_cli.py` (a pre-existing, subprocess-based CLI test that spawns
`python -m squeeze_core`). The same file passes 11/11 in isolation, passes when run together
with the entire `tests/tools/` package, and passed in both the pristine baseline and the
Batch-05 full run. The failures are load-related subprocess flakiness in a pre-existing test,
unrelated to Batch 05 code (which adds no subprocess and does not touch `squeeze_core` or
`metrics`). The authoritative re-run is clean.

## Determinism and integrity verification

- **Private hash verification run twice** (`verify-private-batch`): 26 artifacts, 0
  mismatches, identical hashes both runs.
- **Serializer determinism:** re-serializing the same captured bars yields byte-identical
  JSONL/CSV (unit-tested); on-disk artifacts re-hash to their recorded values.
- **Batch 01–04 fixtures unchanged:** aggregate digest `b0e4a1ec…` identical before/after
  (99 files).
- **Committed acquisition source unchanged** (per-file digest comparison).
- **Archived topology unchanged:** parent `0897562e05d75b812dd284de81dfafdfa1dea916`,
  submodule `app/ScreenerProject` `6dbefd1a6b271bfc48106c4aa002f211735551cd`.

## Static safety checks

- Forbidden-method scan over `tools/`: **CLEAN** (no order/account/portfolio methods outside
  the guard module that names them for documentation).
- Account-identifier / credential scan: no real account IDs anywhere; the only `DU…` strings
  are synthetic test values asserting the tool does **not** store them.
- No outcome / case-association execution path in `tools/`
  (`CaseAssociationMapping`, return/threshold/squeeze functions absent).
