# Phase 3A Design: Deterministic Transparent Candidate Evaluation

## Boundary

Phase 3A evaluates explicitly enabled research rules independently at an explicit
`as_of`. It reports the evidence, metrics, readiness snapshots, comparison, diagnostic,
and one of six outcomes for each rule. It does not compute a composite state, score,
weight, grade, rank, label, recommendation, alert, or trading action.

The four categories remain structurally distinct:

1. `MOMENTUM_DISCOVERY`
2. `SHORT_PRESSURE_CONFIRMATION`
3. `CATALYST_EVIDENCE`
4. `EVIDENCE_VALIDITY`

The six outcomes, in stable enum order, are `PASS`, `FAIL`, `UNKNOWN`, `CONFLICTED`,
`INSUFFICIENT_DATA`, and `NOT_APPLICABLE`. A `FAIL` always requires a known,
point-in-time-eligible, unit-compatible value. Missing evidence is never a failure.

## Additive package

`squeeze_core.evaluation` is additive and does not modify any Phase 1-2V model or
identity. It contains frozen Pydantic contracts, a versioned policy loader, selectors
over existing observations/metrics/readiness results, category-specific rule
evaluators, deterministic aggregation, serialization, and stable identifiers.

The package reuses:

- `build_point_in_time_evidence` for lifecycle and availability filtering;
- Phase 2A `PERCENTAGE_RETURN` rather than recalculating change;
- Phase 2B `RELATIVE_VOLUME` rather than provider snapshot division;
- Phase 2C short-interest and borrow metrics;
- Phase 2D coverage, conflict, missingness, and sufficiency results;
- canonical JSON and the existing deterministic UUID convention.

No old model receives a field, so schema `1.0.0` and all earlier serialized bytes stay
unchanged.

## Contracts and identity

`RuleThreshold` records the value, unit, operator, policy version, provenance,
rationale, and provisional flag. `RuleDefinition` records category, version, required
domains/metrics, and scope requirements. `CandidateEvaluationPolicy` contains an
explicit ordered rule set and has no scoring fields.

`RuleEvaluationRequest` requires symbol, asset class, `as_of`, policy version, enabled
rule IDs, provider scope, market interval/session, observations, metrics, and readiness
results. Enabled rules are never inferred from whatever data happens to be present.
Duplicates and unknown rules are structured errors.

`RuleEvaluationResult` preserves the exact observed and threshold quantities,
provider scope, supporting IDs, quality, sorted diagnostics, and an explanation code.
Its identity includes every semantic discriminator but excludes prose, insertion
order, wall-clock time, absolute paths, and credentials.

`CandidateEvaluationResult` contains sorted rule results and one descriptive count
summary per category. Its identity includes the enabled rule IDs and rule-result IDs.
There is no overall outcome.

## Initial policy

Policy `phase_3a_transparent_candidate_policy.v1` uses an explicit JSON policy file.
Original-platform thresholds are provisional research parameters, not validated
predictors: price `[2,20]`, percentage return `>=10%`, relative volume `>=5`, and float
`<=20,000,000 shares`. The float contract is implemented, but absent canonical float
evidence returns `UNKNOWN`.

Provisional Phase 3A research thresholds are: short-interest change `>=10%`, days to
cover `>=2 days`, borrow fee `>=10% annualized`, borrow-fee absolute change `>=2
percentage points`, borrow availability `<=100,000 shares`, and borrow-availability
absolute change `<=-10,000 shares`. Their provenance is explicit and they are not
presented as universal truths.

## Rule semantics

Momentum rules use the latest eligible completed market-bar close, Phase 2A percentage
return, Phase 2B relative volume, a canonical candidate-snapshot float when available,
market-bar domain presence, and completed-bar lifecycle state.

Short-pressure rules use eligible published short interest and Phase 2C metrics only.
Daily short-sale volume is never accepted. Zero borrow availability is a known value.
Unavailable inputs return `UNKNOWN`; an existing metric with insufficient samples
returns `INSUFFICIENT_DATA`; incompatible units return `INSUFFICIENT_DATA`; material
conflicts return `CONFLICTED`.

Catalyst rules are objective presence/timing checks over Phase 1 news, SEC filing, and
corporate-action evidence. They infer neither direction nor sentiment.

Validity rules project Phase 2D structural facts into independent outcomes. They do
not create a final readiness label. Temporal differences are not material conflicts.

## BIYA

BIYA is evaluated at `2026-07-17T14:23:58Z` and `2026-07-17T16:54:58Z`. Each request
uses only evidence eligible at its boundary. Later outcome bars confirm a later move
but are excluded from both requests. Missing published short interest and historical
borrow inputs stay explicit, and no days-to-cover zero is fabricated. The two complete
evaluations have distinct deterministic IDs and byte-identical repeated serialization.

## CLI and isolation

`build-candidate-evaluation` accepts local policy/evidence files, explicit symbol and
`as_of`, optional explicit enabled rules, and an output path. It performs no network,
credential, database, GUI, or provider-SDK operation. Invalid requests return canonical
structured errors and a nonzero exit code.

