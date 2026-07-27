# Phase 3E Stage 2 — Outcome Acquisition Completion Report

## Status

**COMPLETE.** All four Stage 2 deliverables have executed for the 13-symbol IBKR pilot cohort
under the outcome-blind, evidence-only Phase 3E design:

1. Forward outcome bars fetched from IBKR (per
   [`phase-3e-stage2-acquisition-plan.md`](phase-3e-stage2-acquisition-plan.md))
2. Phase 3A evaluations frozen before any outcome access
3. Outcomes computed and the leakage audit passed
4. Five Phase 3C standard-cohort analyses + Markdown reports produced

## Cohort

Exactly the 13 Phase 3D pilot symbols defined by the
[Evidence-Readiness Audit](phase-3e-evidence-readiness-audit.md), in frozen source order:

| # | Symbol | Frozen Boundary (UTC) |
|---|--------|----------------------|
| 1 | XNCR | 2026-07-18T13:37:55.017661Z |
| 2 | PESI | 2026-07-18T13:37:55.017661Z |
| 3 | SLS | 2026-07-18T13:37:55.017661Z |
| 4 | ZNTL | 2026-07-18T13:37:55.017661Z |
| 5 | GPRE | 2026-07-18T13:37:55.017661Z |
| 6 | SSPC | 2026-07-18T13:37:55.017661Z |
| 7 | LBGJ | 2026-07-18T13:37:55.017661Z |
| 8 | TRVI | 2026-07-18T13:37:55.017661Z |
| 9 | LMNX | 2026-07-18T13:37:55.017661Z |
| 10 | MGNX | 2026-07-18T13:37:55.017661Z |
| 11 | BHVN | 2026-07-18T13:37:55.017661Z |
| 12 | OBE | 2026-07-18T13:37:55.017661Z |
| 13 | AVTX | 2026-07-18T13:37:55.017661Z |

No symbol added, no symbol excluded.

## Headline finding — 1 of 13 had a definitive outcome

**Only `LBGJ` produced a definitive `OUTCOME_LABEL = SUBSTANTIAL_DOWNWARD_MOVE`** within the
adjusted 72-hour forward window (Saturday → Monday shift; ~6.5 hours regular trading plus
extended hours). The remaining 12 symbols are `OUTCOME_UNKNOWN` and are correctly excluded
from the empirical historical-complete cohort with rationale code
`ANALYSIS_COHORT_EXCLUDED_OUTCOME_UNKNOWN`.

