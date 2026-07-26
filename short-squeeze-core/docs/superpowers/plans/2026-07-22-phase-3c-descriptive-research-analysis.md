# Phase 3C Descriptive Research Analysis Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Build an offline deterministic Phase 3C analysis layer over explicit Phase 3B dataset and registry artifacts with transparent cohorts, denominators, Wilson intervals, dependence warnings, data-quality summaries, and honest limitations.

**Architecture:** Add `squeeze_core.analysis` without changing Phase 3B contracts or bytes. Cohort construction and outcome-blind boundary selection produce immutable membership; focused calculators consume that membership; the runner composes self-describing results; separate serializers, reports, CLI handlers, fixtures, and compatibility guards expose deterministic artifacts.

**Tech Stack:** Python 3.13, Pydantic v2 frozen models, `Decimal`, UUIDv5, existing canonical JSON utilities, pytest, standard library only for interval arithmetic.

## Global Constraints

- Branch is `phase/3c-descriptive-research-analysis` from `e0708f51212ab11fd5767fc55b41b58f4614b44b`.
- Schema remains `1.0.0`; Phase 1–3B models, fixtures, manifests, serialized bytes, exports, and CLI outputs remain unchanged.
- Historical, synthetic, partial/blocked, and mixed-provenance populations remain explicit and separate.
- `UNIQUE_SYMBOL_POLICY_SELECTED_BOUNDARY` retains one concrete row per symbol; `UNIQUE_SYMBOL` is aggregate-only.
- Wilson `0.95` uses z `1.95996398454005423552`, Decimal precision `50`, `ROUND_HALF_EVEN`, and bound quantization `0.000000000001`.
- Zero denominators remain undefined.
- Synthetic rows never enter historical rates, historical intervals, or empirical interpretation.
- No optimization, scoring, ranking, recommendation, alert, P&L, backtest, predictive-validation claim, causal claim, network, database, credentials, random identity input, or Phase 3D work.

---

### Task 1: Policies, enums, diagnostics, and immutable contracts

**Files:**
- Create: `src/squeeze_core/analysis/__init__.py`
- Create: `src/squeeze_core/analysis/models.py`
- Create: `src/squeeze_core/analysis/diagnostics.py`
- Create: `src/squeeze_core/analysis/policies.py`
- Create: `src/squeeze_core/analysis/policies/*.json`
- Create: `tests/analysis/__init__.py`
- Create: `tests/analysis/test_models.py`
- Create: `tests/analysis/test_diagnostics.py`
- Create: `tests/analysis/test_policies.py`

**Interfaces:** Produces `AnalysisCohortType`, `AnalysisUnit`, `BoundarySelectionPolicy`, `SampleSizeState`, `IntervalMethod`, `AnalysisCohortDefinition`, `AnalysisCohortMembership`, `AnalysisCohortExclusion`, `ResearchAnalysisRequest`, all component/result models, `AnalysisDiagnostic`, and four exact policy loaders.

- [ ] **Step 1: Write failing contract tests**

```python
def test_policy_selected_boundary_is_distinct_from_symbol_aggregate():
    assert AnalysisUnit.UNIQUE_SYMBOL is not AnalysisUnit.UNIQUE_SYMBOL_POLICY_SELECTED_BOUNDARY

def test_request_preserves_source_ids_independently():
    request = request_model(source_dataset_id="dataset", source_registry_id="registry")
    assert request.source_dataset_id == "dataset"
    assert request.source_registry_id == "registry"
```

- [ ] **Step 2: Run RED**

Run: `.\.venv\Scripts\python.exe -m pytest tests\analysis\test_models.py tests\analysis\test_diagnostics.py tests\analysis\test_policies.py --basetemp=.pytest-run-phase3c-task1-red`

Expected: collection fails because `squeeze_core.analysis` does not exist.

- [ ] **Step 3: Implement minimal frozen contracts and policies**

