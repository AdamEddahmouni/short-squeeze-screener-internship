# Phase 1F Offline Trading-Halt Evidence Design

## Scope and evidence basis

Phase 1F adds deterministic offline normalization of a narrow exchange-shaped trading-halt lifecycle record and extends point-in-time evidence with objective halt state, public/local availability, immutable updates, duplicate/conflict preservation, coverage, and distinct ages. It answers whether eligible evidence says a security was halted or resumed at a requested time and which announcements were then public and locally received. It does not predict post-resumption price direction or create a signal, score, rank, recommendation, alert, or trade.

The read-only archive search covered both archived code repositories, their current nested application, legacy data, documentation, tests, prototypes, and text/JSON/CSV files while excluding credentials, token files, virtual environments, caches, binaries, and Git internals. No exchange halt record, halt parser, cached halt table, halt-code mapping, quote-resumption record, trade-resumption record, or exchange-status structure was found. The relevant paths and dispositions are:

| Path | Fields present | Basis | Timestamp semantics | Fixture use |
|---|---|---|---|---|
| `docs/reconstruction/06-data-source-map.md` | Statement that Nasdaq halt data is not implemented | Recorded audit conclusion | None | Usable only to document absence |
| `archived-project-code/original-short-squeeze-code-archived/IST495/ScreenerProject/data/labeled_data.csv` | News headlines containing the word “halt” | Recorded news-training text, not exchange status | No halt lifecycle timestamps | Unusable |
| `archived-project-code/adams-short-squeeze-code-archived/app/ScreenerProject/data/labeled_data.csv` | Same class of news headlines | Recorded news-training text, not exchange status | No halt lifecycle timestamps | Unusable |
| `archived-project-code/original-short-squeeze-code-archived/IST495/flagged_articles_log.txt` | Product/program pauses and resumptions in headlines | Recorded news log, not exchange status | Article/log context only | Unusable |
| `archived-project-code/adams-short-squeeze-code-archived/app/ScreenerProject/core/ib_api.py` | “resume” in gateway recovery prose | Operational code comment | No market-event time | Unusable |

Provider-shape fixtures are therefore `SANITIZED_REPRESENTATIVE_SAMPLE`; lifecycle, ambiguity, invalid, duplicate, revision, and conflict fixtures are `SYNTHETIC_EDGE_CASE`. No Phase 1F fixture is `SANITIZED_RECORDED_SAMPLE`.

All input is local JSON. Phase 1F contains no Nasdaq/NYSE/exchange connection, halt-list download, HTTP/FTP/WebSocket client, authentication, credential or `.env` read, database, browser, GUI, live alert, order API, or live provider integration.

## Canonical contract decision

The existing canonical contract already binds `EventType.TRADING_HALT` to `TradingHaltPayload(halt_status, halt_reason, halt_time, resume_time)`. Three approaches were considered:

1. Add halt code, announcement, exchange, session date, and four resumption fields to the payload. Although additive at validation time, defaulted fields would appear during canonical serialization of old fixtures and change Phase 1A–1E hashes.
2. Keep the payload unchanged, use one immutable observation per lifecycle announcement, and retain lifecycle-specific distinctions in structured provider metadata. This preserves compatibility while exposing objective status and the principal halt/resume times canonically.
3. Put the complete event only in provenance. This preserves hashes but weakens canonical halt-state consumption.

Approach 2 is selected. Schema remains `1.0.0`; no envelope, enum, payload, or binding change is required.

- `halt_status` is a normalized objective lifecycle status.
- `halt_reason` preserves supplied objective reason text or remains null; codes are not expanded into reasons without a committed mapping.
- `halt_time` is the defensible halt-effective time when known.
- `resume_time` is populated only for an actual quote- or trade-resumption observation, never for a merely scheduled resumption.
- `source_timestamp` is explicit publication time when supplied, otherwise the announcement time when the provider shape declares it public.
- `received_timestamp` is `AdapterContext.ingested_at`.
- `effective_timestamp` is `max(source_timestamp, received_timestamp)`.
- `exchange` remains the existing envelope exchange.
- halt code, announcement representation, publication basis, session date, scheduled quote/trade times, actual quote/trade times, provider halt/event/record IDs, revision status, superseded record ID, and capture facts remain structured provider metadata.
- `parent_observation_ids` and `correlation_id` link immutable revisions when the prior record is present.

This limitation is explicit: canonical consumers can read objective status, halt time, and actual resume time without provider metadata, while precise scheduled-versus-actual and quote-versus-trade fields require the documented Phase 1F metadata contract.

