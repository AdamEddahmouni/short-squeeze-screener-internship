# Phase 1C Offline Finviz and Cross-Source Evidence Design

## Scope

Phase 1C adds an offline Finviz-shaped candidate-universe normalizer, an additive provider-neutral `MARKET_SNAPSHOT` observation, and deterministic point-in-time evidence bundles. It combines candidate snapshots with existing IBKR borrow-fee and borrow-availability observations without scoring, ranking, recommending, averaging, or selecting a provider winner.

All input is local representative or synthetic data. There is no provider connection, authentication, credential access, database, GUI, strategy, or trading behavior.

## Existing-contract decision

The current contract has trade, quote, and bar payloads, but none represents a descriptive screener row. Phase 1C therefore adds `EventType.MARKET_SNAPSHOT`, `PayloadType.MARKET_SNAPSHOT`, and `MarketSnapshotPayload`. The extension is additive: existing enum values, payloads, observation fields, identities, serialized fixtures, and IBKR semantics remain unchanged. Schema version `1.0.0` remains valid.

The payload contains one coherent provider snapshot with nullable descriptive fields: last price, previous close, change percent, volume, average volume, relative volume, float shares, shares outstanding, short-float percent, short-ratio days, market capitalization, sector, industry, country, exchange, earnings date/session, and snapshot scope. It is not a trade, quote, bar, published-short-interest report, borrow record, catalyst, squeeze classification, or recommendation.

## Finviz adapter

`FinvizSnapshotRecord` validates a sanitized provider-shaped row and its explicit input semantics. Supported aliases are limited to the archived parser/test evidence and the Phase 1C handoff: canonical names plus `Ticker`, `Price`, `Prev Close`, `Change`, `Volume`, `Avg Volume`, `Relative Volume`, `Shares Float`, `Shares Outstanding`, `Short Float`, `Short Ratio`, `Market Cap`, `Sector`, `Industry`, `Country`, `Exchange`, and `Earnings`. Unknown aliases are rejected and diagnosed rather than silently consumed.

The normalizer reuses `AdapterContext`, `NormalizationResult`, `NormalizationDiagnostic`, and `RejectedRecord`. One accepted record produces one `MARKET_SNAPSHOT` observation. Structurally usable partial records remain accepted, retain nulls, and carry diagnostics and partial completeness. An invalid price does not discard otherwise unambiguous descriptive fields; a row with no usable descriptive evidence is rejected.

### Parsing

- Prices and ratios use finite `Decimal` values. Negative price and ratio values are invalid. An explicit zero price remains structurally represented but makes the snapshot `INVALID` with a diagnostic.
- Change and short-float percentages require `PERCENT_POINTS`, `DECIMAL_FRACTION`, or `FORMATTED_PERCENT_STRING`; scaling is never inferred from magnitude.
- Quantities accept finite nonnegative integers or decimal strings with decimal `K`, `M`, `B`, or `T` multipliers. Abbreviated values are marked estimated because source formatting may be rounded. Fractional expanded share/volume quantities are rejected rather than rounded.
- Provider relative volume is retained as a provider-published ratio. It is never recalculated, and its unknown reference period is diagnosed.
- `short_float_percent` remains distinct from published short interest, borrow availability, borrow fee, short-sale volume, and covering activity.
- Earnings supports exact/date-only values and before-market/after-market qualifiers. Ambiguous text remains null with a diagnostic; no time or timezone is invented.

### Time and freshness

Provider, capture, received, and effective time remain distinct. A valid provider timestamp is the source timestamp and effective time. If provider time is absent, capture time is used only as an uncertain source/effective placeholder required by the `1.0.0` envelope; provenance retains a null provider timestamp representation, provider metadata retains the capture timestamp, quality is reduced, and diagnostics state that capture is not provider publication time.

If provider and capture times are both absent, the explicit context ingestion time is the same kind of uncertain placeholder. Recent capture never proves live field freshness. Explicit delay status maps to delayed freshness; historical/stale policy is based only on explicit context and configured thresholds; otherwise freshness is unknown.

## Evidence package

`squeeze_core.evidence` contains immutable enums and models for policy, diagnostics, source coverage, conflicts, freshness/completeness summaries, and `PointInTimeEvidenceBundle`.

