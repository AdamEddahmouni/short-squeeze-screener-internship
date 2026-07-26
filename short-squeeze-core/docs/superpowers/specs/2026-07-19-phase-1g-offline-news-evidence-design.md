# Phase 1G Offline Objective News Evidence Design

## Scope and evidence basis

Phase 1G adds deterministic offline normalization of objective news-item metadata and extends point-in-time evidence with explicit publication, provider-availability, capture, receipt, effective, update, correction, withdrawal, deletion, duplicate, conflict, and syndication semantics. It answers which source-supplied news records were actually available to the local system for an explicitly associated symbol at a requested time. It does not decide whether news is positive, negative, bullish, bearish, material, relevant, novel, or actionable.

The read-only archive search covered all three preserved repositories, their tracked and ignored local artifacts, legacy CSV data, ZIP entry names, application code, tests, and reconstruction documentation while excluding credentials, token files, `.env`, caches, virtual environments, and Git internals. The relevant artifacts are:

| Exact path | Fields present | Evidence class | Timing and identity | Fixture disposition |
|---|---|---|---|---|
| `archived-project-code/adams-short-squeeze-code-archived/app/ScreenerProject/core/finviz_api.py` | Finviz-shaped `Title`, `Date`, `Url`, `Ticker` | Recorded source code describing an adapter shape | Raw date only; no saved provider row or provider record ID | Shape basis for representative fixtures only |
| `archived-project-code/adams-short-squeeze-code-archived/app/ScreenerProject/core/yfinance_news_api.py` | Yahoo-shaped `content.title`, `summary`, `pubDate`, `canonicalUrl.url`, `clickThroughUrl.url` | Recorded source code plus mocked representative tests | No saved provider response; ticker association was locally inferred from text | Shape basis for representative fixtures; inferred associations are not reused |
| `archived-project-code/adams-short-squeeze-code-archived/app/ScreenerProject/tests/test_yfinance_news_api.py` | Constructed title, summary, publication time, canonical URL | Mocked representative sample | Invented values, no provider delivery or capture time | Representative shape basis only |
| `archived-project-code/adams-short-squeeze-code-archived/app/ScreenerProject/core/newsapi_news_api.py` | NewsAPI-shaped `title`, `publishedAt`, `url`; local query ticker | Recorded source code describing an adapter shape | No saved response or provider ID; ticker association is request-derived | Shape basis for representative fixtures; query ticker is explicit only when fixture metadata declares it |
| `archived-project-code/adams-short-squeeze-code-archived/app/ScreenerProject/data/news_snapshot.json` | `headline`, `confidence_score`, `tickers`, `url` across 18 rows | Ignored runtime artifact | Provider fallback source is lost; no publication, provider-availability, capture, receipt, or provider ID; records were sentiment-filtered; live URLs include tracking parameters | Unusable as an objective fixture |
| `archive/legacy-data/sample_news_7.06.25.csv`, prototype `sample_news.csv`, and current/original `labeled_data.csv` | `headline`, `price_movement` | Historical model data | No source, URL, ticker, publication, receipt, or provider identity | Unusable |

No defensible saved provider response exists. Every Phase 1G fixture is exactly `SANITIZED_REPRESENTATIVE_SAMPLE` or `SYNTHETIC_EDGE_CASE`; none is `SANITIZED_RECORDED_SAMPLE`.

All inputs are committed local JSON. Phase 1G adds no HTTP, FTP, RSS, browser, WebSocket, provider SDK, authentication, credential read, `.env` read, URL fetch, redirect resolution, article download, database, GUI, order API, sentiment model, embedding, LLM, fuzzy matching, or live provider integration.

## Canonical contract decision

The existing schema already binds `EventType.NEWS_ITEM` to `NewsItemPayload(headline, summary, url, publisher, published_at, associated_symbols)`. Three approaches were considered:

1. Add author, updated time, language, content type, and lifecycle status to the payload. Defaulted fields would enter old canonical serialization and change Phase 1A–1F hashes.
2. Keep the payload unchanged, use one immutable observation per provider record, and retain additional objective metadata in structured provenance. This preserves compatibility and exposes the stable cross-provider core canonically.
3. Put all news fields in provenance. This preserves hashes but weakens canonical news consumption.

Approach 2 is selected. Schema remains `1.0.0`; `NewsItemPayload`, the envelope, event enums, payload enums, and bindings remain unchanged.

