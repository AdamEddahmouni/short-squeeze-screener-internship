# Batch 03 — Case-Association Boundary

The case-association boundary lets a later, separately authorized batch link a
validated bar bundle to an existing case — **without** doing any outcome work in
this batch.

## Declaration (`CaseAssociationMapping`)

Requires explicit fields: `case_id`, `canonical_symbol`,
`frozen_detection_boundary_id`, `requested_window_start`, `requested_window_end`,
`required_interval`, `required_session_coverage`, `bundle_id`.

There is no way to associate bars to a case without such a declaration; the
absence of one is `CASE_ASSOCIATION_WITHOUT_DECLARATION`.

## Validation (`validate_case_association`)

Given caller-supplied known reference sets (e.g. from an existing case registry),
the validator:

- verifies the referenced `case_id` exists (`UNKNOWN_CASE_ID` otherwise);
- verifies the `frozen_detection_boundary_id` exists (`UNKNOWN_BOUNDARY_ID`);
- when the bundle manifest is supplied, checks symbol, interval, and coverage
  compatibility (`CASE_SYMBOL_INCOMPATIBLE`, `CASE_INTERVAL_INCOMPATIBLE`,
  `CASE_COVERAGE_INCOMPATIBLE`).

Reference sets are supplied by the caller, so validation never reaches into or
mutates any case record.

## What it never does (this batch)

- compute an outcome or open the outcome window for analysis;
- create a Phase 3A request or result, or a Phase 3B outcome label or candidate;
- alter Batch 01 or Batch 02 case records;
- promote any candidate.

The result model asserts `outcome_computed = false` and
`phase_3a_or_3b_record_created = false` structurally and always. A validated
mapping is **preparation** for future authorized work — never evidence that the
requested window is complete.
