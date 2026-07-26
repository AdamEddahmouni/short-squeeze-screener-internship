# Phase 1E Offline SEC Filing Evidence Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:test-driven-development to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Normalize local SEC/EDGAR-shaped filing metadata and extend deterministic point-in-time evidence with explicit public availability, receipt, reporting period, immutable amendment, duplicate, and conflict semantics.

**Architecture:** Reuse unchanged schema `1.0.0`, `SecFilingPayload`, and provider-neutral adapter results. Add a pure SEC adapter, then extend evidence with event-specific availability gates, independent coverage, three filing ages, amendment relationships, and accession-aware conflicts whose empty additions serialize away for Phase 1A–1D compatibility.

**Tech Stack:** Python 3.12, Pydantic 2.13.4, pytest 8.4.1, standard-library date/time/zoneinfo/hash/UUID/JSON/path/CLI APIs.

## Global Constraints

- Work only on `phase/1e-offline-sec-filings`; do not merge, push, or add a remote.
- Remain offline; add no SEC/EDGAR/Finviz/IBKR/FINRA connection, download, HTTP/FTP, credentials, environment, database, browser, GUI, or order APIs.
- Keep canonical schema `1.0.0` and `SecFilingPayload` unchanged.
- Preserve every Phase 1A–1D fixture, replay, bundle, and serialized-bundle hash.
- Never backdate effective time to filed date or period of report; enforce public, receipt, and effective gates.
- Keep filing metadata distinct from content interpretation and all market, lending, and short-interest evidence.
- Preserve missing versus zero and originals versus amendments as immutable observations.
- Use representative and synthetic fixtures only; no fixture may claim recorded provenance.
- Add no sentiment, catalyst, dilution, score, ranking, recommendation, strategy, signal, entry, exit, or trading behavior.
- Follow red-green-refactor, focused commits, fresh verification, and archive cleanliness checks.

---

### Task 1: SEC-shaped model, semantics, and parsers

**Files:**
- Create: `src/squeeze_core/adapters/sec/models.py`
- Create: `src/squeeze_core/adapters/sec/semantics.py`
- Create: `src/squeeze_core/adapters/sec/parsing.py`
- Create: `src/squeeze_core/adapters/sec/validation.py`
- Create: `src/squeeze_core/adapters/sec/__init__.py`
- Modify: `src/squeeze_core/adapters/diagnostics.py`
- Create: `tests/adapters/sec/test_models_and_parsing.py`

**Interfaces:**
- Produce immutable `SecFilingRecord`, `DateOnlyFilingPolicy`, `DateOnlyPublicationPolicy`, and `FilingStatus`.
- Produce pure `parse_cik`, `parse_accession_number`, `parse_form_type`, `parse_period_of_report`, `parse_document_count`, `parse_timestamp_value`, `parse_filed_value`, `parse_public_availability`, and `sanitize_primary_document` helpers returning typed results or stable SEC diagnostic errors.

- [ ] Write focused tests for schema/type/origin, aliases, symbol normalization, raw hash, CIK padding/errors, accession canonical/compact/errors, forms/amendment indicators, document/path sanitization, counts, periods, exact/naive/date-only/missing timestamp values, precedence, timezones, and capture-only rejection.
- [ ] Run `.\.venv\Scripts\python.exe -m pytest tests/adapters/sec/test_models_and_parsing.py -q` and confirm failure because the SEC package is absent.
- [ ] Implement the smallest enums, strict model, aliases, and pure parsers required by the tests; never call wall time or open a URL.
- [ ] Re-run the focused test, refactor only after green, then run existing adapter tests.
- [ ] Commit `feat: add sec filing provider contract`.

### Task 2: Deterministic offline normalization and immutable batch relationships

**Files:**
- Create: `src/squeeze_core/adapters/sec/normalizer.py`
- Modify: `src/squeeze_core/adapters/sec/__init__.py`
- Create: `tests/adapters/sec/test_normalizer.py`
- Create: `docs/adr/0014-sec-filing-public-availability.md`
- Create: `docs/adr/0015-acceptance-versus-reporting-period.md`
- Create: `docs/adr/0016-immutable-sec-amendments.md`

