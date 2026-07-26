# Batch 06 — Test and Verification Report

## Baseline (Batch 05 checkpoint)

- Branch: `batch/phase-3d-ibkr-historical-bar-collection-05`; HEAD `fe7ba9d0ecfdaaaf84edfef413fa3fecbd2ccf0b`.
- `phase-1-rc1` = `f903d4d144d3f7e9717b1ab8e684da406d7968fb`.
- Baseline suite reproduced: **2197 passed, 1 skipped, 0 failed**.
- Archived parent HEAD `0897562e05d75b812dd284de81dfafdfa1dea916`; nested submodule
  `app/ScreenerProject` `6dbefd1a6b271bfc48106c4aa002f211735551cd` — unchanged.
- Private Batch 05 raw verifier: **26 artifacts, 0 mismatches**.

## New tests

- `tests/acquisition/test_ibkr_semantics.py` — 21 resolver cases: TRADES→SPLIT_ADJUSTED;
  never RAW_UNADJUSTED; never dividend/fully-adjusted; corporate-action→ADJUSTMENTS_APPLIED;
  volume unknown→UNKNOWN and documented→unit; timestamp unknown stays UNKNOWN and
  documented→START/END; UTC only from epoch evidence; useRTH 0/1 mapping; volume-unit
  unresolved recorded; filtered-feed disclosure preserved; non-TRADES and dividend-without-
  split rejected; deterministic output; no OHLCV/network fields; evidence frozen.
- `tests/tools/ibkr_historical_export/test_semantics_overlay.py` — 9 overlay cases:
  detection-context REJECTED with MISSING_ADJUSTMENT + MISSING_TIMESTAMP; resolved price is
  SPLIT_ADJUSTED in the overlay; original provenance preserved; raw bytes never modified;
  forward artifacts excluded from forward use; deterministic overlay bytes; volume-unit
  unresolved recorded; no outcome / case-association in reports.
- `tests/tools/ibkr_historical_export/test_isolation.py` — updated to register
  `semantics_overlay.py`; still asserts the tool imports no ibapi outside `session.py`, no
  forbidden runtime modules, and never references `CaseAssociationMapping`.

## Final suite

- Full suite: **2227 passed, 1 skipped, 0 failed** (2197 baseline + 30 new).
- Determinism: overlay generation run twice → byte-identical outputs; resolver output
  canonical-JSON identical across runs.

## Integrity after changes

- Raw Batch 05 bytes: **26 artifacts, 0 mismatches** (re-verified post-generation).
- Committed Batch 01–05 artifacts: unchanged. `git diff fe7ba9d --name-status` shows only
  additions plus intentional edits to `tools/ibkr_historical_export/cli.py` (new
  `resolve-semantics` subcommand) and `tests/.../test_isolation.py` (module registration).
  No fixture, anchor, or data artifact was modified.
- Archived topology: unchanged (parent `0897562`, submodule `6dbefd1`).
- Schema: remains `1.0.0`; intake contract `phase_3d_local_bar_intake_contract.v1` unchanged;
  no semantic enum values added.

## Safety verification

- No IBKR historical-data API request occurred; no Gateway market-data connection was opened
  (the resolver and overlay generator are pure/offline; the only Gateway artifact read was
  the read-only local config for the volume-unit hierarchy).
- No order/account/credential access; no case association; no outcome/return/threshold work;
  Phase 3E not started.
- Private overlays are under the Git-ignored `intake/local-bars/` root (verified with
  `git check-ignore`); no provider data committed.
