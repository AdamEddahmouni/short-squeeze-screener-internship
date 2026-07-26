# Phase 1D Offline FINRA-Shaped Published Short Interest Design

## Scope and evidence basis

Phase 1D adds deterministic offline normalization of a deliberately narrow FINRA-shaped published-short-interest record and extends the existing Phase 1C point-in-time evidence bundle. Its governing question is when the record described the market and when the same record was defensibly available to this system.

The read-only archive search found no FINRA short-interest file, export, table, parser, or recorded provider row. `docs/reconstruction/06-data-source-map.md` explicitly records FINRA short-interest and short-volume feeds as not found. The archived current application contains a mocked Yahoo metadata shape with `sharesShort`, `dateShortInterest`, `floatShares`, and `shortPercentOfFloat`; it proves representative field concepts, not FINRA delivery, publication timing, or recorded provenance. Phase 1D therefore uses `SANITIZED_REPRESENTATIVE_SAMPLE` for valid shape fixtures and `SYNTHETIC_EDGE_CASE` for invalid, timing, duplicate, revision, and conflict fixtures. No fixture is a `SANITIZED_RECORDED_SAMPLE`.

All inputs are local JSON. There is no FINRA connection, download, HTTP/FTP client, authentication, credential read, database, GUI, strategy, score, rank, recommendation, or trading behavior.

## Existing-contract decision

`PublishedShortInterestPayload` already has the canonical fields required for this phase: nullable `short_shares`, `float_shares`, `short_float_percent`, `settlement_date`, `publication_date`, and `days_to_cover`. Adding defaulted payload or envelope fields would change canonical serialization of existing Phase 1A observations and replay hashes. Phase 1D therefore makes no canonical payload or envelope change and keeps schema `1.0.0`.

The following semantics use existing canonical mechanisms:

- `settlement_date` is the market reporting period described by the value.
- `publication_date` retains the provider's published calendar date without inventing time precision.
- `source_timestamp` is the normalized publication-availability boundary used by the supported offline shape. A separate provider row timestamp is retained in provenance metadata.
- `received_timestamp` is `AdapterContext.ingested_at`.
- `effective_timestamp` is `max(publication_availability, received_timestamp)` and is never the settlement date.
- `parent_observation_ids` links a correction or revision to the prior immutable observation when batch evidence supports the relationship.
- `correlation_id` groups the immutable revision chain or same-period conflict set.
- provider-specific revision status, revision number, source record linkage, market/exchange, average daily volume, previous short shares, capture time, and provider timestamp remain in provenance metadata rather than becoming provider-specific canonical fields.

This is backward-compatible and preserves all existing serialized observations, IDs, fixture bytes, replay hashes, and Phase 1C bundle hashes when no Phase 1D observation is present.

## FINRA-shaped provider record

`FinraShortInterestRecord` is immutable, forbids unknown fields, and supports only documented representative aliases. It requires `source_record_id`, `provider_schema=FINRA_SHORT_INTEREST_V1`, `record_type=PUBLISHED_SHORT_INTEREST`, a valid fixture origin, and a symbol. Supported concepts are short shares, settlement/reporting date, publication value/timezone/policy, prior short shares, average daily volume, provider-published days to cover, provider float, provider short-float percentage with explicit unit, market/exchange, revision status/number/link, provider record ID/timestamp, and capture timestamp.

Daily short-sale-volume record types are rejected with `FINRA_DAILY_SHORT_VOLUME_NOT_SUPPORTED`; no daily short volume is converted into open short positions.

## Date and availability semantics

Full timezone-aware publication timestamps establish exact publication availability. A naive timestamp requires an explicit publication timezone. Unknown timezones reject.

A date-only publication value never becomes midnight UTC implicitly. The record must choose one explicit policy:

- `STRICT_REJECT`: reject because exact availability is unknown.
- `END_OF_PUBLICATION_DATE`: with an explicit timezone, use the next local midnight as a conservative exclusive end-of-day availability boundary and diagnose the policy.
- `INGESTION_TIME_UNCERTAIN_PLACEHOLDER`: use receipt time as an uncertain availability placeholder, mark quality/completeness accordingly, and diagnose that publication precision is unknown.

Missing publication values are rejected unless a distinct timezone-aware provider timestamp is explicitly declared to represent publication availability. Capture time alone cannot establish publication. Receipt before a claimed later publication is retained with a diagnostic, but effective time remains the later publication boundary. Receipt after publication makes effective time the receipt time.

An observation is eligible only when its publication/source timestamp, received timestamp, and effective timestamp are all at or before bundle `as_of`. Effective-time skew never relaxes the publication or receipt gates.

## Numeric and missing-value semantics

