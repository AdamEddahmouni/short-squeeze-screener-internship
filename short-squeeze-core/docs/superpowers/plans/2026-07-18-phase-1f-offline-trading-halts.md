# Phase 1F Offline Trading-Halt Evidence Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:test-driven-development to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Normalize local exchange-shaped halt/resumption lifecycle records and extend deterministic point-in-time evidence with objective halt state, public/receipt gates, immutable updates, conflicts, coverage, and distinct ages.

**Architecture:** Reuse schema `1.0.0`, the unchanged `TradingHaltPayload`, provider-neutral adapter results, replay ordering, and evidence framework. Add a pure `halts` adapter; retain lifecycle-specific scheduling and identity in structured provenance; then add event-specific eligibility, conditional halt state/ages, and halt-aware conflicts without changing Phase 1A–1E bytes.

**Tech Stack:** Python 3.12, Pydantic 2.13.4, pytest 8.4.1, standard-library datetime/zoneinfo/hash/UUID/JSON/path/CLI APIs.

## Global Constraints

- Work only on `phase/1f-offline-trading-halts`; do not merge, push, or add a remote.
- Remain offline; add no exchange/Nasdaq/NYSE/Finviz/IBKR/FINRA/SEC connection, download, HTTP/FTP/WebSocket, credentials, environment, database, browser, GUI, alert, or order API.
- Keep schema `1.0.0` and `TradingHaltPayload` unchanged.
- Preserve every Phase 1A–1E fixture, replay, bundle, serialized-bundle, and compatibility hash.
- Enforce source/publication, receipt, and effective gates independently; halt-effective or session date never grants availability.
- Keep quote and trade resumption distinct and scheduled values separate from actual values.
- Preserve every lifecycle update as an immutable observation; do not average conflicts or select a winner.
- Use representative and synthetic fixtures only; no fixture may claim recorded provenance.
- Add no sentiment, catalyst direction, price prediction, score, rank, recommendation, strategy, signal, entry, exit, or trading behavior.
- Follow red-green-refactor, focused commits, fresh verification, and archive cleanliness checks.

---

### Task 1: Halt model, lifecycle semantics, and timestamp parsing

**Files:**
- Create: `src/squeeze_core/adapters/halts/models.py`
- Create: `src/squeeze_core/adapters/halts/semantics.py`
- Create: `src/squeeze_core/adapters/halts/parsing.py`
- Create: `src/squeeze_core/adapters/halts/validation.py`
- Create: `src/squeeze_core/adapters/halts/__init__.py`
- Modify: `src/squeeze_core/adapters/diagnostics.py`
- Create: `tests/adapters/halts/__init__.py`
- Create: `tests/adapters/halts/test_models_and_parsing.py`

**Interfaces:**
- Produce immutable `TradingHaltRecord`, `HaltLifecycleStatus`, `HaltRevisionStatus`, and `HaltTimestamp` models.
- Produce `parse_halt_code`, `parse_session_date`, `parse_halt_timestamp`, `parse_public_availability`, and `halt_event_key` helpers returning typed values or stable `HALT_*` parse errors.

- [ ] Write focused tests that import the wished-for interfaces and cover schema/type/origin, aliases, symbol/exchange normalization, required identity, exact timestamps, session dates, time-only plus session/timezone, missing timezone, invalid timestamp, availability precedence, and capture-only rejection.
- [ ] Run `\.\.venv\Scripts\python.exe -m pytest tests/adapters/halts/test_models_and_parsing.py -q` and confirm collection fails because the package is absent.
- [ ] Implement only the strict enums/model/parsers required by the failing tests; accept `TRADING_HALT_V1`, documented aliases, explicit timezones, and no wall clock or lookup.
- [ ] Re-run the focused test, refactor after green, then run all existing adapter tests.
- [ ] Commit `feat: add offline trading-halt provider contract`.

### Task 2: Deterministic single and batch halt normalization

**Files:**
- Create: `src/squeeze_core/adapters/halts/normalizer.py`
- Modify: `src/squeeze_core/adapters/halts/__init__.py`
- Create: `tests/adapters/halts/test_normalizer.py`
- Create: `docs/adr/0017-trading-halt-public-availability.md`
- Create: `docs/adr/0018-scheduled-versus-actual-resumption.md`
- Create: `docs/adr/0019-immutable-halt-lifecycle-updates.md`

