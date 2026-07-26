# Phase 3A Transparent Candidate Evaluation Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Build an offline deterministic framework that reports independent, point-in-time rule outcomes across four categories without scoring or trading semantics.

**Architecture:** Add `squeeze_core.evaluation` beside the anchored Phase 1-2V packages. Frozen contracts and a JSON policy feed category rule functions that reuse existing evidence, metric, and readiness outputs; aggregation adds only category counts and canonical identities.

**Tech Stack:** Python 3.12, Pydantic 2.13.4, pytest 8.4.1, standard library only at runtime.

## Global Constraints

- Work only on `phase/3a-transparent-candidate-evaluation` from `5544cf608abbed7e1508f0bd65dd2a6b5ef66a99`.
- Keep schema `1.0.0` and all Phase 1-2V bytes unchanged.
- Use exactly four rule categories and six outcomes.
- No score, rank, label, recommendation, alert, trading action, network, credentials, database, GUI, ML, or technical indicators.
- Use test-first red-green cycles and focused commits.

---

### Task 1: Frozen contracts and diagnostics

**Files:** Create `src/squeeze_core/evaluation/models.py`, `diagnostics.py`, `identifiers.py`, `serialization.py`; test `tests/evaluation/test_models.py`.

**Interfaces:** Produces `RuleCategory`, `RuleOutcome`, `ThresholdOperator`, `RuleThreshold`, `RuleDefinition`, `RuleEvaluationRequest`, `RuleEvaluationResult`, `CategoryEvaluationSummary`, and `CandidateEvaluationResult`.

- [ ] Write tests asserting exact enums, frozen models, sorted tuples, Decimal bytes, forbidden scoring fields, and stable IDs.
- [ ] Run `python -m pytest tests/evaluation/test_models.py` and observe import failure.
- [ ] Implement the listed models and identity/serialization helpers with canonical JSON.
- [ ] Rerun the test and commit `feat: add phase 3a rule and threshold contracts`.

### Task 2: Versioned policy

**Files:** Create `src/squeeze_core/evaluation/policies.py`, `registry.py`, `policies/phase_3a_transparent_candidate_policy_v1.json`; test `tests/evaluation/test_policy.py`.

**Interfaces:** Produces `load_policy(path)`, `lookup_policy(version)`, and `lookup_rule(policy, rule_id)`.

- [ ] Write failing tests for policy load, explicit thresholds, provenance, stable order, unknown policy/rule, duplicates, and absent scoring fields.
- [ ] Run the focused tests and verify the expected missing-policy failures.
- [ ] Implement strict policy loading and lookups.
- [ ] Rerun and commit `feat: add versioned candidate evaluation policy`.

### Task 3: Selectors and momentum rules

**Files:** Create `selectors.py`, `rules/momentum.py`; test `tests/evaluation/test_momentum.py`.

**Interfaces:** Consumes existing `Observation` and Phase 2A/2B metrics; produces one `RuleEvaluationResult` per momentum rule.

- [ ] Write failing tests for price, percentage return, relative volume, float, domain availability, completed/partial/future bars, scope mismatch, missingness, conflicts, history, and support IDs.
- [ ] Run focused tests and verify missing evaluator failures.
- [ ] Implement selectors through `build_point_in_time_evidence` and metric-name lookup, then comparisons with no hidden thresholds.
- [ ] Rerun and commit `feat: add momentum discovery rules`.

### Task 4: Short-pressure rules

**Files:** Create `rules/short_pressure.py`; test `tests/evaluation/test_short_pressure.py`.

**Interfaces:** Consumes eligible published-short-interest observations and Phase 2C metrics.

- [ ] Write failing coverage for availability, changes, days to cover, borrow values/changes, zero, units, providers, lifecycle, conflicts, insufficient history, and no short-sale-volume substitution.
- [ ] Run focused tests and confirm missing rule functions.
- [ ] Implement the seven rules with explicit non-FAIL missingness.
- [ ] Rerun and commit `feat: add short pressure confirmation rules`.

### Task 5: Catalyst rules

**Files:** Create `rules/catalyst.py`; test `tests/evaluation/test_catalyst.py`.

