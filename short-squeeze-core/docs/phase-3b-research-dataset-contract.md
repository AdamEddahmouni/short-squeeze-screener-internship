# Phase 3B Research Dataset Contract

The immutable dataset preserves case identity, boundary, fixture classification, original-platform status, all Phase 3A rule outcomes and result IDs, research detection, retrospective outcome, research classification, extrema, completeness, diagnostics, limitations, and source IDs. Incomplete and unevaluable records remain represented.

Filters for true positive, false positive, true negative, false negative, and unevaluable cases are deterministic views in canonical case order. JSON and JSONL use canonical serialization. CSV uses a fixed column order, UTF-8, LF endings, Decimal strings, explicit empty cells, and spreadsheet-formula injection protection. Paths and credentials are excluded from public rows.

No dataset field stores a score, weight, rank, recommendation, alert, entry, exit, position, P&L, portfolio result, or trading instruction.

Limitations: small sample size, incomplete historical coverage, unknown platform status, outcome-not-causation, prevalence-not-prediction, missing short-pressure data, public/original-provider differences, provisional detection and outcome definitions, unoptimized thresholds, and absence of statistical validation or trading simulation must accompany interpretation of every export.

## Additive Phase 3C use

Phase 3C reads this contract without changing it. Successful partial crossings do not expose a separate `outcome_completeness` field in this dataset contract; the analysis layer documents that limitation and never fabricates the missing field. Historical, synthetic, and mixed-provenance cohorts are formed explicitly from existing status and fixture-classification fields.
