# Phase 3D Historical Case Acquisition Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Build a controlled, offline, deterministic historical-case acquisition and curation pipeline with point-in-time provenance, preregistered eligibility, frozen detection boundaries, and outcome-leakage prevention.

**Architecture:** Add `squeeze_core.acquisition` as a separate layer over unchanged Phase 3A–3C contracts. Explicit manifests feed immutable provenance, artifact, identity, eligibility, boundary, leakage, curation, migration, and publication components; canonical serializers and fixed reports expose reviewable outputs.

**Tech Stack:** Python 3.12, Pydantic 2 frozen models, UUIDv5, SHA-256, standard library, pytest, and existing canonical JSON utilities.

## Global Constraints

- Branch is `phase/3d-historical-case-acquisition` from `14d35abfc9aacc6f2f4adaa3ad264950ec556d17`.
- Schema remains `1.0.0`; Phase 1–3C contracts, manifests, fixtures, exports, and serialized bytes remain unchanged.
- Inputs are explicit local paths; runtime and tests are offline and deterministic.
- Outcomes remain inaccessible until plan, boundary, Phase 3A request, and Phase 3A result are frozen.
- Missing historical evidence is never fabricated and current values never silently substitute for historical values.
- No threshold changes, optimization, scoring, ranking, recommendations, alerts, backtesting, profit-and-loss calculations, trading action, or Phase 3E work.

---

### Task 1: Contracts, policies, and identities

**Files:** Create `src/squeeze_core/acquisition/{__init__,models,identifiers,diagnostics,policies}.py`, policy JSON documents, and `tests/acquisition/test_{models,identifiers,policies}.py`.

**Interfaces:** Produces all Phase 3D enums and frozen contracts, `deterministic_acquisition_id`, exact policy loaders, and canonical diagnostics.

- [ ] Write failing tests for frozen models, extra-field rejection, canonical tuples, plan-state rules, policy versions, stable UUIDv5 identities, path independence, and semantic identity changes.
- [ ] Run the focused tests and confirm failures are caused by the absent acquisition package.
- [ ] Implement the minimal contracts, validators, identity function, and exact policy loaders.
- [ ] Run focused tests green and commit `feat: add phase 3d acquisition contracts and policies`.

### Task 2: Artifact manifests and provider provenance

**Files:** Create `artifacts.py`, `manifests.py`, `normalization.py`, and artifact/provenance tests.

**Interfaces:** Produces explicit manifest validation, file verification, duplicate detection, and derived-artifact separation.

- [ ] Write failing tests for hashes, lengths, media types, relative paths, missing and duplicate artifacts, restricted classification, time dimensions, provider scope, revisions, and historical/current distinction.
- [ ] Verify RED, implement minimal validation without modifying sources, verify GREEN, and commit `feat: add deterministic artifact provenance`.

### Task 3: Identity, sufficiency, eligibility, and boundary freeze

**Files:** Create `identity_resolution.py`, `eligibility.py`, `boundary_freeze.py`, and focused tests.

**Interfaces:** Produces outcome-blind identity resolution, evidence sufficiency, eligibility decisions, and frozen boundaries.

- [ ] Write failing tests for all identity states, corporate-action risks, every exclusion code, missing evidence semantics, four permitted boundary rules, ties, ambiguity, and outcome-aware rejection.
- [ ] Verify RED, implement minimal deterministic functions, verify GREEN, and commit `feat: add outcome blind case qualification`.

### Task 4: Leakage guards and curation lifecycle

**Files:** Create `leakage_guards.py`, `curation.py`, `review.py`, and lifecycle/leakage tests.

**Interfaces:** Produces leakage audits, publication blocking, monotonic bundle transitions, append-only ledgers, and stable resume.

- [ ] Write failing tests for every prohibited flow, freeze ordering and hashes, separate outcome manifests, plan mutation, lifecycle transitions, retained rejected attempts, and input-order invariance.
- [ ] Verify RED, implement minimal audit and lifecycle logic, verify GREEN, and commit `feat: add leakage guards and acquisition ledger`.

### Task 5: Migration and Phase 3B publication adapter

**Files:** Create `migration.py`, `publication.py`, and migration/publication tests.

**Interfaces:** Produces BIYA and incomplete-case bundles plus unchanged Phase 3B registry/dataset candidates.

- [ ] Write failing migration tests for BIYA primary/dependent boundaries and KLRS, LBGJ, SG, TRVI, SLS, and KLOS limitations.
- [ ] Write failing adapter tests for registry-only, dataset-ready, synthetic, dependent, and leakage-blocked cases and unchanged Phase 3B serialization.
- [ ] Implement minimally, verify GREEN, and commit `feat: add phase 3b acquisition publication adapter`.

### Task 6: Serialization, runner, CLI, reports, and fixtures

**Files:** Create `serialization.py`, `runner.py`, `reports.py`, update `src/squeeze_core/__main__.py`, and create the required acquisition fixtures and tests.

**Interfaces:** Produces canonical collections, four explicit-input commands, deterministic Markdown, batch summaries, and anchor metadata.

- [ ] Write failing tests for canonical ordering, structured CLI errors, no implicit scanning, repeat bytes, required report language, fixtures, and anchors.
- [ ] Implement minimal serializers, orchestration, parser handlers, reports, fixture generator, and fixtures.
- [ ] Run generators and commands twice, compare bytes, run the acquisition suite, and commit `feat: add offline phase 3d acquisition outputs`.

### Task 7: Documentation, isolation, and compatibility

**Files:** Create the required Phase 3D docs and ADRs; update README, architecture, testing, and Phase 3C docs additively; create isolation and compatibility tests.

**Interfaces:** Documents policy and operation and proves Phase 1–3C remain unchanged.

- [ ] Write failing AST isolation and compatibility tests before any needed guard implementation.
- [ ] Add all policy, workflow, migration, publication, and progress documentation plus ADRs 0059–0065.
- [ ] Verify Phase 1–3C bytes against the Phase 3C base, run every required focused suite and the full suite, verify repository and archive state, and commit `chore: finalize phase 3d controlled acquisition`.

### Task 8: Completion gate

**Files:** No new runtime scope.

- [ ] Use the verification-before-completion and finishing-a-development-branch workflows.
- [ ] Confirm no remotes, pushes, merges, Phase 3E work, or prohibited functionality.
- [ ] Report repository state, all test totals, plan, artifacts, ledger, leakage, migrations, publication candidates, output hashes, anchors, compatibility, deviations, limitations, exact phase decision, and exactly one recommended next task.
