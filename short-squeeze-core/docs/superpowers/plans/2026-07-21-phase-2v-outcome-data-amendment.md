# Phase 2V BIYA Outcome-Data Amendment Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Acquire and preserve BIYA historical outcome evidence, normalize it through existing contracts, compute both-boundary retrospective outcomes, and publish a separate deterministic amendment without changing prior Phase 2V evidence.

**Architecture:** Controlled scripts own network/provider access and immutable raw files. Additive network-free validation modules own manifests, normalization orchestration, outcome calculations, amendment conclusions, serialization, and public projection. The original BIYA case and every prior anchor remain untouched.

**Tech Stack:** Python 3.12 standard library, Pydantic 2.13.4, existing `squeeze_core` contracts/adapters/serialization, pytest 8.4.1, static HTML/CSS/JavaScript.

## Global Constraints

Schema remains `1.0.0`. Tests require no network. Both detection boundaries and all fixed windows are evaluated. Raw inputs are immutable and normalized derivatives are separate. No Phase 3A work, score, rank, recommendation, alert, backtest, simulated trade, P&L, permanent live integration, database, authentication, paper trading, or live trading is introduced. Archived repositories and credentials remain byte-for-byte unchanged.

---

### Task 1: Acquisition manifest contract

**Files:** Create `src/squeeze_core/validation/outcome_acquisition.py`; create `tests/validation/test_outcome_acquisition.py`.

**Interfaces:** Produce frozen manifest/result-state models, stable IDs, raw hashing, canonical serialization, and sanitized relative-path validation.

- [ ] Write focused failing tests for success, partial, empty, entitlement, network, unsupported, stable ID/bytes, hash/count/range, explicit parameters/retrieval time, ordering, and secret/path rejection.
- [ ] Run `pytest tests/validation/test_outcome_acquisition.py -q --basetemp=.pytest-run-phase2v-outcome-t1-red` and confirm failures are caused by the missing API.
- [ ] Implement the minimum manifest models, builders, identifiers, and serializers.
- [ ] Run the focused suite with `.pytest-run-phase2v-outcome-t1-green` and confirm it passes.
- [ ] Commit `feat: add historical acquisition manifests and contracts`.

### Task 2: Controlled acquisition tooling

**Files:** Create `scripts/acquisition/acquire_biya_history.py`; create `scripts/acquisition/build_biya_acquisition_manifest.py`; create `tests/validation/test_outcome_acquisition_cli.py`; create `data/acquisition/biya/README.md`.

**Interfaces:** Consume explicit request arguments; write immutable raw bytes plus one manifest per attempt; emit structured failures without secrets.

- [ ] Write failing CLI tests using saved response transports and injected failures.
- [ ] Run the focused red suite and verify expected missing-command failures.
- [ ] Implement explicit argument parsing, no-overwrite writes, provider result mapping, and canonical output.
- [ ] Run focused tests and commit `feat: add controlled biya historical data acquisition`.

### Task 3: Historical normalization

**Files:** Create `src/squeeze_core/validation/outcome_normalization.py`; create `tests/validation/test_outcome_normalization.py`; add amendment fixtures under `tests/fixtures/validation/outcome_amendment/`.

**Interfaces:** Consume manifest/raw records; produce Phase 1 `Observation` objects for supported domains and separate short-sale-volume evidence.

- [ ] Write failing tests for one/five-minute, daily, sessions, timezones, duplicates, conflicts, missing/zero volume, partial/adjustment state, order invariance, IDs, and acquisition linkage.
- [ ] Verify red failures, implement through existing adapters, verify green, and commit `feat: normalize acquired biya historical evidence`.

### Task 4: Boundary outcome calculations

**Files:** Create `src/squeeze_core/validation/outcome_amendment.py`; create `tests/validation/test_outcome_amendment.py`.

**Interfaces:** Produce fixed-policy references and all required window observations for both detection boundaries.

