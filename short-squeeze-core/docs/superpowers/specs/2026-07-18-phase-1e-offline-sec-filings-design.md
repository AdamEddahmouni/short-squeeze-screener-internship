# Phase 1E Offline SEC Filing Evidence Design

## Scope and evidence basis

Phase 1E adds deterministic offline normalization of a deliberately narrow SEC/EDGAR-shaped filing metadata record and extends point-in-time evidence with filing availability, amendment, duplicate, conflict, and age semantics. It answers which filing metadata was publicly available and locally received by a requested time. It does not read filing bodies or infer sentiment, catalyst direction, dilution, squeeze potential, or trading action.

The read-only archive search found no accession number, CIK, EDGAR metadata row, filing URL, acceptance timestamp, period-of-report record, SEC parser, or saved filing fixture. Matches were limited to unrelated news-training headlines containing “SEC” or “filing.” Those headlines are not filing metadata and are unusable. Valid shape fixtures therefore use `SANITIZED_REPRESENTATIVE_SAMPLE`; invalid, timing, duplicate, amendment, and conflict fixtures use `SYNTHETIC_EDGE_CASE`. No Phase 1E fixture is a `SANITIZED_RECORDED_SAMPLE`.

All inputs are local JSON. There is no SEC.gov/EDGAR connection, URL opening, download, HTTP/FTP client, authentication, credential read, database, browser, document/XBRL parser, GUI, strategy, score, rank, recommendation, or trading behavior.

## Contract decision and alternatives

Three approaches were evaluated:

1. Add acceptance, publication, and amendment fields to `SecFilingPayload`. This is semantically direct but defaulted fields would change canonical serialization and hashes for old observations.
2. Keep the payload unchanged and use the established envelope, provenance, and relationship mechanisms. This preserves schema and hashes while retaining all required metadata explicitly.
3. Put the entire filing record in opaque provenance. This preserves compatibility but makes core filing identity and reporting fields unavailable to canonical consumers.

Approach 2 is selected. `SecFilingPayload` already contains stable provider-neutral identity and description fields: `form_type`, `accession_number`, `filed_at`, `period_of_report`, `primary_document`, and `issuer_cik`. Schema remains `1.0.0`; no canonical payload, envelope, enum, or event binding changes are required.

- `filed_at` retains the provider filing value. A date-only value uses an explicit conservative or uncertain policy and is never presented as exact.
- `source_timestamp` is the defensible public-availability boundary: explicit publication time when present, otherwise SEC acceptance time when declared public, otherwise an explicit date-only policy result.
- `received_timestamp` is `AdapterContext.ingested_at`.
- `effective_timestamp` is `max(public_availability, received_timestamp)` and is never the period of report.
- `parent_observation_ids` links an amendment to an original filing when the referenced accession is present in the normalized batch.
- `correlation_id` groups a filing/amendment chain or same-accession conflict set.
- acceptance/publication source text and precision, explicit amendment flag, amended accession, company name, provider record ID, file/film numbers, document count, fiscal year end, sanitized URL/path facts, capture timestamp, and record status remain structured provenance metadata.

## Provider model and aliases

`SecFilingRecord` is immutable, forbids unknown fields, and accepts only documented aliases. It requires `source_record_id`, `provider_schema=SEC_FILING_V1`, `record_type=SEC_FILING`, a valid fixture origin, and a symbol. Supported concepts are CIK, ticker/symbol, company name, form, accession, filed value/timezone/policy, SEC acceptance value/timezone, explicit publication value/timezone/policy, period of report, primary document, sanitized filing reference, amendment flag and prior accession, file/film numbers, document count, fiscal year end, provider record ID, capture timestamp, and record status.

Aliases are conservative: `ticker` for `symbol`, `cik` for `issuer_cik`, `form` for `form_type`, `acceptance_datetime` for `accepted_at`, `publication_datetime` for `published_at`, `filing_href` for `filing_url`, and `record_status` for status. Normalization does not depend on unknown fields.

## Identity and parsing

CIK is a string identifier. One to ten ASCII digits are accepted and left-padded to ten digits. Missing CIK can produce a partial filing when symbol and accession are valid. Invalid characters or more than ten digits reject; no external lookup or symbol correction occurs.

Accession is required. Canonical `##########-##-######` and compact 18-digit forms are accepted; the compact form is expanded deterministically. Other lengths, characters, and ambiguous transformations reject. Canonical accession plus canonical CIK, form, and source record identity participate in the observation/raw identity through canonical payload and source fields.

Form strings are trimmed, uppercased, and validated with a conservative printable structure supporting spaces, digits, letters, hyphens, and an optional `/A` suffix. Explicit amendment metadata is authoritative. A `/A` suffix can corroborate but cannot invent a relationship. Contradictory explicit and suffix indicators produce a diagnostic and conflicted/partial quality rather than silent correction.

Primary documents are basename-only safe identifiers. Absolute paths, traversal, query strings, fragments, credentials, or live remote URLs are never retained canonically. A filing URL/path is omitted or reduced to non-live sanitized metadata with `SEC_REMOTE_URL_SANITIZED`; tests never access it.

