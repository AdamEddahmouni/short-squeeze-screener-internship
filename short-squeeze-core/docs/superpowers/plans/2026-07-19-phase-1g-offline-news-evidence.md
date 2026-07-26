# Phase 1G Offline Objective News Evidence Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use test-driven-development to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Normalize local Finviz-, Yahoo-, and NewsAPI-shaped objective news metadata and extend deterministic point-in-time evidence with explicit associations, availability, immutable lifecycle, conflicts, syndication, coverage, ages, replay, and CLI support.

**Architecture:** Reuse schema `1.0.0`, the unchanged `NewsItemPayload`, provider-neutral adapter results, replay ordering, and evidence framework. Add a pure `news` adapter; keep provider/lifecycle details in structured provenance; then add news-aware association and availability gates plus conditional relationships and ages without changing Phase 1A–1F bytes.

**Tech Stack:** Python 3.12, Pydantic 2.13.4, pytest 8.4.1, and standard-library datetime/zoneinfo/hash/UUID/JSON/path/URL/CLI APIs.

## Global constraints

- Work only on `phase/1g-offline-news-evidence`; do not merge, push, or add a remote.
- Remain offline; add no provider/RSS/HTTP/FTP/WebSocket/browser client, authentication, credential, `.env`, database, GUI, persistence, alert, or order API.
- Keep schema `1.0.0` and `NewsItemPayload` unchanged.
- Preserve every Phase 1A–1F fixture, replay, bundle, serialized-bundle, and compatibility hash.
- Keep one observation per provider record, with envelope `symbol=null` and explicit canonical `associated_symbols`.
- Preserve publication, update, provider availability, capture, receipt, and effective timestamps independently.
- Preserve immutable lifecycle records, conflicts, and provider observations; do not semantically merge or select a winner.
- Use representative and synthetic fixtures only; never use `data/news_snapshot.json` as a fixture.
- Add no sentiment, catalyst/materiality/relevance/topic/direction classification, entity inference, generated summary, embedding, fuzzy matching, score, rank, recommendation, signal, entry, exit, or trading behavior.
- Follow red-green-refactor, focused commits, fresh verification, and archive cleanliness checks.

---

### Task 1: Provider contract

**Files:**
- Create: `src/squeeze_core/adapters/news/models.py`
- Create: `src/squeeze_core/adapters/news/semantics.py`
- Create: `src/squeeze_core/adapters/news/parsing.py`
- Create: `src/squeeze_core/adapters/news/validation.py`
- Create: `src/squeeze_core/adapters/news/__init__.py`
- Modify: `src/squeeze_core/adapters/diagnostics.py`
- Create: `tests/adapters/news/__init__.py`
- Create: `tests/adapters/news/test_models_and_parsing.py`

**Produces:** `NewsRecord`, `NewsSourceShape`, `NewsLifecycleStatus`, `NewsDateOnlyPolicy`, `ParsedNewsTimestamp`, `SanitizedNewsUrl`, `parse_news_timestamp`, `sanitize_news_url`, and strict alias normalization.

- [ ] Write failing tests that import the wished-for interfaces and assert `NEWS_ITEM_V1`, `NEWS_ITEM`, valid fixture origins, strict unknown-field rejection, Finviz/Yahoo/NewsAPI alias extraction, collision rejection, Unicode preservation, whitespace normalization, URL fragment/tracking removal, article query retention, credential/host/scheme rejection, exact/date-only/unknown-timezone parsing, and stable raw identity.
- [ ] Run `\.\.venv\Scripts\python.exe -m pytest tests/adapters/news/test_models_and_parsing.py -q`; expected result is collection failure because `squeeze_core.adapters.news` does not exist.
- [ ] Implement only the immutable enums/models/parsers and `NEWS_*` diagnostic codes required by those failures. Representative interface:

```python
def sanitize_news_url(value: str | None) -> SanitizedNewsUrl | None: ...
def parse_news_timestamp(value: str | None, *, timezone_name: str | None,
                         policy: NewsDateOnlyPolicy, field: str,
                         received_at: datetime) -> ParsedNewsTimestamp | None: ...
```

- [ ] Re-run the focused test, refactor only after green, then run all existing adapter-contract/model tests.
- [ ] Commit `feat: add offline news provider contract`.

### Task 2: Deterministic normalization

