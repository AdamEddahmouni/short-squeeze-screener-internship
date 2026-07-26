# Claude Fresh-Session Handoff — Batch 06

> This is a real, complete handoff. **Do not start Batch 06 in the Batch 05 session.**
> Batch 06 begins only in a new session, after the operator authorizes it.

## Context carried from Batch 05

Batch 05 installed the official IBKR TWS API (`ibapi` 10.48.1, referenced into the venv;
`protobuf==5.29.5` pinned), built a read-only collection tool
(`tools/ibkr_historical_export/`), and collected historical bars for the frozen 13-symbol
cohort from the local IB Gateway into the Git-ignored `intake/local-bars/ibkr-batch-05/`.

Empirical results that shape Batch 06:

- **All 13 contracts resolved** (unique conIds captured; primary exchanges NASDAQ except
  SSPC=BATS, BHVN=NYSE, OBE=AMEX).
- **All 26 historical requests returned data** (`HISTORICAL_REQUEST_SUCCESS`), but for every
  symbol **both** requests returned the *same* most-recent-available session
  (`2026-07-16T16:00Z → 2026-07-17T23:59Z`). The frozen boundary `2026-07-18` is a
  **Saturday**, so the `FROZEN_FORWARD_24H` window has no native trading and IBKR
  substituted the last available (Friday) session. The forward artifacts therefore do
  **not** represent forward-outcome data.
- **All 26 preflights are `PREFLIGHT_REJECTED`** with `MISSING_ADJUSTMENT_SEMANTICS`, because
  IBKR TRADES adjustment status and volume-unit are declared `UNKNOWN` (they are not
  verifiable from the allowed non-account API surface).

## Repository checkpoint (expected at Batch 06 start)

```
Branch (Batch 05 work): batch/phase-3d-ibkr-historical-bar-collection-05
Parent of Batch 05:     437c596b0fa53a0a555053b066c9b1e7363d3205
Baseline:               2,196 passed, 1 skipped, 0 failed (2,126 + 70 Batch 05 tests)
phase-1-rc1:            f903d4d144d3f7e9717b1ab8e684da406d7968fb
Archived parent:        0897562e05d75b812dd284de81dfafdfa1dea916
Archived submodule:     6dbefd1a6b271bfc48106c4aa002f211735551cd
```

Verify the checkpoint, reproduce the baseline (fresh `--basetemp`), and confirm Batch 01–05
fixtures and archived evidence are unchanged before doing anything.

## Recommended next task (exactly one)

**Offline: resolve and honestly declare IBKR historical TRADES adjustment and volume-unit
semantics, then re-preflight the already-collected detection-context CSVs without any new
IBKR fetch.**

Rationale: the only thing standing between the collected detection-context bars and a
non-rejected preflight is the honest `UNKNOWN` adjustment/volume declaration. Batch 06
should, using **official IBKR API documentation only** (no account calls, no new market-data
requests, no web scraping of data), determine whether `whatToShow=TRADES` historical bars
from this Gateway configuration are raw/split/dividend-affected and whether US-stock volume
is shares or lots. If — and only if — the semantics can be established **truthfully**, extend
the Batch 03 semantics vocabulary honestly (or record that they still cannot be represented)
and re-run the offline preflight against the existing private CSV bytes. If the semantics
remain genuinely unverifiable, that is an honest terminal result and the CSVs stay
`REJECTED`.

Scope guards for Batch 06:

- Do **not** compute outcomes, reference prices, returns, ±25% crossings, or squeeze labels.
- Do **not** create a `CaseAssociationMapping` or associate bars with real cases.
- Do **not** treat the `FROZEN_FORWARD_24H` artifacts as forward-outcome evidence — they are
  pre-boundary Friday data.
- Do **not** re-fetch or extend any window; work only from the bytes already collected.
- Do **not** begin Phase 3E.
- Do **not** weaken Batch 03 semantics merely to force acceptance.

## Alternative task (only if the operator prefers)

If the operator instead wants forward-outcome coverage, that is a **research-design decision
for the operator**, not an implementation task: the frozen forward window is a genuine
non-trading weekend, so no lawful non-account source provides forward bars for the exact
frozen window. Surface this to the operator and stop; do not extend windows to manufacture
data.
