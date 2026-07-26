# Batch 07 — Completion Report

**Task:** Phase 3D Operation-Specific Evidence Admissibility and Phase 3A Readiness Audit.
**Decision/status:** COMPLETE. Conservative BLOCKED results retained where evidence or
semantics are genuinely insufficient. Phase 3E not started.

## Checkpoint

- Starting branch: `batch/phase-3d-ibkr-semantics-resolution-06`
- Starting HEAD: `ae1aa4e4cc82cc8aea5b49a58e2d6d3ed15a1e17` (Batch 06)
- New branch: `batch/phase-3d-operation-specific-readiness-07`
- Baseline reproduced: 2,227 passed / 1 skipped / 0 failed (2,228 collected)
- Final: 2,256 passed / 1 skipped / 0 failed (2,257 collected); +29 tests

## Commits (this batch)

1. `4b02053` docs: preregister operation-specific readiness batch 07
2. `62a73e6` feat: add operation-specific evidence admissibility and phase 3a readiness
3. `26039f1` test: add operation readiness and temporal uncertainty coverage
4. `eae33d5` docs: report batch 07 evidence-readiness findings
5. (finalizing) chore: finalize operation-specific readiness batch 07 — this report +
   the Batch 08 handoff. The exact final HEAD is the tip of the branch; verify with
   `git rev-parse HEAD` (reported in the session summary).

## What was determined

**Existing readiness architecture (audited first).** The project already has a Phase 2D
*operation-specific structural readiness* layer (`squeeze_core.readiness`:
`OperationRequirementPolicy`, `StructuralState`, `InputSufficiencyResult`, and 17
declarative operation policies). It models domain/metric presence and history
sufficiency but **not** the IBKR semantic fields (price/volume adjustment, volume unit,
timestamp START/END, provider filtering). Batch 07 composes with that philosophy and adds
the missing *semantic-admissibility* dimension as a new, narrow, additive package —
without a parallel generic "confidence" framework.

**Operation-specific admissibility policy.** A closed status vocabulary
(`ADMISSIBLE`, `ADMISSIBLE_WITH_CONSTRAINTS`, `BLOCKED_MISSING_SEMANTICS`,
`BLOCKED_MISSING_EVIDENCE`, `BLOCKED_ALIGNMENT`, `BLOCKED_CONFLICT`, `NOT_APPLICABLE`).
`UNKNOWN` never collapses to FAIL; missing evidence is never zero; no numeric confidence.

**Timestamp uncertainty.** Bidirectional 1-minute envelope; a bar is "definitely
completed before the boundary" only when both START and END interpretations end at/before
it. For this cohort the final bar (`2026-07-17T23:59:00Z`) is definitely completed before
the Saturday boundary (`2026-07-18T13:37:55.017661Z`); no straddle; 49,075 s weekend gap.

**Price-operation conclusion.** Split-adjusted price ratios (`PERCENTAGE_*`) are
`ADMISSIBLE_WITH_CONSTRAINTS` (split-invariant, dividend not applied). Absolute price
levels (`ABSOLUTE_*`, `PRICE_RANGE`) are `BLOCKED_MISSING_SEMANTICS` — not invariant to an
unconfirmed corporate action over the boundary→retrieval gap.

**Volume-operation conclusion.** All volume operations are `BLOCKED_MISSING_SEMANTICS`:
volume unit UNRESOLVED, volume corporate-action UNKNOWN, and provider-filter fraction not
shown stationary; the ratio-invariance shortcut is insufficient and no magnitude/lot
inference is permitted.

**Temporal-alignment conclusion.** `ADMISSIBLE` for all 13 cases.

**Phase 2 metric readiness.** Per case: 4 ratio operations `ADMISSIBLE_WITH_CONSTRAINTS`,
6 (3 absolute-price + 3 volume) `BLOCKED_MISSING_SEMANTICS`, of 10 total.

**Phase 3A 25-rule dependency readiness.** 2 `ADMISSIBLE`, 1
`ADMISSIBLE_WITH_CONSTRAINTS`, 2 `BLOCKED_MISSING_SEMANTICS`, 13 `BLOCKED_MISSING_EVIDENCE`,
7 `NOT_APPLICABLE`. No PASS/FAIL emitted; no rule evaluated.

**Phase 3A request readiness.** All 13 cases `PHASE3A_REQUEST_READY` — a non-fabricated,
schema-valid request skeleton is constructible from frozen identity (the contract permits
empty evidence inputs and INSUFFICIENT_DATA/UNKNOWN outcomes). No request was instantiated
or executed; populating market-bar evidence for the admissible momentum rules is a future
step (requires OHLCV reads + intake, out of scope).

## Guarantees held

- Global Batch 04 preflight verdict unchanged: `PREFLIGHT_REJECTED` (no validator
  modified; echoed, never mutated).
- Batch 05 private raw hashes: 26 artifacts, 0 mismatches.
- Forward (`FROZEN_FORWARD_24H`) artifacts referenced by filename/sha/byte-length only;
  OHLCV never opened (hard guard + tests).
- No outcome access, no forward-bar reads, no new market data, no network, no `ibapi`.
- Prior committed bytes unchanged (all changes are additions since `ae1aa4e`).
- Archived topology unchanged (parent `0897562e…`, submodule `6dbefd1a…`).
- Schema remains `1.0.0`; canonical outputs regenerate byte-identically.
- Real-evidence report kept private (gitignored); committed golden uses synthetic data.

## Deviations / limitations

- The committed golden fixture uses synthetic manifests (real Batch 05 provenance is
  licensed/private); the real report lives under the gitignored intake tree.
- The report-level `frozen_boundary_id` is a shared-instant descriptor because each case's
  boundary id binds its own case attempt id (all recomputed deterministically).
- Admissibility is intentionally conservative; several BLOCKED verdicts could become
  admissible only if specific evidence (corporate-action confirmation; volume
  unit/corporate-action/filter-stationarity) is lawfully obtained in a future batch.

## Phase 3E

Phase 3E was **not** started. No rule evaluation, no Phase 3A/3B result, no scoring,
ranking, backtest, P&L, or trading action occurred.

## Recommended next task (single)

See `docs/batch-08-fresh-session-handoff.md`. Because Phase 3A request skeletons are
honestly constructible for all 13 cases and there is genuinely operation-specifically
admissible detection-context evidence (the two market-bar availability rules and the
split-invariant `PERCENTAGE_CHANGE_MINIMUM`), the recommended next task is to **construct
and freeze Phase 3A requests and results for the 13 cases using only that admissible
evidence**, letting every semantically or evidentially blocked rule (`PRICE_RANGE`,
`RELATIVE_VOLUME_MINIMUM`, and all non-market-bar rules) resolve to
`INSUFFICIENT_DATA`/`UNKNOWN` per the existing Phase 3A contract — **without weakening the
global preflight**. Widening admissibility further (corporate-action context for the
absolute-price band; volume unit / corporate-action / filter stationarity for volume
rules) remains a later, separate acquisition.
