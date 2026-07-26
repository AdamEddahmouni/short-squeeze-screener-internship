# Phase 3C Deterministic Descriptive Research Analysis

## Status

Approved for implementation on `phase/3c-descriptive-research-analysis`, based directly on Phase 3B commit `e0708f51212ab11fd5767fc55b41b58f4614b44b`.

Phase 3C is descriptive only. It does not optimize thresholds or policies, validate predictive performance, assign scores, rank candidates, generate recommendations or alerts, simulate trades, calculate P&L, or begin Phase 3D.

## Objective

Phase 3C adds an offline deterministic analysis layer over explicit Phase 3B artifacts. It describes dataset composition, coverage, missingness, rule outcomes, retrospective outcomes, research classifications, confusion-matrix counts, sample size, and repeated-symbol dependence while preserving exact numerators, denominators, exclusions, limitations, and policy provenance.

The primary historical interpretation uses one policy-selected boundary per unique symbol. Case-boundary analysis remains available for transparency but is not treated as an independent performance sample when symbols repeat.

## Architectural decision

Create an additive `squeeze_core.analysis` package. Do not modify Phase 3B models or serialized artifacts. Phase 3C consumes:

- An explicit `ResearchDataset` for completed historical and synthetic cases.
- An explicit `CandidateCaseRegistry` for registry-level, incomplete, partial, blocked, and identity-conflict reporting.
- An immutable `ResearchAnalysisRequest` containing every policy and selection choice.

The rejected alternatives are a monolithic report builder, which would couple selection and interpretation, and extensions to `squeeze_core.research`, which would increase compatibility risk.

## Self-describing artifacts

Every cohort, analysis result, JSON artifact, and Markdown report identifies:

- Source dataset ID.
- Source registry ID when registry evidence is used.
- Cohort definition and cohort ID.
- Analysis unit.
- Boundary-selection policy version.
- Descriptive-statistics policy version.
- Interval policy version and confidence level.
- Sample-size policy version.
- Included and excluded case IDs.
- Fixture/provenance classifications.
- Deterministic identity.

No artifact relies on a hidden default filesystem scan. A request that needs registry-level evidence must provide the registry explicitly.

## Package responsibilities

The package is split by behavior rather than report format:

- `models.py`: frozen enums and analysis contracts.
- `identifiers.py`: UUIDv5 identities over canonical, policy-complete inputs.
- `diagnostics.py`: stable diagnostic contracts and ordering.
- `policies.py`: exact versioned policies and validation.
- `cohorts.py`: explicit cohort membership and exclusions.
- `boundary_selection.py`: all-boundary and earliest-boundary policies.
- `proportions.py`: exact fractions, Decimal proportions, and undefined results.
- `intervals.py`: deterministic standard-library Wilson score intervals.
- `sample_size.py`: conservative fixed sample-size assessments.
- `dependence.py`: repeated-symbol and boundary-count summaries.
- `confusion_matrix.py`: descriptive classification counts and rates.
- `rule_prevalence.py`: Phase 3A rule-outcome prevalence in policy order.
- `missingness.py`: domain, conflict, insufficiency, and registry-quality summaries.
- `runner.py`: orchestration over already loaded explicit artifacts.
- `serialization.py`: canonical JSON parsing and rendering.
- `reports.py`: deterministic Markdown rendering.

Files may be combined where implementation remains focused; these responsibility boundaries remain mandatory.

## Cohorts

Phase 3C defines these standard cohorts:

1. Historical completed case boundaries.
2. Historical completed unique symbols using the earliest eligible boundary.
3. Synthetic completed cases.
4. All registered cases for registry and data-quality counts.
5. Partial, artifact-discovery, blocked, and conflicting-identity cases.
6. Mixed-provenance registry summary, explicitly labeled as non-performance analysis.

Historical empirical-rate descriptions never contain synthetic rows. Synthetic TP, FP, TN, and FN cases exist only for software and truth-table coverage and never enter historical descriptive research-classification rates, historical confidence intervals, or empirical interpretation. Incomplete, blocked, evaluation-only, outcome-only, artifact-discovery-only, and unknown-outcome cases never enter complete-case empirical rates. They remain visible through explicit exclusions and registry-level summaries.

## Analysis units and boundary selection

Supported analysis units are:

- `CASE_BOUNDARY`.
- `UNIQUE_SYMBOL`.
- `UNIQUE_SYMBOL_POLICY_SELECTED_BOUNDARY`.

`UNIQUE_SYMBOL_POLICY_SELECTED_BOUNDARY` is required whenever an analysis retains one concrete Phase 3B row per symbol under a boundary-selection policy. `UNIQUE_SYMBOL` is reserved for symbol-level aggregates that do not select or inherit a representative boundary row. The two units are not aliases and must produce different identities.

Supported boundary policies are:

- `all_case_boundaries.v1`.
- `earliest_detection_boundary_per_symbol.v1`.

The earliest-boundary policy groups eligible rows by normalized symbol and chooses the minimum `evaluation_as_of`. Equal timestamps are fully resolved by canonical `case_id` ordering because case IDs are unique within a valid source. `ANALYSIS_BOUNDARY_SELECTION_AMBIGUOUS` is reserved for absent required boundary data or input that remains genuinely unresolved after all documented tie-break rules. Selection does not inspect outcome labels, returns, classifications, rule outcomes, or original-platform status. The result preserves the selected boundary, excluded boundary IDs, and total boundary count for every symbol.

No latest, best, maximum-return, or favorable-classification policy exists.

## Policies

Phase 3C uses four explicit policies:

- `phase_3c_descriptive_statistics_policy.v1`.
- `phase_3c_interval_policy.v1` with `WILSON_SCORE` and confidence level `0.95`.
- `phase_3c_sample_size_policy.v1`.
- `earliest_detection_boundary_per_symbol.v1` or `all_case_boundaries.v1`.

All policies are provisional and unoptimized. Changing a policy version or confidence level changes deterministic identities.

## Proportions and undefined results

Every proportion preserves its metric name, numerator, denominator, exact fraction, Decimal value, percentage value, defined state, undefined reason, cohort ID, analysis unit, confidence level, interval policy, and sample-size policy.

Zero denominators produce an explicit undefined result. They never serialize as zero percent, NaN, or infinity. Evaluable-case denominators include only cases for which the relevant binary distinction is defined. Unevaluable cases remain separate counts.

## Wilson intervals

Wilson score intervals are calculated only for defined binomial proportions using deterministic standard-library `Decimal` arithmetic. Policy `phase_3c_interval_policy.v1` supports confidence level `0.95` with fixed z constant `1.95996398454005423552`. Intermediate arithmetic uses a local Decimal context with precision `50` and `ROUND_HALF_EVEN`; serialized lower and upper bounds are quantized to `0.000000000001` with `ROUND_HALF_EVEN`. Platform-dependent inverse-normal calculations are forbidden. Bounds are clamped to `[0, 1]`. A zero denominator yields no interval and a stable diagnostic.

Intervals for case-boundary cohorts with repeated symbols carry `independence_assumption_not_satisfied`. Unique-symbol intervals state that repeated boundaries were removed but do not imply market representativeness. Intervals are descriptive uncertainty summaries, not proof, significance, or validation.

## Sample-size assessment

`phase_3c_sample_size_policy.v1` maps:

- `0` to `NO_OBSERVATIONS`.
- `1` to `ONE_OBSERVATION`.
- `2..4` to `VERY_SMALL`.
- `5..19` to `SMALL`.
- `20..49` to `LIMITED`.
- `50+` to `DESCRIPTIVE_ONLY`.

Every assessment preserves sample size, unique-symbol count, analysis unit, limitations, allowed interpretation, forbidden interpretation, and policy version. Phase 3C never declares a sample statistically validated.

## Descriptive components

The runner produces:

- Cohort composition and explicit exclusions.
- Symbol dependence and boundary counts.
- Data-quality and provenance counts.
- Phase 3A rule-outcome prevalence in stable policy order.
- Missing-domain, conflict, and insufficient-data prevalence.
- Detection-status prevalence.
- Outcome-label prevalence.
- Research-classification prevalence.
- TP, FP, TN, FN, and unevaluable counts.
- Sensitivity, specificity, PPV, NPV, false-positive rate, and false-negative rate when denominators are nonzero.
- Wilson intervals and sample-size assessments for supported proportions.
- Machine-readable diagnostics and limitations.

These are called descriptive research-classification rates, never validated model-performance metrics.