**Files:**
- Create: `src/squeeze_core/adapters/news/normalizer.py`
- Modify: `src/squeeze_core/adapters/news/__init__.py`
- Create: `tests/adapters/news/test_normalizer.py`
- Create: `docs/adr/0020-news-publication-and-receipt-availability.md`
- Create: `docs/adr/0021-explicit-symbol-association-only.md`
- Create: `docs/adr/0022-immutable-news-updates-without-semantic-deduplication.md`

**Produces:** `normalize_news_record(record, context) -> NormalizationResult` and `normalize_news_records(records, context) -> NormalizationResult`.

- [ ] Write failing tests for complete and partial records; required/invalid headlines; missing summary/publisher/author/URL/publication; source-supplied summaries only; explicit/multiple/empty/missing symbols; original publication versus update; provider availability/capture/receipt/effective separation; all date-only policies; provider-ID and deterministic fallback identity; lifecycle statuses; revision links; exact duplicates; same-ID conflicts; stable diagnostics, raw hashes, provenance, IDs, and ordering.
- [ ] Run the focused test and verify failures are caused by missing normalizer behavior.
- [ ] Implement minimal normalization that emits exactly one `NEWS_ITEM` observation per accepted provider record with:

```python
Observation(
    event_type=EventType.NEWS_ITEM,
    symbol=None,
    source_timestamp=availability,
    received_timestamp=context.ingested_at,
    effective_timestamp=max(availability, context.ingested_at),
    payload=NewsItemPayload(...),
)
```

- [ ] Implement deterministic exact-duplicate suppression, same-ID conflict preservation, and explicit parent/correlation links without semantic comparison.
- [ ] Run news tests plus all earlier adapter and canonical serialization/hash tests.
- [ ] Add ADRs 0020–0022 from green behavior and commit `feat: add deterministic news normalization`.

### Task 3: Evidence eligibility and coverage

**Files:**
- Modify: `src/squeeze_core/evidence/models.py`
- Modify: `src/squeeze_core/evidence/policy.py`
- Modify: `src/squeeze_core/evidence/builder.py`
- Modify: `src/squeeze_core/evidence/__init__.py`
- Create: `tests/evidence/test_news_timeline.py`
- Modify: `tests/evidence/test_selection_and_coverage.py`

**Produces:** `CoverageDomain.NEWS`, `include_news_domain`, news-specific evidence diagnostics, and conditional news ages.

- [ ] Write failing tests proving publication/provider availability, receipt, and effective gates independently; explicit association inclusion; missing/empty/different-symbol exclusion; pre-update historical stability; date-only non-prematurity; independent `NEWS` coverage; missing-is-not-neutral; and publication/update/availability/capture age separation.
- [ ] Run focused evidence tests and confirm the news domain and age fields are absent.
- [ ] Implement news-aware association before the generic envelope-symbol test, strict source/receipt/effective gates, conditional `ObservationAge` fields using `exclude_if`, and deterministic coverage/diagnostics.
- [ ] Run focused tests plus all Phase 1C–1F evidence and hash tests.
- [ ] Commit `feat: enforce news publication and receipt eligibility`.

### Task 4: Lifecycle, conflicts, and syndication

**Files:**
- Modify: `src/squeeze_core/evidence/models.py`
- Modify: `src/squeeze_core/evidence/conflicts.py`
- Modify: `src/squeeze_core/evidence/builder.py`
- Create: `tests/evidence/test_news_conflicts.py`

**Produces:** conditional `NewsRelationship` objects and news structural conflicts.

- [ ] Write failing tests for original/update/correction/withdrawal/deletion relationships, missing relationship, exact duplicate, same provider ID changed content, same canonical URL changed headline/publication/symbols, same headline different URLs, same URL across providers, deterministic syndication, no semantic-similarity deduplication, no merge, no provider winner, and stable IDs/order.
- [ ] Run focused tests and confirm news relationship/conflict behavior is absent.
- [ ] Implement relationship construction only from explicit provider IDs, canonical URLs, and provider-declared links. Add structural comparisons for provider record ID, canonical URL, headline, publication time, and explicit symbol tuple while treating declared lifecycle progression as linked immutable evidence.
- [ ] Run all conflict, timeline, and evidence tests.
- [ ] Commit `feat: preserve immutable news lifecycle and syndication`.

### Task 5: Fixtures and replay

