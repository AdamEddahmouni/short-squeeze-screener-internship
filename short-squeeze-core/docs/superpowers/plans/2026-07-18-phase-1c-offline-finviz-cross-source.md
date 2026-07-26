# Phase 1C Offline Finviz and Cross-Source Evidence Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:test-driven-development to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Normalize local Finviz-shaped screener snapshots and build deterministic point-in-time evidence bundles with existing IBKR borrow observations without conflating semantics or producing strategy output.

**Architecture:** Add one backward-compatible canonical market-snapshot payload, a pure Finviz adapter behind the existing adapter result boundary, and an independent evidence package that selects immutable observations using an explicit point-in-time policy. Reuse canonical serialization, replay ordering, provenance, quality, and hashes.

**Tech Stack:** Python 3.12, Pydantic 2.13.4, pytest 8.4.1, standard-library decimal/date/time/hash/UUID/JSON/CLI APIs.

## Global Constraints

- Remain fully offline; no Finviz/IBKR connections, credentials, environment, HTTP, browser automation, SDKs, databases, GUI, or order APIs.
- Keep schema `1.0.0` and preserve every existing serialized observation and Phase 1A/1B fixture hash.
- Preserve provider, capture, received, and effective timestamp distinctions; capture is only an uncertain placeholder when provider time is absent.
- Keep short-float percentage, borrow fee, and borrow availability separate.
- Preserve conflicts without averaging or choosing a winner.
- Use only `SANITIZED_REPRESENTATIVE_SAMPLE` and `SYNTHETIC_EDGE_CASE` fixture origins.
- Add no strategy, scoring, ranking, recommendation, signal, entry, exit, or trading behavior.
- Follow red-green-refactor, focused commits, full verification, and no push.

---

### Task 1: Additive market-snapshot contract

**Files:**
- Modify: `src/squeeze_core/contracts/enums.py`
- Modify: `src/squeeze_core/contracts/payloads.py`
- Modify: `src/squeeze_core/contracts/observation.py`
- Modify: `src/squeeze_core/contracts/__init__.py`
- Create: `tests/test_market_snapshot_contract.py`
- Create: `docs/adr/0008-provider-neutral-market-snapshot.md`

**Interfaces:**
- Produces `EventType.MARKET_SNAPSHOT`, `PayloadType.MARKET_SNAPSHOT`, `EarningsSession`, and `MarketSnapshotPayload`.
- `MarketSnapshotPayload` exposes nullable descriptive fields and rejects negative numeric values while allowing explicit zero where structurally representable.

- [ ] Write contract tests proving a market snapshot validates, is not a bar, retains `short_float_percent`, round-trips canonically, and leaves old fixture bytes/hashes unchanged.
- [ ] Run `.\.venv\Scripts\python.exe -m pytest tests/test_market_snapshot_contract.py tests/test_fixture_integrity.py -q` and confirm failure because the new enum/payload is absent.
- [ ] Implement the smallest enum, payload, binding, and export additions.
- [ ] Run focused and full tests; confirm the new tests pass and the original 74 tests remain green.
- [ ] Add ADR 0008 and commit `feat: add provider-neutral market snapshot contract`.

### Task 2: Finviz provider model and deterministic parsing

**Files:**
- Create: `src/squeeze_core/adapters/finviz/models.py`
- Create: `src/squeeze_core/adapters/finviz/semantics.py`
- Create: `src/squeeze_core/adapters/finviz/parsing.py`
- Create: `src/squeeze_core/adapters/finviz/__init__.py`
- Modify: `src/squeeze_core/adapters/diagnostics.py`
- Create: `tests/adapters/finviz/test_models_and_parsing.py`

**Interfaces:**
- Produces immutable `FinvizSnapshotRecord`, `PercentageUnit`, `DelayStatus`, and parsing results for price, percentage, quantity, ratio, earnings, and timestamp representations.
- Parsing functions return typed values plus deterministic diagnostic facts; they never use magnitude inference or wall time.

