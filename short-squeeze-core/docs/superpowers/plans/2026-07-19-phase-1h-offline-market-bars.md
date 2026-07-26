# Phase 1H Offline Market-Bar Evidence Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use test-driven-development to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Add offline deterministic market-bar normalization, immutable lifecycle evidence, session-aware objective series, replay fixtures, and local CLI support without analytics or strategy behavior.

**Architecture:** Reuse schema `1.0.0`, unchanged `BarPayload`, the provider-neutral adapter boundary, canonical replay, and the existing evidence bundle. Store boundary/session/lifecycle detail in structured provenance, activate independent `MARKET_BARS` coverage, and add a small pure series builder over eligible canonical observations.

**Tech Stack:** Python 3.12, Pydantic 2.13.4, pytest 8.4.1, and standard-library decimal/datetime/zoneinfo/hash/UUID/JSON/path/CLI APIs.

## Global Constraints

- Work only on `phase/1h-offline-market-bars`; do not merge, push, or add a remote.
- Keep schema `1.0.0` and `BarPayload` unchanged; preserve all Phase 1A-1G hashes.
- Use only local representative and synthetic fixtures; no fixture is recorded.
- Add no network/provider client, credential, `.env`, token, database, GUI, persistence, alert, order, wall-clock, or random deterministic input.
- Add no return, gap, RVOL, rolling volume, indicator, momentum, breakout, trend, score, rank, recommendation, entry, exit, signal, interpolation, filling, aggregation, or resampling logic.
- Follow red-green-refactor, focused commits, fresh verification, and archived-repository cleanliness checks.

---

### Task 1: Strict provider contract, interval model, and timestamp parsing

**Files:**
- Create: `src/squeeze_core/adapters/market_bars/{__init__,models,semantics,parsing,validation}.py`
- Modify: `src/squeeze_core/adapters/diagnostics.py`
- Create: `tests/adapters/market_bars/{__init__,test_models_and_parsing}.py`

**Interfaces:**
- Produces: `MarketBarRecord`, `BarInterval`, `BarIntervalUnit`, `BarIntervalKind`, `BarTimestampMeaning`, `BarCompletionStatus`, `BarSession`, `BarVolumeUnit`, `parse_bar_timestamp`, `resolve_bar_boundaries`.

- [ ] Write tests importing these interfaces and covering strict schema/type/origin, provider aliases, collision rejection, supported/ambiguous intervals, fixed versus session-based daily identity, explicit boundaries, start/end labels, time-only plus session date, date-only daily values, missing timezone, DST ambiguity/nonexistence, and stable raw identity.
- [ ] Run `.\.venv\Scripts\python.exe -m pytest tests\adapters\market_bars\test_models_and_parsing.py -q`; expect collection failure because the package does not exist.
- [ ] Implement the immutable models and parsing helpers with standard-library `zoneinfo`, explicit diagnostic exceptions, and no provider acquisition.
- [ ] Re-run the focused test; expect all tests to pass.
- [ ] Commit with `feat: add offline market-bar provider contract`.

### Task 2: Deterministic single and batch normalization

**Files:**
- Create: `src/squeeze_core/adapters/market_bars/normalizer.py`
- Modify: `src/squeeze_core/adapters/market_bars/__init__.py`
- Create: `tests/adapters/market_bars/test_normalizer.py`

**Interfaces:**
- Produces: `normalize_market_bar_record(record, context) -> NormalizationResult` and `normalize_market_bar_records(records, context) -> NormalizationResult`.

- [ ] Write tests for exact Decimal OHLC, invalid/missing OHLC, missing/zero/negative/fractional volume, nullable trade count/VWAP, explicit sessions, session-date mismatch, publication/capture/receipt/effective separation, partial/completed/corrected/cancelled status, immutable revision links, exact duplicates, same-ID conflicts, cross-provider boundary conflicts, stable diagnostics, and repeatable hashes.
- [ ] Run the focused test and confirm failure because normalization is absent.
- [ ] Implement minimal normalization into unchanged canonical `BAR` observations, storing boundary/session/lifecycle detail in provenance and linking explicit revisions without mutation.
- [ ] Re-run focused adapter tests and all contract/serialization tests; expect pass and unchanged legacy hashes.
- [ ] Commit with `feat: add deterministic market-bar normalization`.

### Task 3: Point-in-time eligibility, coverage, ages, and lifecycle relationships

**Files:**
- Modify: `src/squeeze_core/evidence/{models,policy,builder,conflicts,__init__}.py`
- Create: `tests/evidence/test_market_bar_timeline.py`
- Create: `tests/evidence/test_market_bar_conflicts.py`

**Interfaces:**
- Produces: `CoverageDomain.MARKET_BARS`, bar evidence diagnostics, conditional bar ages, and deterministic bar revision/conflict relationships through `build_point_in_time_evidence`.

- [ ] Write failing timeline tests for before partial, after partial receipt, after interval end/before completion receipt, after completion receipt, before correction receipt, after correction receipt, and historical rebuild byte identity.
- [ ] Write failing tests for independent coverage, missing/partial/conflicted states, publication and receipt gates, same-boundary comparisons, different-boundary incompatibility, no averaging, and stable conflict IDs.
- [ ] Run both tests and confirm failures for the absent domain and gates.
- [ ] Implement the smallest conditional model/builder/conflict extensions using excluded default fields so Phase 1A-1G bundle bytes remain unchanged.
- [ ] Run focused evidence tests plus Phase 1C-1G compatibility tests; expect pass.
- [ ] Commit with `feat: enforce point-in-time market-bar evidence`.