```python
class AnalysisUnit(StrEnum):
    CASE_BOUNDARY = "CASE_BOUNDARY"
    UNIQUE_SYMBOL = "UNIQUE_SYMBOL"
    UNIQUE_SYMBOL_POLICY_SELECTED_BOUNDARY = "UNIQUE_SYMBOL_POLICY_SELECTED_BOUNDARY"

class ResearchAnalysisRequest(BaseModel):
    model_config = ConfigDict(extra="forbid", frozen=True)
    schema_version: str = "1.0.0"
    analysis_version: str = "phase_3c_analysis.v1"
    source_dataset_id: str | None = None
    source_registry_id: str | None = None
    cohort_definition: AnalysisCohortDefinition
    analysis_unit: AnalysisUnit
    boundary_selection_policy_version: str
    statistics_policy_version: str
    interval_policy_version: str
    confidence_level: Decimal
    sample_size_policy_version: str
    included_statistics: tuple[str, ...]
    excluded_statistics: tuple[str, ...]
    deterministic_id: str | None = None
```

Add the complete fields from the approved design for membership, exclusions, proportions, intervals, sample size, dependence, data quality, prevalence, confusion matrices, limitations, and results. Validators sort set-like tuples and forbid incompatible cohort/unit combinations.

- [ ] **Step 4: Run GREEN and commit**

Run the Step 2 command with basetemp `.pytest-run-phase3c-task1-green`.

Commit: `feat: add phase 3c analysis contracts`

### Task 2: Deterministic identities

**Files:**
- Create: `src/squeeze_core/analysis/identifiers.py`
- Create: `tests/analysis/test_identifiers.py`

**Interfaces:** Produces `deterministic_analysis_id(identity: dict[str, Any]) -> str` and component identity builders.

- [ ] **Step 1: Write RED tests for stable IDs, order invariance, policy/source changes, and collisions**

```python
def test_source_ids_are_independent_identity_inputs():
    base = {"source_dataset_id": "d", "source_registry_id": "r"}
    assert deterministic_analysis_id(base) != deterministic_analysis_id({**base, "source_registry_id": "r2"})
```

- [ ] **Step 2: Run RED**

Run: `.\.venv\Scripts\python.exe -m pytest tests\analysis\test_identifiers.py --basetemp=.pytest-run-phase3c-task2-red`

- [ ] **Step 3: Implement canonical UUIDv5 identity**

```python
ANALYSIS_NAMESPACE = UUID("30f77e74-c484-4f73-a651-20f698543c55")

def deterministic_analysis_id(identity: dict[str, Any]) -> str:
    encoded = json.dumps(identity, sort_keys=True, separators=(",", ":"), ensure_ascii=False, default=_identity_default)
    return str(uuid5(ANALYSIS_NAMESPACE, encoded))
```

- [ ] **Step 4: Run GREEN and commit**

Commit: `feat: add deterministic phase 3c identities`

### Task 3: Cohort construction and exclusions

**Files:**
- Create: `src/squeeze_core/analysis/cohorts.py`
- Create: `tests/analysis/helpers.py`
- Create: `tests/analysis/test_cohorts.py`

**Interfaces:** Produces `build_dataset_cohort(request, dataset)` and `build_registry_cohort(request, registry)`.

- [ ] **Step 1: Write RED tests for five standard cohorts, empty/mixed cohorts, duplicates, exclusions, provenance, and input-order invariance**

```python
def test_historical_complete_excludes_every_synthetic_row(dataset):
    membership = build_dataset_cohort(historical_request(), dataset)
    assert membership.included_case_ids == ("BIYA_EARLIEST_BOUNDARY", "BIYA_LATEST_BOUNDARY")
    assert all(item.reason_code == "ANALYSIS_COHORT_EXCLUDED_SYNTHETIC_CASE" for item in membership.exclusions if item.case_id.startswith("SYN_"))
```

- [ ] **Step 2: Run RED**

Run: `.\.venv\Scripts\python.exe -m pytest tests\analysis\test_cohorts.py --basetemp=.pytest-run-phase3c-task3-red`

- [ ] **Step 3: Implement explicit predicate tables**

```python
DATASET_COHORT_PREDICATES = {
    AnalysisCohortType.HISTORICAL_COMPLETED: lambda row: row.case_status is CandidateCaseStatus.COMPLETE and row.fixture_classification is FixtureClassification.SANITIZED_PUBLIC_HISTORICAL_DATA,
    AnalysisCohortType.SYNTHETIC: lambda row: row.fixture_classification is FixtureClassification.SYNTHETIC_EDGE_CASE,
}
```