## Provider model and aliases

`TradingHaltRecord` is immutable, forbids unknown fields, and requires `source_record_id`, `provider_schema=TRADING_HALT_V1`, `record_type=TRADING_HALT`, fixture origin, symbol, and lifecycle status. Stable fields are symbol, exchange/market, halt/event/provider record IDs, halt code, reason text, announcement, halt-effective, scheduled/actual quote resumption, scheduled/actual trade resumption, publication, session date, timezone, revision status/number, superseded record ID, capture timestamp, and sanitized provider metadata.

Documented aliases are conservative: `ticker` for `symbol`, `market` for `exchange`, `reason_code` for `halt_code`, `reason` for `reason_text`, `announcement_datetime` for `announcement_at`, `halt_datetime` for `halt_at`, `quote_resume_scheduled_at` for `quote_resumption_scheduled_at`, `quote_resume_at` for `quote_resumed_at`, `trade_resume_scheduled_at` for `trade_resumption_scheduled_at`, `trade_resume_at` for `trading_resumed_at`, `published_at` for `publication_at`, and `record_status` for `status`. Alias collisions reject rather than silently choosing a value.

Supported statuses are `HALT_ANNOUNCED`, `HALT_ACTIVE`, `QUOTE_RESUMPTION_SCHEDULED`, `QUOTE_RESUMED`, `TRADE_RESUMPTION_SCHEDULED`, `TRADING_RESUMED`, `HALT_CANCELLED`, `HALT_UPDATED`, and `UNKNOWN`. They are objective event states, not strategy labels.

## Halt identifiers, codes, reasons, and multiple events

Provider halt/event ID is preferred for grouping distinct halt lifecycles. When absent, a deterministic event key uses symbol, exchange, session date, and halt-effective representation, while retaining partial quality. Symbol plus session date alone never merges events. Provider record ID identifies a particular announcement/update and may differ across revisions.

Halt codes are trimmed and uppercased only for stable comparison while the original representation remains metadata. Known, unknown, and missing codes are all representable. Phase 1F includes no broad taxonomy. A small fixture-documented known-code set exists only to distinguish `known` from `unknown`; it does not infer reason or direction. Provider reason text is preserved independently. Missing code or reason produces diagnostics, not invented content.

## Timestamp, session, and timezone semantics

Announcement, halt-effective, quote-resumption, trade-resumption, publication, received, and effective times remain distinct. Session date is descriptive and never grants availability.

Exact timestamps require an embedded offset or explicit timezone. A date-only value is valid only for session date, not as a precise halt or availability time. A time-only halt/resumption value requires both an explicit session date and timezone and is combined deterministically. A time-only value without either rejects. Unknown timezone rejects precise normalization rather than assuming UTC. Daylight-saving conversion uses the standard library `zoneinfo` database.

Public availability precedence is explicit publication time, then public announcement time. Capture time alone cannot establish availability. Missing publication and announcement rejects because point-in-time eligibility cannot be defended. Receipt before a claimed later public time is retained with a warning and effective time waits for publication. Publication before receipt is normal. Halt-effective time can precede availability and never backdates the observation.

## Scheduled and actual resumption

Scheduled quote resumption, actual quote resumption, scheduled trade resumption, and actual trade resumption are four independent fields. Scheduled times never populate canonical `resume_time`. Actual quote/trade observations populate `resume_time` with their matching actual time and retain the exact field identity in metadata. A later actual time does not overwrite an earlier schedule; it creates a new observation.

An indefinite halt has no scheduled or actual resumption and remains `HALT_ACTIVE` or `UNKNOWN` according to eligible explicit evidence. A changed schedule is a new `HALT_UPDATED` or scheduling observation linked to the prior record. Cancellation is a new `HALT_CANCELLED` observation. A cancellation of a schedule is not evidence that trading resumed.

## Immutable revisions, duplicates, and conflicts

Every update is normalized independently with its own raw hash, publication, receipt, effective time, provider record identity, status, and optional parent. A resolvable `supersedes_source_record_id` creates deterministic parent/correlation links. A missing relationship is retained as partial evidence with a stable diagnostic. Historical observations are never mutated or deleted.

An exact duplicate is the same source identity and raw hash and is emitted once with a duplicate diagnostic. The same source record ID with different content preserves all observations as a provider-record conflict. Same halt event with differing nonmissing halt codes or incompatible scheduled resumption times preserves a structural conflict; no winner is selected and times are not averaged. Scheduled and actual values, quote and trade stages, and different effective lifecycle times are compatible temporal progression unless their same-semantic values conflict. Separate halt event IDs remain separate even on the same symbol/session date.

