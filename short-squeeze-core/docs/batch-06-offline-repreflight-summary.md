# Batch 06 — Offline Re-Preflight Summary

Re-ran the **existing** Batch 04 offline preflight against the **already-collected** Batch 05
`DETECTION_CONTEXT_PRECEDING_24H` CSV bytes, using the Batch 06 resolved semantics. No new
API request, no Gateway connection, no window change, no case association, no outcome work.

## Resolved semantics applied

| Field | Value | Status |
|---|---|---|
| `price_adjustment_semantics` | `SPLIT_ADJUSTED` | resolved (official) |
| `corporate_action_handling` | `ADJUSTMENTS_APPLIED` | resolved (official) |
| `event_timezone` | `UTC` | resolved (installed API: formatDate=2) |
| `session_coverage` (requested) | `EXTENDED` | resolved (installed API: useRTH=0) |
| `volume_adjustment_semantics` | `UNKNOWN` | unresolved (docs silent) |
| `timestamp_semantics` | `UNKNOWN` | unresolved (docs silent, intraday) |
| volume unit (provenance only) | `HISTORICAL_VOLUME_UNIT_UNRESOLVED` | unresolved |

## Per-symbol result (13 detection-context artifacts)

| Symbol | Preflight status | Reason codes |
|---|---|---|
| XNCR | PREFLIGHT_REJECTED | MISSING_ADJUSTMENT_SEMANTICS, MISSING_TIMESTAMP_SEMANTICS |
| PESI | PREFLIGHT_REJECTED | MISSING_ADJUSTMENT_SEMANTICS, MISSING_TIMESTAMP_SEMANTICS |
| SLS  | PREFLIGHT_REJECTED | MISSING_ADJUSTMENT_SEMANTICS, MISSING_TIMESTAMP_SEMANTICS |
| ZNTL | PREFLIGHT_REJECTED | MISSING_ADJUSTMENT_SEMANTICS, MISSING_TIMESTAMP_SEMANTICS |
| GPRE | PREFLIGHT_REJECTED | MISSING_ADJUSTMENT_SEMANTICS, MISSING_TIMESTAMP_SEMANTICS |
| SSPC | PREFLIGHT_REJECTED | MISSING_ADJUSTMENT_SEMANTICS, MISSING_TIMESTAMP_SEMANTICS |
| LBGJ | PREFLIGHT_REJECTED | MISSING_ADJUSTMENT_SEMANTICS, MISSING_TIMESTAMP_SEMANTICS |
| TRVI | PREFLIGHT_REJECTED | MISSING_ADJUSTMENT_SEMANTICS, MISSING_TIMESTAMP_SEMANTICS |
| LMNX | PREFLIGHT_REJECTED | MISSING_ADJUSTMENT_SEMANTICS, MISSING_TIMESTAMP_SEMANTICS |
| MGNX | PREFLIGHT_REJECTED | MISSING_ADJUSTMENT_SEMANTICS, MISSING_TIMESTAMP_SEMANTICS |
| BHVN | PREFLIGHT_REJECTED | MISSING_ADJUSTMENT_SEMANTICS, MISSING_TIMESTAMP_SEMANTICS |
| OBE  | PREFLIGHT_REJECTED | MISSING_ADJUSTMENT_SEMANTICS, MISSING_TIMESTAMP_SEMANTICS |
| AVTX | PREFLIGHT_REJECTED | MISSING_ADJUSTMENT_SEMANTICS, MISSING_TIMESTAMP_SEMANTICS |

**Result: 13/13 `PREFLIGHT_REJECTED`.** This is the honest outcome and is preserved as-is.

## Interpretation

Batch 05 rejected on **three** UNKNOWN adjustment fields plus an assumed timestamp. Batch 06
resolves price adjustment and corporate-action handling from official evidence, reducing the
adjustment blockers to a single one (volume), and honestly reclassifies the timestamp from an
unverified `START` to `UNKNOWN`. The artifacts remain rejected because two fields cannot be
established from official evidence. No validator or schema was changed to force acceptance
(handoff §20). Readiness would require official documentation of (a) volume corporate-action
treatment and (b) intraday bar start/end — neither exists today.

## Forward-artifact exclusion

The 13 `FROZEN_FORWARD_24H` artifacts were **not** re-preflighted as forward evidence. Their
status remains `REQUEST_SUCCEEDED_BUT_RETURNED_COVERAGE_DOES_NOT_REPRESENT_FROZEN_FORWARD_WINDOW`.
They are retained privately for provenance only.

## Artifacts (private, Git-ignored)

`intake/local-bars/ibkr-batch-05/semantics/batch-06/`:
`ibkr-official-semantics-evidence.json`, `local-volume-setting-evidence.json`,
`semantic-resolution-manifest.json`, `<symbol>-detection-context-intake-manifest.json` (×13),
`<symbol>-detection-context-preflight-report.json` (×13), `batch-06-private-summary.json`.
Regenerate offline with: `python -m tools.ibkr_historical_export resolve-semantics`.