`PointInTimeEvidencePolicy` supplies `as_of`, bounded future skew, maximum age by event type, stale/delayed/unknown-freshness inclusion flags, conflict tolerances, and informational source-priority metadata. Priority metadata never selects a winner.

Bundle construction:

1. accepts canonical observations only;
2. filters to the requested symbol;
3. excludes observations received after `as_of`;
4. excludes effective timestamps after `as_of + maximum_future_skew`;
5. applies policy-controlled stale, delayed, and unknown-freshness inclusion;
6. orders included observations with the canonical replay key;
7. preserves every included `Observation` object unchanged;
8. reports candidate-snapshot, borrow-fee, and borrow-availability coverage independently;
9. detects conflicts only among semantically compatible fields;
10. canonically serializes and hashes the result without wall-clock, random, path, or iteration-order input.

The received-time exclusion is strict and is not relaxed by effective-time skew: evidence first received after `as_of` was not available at `as_of`.

## Conflict model

Conflict extraction maps event payloads to explicit semantic fields. `MARKET_SNAPSHOT.float_shares` can be compared only with another compatible float-shares observation; borrow fee compares only with annualized borrow fee; availability compares only with available shares. Finviz short float, IBKR fee, and IBKR availability are incompatible dimensions and are never compared as competing values.

Same semantic field and effective time with different values produces `VALUE_CONFLICT`; same-provider duplicate records produce `DUPLICATE_CONFLICT`; compatible values at different effective times produce `TEMPORAL_DIFFERENCE`; explicitly attempted incompatible comparisons are represented or diagnosed as `INCOMPATIBLE_SEMANTICS`. No value is averaged or overwritten and no winner is selected. Conflict IDs and ordering are content-derived and deterministic.

## Fixtures and replay

No defensible recorded Finviz export exists. The archived hand-built CSV establishes representative column names only. Valid Finviz fixtures are `SANITIZED_REPRESENTATIVE_SAMPLE`; malformed, duplicate, conflict, and cross-source policy cases are `SYNTHETIC_EDGE_CASE`. Fixtures use `TESTA`, `TESTB`, and `TESTC`, contain no credentials/account data/private URLs, and document timestamp availability and expected outcomes.

A deterministic builder produces Finviz JSONL, mixed Finviz/IBKR JSONL, strict replay results, bundles, and committed hashes. Existing Phase 1A and Phase 1B fixtures and expected hashes must remain byte-identical.

## CLI

`normalize-provider --provider finviz` routes a local JSON object through the Finviz normalizer. `build-evidence` loads local canonical JSONL, applies an explicit policy/as-of time, and prints a canonical bundle. Rejected normalization or invalid evidence input returns nonzero with structured machine-readable output.

CLI output contains no strategy vocabulary, score, tier, probability, entry, exit, buy, sell, or recommendation.

## Testing and isolation

Implementation follows red-green-refactor. Tests cover contract compatibility, supported aliases, exact raw hashes, parsing units and edge cases, timestamp/freshness uncertainty, missing versus zero, partial normalization, duplicate/conflict batches, evidence selection and coverage, stable conflict IDs, replay integration, CLI behavior, fixture hashes, and repeated byte identity.

Static scans prohibit wall-clock calls in deterministic paths, environment reads, `.env`, HTTP/network/browser/provider SDK imports, databases, credential/token/session logic, GUI dependencies, and order APIs.

## Handoff discrepancy

The Phase 1C handoff listed `docs/point-in-time-normalization.md`, but that file is absent at the Phase 1B starting commit. ADR 0006 and `docs/adapter-contract.md` are treated as the authoritative existing point-in-time normalization coverage. This absence is not repaired retroactively and does not change Phase 1B behavior.

The Codex output stream disconnected after these planning files were created and before they were reviewed or committed. Repository inspection on resumption found only these two untracked files at the expected Phase 1B HEAD; the interruption changed no design decision or implementation state.

## Boundaries

Phase 1C does not connect to Finviz or IBKR, authenticate, validate licensing or entitlements, prove real-time field freshness, calculate indicators or squeeze probability, filter/rank candidates, produce Prime/Subprime labels, recommend trades, identify entries/exits, persist to a database, or place/cancel orders.
