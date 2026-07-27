# Short-Squeeze Project — Phase 3C Complete Handoff

Generated: 2026-07-22  
Repository: `C:\Users\adame\Desktop\short-squeeze-project\short-squeeze-core`

## Completion status

Phase 3C is complete on branch `phase/3c-descriptive-research-analysis` at commit `14d35abfc9aacc6f2f4adaa3ad264950ec556d17`.

Delivered:

- Additive `squeeze_core.analysis` architecture.
- Five isolated cohort views.
- Outcome-blind boundary selection.
- Exact proportions and deterministic Wilson intervals.
- Dependence, sample-size, prevalence, confusion-matrix, missingness, and registry-quality analysis.
- Self-describing serialization and Markdown reports.
- Offline analysis and report CLI commands.
- 17 deterministic fixtures and 38 anchors.
- Compatibility and AST isolation guards.
- Policy documents and ADRs 0053–0058.

Verification:

- Final-HEAD full suite: `1893 passed, 1 skipped in 106.63s`.
- Dedicated suites: analysis 120, research 65, evaluation 50, validation 367, readiness 124, metrics 453, compatibility 130.
- All five standard analysis outputs repeated byte-identically.
- All five standard Markdown reports repeated byte-identically.
- All 17 generated fixture files repeated byte-identically.
- All nine Phase 1–3B manifests remain unchanged from `e0708f51212ab11fd5767fc55b41b58f4614b44b`.
- Archived repositories remain at `0897562e05d75b812dd284de81dfafdfa1dea916`, `6dbefd1a6b271bfc48106c4aa002f211735551cd`, and `84f770ddf33cf35bbe4ec3d8dfc12876d0068fd8`.
- Schema version remains `1.0.0`.
- Working tree was clean at completion.
- No Git remotes are configured.
- Phase 3D was not started.

Key project records:

- `docs/phase-3c-design.md`
- `docs/phase-3c-test-plan.md`
- `docs/phase-3c-progress.md` — includes all 38 anchor hashes and repeated CLI/report hashes.
- `docs/phase-3c-biya-analysis.md`
- `tests/fixtures/analysis/expected_phase_3c_analysis_metadata.json`

## Original fresh-session handoff

The complete original handoff follows verbatim.

---

# Short-Squeeze Project — Fresh-Session Handoff for Phase 3C

You are continuing a multi-phase forensic reconstruction and clean rebuild of an inherited short-squeeze research application.

This is a fresh Codex session.

Do not rely on prior chat context. Treat this prompt and the repository contents as the complete handoff.

Verify every supplied repository-state claim before modifying anything.

Complete Phase 3C only:

DETERMINISTIC DESCRIPTIVE RESEARCH ANALYSIS WITH EXPLICIT SAMPLE-SIZE, DEPENDENCE, COVERAGE, AND UNCERTAINTY LIMITATIONS

Do not begin threshold optimization, predictive modeling, candidate ranking, recommendations, alerts, paper trading, live trading, or Phase 3D.

---

# 1. Workspace

Workspace root:

C:\Users\adame\Desktop\short-squeeze-project

Implementation repository:

C:\Users\adame\Desktop\short-squeeze-project\short-squeeze-core

All implementation work must remain confined to:

C:\Users\adame\Desktop\short-squeeze-project\short-squeeze-core

The inherited repositories remain forensic evidence only.

They must remain:

- Unmodified
- Clean
- At their required commits
- Unmerged
- Unused as implementation targets

Read-only inspection is permitted where necessary.

Do not modify:

- Archived source code
- Archived tests
- Archived logs
- Archived credentials
- Archived Git history
- Authentication helpers
- Token files
- Phase 0 reconstruction evidence
- Completed Phase 1 history
- Completed Phase 2 history
- Completed Phase 2V history
- Completed Phase 3A history
- Completed Phase 3B history

---

# 2. Standing credential rule

This project and its forensic repositories are local-only.

Do not redact, mask, remove, replace, rotate, alter, or rewrite credentials, tokens, authentication parameters, API keys, cookies, or fragments of them in local source files, logs, documentation, inventories, fixtures, or forensic artifacts unless the user explicitly authorizes that exact change.

Preserve original artifacts byte-for-byte.

You may prevent credentials from entering an externally published generated copy, but any filtering must affect only that generated copy and must never modify the underlying local artifact.

Do not use fragments of real credentials as synthetic test values.

Use unrelated dummy values for tests.

Do not perform credential cleanup during this phase.

Do not print credentials in the completion report.

---

# 3. Expected repository state

Repository:

C:\Users\adame\Desktop\short-squeeze-project\short-squeeze-core

Expected branch:

phase/3b-multi-candidate-research-evaluation

Expected Phase 3B HEAD:

e0708f51212ab11fd5767fc55b41b58f4614b44b

Expected Phase 3B base:

b7c7394d5fe8ee16bd3bd1482ce218a203162104

Expected Phase 3A base:

5544cf608abbed7e1508f0bd65dd2a6b5ef66a99

Expected Phase 2D checkpoint:

9406032ab6f2422818e1986f78a60496daae8dd6

Expected Phase 1 release-candidate tag:

phase-1-rc1

Expected tag target:

f903d4d144d3f7e9717b1ab8e684da406d7968fb

Expected working tree:

clean

Expected remotes:

none

Expected baseline suite:

1770 passed
1 skipped
0 failed

Before doing anything else, run:

cd C:\Users\adame\Desktop\short-squeeze-project\short-squeeze-core

git status
git status --short
git branch --show-current
git rev-parse HEAD
git log --oneline --decorate -130
git remote -v
git tag --list
git show phase-1-rc1 --no-patch
git merge-base HEAD e0708f51212ab11fd5767fc55b41b58f4614b44b

Run the baseline suite with a fresh explicit temporary directory:

.\.venv\Scripts\python.exe -m pytest `
  --basetemp=.pytest-run-phase3c-baseline

Expected:

1770 passed
1 skipped
0 failed

Do not use the known locked .pytest-tmp path.

Do not broadly delete pytest directories.

If the terminal summary line is missing, use JUnit XML or another deterministic reporting method to verify the exact totals.

If the starting branch, HEAD, tag, tracked state, or baseline differs materially:

1. Do not reset.
2. Do not restore files.
3. Do not run git clean.
4. Do not discard changes.
5. Record the discrepancy.
6. Determine whether it is approved continuation work.
7. Stop only if continuing could overwrite or misattribute work.

---

# 4. Archived repository verification

The archived repositories must remain at:

0897562e05d75b812dd284de81dfafdfa1dea916
6dbefd1a6b271bfc48106c4aa002f211735551cd
84f770ddf33cf35bbe4ec3d8dfc12876d0068fd8

The second and third repositories may be nested Git repositories or submodules.

Verify them read-only.

Do not:

- Reset
- Checkout
- Clean
- Commit
- Amend
- Merge
- Rebase
- Change ACLs
- Add remotes
- Rewrite files
- Run formatters against archived files

---

# 5. Completed project state

The rebuild has completed:

## Phase 1

Point-in-time canonical evidence for:

CANDIDATE_SNAPSHOT
BORROW_FEE
BORROW_AVAILABILITY
PUBLISHED_SHORT_INTEREST
SEC_FILINGS
TRADING_HALTS
NEWS
MARKET_BARS
TRADES
QUOTES

## Phase 2A

Foundational market metrics:

ABSOLUTE_RETURN
PERCENTAGE_RETURN
ABSOLUTE_SESSION_GAP
PERCENTAGE_SESSION_GAP
ABSOLUTE_BAR_RANGE
PERCENTAGE_BAR_RANGE
MEAN_VOLUME_BASELINE

## Phase 2B

Normalized market-activity metrics:

RELATIVE_VOLUME
VOLUME_PERCENT_DEVIATION
VOLUME_Z_SCORE
MEAN_PERCENTAGE_RETURN_BASELINE
PERCENTAGE_RETURN_STANDARD_DEVIATION_BASELINE
PERCENTAGE_RETURN_Z_SCORE

## Phase 2C

Short-interest and borrow-derived metrics:

PUBLISHED_SHORT_INTEREST_ABSOLUTE_CHANGE
PUBLISHED_SHORT_INTEREST_PERCENTAGE_CHANGE
PUBLISHED_SHORT_INTEREST_REVISION_DELTA
DAYS_TO_COVER_COMPONENTS
DAYS_TO_COVER
BORROW_FEE_ABSOLUTE_CHANGE
BORROW_FEE_RELATIVE_PERCENTAGE_CHANGE
BORROW_AVAILABILITY_ABSOLUTE_CHANGE
BORROW_AVAILABILITY_PERCENTAGE_CHANGE

## Phase 2D

Cross-domain evidence readiness and alignment:

- Domain coverage
- Input sufficiency
- Availability-age alignment
- Reporting-period alignment
- Conflict summaries
- Missingness summaries
- Operation-specific structural readiness

## Phase 2V

BIYA forensic validation:

- Detection-time evidence
- Frozen original-rule reconstruction
- Original-versus-rebuilt comparisons
- Historical as-of replay
- Rule methodology classifications
- Public validation export
- Static research demonstration

The final BIYA forensic conclusion remains:

OUTCOME_CONFIRMED_METHODOLOGY_UNVERIFIED

## Phase 3A

Deterministic transparent rule-level candidate evaluation.

Categories:

MOMENTUM_DISCOVERY
SHORT_PRESSURE_CONFIRMATION
CATALYST_EVIDENCE
EVIDENCE_VALIDITY

Allowed rule outcomes:

PASS
FAIL
UNKNOWN
CONFLICTED
INSUFFICIENT_DATA
NOT_APPLICABLE

Phase 3A implemented 25 independent rules with:

- Explicit policy versions
- Explicit thresholds
- Threshold provenance
- Supporting evidence IDs
- Supporting metric IDs
- Supporting readiness IDs
- Deterministic identities
- Category summaries containing counts only
- No score
- No rank
- No recommendation
- No Prime/Subprime label

## Phase 3B

Deterministic multi-candidate research evaluation.

Phase 3B provides:

- Immutable candidate case registry
- Frozen Phase 3A result reuse
- Explicit local Phase 3A request execution
- Provisional research detection
- Retrospective outcome labeling
- Immutable research classification
- Deterministic batch execution
- Rule-outcome matrices
- Rule and category frequency summaries
- Missingness summaries
- TP, FP, TN, FN, and unevaluable datasets
- Canonical JSON, JSONL, and CSV exports
- Stable UUIDv5 identities
- No score, rank, recommendation, alert, P&L, or trading field

Phase 3B final HEAD:

e0708f51212ab11fd5767fc55b41b58f4614b44b

Phase 3B verification:

1770 passed
1 skipped
0 failed

Phase 3B case composition:

- 2 completed historical BIYA boundary cases
- 11 synthetic edge cases
- KLRS, LBGJ, SG, TRVI, and SLS explicitly incomplete
- KLOS retained as a conflicting-identity case
- No historical inputs fabricated

---

# 6. Approved Phase 3B policies

Research detection policy:

phase_3b_research_detection_policy.v1

Required rules:

PRICE_RANGE
MARKET_DATA_AVAILABLE
COMPLETED_BAR_AVAILABLE

Resolution:

- All required rules PASS → DETECTED
- Any required rule FAIL → NOT_DETECTED
- Any required rule UNKNOWN, CONFLICTED, INSUFFICIENT_DATA, or NOT_APPLICABLE → UNEVALUABLE

This policy is:

- Explicit
- Provisional
- Unoptimized
- A minimum market-eligibility predicate
- Not a squeeze-confirmation predicate
- Not a momentum-confirmation predicate
- Not a recommendation

Outcome-label policy:

phase_3b_outcome_label_policy.v1

Reference-price policy:

first eligible trade-bar close at or after the detection boundary

Fixed horizon:

24_HOURS

Thresholds:

- Upward: +25%
- Downward: -25%

Resolution:

- Both crossed → MIXED_OR_VOLATILE
- Upward only → SUBSTANTIAL_UPWARD_MOVE
- Downward only → SUBSTANTIAL_DOWNWARD_MOVE
- Complete horizon with neither crossed → NO_SUBSTANTIAL_UPWARD_MOVE
- Partial horizon with neither crossed → OUTCOME_INSUFFICIENT_DATA
- No objective observation → OUTCOME_UNKNOWN

A partial window may establish an observed threshold crossing.

A partial window may not establish that no threshold crossing occurred.

Research classification targets only the configured substantial-upward-move outcome.

Original-platform surfaced status remains independent and never changes research classification.

---

# 7. Phase 3C branch

Create:

phase/3c-descriptive-research-analysis

Suggested command:

git switch -c phase/3c-descriptive-research-analysis

Branch directly from:

e0708f51212ab11fd5767fc55b41b58f4614b44b

Do not continue work on the completed Phase 3B branch after creating Phase 3C.

Do not merge.

Do not push.

Do not rebase completed history.

Do not amend or squash prior commits.

---

# 8. Phase 3C objective

Phase 3C objective:

Design and implement a deterministic descriptive research-analysis layer over the approved Phase 3B datasets that calculates transparent data-quality, coverage, rule-outcome, cohort, and research-classification statistics with explicit denominators, uncertainty intervals, dependence warnings, and sample-size limitations, without optimizing thresholds, assigning predictive importance, creating candidate scores, ranking candidates, generating recommendations, producing alerts, or adding trading logic.

Phase 3C must answer:

- How many historical, synthetic, partial, blocked, and unevaluable cases exist?
- How many unique symbols are represented?
- How many detection boundaries exist per symbol?
- How much of the dataset is duplicated or dependent at the symbol level?
- How often is each Phase 3A rule PASS, FAIL, UNKNOWN, CONFLICTED, INSUFFICIENT_DATA, or NOT_APPLICABLE?
- How much evidence is missing by domain?
- How often are research cases DETECTED, NOT_DETECTED, or UNEVALUABLE?
- How often do configured retrospective outcomes occur?
- How many TP, FP, TN, FN, and unevaluable cases exist?
- Which descriptive rates are mathematically defined?
- Which rates are not meaningful because denominators are zero or sample sizes are too small?
- What changes when analysis is performed by case boundary versus unique symbol?
- What can be reported honestly from the current historical data?
- What cannot be concluded?
- What additional historical evidence is required before predictive validation is attempted?

Phase 3C must not answer:

- Which threshold is best?
- Which rule is most predictive?
- Which candidate should be bought?
- Which candidate ranks highest?
- Which score should be assigned?
- Which rule should be weighted more heavily?
- Which alert should fire?
- What entry or exit should be used?
- What profit could have been made?
- Whether BIYA proves the methodology works
- Whether the system has statistically validated predictive performance

---

# 9. Core analysis boundary

Phase 3C may produce:

- Deterministic cohort summaries
- Dataset composition summaries
- Case-count summaries
- Unique-symbol summaries
- Boundary-count summaries
- Rule-outcome prevalence
- Evidence-missingness prevalence
- Detection-status prevalence
- Outcome-label prevalence
- Research-classification counts
- Confusion-matrix counts
- Descriptive rates
- Explicit numerators and denominators
- Wilson score intervals for supported binomial proportions
- Sample-size sufficiency states
- Dependence and repeated-symbol warnings
- Case-level versus symbol-level comparisons
- Historical-only summaries
- Synthetic-only summaries
- Mixed-provenance warnings
- Machine-readable analysis reports
- Human-readable local Markdown reports
- Deterministic CLI output

Phase 3C must not produce:

- Threshold optimization
- Grid search
- Hyperparameter search
- Rule tuning
- Policy tuning
- Weights
- Composite scores
- Candidate ranking
- Feature importance
- Statistical significance claims
- P-values
- Hypothesis tests
- Causal claims
- Correlation claims presented as predictive evidence
- Regression models
- Machine learning
- Cross-validation
- Backtesting
- P&L
- Trade simulation
- Recommendations
- Alerts
- Live scans
- Permanent provider integrations

---

# 10. Required provenance separation

Never combine these populations silently:

HISTORICAL_CASES
SYNTHETIC_CASES
PARTIAL_OR_BLOCKED_CASES
MIXED_PROVENANCE_CASES

Every analysis must explicitly declare its cohort.

Default report sections should include:

1. Historical completed cases only
2. Historical completed unique-symbol cohort
3. Synthetic cases only
4. All registered cases for data-quality counts
5. Partial and blocked cases
6. Mixed-provenance summary, clearly labeled as non-performance analysis

Synthetic cases exist for contract and branch coverage.

They must never be included in historical performance rates.

Partial, blocked, evaluation-only, outcome-only, and artifact-discovery-only cases must not enter complete-case performance rates.

Do not silently drop them.

Report their exclusion counts and reasons.

---

# 11. Critical dependence problem

The current completed historical dataset contains two BIYA cases representing different detection boundaries for the same symbol.

These are not independent observations.

Phase 3C must explicitly model:

case-level analysis

and

unique-symbol analysis

The default historical performance interpretation must use the unique-symbol cohort.

Case-boundary analysis may still be reported, but it must carry a dependence warning.

Never report two BIYA boundaries as two independent predictive successes.

Create an explicit analysis unit enum such as:

CASE_BOUNDARY
UNIQUE_SYMBOL
UNIQUE_SYMBOL_POLICY_SELECTED_BOUNDARY

For the unique-symbol cohort, do not choose the most favorable boundary.

Use an explicit deterministic boundary-selection policy.

Recommended policy:

earliest_detection_boundary_per_symbol.v1

Requirements:

- Select the earliest eligible detection boundary for each symbol
- Stable tie-breaking
- Explicit policy version
- No outcome-aware selection
- No selection by maximum return
- No selection by favorable classification
- Preserve excluded boundary IDs
- Preserve boundary count per symbol

Also support:

all_case_boundaries.v1

for transparent case-level reporting with dependence warnings.

Do not create a latest-or-best boundary policy.

---

# 12. Cohort contracts

Create immutable contracts such as:

AnalysisCohortType
AnalysisUnit
BoundarySelectionPolicy
AnalysisCohortDefinition
AnalysisCohortMembership
AnalysisCohortExclusion
ResearchAnalysisRequest
ResearchAnalysisResult
SampleSizeAssessment
ProportionEstimate
IntervalEstimate
ConfusionMatrixSummary
RuleOutcomePrevalence
DomainMissingnessSummary
DetectionPrevalenceSummary
OutcomePrevalenceSummary
ClassificationPrevalenceSummary
SymbolDependenceSummary
DataQualitySummary
ResearchLimitation
ResearchAnalysisReport

Use repository conventions.

All models must be frozen and deterministic.

Do not modify Phase 3B models if additive Phase 3C models can solve the need.

---

# 13. Suggested package structure

Prefer an additive package such as:

src/squeeze_core/analysis/
├── __init__.py
├── models.py
├── identifiers.py
├── diagnostics.py
├── cohorts.py
├── boundary_selection.py
├── proportions.py
├── intervals.py
├── confusion_matrix.py
├── rule_prevalence.py
├── missingness.py
├── dependence.py
├── sample_size.py
├── reports.py
├── serialization.py
├── policies.py
└── runner.py

Use actual repository conventions.

Do not create unnecessary files merely to match this suggestion.

Keep:

- Cohort selection separate from metric calculation
- Historical and synthetic analysis separate
- Case-level and symbol-level analysis separate
- Counts separate from interpretation
- Intervals separate from point estimates
- Sample-size assessment separate from observed rates
- Report rendering separate from analysis models
- Phase 3C analysis separate from Phase 3B dataset construction

---

# 14. Analysis request

Create an immutable explicit request.

Suggested fields:

analysis_request_id
analysis_version
source_dataset_id
cohort_definition
analysis_unit
boundary_selection_policy_version
confidence_level
sample_size_policy_version
included_statistics
excluded_statistics
policy_versions
deterministic_id

Requirements:

- Explicit source dataset
- Explicit cohort
- Explicit analysis unit
- Explicit boundary-selection policy
- Explicit confidence level
- Explicit sample-size policy
- No implicit filesystem scan
- No automatic “best” cohort
- No random IDs
- No wall-clock identity input
- No network
- No database
- No hidden outcome-aware filtering

---

# 15. Analysis result

Suggested fields:

analysis_result_id
analysis_version
source_dataset_id
cohort_membership
cohort_exclusions
case_count
unique_symbol_count
boundary_count
symbol_dependence_summary
data_quality_summary
rule_outcome_prevalence
domain_missingness_summary
detection_prevalence
outcome_prevalence
classification_prevalence
confusion_matrix
descriptive_rates
sample_size_assessments
limitations
diagnostics
deterministic_id

Do not include:

- Candidate score
- Candidate rank
- Rule importance score
- Threshold recommendation
- Trade recommendation
- Alert priority
- Expected return
- P&L
- Confidence that a squeeze will occur

---

# 16. Descriptive statistics policy

Create:

phase_3c_descriptive_statistics_policy.v1

Allowed statistics:

- Integer counts
- Exact fractions
- Decimal proportions
- Percentages derived from explicit numerators and denominators
- Minimum
- Maximum
- Median when appropriate
- Arithmetic mean only for clearly defined descriptive numeric fields
- Rule-outcome frequency
- Missingness frequency
- Cohort composition
- Confusion-matrix counts
- Sensitivity/recall
- Specificity
- Positive predictive value
- Negative predictive value
- False-positive rate
- False-negative rate
- Detection prevalence
- Outcome prevalence
- Evaluability rate
- Coverage rate
- Wilson score confidence intervals for binomial proportions

Forbidden statistics:

- P-values
- Hypothesis tests
- Correlation coefficients presented as predictive evidence
- Regression coefficients
- Feature importance
- Information gain
- ROC-AUC
- PR-AUC
- F1 optimization
- Threshold search
- Youden index
- Sharpe ratio
- Profit factor
- Expected value
- Simulated return
- Kelly sizing
- Any trading performance statistic

Do not add a metric merely because it is common in machine learning.

The current sample is too small for predictive-performance claims.

---

# 17. Proportion and denominator policy

Every proportion must preserve:

numerator
denominator
exact_fraction
decimal_value
percentage_value
defined
undefined_reason
cohort_id
analysis_unit

Requirements:

- Denominator must be explicit
- Zero denominator must never become zero percent
- Zero denominator must produce an undefined result
- Missing values must not silently enter denominators
- Unevaluable cases must be reported separately
- Every rate must identify whether it is among all cases or evaluable cases
- Exact Decimal serialization
- No floating-point identity instability

Example distinctions:

pass_rate_among_all_cases
pass_rate_among_evaluable_cases
unknown_rate_among_all_cases
detection_rate_among_evaluable_cases
outcome_rate_among_complete_outcomes

Do not use a generic ambiguous field named rate.

---

# 18. Confidence interval policy

Create:

phase_3c_interval_policy.v1

Use:

WILSON_SCORE

Default confidence level:

0.95

Requirements:

- Apply only to binomial proportions
- Preserve numerator and denominator
- Preserve confidence level
- Preserve method
- Preserve lower and upper bounds
- Use deterministic numeric handling
- Clamp bounds to [0, 1]
- Define behavior for numerator = 0
- Define behavior for numerator = denominator
- Define behavior for denominator = 0
- Do not call intervals proof or significance
- Do not imply independence when repeated boundaries share a symbol

For case-boundary cohorts containing repeated symbols:

- Calculate intervals only if requested
- Attach a dependence warning
- Mark the interval as independence_assumption_not_satisfied

For unique-symbol cohorts:

- Mark that the cohort removes repeated symbol boundaries
- Do not claim broader market representativeness

Do not implement bootstrap intervals.

Do not use random sampling.

Do not add SciPy merely for interval calculations.

Use deterministic standard-library-compatible implementation.

---

# 19. Sample-size policy

Create:

phase_3c_sample_size_policy.v1

Suggested assessment states:

NO_OBSERVATIONS
ONE_OBSERVATION
VERY_SMALL
SMALL
LIMITED
DESCRIPTIVE_ONLY
ADEQUATE_FOR_ESTIMATION_NOT_VALIDATION

Use conservative fixed thresholds.

Recommended initial policy:

n = 0:
NO_OBSERVATIONS

n = 1:
ONE_OBSERVATION

n = 2 through 4:
VERY_SMALL

n = 5 through 19:
SMALL

n = 20 through 49:
LIMITED

n = 50 or greater:
DESCRIPTIVE_ONLY

Do not declare any sample size statistically validated during Phase 3C.

The state ADEQUATE_FOR_ESTIMATION_NOT_VALIDATION may remain reserved and unused unless clearly justified.

Each assessment must include:

sample_size
unique_symbol_count
analysis_unit
state
limitations
allowed_interpretation
forbidden_interpretation
policy_version

For the current completed historical unique-symbol cohort, the expected assessment is:

ONE_OBSERVATION

Do not hide this.

---

# 20. Confusion-matrix policy

Create deterministic confusion-matrix counts:

true_positive_count
false_positive_count
true_negative_count
false_negative_count
unevaluable_count

Derived rates may include:

sensitivity
specificity
positive_predictive_value
negative_predictive_value
false_positive_rate
false_negative_rate

Each derived rate must:

- Preserve numerator
- Preserve denominator
- Be undefined when denominator is zero
- Include Wilson interval only when defined
- Include sample-size assessment
- Identify cohort and analysis unit
- Include dependence warning where relevant

Do not call these validated model-performance metrics.

Use wording such as:

descriptive research-classification rate

For the current unique-symbol historical cohort, most rates will be undefined or based on one observation.

That is expected.

Do not invent negatives to complete the matrix.

Do not mix synthetic cases into historical confusion-matrix results.

---

# 21. Rule-outcome prevalence

For each Phase 3A rule, report:

pass_count
fail_count
unknown_count
conflicted_count
insufficient_data_count
not_applicable_count
total_case_count
evaluable_count

Also calculate:

pass_rate_among_all_cases
pass_rate_among_evaluable_cases
fail_rate_among_evaluable_cases
unknown_rate_among_all_cases
conflicted_rate_among_all_cases
insufficient_data_rate_among_all_cases
not_applicable_rate_among_all_cases

Requirements:

- Explicit denominators
- Wilson intervals only for clearly binomial proportions
- Stable rule ordering from Phase 3A policy
- Historical and synthetic cohorts separate
- Case-boundary and unique-symbol cohorts separate
- No rule ranking
- No “best rule”
- No predictive-importance claim
- No threshold recommendation

---

# 22. Outcome-conditioned rule summaries

Phase 3B already provides outcome-conditioned rule counts.

Phase 3C may analyze them descriptively.

For each rule and outcome label, report:

- Outcome-group case count
- Rule-result counts
- Evaluability count
- Pass proportion among evaluable cases
- Unknown proportion among all group cases
- Sample-size assessment
- Dependence warning
- Historical/synthetic provenance

Do not calculate these when the group contains no cases.

Do not compare groups using significance tests.

Do not claim a rule predicts the outcome.

Do not rank rules by observed pass proportion.

---

# 23. Missingness and data-quality analysis

Produce deterministic summaries for:

- Missing published short interest
- Missing short-interest change
- Missing days to cover
- Missing borrow fee
- Missing borrow-fee change
- Missing borrow availability
- Missing borrow-availability change
- Missing float
- Missing percentage-change history
- Missing relative-volume history
- Missing news
- Missing news timestamp
- Missing SEC filing evidence
- Missing corporate-action context
- Missing provider scope
- Conflicted evidence
- Insufficient history
- Partial outcome windows
- Unknown original-platform surfaced status
- Conflicting identity
- Incomplete candidate case
- Multiple boundaries per symbol

For every missingness statistic:

- Preserve count
- Preserve denominator
- Preserve affected case IDs
- Preserve affected symbols
- Preserve cohort
- Preserve analysis unit
- Do not convert missing evidence into failure

This is a central Phase 3C output.

---

# 24. Symbol-dependence analysis

Create an explicit symbol-dependence summary.

Suggested fields:

case_count
unique_symbol_count
symbols_with_multiple_boundaries
repeated_boundary_count
maximum_boundaries_per_symbol
boundary_ids_by_symbol
dependence_detected
independence_assumption_satisfied
recommended_analysis_unit
limitations

For the current historical dataset:

- BIYA has two boundaries
- Case count is two
- Unique symbol count is one
- Independence is not satisfied at case-boundary level
- Recommended analysis unit is unique symbol
- Earliest-boundary policy must select the earliest BIYA boundary

Do not treat this as an error.

Treat it as a documented dependence limitation.

---

# 25. Historical versus synthetic reports

Generate separate deterministic reports:

historical_case_boundary_analysis
historical_unique_symbol_analysis
synthetic_case_analysis
all_registered_case_data_quality_analysis
partial_and_blocked_case_analysis

The main executive research summary must prioritize:

historical_unique_symbol_analysis

The synthetic report must prominently state:

Synthetic cases test software behavior and classification coverage. They do not provide empirical evidence about market performance.

The all-registered report must prominently state:

This report describes registry and data quality. It is not a performance estimate.

---

# 26. BIYA analysis

Phase 3C must report BIYA transparently at both levels.

## Case-boundary analysis

Include:

BIYA_EARLIEST_BOUNDARY
BIYA_LATEST_BOUNDARY

Report:

- Both Phase 3B detection statuses
- Both outcome labels
- Both research classifications
- Rule-outcome patterns
- Missing short-pressure evidence
- Partial-window limitations
- Shared-symbol dependence
- Confirmation that these are not independent cases

## Unique-symbol analysis

Use:

earliest_detection_boundary_per_symbol.v1

Select:

BIYA_EARLIEST_BOUNDARY

Preserve:

- Selected boundary ID
- Excluded later boundary ID
- Selection rationale
- Confirmation that selection was outcome-blind
- One-symbol sample-size assessment
- No validation claim

The report must state:

BIYA demonstrates that the deterministic pipeline can preserve a detected case and a later substantial move without injecting outcome information into the original evaluation. It does not validate squeeze causation or general predictive performance.

Do not call BIYA proof that the methodology works.

---

# 27. Incomplete real symbols

KLRS, LBGJ, SG, TRVI, SLS, and KLOS must remain represented in data-quality analysis.

For each, report:

- Registry status
- Case type
- Platform surfaced status
- Detection-time evidence status
- Evaluation availability
- Outcome availability
- Identity conflicts
- Exclusion reason from complete historical performance analysis
- Required evidence to become analyzable

Do not fabricate missing evaluation or outcome records.

Do not infer that a symbol was not surfaced merely because evidence is absent.

---

# 28. Required diagnostics

Create stable machine-readable diagnostics.

Cohort diagnostics:

ANALYSIS_COHORT_EMPTY
ANALYSIS_COHORT_PARTIAL
ANALYSIS_COHORT_SYNTHETIC_ONLY
ANALYSIS_COHORT_MIXED_PROVENANCE
ANALYSIS_COHORT_EXCLUDED_INCOMPLETE_CASE
ANALYSIS_COHORT_EXCLUDED_BLOCKED_CASE
ANALYSIS_COHORT_EXCLUDED_OUTCOME_UNKNOWN
ANALYSIS_COHORT_EXCLUDED_DUPLICATE_SYMBOL_BOUNDARY

Dependence diagnostics:

ANALYSIS_REPEATED_SYMBOL_DETECTED
ANALYSIS_CASES_NOT_INDEPENDENT
ANALYSIS_BOUNDARY_SELECTION_APPLIED
ANALYSIS_BOUNDARY_SELECTION_AMBIGUOUS

Rate diagnostics:

ANALYSIS_RATE_UNDEFINED_ZERO_DENOMINATOR
ANALYSIS_RATE_VERY_SMALL_SAMPLE
ANALYSIS_RATE_DEPENDENCE_WARNING
ANALYSIS_INTERVAL_NOT_COMPUTED
ANALYSIS_INTERVAL_INDEPENDENCE_ASSUMPTION_UNSATISFIED

Data-quality diagnostics:

ANALYSIS_MISSING_SHORT_PRESSURE_EVIDENCE
ANALYSIS_MISSING_MOMENTUM_HISTORY
ANALYSIS_PARTIAL_OUTCOME_WINDOW
ANALYSIS_PLATFORM_STATUS_UNKNOWN
ANALYSIS_IDENTITY_CONFLICT
ANALYSIS_INSUFFICIENT_HISTORICAL_CASES

Interpretation diagnostics:

ANALYSIS_DESCRIPTIVE_ONLY
ANALYSIS_NO_PREDICTIVE_VALIDATION
ANALYSIS_NO_CAUSAL_INFERENCE
ANALYSIS_SYNTHETIC_CASES_EXCLUDED_FROM_EMPIRICAL_RESULTS
ANALYSIS_THRESHOLD_OPTIMIZATION_NOT_PERFORMED

Do not add trading diagnostics.

---

# 29. Deterministic identity

Every cohort identity should include:

source_dataset_id
cohort_type
analysis_unit
boundary_selection_policy_version
included_case_ids
excluded_case_ids
exclusion_reason_codes
fixture classifications
policy versions

Every proportion identity should include:

metric_name
numerator
denominator
cohort_id
analysis_unit
interval_policy_version
confidence_level
sample_size_policy_version

Every analysis-result identity should include:

analysis_version
source_dataset_id
cohort_id
analysis_unit
boundary_selection_policy_version
statistics_policy_version
interval_policy_version
sample_size_policy_version
result component IDs
limitations codes

Do not include:

- Wall clock
- Random IDs
- Absolute paths
- Credentials
- Unrestricted prose
- Dict or set iteration order
- Outcome-aware boundary selection
- Candidate order unless explicitly policy-relevant

---

# 30. Serialization

Use canonical repository serialization.

Requirements:

- Stable field order
- Stable cohort order
- Stable rule order
- Stable diagnostic order
- Exact Decimal strings
- LF line endings
- Byte-identical repeated output
- Separate Phase 3C serializers and hashes
- No changes to Phase 1–3B serialized bytes
- No locale-specific formatting
- No NaN
- No Infinity
- Explicit undefined values
- Explicit undefined reasons

Do not modify prior manifests.

---

# 31. CLI

Add an offline command:

analyze-research-dataset

Example:

python -m squeeze_core analyze-research-dataset `
  --dataset tests\fixtures\research\phase_3b_research_dataset.json `
  --cohort historical-complete `
  --analysis-unit unique-symbol `
  --boundary-policy earliest_detection_boundary_per_symbol.v1 `
  --statistics-policy phase_3c_descriptive_statistics_policy.v1 `
  --interval-policy phase_3c_interval_policy.v1 `
  --sample-size-policy phase_3c_sample_size_policy.v1 `
  --output build\analysis\phase-3c-historical-unique-symbol.json

Add a local report command:

render-research-analysis-report

Example:

python -m squeeze_core render-research-analysis-report `
  --analysis build\analysis\phase-3c-historical-unique-symbol.json `
  --format markdown `
  --output build\analysis\phase-3c-historical-unique-symbol.md