Registry cohorts preserve every entry and explicit reason. No path scanning or evidence inference is allowed.

- [ ] **Step 4: Run GREEN and commit**

Commit: `feat: add deterministic phase 3c cohorts`

### Task 4: Outcome-blind boundary selection

**Files:**
- Create: `src/squeeze_core/analysis/boundary_selection.py`
- Create: `tests/analysis/test_boundary_selection.py`

**Interfaces:** Produces `select_boundaries(rows, policy) -> BoundarySelectionResult`.

- [ ] **Step 1: Write RED tests for earliest selection, multiple symbols, equal-time case-ID tie, missing time, order invariance, and outcome mutation invariance**

```python
def test_equal_times_are_fully_resolved_by_case_id(rows_at_same_time):
    result = select_boundaries(tuple(reversed(rows_at_same_time)), EARLIEST_POLICY)
    assert result.selected_case_ids == (min(row.case_id for row in rows_at_same_time),)
    assert "ANALYSIS_BOUNDARY_SELECTION_AMBIGUOUS" not in result.diagnostic_codes
```

- [ ] **Step 2: Run RED**

Run: `.\.venv\Scripts\python.exe -m pytest tests\analysis\test_boundary_selection.py --basetemp=.pytest-run-phase3c-task4-red`

- [ ] **Step 3: Implement selection using only `(symbol, evaluation_as_of, case_id)`**

```python
selected = min(symbol_rows, key=lambda row: (row.evaluation_as_of, row.case_id))
```

- [ ] **Step 4: Run GREEN and commit**

Commit: `feat: add outcome blind boundary selection`

### Task 5: Exact proportions and undefined rates

**Files:**
- Create: `src/squeeze_core/analysis/proportions.py`
- Create: `tests/analysis/test_proportions.py`

**Interfaces:** Produces `build_proportion(metric_name, numerator, denominator, context) -> ProportionEstimate`.

- [ ] **Step 1: Write RED tests for `0/1`, `1/1`, `1/2`, `2/3`, `0/0`, invalid counts, Decimal text, and IDs**

```python
def test_zero_denominator_is_undefined():
    value = build_proportion("sensitivity", 0, 0, CONTEXT)
    assert not value.defined
    assert value.decimal_value is None
    assert value.undefined_reason == "ZERO_DENOMINATOR"
```

- [ ] **Step 2: Run RED**

Run: `.\.venv\Scripts\python.exe -m pytest tests\analysis\test_proportions.py --basetemp=.pytest-run-phase3c-task5-red`

- [ ] **Step 3: Implement exact fractions with Decimal division only when denominator is nonzero**

- [ ] **Step 4: Run GREEN and commit**

Commit: `feat: add exact phase 3c proportions`

### Task 6: Wilson intervals

**Files:**
- Create: `src/squeeze_core/analysis/intervals.py`
- Create: `tests/analysis/test_intervals.py`

**Interfaces:** Produces `wilson_score_interval(numerator, denominator, context) -> IntervalEstimate | None`.

- [ ] **Step 1: Write RED tests with precomputed expected twelve-place bounds and unsupported confidence levels**

```python
def test_wilson_one_of_two_uses_fixed_policy_arithmetic():
    interval = wilson_score_interval(1, 2, CONTEXT)
    assert (interval.lower_bound, interval.upper_bound) == (Decimal("0.094531205734"), Decimal("0.905468794266"))
```

- [ ] **Step 2: Run RED**

Run: `.\.venv\Scripts\python.exe -m pytest tests\analysis\test_intervals.py --basetemp=.pytest-run-phase3c-task6-red`

- [ ] **Step 3: Implement fixed-constant Decimal formula**

```python
Z = Decimal("1.95996398454005423552")
QUANTUM = Decimal("0.000000000001")
with localcontext(Context(prec=50, rounding=ROUND_HALF_EVEN)):
    center = (p + z2 / (2 * n)) / denominator_term
    margin = Z * ((p * (1 - p) / n + z2 / (4 * n * n)).sqrt()) / denominator_term
```

