# Batch 06 — Completion Report

**Phase 3D IBKR Historical-Bar Semantics Resolution and Offline Re-Preflight (Batch 06)**

## Decision / status

COMPLETE. IBKR historical `TRADES` semantics were resolved from official evidence to the
extent the official record supports, the two genuinely undocumented fields were preserved
honestly as `UNKNOWN`, and the existing Batch 04 offline preflight was re-run against the 13
already-collected `DETECTION_CONTEXT_PRECEDING_24H` CSVs. All 13 remain honestly
`PREFLIGHT_REJECTED`. No new market data was requested; Phase 3E was not started.

## Checkpoint

- Starting branch/HEAD: `batch/phase-3d-ibkr-historical-bar-collection-05` /
  `fe7ba9d0ecfdaaaf84edfef413fa3fecbd2ccf0b`.
- Batch 06 branch: `batch/phase-3d-ibkr-semantics-resolution-06`.
- Baseline reproduced: 2197 passed, 1 skipped. Final: 2227 passed, 1 skipped.

## Commits

| Hash | Subject |
|---|---|
| `07a97330caa1591757c05086b664db8b8bc53384` | docs: preregister IBKR semantics resolution batch 06 |
| `91b862bf1572538ce4570dce8079d49182537c52` | feat: add deterministic IBKR historical semantics resolver |
| `d65c58a06cec1269e31529f96c37fe7888eca4d2` | test: add IBKR semantics and re-preflight coverage |
| `c9300caf5d565ee7950d7ee8521d04a2cf607b69` | docs: record official IBKR historical-data semantics evidence |
| (this commit) | docs: report batch 06 completion and add batch 07 handoff |

## Resolved semantics

| Field | Value | Disposition | Basis |
|---|---|---|---|
| `price_adjustment_semantics` | `SPLIT_ADJUSTED` | RESOLVED | official: TRADES split-adjusted, not dividend |
| `corporate_action_handling` | `ADJUSTMENTS_APPLIED` | RESOLVED | official: splits applied |
| `event_timezone` | `UTC` | RESOLVED | installed ibapi: formatDate=2 = seconds since 1/1/1970 GMT |
| `session_coverage` (requested) | `EXTENDED` | RESOLVED | installed ibapi: useRTH=0 |
| `volume_adjustment_semantics` | `UNKNOWN` | UNRESOLVED | official docs silent on volume corporate-action |
| `timestamp_semantics` | `UNKNOWN` | UNRESOLVED | official docs silent on intraday bar start/end |
| volume unit (provenance only) | `HISTORICAL_VOLUME_UNIT_UNRESOLVED` | UNRESOLVED | not captured; obfuscated config; UI declined |

Price adjustment is representable by the existing enum with **no** schema change (schema stays
`1.0.0`). No enum value was added.

## Re-preflight (13 detection-context artifacts)

All 13 (XNCR, PESI, SLS, ZNTL, GPRE, SSPC, LBGJ, TRVI, LMNX, MGNX, BHVN, OBE, AVTX):
`PREFLIGHT_REJECTED` with `MISSING_ADJUSTMENT_SEMANTICS` (volume) + `MISSING_TIMESTAMP_SEMANTICS`.
Batch 05's three-field adjustment block is reduced to one adjustment field; the timestamp is
honestly reclassified from an assumed `START` to `UNKNOWN`. No validator/schema changed to
force acceptance.

## Forward-artifact exclusion

The 13 `FROZEN_FORWARD_24H` artifacts were not re-preflighted as forward evidence; status
remains `REQUEST_SUCCEEDED_BUT_RETURNED_COVERAGE_DOES_NOT_REPRESENT_FROZEN_FORWARD_WINDOW`.

## Integrity

- Private Batch 05 raw: 26 artifacts, 0 mismatches (before and after).
- Committed Batch 01–05 artifacts: unchanged.
- Archived topology: parent `0897562`, submodule `6dbefd1` — unchanged.
- Overlay/resolver determinism: byte-identical across repeated runs.

## Confirmations

No new fetch • no Gateway market-data connection • no window shift/extend/replace • no account
or credential access • no case association • no outcome/return/threshold computation • no Phase
3A/3B/3C expansion • Phase 3E not started.

## Deviations

None material. Two intentional edits to pre-existing files: `cli.py` (offline
`resolve-semantics` subcommand) and `test_isolation.py` (register the new module). The
timestamp field is now `UNKNOWN` rather than Batch 05's assumed `START` — a deliberate honesty
correction, not a regression.

## Limitations

- Two fields cannot be established from official evidence today (volume corporate-action;
  intraday bar start/end), so the detection-context artifacts cannot reach `READY`.
- The volume unit in effect during Batch 05 collection is unrecoverable from safe read-only
  evidence.
- The `FROZEN_FORWARD_24H` artifacts remain unusable as forward-outcome evidence.

## Phase 3E stop statement

Phase 3E is NOT started. Batch 06 ends at semantic readiness analysis and offline re-preflight
only. No case association, outcome capture, return calculation, threshold labeling, or
predictive-validation work was performed or begun.