Optional:

analyze-research-cohorts

to generate all approved standard cohorts in one deterministic command.

Avoid unnecessary command proliferation.

CLI requirements:

- Local inputs only
- Explicit policies
- Explicit cohort
- Explicit analysis unit
- Stable canonical output
- Structured errors
- Nonzero invalid exit
- No network
- No database
- No credentials
- No GUI
- No score
- No rank
- No recommendation
- No alert
- No P&L
- No trading action
- No threshold optimization

---

# 32. Reports

Create deterministic JSON analysis artifacts and deterministic Markdown reports.

Required standard reports:

phase_3c_historical_case_boundary_analysis.json
phase_3c_historical_case_boundary_analysis.md

phase_3c_historical_unique_symbol_analysis.json
phase_3c_historical_unique_symbol_analysis.md

phase_3c_synthetic_case_analysis.json
phase_3c_synthetic_case_analysis.md

phase_3c_all_registered_data_quality_analysis.json
phase_3c_all_registered_data_quality_analysis.md

phase_3c_partial_blocked_case_analysis.json
phase_3c_partial_blocked_case_analysis.md

Each Markdown report must include:

- Scope
- Cohort definition
- Analysis unit
- Included cases
- Excluded cases
- Boundary-selection policy
- Sample-size assessment
- Dependence assessment
- Counts
- Defined rates
- Undefined rates
- Confidence intervals where allowed
- Missingness findings
- Limitations
- Forbidden interpretations
- No recommendation