## Point-in-time eligibility and objective halt state

`TRADING_HALT` observations are eligible only when source/publication, receipt, and effective timestamps are all at or before `as_of`. Maximum future skew never relaxes the source or receipt gates. A halt that occurred before `as_of` but was announced later is excluded. An announcement published before `as_of` but received later is excluded. Later updates never rewrite an earlier bundle.

`HaltStateSummary` is conditionally present only when the halt domain is active and contains the objective state, halt event keys, supporting observation IDs, and conflict IDs. States are `NOT_OBSERVED`, `HALT_ANNOUNCED`, `HALTED`, `QUOTE_RESUMPTION_SCHEDULED`, `QUOTES_RESUMED`, `TRADE_RESUMPTION_SCHEDULED`, `TRADING_RESUMED`, `CANCELLED`, `CONFLICTED`, and `UNKNOWN`.

Derivation uses eligible observations only, grouped by deterministic halt event and ordered by canonical replay key. Explicit lifecycle status advances state; scheduled events never become actual; quote resumption never becomes trading resumption; cancellation does not imply resumption. Unresolved same-event code or schedule conflicts yield `CONFLICTED`. Unknown/partial objective status yields `UNKNOWN`. Supporting IDs are sorted deterministically. Price, volume, news, later trades, and strategy fields never participate.

## Coverage, conflicts, and ages

`TRADING_HALTS` is an independent coverage domain activated by input or `include_trading_halts_domain`. It uses existing `PRESENT`, `MISSING`, `STALE`, `DELAYED`, `UNKNOWN_FRESHNESS`, `CONFLICTED`, `INVALID`, and `PARTIAL` states. Absence of halt evidence is not proof that no halt occurred and carries no directional meaning.

Included halt observations add conditional age metadata:

- `announcement_age_ms`: age from public announcement/publication;
- `availability_age_ms`: age from effective local availability;
- `halt_event_age_ms`: age from halt-effective time when known;
- `resumption_event_age_ms`: age from an actual quote/trade resumption when known.

These additions are omitted for earlier domains so Phase 1A–1E bundle bytes remain unchanged.

## Diagnostics, replay, fixtures, CLI, and determinism

Adapter diagnostics use stable `HALT_*` codes for structural validation, identity, code state, time precision/timezone, publication/receipt ordering, lifecycle stages, indefinite records, revisions, duplicates, conflicts, partial records, and unsupported types. Evidence diagnostics use stable `EVIDENCE_HALT_*`, lifecycle, conflict, missing-domain, and partial-coverage codes. Ordering is explicit by code, observation ID, domain, and message.

The deterministic pipeline is local halt fixture to pure normalization to canonical `TRADING_HALT` observations to mixed Phase 1F JSONL to strict replay to timeline bundles and objective state. The `TESTA` timeline separates halt at 10:00, public/local announcement at 10:01, scheduled quote resumption and update, actual quotes resumed, scheduled trade resumption, and actual trading resumed. Earlier bundles remain byte-identical after later records are supplied.

`normalize-provider --provider halts` reads local JSON and emits stable machine-readable output. Existing evidence/timeline commands consume halt observations; `build-halt-state` may expose the same objective summary without acquisition. Rejected records return nonzero. Output contains no prediction, sentiment, score, rank, recommendation, entry, exit, or trading action.

All IDs, hashes, diagnostics, relationships, conflicts, coverage, state, replay, and bundle bytes derive only from fixture data, adapter context, normalization version, schema, evidence policy, and `as_of`. No wall clock, random UUID, environment path, unordered iteration, live lookup, or mutable external state participates.

## Testing and boundaries

Tests use red-green-refactor and cover the strict model, aliases, source/raw identity, exact/date-only/time-only/unknown-timezone parsing, lifecycle stages, scheduled/actual separation, indefinite/cancelled/changed resumptions, complete/partial/rejected normalization, duplicates, same-ID conflicts, revision links, public/receipt/effective gates, historical rebuilds, independent coverage, ages, structural conflicts, objective state, strict replay, CLI, fixture provenance, repeated byte identity, Phase 1A–1E hashes, archive cleanliness, and isolation scans.

Phase 1F does not connect to exchanges; download halt lists; issue alerts; infer halt reasons from codes; predict direction or volatility direction; classify catalysts; calculate squeeze probability; score/rank candidates; identify entries/exits; emit trading signals; persist data; add a web API/GUI; trade; or begin Phase 1G.
