# Phase 1D Offline FINRA-Shaped Published Short Interest Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:test-driven-development to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Normalize local FINRA-shaped published-short-interest records and extend deterministic point-in-time evidence with explicit publication, receipt, settlement-age, and immutable revision semantics.

**Architecture:** Reuse the unchanged schema `1.0.0` published-short-interest payload and provider-neutral adapter result. Add a pure FINRA adapter, then extend the existing evidence builder with event-specific publication gates, independent coverage, reporting/availability ages, revision relationships, and settlement-period-aware conflicts whose empty additions serialize away for Phase 1C compatibility.

**Tech Stack:** Python 3.12, Pydantic 2.13.4, pytest 8.4.1, standard-library decimal/date/time/zoneinfo/hash/UUID/JSON/CLI APIs.

## Global Constraints

- Work only on `phase/1d-offline-finra-short-interest`; do not merge, push, or add a remote.
- Remain offline; add no FINRA/Finviz/IBKR connection, download, HTTP/FTP, credentials, environment, database, browser, GUI, or order APIs.
- Keep canonical schema `1.0.0` and the existing published-short-interest payload unchanged.
- Preserve all existing Phase 1A/1B/1C fixture, replay, bundle, and serialized-bundle hashes.
- Never backdate effective time to settlement date; enforce publication, receipt, and effective gates.
- Keep published short interest, daily short-sale volume, Finviz short float, and IBKR lending evidence distinct.
- Preserve missing versus zero and original versus correction as immutable observations.
- Use representative and synthetic fixtures only; no fixture may claim recorded provenance.
- Add no score, ranking, recommendation, strategy, signal, entry, exit, or trading behavior.
- Follow red-green-refactor, focused commits, fresh verification, and archive cleanliness checks.

---

### Task 1: FINRA-shaped model, semantics, and parsers

**Files:**
- Create: `src/squeeze_core/adapters/finra/models.py`
- Create: `src/squeeze_core/adapters/finra/semantics.py`
- Create: `src/squeeze_core/adapters/finra/parsing.py`
- Create: `src/squeeze_core/adapters/finra/__init__.py`
- Modify: `src/squeeze_core/adapters/diagnostics.py`
- Create: `tests/adapters/finra/test_models_and_parsing.py`

**Interfaces:**
- Produce immutable `FinraShortInterestRecord`, `RevisionStatus`, `PercentageUnit`, and `DateOnlyPublicationPolicy`.
- Produce pure `parse_nonnegative_integer`, `parse_nonnegative_decimal`, `parse_percentage`, `parse_settlement_date`, and `parse_publication_availability` helpers returning typed results or stable FINRA diagnostic errors.

- [ ] Write focused tests for schema/type/origin, aliases, symbol normalization, stable raw hash, integer/decimal/percentage rules, settlement dates, full/naive/date-only/missing publication values, publication policies, timezones, provider/capture timestamps, revision fields, and daily short-volume rejection.
- [ ] Run `.\.venv\Scripts\python.exe -m pytest tests/adapters/finra/test_models_and_parsing.py -q` and confirm failure because the FINRA package is absent.
- [ ] Implement the smallest enums, strict model, aliases, and parsers needed by the tests; parsers must accept explicit values only and never call wall time.
- [ ] Re-run the focused test, refactor only after green, and run existing adapter tests.
- [ ] Commit `feat: add finra short-interest provider contract`.

### Task 2: Offline FINRA normalization and immutable batch relationships

**Files:**
- Create: `src/squeeze_core/adapters/finra/normalizer.py`
- Create: `src/squeeze_core/adapters/finra/validation.py`
- Modify: `src/squeeze_core/adapters/finra/__init__.py`
- Create: `tests/adapters/finra/test_normalizer.py`
- Create: `docs/adr/0011-published-short-interest-availability.md`
- Create: `docs/adr/0012-settlement-date-versus-effective-time.md`
- Create: `docs/adr/0013-immutable-short-interest-revisions.md`