Do not produce marketing language.

Do not imply system accuracy from one symbol.

---

# 33. Fixtures

Create:

tests/fixtures/analysis/
├── phase_3c_statistics_policy.json
├── phase_3c_interval_policy.json
├── phase_3c_sample_size_policy.json
├── phase_3c_boundary_selection_policy.json
├── phase_3c_analysis_requests.json
├── phase_3c_historical_case_boundary_analysis.json
├── phase_3c_historical_unique_symbol_analysis.json
├── phase_3c_synthetic_case_analysis.json
├── phase_3c_all_registered_data_quality_analysis.json
├── phase_3c_partial_blocked_case_analysis.json
├── phase_3c_historical_unique_symbol_report.md
├── phase_3c_rule_prevalence_summary.json
├── phase_3c_missingness_summary.json
├── phase_3c_symbol_dependence_summary.json
├── phase_3c_confusion_matrix_summary.json
├── expected_phase_3c_analysis_metadata.json
└── phase_3c_fixture_metadata.json

Use existing Phase 3B fixtures by reference where possible.

Do not duplicate large datasets unnecessarily.

Classify fixtures accurately:

SANITIZED_PUBLIC_HISTORICAL_DATA
SANITIZED_LOCAL_ARTIFACT
SYNTHETIC_EDGE_CASE
MIXED_PROVENANCE
DERIVED_DETERMINISTIC_ANALYSIS

