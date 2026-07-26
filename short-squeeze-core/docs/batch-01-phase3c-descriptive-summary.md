# Batch 01 — Phase 3C Descriptive Summary

The batch-01 Phase 3B registry candidates were run through the **existing** Phase
3C descriptive analyzer with no changes to any Phase 3C policy or code. Two
cohorts were generated; outputs are regenerable under `build/analysis/batch-01/`.

Commands (offline, local inputs only):

```bash
python -m squeeze_core analyze-research-dataset \
  --case-registry build/acquisition/batch-01/phase3b-registry-candidates.json \
  --cohort all-registered --analysis-unit unique-symbol \
  --boundary-policy earliest_detection_boundary_per_symbol.v1 \
  --statistics-policy phase_3c_descriptive_statistics_policy.v1 \
  --interval-policy phase_3c_interval_policy.v1 \
  --sample-size-policy phase_3c_sample_size_policy.v1 \
  --confidence-level 0.95 \
  --output build/analysis/batch-01/batch-01-all-registered-unique-symbol.json
```

(`--cohort partial-blocked` was also generated.)

## Results (all-registered, unique-symbol)

| Metric | Value |
| --- | --- |
| Analysis version | `phase_3c_analysis.v1` |
| Registered cases | 13 |
| Unique symbols | 13 |
| Complete cases | 0 |
| Partial cases (ARTIFACT_DISCOVERY_ONLY) | 13 |
| Blocked cases | 0 |
| Synthetic cases | 0 |
| Conflicting-identity cases | 0 |
| Evaluation boundaries | 0 |
| Confusion matrix | none (no complete cases) |
| Defined outcome/detection rates | none (no complete cases) |

- **Confusion-matrix counts:** undefined — there are no complete cases, so no
  detection×outcome confusion matrix is produced.
- **Rule prevalence / detection prevalence / outcome prevalence:** undefined for
  the same reason.
- **Sample-size assessment:** `allowed_interpretation` =
  `DESCRIBE_COHORT_COUNTS`, `DESCRIBE_UNCERTAINTY`; `forbidden_interpretation` =
  `CAUSAL_INFERENCE`, `PREDICTIVE_VALIDATION`, `STATISTICAL_VALIDATION`.
- **Missingness:** all 13 cases are registry-only; no per-domain complete-case
  missingness table applies.
- **Diagnostics:** `ANALYSIS_COHORT_MIXED_PROVENANCE`,
  `ANALYSIS_DESCRIPTIVE_ONLY`, `ANALYSIS_NO_PREDICTIVE_VALIDATION`.

## Distinguishing batch cases from prior BIYA / migrated cases

This analysis runs over the **batch-only** registry
(`phase_3d_batch_01_registry.v1`). It is not combined with the prior Phase 3B
fixtures, so the original BIYA and migrated cases remain distinguishable and no
prior artifact is overwritten.

## Explicit statement

**No predictive validation is claimed.** All values above are descriptive
research-classification and data-quality counts over registered cases. They are
not a performance estimate, not a detection accuracy, and not evidence of
predictive validity. Determinism was verified: the analysis output is
byte-identical across repeated runs.