## Timestamp and availability semantics

Filed, accepted, published, received, and effective values remain distinct. Exact timestamps require an embedded offset or an explicit timezone. A date-only filed value does not establish availability and is represented with an explicit filed-date policy and uncertainty metadata.

Public availability is selected in this order:

1. exact explicit publication timestamp;
2. exact SEC acceptance timestamp when the record declares acceptance as the public boundary;
3. date-only publication under an explicit policy.

Date-only publication policies are `STRICT_REJECT`, `END_OF_PUBLICATION_DATE`, and `INGESTION_TIME_UNCERTAIN_PLACEHOLDER`. End-of-day means the next local midnight boundary in an explicit timezone; it prevents premature inclusion. The placeholder uses receipt time and marks uncertainty. Missing exact or policy-backed public availability rejects; capture time alone cannot prove availability.

Receipt before a claimed later public time is retained with a diagnostic, but effective time remains the later boundary. A bundle includes a filing only when public/source, received, and effective timestamps are all at or before `as_of`. Maximum future skew never relaxes public or receipt gates.

## Amendments, duplicates, corrections, and conflicts

Originals and amendments are separate immutable observations. An amendment with a resolvable `amends_accession_number` receives the original observation ID as a parent and shares a deterministic correlation ID. Missing links are diagnosed and retained as partial evidence when identity and availability remain defensible. An amendment never mutates or deletes its original and cannot alter an earlier bundle.

Exact duplicate source records are suppressed deterministically with a duplicate diagnostic. Same accession with materially different canonical metadata produces a conflict diagnostic and preserved conflict observations. Different accessions, including amendments and filings for different periods, are temporal differences rather than duplicate accession conflicts. Provider corrected metadata is a new immutable observation; Phase 1E does not select a winner.

Filing conflict comparison is metadata-specific: same canonical accession can compare form, filed time, period of report, primary document, and CIK. SEC filing metadata is never compared numerically or semantically with short interest, borrow fee, borrow availability, or market snapshots.

## Evidence coverage and ages

`SEC_FILINGS` is an independent evidence domain. A policy flag can require it even when no SEC observations are supplied. Coverage can be `PRESENT`, `MISSING`, `PARTIAL`, `STALE`, `DELAYED`, `UNKNOWN_FRESHNESS`, `CONFLICTED`, or `INVALID` using existing states where available. Absence is never zero, negative evidence, or lack of a catalyst.

Included SEC observations carry separate ages:

- `availability_age_ms`: age from effective local availability;
- `filing_age_ms`: age from the public-availability/acceptance source timestamp;
- `reporting_period_age_days`: calendar age from period of report, when present.

New optional bundle fields serialize conditionally so Phase 1A–1D bundles with no SEC domain remain byte-identical.

## Diagnostics, determinism, replay, fixtures, and CLI

SEC adapter diagnostics use stable `SEC_*` codes for structural validation, CIK/accession/form parsing, timestamp precision and ordering, missing metadata, amendments, duplicates, conflicts, sanitization, partial records, and unsupported types. Evidence diagnostics use stable `EVIDENCE_SEC_FILING_*` and `EVIDENCE_MISSING_SEC_FILINGS` codes for eligibility, coverage, amendments, duplicates, conflicts, and temporal differences. Diagnostic ordering is explicit.

The deterministic pipeline is local SEC-shaped fixture to normalizer to canonical `SEC_FILING` observation to mixed Finviz/IBKR/FINRA/SEC JSONL to strict replay to timeline bundles. It uses no wall clock, random UUID, environment path, unordered iteration, URL resolution, or external state.

The `TESTA` timeline has an original filing accepted/published/received, a later amendment accepted then received, and bundles before acceptance, after acceptance-before-receipt, after original receipt, before amendment receipt, and after amendment receipt. Mixed fixtures preserve all evidence domains independently. Representative cases and synthetic edge cases carry complete provenance metadata and invented identities only.

`normalize-provider --provider sec` reads local files and emits stable machine-readable output; rejection returns nonzero. Existing evidence and timeline commands accept canonical SEC observations without acquiring data.

## Testing and boundaries

Tests follow red-green-refactor and cover model structure, aliases, CIK/accession/form parsing, exact/date-only/missing timestamps, availability precedence, sanitization, complete/partial/rejected records, amendments, duplicates, conflicts, eligibility, historical rebuilds, independent coverage, ages, strict replay, CLI, fixture provenance, repeated byte identity, all Phase 1A–1D hashes, and isolation scans.

Phase 1E does not connect to SEC/EDGAR; download documents; parse filing bodies, HTML, or XBRL; extract offering or dilution facts; classify forms as positive/negative/bullish/bearish/catalysts; connect to Finviz/IBKR/FINRA; calculate squeeze probability; score or rank candidates; identify entries/exits; emit trading signals; persist data; or begin Phase 1F.