- [ ] Write failing tests for provider schema/type/origin, aliases, prices, all three percentage units, `K/M/B/T` quantities, approximation, ratios, earnings qualifiers, malformed/negative/missing values, and exact raw hashes.
- [ ] Run the focused test and confirm imports fail because the Finviz package is absent.
- [ ] Implement only the supported aliases and pure parsing helpers required by the tests.
- [ ] Run focused tests and refactor shared timestamp handling only if existing IBKR behavior and hashes remain unchanged.
- [ ] Commit `feat: add finviz provider parsing contract`.

### Task 3: Offline Finviz normalization

**Files:**
- Create: `src/squeeze_core/adapters/finviz/normalizer.py`
- Modify: `src/squeeze_core/adapters/finviz/__init__.py`
- Create: `tests/adapters/finviz/test_normalizer.py`

**Interfaces:**
- Produces `normalize_finviz_snapshot_record(record, context) -> NormalizationResult` and `normalize_finviz_snapshot_records(records, context) -> NormalizationResult`.
- One accepted input emits one canonical `MARKET_SNAPSHOT`; partial inputs retain valid fields and diagnostics.

- [ ] Write failing tests for full/partial records, zero versus missing, invalid price with usable fields, provider/capture/received/effective times, unknown delay/freshness, stale thresholds, duplicate hash/ID suppression, and conflicting Finviz records.
- [ ] Run the focused test and confirm the normalization API is missing.
- [ ] Implement raw hashing, quality/provenance construction, timestamp placeholders, field parsing, stable diagnostics, batch duplicate/conflict preservation, and deterministic observation ordering.
- [ ] Run focused, contract, and Phase 1B tests; confirm IBKR outputs are unchanged.
- [ ] Commit `feat: add offline finviz screener normalization`.

### Task 4: Point-in-time evidence models and selection

**Files:**
- Create: `src/squeeze_core/evidence/models.py`
- Create: `src/squeeze_core/evidence/policy.py`
- Create: `src/squeeze_core/evidence/builder.py`
- Create: `src/squeeze_core/evidence/__init__.py`
- Create: `tests/evidence/test_selection_and_coverage.py`

**Interfaces:**
- Produces immutable `PointInTimeEvidencePolicy`, `EvidenceDiagnostic`, `SourceCoverage`, `EvidenceConflict`, and `PointInTimeEvidenceBundle`.
- Produces `build_point_in_time_evidence(symbol, observations, policy) -> PointInTimeEvidenceBundle`.

- [ ] Write failing tests for symbol filtering, future-effective exclusion, received-after-as-of exclusion, bounded skew, stale/delayed/unknown policy, missing domains, stable ordering, unchanged observation serialization, and stable bundle hash.
- [ ] Run the focused test and confirm the evidence package is absent.
- [ ] Implement deterministic selection, coverage, freshness/completeness summaries, diagnostics, canonical serialization, and self-excluding bundle hash.
- [ ] Run focused and replay tests.
- [ ] Commit `feat: add point-in-time cross-source evidence bundles`.

### Task 5: Compatible-field conflict preservation

**Files:**
- Create: `src/squeeze_core/evidence/conflicts.py`
- Modify: `src/squeeze_core/evidence/builder.py`
- Modify: `src/squeeze_core/evidence/__init__.py`
- Create: `tests/evidence/test_conflicts.py`

**Interfaces:**
- Produces deterministic semantic-field extraction and conflict classifications `VALUE_CONFLICT`, `DUPLICATE_CONFLICT`, `TEMPORAL_DIFFERENCE`, and `INCOMPATIBLE_SEMANTICS`.
- Conflict objects retain observation IDs, values, units, sources, effective/received timestamps, and differences without changing observations.

- [ ] Write failing tests for compatible float conflicts, same-provider duplicates, temporal differences, stable IDs/order, incompatible short-float/fee/availability semantics, no averaging, and no winner metadata.
- [ ] Run the focused test and confirm conflict extraction is missing.
- [ ] Implement explicit compatible semantic mappings and deterministic conflict construction.
- [ ] Run focused and evidence tests.
- [ ] Commit `feat: preserve cross-source evidence conflicts`.