- [ ] Write failing tests for both references, every window, movement shapes, extrema/timing/volume, missing/incomplete data, sessions, partial bars, and split consistency.
- [ ] Verify red failures, implement deterministic calculations without trade semantics, verify green, and commit `feat: add boundary-based retrospective outcome calculations`.

### Task 5: Separate amendment case and conclusion

**Files:** Create `src/squeeze_core/validation/outcome_case.py`; create `tests/validation/test_outcome_case.py`.

**Interfaces:** Consume the immutable original case plus historical outcome/context; produce only the two permitted amendment conclusions.

- [ ] Write failing tests for confirmed, missing, flat, article-only, statement-only, prohibited conclusion states, stable ID, and byte-identical original case.
- [ ] Verify red failures, implement the separate result, verify green, and commit `feat: add outcome confirmation amendment to validation cases`.

### Task 6: Real acquisition, fixtures, and anchors

**Files:** Populate `data/acquisition/biya/`; populate `tests/fixtures/validation/outcome_amendment/`; create `scripts/generate_phase_2v_outcome_anchors.py`; create `tests/validation/test_phase_2v_outcome_anchors.py`.

**Interfaces:** Preserve real sanitized acquisitions where available and accurately label unavailable/synthetic evidence.

- [ ] Execute source-priority acquisition through the explicit retrieval timestamp and inspect every manifest.
- [ ] Normalize supported raw data and classify fixture provenance accurately.
- [ ] Add failing anchor assertions, generate anchors, rerun twice, and compare bytes.
- [ ] Commit `test: add phase 2v outcome amendment fixtures and anchors`.

### Task 7: Deterministic CLI and public projection

**Files:** Modify `src/squeeze_core/__main__.py`; create/modify amendment public-export modules and CLI tests; update `apps/biya-validation-demo/data/biya-case.json`.

**Interfaces:** Add explicit normalization/build commands and a whitelist amendment export.

- [ ] Write failing valid/invalid/determinism/sanitization CLI tests.
- [ ] Implement commands and public projection, run focused tests, and commit `feat: extend candidate validation cli for outcome amendment`.
- [ ] Generate the public export twice, compare bytes, and commit `feat: update deterministic public biya export`.

### Task 8: Research demonstration

**Files:** Modify `apps/biya-validation-demo/index.html`, `app.js`, `styles.css`, and `README.md`; add UI assertions.

**Interfaces:** Render both boundaries, fixed policy, windows, extrema/timing, context, limitations, and conclusion without trading language.

- [ ] Add failing DOM/content assertions.
- [ ] Implement the outcome ledger design with responsive mobile layout, keyboard focus, and reduced-motion support.
- [ ] Build/serve locally, inspect desktop/mobile screenshots, run UI checks, and commit `feat: update biya validation research demonstration`.

### Task 9: Findings documentation

**Files:** Create `docs/phase-2v-biya-outcome-report.md`, `docs/phase-2v-outcome-data-limitations.md`, `docs/phase-2v-outcome-amendment-progress.md`; update the additive documents named in the handoff and `README.md`.

- [ ] Document acquisition facts, both boundaries, all supported windows, context, gaps, unchanged forensic findings, and exact conclusion.
- [ ] Verify documentation assertions and commit `docs: document biya historical outcome findings and limitations`.

### Task 10: Final verification

**Files:** No production changes unless a failing verification first receives a regression test.

- [ ] Run amendment anchors, deterministic processing, and public export twice each; compare exact bytes.
- [ ] Run full, validation, readiness, metrics, and compatibility suites with fresh required base-temp paths.
- [ ] Scan publishable outputs, validate desktop/mobile demo, and check Vercel authentication without initiating login.
- [ ] Verify prior anchors against `232cc7e`, Git status/remotes/history/tag/base, and all archive commits/clean states.
- [ ] Commit only any evidence-backed final documentation correction as `chore: finalize phase 2v outcome data amendment`.