- [ ] **Step 4: Run GREEN and commit**

Commit: `feat: add deterministic wilson intervals`

### Task 7: Sample-size assessments

**Files:**
- Create: `src/squeeze_core/analysis/sample_size.py`
- Create: `tests/analysis/test_sample_size.py`

**Interfaces:** Produces `assess_sample_size(sample_size, unique_symbol_count, analysis_unit, policy) -> SampleSizeAssessment`.

- [ ] **Step 1: Write RED parameter tests for `0,1,2,4,5,19,20,49,50` and interpretation text**
- [ ] **Step 2: Run RED**

Run: `.\.venv\Scripts\python.exe -m pytest tests\analysis\test_sample_size.py --basetemp=.pytest-run-phase3c-task7-red`

- [ ] **Step 3: Implement the exact fixed threshold table from the design**
- [ ] **Step 4: Run GREEN and commit**

Commit: `feat: add phase 3c sample size assessments`

### Task 8: Symbol dependence

**Files:**
- Create: `src/squeeze_core/analysis/dependence.py`
- Create: `tests/analysis/test_dependence.py`

**Interfaces:** Produces `summarize_symbol_dependence(rows, analysis_unit) -> SymbolDependenceSummary`.

- [ ] **Step 1: Write RED tests for independent symbols and two BIYA boundaries**

```python
def test_biya_boundaries_are_not_independent(historical_rows):
    result = summarize_symbol_dependence(historical_rows, AnalysisUnit.CASE_BOUNDARY)
    assert result.case_count == 2 and result.unique_symbol_count == 1
    assert result.symbols_with_multiple_boundaries == ("BIYA",)
    assert not result.independence_assumption_satisfied
```

- [ ] **Step 2: Run RED**

Run: `.\.venv\Scripts\python.exe -m pytest tests\analysis\test_dependence.py --basetemp=.pytest-run-phase3c-task8-red`

- [ ] **Step 3: Implement canonical symbol grouping and boundary maps**
- [ ] **Step 4: Run GREEN and commit**

Commit: `feat: add phase 3c symbol dependence analysis`

### Task 9: Confusion matrices and prevalence

**Files:**
- Create: `src/squeeze_core/analysis/confusion_matrix.py`
- Create: `src/squeeze_core/analysis/prevalence.py`
- Create: `tests/analysis/test_confusion_matrix.py`
- Create: `tests/analysis/test_prevalence.py`

**Interfaces:** Produces `build_confusion_matrix(rows, context)`, `build_detection_prevalence`, `build_outcome_prevalence`, and `build_classification_prevalence`.

- [ ] **Step 1: Write RED tests for TP/FP/TN/FN/unevaluable, all zero denominators, defined rates, intervals, and synthetic exclusion**
- [ ] **Step 2: Run RED**

Run: `.\.venv\Scripts\python.exe -m pytest tests\analysis\test_confusion_matrix.py tests\analysis\test_prevalence.py --basetemp=.pytest-run-phase3c-task9-red`

- [ ] **Step 3: Implement count-first composition through `build_proportion`, `wilson_score_interval`, and `assess_sample_size`**
- [ ] **Step 4: Run GREEN and commit**

Commit: `feat: add descriptive confusion matrix analysis`

### Task 10: Rule-outcome prevalence

**Files:**
- Create: `src/squeeze_core/analysis/rule_prevalence.py`
- Create: `tests/analysis/test_rule_prevalence.py`

**Interfaces:** Produces `build_rule_outcome_prevalence(rows, rule_order, context)` and outcome-conditioned summaries.

- [ ] **Step 1: Write RED tests for all six Phase 3A outcomes, both denominators, zero evaluable cases, cohort separation, and stable rule order**
- [ ] **Step 2: Run RED**

Run: `.\.venv\Scripts\python.exe -m pytest tests\analysis\test_rule_prevalence.py --basetemp=.pytest-run-phase3c-task10-red`

- [ ] **Step 3: Implement policy-ordered counters without rank or importance fields**
- [ ] **Step 4: Run GREEN and commit**

Commit: `feat: add phase 3c rule prevalence analysis`

### Task 11: Missingness and registry data quality