**Files:**
- Create: `tests/fixtures/providers/news/fixture_metadata.json`
- Create: `tests/fixtures/providers/news/context.json`
- Create: `tests/fixtures/providers/news/representative_cases.json`
- Create: `tests/fixtures/providers/news/edge_cases.json`
- Create: `tests/fixtures/providers/news/update_cases.json`
- Create: `tests/fixtures/providers/news/syndication_cases.json`
- Create: `tests/fixtures/evidence/mixed_phase_1g_cases.json`
- Create: `tests/fixtures/evidence/news_availability_timeline.json`
- Create: `tests/fixtures/evidence/expected_phase_1g_bundle_metadata.json`
- Create: `tests/fixtures/evidence/normalized_phase_1g_point_in_time.jsonl`
- Create: `tests/phase_1g_fixture_builders.py`
- Create: `tests/adapters/news/test_provider_fixtures.py`
- Create: `tests/evidence/test_phase_1g_replay_integration.py`

**Produces:** all required provider cases, the immutable `TESTA` lifecycle, mixed Phase 1G scenarios, canonical observations, strict replay, timeline bundles, and committed hashes.

- [ ] Write failing fixture tests for every required metadata key and origin, all 35 provider cases, synthetic domains/symbols, no live/sensitive content, no interpretation fields, mixed-domain independence, timeline history, repeated generation, strict replay, and all Phase 1A–1F anchors.
- [ ] Add representative and synthetic JSON using only `TESTA`, `TESTB`, `TESTC`, `news.example.invalid`, and `publisher.example.invalid`.
- [ ] Implement the deterministic builder and generate artifacts twice. Assert byte equality and record raw-record, original/update/withdrawal observation, JSONL, replay, timeline, and bundle hashes.
- [ ] Run fixture, replay, timeline, compatibility, and isolation tests.
- [ ] Commit `test: add news availability and lifecycle fixtures`.

### Task 6: Offline CLI

**Files:**
- Modify: `src/squeeze_core/__main__.py`
- Modify: `tests/test_cli.py`

**Produces:** `normalize-provider --provider news`; existing evidence and timeline commands accept news without a parallel command framework.

- [ ] Write failing CLI tests for representative normalization, case selection, rejection/nonzero exit, stable machine-readable output, evidence/timeline NEWS coverage, lifecycle relationships, local-file-only behavior, and absence of sentiment/catalyst/score/rank/recommendation fields.
- [ ] Route news through the existing fixture/context loading, normalization result, canonical serialization, evidence, and timeline paths.
- [ ] Run CLI tests and each documented command twice.
- [ ] Commit `feat: extend offline cli for news evidence`.

### Task 7: Documentation and final verification

**Files:**
- Create: `docs/providers/news-offline-normalization.md`
- Create: `docs/news-availability-semantics.md`
- Create: `docs/news-update-and-withdrawal-timeline.md`
- Create: `docs/phase-1g-progress.md`
- Modify: `README.md`
- Modify: `docs/architecture.md`
- Modify: `docs/adapter-contract.md`
- Modify: `docs/observation-contract.md`
- Modify: `docs/field-semantics.md`
- Modify: `docs/cross-source-evidence.md`
- Modify: `docs/point-in-time-evidence-policy.md`
- Modify: `docs/testing-and-validation.md`

**Produces:** complete objective semantics, commands, fixture provenance, deterministic anchors, limitations, and final verification evidence.

- [ ] Document only implemented behavior: evidence basis, aliases, payload compatibility, text/URL/symbol/timestamp policies, lifecycle, duplicates/conflicts/syndication, coverage, ages, fixtures, replay, CLI, and explicit interpretation exclusions.
- [ ] Run the full pytest suite and every documented validate/replay/normalize/build/timeline command.
- [ ] Regenerate Phase 1G artifacts twice and verify all legacy and new hashes from fresh bytes.
- [ ] Scan source/tests/fixtures/docs for credentials, private/live URLs, `.env`, network/download/browser/provider SDK/database/order/GUI/wall-clock/random/model/embedding/fuzzy/LLM/entity/sentiment/catalyst/strategy behavior.
- [ ] Verify all three archived repositories remain clean at `0897562e…`, `6dbefd1a…`, and `84f770dd…`.
- [ ] Commit `docs: document point-in-time objective news evidence`.
- [ ] Verify branch, HEAD, log, remotes, and clean tree; do not push, merge, or begin Phase 1H.