### Task 4: Objective session-aware bar series

**Files:**
- Create: `src/squeeze_core/evidence/bars.py`
- Modify: `src/squeeze_core/evidence/__init__.py`
- Create: `tests/evidence/test_bar_series.py`

**Interfaces:**
- Produces: `BarSeriesPolicy`, `BarSeriesDiagnostic`, `BarSeries`, and `build_bar_series(observations, policy)`.

- [ ] Write failing tests for symbol, interval, and session filtering; stable start/source/identity ordering; latest eligible record; duplicate boundaries; overlaps; explicit expected missing intervals; closed-session distinction; unknown expectation; daily session dates; and absence of interpolation/resampling/calculation fields.
- [ ] Run the focused test and confirm the wished-for API is absent.
- [ ] Implement pure structural selection over canonical bar observations and explicit fixture policy windows.
- [ ] Re-run the focused test; expect pass and byte-identical repeated series hashes.
- [ ] Commit with `feat: add session-aware objective bar series`.

### Task 5: Provider and mixed replay fixtures

**Files:**
- Create: `tests/fixtures/providers/market_bars/{fixture_metadata,context,representative_cases,edge_cases,lifecycle_cases,session_cases}.json`
- Create: `tests/fixtures/evidence/{mixed_phase_1h_cases,market_bar_availability_timeline,expected_phase_1h_bundle_metadata}.json`
- Create: `tests/fixtures/evidence/normalized_phase_1h_point_in_time.jsonl`
- Create: `tests/phase_1h_fixture_builders.py`
- Create: `tests/adapters/market_bars/test_provider_fixtures.py`
- Create: `tests/evidence/test_phase_1h_replay_integration.py`

**Interfaces:**
- Produces: deterministic provider cases, lifecycle/session cases, mixed observations, timeline bundles, and compatibility anchors.

- [ ] Write failing fixture-integrity and replay tests for all required case IDs, exact provenance classification, no real symbols/credentials/live URLs, generation idempotence, strict replay, all prior domains, lifecycle hashes, and Phase 1A-1G anchors.
- [ ] Run the focused tests and confirm missing fixture failures.
- [ ] Add sanitized representative/synthetic JSON and a deterministic builder using only existing and new pure normalizers.
- [ ] Generate twice and assert byte-identical files, raw hashes, replay hash, timeline bundle hashes, final series hash, and serialized bundle hash.
- [ ] Run focused fixture/replay tests; expect pass.
- [ ] Commit with `test: add market-bar lifecycle and mixed replay fixtures`.

### Task 6: Offline CLI

**Files:**
- Modify: `src/squeeze_core/__main__.py`
- Modify: `tests/test_cli.py`

**Interfaces:**
- Extends: `normalize-provider --provider market-bars`.
- Produces: `build-bar-series --input PATH --symbol SYMBOL --interval INTERVAL --as-of TIMESTAMP`.

- [ ] Write failing CLI tests for accepted normalization, rejected input/nonzero exit, stable JSON, local timeline evidence, symbol/interval/session filtering, and forbidden analytical-output keys.
- [ ] Run focused CLI tests and confirm parser/provider-choice failures.
- [ ] Add command dispatch to existing local loaders and pure builders.
- [ ] Re-run CLI tests; expect pass and deterministic repeated output.
- [ ] Commit with `feat: expose offline market-bar evidence through cli`.

### Task 7: Documentation, isolation, and final compatibility verification

**Files:**
- Create: `docs/providers/market-bars-offline.md`
- Create: `docs/market-bar-availability-semantics.md`
- Create: `docs/market-bar-session-and-lifecycle-timeline.md`
- Create: `docs/adr/0023-market-bar-availability.md`
- Create: `docs/adr/0024-partial-completed-and-corrected-bars.md`
- Create: `docs/adr/0025-session-aware-bar-evidence-without-indicators.md`
- Create: `docs/phase-1h-progress.md`
- Modify: `README.md`, `docs/{architecture,adapter-contract,observation-contract,field-semantics,cross-source-evidence,point-in-time-evidence-policy,testing-and-validation}.md`

**Interfaces:**
- Produces: complete Phase 1H operator/provider semantics and verification record.

- [ ] Document aliases, boundaries, sessions/DST, numeric units, availability, lifecycle, conflicts, series/missing intervals, fixture provenance, CLI commands, hashes, compatibility, and explicit exclusions.
- [ ] Run `.\.venv\Scripts\python.exe -m pytest`; expect zero failures.
- [ ] Run deterministic fixture generation twice, strict replay, CLI smoke tests, forbidden-import/keyword scans, credential-pattern scans, and archived-repository status/HEAD checks.
- [ ] Verify `git diff f3aef4a..HEAD` contains no archive, credential, token, Phase 0, schema-version, indicator, score, rank, signal, or live-provider changes.
- [ ] Commit with `docs: document point-in-time market-bar evidence` and confirm a clean tree.
