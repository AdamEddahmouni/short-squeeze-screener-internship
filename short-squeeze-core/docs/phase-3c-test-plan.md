# Phase 3C Test Plan

## Purpose

This plan verifies the deterministic descriptive research-analysis layer defined in `docs/phase-3c-design.md`. Tests are written and observed failing before production behavior is added. Each implementation slice ends with focused green tests and a local commit.

The existing Phase 1–3B suite and anchor bytes remain the compatibility baseline. Phase 3C uses fresh basetemp directories and separate fixtures under `tests/fixtures/analysis`.

## Test organization

Create `tests/analysis` with focused modules for:

- Models, diagnostics, policies, and identity.
- Cohort selection and exclusions.
- Boundary selection.
- Proportions and Wilson intervals.
- Sample-size assessment.
- Symbol dependence.
- Confusion matrices and prevalence.
- Rule-outcome prevalence.
- Missingness and registry data quality.
- Runner orchestration.
- Serialization and Markdown reports.
- BIYA and standard cohorts.
- CLI behavior.
- Anchors and deterministic regeneration.
- Runtime isolation and prior-phase compatibility.

Tests use Phase 3B fixtures by reference. Small synthetic objects may cover mathematical and branch edge cases, but their fixture classification remains synthetic and they are never presented as historical evidence.

## Contracts, diagnostics, and identities

Verify that all Phase 3C models are frozen, reject extra fields, preserve schema `1.0.0`, normalize symbols, canonically order set-like fields, and reject contradictory states.

Identity tests cover:

- Stable UUIDv5 output for identical semantic input.
- Input-order invariance for case IDs, symbols, diagnostics, and exclusions where ordering is not policy-significant.
- Identity changes for source dataset, source registry, cohort, analysis unit, boundary policy, statistics policy, interval policy, confidence level, sample-size policy, provenance, membership, exclusion, and limitation changes.
- `UNIQUE_SYMBOL` and `UNIQUE_SYMBOL_POLICY_SELECTED_BOUNDARY` remain semantically distinct and produce distinct identities.
- Registry-only results preserve `source_registry_id`, dataset-only results preserve `source_dataset_id`, and combined results preserve both independently without a synthetic combined source identity.
- No wall-clock, absolute-path, credential, random, outcome-aware selection, or unrestricted-prose identity inputs.
- No collisions among required Phase 3C anchors.

Diagnostic tests assert exact codes and canonical ordering for empty, partial, mixed, excluded, dependent, undefined-rate, interval, data-quality, and interpretation states.

## Cohort construction

Write failing tests for:

- Historical completed case-boundary membership.
- Historical completed unique-symbol membership.
- Synthetic-only membership.
- All-registered membership.
- Partial, artifact-discovery, blocked, and conflicting-identity membership.
- Mixed-provenance warning and performance-analysis rejection.
- Empty cohorts.
- Duplicate case IDs.
- Missing required registry input.
- Stable included and excluded case IDs.
- Exact exclusion reason codes.
- Fixture classifications and counts.
- Input-order invariance.
- No silent dropping of incomplete cases.

Historical empirical-rate cohorts must reject synthetic rows. Synthetic TP, FP, TN, and FN fixtures exist only for software and truth-table coverage and must never enter historical descriptive research-classification rates, historical confidence intervals, or empirical interpretation. Complete-case cohorts must exclude partial, blocked, evaluation-only, outcome-only, artifact-discovery-only, and unknown-outcome cases with preserved reasons.

## Boundary selection

Write failing tests showing that `earliest_detection_boundary_per_symbol.v1`:

- Selects the earliest `evaluation_as_of` for one symbol.
- Selects independently for multiple symbols.
- Uses canonical case ID as a stable tie-breaker.
- Preserves excluded later boundary IDs.
- Preserves boundary counts per symbol.
- Is invariant to input order.
- Does not read outcome label, maximum move, research classification, rule result, or platform status.
- Does not select a favorable outcome or maximum return.
- Produces a different identity from `all_case_boundaries.v1`.

Canonical case ID ordering must fully resolve equal `evaluation_as_of` ties for valid unique case IDs. `ANALYSIS_BOUNDARY_SELECTION_AMBIGUOUS` is emitted only when required boundary data is absent or input remains genuinely unresolved after documented tie-break rules. No latest-or-best policy is implemented.

## Proportions

Test `0/1`, `1/1`, `1/2`, `2/3`, and `0/0`.

Every result must preserve:

- Metric name.
- Numerator and denominator.
- Exact fraction.
- Exact Decimal value and percentage.
- Defined state and undefined reason.
- Cohort ID and analysis unit.
- Interval, confidence, and sample-size policy provenance.
- Deterministic identity.

`0/0` must be undefined, with no decimal percentage, NaN, infinity, or coerced zero. A numerator below zero or greater than the denominator is invalid.

