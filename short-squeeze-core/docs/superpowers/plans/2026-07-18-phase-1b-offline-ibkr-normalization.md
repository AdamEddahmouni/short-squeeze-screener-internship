# Phase 1B Offline IBKR Normalization Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:test-driven-development to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Convert sanitized local IBKR borrow records into deterministic Phase 1A observations with explicit point-in-time, quality, provenance, and diagnostic semantics.

**Architecture:** Add immutable provider-neutral result/context models, an IBKR-specific validated record and pure normalizer, and a batch reconciliation layer. Reuse the Phase 1A observation, serialization, and replay contracts without schema changes.

**Tech Stack:** Python 3.12, Pydantic 2.13.4, pytest 8.4.1, standard-library JSON/timezone/hash/CLI APIs.

## Global Constraints

- Offline local objects/files only; no IBKR SDK, network, environment, credentials, database, or order APIs.
- Phase 1B only; no strategy, scoring, indicators, sentiment, GUI, or live-provider behavior.
- Preserve missing versus zero, explicit units, raw-record linkage, and timestamp uncertainty.
- Use sanitized representative and synthetic fixtures only; never claim recorded provenance.
- Follow red-green-refactor and make focused commits; do not push.

---

### Task 1: Provider-neutral adapter contract

**Files:**
- Create: `src/squeeze_core/adapters/base.py`
- Create: `src/squeeze_core/adapters/diagnostics.py`
- Create: `src/squeeze_core/adapters/__init__.py`
- Test: `tests/adapters/test_adapter_contract.py`

**Interfaces:**
- Produces immutable `AdapterContext`, `NormalizationDiagnostic`, `RejectedRecord`, and `NormalizationResult` models.
- Results expose typed observation and diagnostic tuples, never an unstructured primary dictionary.

- [ ] Write tests for immutability, timezone-aware ingestion, rejection/result invariants, and stable diagnostic codes.
- [ ] Run the focused test and confirm failure because the adapter package is absent.
- [ ] Implement the smallest Pydantic models and enums that satisfy the tests.
- [ ] Run focused and full Phase 1A tests.
- [ ] Commit `feat: add provider-neutral offline adapter contract`.

### Task 2: IBKR record validation and normalization

**Files:**
- Create: `src/squeeze_core/adapters/ibkr/models.py`
- Create: `src/squeeze_core/adapters/ibkr/semantics.py`
- Create: `src/squeeze_core/adapters/ibkr/normalizer.py`
- Create: `src/squeeze_core/adapters/ibkr/__init__.py`
- Test: `tests/adapters/ibkr/test_normalizer.py`

**Interfaces:**
- Consumes: `AdapterContext` and provider-shaped mappings validated as `IbkrBorrowRecord`.
- Produces: `normalize_ibkr_borrow_record(record, context) -> NormalizationResult` and `normalize_ibkr_borrow_records(records, context) -> NormalizationResult`.

- [ ] Write failing tests for complete records, explicit zeros, missing values, explicit percent units, known/delayed timestamps, invalid numeric values, duplicates, and conflicts.
- [ ] Run focused tests and confirm feature-missing failures.
- [ ] Implement timestamp parsing, explicit scaling, raw hashing, canonical observation construction, and batch reconciliation.
- [ ] Run focused tests and refactor while green.
- [ ] Commit `feat: add IBKR borrow-record normalization`.

### Task 3: Sanitized fixtures and generated replay evidence

**Files:**
- Create: `tests/fixtures/providers/ibkr/*.json`
- Create: `tests/provider_fixture_builders.py`
- Create: `tests/fixtures/providers/ibkr/normalized_session.jsonl`
- Test: `tests/adapters/ibkr/test_provider_fixtures.py`
- Test: `tests/adapters/ibkr/test_replay_integration.py`

**Interfaces:**
- Consumes: local fixture records/context and the IBKR normalizer.
- Produces: deterministic JSONL and checked SHA-256 constants replayable in strict mode.

- [ ] Write failing fixture provenance, builder drift, canonical hash, strict replay, repeat-replay, and isolation tests.
- [ ] Add explicit fixture metadata and representative/synthetic inputs with no account or credential data.
- [ ] Implement the deterministic builder and generate committed JSONL from the same code path.
- [ ] Record expected raw, JSONL, and replay hashes only after deterministic repeated runs.
- [ ] Commit `test: add sanitized provider fixtures and replay edge cases`.

### Task 4: Offline CLI

**Files:**
- Modify: `src/squeeze_core/__main__.py`
- Test: `tests/test_cli.py`

**Interfaces:**
- Produces: `normalize-provider --provider ibkr --input RECORD --context CONTEXT`, machine-readable canonical output, structured diagnostics, and nonzero rejection status.

- [ ] Write failing success/rejection/local-only CLI tests.
- [ ] Extend argparse and route only local JSON files through the normalizer.
- [ ] Run CLI and full tests.
- [ ] Commit `feat: add offline provider normalization command`.

### Task 5: Documentation and final verification

**Files:**
- Create: `docs/adapter-contract.md`
- Create: `docs/providers/ibkr-offline-normalization.md`
- Create: `docs/adr/0005-offline-adapter-boundary.md`
- Create: `docs/adr/0006-point-in-time-normalization-context.md`
- Create: `docs/adr/0007-provider-units-and-missing-values.md`
- Modify: `README.md`
- Modify: `docs/architecture.md`
- Modify: `docs/testing-and-validation.md`

**Interfaces:**
- Documents exact implemented record/context/result shapes, diagnostic codes, time/unit/quality rules, fixture provenance, commands, hashes, and limitations.

- [ ] Update docs from implemented behavior and run command examples.
- [ ] Run all tests and deterministic builder/replay twice.
- [ ] Scan new repository files for credential-like assignments, environment/network/SDK/database/order imports, active accounts, tokens, sessions, and private URLs.
- [ ] Compare archived repository Git states and confirm no modifications.
- [ ] Commit `docs: document offline provider normalization`.
- [ ] Verify branch, HEAD, log, remotes, and clean working tree; do not push.