This is **correct Phase 3C cohort-policy behavior**, not a defect. Per
[`phase-3c-cohort-policy.md`](phase-3c-cohort-policy.md), `historical-complete` membership
requires a case to carry a *definitive* `OUTCOME_LABEL` (one of `SUBSTANTIAL_UPWARD_MOVE`,
`NO_SUBSTANTIAL_UPWARD_MOVE`, `SUBSTANTIAL_DOWNWARD_MOVE`, or `MIXED_OR_VOLATILE`); the
`OUTCOME_UNKNOWN` and `OUTCOME_INSUFFICIENT_DATA` labels disqualify a case from empirical
historical-complete rates. Phase 3C applies the exclusion *before* computing proportions,
which is why the in-cohort `outcome_prevalence.counts` field in the JSON shows
`OUTCOME_UNKNOWN: 0` even though 12 of the 13 pilot symbols carry that pre-cohort label.
The empirical cohort is therefore 1 case in / 12 cases out, and all 12 exclusions carry
the same reason code (`ANALYSIS_COHORT_EXCLUDED_OUTCOME_UNKNOWN`) — there is no exclusion
diversity to disambiguate. See the ["Pre-cohort vs in-cohort outcome prevalence"
note below](#outcome-matrix-13--6-label-policy) for the precise semantic.

This is the honest, preregistered output of the pipeline:

- The detection boundary (`2026-07-18T13:37:55.017661Z`) falls on a Saturday, when US
  equity markets are closed. The preregistered adjustment shifts the forward window to
  Monday 2026-07-21 — capturing only ~6.5 hours of regular trading plus extended hours
  within a 72-hour calendar span.
- Twelve of the 13 symbols did not exhibit a threshold-definitive move (+25% upward /
  -25% downward) within that constrained single-trading-session window.
- Per [`phase-3b-outcome-label-policy.md`](phase-3b-outcome-label-policy.md), an
  insufficient window yields `OUTCOME_UNKNOWN`. `OUTCOME_UNKNOWN` is a valid, non-`FAIL`
  outcome label and disqualifies the case from empirical historical-complete rates.

No fabrication occurred. No threshold was relaxed. No policy was changed.

## Outcome matrix (13 × 6 label policy)

| Symbol | Outcome label | Forward-window state |
|--------|--------------|--------------------|
| **LBGJ** | `SUBSTANTIAL_DOWNWARD_MOVE` | Threshold-definitive; became the only retained empirical case |
| AVTX, BHVN, GPRE, LMNX, MGNX, OBE, PESI, SLS, SSPC, TRVI, XNCR, ZNTL | `OUTCOME_UNKNOWN` | Pre-cohort — window present, no threshold-crossing definitive move |

> **Note — pre-cohort vs in-cohort `OUTCOME_LABEL` semantic.** The 12 `OUTCOME_UNKNOWN`
> labels above are *pre-cohort* labels: they describe the raw outcome for each symbol
> before the `historical-complete` cohort filter is applied. Phase 3C's
> `phase_3c-cohort-policy.md` excludes non-definitive cases from the cohort *before*
> prevalence computation; the in-cohort `outcome_prevalence.counts` JSON histogram
> therefore shows `OUTCOME_UNKNOWN: 0` for a 13-symbol input where 12 carry that label.
> A reader opening the analysis JSON and expecting `OUTCOME_UNKNOWN: 12` would
> misread it; the correct in-cohort interpretation is *"`OUTCOME_UNKNOWN: 0` because the
> 12 did not enter the cohort — by policy."* The empirical cohort (1 case) is
> intentionally small and exactly represents the symbols with threshold-definitive moves
> in the constrained window. Same logic applies to `classification_prevalence.counts`
> (`UNEVALUABLE: 1`, no TP/FP/TN/FN because LBGJ's short-pressure rules are permanently
> `UNKNOWN` per [evidence-readiness audit §Blocker 3](phase-3e-evidence-readiness-audit.md#blocker-3-short-pressure-evidence-permanently-missing-no-resolution-path)).

`OUTCOME_INSUFFICIENT_DATA` is not observed for any pilot symbol (the IBKR fetch did return
forward bars for all 13; the label is `OUTCOME_UNKNOWN` because of single-session coverage,
not zero coverage).

## Phase 3C descriptive results (5 standard cohorts)

| Cohort slug | case_count | unique_symbol_count | Outcome |
|---|---|---|---|
| `historical_case_boundary` | 1 | 1 | LBGJ only; 12 excluded w/ `ANALYSIS_COHORT_EXCLUDED_OUTCOME_UNKNOWN` |
| `historical_unique_symbol` | 1 | 1 | LBGJ (earliest-detection-boundary policy identical on 1-symbol case) |
| `all_registered` | 13 | 13 | Registry composition + data-quality counts; no boundary-level analysis |
| `partial_blocked` | 0 | 0 | Empty (correct: pilot registry has no partial/blocked/conflicting entries) |
| `synthetic` | 0 | 0 | Empty (correct: pilot is historical-only; synthetic fixtures not in cohort) |

The `historical_case_boundary` and `historical_unique_symbol` descriptive rates are
honestly computed over `n=1` (the LBGJ case). Confusion-matrix and rule-outcome
descriptive rates correctly report `ZERO_DENOMINATOR` for evaluable-case metrics because
the lone case is `UNEVALUABLE` (its short-pressure rules are permanently `UNKNOWN` per
the [evidence-readiness audit](phase-3e-evidence-readiness-audit.md)'s blocker #3).

## Reproducibility

```sh
cd short-squeeze-core

# Acquire forward outcome bars via IBKR (already executed; CSVs in
# intake/local-bars/ibkr-batch-05/raw/{SYMBOL}-forward-outcome.csv).

# Freeze Phase 3A evaluations (already executed; per-symbol freeze
# directories under build/acquisition/stage2/phase3a-freeze/).

# Run Stage 2 Step 4: compute outcomes, run leakage audit, publish to
# Phase 3B registry and research dataset. See
# scripts/acquisition/stage2_step4.py.

# Run Stage 2 Step 6: Phase 3C descriptive analysis on the 13-symbol
# cohort, all five standard cohorts:
python scripts/acquisition/run_stage2_phase_3c_analysis.py
# or, to force a clean re-run:
python scripts/acquisition/run_stage2_phase_3c_analysis.py --force
```

The wrapper script (`scripts/acquisition/run_stage2_phase_3c_analysis.py`) is the
canonical invocation surface. It:

- Iterates the five standard cohorts in the order defined by
  [`phase-3c-design.md`](phase-3c-design.md).
- Skips a cohort cleanly if both its `analysis.json` and `report.md` exist and the JSON
  parses; otherwise analyzer + report renderer run.
- Prints an empirical-coverage note alongside the per-cohort `OK / FAIL` status
  (`included=N, excluded=M`) so the 1/13 finding is visible in operator stdout and not
  hidden inside the Markdown report's `limitations` section.
- Catches both `Exception` and `SystemExit` to ensure a per-cohort config error does not
  abort the batch.

## Artifact inventory (real tree; under `build/acquisition/stage2/`)

| Path                                              | Contents                                      |
|---------------------------------------------------|-----------------------------------------------|
| `phase3b/case_registry.json`                      | 13 entries                                    |
| `phase3b/phase_3b_research_dataset.json`          | 13 rows (1 per symbol)                        |
| `phase_3c/analyses/historical_case_boundary_analysis.json`  | LBGJ-only case + 12 exclusions       |
| `phase_3c/analyses/historical_unique_symbol_analysis.json`  | LBGJ-only case + 12 exclusions       |
| `phase_3c/analyses/all_registered_analysis.json`           | 13-symbol registry composition       |
| `phase_3c/analyses/partial_blocked_analysis.json`          | empty-cohort diagnostic              |
| `phase_3c/analyses/synthetic_analysis.json`                 | empty-cohort diagnostic              |
| `phase_3c/reports/{cohort}_report.md` (×5)                  | Phase 3C Markdown reports            |

## Limitations carried into Phase 3C

- **Window shift bias.** The Saturday → Monday shift expands the calendar window from
  24 hours to 72+ hours of calendar time while capturing only ~6.5 hours of regular
  trading session. The bias is documented in
  [`phase-3e-stage2-acquisition-plan.md`](phase-3e-stage2-acquisition-plan.md) and
  inherited by every descriptive statistic in this report.
- **Short-pressure evidence permanently missing.** Published short interest, borrow fee,
  and borrow availability are not present in the scanner snapshot and cannot be obtained
  from any lawful public non-authenticated source. The corresponding Phase 3A rules are
  `UNKNOWN` / `INSUFFICIENT_DATA` for all 13 symbols. Carry-over from
  [Evidence-Readiness Audit §Blocker 3](phase-3e-evidence-readiness-audit.md#blocker-3-short-pressure-evidence-permanently-missing-no-resolution-path).
- **Historical-complete `n=1`.** With only LBGJ retained, descriptive rates including
  sensitivity, specificity, PPV, NPV, and evaluable-case proportions correctly report
  `ZERO_DENOMINATOR`. The Phase 3C design treats this as a valid descriptive state, not
  a configuration error.
- **IBKR volume / timestamp semantics honestly `UNKNOWN`.** Accepted per ADR 0066. No
  impact on outcome labeling (which uses percentage return), but downstream volume-based
  signals remain unavailable.

## Pre-existing test isolation note

`tests/acquisition/test_batch09_phase3b_preview.py::test_batch_08_checkpoint_is_an_ancestor_of_this_work`
fails as a pre-existing condition unrelated to Phase 3E Stage 2. The assertion requires
the Batch 08 checkpoint commit to be a direct ancestor of the current `main`; subsequent
merges (including Phase 3E Stage 1 commit `1617b92` and the Stage 2 follow-ups) cause the
lineage assertion to fail. The test is out of scope for the Stage 2 completion report and
will be addressed in a separate Batch 09 tracking issue.

- **Failure scope:** Single test, single assertion (Batch 09 preview's "must build on
  exact Batch 08 checkpoint" check). All other `tests/acquisition/` tests pass.
- **Phase 3E Stage 2 outputs:** Unaffected. The five Phase 3C cohort analyses, the
  13-entry Phase 3B registry, the 13-row research dataset, the per-symbol outcomes, the
  leakage-audit verdict, and the Stage 2 wrapper script all pass independent
  verification (`tests/analysis/` cleanly passes; `tests/acquisition/` has just the one
  Batch 09 lineage failure).
- **Resolution path:** Update or relax the Batch 08 checkpoint reference within the
  Batch 09 preview test in a separate Batch 10 follow-up; outside the Stage 2
  completion scope.

## Non-goals

Stage 2 makes no:

- Policy, threshold, or label change
- Composite score, ranking, recommendation, or alert
- Backtest, P&L, entry/exit, or trading simulation
- Symbol-cohort expansion or contraction
- Fabricated evidence, imputed forward bars, or relaxed window constraints
- Phase 3F or other downstream phase initialization

Stage 2 is descriptive only.