**Files:**
- Create: `src/squeeze_core/analysis/missingness.py`
- Create: `tests/analysis/test_missingness.py`
- Create: `tests/analysis/test_registry_quality.py`

**Interfaces:** Produces `build_domain_missingness(rows, context)` and `build_registry_data_quality(entries, context)`.

- [ ] **Step 1: Write RED tests for every required missingness category and KLRS/LBGJ/SG/TRVI/SLS/KLOS**
- [ ] **Step 2: Run RED**

Run: `.\.venv\Scripts\python.exe -m pytest tests\analysis\test_missingness.py tests\analysis\test_registry_quality.py --basetemp=.pytest-run-phase3c-task11-red`

- [ ] **Step 3: Implement explicit rule/domain/diagnostic maps and preserve affected IDs/symbols**
- [ ] **Step 4: Run GREEN and commit**

Commit: `feat: add phase 3c missingness and data quality analysis`

### Task 12: Runner orchestration

**Files:**
- Create: `src/squeeze_core/analysis/runner.py`
- Create: `tests/analysis/test_runner.py`

**Interfaces:** Produces `run_research_analysis(request, dataset=None, registry=None) -> ResearchAnalysisResult` and `build_standard_analysis_requests(dataset, registry)`.

- [ ] **Step 1: Write RED tests for explicit sources, all standard cohorts, source mismatch, mixed empirical rejection, and repeated bytes**
- [ ] **Step 2: Run RED**

Run: `.\.venv\Scripts\python.exe -m pytest tests\analysis\test_runner.py --basetemp=.pytest-run-phase3c-task12-red`

- [ ] **Step 3: Implement orchestration in selection-then-calculation order**

```python
membership = build_cohort(request, dataset=dataset, registry=registry)
selection = apply_boundary_policy(membership.rows, request.boundary_selection_policy_version)
dependence = summarize_symbol_dependence(selection.rows, request.analysis_unit)
return ResearchAnalysisResult(...)
```

- [ ] **Step 4: Run GREEN and commit**

Commit: `feat: add phase 3c analysis runner`

### Task 13: Canonical serialization

**Files:**
- Create: `src/squeeze_core/analysis/serialization.py`
- Create: `tests/analysis/test_serialization.py`

**Interfaces:** Produces `serialize_analysis_model`, `deserialize_analysis_result`, and `serialize_analysis_collection`.

- [ ] **Step 1: Write RED tests for stable order, Decimal strings, LF, undefined values, source IDs, and prohibited keys**
- [ ] **Step 2: Run RED**

Run: `.\.venv\Scripts\python.exe -m pytest tests\analysis\test_serialization.py --basetemp=.pytest-run-phase3c-task13-red`

- [ ] **Step 3: Implement through existing `canonical_json_bytes` without changing shared serialization**
- [ ] **Step 4: Run GREEN and commit**

Commit: `feat: add phase 3c canonical serialization`

### Task 14: Deterministic Markdown reports

**Files:**
- Create: `src/squeeze_core/analysis/reports.py`
- Create: `tests/analysis/test_reports.py`

**Interfaces:** Produces `render_markdown_report(result) -> bytes`.

- [ ] **Step 1: Write RED tests for section order, required historical language, synthetic/all-registry notices, undefined rendering, and terminology bans**
- [ ] **Step 2: Run RED**

Run: `.\.venv\Scripts\python.exe -m pytest tests\analysis\test_reports.py --basetemp=.pytest-run-phase3c-task14-red`

- [ ] **Step 3: Implement fixed ordered sections and explicit limitation templates**
- [ ] **Step 4: Run GREEN and commit**

Commit: `feat: add deterministic phase 3c reports`

### Task 15: BIYA and standard-cohort analysis

**Files:**
- Create: `tests/analysis/test_biya_analysis.py`
- Create: `tests/analysis/test_standard_cohorts.py`

**Interfaces:** Validates Tasks 1–14 against unchanged Phase 3B fixtures.

- [ ] **Step 1: Write RED integration assertions for two dependent boundaries and one earliest selected boundary**
- [ ] **Step 2: Run RED and correct only missing integration behavior**

Run: `.\.venv\Scripts\python.exe -m pytest tests\analysis\test_biya_analysis.py tests\analysis\test_standard_cohorts.py --basetemp=.pytest-run-phase3c-task15-red`