**Interfaces:**
- Produce `normalize_sec_filing_record(record, context) -> NormalizationResult`.
- Produce `normalize_sec_filing_records(records, context) -> NormalizationResult` with stable duplicate suppression, same-accession conflict diagnostics, and deterministic amendment parent/correlation links.
- One defensible record emits one `SEC_FILING` observation with `source_timestamp=public_availability`, `received_timestamp=context.ingested_at`, and `effective_timestamp=max(source_timestamp, received_timestamp)`.

- [ ] Write failing tests for complete, partial, invalid, exact/date-only/missing availability, explicit publication precedence, acceptance fallback, filed-date uncertainty, receipt ordering, missing CIK, missing period/document, sanitization, original/amendment, missing amendment link, duplicate, same-accession conflict, corrected metadata, and different-accession cases.
- [ ] Run focused tests and confirm normalization functions are missing.
- [ ] Implement raw hashing, timestamp/quality/provenance construction, payload mapping, typed rejection, deterministic diagnostics, batch duplicate suppression, amendment parents, and conflict preservation.
- [ ] Run focused, canonical contract, IBKR, Finviz, and FINRA tests; verify legacy observations are unchanged.
- [ ] Add ADRs 0014–0016 from implemented semantics and commit `feat: add deterministic sec filing normalization`.

### Task 3: SEC availability eligibility, independent coverage, and age metadata

**Files:**
- Modify: `src/squeeze_core/evidence/models.py`
- Modify: `src/squeeze_core/evidence/policy.py`
- Modify: `src/squeeze_core/evidence/builder.py`
- Modify: `src/squeeze_core/evidence/__init__.py`
- Create: `tests/evidence/test_sec_filing_timeline.py`
- Modify: `tests/evidence/test_selection_and_coverage.py`

**Interfaces:**
- Add `CoverageDomain.SEC_FILINGS` and optional `include_sec_filings_domain` policy.
- Extend conditional `ObservationAge` metadata with `filing_age_ms` while retaining `availability_age_ms` and `reporting_period_age_days` compatibility.
- Reuse `RevisionRelationship` for filing amendments with objective status values.

- [ ] Write failing tests proving period/filed date never grants eligibility, public/receipt/effective gates are independent, amendments cannot alter earlier bundles, relationships appear only when eligible, three ages remain distinct, date-only records are not premature, and coverage is independent.
- [ ] Run focused tests and confirm SEC coverage and filing age are absent.
- [ ] Implement event-specific gates, diagnostics, ages, amendment relationships, stable ordering, and conditional omission of empty Phase 1E fields.
- [ ] Run focused evidence tests plus all Phase 1C/1D expected bundle and serialization hash tests.
- [ ] Commit `feat: enforce sec acceptance and receipt eligibility`.

### Task 4: Accession-aware duplicate and conflict semantics

**Files:**
- Modify: `src/squeeze_core/evidence/conflicts.py`
- Modify: `src/squeeze_core/evidence/builder.py`
- Create: `tests/evidence/test_sec_filing_conflicts.py`

**Interfaces:**
- Extract objective filing metadata values keyed by canonical accession.
- Same accession can be duplicate/conflicted; different accessions produce temporal differences; declared amendment parent pairs are relationships rather than unresolved conflicts.

- [ ] Write failing tests for same-accession metadata conflict, exact duplicate, amendment relationship, different-accession temporal difference, stable IDs, incompatible short-interest/borrow/snapshot comparisons, no averaging, and no winner.
- [ ] Run focused tests and confirm SEC metadata is not classified.
- [ ] Implement deterministic accession-aware classification without altering earlier semantic fields.
- [ ] Run all conflict and evidence tests.
- [ ] Commit `feat: preserve sec filing evidence conflicts`.

### Task 5: Representative, edge, amendment, timeline, and mixed fixtures

