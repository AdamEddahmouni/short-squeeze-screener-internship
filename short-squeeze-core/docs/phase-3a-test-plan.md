# Phase 3A Test Plan

Tests live in `tests/evaluation/`; fixtures live in `tests/fixtures/evaluation/` and
are classified as sanitized historical data, sanitized local artifact, or synthetic
edge case. No test uses network, credentials, a database, or wall-clock time.

## Contract and policy tests

- Assert all models are frozen and reject unknown fields.
- Assert exact category and outcome vocabularies and stable ordering.
- Assert exact Decimal serialization and deterministic identity.
- Assert no model or policy field contains score, weight, grade, rank, recommendation,
  candidate label, or composite state.
- Load the default policy twice; verify rule/category order, explicit units/operators,
  threshold provenance, and provisional flags.
- Reject unknown policies/rules and duplicate rule IDs with structured diagnostics.

## Rule outcome tests

Every rule has PASS and FAIL cases where a comparable value exists, plus the applicable
UNKNOWN, CONFLICTED, INSUFFICIENT_DATA, and NOT_APPLICABLE paths. Cross-cutting cases
assert that missing never defaults to FAIL, zero remains known, provider scope is
explicit, future evidence is excluded, corrections/cancellations follow receipt time,
and units cannot be compared silently.

Momentum coverage includes both price boundaries, return and relative-volume metrics,
insufficient relative-volume history and zero baseline, float known/missing, completed
and partial bars, future bars, mixed providers, and stable support IDs.

Short-pressure coverage includes short-interest availability/change, days-to-cover,
borrow fee/change, borrow availability/change, zero availability, provider mismatch,
future publications, revisions/cancellations, and an explicit assertion that FINRA
daily short-sale volume cannot satisfy any rule.

Catalyst coverage includes news before/after `as_of`, unknown publication time, late
receipt, withdrawal, SEC filing timing, corporate actions including reverse splits,
and absence of directional inference.

Validity coverage exercises Phase 2D domain states, material versus temporal conflict,
unit compatibility, history sufficiency, default-substitution detection, provider
scope, and point-in-time lifecycle changes.

## Aggregation and determinism

- Cover all six category counts across all four categories.
- Permute input observations, metrics, readiness objects, and enabled rules.
- Compare canonical bytes and deterministic IDs.
- Verify no aggregate outcome, score, grade, rank, recommendation, alert, or label.
- Generate the Phase 3A anchor manifest twice and compare bytes.
- Run the CLI twice and compare bytes.

## BIYA regression

At both detection boundaries, assert successful construction, independent category
results, explicit short-pressure missingness, exclusion of later news/outcome data,
preserved corporate-action context, no historical-borrow backfill, no days-to-cover
zero, distinct boundary identities, and byte-identical repeat runs. The Phase 2V
outcome conclusion remains an external reference and never becomes an evaluation input.

## Compatibility and isolation

The full Phase 1-2V suite and every prior manifest must remain unchanged. AST-aware
tests scan `squeeze_core.evaluation` for executable network/database/GUI/provider/ML/
indicator/trading imports and for random or wall-clock identity inputs. Dedicated
evaluation, validation, readiness, metrics, and compatibility suites run with fresh
explicit pytest temp directories before completion.