---

# 34. Synthetic analysis fixtures

Create deterministic synthetic inputs covering:

1. Zero-case cohort
2. One-case cohort
3. Two independent symbols
4. Two boundaries for one symbol
5. Multiple boundaries with earliest selection
6. Boundary selection tie
7. TP only
8. FP only
9. TN only
10. FN only
11. All unevaluable
12. Zero denominator sensitivity
13. Zero denominator specificity
14. Zero denominator PPV
15. Zero denominator NPV
16. Proportion numerator zero
17. Proportion numerator equals denominator
18. Wilson interval at zero successes
19. Wilson interval at all successes
20. Wilson interval with denominator one
21. Historical and synthetic mixed cohort rejection or warning
22. Partial case exclusion
23. Blocked case exclusion
24. Unknown outcome exclusion
25. Repeated symbol dependence warning
26. Stable case ordering
27. Stable symbol ordering
28. Input-order invariance
29. Policy-version identity change
30. Confidence-level identity change
31. No score field
32. No rank field
33. No recommendation field
34. No P&L field
35. No threshold-search field

Synthetic inputs must not be presented as historical evidence.

---

# 35. Required tests

## Cohort tests

Test:

- Historical completed cohort
- Historical unique-symbol cohort
- Synthetic-only cohort
- All registered cohort
- Partial/blocked cohort
- Mixed provenance
- Empty cohort
- Duplicate case ID
- Duplicate symbol boundaries
- Stable membership ID
- Stable exclusions
- Input-order invariance
- No outcome-aware selection