## Registry-level data quality

The registry path remains distinct from dataset-row analysis. It keeps KLRS, LBGJ, SG, TRVI, SLS, and KLOS visible with their registry status, case type, platform status, artifact availability, identity conflict, exclusion reason, and required evidence. Missing evidence is not converted into a failed rule or an inferred platform outcome.

The all-registered report describes registry composition and data quality. It is not a performance estimate.

## BIYA dependence treatment

The completed historical dataset contains `BIYA_EARLIEST_BOUNDARY` and `BIYA_LATEST_BOUNDARY`. They are two boundaries for one symbol and are dependent observations.

Case-boundary analysis includes both and carries a dependence warning. Unique-symbol analysis selects `BIYA_EARLIEST_BOUNDARY` under `earliest_detection_boundary_per_symbol.v1`, records the later boundary as excluded, and assesses the cohort as one observation. This selection is outcome-blind.

BIYA demonstrates that the deterministic pipeline can preserve a detected case and a later substantial move without injecting outcome information into the original evaluation. It does not validate squeeze causation or general predictive performance.

## Reports and CLI

`analyze-research-dataset` accepts local explicit dataset and policy inputs. Registry-based cohorts additionally require a local explicit case registry. It writes canonical JSON and returns structured nonzero errors for invalid configurations.

`render-research-analysis-report` accepts a Phase 3C JSON analysis artifact and writes deterministic Markdown. A standard-cohort command may generate the five required report pairs without introducing implicit discovery.

Required reports cover historical case boundaries, historical unique symbols, synthetic cases, all registered data quality, and partial/blocked cases. The executive order prioritizes historical unique symbols.

## Determinism and identity

UUIDv5 identities include every material input: source IDs, cohort and analysis unit, boundary policy, included and excluded cases, exclusion codes, provenance classifications, policy versions, confidence level, component IDs, and limitation codes. Registry-level results preserve `source_registry_id`; dataset-based results preserve `source_dataset_id`; results using both preserve both fields independently. No synthetic combined source identity may obscure either original artifact.

Canonical serialization uses stable field and section order, sorted set-like values, exact Decimal strings, explicit null/undefined values, UTF-8, and LF line endings. It excludes absolute paths, wall-clock inputs, random IDs, credentials, unrestricted prose, and unordered iteration.

## Error handling

Invalid policy versions, unsupported confidence levels, duplicate case IDs, missing required registry inputs, ambiguous boundary ties after canonical tie-breaking, numerator/denominator violations, and mixed-provenance performance requests raise structured configuration errors. Empty cohorts and zero denominators are valid descriptive states represented by diagnostics rather than exceptions.

## Compatibility and isolation

Phase 3C remains schema `1.0.0` and additive. Prior Phase 1–3B fixtures, manifests, public exports, models, and CLI output bytes remain unchanged.

Runtime code remains offline and standard-library compatible apart from the repository's existing Pydantic contracts. It contains no provider SDKs, network clients, credential access, database drivers, random sampling, scientific-computing stack, machine learning, scoring, ranking, alerting, optimization, backtesting, P&L, or trading operations.

## Required historical interpretation

Every historical report states all of the following without qualification:

- The historical completed dataset currently represents one unique symbol.
- The two BIYA boundaries are dependent observations of the same symbol.
- Case-boundary counts are not independent performance samples.
- The default unique-symbol analysis selects the earliest boundary without using the outcome.
- The historical sample is insufficient for predictive validation.
- Outcome confirmation does not prove short-squeeze causation.
- Missing short-pressure evidence remains material.
- Rule prevalence does not prove predictive importance.
- Confidence intervals do not repair an unrepresentative sample.
- Synthetic cases are excluded from empirical performance estimates.
- Thresholds and policies were not optimized.
- No P&L, backtest, entry, exit, recommendation, or trading simulation was performed.

## Completion boundary

Phase 3C ends after deterministic fixtures, reports, CLIs, compatibility guards, isolation checks, documentation, focused commits, and full verification are complete. Phase 3D is not started.

## Additive Phase 3D relationship

Phase 3D was subsequently implemented as a separate acquisition package. It consumes Phase 3B artifacts for migration and publication compatibility but does not alter this design, its policies, thresholds, cohorts, fixtures, reports, or serialized results.