**Files:**
- Create: `tests/fixtures/providers/sec/fixture_metadata.json`
- Create: `tests/fixtures/providers/sec/context.json`
- Create: `tests/fixtures/providers/sec/representative_cases.json`
- Create: `tests/fixtures/providers/sec/edge_cases.json`
- Create: `tests/fixtures/providers/sec/amendment_cases.json`
- Create: `tests/fixtures/evidence/mixed_finviz_ibkr_finra_sec_cases.json`
- Create: `tests/fixtures/evidence/sec_filing_availability_timeline.json`
- Create: `tests/fixtures/evidence/expected_phase_1e_bundle_metadata.json`
- Create: `tests/fixtures/evidence/normalized_phase_1e_point_in_time.jsonl`
- Create: `tests/phase_1e_fixture_builders.py`
- Create: `tests/adapters/sec/test_provider_fixtures.py`
- Create: `tests/evidence/test_phase_1e_replay_integration.py`

**Interfaces:**
- Produce deterministic canonical SEC observations, mixed JSONL, strict replay, five timeline bundles, amendment relationships, and committed SHA-256 metadata.

- [ ] Write failing tests for all 30 provider cases and 15 mixed cases, exact fixture metadata keys/origins, invented identities, no sensitive/live URLs, repeated generation, strict replay, replay eligibility, historical rebuild stability, and all Phase 1A–1D hashes.
- [ ] Add representative and synthetic fixture documents without real symbols or provider claims.
- [ ] Implement the builder, generate artifacts twice, compare bytes, and record raw/observation/JSONL/replay/timeline/bundle hashes.
- [ ] Run provider fixture, replay, hash, and isolation tests.
- [ ] Commit `test: add sec availability timeline fixtures`.

### Task 6: Offline CLI extension

**Files:**
- Modify: `src/squeeze_core/__main__.py`
- Modify: `tests/test_cli.py`

**Interfaces:**
- Extend `normalize-provider --provider sec` and reuse `build-evidence`/`build-evidence-timeline` for SEC-aware canonical input.

- [ ] Write failing success, rejection, case-selection, stable-output, local-file-only, evidence, and timeline CLI tests.
- [ ] Route SEC normalization through existing context/fixture loading and evidence APIs.
- [ ] Run CLI tests and representative documented commands.
- [ ] Commit `feat: extend offline cli for sec evidence`.

### Task 7: Documentation and final verification

**Files:**
- Create: `docs/providers/sec-offline-filings.md`
- Create: `docs/sec-filing-availability-semantics.md`
- Create: `docs/sec-filing-amendment-timeline.md`
- Create: `docs/phase-1e-progress.md`
- Modify: `README.md`
- Modify: `docs/architecture.md`
- Modify: `docs/adapter-contract.md`
- Modify: `docs/observation-contract.md`
- Modify: `docs/field-semantics.md`
- Modify: `docs/cross-source-evidence.md`
- Modify: `docs/point-in-time-evidence-policy.md`
- Modify: `docs/testing-and-validation.md`

**Interfaces:**
- Document exact evidence basis, aliases, identity, dates/times, availability, amendments, conflicts, coverage, ages, fixture hashes, commands, and limitations.

- [ ] Update documentation from actual behavior and record the absence of a recorded SEC sample without overstating provenance.
- [ ] Run the complete pytest suite and every documented validate/replay/normalize/build/timeline command.
- [ ] Regenerate Phase 1E artifacts twice and verify all legacy and new hashes from fresh output.
- [ ] Scan for credentials, private/live URLs, `.env`, network/download/browser/provider SDK/database/order/GUI/wall-clock dependencies and prohibited interpretation language in machine output.
- [ ] Verify all three archived repositories remain clean at `0897562e...`, `6dbefd1a...`, and `84f770dd...`.
- [ ] Commit `docs: document point-in-time sec filing evidence`.
- [ ] Verify branch, HEAD, log, remotes, and clean tree; do not push, merge, or begin Phase 1F.
