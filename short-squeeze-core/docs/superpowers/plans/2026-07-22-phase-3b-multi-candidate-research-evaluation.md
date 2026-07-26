# Phase 3B Multi-Candidate Research Evaluation Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Build an offline deterministic runner that reuses Phase 3A evaluations, applies separate research detection and retrospective outcome policies, classifies cases, and exports outcome-labeled research datasets without scoring, ranking, recommendations, alerts, or trading logic.

**Architecture:** Add `squeeze_core.research` as an artifact-first orchestration package. Explicit registry entries resolve frozen Phase 3A results or explicit Phase 3A requests, after which independent detection, outcome, classification, aggregation, and export components produce canonical artifacts. Existing Phase 1-3A contracts and bytes remain untouched.

**Tech Stack:** Python 3.12, Pydantic 2.13.4 frozen models, `Decimal`, standard-library JSON/CSV, existing canonical serialization, pytest 8.4.1.

## Global Constraints

- Schema remains exactly `1.0.0`.
- Detection policy is exactly `phase_3b_research_detection_policy.v1` with `PRICE_RANGE`, `MARKET_DATA_AVAILABLE`, and `COMPLETED_BAR_AVAILABLE`.
- Outcome policy is exactly `phase_3b_outcome_label_policy.v1`, reference policy `first_eligible_trade_bar_close_at_or_after_boundary.v1`, horizon `24_HOURS`, thresholds `+25%` and `-25%`.
- Both policies are provisional, versioned, identical across cases, and unoptimized.
- Preserve all independent Phase 3A rule outcomes and supporting result IDs.
- Outcome data never modifies or enters Phase 3A evaluation inputs.
- Original-platform surfaced status never changes detection or classification.
- No score, weight, points, rank, recommendation, alert, entry, exit, P&L, portfolio simulation, threshold tuning, statistical validation, provider integration, database, authentication, paper trading, live trading, or machine learning.
- Runtime and tests are deterministic, offline, standard-library isolated, and credential-free.
- Do not modify any prior manifest, fixture byte, result model, history, archived repository, remote, or tag.

---

### Task 1: Immutable research contracts and diagnostics

**Files:**
- Create: `src/squeeze_core/research/__init__.py`
- Create: `src/squeeze_core/research/models.py`
- Create: `src/squeeze_core/research/diagnostics.py`
- Create: `src/squeeze_core/research/identifiers.py`
- Test: `tests/research/test_models.py`
- Test: `tests/research/test_diagnostics.py`
- Test: `tests/research/__init__.py`

**Interfaces:**
- Produces: enums and frozen models named in `docs/phase-3b-design.md`, `ResearchDiagnostic`, `ResearchDiagnosticCode`, `deterministic_research_id(identity: dict[str, object]) -> str`, and stable identity helpers.
- Consumes: `AssetClass`, `Quality`, `CandidateEvaluationResult`, `RuleEvaluationResult`, and existing `canonical_hash`/UUID conventions.

- [ ] **Step 1: Write failing model and diagnostic tests**

```python
def test_research_models_are_frozen_and_forbid_trading_fields():
    entry = registry_entry(case_id="CASE-A")
    with pytest.raises(ValidationError):
        entry.case_id = "CASE-B"
    forbidden = {"score", "weight", "rank", "recommendation", "alert", "pnl", "entry", "exit"}
    fields = set().union(*(set(model.model_fields) for model in RESEARCH_MODELS))
    assert forbidden.isdisjoint({field.lower() for field in fields})

def test_diagnostics_sort_by_code_case_rule_field_and_input_ids():
    assert sort_diagnostics(reversed(DIAGNOSTICS)) == EXPECTED_DIAGNOSTICS
```

- [ ] **Step 2: Run tests and verify RED**

Run: `.\.venv\Scripts\python.exe -m pytest tests\research\test_models.py tests\research\test_diagnostics.py --basetemp=.pytest-run-phase3b-task1-red`

Expected: collection fails because `squeeze_core.research` does not exist.

- [ ] **Step 3: Implement the minimal contracts and identity functions**