**Interfaces:**
- Produce `normalize_trading_halt_record(record, context) -> NormalizationResult`.
- Produce `normalize_trading_halt_records(records, context) -> NormalizationResult` with exact-duplicate suppression, same-ID conflict preservation, deterministic parent/correlation links, and stable ordering.
- Emit one unchanged canonical `TRADING_HALT` payload per lifecycle record with `source_timestamp=public_availability`, `received_timestamp=context.ingested_at`, and `effective_timestamp=max(source_timestamp, received_timestamp)`.

- [ ] Write failing tests for complete/partial/rejected records, missing reason/code, unknown code, halt without effective time, all scheduled/actual lifecycle stages, indefinite/cancelled/changed schedule, publication/receipt ordering, revisions, missing links, duplicates, same-ID conflicts, multiple halt events, raw hashes, and deterministic provenance.
- [ ] Run `\.\.venv\Scripts\python.exe -m pytest tests/adapters/halts/test_normalizer.py -q` and confirm normalization imports or assertions fail for the intended missing behavior.
- [ ] Implement minimal normalization, quality/provenance metadata, immutable batch links, duplicate suppression, and conflict marking; scheduled times must never populate canonical `resume_time`.
- [ ] Run halt tests plus canonical, IBKR, Finviz, FINRA, and SEC adapter tests and verify old serialized observations remain unchanged.
- [ ] Add ADRs 0017–0019 from the green behavior and commit `feat: add deterministic halt normalization`.

### Task 3: Halt availability, independent coverage, ages, and objective state

**Files:**
- Modify: `src/squeeze_core/evidence/models.py`
- Modify: `src/squeeze_core/evidence/policy.py`
- Modify: `src/squeeze_core/evidence/builder.py`
- Modify: `src/squeeze_core/evidence/__init__.py`
- Create: `tests/evidence/test_trading_halt_timeline.py`
- Modify: `tests/evidence/test_selection_and_coverage.py`

**Interfaces:**
- Add `CoverageDomain.TRADING_HALTS`, `include_trading_halts_domain`, `HaltState`, and conditional `HaltStateSummary`.
- Extend conditional `ObservationAge` with `announcement_age_ms`, `halt_event_age_ms`, and `resumption_event_age_ms` while preserving prior serialization.
- Add `derive_halt_state(observations) -> HaltStateSummary` and reuse it in `build_point_in_time_evidence`.

- [ ] Write failing timeline tests for pre-publication exclusion, pre-receipt exclusion, eligible halt, later update exclusion, historical byte stability, scheduled-not-actual behavior, quotes-without-trades, indefinite halt, every objective state, supporting IDs, and independent coverage/ages.
- [ ] Run the focused evidence tests and confirm halt coverage/state/age interfaces are absent.
- [ ] Implement strict halt source/receipt/effective gates, conditional age fields, event grouping, deterministic state progression, conflict-to-`CONFLICTED`, and unknown/partial handling without reading price or later trades.
- [ ] Run focused tests plus all Phase 1C–1E bundle/hash tests.
- [ ] Commit `feat: enforce halt publication and receipt eligibility`.

### Task 4: Halt-specific structural conflicts

**Files:**
- Modify: `src/squeeze_core/evidence/conflicts.py`
- Modify: `src/squeeze_core/evidence/builder.py`
- Create: `tests/evidence/test_trading_halt_conflicts.py`

**Interfaces:**
- Extract halt code, scheduled quote time, scheduled trade time, actual quote time, and actual trade time keyed by deterministic halt event and lifecycle meaning.
- Treat declared revisions and scheduled-to-actual/quote-to-trade progression as compatible; preserve same-semantic disagreements with stable IDs.

- [ ] Write failing tests for exact duplicate, same-record content conflict, halt-code conflict, scheduled quote/trade time conflicts, temporal lifecycle progression, multiple distinct halts, no averaging, no winner selection, and stable conflict IDs.
- [ ] Run `\.\.venv\Scripts\python.exe -m pytest tests/evidence/test_trading_halt_conflicts.py -q` and confirm halt semantics are not yet extracted.
- [ ] Implement halt semantic extraction and comparison without changing earlier source-domain comparisons.
- [ ] Run all conflict and evidence tests.
- [ ] Commit `feat: preserve immutable halt lifecycle updates`.

### Task 5: Provider, lifecycle, mixed-evidence, timeline, and hash fixtures

