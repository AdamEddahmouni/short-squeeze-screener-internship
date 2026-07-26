# Synthetic Invalid Scenarios

`invalid-scenario-index.json` records deterministic failing scenarios. Executed
scenarios run the synthetic bundle through the real preflight workflow and record
the resulting status and reason codes. Documented scenarios describe load-time or
environment-limited barriers (for example ambiguous local time, which needs IANA
time-zone data) without executing. No unsafe input is ever auto-repaired.

## Executed scenarios

- `missing_raw_artifact` -> NOT_READY_REJECTED [ARTIFACT_MISSING] - Place the exact raw file, or fix artifact_relative_path.
- `incorrect_byte_length` -> NOT_READY_REJECTED [ARTIFACT_BYTE_LENGTH_MISMATCH] - Recompute artifact_byte_length for the exact file.
- `incorrect_sha256` -> NOT_READY_REJECTED [ARTIFACT_SHA256_MISMATCH] - Recompute artifact_sha256 for the exact file.
- `unsupported_encoding` -> NOT_READY_REJECTED [UNSUPPORTED_ENCODING] - Set encoding to a supported value (utf-8, utf-8-sig, ascii, latin-1).
- `unsupported_format` -> NOT_READY_REJECTED [UNSUPPORTED_FORMAT] - Provide a CSV export and set artifact_format to CSV.
- `unknown_timezone` -> NOT_READY_REJECTED [UNKNOWN_TIMEZONE] - Use UTC or an explicit offset like -05:00.
- `unsupported_interval` -> NOT_READY_REJECTED [UNSUPPORTED_INTERVAL] - Provide a supported fixed-interval export and declare it.
- `missing_timestamp_semantics` -> NOT_READY_REJECTED [MISSING_TIMESTAMP_SEMANTICS] - Set timestamp_semantics to START or END per the provider convention.
- `missing_adjustment_semantics` -> NOT_READY_REJECTED [MISSING_ADJUSTMENT_SEMANTICS] - Declare the price/volume/corporate-action semantics from provider docs.
- `contradictory_adjustment_semantics` -> NOT_READY_REJECTED [CONTRADICTORY_ADJUSTMENT_SEMANTICS] - Make price adjustment and corporate_action_handling consistent.
- `current_value_as_historical` -> NOT_READY_REJECTED [CURRENT_VALUE_AS_HISTORICAL] - Provide a historical export and declare HISTORICAL.
- `synthetic_value_as_historical` -> NOT_READY_REJECTED [SYNTHETIC_VALUE_AS_HISTORICAL] - Set intended_use to INFRASTRUCTURE_FIXTURE for synthetic data.
- `symbol_mismatch` -> NOT_READY_REJECTED [SYMBOL_MISMATCH] - Correct provider_symbol or the symbol_column mapping.
- `venue_mismatch` -> NOT_READY_REJECTED [MARKET_VENUE_MISMATCH] - Correct market_or_venue or the venue_column mapping.
- `malformed_decimal` -> NOT_READY_REJECTED [MALFORMED_DECIMAL] - Correct decimal_separator/thousands_separator_policy.
- `nan_or_infinity` -> NOT_READY_REJECTED [NAN_OR_INFINITY] - If NaN means null, map via null_tokens; otherwise obtain clean data.
- `missing_ohlc_value` -> NOT_READY_REJECTED [MISSING_OHLC_VALUE] - Fix the OHLC mapping if a real value was misread as null.
- `negative_volume` -> NOT_READY_REJECTED [NEGATIVE_VOLUME] - Fix the volume_column mapping if a wrong column was mapped.
- `negative_trade_count` -> NOT_READY_REJECTED [NEGATIVE_TRADE_COUNT] - Fix the trade_count_column mapping if a wrong column was mapped.
- `invalid_ohlc_relationship` -> NOT_READY_REJECTED [INVALID_OHLC_RELATIONSHIP] - Fix the OHLC mapping if high/low were transposed.
- `event_time_outside_coverage` -> NOT_READY_REJECTED [EVENT_TIME_OUTSIDE_COVERAGE] - Widen expected_start_time/expected_end_time to the true coverage.
- `identical_duplicate_collapse_policy` -> NOT_READY_QUARANTINED [(status-only)] - Identical duplicates are collapsed (quarantine); choose the intended duplicate_policy.
- `identical_duplicate_reject_policy` -> NOT_READY_REJECTED [DUPLICATE_TIMESTAMP] - Under REJECT_ALL_DUPLICATES all duplicates reject; choose the intended policy.
- `conflicting_duplicate_bar` -> NOT_READY_REJECTED [CONFLICTING_DUPLICATE_BAR] - Obtain a clean export without conflicting duplicates.
- `overlapping_bars` -> NOT_READY_REJECTED [OVERLAPPING_BARS] - Correct bar_interval/timestamp_semantics if mis-declared.
- `non_monotonic_order` -> NOT_READY_REJECTED [NON_MONOTONIC_ORDER] - Set sort_expectation to STABLE_SORT_BY_EVENT_START if unordered input is acceptable.
- `coverage_gap` -> NOT_READY_REJECTED [COVERAGE_GAP] - Set session_coverage_policy to ALLOW_GAPS if gaps are legitimate.

## Documented scenarios

- `malformed_manifest` -> MALFORMED_MANIFEST - Fix the manifest against the template; remove guidance keys.
- `missing_interval` -> MISSING_INTERVAL - Declare bar_interval to match the export.
- `ambiguous_timezone` -> AMBIGUOUS_TIMEZONE - Re-declare event_timezone as UTC or an explicit offset if the export supports it.
- `nonexistent_local_time` -> NONEXISTENT_LOCAL_TIME - Re-declare event_timezone as UTC or an explicit offset if the export supports it.
- `absolute_path_in_identity` -> ABSOLUTE_PATH_IN_IDENTITY - Use a relative path such as raw/your-export.csv.
- `attempted_case_association_in_batch_04` -> CASE_ASSOCIATION_WITHOUT_DECLARATION - Do not attempt association in Batch 04; it is future authorized work only.