**Interfaces:**
- Produce `normalize_finra_short_interest_record(record, context) -> NormalizationResult`.
- Produce `normalize_finra_short_interest_records(records, context) -> NormalizationResult` with stable duplicate suppression, same-period conflict marking, and deterministic parent/correlation links.
- One defensible record emits one `PUBLISHED_SHORT_INTEREST` observation with `source_timestamp=publication_availability`, `received_timestamp=context.ingested_at`, and `effective_timestamp=max(source_timestamp, received_timestamp)`.

- [ ] Write failing tests for complete, zero, missing, partial, invalid, date-only, missing-publication, capture-only, receipt-before/after-publication, provider timestamp, corrected/revised/cancelled, missing link, duplicate, same-period conflict, and different-period cases.
- [ ] Run the focused tests and confirm the normalization functions are missing.
- [ ] Implement exact raw hashing, timestamp/quality/provenance construction, payload mapping, structured rejection, deterministic diagnostic order, batch duplicate suppression, revision parent links, and conflict preservation.
- [ ] Run focused, canonical contract, IBKR, and Finviz tests; verify old observations are unchanged.
- [ ] Add ADRs 0011-0013 from implemented semantics and commit `feat: add offline finra short-interest normalization`.

### Task 3: Publication eligibility, independent coverage, and age metadata

**Files:**
- Modify: `src/squeeze_core/evidence/models.py`
- Modify: `src/squeeze_core/evidence/policy.py`
- Modify: `src/squeeze_core/evidence/builder.py`
- Modify: `src/squeeze_core/evidence/__init__.py`
- Create: `tests/evidence/test_short_interest_timeline.py`
- Modify: `tests/evidence/test_selection_and_coverage.py`

**Interfaces:**
- Add `CoverageDomain.PUBLISHED_SHORT_INTEREST`.
- Add conditional `ObservationAge(observation_id, availability_age_ms, reporting_period_age_days)` and `RevisionRelationship(prior_observation_id, revision_observation_id, status)` collections to `PointInTimeEvidenceBundle`.
- Add optional `maximum_reporting_period_age_days` to policy without changing existing behavior when absent.

- [ ] Write failing tests proving settlement alone never grants eligibility, publication/receipt/effective gates are independent, corrected data cannot alter earlier bundles, correction relationships appear only when eligible, reporting age differs from availability age, and coverage is independent.
- [ ] Run focused tests and confirm the fourth domain and structured metadata are absent.
- [ ] Implement event-specific gates, diagnostics, ages, revision relationships, reporting-period staleness, stable ordering, and conditional omission of empty Phase 1D fields.
- [ ] Run focused evidence tests plus the Phase 1C expected bundle/serialization hash tests.
- [ ] Commit `feat: enforce short-interest publication eligibility`.

### Task 4: Settlement-period-aware conflict semantics

**Files:**
- Modify: `src/squeeze_core/evidence/conflicts.py`
- Modify: `src/squeeze_core/evidence/builder.py`
- Modify: `tests/evidence/test_conflicts.py`
- Create: `tests/evidence/test_short_interest_conflicts.py`

**Interfaces:**
- Extract `published_short_shares`, provider-published `published_short_float_percent`, and `published_days_to_cover` with settlement-period comparison keys.
- Same settlement period can conflict; different settlement periods produce `TEMPORAL_DIFFERENCE`; explicit revision parent pairs are relationships, not unresolved conflicts.

- [ ] Write failing tests for same-period value conflict, duplicate conflict, different-period temporal difference, revision exclusion, stable IDs, incompatible borrow comparisons, conditional Finviz short-float refusal, no averaging, and no winner.
- [ ] Run focused tests and confirm published-short-interest fields are not extracted.
- [ ] Implement comparison-period-aware semantic extraction and deterministic classification without altering existing market/borrow conflict behavior.
- [ ] Run all conflict and evidence tests.
- [ ] Commit `feat: preserve short-interest evidence conflicts`.

### Task 5: Deterministic representative, edge, revision, timeline, and mixed fixtures