```python
class DetectionStatus(StrEnum):
    DETECTED = "DETECTED"
    NOT_DETECTED = "NOT_DETECTED"
    UNEVALUABLE = "UNEVALUABLE"

class OutcomeLabel(StrEnum):
    SUBSTANTIAL_UPWARD_MOVE = "SUBSTANTIAL_UPWARD_MOVE"
    NO_SUBSTANTIAL_UPWARD_MOVE = "NO_SUBSTANTIAL_UPWARD_MOVE"
    SUBSTANTIAL_DOWNWARD_MOVE = "SUBSTANTIAL_DOWNWARD_MOVE"
    MIXED_OR_VOLATILE = "MIXED_OR_VOLATILE"
    OUTCOME_UNKNOWN = "OUTCOME_UNKNOWN"
    OUTCOME_INSUFFICIENT_DATA = "OUTCOME_INSUFFICIENT_DATA"

def deterministic_research_id(identity: dict[str, object]) -> str:
    return str(uuid5(RESEARCH_NAMESPACE, canonical_json_bytes(identity).decode("utf-8")))
```

Implement the remaining exact enums and frozen fields from the design, including registry, policy, result, batch, matrix, summary, dataset, and provenance contracts. Validators normalize symbols/UTC and sort only fields whose contract is canonical rather than request-ordered.

- [ ] **Step 4: Run Task 1 tests and verify GREEN**

Run: `.\.venv\Scripts\python.exe -m pytest tests\research\test_models.py tests\research\test_diagnostics.py --basetemp=.pytest-run-phase3b-task1-green`

Expected: all Task 1 tests pass.

- [ ] **Step 5: Commit**

```text
feat: add phase 3b research case contracts
```

### Task 2: Versioned policies, detection, outcome labeling, and classification

**Files:**
- Create: `src/squeeze_core/research/policies.py`
- Create: `src/squeeze_core/research/policies/phase_3b_research_detection_policy_v1.json`
- Create: `src/squeeze_core/research/policies/phase_3b_outcome_label_policy_v1.json`
- Create: `src/squeeze_core/research/detection.py`
- Create: `src/squeeze_core/research/outcomes.py`
- Create: `src/squeeze_core/research/classification.py`
- Test: `tests/research/test_policies.py`
- Test: `tests/research/test_detection.py`
- Test: `tests/research/test_outcomes.py`
- Test: `tests/research/test_classification.py`

**Interfaces:**
- Produces: `load_detection_policy`, `load_outcome_policy`, `evaluate_research_detection(evaluation, policy)`, `label_outcome(observation, policy)`, and `classify_research_case(detection, label)`.
- Consumes: immutable Task 1 contracts and Phase 3A `CandidateEvaluationResult`.

- [ ] **Step 1: Write failing policy and detection tests**

```python
@pytest.mark.parametrize((outcomes, expected), [
    (("PASS", "PASS", "PASS"), "DETECTED"),
    (("PASS", "FAIL", "PASS"), "NOT_DETECTED"),
    (("PASS", "UNKNOWN", "PASS"), "UNEVALUABLE"),
    (("PASS", "CONFLICTED", "PASS"), "UNEVALUABLE"),
    (("PASS", "INSUFFICIENT_DATA", "PASS"), "UNEVALUABLE"),
    (("PASS", "NOT_APPLICABLE", "PASS"), "UNEVALUABLE"),
])
def test_detection_truth_table(outcomes, expected):
    result = evaluate_research_detection(evaluation_with_required_outcomes(outcomes), DETECTION_POLICY)
    assert result.status.value == expected
    assert result.supporting_rule_result_ids
```

- [ ] **Step 2: Run detection tests and verify RED**

Run: `.\.venv\Scripts\python.exe -m pytest tests\research\test_policies.py tests\research\test_detection.py --basetemp=.pytest-run-phase3b-task2a-red`

Expected: imports fail because the policy and detector are missing.

- [ ] **Step 3: Implement exact policy validation and detection precedence**

```python
def evaluate_research_detection(evaluation, policy):
    required = {item.rule_id: item for item in evaluation.rule_results if item.rule_id in policy.required_rule_ids}
    if set(required) != set(policy.required_rule_ids):
        raise ResearchConfigurationError("RESEARCH_DETECTION_REQUIRED_RULE_UNKNOWN")
    outcomes = tuple(required[rule_id].outcome for rule_id in policy.required_rule_ids)
    if any(item is RuleOutcome.FAIL for item in outcomes):
        status = DetectionStatus.NOT_DETECTED
    elif all(item is RuleOutcome.PASS for item in outcomes):
        status = DetectionStatus.DETECTED
    else:
        status = DetectionStatus.UNEVALUABLE
    return build_detection_result(status, required, policy)
```

