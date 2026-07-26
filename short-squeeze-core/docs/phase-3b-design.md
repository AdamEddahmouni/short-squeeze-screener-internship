# Phase 3B Design: Deterministic Multi-Candidate Research Evaluation

## Boundary

Phase 3B applies the unchanged Phase 3A policy to explicit registered candidate cases,
then attaches retrospective labels in a separate research layer. It produces stable
case results, matrices, descriptive frequency summaries, classification-specific
datasets, and JSON, JSONL, and CSV exports.

Phase 3B does not produce a composite score, weighted sum, candidate rank,
Prime/Subprime label, recommendation, alert, entry or exit, P&L, portfolio simulation,
threshold optimization, statistical validation, or trading action. Schema version
remains `1.0.0`; all Phase 1-3A contracts and serialized bytes remain unchanged.

## Architecture

The additive `squeeze_core.research` package uses an artifact-first hybrid runner:

1. An immutable registry names explicit cases and explicit local artifact paths.
2. A case with a Phase 3A request invokes the existing `evaluate_candidate` function;
   a case with a frozen Phase 3A result deserializes and verifies that result.
3. The Phase 3A result is complete before research detection is evaluated.
4. A separate retrospective observation is labeled under the outcome policy.
5. An immutable truth table combines research detection and outcome label.
6. Aggregators build matrices, summaries, and datasets from completed case results.

The layers remain structurally separate:

`CANDIDATE_DETECTION_RECORD -> PHASE_3A_RULE_EVALUATION -> RETROSPECTIVE_OUTCOME_OBSERVATION -> RESEARCH_CASE_CLASSIFICATION -> DATASET_AGGREGATION`

Outcome observations never enter a Phase 3A request. Original-platform surfaced status
is retained for comparison but is not an input to research detection or classification.

## Contracts

All contracts are frozen Pydantic models with `extra="forbid"`. Additive enums cover
candidate case type and completeness status, original-platform status, detection
status, outcome label, research classification, fixture classification, ordering
policy, and stable diagnostic codes.

The registry entry records explicit case identity, symbol, asset class, case type and
status, detection evidence, `evaluation_as_of`, Phase 3A request/result paths, outcome
path, artifact and dataset IDs, policy version, limitations, and fixture classification.
Paths are input locators only and never enter deterministic identities or public rows.
Registry validation rejects duplicate case IDs, duplicate semantic identities,
unsupported policies, and undeclared paths.

`CandidateResearchCase` retains all 25 Phase 3A rule results, supporting evaluation and
outcome IDs, detection result, outcome label result, original-platform status,
limitations, diagnostics, quality, and deterministic ID. Incomplete registered cases
produce explicit skipped/partial case records and batch diagnostics; missing data is
never converted to a negative result.

## Research detection policy

Policy `phase_3b_research_detection_policy.v1` is provisional and unoptimized. Its
required rules are exactly:

- `PRICE_RANGE`
- `MARKET_DATA_AVAILABLE`
- `COMPLETED_BAR_AVAILABLE`

All three `PASS` produces `DETECTED`. Any required `FAIL` produces `NOT_DETECTED`.
Any required `UNKNOWN`, `CONFLICTED`, `INSUFFICIENT_DATA`, or `NOT_APPLICABLE` produces
`UNEVALUABLE`. The detection result preserves the required Phase 3A rule-result IDs
and diagnostics. The policy has no weights, points, rates, score, rank, recommendation,
or alert semantics and is applied identically to every evaluated case.

## Outcome-label policy

Policy `phase_3b_outcome_label_policy.v1` is provisional and unoptimized. It uses
`first_eligible_trade_bar_close_at_or_after_boundary.v1`, a fixed `24_HOURS` horizon,
an upward threshold of `25%`, and a downward threshold of `-25%`.

Label precedence is deterministic:

1. Both thresholds directly observed: `MIXED_OR_VOLATILE`.
2. Upward threshold only: `SUBSTANTIAL_UPWARD_MOVE`.
3. Downward threshold only: `SUBSTANTIAL_DOWNWARD_MOVE`.
4. Complete horizon with neither: `NO_SUBSTANTIAL_UPWARD_MOVE`.
5. Partial horizon with neither: `OUTCOME_INSUFFICIENT_DATA`.
6. No objective observation: `OUTCOME_UNKNOWN`.

Threshold equality counts as crossing. Partial coverage may prove a directly observed
crossing but may never prove that no crossing occurred. Each result preserves reference
price and policy, boundary, horizon, favorable and adverse extrema, completeness,
supporting observation IDs, limitations, and deterministic identity. It contains no
trade or causal field.

## Research classification

The immutable truth table is:

| Detection | Outcome | Classification |
| --- | --- | --- |
| `DETECTED` | `SUBSTANTIAL_UPWARD_MOVE` | `TRUE_POSITIVE` |
| `DETECTED` | `NO_SUBSTANTIAL_UPWARD_MOVE` | `FALSE_POSITIVE` |
| `NOT_DETECTED` | `SUBSTANTIAL_UPWARD_MOVE` | `FALSE_NEGATIVE` |
| `NOT_DETECTED` | `NO_SUBSTANTIAL_UPWARD_MOVE` | `TRUE_NEGATIVE` |
| `UNEVALUABLE` | any | `UNEVALUABLE` |
| any | `OUTCOME_UNKNOWN` | `UNEVALUABLE` |
| any | `OUTCOME_INSUFFICIENT_DATA` | `UNEVALUABLE` |
| any | `MIXED_OR_VOLATILE` | `UNEVALUABLE` |
| any | `SUBSTANTIAL_DOWNWARD_MOVE` | `UNEVALUABLE` |

Original-platform status never changes this mapping. `NOT_APPLICABLE` is reserved for
records outside the research predicate's declared scope, not for missing evidence.

## Batch execution and ordering

The immutable batch request contains explicit case IDs and exact Phase 3A, detection,
outcome, registry, and batch versions. It never scans for cases. Duplicate or unknown
IDs are structured errors. Request-order mode preserves explicit order; canonical mode
sorts by case ID. Sequential execution is used because deterministic throughput is
adequate for the bounded local dataset.

`fail_fast=true` stops on the first invalid case. `fail_fast=false` retains a structured
failed/skipped record and continues. Empty and partial batches are explicit diagnostic
states. Batch identity includes policy versions, registry identity, case IDs, ordering
policy, and case-result IDs; it excludes wall clock, absolute paths, prose, and random
values.

## Matrices, summaries, and datasets

The rule-outcome matrix contains one row per evaluated case and one column per Phase 3A
rule in policy order. Values remain the six textual Phase 3A outcomes; no numeric
encoding implies preference. Rule and category summaries report exact counts and
Decimal rates with numerator and denominator. Outcome-conditioned summaries are
descriptive only. Missingness explicitly covers short interest, days to cover, borrow
fee, borrow availability, float, relative-volume history, news timestamps, SEC filings,
provider scope, conflicts, and insufficient history.

The dataset retains incomplete and unevaluable cases. Deterministic filters produce
true-positive, false-positive, true-negative, false-negative, and unevaluable datasets
in canonical case order. JSON and JSONL use canonical serialization. CSV uses a fixed
column contract, UTF-8, LF endings, Decimal strings, explicit empty cells, and formula
injection protection. No export contains absolute paths, credentials, scores, ranks,
recommendations, alerts, P&L, or trading fields.

## Historical and synthetic cases

BIYA earliest and latest detection boundaries are distinct completed historical cases.
Both reuse their frozen Phase 3A evaluations and their corresponding Phase 2V outcome
observations. Their short-pressure results remain unknown. The 24-hour retained windows
directly cross +25%, so partial coverage is sufficient for the upward label; later
movement does not alter either evaluation.

Additional discovered symbols remain honest artifact-discovery or blocked cases as
specified in `phase-3b-candidate-case-inventory.md`. Synthetic cases cover every
detection, label, classification, missingness, conflict, ordering, and error branch and
are always marked `SYNTHETIC_EDGE_CASE`.

## Diagnostics and failure behavior

Stable `RESEARCH_CASE_*`, `RESEARCH_DETECTION_*`, `RESEARCH_OUTCOME_*`,
`RESEARCH_BATCH_*`, and `RESEARCH_DATASET_*` codes distinguish invalid configuration,
missing evidence, incomplete coverage, skipped cases, small samples, and mixed
provenance. Configuration errors are nonzero CLI failures with canonical structured
errors. Research-data limitations remain rows and diagnostics rather than exceptions
unless the registry or policy itself is invalid.

## CLI and isolation

`build-research-evaluation-batch` accepts an explicit local registry and explicit
policy versions. `export-research-dataset` accepts a completed local batch and one of
`json`, `jsonl`, or `csv`. Both commands are offline, deterministic, and write through
the existing atomic output convention.

The runtime imports no network client, provider SDK, credential or `.env` reader,
database, GUI or web framework, trading API, random identifier, wall-clock identity,
Pandas, NumPy, SciPy, ML library, sentiment model, technical-indicator library, scoring,
ranking, recommendation, or alert implementation.

## Required interpretation limits

Historical cases may be incomplete, and original-platform surfaced status may be
unknown. Outcome confirmation does not prove short-squeeze causation. Rule prevalence
does not prove predictive value. Small samples limit interpretation. Missing
short-pressure evidence may dominate results. Public historical sources may differ
from original providers. Outcome labels and the detection predicate are provisional.
Thresholds are not optimized, and no trading simulation is performed.

## Phase 3C consumer boundary

Phase 3C consumes the immutable registry and dataset described here through separate `squeeze_core.analysis` models. It does not add fields to Phase 3B, reinterpret fixture provenance, or modify Phase 3B serialized bytes. Source registry and dataset IDs remain independent identity inputs.