## Boundary-selection tests

Test:

- Earliest boundary selected
- Later boundary excluded
- Stable tie-breaking
- Missing boundary
- Multiple symbols
- One symbol
- No favorable-outcome selection
- No maximum-return selection
- Stable policy identity

## Proportion tests

Test:

- 0/1
- 1/1
- 1/2
- 2/3
- 0/0 undefined
- Exact numerator
- Exact denominator
- Exact fraction
- Decimal serialization
- Percentage serialization
- Undefined reason
- Stable identity

## Wilson interval tests

Test:

- Zero successes
- All successes
- One observation
- Small denominator
- Typical denominator
- Confidence 0.95
- Unsupported confidence level
- Zero denominator
- Bounds clamped to [0,1]
- Deterministic repeated output
- No random sampling

## Sample-size tests

Test:

- n=0
- n=1
- n=2
- n=4
- n=5
- n=19
- n=20
- n=49
- n=50
- Unique-symbol count preserved
- Analysis unit preserved
- No validation claim

## Confusion-matrix tests

Test:

- TP
- FP
- TN
- FN
- Unevaluable
- Undefined sensitivity
- Undefined specificity
- Undefined PPV
- Undefined NPV
- Defined rates
- Exact denominators
- Wilson intervals
- Dependence warning
- Synthetic exclusion from historical rates

## Rule-prevalence tests

Test:

- Every Phase 3A outcome
- Evaluable denominator
- Zero evaluable denominator
- Case-boundary cohort
- Unique-symbol cohort
- Historical cohort
- Synthetic cohort
- Stable rule order
- No rule rank
- No importance score

## Missingness tests

Test:

- Missing short interest
- Missing days to cover
- Missing borrow fee
- Missing borrow availability
- Missing float
- Missing relative-volume history
- Missing news timestamp
- Missing SEC evidence
- Missing provider scope
- Conflicted evidence
- Insufficient history
- Partial outcome
- Platform status unknown
- Identity conflict
- Stable affected-case IDs

## Dependence tests

Test:

- One case per symbol
- Multiple cases per symbol
- Independence satisfied
- Independence not satisfied
- Recommended unique-symbol analysis
- Boundary count per symbol
- Stable dependence identity

## Report tests

Test:

- JSON report
- Markdown report
- Stable section order
- Included case list
- Excluded case list
- Sample-size warning
- Dependence warning
- Undefined rate rendering
- No predictive-validation claim
- No causal claim
- No recommendation
- Repeated byte-identical output

## Compatibility tests

Test:

- Phase 1 anchors unchanged
- Phase 2A anchors unchanged
- Phase 2B anchors unchanged
- Phase 2C anchors unchanged
- Phase 2D anchors unchanged
- Original Phase 2V anchors unchanged
- Phase 2V amendment anchors unchanged
- Phase 3A anchors unchanged
- Phase 3B anchors unchanged
- Prior CLI outputs unchanged
- Prior public exports unchanged
- Schema remains 1.0.0

---

# 36. Phase 3C anchors

Create:

tests\fixtures\analysis\expected_phase_3c_analysis_metadata.json

Anchor at least:

historical_case_boundary_cohort
historical_unique_symbol_cohort
synthetic_case_cohort
all_registered_case_cohort
partial_blocked_case_cohort
earliest_boundary_selection
biya_symbol_dependence_summary
sample_size_zero
sample_size_one
sample_size_very_small
proportion_zero_of_one
proportion_one_of_one
proportion_one_of_two
proportion_undefined
wilson_zero_success
wilson_all_success
wilson_one_of_two
confusion_matrix_historical_case_boundary
confusion_matrix_historical_unique_symbol
rule_prevalence_historical_case_boundary
rule_prevalence_historical_unique_symbol
rule_prevalence_synthetic
missingness_historical
missingness_all_registered
detection_prevalence_historical
outcome_prevalence_historical
classification_prevalence_historical
biya_case_boundary_analysis
biya_unique_symbol_analysis
historical_case_boundary_report
historical_unique_symbol_report
synthetic_report
all_registered_data_quality_report
partial_blocked_report
phase_3c_cli_output
phase_3c_report_cli_output
mixed_phase_3c_output
serialized_phase_3c_collection

Generate at least twice.

Investigate:

- Unexplained collisions
- Case-order dependence
- Symbol-order dependence
- Rule-order dependence
- Cohort-policy omissions
- Boundary-policy omissions
- Confidence-level omissions
- Sample-size-policy omissions
- Historical/synthetic provenance collisions
- Markdown line-ending instability
- Decimal instability
- Undefined-rate instability