### Task 6: Representative fixtures and replay evidence

**Files:**
- Create: `tests/fixtures/providers/finviz/fixture_metadata.json`
- Create: `tests/fixtures/providers/finviz/context.json`
- Create: `tests/fixtures/providers/finviz/representative_cases.json`
- Create: `tests/fixtures/providers/finviz/edge_cases.json`
- Create: `tests/fixtures/evidence/mixed_finviz_ibkr_cases.json`
- Create: `tests/fixtures/evidence/expected_bundle_metadata.json`
- Create: `tests/fixtures/evidence/normalized_point_in_time.jsonl`
- Create: `tests/phase_1c_fixture_builders.py`
- Create: `tests/adapters/finviz/test_provider_fixtures.py`
- Create: `tests/evidence/test_replay_integration.py`

**Interfaces:**
- Produces deterministic normalized Finviz and mixed-source JSONL, strict replay bytes, evidence bundle bytes, and committed SHA-256 metadata.

- [ ] Write failing provenance, required-case, builder-drift, old-hash-stability, strict replay, replay-to-bundle equality, repeated-generation, and isolation tests.
- [ ] Add representative/synthetic cases for all required timestamp, missing/zero, stale/delayed, future, duplicate, conflict, exchange, symbol, and mixed-source scenarios.
- [ ] Implement the deterministic builder and generate derived artifacts twice.
- [ ] Record exact raw, observation, JSONL, replay, and bundle hashes only after byte-identical repeated runs.
- [ ] Commit `test: add finviz and mixed evidence fixtures`.

### Task 7: Offline CLI

**Files:**
- Modify: `src/squeeze_core/__main__.py`
- Modify: `tests/test_cli.py`

**Interfaces:**
- Extends `normalize-provider --provider finviz` and adds `build-evidence --input PATH --symbol SYMBOL --as-of TIMESTAMP` with optional local policy input.

- [ ] Write failing success/rejection/local-only/stable-output tests for Finviz normalization and evidence construction.
- [ ] Extend argparse and routing without changing existing validate/replay/IBKR output.
- [ ] Run CLI tests and representative commands.
- [ ] Commit `feat: extend cli for evidence bundle generation`.

### Task 8: Documentation and final verification

**Files:**
- Create: `docs/providers/finviz-offline-normalization.md`
- Create: `docs/cross-source-evidence.md`
- Create: `docs/point-in-time-evidence-policy.md`
- Create: `docs/adr/0009-cross-source-evidence-without-scoring.md`
- Create: `docs/adr/0010-conflict-preservation.md`
- Create: `docs/phase-1c-progress.md`
- Modify: `README.md`
- Modify: `docs/architecture.md`
- Modify: `docs/adapter-contract.md`
- Modify: `docs/field-semantics.md`
- Modify: `docs/testing-and-validation.md`

**Interfaces:**
- Documents exact aliases, units, time/freshness behavior, fixture provenance, evidence policy, conflict semantics, commands, hashes, discrepancy, and limitations.

- [ ] Update documentation from implemented behavior and record the absent Phase 1B `docs/point-in-time-normalization.md` discrepancy.
- [ ] Run the complete pytest suite and all documented validate/replay/normalize/build commands.
- [ ] Regenerate deterministic artifacts twice and compare bytes/hashes; verify old Phase 1A/1B hashes.
- [ ] Scan the clean core for credential assignments, `.env`, network/HTTP/browser/SDK/database/order/GUI/wall-clock dependencies and prohibited strategy output.
- [ ] Verify all archived repositories remain clean and unchanged.
- [ ] Commit `docs: document finviz and cross-source evidence`.
- [ ] Verify branch, HEAD, log, remotes, and clean tree; do not push and do not begin Phase 1D.