- `headline` is required, Unicode-preserving, trimmed, and has repeated whitespace collapsed without rewriting wording, capitalization, or grammar.
- `summary` is only provider-supplied summary or description. Missing remains null. No summary is generated.
- `url` is the sanitized canonical article URL identity when valid; missing remains null and invalid input is diagnosed without being guessed.
- `publisher` is source-supplied. Author is distinct and remains structured provenance.
- `published_at` is the original defensible publication instant. Updated time never overwrites it.
- `associated_symbols` contains only explicit source- or fixture-supplied associations, normalized for case/whitespace and deterministically ordered.
- The envelope `symbol` is null for news observations so a multi-symbol record remains one canonical observation. Symbol-specific evidence membership is determined only from `payload.associated_symbols`.
- `source_record_id` is the provider record ID when present, otherwise a deterministic provider-scoped identity based on sanitized canonical URL and stable raw identity. The fallback is diagnosed and never claims a provider ID.
- `source_timestamp` is explicit provider availability when supplied, otherwise the defensible publication boundary.
- `received_timestamp` is `AdapterContext.ingested_at`.
- `effective_timestamp` is `max(source_timestamp, received_timestamp)`.
- Author, updated time, language, content type, lifecycle status, provider availability, capture time, provider record identity status, canonical URL identity, URL policy version, source shape, and revision facts remain structured provider metadata.

## Offline provider contract and supported aliases

`NewsRecord` is immutable, forbids unknown fields after alias normalization, and requires `provider_schema=NEWS_ITEM_V1`, `record_type=NEWS_ITEM`, fixture origin, source shape, and headline for accepted normal records. It supports stable neutral fields for provider, provider record ID, headline, summary, publisher, author, URL, publication/update/provider-availability/capture timestamps, explicit symbols, language, content type, status, revision relation, and sanitized provider metadata.

Aliases are restricted to archived evidence:

- Finviz shape: `Title -> headline`, `Date -> published_at`, `Url -> url`, `Ticker -> symbols`.
- Yahoo shape: `content.title -> headline`, `content.summary -> summary`, `content.pubDate -> published_at`, `content.canonicalUrl.url` or `content.clickThroughUrl.url -> url`. No ticker is inferred from title or summary.
- NewsAPI shape: `title -> headline`, `description -> summary`, `source.name -> publisher`, `author -> author`, `url -> url`, `publishedAt -> published_at`. A request/query ticker is accepted only through the explicit fixture `symbols` field, never inferred from the query text.

Alias collisions with unequal values reject. No undocumented provider field is silently accepted.

## URL identity and sanitization

URL handling uses only standard-library parsing and never opens a URL.

- Only `http` and `https` are structurally accepted.
- A host is required. Embedded username/password information rejects.
- Scheme and host are lowercased; a default port is removed; path and article-identifying query parameters are preserved.
- Fragments are removed with `NEWS_URL_FRAGMENT_REMOVED`.
- Tracking parameters are removed only by versioned policy `news-url-v1`: keys beginning `utm_` plus exact `gclid`, `fbclid`, `mc_cid`, and `mc_eid`, case-insensitively.
- Remaining query pairs preserve their input order and values. They are not sorted, decoded/re-encoded semantically, or treated as equivalent across distinct URLs.
- Sensitive query keys such as `token`, `api_key`, `apikey`, `auth`, `authorization`, `session`, and `signature` reject rather than being serialized.
- Missing URL is accepted as partial objective metadata. Invalid or sensitive URL input is omitted from canonical payload with stable diagnostics when the remaining record is defensible.

Canonical URL equality is exact equality after this policy. No redirect, canonical-link lookup, domain heuristic, fuzzy title comparison, or semantic similarity is used.

## Symbol association

Only explicit source- or fixture-supplied symbols are retained. Values are trimmed, uppercased, validated as conservative symbol tokens, deduplicated, and sorted. A missing association and an explicit empty list remain distinguishable in provenance and diagnostics even though the canonical tuple is empty in both cases.

News observations always keep envelope `symbol=null`; this prevents duplication or privileging the first symbol. A news observation enters a symbol-specific evidence bundle only when the requested normalized symbol occurs in `payload.associated_symbols`. Headline, summary, publisher, URL, prior observations, company names, and query text are never used for entity resolution.

## Timestamp and date-only policies

Original publication, provider-declared update, provider availability, capture, local receipt, and effective availability are distinct.

Exact timestamps require an embedded numeric offset or an explicit context/source timezone. Unknown timezone never silently becomes UTC. Capture time is descriptive and cannot establish public availability.

`STRICT` rejects a date-only publication or update when that value is required to establish availability. `CONSERVATIVE_END_OF_DAY` resolves the date at `23:59:59.999999` in the explicitly supplied timezone and admits it no earlier than that boundary. `UNCERTAIN_PLACEHOLDER` uses receipt as the availability placeholder, keeps publication precision uncertain in provenance, and emits diagnostics. It does not fabricate midnight or assert provider publication time.

When provider availability is exact, a missing publication instant may be accepted with `published_at=null`; provider availability still gates source time. When neither publication nor provider availability is defensible, strict/conservative modes reject and uncertain mode may accept only at receipt with unknown-availability quality and diagnostics.

Publication after receipt and provider availability after receipt are preserved with warnings; effective time waits for the later defensible boundary. Updated time never substitutes for original publication.

## Immutable lifecycle, duplicates, conflicts, and syndication