- [ ] **Step 4: Run detection tests and verify GREEN**

Run the Step 2 command with basetemp `.pytest-run-phase3b-task2a-green`.

Expected: all policy and detection tests pass.

- [ ] **Step 5: Write failing outcome and classification tests**

```python
@pytest.mark.parametrize((up, down, completeness, expected), [
    (Decimal("25"), Decimal("-24.99"), "COMPLETE", "SUBSTANTIAL_UPWARD_MOVE"),
    (Decimal("24.99"), Decimal("-25"), "COMPLETE", "SUBSTANTIAL_DOWNWARD_MOVE"),
    (Decimal("25"), Decimal("-25"), "PARTIAL", "MIXED_OR_VOLATILE"),
    (Decimal("24"), Decimal("-24"), "COMPLETE", "NO_SUBSTANTIAL_UPWARD_MOVE"),
    (Decimal("24"), Decimal("-24"), "PARTIAL", "OUTCOME_INSUFFICIENT_DATA"),
])
def test_outcome_truth_table(up, down, completeness, expected):
    assert label_outcome(outcome(up, down, completeness), OUTCOME_POLICY).label.value == expected

def test_research_classification_is_independent_of_platform_status():
    assert classify_research_case(DETECTED, SUBSTANTIAL_UPWARD).classification is TRUE_POSITIVE
```

- [ ] **Step 6: Run outcome/classification tests and verify RED**

Run: `.\.venv\Scripts\python.exe -m pytest tests\research\test_outcomes.py tests\research\test_classification.py --basetemp=.pytest-run-phase3b-task2b-red`

Expected: imports fail because outcome labeling and classification are missing.

- [ ] **Step 7: Implement approved label precedence and immutable truth table**

```python
def classify_research_case(detection, outcome):
    if detection.status is DetectionStatus.UNEVALUABLE:
        value = ResearchCaseClassification.UNEVALUABLE
    else:
        value = CLASSIFICATION_TABLE.get((detection.status, outcome.label), ResearchCaseClassification.UNEVALUABLE)
    return build_classification_result(detection, outcome, value)
```

Label partial windows positively only when a threshold equality/crossing is observed; otherwise return insufficient. Missing observations return unknown.

- [ ] **Step 8: Run all Task 2 tests and verify GREEN**

Run: `.\.venv\Scripts\python.exe -m pytest tests\research\test_policies.py tests\research\test_detection.py tests\research\test_outcomes.py tests\research\test_classification.py --basetemp=.pytest-run-phase3b-task2-green`

Expected: all Task 2 tests pass.

- [ ] **Step 9: Commit**

```text
feat: add versioned research detection and outcome policies
```

### Task 3: Explicit case registry and artifact loading

**Files:**
- Create: `src/squeeze_core/research/registry.py`
- Create: `src/squeeze_core/research/io.py`
- Test: `tests/research/test_registry.py`
- Test: `tests/research/test_io.py`

**Interfaces:**
- Produces: `load_case_registry(path)`, `resolve_registry_cases(registry, case_ids, ordering_policy)`, `load_phase_3a_result(entry, root)`, and `load_outcome_observation(entry, root)`.
- Consumes: existing Phase 3A deserializer, Phase 2V `BoundaryOutcomeObservation`, Task 1 contracts.

- [ ] **Step 1: Write failing registry tests**

```python
def test_registry_requires_explicit_unique_case_ids_and_never_scans(tmp_path):
    registry = case_registry(entries=(entry("A"), entry("B")))
    assert [item.case_id for item in resolve_registry_cases(registry, ("B", "A"), REQUEST_ORDER)] == ["B", "A"]
    with pytest.raises(ResearchConfigurationError, match="RESEARCH_CASE_DUPLICATE"):
        case_registry(entries=(entry("A"), entry("A")))
```

- [ ] **Step 2: Run registry tests and verify RED**

