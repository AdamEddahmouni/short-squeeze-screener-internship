# Batch 03 — Validation, Rejection, and Quarantine Policy

Deterministic statuses and reason codes live in
`squeeze_core.acquisition.local_bar_intake.semantics`.

## Statuses

- Bundle: `ACCEPTED`, `QUARANTINED`, `REJECTED` (`IntakeValidationStatus`).
- Row: `NORMALIZED`, `QUARANTINED`, `REJECTED` (`RowNormalizationStatus`).

`ACCEPTED` — every distinct bar normalized, no fatal codes.
`QUARANTINED` — harmless identical-duplicate rows were collapsed (bars still
emitted for the distinct set); no fatal codes.
`REJECTED` — one or more fatal codes; **no** bar set is emitted (partial
acceptance of an unsafe bundle is never performed).

## Reason codes (`IntakeReasonCode`)

Artifact: `ARTIFACT_MISSING`, `ARTIFACT_EMPTY`, `ARTIFACT_BYTE_LENGTH_MISMATCH`,
`ARTIFACT_SHA256_MISMATCH`, `UNSUPPORTED_ENCODING`, `UNSUPPORTED_FORMAT`.

Manifest / declaration: `MALFORMED_MANIFEST`, `MANIFEST_SCHEMA_MISMATCH`,
`UNKNOWN_TIMEZONE`, `AMBIGUOUS_TIMEZONE`, `NONEXISTENT_LOCAL_TIME`,
`MISSING_TIMESTAMP_SEMANTICS`, `MISSING_INTERVAL`, `UNSUPPORTED_INTERVAL`,
`MISSING_ADJUSTMENT_SEMANTICS`, `UNSUPPORTED_ADJUSTMENT_SEMANTICS`,
`CONTRADICTORY_ADJUSTMENT_SEMANTICS`, `DATA_TIME_BASIS_UNKNOWN`.

Row / value: `INVALID_TIMESTAMP`, `EVENT_TIME_OUTSIDE_COVERAGE`,
`MIXED_INTERVALS_UNDECLARED`, `SYMBOL_MISMATCH`, `MARKET_VENUE_MISMATCH`,
`MISSING_OHLC_VALUE`, `MALFORMED_DECIMAL`, `NAN_OR_INFINITY`, `NEGATIVE_VOLUME`,
`NEGATIVE_TRADE_COUNT`, `INVALID_OHLC_RELATIONSHIP`, `INVALID_BOUNDARY_DURATION`,
`MALFORMED_ROW`.

Cross-row: `DUPLICATE_TIMESTAMP`, `CONFLICTING_DUPLICATE_BAR`, `OVERLAPPING_BARS`,
`NON_MONOTONIC_ORDER`, `COVERAGE_GAP`.

Provenance / safety: `CURRENT_VALUE_AS_HISTORICAL`,
`SYNTHETIC_VALUE_AS_HISTORICAL`, `ABSOLUTE_PATH_IN_IDENTITY`,
`CREDENTIAL_LIKE_VALUE_PRESENT`.

Case association: `CASE_ASSOCIATION_WITHOUT_DECLARATION`, `UNKNOWN_CASE_ID`,
`UNKNOWN_BOUNDARY_ID`, `CASE_SYMBOL_INCOMPATIBLE`, `CASE_COVERAGE_INCOMPATIBLE`,
`CASE_INTERVAL_INCOMPATIBLE`.

## Bar-integrity checks

```text
high >= max(open, close, low)      low <= min(open, close, high)
volume >= 0 (when present)         trade_count >= 0 (when present)
event_end_time > event_start_time
```

Missing or ambiguous evidence stays missing or ambiguous — bars are never
"repaired" by guessing, and OHLCV is never inferred.

## Preregistered safe normalization

- `STABLE_SORT_BY_EVENT_START` stably sorts by `(event_start_time,
  source_row_number)` and always preserves the 1-based physical
  `source_row_number`, so provenance survives sorting. `REQUIRE_PRESORTED`
  rejects non-monotonic input instead of reordering it.

## Duplicate / continuity policy

- `COLLAPSE_IDENTICAL_REJECT_CONFLICTING` (default): byte-identical duplicate rows
  at one timestamp collapse to one bar (dropped row → `QUARANTINED`,
  `DUPLICATE_TIMESTAMP`); differing rows at one timestamp →
  `CONFLICTING_DUPLICATE_BAR` (reject). `REJECT_ALL_DUPLICATES` rejects any
  duplicate timestamp.
- `REQUIRE_CONTINUOUS` fixed-interval coverage rejects gaps (`COVERAGE_GAP`);
  `ALLOW_GAPS` permits them. Overlapping bars are always rejected
  (`OVERLAPPING_BARS`).

## Provenance safety

- A `CURRENT` export cannot be ingested as historical
  (`CURRENT_VALUE_AS_HISTORICAL`).
- A `SYNTHETIC_FIXTURE` bundle declared as `HISTORICAL_EVIDENCE` is rejected
  (`SYNTHETIC_VALUE_AS_HISTORICAL`); synthetic fixtures are accepted only as
  `INFRASTRUCTURE_FIXTURE`, and every emitted bar carries
  `value_authenticity=SYNTHETIC_FIXTURE` so it can never be mistaken for real
  historical evidence.