Statuses are `ORIGINAL`, `UPDATED`, `CORRECTED`, `WITHDRAWN`, `DELETED`, and `UNKNOWN`. They are objective source states, not direction or materiality labels.

Every lifecycle record becomes its own observation with its own raw hash, source identity, availability, receipt, effective time, headline/metadata snapshot, and optional parent. A source-supplied `supersedes_provider_record_id` is preferred. An explicit prior canonical URL may link when policy and provider identity support it. Similar headlines never create a link.

An exact raw duplicate is emitted once with a deterministic diagnostic. Same provider plus same provider record ID with changed content preserves every observation as conflicted; no winner is selected. Same canonical URL with changed headline, publication time, or explicit symbols produces field-specific structural conflicts unless an explicit revision relationship explains compatible progression. Same headline with different URLs remains separate and is not a duplicate.

Same canonical URL across different providers produces a deterministic `NewsRelationship(kind=SYNDICATED)` between independent observations. It does not merge, suppress, select, or claim that the article bodies are identical. Provider observations retain independent timing and provenance. Relationship and conflict IDs derive only from sorted observation IDs and relationship semantics.

## Point-in-time eligibility, coverage, relationships, and ages

`NEWS` is an independent coverage domain activated by news input or `include_news_domain`. News is never compared with market snapshots, borrow evidence, published short interest, SEC filings, or trading halts as a competing value.

A news observation is eligible only when:

1. the requested symbol is explicitly in `associated_symbols`;
2. original publication/provider availability is no later than `as_of`;
3. local receipt is no later than `as_of`;
4. effective time is no later than `as_of`.

Maximum future skew never relaxes the publication/availability or receipt gates. Later updates, corrections, withdrawals, and deletions cannot alter an earlier bundle. Earlier bundles rebuilt with the full later observation set remain byte-identical.

Coverage uses existing states `PRESENT`, `MISSING`, `STALE`, `DELAYED`, `UNKNOWN_FRESHNESS`, `CONFLICTED`, `INVALID`, and `PARTIAL`. Missing news means only that eligible objective news evidence is absent; it is not neutral or negative evidence. Presence is not a catalyst signal.

News conditionally extends `ObservationAge` with `publication_age_ms`, `update_age_ms`, `capture_age_ms`, and the existing `availability_age_ms`. Additions use `exclude_if` so Phase 1A–1F bundle bytes remain unchanged. `NewsRelationship` conditionally records `REVISION`, `CORRECTION`, `WITHDRAWAL`, `DELETION`, and `SYNDICATED` links. Existing generic revision relationships remain available for explicit parent chains; no parallel bundle framework is introduced.

## Diagnostics, replay, fixtures, CLI, and determinism

Adapter diagnostics use stable `NEWS_*` codes for structure, headline/text, URL, timing, association, partial records, lifecycle, duplicates, conflicts, syndication, and unsupported shapes. Evidence diagnostics use stable `EVIDENCE_NEWS_*` codes for publication, availability, receipt, association, updates, withdrawals, duplicates, conflicts, syndication, missing coverage, and partial coverage. Diagnostics are sorted deterministically by code, field, source record ID, and message.

The deterministic pipeline is local news fixture to pure normalization to canonical `NEWS_ITEM` observations to mixed Phase 1G JSONL to strict replay to timeline bundles. The `TESTA` timeline contains original publication, provider availability, local receipt, update availability/receipt, and withdrawal availability/receipt. Historical bundles remain stable as later records are added.

`normalize-provider --provider news` reads local fixtures and context only. Existing `build-evidence` and `build-evidence-timeline` commands consume news observations and emit coverage, relationships, conflicts, ages, and diagnostics. Rejected records return nonzero. No objective requirement needs a separate state command, so Phase 1G does not add one.

All observations, raw hashes, diagnostics, conflicts, relationships, coverage, replay output, bundle IDs, and bundle hashes derive solely from fixture data, adapter context, policy/version, schema, and `as_of`. No wall clock, random UUID, environment path, unordered iteration, URL lookup, model, embedding, or mutable external state participates.

## Testing and explicit exclusions

Tests use red-green-refactor and cover strict provider models, supported aliases, raw/source identity, Unicode and whitespace, URL policy, explicit/missing/empty symbols, timestamp precision/policies, partial/rejected records, every lifecycle status, duplicate/conflict/syndication handling, source/receipt/effective gates, historical rebuilds, independent coverage, all news age dimensions, mixed replay, CLI, fixture provenance, repeated byte identity, and every Phase 1A–1F compatibility anchor.

Phase 1G does not connect to news providers or RSS; fetch article pages; run sentiment; classify catalysts, topics, relevance, materiality, direction, novelty, or entities; infer tickers; semantically deduplicate; generate summaries; calculate squeeze probability; score or rank candidates; recommend trades; identify entries/exits; persist data; add a GUI/web API; trade; or begin Phase 1H.