Run: `.\.venv\Scripts\python.exe -m pytest tests\research\test_registry.py tests\research\test_io.py --basetemp=.pytest-run-phase3b-task3-red`

Expected: missing registry and I/O functions.

- [ ] **Step 3: Implement explicit resolution and root-confined loaders**

Resolve only declared case IDs. Reject absolute paths and normalized paths escaping the registry root. Deserialize frozen Phase 3A results; when an explicit request artifact is supplied, invoke existing Phase 3A evaluation code and verify policy version. Preserve missing artifacts as case diagnostics when status permits them.

- [ ] **Step 4: Run Task 3 tests and verify GREEN**

Run Step 2 with basetemp `.pytest-run-phase3b-task3-green`.

- [ ] **Step 5: Commit**

```text
feat: add explicit phase 3b case registry
```

### Task 4: Deterministic batch runner

**Files:**
- Create: `src/squeeze_core/research/batch.py`
- Test: `tests/research/test_batch.py`

**Interfaces:**
- Produces: `build_research_case(entry, artifacts, policies)` and `run_research_batch(request, registry, root)`.
- Consumes: Tasks 1-3 and existing Phase 3A evaluation functions.

- [ ] **Step 1: Write failing batch tests**

Cover one/multiple cases, both order policies, partial/evaluation-only/outcome-only/artifact-discovery/blocked cases, unknown/duplicate IDs, empty batches, `fail_fast` true/false, repeated bytes, and no outcome-based ordering.

- [ ] **Step 2: Run tests and verify RED**

Run: `.\.venv\Scripts\python.exe -m pytest tests\research\test_batch.py --basetemp=.pytest-run-phase3b-task4-red`

Expected: missing batch runner.

- [ ] **Step 3: Implement sequential deterministic execution**

```python
for entry in resolve_registry_cases(registry, request.case_ids, request.ordering_policy):
    try:
        case_results.append(build_research_case(entry, load_artifacts(entry), policies))
    except ResearchCaseUnavailable as exc:
        if request.fail_fast:
            raise
        skipped_results.append(skipped_case(entry, exc.diagnostics))
return finalize_batch(request, registry, case_results, skipped_results)
```

- [ ] **Step 4: Run Task 4 tests and verify GREEN**

Run Step 2 with basetemp `.pytest-run-phase3b-task4-green`.

- [ ] **Step 5: Commit**

```text
feat: add multi candidate research evaluation runner
```

### Task 5: Rule matrices and descriptive summaries

**Files:**
- Create: `src/squeeze_core/research/matrices.py`
- Create: `src/squeeze_core/research/summaries.py`
- Test: `tests/research/test_matrices.py`
- Test: `tests/research/test_summaries.py`

**Interfaces:**
- Produces: `build_rule_outcome_matrix`, `build_rule_frequency_summary`, `build_outcome_conditioned_summary`, `build_category_frequency_summary`, and `build_missingness_summary`.
- Consumes: batch case results and Phase 3A policy order.

- [ ] **Step 1: Write failing count, ordering, denominator, and missingness tests**

```python
def test_rule_frequency_preserves_exact_counts_and_zero_denominator():
    summary = build_rule_frequency_summary(cases, POLICY)
    row = by_rule(summary, "PRICE_RANGE")
    assert (row.pass_count, row.fail_count, row.evaluable_case_count) == (1, 1, 2)
    assert row.pass_rate_among_evaluable == Decimal("0.5")
```

- [ ] **Step 2: Run tests and verify RED**

Run: `.\.venv\Scripts\python.exe -m pytest tests\research\test_matrices.py tests\research\test_summaries.py --basetemp=.pytest-run-phase3b-task5-red`

- [ ] **Step 3: Implement stable policy-order matrices and exact Decimal summaries**

Use named outcome counters, explicit evaluable denominators (`PASS` plus `FAIL`), `None` for zero-denominator rates, and separate outcome-conditioned groups. Missingness is derived from rule outcomes and diagnostic codes without hiding unevaluable cases.

- [ ] **Step 4: Run Task 5 tests and verify GREEN**

Run Step 2 with basetemp `.pytest-run-phase3b-task5-green`.

- [ ] **Step 5: Commit**

```text
feat: add deterministic research matrices and summaries
```

### Task 6: Dataset construction and canonical exports