Short shares, previous short shares, float, and average daily volume are exact nonnegative whole numbers. Fractional, negative, nonfinite, and unsupported formatted values are invalid and never rounded. `short_shares=0` is a known published zero; missing short shares stays null with partial quality.

Short-float percentage requires `PERCENT_POINTS`, `DECIMAL_FRACTION`, or `FORMATTED_PERCENT_STRING`. Scaling is never inferred from magnitude. Provider-published days to cover is a nonnegative finite decimal and is not silently recomputed. Missing float, percentage, volume, and days to cover remain missing. A zero float is invalid. Locally derived percentages or days to cover are outside the normalizer.

## Revision, duplicate, and conflict semantics

Revision statuses are `ORIGINAL`, `CORRECTED`, `REVISED`, `CANCELLED`, and `UNKNOWN`. Normalizing a batch first emits immutable observations, suppresses exact raw/source-ID duplicates, and then resolves supported `supersedes_source_record_id` links to deterministic parent observation IDs. A later correction never mutates or deletes the original.

Eligible revision chains are represented in the evidence bundle as deterministic `RevisionRelationship` objects. Before correction receipt, only the original is eligible. After correction receipt, both observations remain included and the relationship identifies the later observation as superseding the earlier one. Historical rebuilds therefore remain stable.

Same-symbol, same-settlement-period, same-semantic-field values with no supported supersession link can form a value or duplicate conflict. Different settlement periods form `TEMPORAL_DIFFERENCE`. Published short shares are never compared against Finviz short float, IBKR borrow fee, or IBKR availability. Published short-float percentage is not compared with Finviz short float unless a future explicit methodology/scope policy makes them compatible; Phase 1D diagnoses them as incompatible and does not create a numeric conflict.

## Evidence coverage and age

`PUBLISHED_SHORT_INTEREST` becomes a fourth independent coverage domain. Selection computes `ObservationAge` only for included published-short-interest observations:

- `availability_age_ms` is age from effective availability to bundle `as_of`.
- `reporting_period_age_days` is calendar age from settlement date to bundle `as_of`.

The existing event maximum-age policy continues to govern availability staleness. A separate optional `maximum_reporting_period_age_days` policy governs reporting-period staleness. A newly received old report can therefore have low availability age and high reporting-period age. Coverage can be present, stale, delayed, unknown, conflicted, invalid, or missing without changing other domains.

New optional bundle collections use conditional serialization: they are omitted when empty. Phase 1C bundles with no published-short-interest observations remain byte-identical and retain their hashes.

## Diagnostics, determinism, replay, and CLI

FINRA diagnostics are stable prefixed codes for structural validation, missing/invalid numeric values, unsupported units, missing/invalid settlement/publication values, date-only policy, timezone uncertainty, capture-only timing, receipt/publication ordering, partial records, duplicates, conflicts, revisions, and rejected daily short volume. Evidence diagnostics separately describe not-yet-published, not-yet-received, stale reporting periods, available corrections, supersession, temporal differences, conflicts, and missing coverage. Ordering is explicit and deterministic.

The pipeline is local fixture to normalizer to canonical JSONL to strict replay to point-in-time bundles at several timestamps. IDs and hashes use canonical content only; no wall clock, random UUID, absolute path, environment state, or unordered iteration participates.

`normalize-provider --provider finra` reads a local object/case and returns canonical JSON with nonzero status for rejection. `build-evidence` automatically applies the publication, receipt, effective, reporting-age, conflict, and revision rules. A local `build-evidence-timeline` command may build deterministic bundles for an explicit list of `as_of` timestamps if it can be added without duplicating builder logic.

## Test and fixture design

Tests follow red-green-refactor and cover provider identity/schema/type/origin, supported aliases, exact hashing, full/date-only/missing/invalid timestamps, all numeric unit and missing/zero cases, partial/rejected normalization, daily short-volume rejection, duplicates, revisions, conflicts, eligibility gates, historical rebuilds, independent coverage, reporting versus availability age, replay, CLI, existing hashes, repeated byte identity, and isolation scans.

The deterministic `TESTA` timeline contains settlement, publication, receipt, later correction publication/receipt, and bundles before publication, after publication-before-receipt, after original receipt, before correction receipt, and after correction receipt. Mixed fixtures combine one Finviz snapshot, IBKR fee/availability, and FINRA-shaped published short interest without semantic conflation.

## Boundaries

Phase 1D does not connect to or download from FINRA; normalize daily short-sale volume; prove provider entitlement, schedule, or delivery timing; estimate real-time market-wide short interest; connect to Finviz or IBKR; calculate squeeze probability; score or rank candidates; identify entries/exits; emit trading signals; persist data; or begin Phase 1E.