**Files:**
- Create: `tests/fixtures/providers/halts/fixture_metadata.json`
- Create: `tests/fixtures/providers/halts/context.json`
- Create: `tests/fixtures/providers/halts/representative_cases.json`
- Create: `tests/fixtures/providers/halts/edge_cases.json`
- Create: `tests/fixtures/providers/halts/lifecycle_cases.json`
- Create: `tests/fixtures/evidence/mixed_phase_1f_cases.json`
- Create: `tests/fixtures/evidence/halt_resumption_timeline.json`
- Create: `tests/fixtures/evidence/expected_phase_1f_bundle_metadata.json`
- Create: `tests/fixtures/evidence/normalized_phase_1f_point_in_time.jsonl`
- Create: `tests/phase_1f_fixture_builders.py`
- Create: `tests/adapters/halts/test_provider_fixtures.py`
- Create: `tests/evidence/test_phase_1f_replay_integration.py`

**Interfaces:**
- Produce all 30 required provider cases, the `TESTA` lifecycle, 15 mixed cases, canonical halt observations, mixed JSONL, strict replay, timeline bundles, objective states, and committed SHA-256 metadata.

- [ ] Write failing fixture tests for exact metadata keys/origins, representative versus synthetic provenance, invented symbols, all required cases, no sensitive/live content, mixed domain independence, no interpretation fields, repeated generation, strict replay, historical rebuild stability, and every Phase 1A–1E compatibility hash.
- [ ] Add local representative/synthetic JSON fixtures and use only `TESTA`, `TESTB`, and `TESTC`.
- [ ] Implement the deterministic builder, generate artifacts twice, byte-compare results, and record raw/observation/resumption/JSONL/replay/timeline/state/bundle hashes.
- [ ] Run provider fixture, replay, timeline, hash, and isolation tests.
- [ ] Commit `test: add halt and resumption timeline fixtures`.

### Task 6: Offline CLI extension

**Files:**
- Modify: `src/squeeze_core/__main__.py`
- Modify: `tests/test_cli.py`

**Interfaces:**
- Extend `normalize-provider --provider halts` and existing evidence/timeline commands.
- Add `build-halt-state --input PATH --symbol SYMBOL --as-of TIMESTAMP` as a local wrapper over the same eligibility/state implementation.

- [ ] Write failing success, rejection, case-selection, stable-output, local-file-only, evidence/timeline, and objective state CLI tests, including nonzero rejection and absence of prediction/score/rank/recommendation fields.
- [ ] Route halt normalization and state construction through existing context, fixture loading, evidence policy, and canonical serialization APIs.
- [ ] Run CLI tests and the representative documented commands twice.
- [ ] Commit `feat: extend offline cli for halt evidence`.

### Task 7: Documentation, completion record, and full verification

**Files:**
- Create: `docs/providers/trading-halts-offline.md`
- Create: `docs/trading-halt-availability-semantics.md`
- Create: `docs/trading-halt-resumption-timeline.md`
- Create: `docs/phase-1f-progress.md`
- Modify: `README.md`
- Modify: `docs/architecture.md`
- Modify: `docs/adapter-contract.md`
- Modify: `docs/observation-contract.md`
- Modify: `docs/field-semantics.md`
- Modify: `docs/cross-source-evidence.md`
- Modify: `docs/point-in-time-evidence-policy.md`
- Modify: `docs/testing-and-validation.md`

**Interfaces:**
- Document the evidence basis, aliases, identities, timestamps, code handling, lifecycle, immutable updates, state, conflicts, coverage, ages, fixtures, commands, hashes, and limitations exactly as implemented.

- [ ] Update documentation and state explicitly that no recorded halt sample exists and no directional interpretation is produced.
- [ ] Run the full pytest suite and every documented validate/replay/normalize/build/timeline/state command.
- [ ] Regenerate Phase 1F artifacts twice and verify all legacy/new hashes from fresh bytes.
- [ ] Scan source/tests/fixtures/docs for credentials, private/live URLs, `.env`, network/download/browser/provider SDK/database/order/GUI/wall-clock/random inputs and prohibited prediction/sentiment/strategy output.
- [ ] Verify all three archived repositories remain clean at `0897562e...`, `6dbefd1a...`, and `84f770dd...`.
- [ ] Commit `docs: document point-in-time trading-halt evidence`.
- [ ] Verify branch, HEAD, log, remotes, and clean tree; do not push, merge, or begin Phase 1G.