## Wilson intervals

Test zero successes, all successes, one of two, one observation, small denominators, and a typical denominator at confidence `0.95`. Expected values use fixed z constant `1.95996398454005423552`, Decimal context precision `50`, `ROUND_HALF_EVEN`, and serialized quantization `0.000000000001`.

Verify:

- Exact numerator, denominator, method, and confidence level.
- Deterministic repeated bounds.
- Bounds clamped to `[0, 1]`.
- Zero denominator produces no interval.
- Unsupported confidence levels are rejected.
- Repeated-symbol case-boundary intervals carry the unsatisfied-independence marker.
- Unique-symbol intervals do not claim representativeness.
- No bootstrap, random sampling, SciPy, or floating serialization instability.
- No platform-dependent inverse-normal calculation.

## Sample-size assessment

Parameterize boundaries:

- `0` → `NO_OBSERVATIONS`.
- `1` → `ONE_OBSERVATION`.
- `2` and `4` → `VERY_SMALL`.
- `5` and `19` → `SMALL`.
- `20` and `49` → `LIMITED`.
- `50` → `DESCRIPTIVE_ONLY`.

Preserve unique-symbol count and analysis unit. Every state includes allowed and forbidden interpretations and explicitly denies predictive validation. The completed historical unique-symbol cohort must be `ONE_OBSERVATION`.

## Dependence

Test one case per symbol and multiple boundaries per symbol. Assert case count, unique-symbol count, symbols with multiple boundaries, repeated-boundary count, maximum boundaries, ordered boundary IDs, dependence flag, independence flag, recommended analysis unit, limitations, and stable identity.

For the historical BIYA case-boundary cohort, assert two cases, one symbol, one repeated boundary, dependence detected, independence not satisfied, and unique-symbol analysis recommended. This state is a limitation, not an error.

## Confusion matrices and prevalence

Build synthetic unit tests for TP-only, FP-only, TN-only, FN-only, mixed counts, and all-unevaluable inputs. Assert exact TP, FP, TN, FN, and unevaluable counts.

Derived sensitivity, specificity, PPV, NPV, false-positive rate, and false-negative rate preserve exact numerators and denominators. Zero-denominator rates remain undefined. Defined binomial rates include Wilson intervals and sample-size assessments.

Historical confusion-matrix tests exclude synthetic rows and apply dependence warnings at case-boundary level. Names and report text use “descriptive research-classification rate,” never validated model-performance language.

Detection, outcome, and classification prevalence tests cover every enum value, all-case and evaluable denominators, zero denominators, stable enum order, and explicit unevaluable counts.

## Rule-outcome prevalence

For every Phase 3A rule, test PASS, FAIL, UNKNOWN, CONFLICTED, INSUFFICIENT_DATA, and NOT_APPLICABLE counts plus total and evaluable denominators.

Verify pass rate among all cases, pass and fail rates among evaluable cases, and unknown/conflicted/insufficient/not-applicable rates among all cases. Zero evaluable denominators remain undefined. Rule order follows the Phase 3A policy, with no rank, importance, weight, or threshold recommendation.

Cover historical case-boundary, historical unique-symbol, and synthetic cohorts separately. Outcome-conditioned summaries preserve group size, provenance, sample size, and dependence without significance tests or predictive claims.

## Missingness and registry data quality

Test deterministic summaries for:

- Published short interest and change.
- Days to cover.
- Borrow fee and change.
- Borrow availability and change.
- Float.
- Percentage-change and relative-volume history.
- News and news timestamp.
- SEC filings and corporate-action context.
- Provider scope.
- Conflicted evidence.
- Insufficient history.
- Partial outcomes.
- Unknown platform status.
- Conflicting identity.
- Incomplete registry cases.
- Multiple boundaries per symbol.

Each statistic preserves count, denominator, affected case IDs, affected symbols, cohort, analysis unit, and identity. Missingness is not converted to failure.

Registry tests assert honest coverage for KLRS, LBGJ, SG, TRVI, SLS, and KLOS, including status, platform state, available artifacts, identity conflict, performance-cohort exclusion reason, and required evidence. They must not fabricate evaluation or outcome records or infer `NOT_SURFACED` from absence.

## Runner and standard cohorts

The runner receives already loaded dataset and optional registry objects plus a fully specified immutable request. Tests reject implicit scans, unrecognized versions, absent registry input for registry cohorts, inconsistent source IDs, and hidden mixed-provenance performance requests.

Build and compare the five standard results:

1. Historical case boundaries.
2. Historical unique symbols.
3. Synthetic cases.
4. All registered data quality.
5. Partial and blocked cases.

Every result is self-describing and includes all source IDs, cohort and analysis policies, provenance, membership, exclusions, components, limitations, diagnostics, and deterministic identity.

## BIYA regression analysis

