# Phase 3D Calibration Report

- Experiment: `detection_predicate_candidates_historical.v1`
- Type: `DETECTION_ABLATION`
- Cohort: `HISTORICAL_COMPLETED_CASES`
- Analysis unit: `CASE_BOUNDARY`
- Baseline: `baseline`

## Limitations

- **COUNTERFACTUAL_EXPLORATION_ONLY** — Calibration results are counterfactual explorations, not predictive validation.
- **NO_THRESHOLD_AUTO_PROMOTION** — No variant in this report is authorized for automatic promotion to production policy.
- **SMALL_SAMPLE_WARNING** — Small labeled cohorts limit interpretability; intervals do not repair representativeness.
- **OUTCOME_BLIND_BOUNDARY_SELECTION** — Boundary selection reuses Phase 3C outcome-blind cohort policies.

## Variant summary

### baseline

Current Phase 3B structural momentum predicate (3 rules).

- Cases: 7
- Confusion matrix: TP=2 FP=0 TN=0 FN=0 unevaluable=5

### momentum_pct_change

Add PERCENTAGE_CHANGE_MINIMUM; tests whether metric availability changes BIYA detection.

- Cases: 7
- Confusion matrix: TP=2 FP=0 TN=1 FN=1 unevaluable=3
- Classification flips from baseline: 2
  - `KLRS_ARTIFACT_DISCOVERY` (KLRS): UNEVALUABLE → FALSE_NEGATIVE
  - `SG_ARTIFACT_DISCOVERY` (SG): UNEVALUABLE → TRUE_NEGATIVE

### momentum_full

Require all six momentum discovery rules.

- Cases: 7
- Confusion matrix: TP=0 FP=0 TN=1 FN=3 unevaluable=3
- Classification flips from baseline: 4
  - `BIYA_EARLIEST_BOUNDARY` (BIYA): TRUE_POSITIVE → FALSE_NEGATIVE
  - `BIYA_LATEST_BOUNDARY` (BIYA): TRUE_POSITIVE → FALSE_NEGATIVE
  - `KLRS_ARTIFACT_DISCOVERY` (KLRS): UNEVALUABLE → FALSE_NEGATIVE
  - `SG_ARTIFACT_DISCOVERY` (SG): UNEVALUABLE → TRUE_NEGATIVE

### short_pressure_core

Baseline plus PUBLISHED_SHORT_INTEREST_AVAILABLE.

- Cases: 7
- Confusion matrix: TP=2 FP=0 TN=0 FN=0 unevaluable=5
- Classification flips from baseline: 0