- [ ] **Step 3: Add minimal runner/report integration needed for GREEN**
- [ ] **Step 4: Run GREEN and commit**

Commit: `test: add phase 3c biya and standard cohort analysis`

### Task 16: Offline CLI

**Files:**
- Modify: `src/squeeze_core/__main__.py`
- Create: `tests/analysis/test_cli.py`

**Interfaces:** Adds `analyze-research-dataset` and `render-research-analysis-report`.

- [ ] **Step 1: Write RED tests for explicit local inputs, registry requirement, structured errors, and repeated bytes**
- [ ] **Step 2: Run RED**

Run: `.\.venv\Scripts\python.exe -m pytest tests\analysis\test_cli.py --basetemp=.pytest-run-phase3c-task16-red`

- [ ] **Step 3: Add exact parser options and handlers**

```python
analysis = commands.add_parser("analyze-research-dataset")
analysis.add_argument("--dataset", type=Path)
analysis.add_argument("--case-registry", type=Path)
analysis.add_argument("--cohort", required=True)
analysis.add_argument("--analysis-unit", required=True)
analysis.add_argument("--boundary-policy", required=True)
analysis.add_argument("--statistics-policy", required=True)
analysis.add_argument("--interval-policy", required=True)
analysis.add_argument("--confidence-level", required=True)
analysis.add_argument("--sample-size-policy", required=True)
analysis.add_argument("--output", type=Path, required=True)
```

- [ ] **Step 4: Run GREEN and commit**

Commit: `feat: add offline phase 3c cli commands`

### Task 17: Fixtures, anchors, isolation, compatibility, documentation, and final verification

**Files:**
- Create: `scripts/generate_phase_3c_anchors.py`
- Create: `tests/fixtures/analysis/*`
- Create: `tests/analysis/test_anchors.py`
- Create: `tests/analysis/test_isolation.py`
- Create: `tests/compatibility/test_phase_3c_compatibility.py`
- Create: Phase 3C policy, dependence, confusion-matrix, data-quality, BIYA, progress, and ADR documents required by the handoff
- Modify additively: `README.md`, `docs/architecture.md`, `docs/testing-and-validation.md`, and the three named Phase 3B documents

**Interfaces:** Produces all required fixture/report pairs and anchor names, AST isolation enforcement, unchanged prior-anchor proof, and completion documentation.

- [ ] **Step 1: Write RED anchor, isolation, and compatibility tests**
- [ ] **Step 2: Run RED**

Run: `.\.venv\Scripts\python.exe -m pytest tests\analysis\test_anchors.py tests\analysis\test_isolation.py tests\compatibility\test_phase_3c_compatibility.py --basetemp=.pytest-run-phase3c-task17-red`

- [ ] **Step 3: Implement generator, fixtures, policy docs, ADRs 0053–0058, additive docs, and AST guards**
- [ ] **Step 4: Generate twice and compare SHA-256 for every output**
- [ ] **Step 5: Run focused GREEN**
- [ ] **Step 6: Commit fixture/isolation slice**

Commit: `test: add phase 3c fixtures deterministic anchors and guards`

- [ ] **Step 7: Commit documentation slice**

Commit: `docs: document phase 3c results and limitations`

- [ ] **Step 8: Run every dedicated suite and the full suite using the exact fresh basetemps from `docs/phase-3c-test-plan.md`**
- [ ] **Step 9: Run generators, CLIs, Markdown rendering, and both BIYA analyses twice and compare bytes**
- [ ] **Step 10: Diff all nine prior manifests against `e0708f51212ab11fd5767fc55b41b58f4614b44b`**
- [ ] **Step 11: Verify clean Git state, branch, remotes, tags, merge base, and all three archived repository commits**
- [ ] **Step 12: Record verified totals/hashes in `docs/phase-3c-progress.md`, commit `chore: finalize phase 3c descriptive research analysis`, then rerun completion-critical checks from final HEAD**

## Execution mode

Execute inline in this session with the `executing-plans` skill. Multi-agent dispatch is not used because the user did not request subagents and the active collaboration policy forbids proactive delegation.