**Files:**
- Create: `tests/fixtures/providers/finra/fixture_metadata.json`
- Create: `tests/fixtures/providers/finra/context.json`
- Create: `tests/fixtures/providers/finra/representative_cases.json`
- Create: `tests/fixtures/providers/finra/edge_cases.json`
- Create: `tests/fixtures/providers/finra/revision_cases.json`
- Create: `tests/fixtures/evidence/mixed_finviz_ibkr_finra_cases.json`
- Create: `tests/fixtures/evidence/short_interest_publication_timeline.json`
- Create: `tests/fixtures/evidence/expected_phase_1d_bundle_metadata.json`
- Create: `tests/fixtures/evidence/normalized_phase_1d_point_in_time.jsonl`
- Create: `tests/phase_1d_fixture_builders.py`
- Create: `tests/adapters/finra/test_provider_fixtures.py`
- Create: `tests/evidence/test_phase_1d_replay_integration.py`

**Interfaces:**
- Produce deterministic canonical FINRA observations, mixed JSONL, strict replay, five timeline bundles, revision relationships, and committed SHA-256 metadata.

- [ ] Write failing tests for every required provider/mixed case, exact fixture metadata keys/origins, synthetic symbols, no sensitive content, repeated generation, strict replay, eligibility after replay, historical rebuild stability, and all pre-Phase-1D hashes.
- [ ] Add representative and synthetic fixture documents for the 22 provider cases, revision timeline, and 12 mixed cases without real symbols or provider claims.
- [ ] Implement the builder, generate artifacts twice, compare bytes, and record raw/observation/JSONL/replay/timeline/bundle hashes.
- [ ] Run provider fixture, replay, hash, and isolation tests.
- [ ] Commit `test: add finra publication timeline fixtures`.

### Task 6: Offline CLI extensions

**Files:**
- Modify: `src/squeeze_core/__main__.py`
- Modify: `tests/test_cli.py`

**Interfaces:**
- Extend `normalize-provider --provider finra`.
- Add `build-evidence-timeline --input PATH --symbol SYMBOL --as-of-file PATH` only if it delegates each timestamp to the existing builder and preserves stable JSON ordering.

- [ ] Write failing success, rejection, case selection, stable output, local-file-only, evidence, and timeline CLI tests.
- [ ] Route FINRA normalization and optional timeline construction through existing context/fixture loading and evidence APIs.
- [ ] Run CLI tests and representative documented commands.
- [ ] Commit `feat: extend offline cli for finra evidence`.

### Task 7: Documentation and final verification

**Files:**
- Create: `docs/providers/finra-offline-short-interest.md`
- Create: `docs/published-short-interest-semantics.md`
- Create: `docs/short-interest-publication-timeline.md`
- Create: `docs/phase-1d-progress.md`
- Modify: `README.md`
- Modify: `docs/architecture.md`
- Modify: `docs/adapter-contract.md`
- Modify: `docs/observation-contract.md`
- Modify: `docs/field-semantics.md`
- Modify: `docs/cross-source-evidence.md`
- Modify: `docs/point-in-time-evidence-policy.md`
- Modify: `docs/testing-and-validation.md`

**Interfaces:**
- Document exact evidence basis, aliases, units, dates, availability, revision, conflict, coverage, age, fixture hashes, commands, and limitations.

- [ ] Update documentation from actual implemented behavior and record the absence of a recorded FINRA sample without overstating provenance.
- [ ] Run the complete pytest suite and every documented validate/replay/normalize/build/timeline command.
- [ ] Regenerate Phase 1D artifacts twice and verify all old and new hashes from fresh output.
- [ ] Scan the core for credentials, private URLs, `.env`, network/download/browser/provider SDK/database/order/GUI/wall-clock dependencies and prohibited strategy language in machine output.
- [ ] Verify all three archived repositories remain clean at `0897562e...`, `6dbefd1a...`, and `84f770dd...`.
- [ ] Commit `docs: document published short-interest evidence`.
- [ ] Verify branch, HEAD, log, remotes, and clean tree; do not push, merge, or begin Phase 1E.
