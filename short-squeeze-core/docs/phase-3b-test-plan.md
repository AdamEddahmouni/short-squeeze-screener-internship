# Phase 3B Test Plan

Tests live in `tests/research/`; fixtures live in `tests/fixtures/research/`. Tests are
offline and use fresh explicit pytest temporary directories.

## Contracts, registry, and identity

- Assert every model is frozen, forbids extra fields, normalizes symbols and UTC
  boundaries, and uses stable enum and field order.
- Reject duplicate and unknown case IDs, duplicate semantic identities, unsupported
  policies, and conflicting symbol/as-of identities with stable diagnostics.
- Verify explicit request and canonical case ordering independently.
- Verify paths, wall-clock values, random values, credentials, and unrestricted prose
  do not enter deterministic identities.
- Verify no contract exposes score, weight, rank, recommendation, alert, P&L, entry,
  exit, position, or trading fields.

## Detection policy

- All three required rules `PASS` -> `DETECTED`.
- Any one required rule `FAIL` -> `NOT_DETECTED`.
- A required `UNKNOWN`, `CONFLICTED`, `INSUFFICIENT_DATA`, or `NOT_APPLICABLE` ->
  `UNEVALUABLE`.
- Reject duplicate required rules, unknown rules, and unsupported versions.
- Preserve supporting Phase 3A rule-result IDs and stable diagnostics.
- Verify original-platform status has no effect on status or deterministic ID.
- Generate stable IDs and byte-identical serialization under permuted input order.

## Outcome labels

- Moves above and exactly equal to `+25%` cross the upward threshold; a smaller move
  does not.
- Moves below and exactly equal to `-25%` cross the downward threshold; a smaller
  adverse move does not.
- Both crossings produce `MIXED_OR_VOLATILE`; upward-only and downward-only crossings
  produce their respective labels.
- A complete 24-hour horizon with neither produces
  `NO_SUBSTANTIAL_UPWARD_MOVE`.
- A partial horizon with neither produces `OUTCOME_INSUFFICIENT_DATA`.
- A partial horizon with a directly observed crossing retains the crossing label.
- A missing objective observation produces `OUTCOME_UNKNOWN`.
- Reject unsupported horizon, reference, and policy versions.
- Preserve boundary, reference, extrema, coverage, support IDs, policy provenance,
  stable IDs, and exact Decimal serialization.
- Verify no label or field claims a confirmed squeeze, P&L, entry, or exit.

## Research classification

- Cover true positive, false positive, false negative, and true negative exactly as
  declared by the truth table.
- Cover unevaluable detection, unknown outcome, insufficient outcome, mixed outcome,
  and downward outcome as `UNEVALUABLE`.
- Verify original-platform status does not alter classification.
- Verify labeling a later outcome leaves the original Phase 3A object and serialized
  bytes unchanged.
- Verify stable classification identity and no trading interpretation.

## Batch execution

- Cover one and multiple cases, request and canonical order, input permutation,
  duplicate/unknown case IDs, empty batch, complete, partial, evaluation-only,
  outcome-only, artifact-discovery, and blocked cases.
- Cover `fail_fast=true` and `fail_fast=false` with exact failed/skipped diagnostics.
- Invoke the existing Phase 3A evaluator for explicit request artifacts and verify
  frozen result artifacts without reimplementing rule semantics.
- Run repeated builds and compare batch bytes and IDs.
- Assert no network access and no sorting by outcome or candidate attractiveness.

## Matrices and summaries

- Cover one and multiple cases/rules, all six Phase 3A outcomes, policy rule order,
  request/canonical case order, observed values, threshold values, and diagnostics.
- Verify pass, fail, unknown, conflict, insufficient, and not-applicable counts,
  evaluable denominators, zero denominators, and exact Decimal rates.
- Verify outcome-conditioned and category summaries are counts only and carry the
  small-sample diagnostic.
- Verify missingness for short interest, days to cover, borrow fee, borrow availability,
  float, relative-volume history, news timestamps, SEC filings, provider scope,
  conflicts, and insufficient history.
- Assert no predictive-claim, score, rank, or recommendation field.

## Dataset and export

- Cover JSON, JSONL, and CSV, stable row/dataset/provenance IDs, stable column order,
  exact Decimal strings, missing values, all rule outcomes, category counts,
  original-platform status, detection, label, classification, limitations, source IDs,
  and fixture classification.
- Cover true-positive, false-positive, true-negative, false-negative, and unevaluable
  filtered datasets in canonical order.
- Verify UTF-8, LF-only CSV, explicit empty values, and formula-injection protection.
- Verify no absolute paths, credential values, score, weight, rank, recommendation,
  alert, P&L, or trading field.
- Export every format twice and compare bytes.

## BIYA and additional cases

- Build earliest and latest BIYA cases separately at their exact boundaries.
- Assert the frozen Phase 3A evaluation IDs remain unchanged, required detection rules
  pass, short-pressure rules remain unknown, and 24-hour outcome labels are substantial
  upward moves under the approved partial-window asymmetry.
- Assert outcome construction does not mutate Phase 3A results.
- Retain `KLRS`, `LBGJ`, `SG`, `TRVI`, `SLS`, and conflicted `KLOS` with the exact
  incomplete statuses documented in the inventory; do not fabricate evaluations.
- Mark every synthetic case `SYNTHETIC_EDGE_CASE` and cover all classifications,
  missing outcomes, conflicts, insufficient data, duplicate IDs, and ordering modes.

## Anchors, compatibility, and isolation

- Generate every named Phase 3B anchor twice and compare bytes and hashes.
- Run both CLI commands and BIYA case builds twice and compare bytes.
- Assert all pre-Phase-3B manifests are unchanged from
  `b7c7394d5fe8ee16bd3bd1482ce218a203162104`.
- Run AST-aware isolation checks over `squeeze_core.research` for prohibited imports,
  executable calls, identity inputs, scoring, ranking, recommendations, alerts, and
  trading language.
- Run dedicated research, evaluation, validation, readiness, metrics, and compatibility
  suites, then the complete suite with fresh explicit temp directories.
