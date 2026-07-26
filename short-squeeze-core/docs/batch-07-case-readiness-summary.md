# Batch 07 — 13-Case Readiness Summary

Per-case operation-specific readiness for the frozen Batch 01 cohort against the Batch 05
`DETECTION_CONTEXT_PRECEDING_24H` bars. Descriptive only — no outcome, score, ranking, or
recommendation. Identifiers below are the real (private-evidence) run
(`report_id = 57aa5c14-8f21-533f-ab3c-03b961b3984d`); the committed golden fixture uses
synthetic manifests and therefore has different hashes/ids by design.

## Shared readiness facts (identical for all 13 cases)

All 13 detection-context artifacts share: requested window = 24 h ending at the frozen
boundary `2026-07-18T13:37:55.017661Z`; 1-minute bars; observed coverage
`2026-07-16T16:00:00Z → 2026-07-17T23:59:00Z`; final-bar latest-possible completion
`2026-07-18T00:00:00Z`; gap to boundary `49,075 s`. Resolved semantics: price
`SPLIT_ADJUSTED` (not dividend-adjusted); volume adjustment `UNKNOWN`; volume unit
`UNRESOLVED`; timestamp START/END `UNKNOWN`; session `useRTH=0` extended; provider-filtered
feed.

Because these facts are identical across the cohort, the per-operation verdicts are
identical for every case:

| dimension | verdict |
|-----------|---------|
| temporal_alignment_readiness | ADMISSIBLE (final bar definitely completed before boundary) |
| price ratio ops (PERCENTAGE_*) | ADMISSIBLE_WITH_CONSTRAINTS |
| price absolute-level ops (ABSOLUTE_*) | BLOCKED_MISSING_SEMANTICS |
| volume ops (MEAN_VOLUME_BASELINE, RELATIVE_VOLUME, VOLUME_Z_SCORE) | BLOCKED_MISSING_SEMANTICS |
| phase3a_request_readiness | PHASE3A_REQUEST_READY |
| blocking_reason_codes | PRICE_ABSOLUTE_LEVEL_CORPORATE_ACTION_UNCONFIRMED, VOLUME_UNIT_UNRESOLVED, VOLUME_CORPORATE_ACTION_UNKNOWN, VOLUME_FILTER_STATIONARITY_UNPROVEN |

Phase 2 metric readiness per case: 4 `ADMISSIBLE_WITH_CONSTRAINTS` (the ratio operations)
and 6 `BLOCKED_MISSING_SEMANTICS` (3 absolute-price + 3 volume), out of 10 operations.

## Per-case table (source order)

| # | symbol | case_id | bars | boundary_id | association_id | request_readiness |
|---|--------|---------|------|-------------|----------------|-------------------|
| 1 | XNCR | BATCH01_XNCR_20260718 | 1164 | 0d811ed0-d30e-574a-b419-9f7240d7d7d9 | accde6eb-3ea5-5fd3-82b9-0d0b605fc880 | PHASE3A_REQUEST_READY |
| 2 | PESI | BATCH01_PESI_20260718 | 1348 | e0597fe3-ca84-5fd5-952c-a375c134d211 | 415c263b-2cd6-54a0-a2be-9b45a65588b6 | PHASE3A_REQUEST_READY |
| 3 | SLS | BATCH01_SLS_20260718 | 1440 | c409fc84-1708-5ba9-b73e-b74cb10c2b44 | 5555072a-968f-561d-8014-18d2809fd25c | PHASE3A_REQUEST_READY |
| 4 | ZNTL | BATCH01_ZNTL_20260718 | 1338 | 70c2d9d9-bfb5-5e96-bd33-1a4a611b4c15 | 9a369bf5-d6f0-5177-87b5-dc0813f5ec43 | PHASE3A_REQUEST_READY |
| 5 | GPRE | BATCH01_GPRE_20260718 | 1195 | ab441789-936f-5940-b1f1-2f8d87739b5f | 4ece38ad-781c-5819-9458-cf9166ee0455 | PHASE3A_REQUEST_READY |
| 6 | SSPC | BATCH01_SSPC_20260718 | 1440 | e11bacdc-3989-5bc4-8da1-9d68565f8309 | d7fa6c6f-1c7c-5fff-98bb-9a08f6ab5148 | PHASE3A_REQUEST_READY |
| 7 | LBGJ | BATCH01_LBGJ_20260718 | 1440 | 43b6e346-8637-5297-a7bd-a4d1a3f46260 | d5fdf9c2-105c-5828-a9c3-c99009125fbc | PHASE3A_REQUEST_READY |
| 8 | TRVI | BATCH01_TRVI_20260718 | 1428 | 8c6c7380-fb11-57f6-98f2-9369437fb129 | 6ba6e80d-88d6-5cad-b029-6dee3dac6c66 | PHASE3A_REQUEST_READY |
| 9 | LMNX | BATCH01_LMNX_20260718 | 1432 | 9a64e349-1d7c-569f-b226-ff174d24cdf8 | 0af64880-f5b9-5bfa-86a3-8ea535aa6606 | PHASE3A_REQUEST_READY |
| 10 | MGNX | BATCH01_MGNX_20260718 | 1333 | 1a8f919b-4c8f-53a4-9d86-33dd567a033e | b86123db-051a-5230-8252-3d3390a33235 | PHASE3A_REQUEST_READY |
| 11 | BHVN | BATCH01_BHVN_20260718 | 1399 | 0c264dc4-aaf3-5066-971e-da6c0974c111 | 5ac3fb34-6a61-5d3c-8f01-def3627855e4 | PHASE3A_REQUEST_READY |
| 12 | OBE | BATCH01_OBE_20260718 | 1394 | b55bcd61-804d-51fc-8300-16787110a36e | 0069895a-15eb-5ea5-b175-ae7df9d72aaf | PHASE3A_REQUEST_READY |
| 13 | AVTX | BATCH01_AVTX_20260718 | 1413 | 2e218cad-77bd-5129-9341-a791b6cb3a16 | 93aaf155-c023-52ac-b4f7-912c2bf6610f | PHASE3A_REQUEST_READY |

Bar counts vary with per-symbol liquidity/coverage; they do not change any admissibility
verdict. Boundary ids are recomputed deterministically from frozen inputs
(`case_id`, `symbol`, `ORIGINAL_PLATFORM_SURFACED_TIMESTAMP`) and match the Batch 01
boundary freeze without reading or mutating that registry.

## What "PHASE3A_REQUEST_READY" means here (narrow)

The Phase 3A `RuleEvaluationRequest` contract defaults every evidence-input tuple to empty
and its `RuleOutcome` vocabulary includes `INSUFFICIENT_DATA`/`UNKNOWN`. A request built
from frozen identity alone (symbol, `as_of` = boundary, policy version, the 25 enabled
rule ids, `asset_class=EQUITY`) is valid **without fabricating any evidence field**;
absent-domain rules would legitimately resolve to `INSUFFICIENT_DATA`/`UNKNOWN`.

READY therefore means *a non-fabricated, schema-valid request skeleton is constructible*.
It does **not** assert that the Batch 05 bars can be admitted as request inputs for the
momentum market-bar rules — that admission is governed per-operation (2 availability rules
ADMISSIBLE, 1 percentage-change ADMISSIBLE_WITH_CONSTRAINTS, PRICE_RANGE and
RELATIVE_VOLUME_MINIMUM BLOCKED) and, where admissible, is deferred to a future batch
because populating those inputs requires reading OHLCV and passing intake — both outside
Batch 07 scope. Batch 07 records the determination and never instantiates or evaluates a
request.
