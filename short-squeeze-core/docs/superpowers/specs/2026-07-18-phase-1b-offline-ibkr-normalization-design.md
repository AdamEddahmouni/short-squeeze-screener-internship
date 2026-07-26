# Phase 1B Offline IBKR Normalization Design

## Scope

Phase 1B adds an offline-only, provider-neutral adapter boundary and one IBKR short-stock-file-shaped normalizer. It converts sanitized local records into the existing immutable `1.0.0` borrow-fee and borrow-availability observations. It adds no provider connection, credentials, storage, strategy, scoring, or trading behavior.

## Architecture and data flow

`IbkrBorrowRecord` validates provider-shaped fields without guessing units or timestamps. Immutable `AdapterContext` supplies ingestion time, timestamp assumptions, entitlement, collection method, and version labels. `normalize_ibkr_borrow_record` returns a typed result containing zero to two canonical observations plus stable diagnostics or a typed rejection. A batch function detects duplicate and conflicting records without choosing a winner.

Raw records are canonically serialized and hashed before normalization. Each output references that hash, the source record ID, adapter and normalization versions, timestamp representation, entitlement, and sanitized provider metadata. Fee and availability remain separate observations.

## Decisions

- The fixture basis is representative because no recorded IBKR row is preserved. Valid shape examples are `SANITIZED_REPRESENTATIVE_SAMPLE`; malformed, duplicate, and conflict cases are `SYNTHETIC_EDGE_CASE`.
- IBKR borrow data is `PROVIDER_PUBLISHED`, not market-wide direct observation or short interest.
- Percent input units are explicit: `PERCENT_POINTS` preserves `0.325` as `0.325%`; `DECIMAL_FRACTION` converts it to `32.5%`. Unsupported or absent units reject fee output rather than inferring by magnitude.
- Negative fees are rejected as invalid under the Phase 1A nonnegative borrow-fee contract; no rebate interpretation is invented.
- Missing values produce nullable payload fields and `MISSING` quality. Explicit zero remains zero with `KNOWN_VALUE` quality.
- An explicit offset or separately supplied IANA timezone can normalize a timestamp. A date-only value uses start-of-day only when a source timezone is supplied and is diagnosed as date precision. Missing timestamps use ingestion time only as an explicitly uncertain effective placeholder and receive `MISSING` quality plus a diagnostic. Naive timestamps with unknown timezone reject the record.
- Known delay produces `DELAYED` freshness and quality. Unknown delay and entitlement are visible diagnostics.
- Duplicate records are diagnosed and emitted once. Same symbol/effective timestamp records with different lending values are preserved and marked `CONFLICTED`; no winner is selected.

## Testing and error handling

Tests exercise validation, missing/zero distinction, timezones, delays, units, invalid values, raw hashes, version provenance, duplicate/conflict batches, canonical validation, CLI behavior, isolation scans, generated JSONL, strict replay, and byte-identical replay results. Fixture generation uses only explicit timestamps and stable IDs. Rejections and diagnostics are structured models, not exception strings or dictionaries.

## Boundaries

The adapter package may import only the Python standard library, Pydantic, and `squeeze_core` contracts/serialization. It never reads environment variables, opens sockets, imports an IBKR SDK, contacts a database, or writes outside explicit CLI output/fixture-builder paths.