Do not modify prior manifests.

---

# 37. Documentation

Create:

docs\phase-3c-design.md
docs\phase-3c-test-plan.md
docs\phase-3c-cohort-policy.md
docs\phase-3c-boundary-selection-policy.md
docs\phase-3c-descriptive-statistics-policy.md
docs\phase-3c-confidence-interval-policy.md
docs\phase-3c-sample-size-policy.md
docs\phase-3c-dependence-and-duplicate-symbols.md
docs\phase-3c-confusion-matrix-semantics.md
docs\phase-3c-data-quality-analysis.md
docs\phase-3c-biya-analysis.md
docs\phase-3c-progress.md

Add ADRs similar to:

docs\adr\0053-synthetic-cases-are-excluded-from-historical-performance-analysis.md
docs\adr\0054-repeated-symbol-boundaries-are-not-independent-observations.md
docs\adr\0055-earliest-boundary-selection-is-outcome-blind.md
docs\adr\0056-phase-3c-statistics-are-descriptive-only.md
docs\adr\0057-zero-denominator-rates-remain-undefined.md
docs\adr\0058-phase-3c-does-not-optimize-policies-or-thresholds.md

Adjust numbering according to the actual ADR sequence.

Update additively:

README.md
docs\architecture.md
docs\testing-and-validation.md
docs\phase-3b-design.md
docs\phase-3b-research-dataset-contract.md
docs\phase-3b-progress.md

Do not rewrite prior completion reports.

---

# 38. Required interpretation language

Every historical analysis report must state:

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

Do not soften these limitations.

---

# 39. Isolation audit

Verify new deterministic runtime code contains no executable:

- HTTP clients
- FTP clients
- WebSocket clients
- Provider SDKs
- .env reads
- Credential reads
- Token refresh
- Database drivers
- GUI frameworks
- Web frameworks
- Trading APIs
- Order placement
- Random IDs
- Wall-clock identity inputs
- Pandas
- NumPy
- SciPy
- Statsmodels
- Scikit-learn
- ML frameworks
- Sentiment models
- Technical-indicator libraries
- Composite scoring
- Candidate ranking
- Recommendations
- Alerts
- Prime/Subprime
- Buy/sell language
- Threshold search
- Grid search
- Hyperparameter optimization
- Backtesting
- P&L calculations

Tests must remain offline.

Do not treat documentation describing prohibited behavior as executable violations.

Use AST-aware checks where practical.

---

# 40. Compatibility requirements

All Phase 1–3B tests and anchors must remain unchanged.

Schema remains:

1.0.0

Do not modify:

- Phase 1 anchor manifest
- Phase 2A anchor manifest
- Phase 2B anchor manifest
- Phase 2C anchor manifest
- Phase 2D anchor manifest
- Original Phase 2V anchor manifest
- Phase 2V outcome-amendment anchor manifest
- Phase 3A anchor manifest
- Phase 3B anchor manifest
- Prior fixture bytes
- Prior result-model bytes
- Prior dataset bytes
- Prior public-export bytes
- Prior CLI output anchors

Phase 3C must use separate additive models and anchors.

If a shared model must change:

1. Add a failing compatibility test.
2. Prove an additive model cannot solve the need.
3. Preserve prior serialized bytes.
4. Add an ADR.
5. Stop before a breaking change.

---

# 41. Suggested commit sequence

Use focused local commits.

Suggested sequence:

docs: specify phase 3c descriptive research analysis

docs: define phase 3c cohort and boundary policies

feat: add phase 3c analysis contracts

feat: add deterministic cohort construction

feat: add outcome blind boundary selection

feat: add exact proportions and wilson intervals

feat: add sample size assessments

feat: add descriptive confusion matrix analysis

feat: add rule prevalence and missingness analysis

feat: add symbol dependence analysis

feat: add deterministic phase 3c reports

test: add phase 3c biya and synthetic analysis cases

feat: add offline phase 3c cli commands

test: add phase 3c fixtures and deterministic anchors

docs: document phase 3c results and limitations

chore: finalize phase 3c descriptive research analysis

Adjust when justified.

Do not:

- Amend prior commits
- Squash prior history
- Rebase
- Merge
- Push
- Add remotes
- Create one opaque bulk commit

---

# 42. Acceptance criteria

Phase 3C is complete only when:

- Work occurs on phase/3c-descriptive-research-analysis.
- Branch starts from e0708f51212ab11fd5767fc55b41b58f4614b44b.
- Phase 1–3B history remains unchanged.
- Archived repositories remain unchanged.
- Baseline suite passes.
- Design and test plan are committed before runtime implementation.
- Historical and synthetic cohorts remain separate.
- Partial and blocked cases remain explicit.
- Case-boundary and unique-symbol analyses both exist.
- Earliest-boundary selection is deterministic and outcome-blind.
- BIYA boundaries are not treated as independent observations.
- Descriptive statistics preserve explicit numerators and denominators.
- Zero-denominator rates remain undefined.
- Wilson intervals are deterministic.
- Dependence warnings exist.
- Sample-size assessments exist.
- Current historical unique-symbol sample is identified as one observation.
- Confusion-matrix counts exist.
- Derived rates are undefined where denominators are zero.
- Rule-outcome prevalence exists.
- Missingness summaries exist.
- Symbol-dependence summaries exist.
- Historical, synthetic, all-registered, and partial/blocked reports exist.
- Synthetic cases are excluded from historical performance estimates.
- No threshold optimization exists.
- No score exists.
- No rank exists.
- No recommendation exists.
- No alert exists.
- No P&L exists.
- No backtest exists.
- No predictive-validation claim exists.
- No causal squeeze claim exists.
- Phase 3C anchors regenerate byte-identically.
- All prior anchors remain unchanged.
- Full suite passes.
- Working tree is clean.
- No remotes are added.
- Nothing is pushed.
- Nothing is merged.
- Phase 3D is not started.

---

# 43. Final verification

Run the full suite:

.\.venv\Scripts\python.exe -m pytest `
  --basetemp=.pytest-run-phase3c-final

Run dedicated suites:

.\.venv\Scripts\python.exe -m pytest tests\analysis `
  --basetemp=.pytest-run-phase3c-analysis

.\.venv\Scripts\python.exe -m pytest tests\research `
  --basetemp=.pytest-run-phase3c-research

.\.venv\Scripts\python.exe -m pytest tests\evaluation `
  --basetemp=.pytest-run-phase3c-evaluation

.\.venv\Scripts\python.exe -m pytest tests\validation `
  --basetemp=.pytest-run-phase3c-validation

.\.venv\Scripts\python.exe -m pytest tests\readiness `
  --basetemp=.pytest-run-phase3c-readiness

.\.venv\Scripts\python.exe -m pytest tests\metrics `
  --basetemp=.pytest-run-phase3c-metrics

.\.venv\Scripts\python.exe -m pytest tests\compatibility `
  --basetemp=.pytest-run-phase3c-compat

Run the Phase 3C anchor generator at least twice.

Run each standard analysis CLI at least twice and compare bytes.

Run each Markdown report generator at least twice and compare bytes.

Run BIYA case-boundary analysis at least twice.

Run BIYA unique-symbol analysis at least twice.

Verify Git:

git status
git status --short
git branch --show-current
git rev-parse HEAD
git log --oneline --decorate -160
git remote -v
git diff --exit-code
git diff --cached --exit-code
git show phase-1-rc1 --no-patch