**Files:**
- Create: `src/squeeze_core/research/dataset.py`
- Create: `src/squeeze_core/research/serialization.py`
- Test: `tests/research/test_dataset.py`
- Test: `tests/research/test_serialization.py`

**Interfaces:**
- Produces: `build_research_dataset`, `filter_research_dataset`, `serialize_research_json`, `serialize_research_jsonl`, `serialize_research_csv`, and deserializers used by the CLI.
- Consumes: completed/partial batch result and Task 1 dataset contracts.

- [ ] **Step 1: Write failing JSON/JSONL/CSV tests**

Cover stable IDs and columns, exact Decimal text, empty values, LF endings, formula-prefix escaping, canonical filters, provenance counts, no absolute paths/credentials, and forbidden field names.

- [ ] **Step 2: Run tests and verify RED**

Run: `.\.venv\Scripts\python.exe -m pytest tests\research\test_dataset.py tests\research\test_serialization.py --basetemp=.pytest-run-phase3b-task6-red`

- [ ] **Step 3: Implement dataset rows, filters, provenance, and serializers**

```python
CSV_COLUMNS = (
    "dataset_version", "case_id", "symbol", "asset_class", "case_type", "case_status",
    "evaluation_as_of", "phase_3a_policy_version", "research_detection_policy_version",
    "outcome_policy_version", "original_platform_surfaced_status",
    "research_detection_status", "outcome_label", "research_classification",
    "fixture_classification", "row_id",
)
```

Append policy-ordered `<rule_id>_outcome` columns and fixed JSON-string columns for support IDs, missingness, diagnostics, and limitations. Serialize through `csv.writer(..., lineterminator="\n")` and canonical JSON.

- [ ] **Step 4: Run Task 6 tests and verify GREEN**

Run Step 2 with basetemp `.pytest-run-phase3b-task6-green`.

- [ ] **Step 5: Commit**

```text
feat: add deterministic research dataset exports
```

### Task 7: Historical BIYA, incomplete real cases, synthetic coverage, and anchors

**Files:**
- Create: `tests/research/helpers.py`
- Create: `tests/research/test_biya_research_cases.py`
- Create: `tests/research/test_anchors.py`
- Create: `scripts/generate_phase_3b_anchors.py`
- Create: all required `tests/fixtures/research/*` files from the handoff

**Interfaces:**
- Produces: two completed BIYA cases, honest incomplete registered historical cases, synthetic branch coverage, deterministic named anchors, and fixture metadata.
- Consumes: Phase 3A BIYA results and Phase 2V outcome fixtures by reference.

- [ ] **Step 1: Write failing BIYA and anchor tests**

Assert exact Phase 3A IDs, three required passes, unknown short-pressure evidence, upward label under partial-window asymmetry, true-positive classification, no mutation, distinct boundaries, synthetic classification coverage, and all required anchor names.

- [ ] **Step 2: Run tests and verify RED**

Run: `.\.venv\Scripts\python.exe -m pytest tests\research\test_biya_research_cases.py tests\research\test_anchors.py --basetemp=.pytest-run-phase3b-task7-red`

- [ ] **Step 3: Implement fixture generator and generate fixtures twice**

Run twice: `.\.venv\Scripts\python.exe scripts\generate_phase_3b_anchors.py`

Expected: second run produces byte-identical fixtures and metadata. Compare SHA-256 for every generated file.

- [ ] **Step 4: Run Task 7 tests and verify GREEN**

Run Step 2 with basetemp `.pytest-run-phase3b-task7-green`.

- [ ] **Step 5: Commit**

```text
test: add phase 3b biya synthetic fixtures and anchors
```

### Task 8: Offline CLI commands

**Files:**
- Modify: `src/squeeze_core/__main__.py`
- Test: `tests/research/test_cli.py`

**Interfaces:**
- Produces: `build-research-evaluation-batch` and `export-research-dataset` commands.
- Consumes: registry, policies, batch runner, dataset deserializer, and serializers.

- [ ] **Step 1: Write failing deterministic CLI and structured-error tests**

Invoke each command twice, compare output files and stdout, cover JSON/JSONL/CSV, and assert invalid cases return canonical error JSON on stderr with nonzero exit.

- [ ] **Step 2: Run tests and verify RED**