Case-boundary tests include `BIYA_EARLIEST_BOUNDARY` and `BIYA_LATEST_BOUNDARY`, their detection statuses, outcome labels, classifications, rule patterns, missing short-pressure evidence, partial-window limitations, and shared-symbol warning. Assert they are not independent predictive successes.

Unique-symbol tests select `BIYA_EARLIEST_BOUNDARY`, exclude `BIYA_LATEST_BOUNDARY`, use `earliest_detection_boundary_per_symbol.v1`, record outcome-blind rationale, and assess one observation. The result and report contain no predictive-validation or squeeze-causation claim.

## Serialization and reports

Canonical JSON tests assert stable field order, Decimal strings, explicit undefined values, LF endings, no NaN/infinity, and byte-identical repeated output.

Markdown tests assert stable section order and exact inclusion of scope, cohort, analysis unit, membership, exclusions, boundary policy, sample size, dependence, counts, defined and undefined rates, intervals, missingness, limitations, forbidden interpretations, and no recommendation.

Every historical report must contain the twelve required interpretation statements from the design. The synthetic report must state that synthetic cases test software behavior and do not provide empirical market evidence. The all-registered report must state that it is a data-quality description, not a performance estimate.

Scan serialized keys and report headings to reject score, rank, importance, recommendation, alert, expected return, P&L, backtest, entry/exit, threshold search, and trading fields. Reject `accuracy`, `validated performance`, `predictive success rate`, and `model quality` unless the phrase occurs only in explicit limitation text that negates the claim.

## CLI

Test `analyze-research-dataset` with explicit dataset, cohort, analysis unit, boundary policy, statistics policy, interval policy, confidence level, sample-size policy, and output. Registry cohorts additionally pass an explicit registry path.

Test `render-research-analysis-report` with explicit analysis, format, and output. Invoke standard commands twice and compare stdout and output bytes.

Invalid input returns canonical structured error JSON and nonzero exit. Tests confirm local files only, no network, no credentials, no GUI, no database, and no automatic cohort selection.

## Fixtures and anchors

Generate the Phase 3C fixtures and every named anchor required by the handoff under `tests/fixtures/analysis`. Use Phase 3B fixture references rather than copying large datasets.

Run the generator twice and compare every generated file hash. Test case-order, symbol-order, and rule-order invariance; policy and confidence identity changes; provenance separation; Markdown line endings; Decimal stability; and undefined-rate stability.

Required anchor names include all cohort, boundary, dependence, proportion, interval, sample-size, confusion-matrix, prevalence, missingness, BIYA, report, CLI, mixed-output, and serialized-collection anchors listed in the Phase 3C handoff.

## Isolation and compatibility

AST-aware tests scan only executable Phase 3C runtime code for prohibited imports and operations: network clients, provider SDKs, environment or credential access, databases, GUI/web frameworks, trading APIs, random or clock identity inputs, pandas/NumPy/SciPy/statsmodels/scikit-learn/ML frameworks, indicators, sentiment, scoring, ranking, recommendations, alerts, optimization, backtesting, and P&L.

Compatibility tests assert:

- Schema remains `1.0.0`.
- All nine prior manifests are byte-identical to Phase 3C base `e0708f51212ab11fd5767fc55b41b58f4614b44b`.
- Prior public exports and CLI anchors remain unchanged.
- Existing Phase 1–3B model and serialized bytes remain unchanged.
- Prior commands retain their output.

## Verification commands

Use fresh explicit temporary directories:

```powershell
.\.venv\Scripts\python.exe -m pytest tests\analysis --basetemp=.pytest-run-phase3c-analysis
.\.venv\Scripts\python.exe -m pytest tests\research --basetemp=.pytest-run-phase3c-research
.\.venv\Scripts\python.exe -m pytest tests\evaluation --basetemp=.pytest-run-phase3c-evaluation
.\.venv\Scripts\python.exe -m pytest tests\validation --basetemp=.pytest-run-phase3c-validation
.\.venv\Scripts\python.exe -m pytest tests\readiness --basetemp=.pytest-run-phase3c-readiness
.\.venv\Scripts\python.exe -m pytest tests\metrics --basetemp=.pytest-run-phase3c-metrics
.\.venv\Scripts\python.exe -m pytest tests\compatibility --basetemp=.pytest-run-phase3c-compat
.\.venv\Scripts\python.exe -m pytest --basetemp=.pytest-run-phase3c-final
```

After the final documentation commit, rerun the full suite, all deterministic generators and CLIs twice, prior-manifest diffs, Git state, tags, remotes, merge base, and all three archived repository checks before making a completion claim.

## Acceptance rule

Phase 3C is approved only when every required focused, dedicated, compatibility, determinism, isolation, and full-suite check passes from the final committed state; the tree is clean; no remote was added; nothing was pushed or merged; and Phase 3D has not begun.