Verify all prior manifests against the Phase 3C starting HEAD.

At minimum verify:

tests\fixtures\compatibility\phase_1_anchor_manifest.json
tests\fixtures\metrics\expected_phase_2a_metric_metadata.json
tests\fixtures\metrics\expected_phase_2b_metric_metadata.json
tests\fixtures\metrics\expected_phase_2c_metric_metadata.json
tests\fixtures\readiness\expected_phase_2d_readiness_metadata.json
tests\fixtures\validation\expected_phase_2v_validation_metadata.json
tests\fixtures\validation\outcome_amendment\expected_phase_2v_outcome_metadata.json
tests\fixtures\evaluation\expected_phase_3a_evaluation_metadata.json
tests\fixtures\research\expected_phase_3b_research_metadata.json

Use:

git diff --exit-code `
  e0708f51212ab11fd5767fc55b41b58f4614b44b `
  -- <manifest-path>

Verify archived repositories read-only.

---

# 44. Completion report

At completion, report:

## Repository state

- Repository path
- Branch
- Starting HEAD
- Final HEAD
- Working-tree state
- Remotes
- New commits
- Push status
- Merge status
- Tags
- Phase 3B base confirmation

## Baseline and final verification

- Baseline command
- Baseline totals
- Final command
- Final totals
- Analysis totals
- Research totals
- Evaluation totals
- Validation totals
- Readiness totals
- Metrics totals
- Compatibility totals
- Repeated anchor results
- Repeated CLI results
- Repeated report results

## Policies

Report:

- Statistics policy version
- Interval policy version
- Confidence level
- Sample-size policy version
- Boundary-selection policy version
- Confirmation that policies remain provisional and unoptimized
- Confirmation that no threshold search occurred

## Cohorts

For each standard cohort, report:

- Cohort ID
- Cohort type
- Analysis unit
- Included case count
- Unique-symbol count
- Excluded case count
- Exclusion reasons
- Fixture classifications
- Dependence status
- Sample-size assessment

## BIYA

Report separately:

### Case-boundary analysis

- Two boundary IDs
- Detection statuses
- Outcome labels
- Research classifications
- Dependence warning
- Confirmation that they are not independent observations

### Unique-symbol analysis

- Selected earliest boundary
- Excluded later boundary
- Boundary-selection policy
- Confirmation that selection was outcome-blind
- Sample size of one
- No predictive-validation claim

## Dataset composition

Report:

- Registered case count
- Complete historical case-boundary count
- Complete historical unique-symbol count
- Synthetic case count
- Partial case count
- Blocked case count
- Conflicting-identity count
- Unknown platform-status count

## Confusion matrices

For case-boundary and unique-symbol historical cohorts, report:

- TP
- FP
- TN
- FN
- Unevaluable
- Defined rates
- Undefined rates
- Numerators
- Denominators
- Confidence intervals
- Dependence warnings
- Sample-size warnings

Do not call these validated performance metrics.

## Rule prevalence

For every Phase 3A rule, report:

- Pass count
- Fail count
- Unknown count
- Conflict count
- Insufficient count
- Not-applicable count
- Total denominator
- Evaluable denominator
- Defined rates
- Undefined rates

Do not rank the rules.

## Missingness findings

Report:

- Most frequently unavailable inputs
- Most frequent insufficient-data states
- Most frequent conflicts
- Most affected cases
- Most affected symbols
- Historical versus synthetic differences
- Provider and source limitations

## Dependence findings

Report:

- Symbols with multiple boundaries
- Repeated boundary count
- Independence status
- Recommended analysis unit
- Boundary-selection result

## Reports and exports

Report:

- JSON hashes
- Markdown hashes
- Row or section counts where applicable
- Stable regeneration result
- No sensitive data confirmation

## Anchors

Report every Phase 3C anchor hash.

## Compatibility

Report:

- Schema version
- Phase 1 anchor status
- Phase 2A anchor status
- Phase 2B anchor status
- Phase 2C anchor status
- Phase 2D anchor status
- Original Phase 2V anchor status
- Phase 2V amendment anchor status
- Phase 3A anchor status
- Phase 3B anchor status
- Existing fixture impact
- Existing CLI impact
- Prior test status

## Files changed

Provide a concise grouped tree.

## Deviations

Explain every material departure from this handoff.

## Remaining limitations

State clearly that Phase 3C does not include:

- Threshold optimization
- Rule weighting
- Composite scoring
- Candidate ranking
- Prime/Subprime
- Recommendations
- Alerts
- Entry or exit logic
- P&L
- Portfolio simulation
- Backtesting
- Predictive validation
- Hypothesis testing
- Causal inference
- Permanent live integrations
- Database persistence
- Authentication
- Paper trading
- Live trading
- Machine learning

## Phase decision

State exactly one:

Phase 3C approved.

or:

Phase 3C blocked.

List exact blockers if blocked.

## Recommended next phase

Recommend exactly one next task.

Preferred recommendation if Phase 3C is approved:

Begin Phase 3D by designing and implementing a controlled historical-case acquisition and curation pipeline that expands the number of independent real-symbol cases, preserves point-in-time evidence and provider provenance, prevents outcome leakage, and enforces preregistered inclusion criteria without modifying Phase 3A thresholds or optimizing Phase 3B policies.

Do not begin Phase 3D.

---

# 45. Stop conditions

Stop and report before continuing only when:

- Starting Git state could cause work loss.
- The branch contains unrelated changes.
- Archived repositories would need modification.
- A breaking prior-schema change appears necessary.
- A prior anchor changes unexpectedly.
- Historical and synthetic cases cannot remain separated.
- BIYA boundaries would need to be treated as independent.
- Boundary selection would require outcome awareness.
- Zero-denominator rates would need to be coerced to zero.
- Confidence intervals would require random or nondeterministic computation.
- Threshold optimization becomes necessary.
- Candidate scoring or ranking becomes necessary.
- Statistical claims would exceed available sample support.
- Recommendations, alerts, or trading logic become necessary.
- Phase 3C cannot remain deterministic and offline.

A tiny historical sample is not a blocker.

Undefined rates are not a blocker.

Wide confidence intervals are not a blocker.

A one-symbol unique historical cohort is not a blocker.

These are expected limitations and must remain explicit.

Begin by:

1. Verifying the exact clean Phase 3B checkpoint.
2. Running the 1,770-passed baseline.
3. Creating phase/3c-descriptive-research-analysis.
4. Writing and committing the Phase 3C design and test plan.
5. Defining cohort, boundary-selection, statistics, interval, and sample-size policies.
6. Implementing immutable Phase 3C analysis contracts.
7. Implementing deterministic cohort construction.
8. Implementing outcome-blind earliest-boundary selection.
9. Implementing exact proportions and undefined-rate handling.
10. Implementing Wilson intervals.
11. Implementing sample-size assessments.
12. Implementing confusion-matrix descriptions.
13. Implementing rule-prevalence and missingness analysis.
14. Implementing symbol-dependence analysis.
15. Implementing historical, synthetic, all-registered, and partial/blocked reports.
16. Adding BIYA case-boundary and unique-symbol analyses.
17. Adding CLI, fixtures, tests, anchors, documentation, compatibility, and isolation checks.
18. Running final determinism and compatibility verification.
19. Stopping after the Phase 3C completion report.

Do not begin Phase 3D.