Run: `.\.venv\Scripts\python.exe -m pytest tests\research\test_cli.py --basetemp=.pytest-run-phase3b-task8-red`

- [ ] **Step 3: Add parsers and command handlers**

```python
batch = commands.add_parser("build-research-evaluation-batch")
batch.add_argument("--case-registry", type=Path, required=True)
batch.add_argument("--case-id", action="append", required=True)
batch.add_argument("--phase-3a-policy", required=True)
batch.add_argument("--detection-policy", required=True)
batch.add_argument("--outcome-policy", required=True)
batch.add_argument("--output", type=Path, required=True)
```

Add the export parser with `--batch`, `--format {json,jsonl,csv}`, and `--output`. Use local paths only and existing atomic/canonical write conventions.

- [ ] **Step 4: Run Task 8 tests and verify GREEN**

Run Step 2 with basetemp `.pytest-run-phase3b-task8-green`.

- [ ] **Step 5: Commit**

```text
feat: add offline phase 3b research cli commands
```

### Task 9: Documentation, ADRs, compatibility, and isolation

**Files:**
- Create: policy, classification, matrix, dataset, BIYA, progress documents required by the handoff
- Create: `docs/adr/0049-outcome-labels-remain-separate-from-rule-evaluations.md`
- Create: `docs/adr/0050-research-detection-is-not-candidate-ranking.md`
- Create: `docs/adr/0051-unevaluable-cases-remain-in-the-dataset.md`
- Create: `docs/adr/0052-phase-3b-does-not-optimize-thresholds.md`
- Modify additively: README and six prior architecture/contract documents named in the handoff
- Create: `tests/research/test_isolation.py`
- Create: `tests/compatibility/test_phase_3b_compatibility.py`

**Interfaces:**
- Produces: complete contract documentation and executable guards against forbidden dependencies/fields and prior-anchor changes.

- [ ] **Step 1: Write failing isolation and compatibility tests**

AST-scan `squeeze_core.research`, assert schema `1.0.0`, compare all eight prior manifests to base bytes, and inspect runtime model/serialized keys for prohibited concepts.

- [ ] **Step 2: Run tests and verify RED**

Run: `.\.venv\Scripts\python.exe -m pytest tests\research\test_isolation.py tests\compatibility\test_phase_3b_compatibility.py --basetemp=.pytest-run-phase3b-task9-red`

- [ ] **Step 3: Add documentation and exact guards**

Every research report repeats the eleven limitations from the handoff. Prior docs receive additive Phase 3B references only; prior completion reports and manifests remain unchanged.

- [ ] **Step 4: Run Task 9 tests and verify GREEN**

Run Step 2 with basetemp `.pytest-run-phase3b-task9-green`.

- [ ] **Step 5: Commit**

```text
docs: document phase 3b research semantics and limitations
```

### Task 10: Final deterministic verification and closeout

**Files:**
- Modify: `docs/phase-3b-progress.md` with fresh totals and hashes only

**Interfaces:**
- Produces: clean committed Phase 3B branch and evidence for the completion report.

- [ ] **Step 1: Run the Phase 3B generator, CLIs, exports, and BIYA builds twice**

Compare SHA-256 bytes for anchors, batch JSON, JSON, JSONL, CSV, and both BIYA cases. Investigate every mismatch before continuing.

- [ ] **Step 2: Run dedicated suites**

Run the six exact dedicated commands from the handoff with fresh basetemps and record totals.

- [ ] **Step 3: Run the full suite**

Run: `.\.venv\Scripts\python.exe -m pytest --basetemp=.pytest-run-phase3b-final`

Expected: zero failures; record exact pass/skip totals rather than projecting them.

- [ ] **Step 4: Verify compatibility, Git, remotes, tags, base, and archived repositories**

Run every final Git and prior-manifest command from the handoff. Confirm all archived repositories remain clean at their required commits and no remote exists.

- [ ] **Step 5: Update progress documentation and commit closeout**

```text
chore: finalize phase 3b multi candidate research evaluation
```

- [ ] **Step 6: Re-run completion-critical verification after the final commit**

Re-run full tests, status, diff checks, manifest comparisons, anchor/CLI/export hashes, and archived-repository checks. Only then issue the required completion report and stop before Phase 3C.