**Interfaces:** Consumes point-in-time news, SEC filing, and corporate-action observations.

- [ ] Write failing tests for before/after/unknown/withdrawn news, SEC timing, corporate actions, reverse split context, and no direction inference.
- [ ] Run focused tests and confirm missing rule functions.
- [ ] Implement objective presence/timing rules only.
- [ ] Rerun and commit `feat: add catalyst evidence rules`.

### Task 6: Evidence-validity rules

**Files:** Create `rules/evidence_validity.py`; test `tests/evaluation/test_evidence_validity.py`.

**Interfaces:** Consumes Phase 2D coverage, conflict, sufficiency, and readiness results by deterministic ID.

- [ ] Write failing tests for all domain states, temporal/material conflicts, units, provider ambiguity, history, default substitution, and lifecycle eligibility.
- [ ] Run focused tests and confirm missing functions.
- [ ] Implement seven projections without a final readiness state.
- [ ] Rerun and commit `feat: add evidence validity rules`.

### Task 7: Orchestration and aggregation

**Files:** Create `evaluator.py`, `candidate.py`, package `__init__.py`; test `tests/evaluation/test_candidate.py`.

**Interfaces:** Produces `evaluate_candidate(request, policy)` and stable category summaries.

- [ ] Write failing tests for four-category dispatch, six counts, duplicate/unknown rules, input/rule-order invariance, stable bytes/ID, and absent composite fields.
- [ ] Run focused tests and observe missing orchestrator failure.
- [ ] Implement deterministic dispatch and aggregation.
- [ ] Rerun and commit `feat: add deterministic candidate evaluation aggregation`.

### Task 8: BIYA regression fixtures

**Files:** Create `tests/fixtures/evaluation/biya_*` and `tests/evaluation/test_biya.py`.

**Interfaces:** Uses sanitized Phase 2V detection evidence by reference, never outcome data.

- [ ] Write failing boundary tests for missing pressure data, eligible catalyst/context, no look-ahead, distinct IDs, and repeated bytes.
- [ ] Add the smallest sanitized fixture references needed to pass.
- [ ] Run twice and commit `test: add phase 3a biya regression cases`.

### Task 9: Offline CLI

**Files:** Modify `src/squeeze_core/__main__.py`; test `tests/evaluation/test_cli.py`.

**Interfaces:** Adds `build-candidate-evaluation --policy --evidence --symbol --as-of --output [--rule]`.

- [ ] Write failing CLI success/error/determinism/isolation tests.
- [ ] Implement thin local parsing and canonical output.
- [ ] Run twice, compare bytes, and commit `feat: add offline candidate evaluation cli`.

### Task 10: Fixtures and anchors

**Files:** Create synthetic case fixtures, `scripts/generate_phase_3a_evaluation_anchors.py`, manifest, and anchor tests.

- [ ] Write a failing completeness test for every required anchor name.
- [ ] Generate fixtures and anchors; run the generator twice and compare bytes.
- [ ] Investigate collisions/order instability and commit `test: add phase 3a deterministic fixtures and anchors`.

### Task 11: Documentation and mapping

**Files:** Create the required rule/policy/provenance/contract/BIYA/progress/mapping documents and update existing overview documents additively.

- [ ] Add a documentation test or deterministic file-existence/content assertions.
- [ ] Document every implemented rule, threshold, missing/conflict/unit behavior, and original-rule disposition.
- [ ] Run docs/isolation tests and commit `docs: document phase 3a rule semantics and original rule mapping`.

### Task 12: Final compatibility verification

**Files:** Add `tests/evaluation/test_isolation.py` and compatibility assertions; update progress only after evidence exists.

- [ ] Run evaluation, validation, readiness, metrics, compatibility, and full suites with the specified fresh temp directories.
- [ ] Run anchors, CLI, and both BIYA evaluations twice and compare bytes.
- [ ] Verify prior manifests, archived repositories, branch ancestry, no remotes, and a clean tree.
- [ ] Commit `chore: finalize phase 3a transparent candidate evaluation` and stop before Phase 3B.
