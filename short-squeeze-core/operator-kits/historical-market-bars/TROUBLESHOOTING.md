# Troubleshooting

Each reason code below tells you what it means, why the workflow blocks or
quarantines it, what to inspect, what you may safely change (a manifest or
mapping-profile correction — never the raw bytes), what you must not guess, and
whether a new export is required. The workflow never advises bypassing a source
restriction or editing raw data to force acceptance.

## ABSOLUTE_PATH_IN_IDENTITY

- **Meaning:** artifact_relative_path is absolute or escapes the intake root.
- **Why it blocks/quarantines:** Blocks at load: absolute/machine paths never enter deterministic identity.
- **Inspect:** artifact_relative_path; it must be a relative path under the bundle root.
- **You may change:** Use a relative path such as raw/your-export.csv.
- **Do not guess:** Do not embed a machine-specific absolute path.
- **New export required:** NO

## AMBIGUOUS_TIMEZONE

- **Meaning:** A local timestamp is ambiguous (a daylight-saving fall-back repeats the hour).
- **Why it blocks/quarantines:** Blocks the row: the instant is not unique, so it is never guessed.
- **Inspect:** Whether the export provides UTC or an explicit offset instead of local time.
- **You may change:** Re-declare event_timezone as UTC or an explicit offset if the export supports it.
- **Do not guess:** Do not pick one side of the repeated hour.
- **New export required:** SOMETIMES

## ARTIFACT_BYTE_LENGTH_MISMATCH

- **Meaning:** The raw file's byte length differs from artifact_byte_length in the manifest.
- **Why it blocks/quarantines:** Blocks the bundle: the manifest no longer describes the exact bytes.
- **Inspect:** The real byte length (historical-bar-hash) versus the declared value.
- **You may change:** Recompute and set artifact_byte_length for the exact file placed under raw/.
- **Do not guess:** Do not resave or reformat the raw file to reach the declared length.
- **New export required:** NO

## ARTIFACT_EMPTY

- **Meaning:** The raw file exists but has zero bytes.
- **Why it blocks/quarantines:** Blocks the bundle: an empty export carries no bars.
- **Inspect:** Whether the export completed and was copied fully.
- **You may change:** Replace with the complete raw export and update sha256/byte_length.
- **Do not guess:** Do not fabricate rows to fill an empty file.
- **New export required:** SOMETIMES

## ARTIFACT_MISSING

- **Meaning:** No file was found at the manifest's artifact_relative_path under the bundle root.
- **Why it blocks/quarantines:** Blocks the bundle: nothing can be validated or normalized.
- **Inspect:** The bundle root, the raw/ folder, and artifact_relative_path spelling.
- **You may change:** Fix artifact_relative_path, or place the exact raw file where it points.
- **Do not guess:** Do not substitute a different file to make the path resolve.
- **New export required:** NO

## ARTIFACT_SHA256_MISMATCH

- **Meaning:** The raw file's SHA-256 differs from artifact_sha256 in the manifest.
- **Why it blocks/quarantines:** Blocks the bundle: the bytes were altered or the wrong file is present.
- **Inspect:** The real SHA-256 (historical-bar-hash); whether line endings changed on copy.
- **You may change:** Recompute and set artifact_sha256 for the exact file placed under raw/.
- **Do not guess:** Do not edit raw bytes to reach the declared hash.
- **New export required:** SOMETIMES

## CASE_ASSOCIATION_WITHOUT_DECLARATION

- **Meaning:** An association was attempted without a declared, validated mapping.
- **Why it blocks/quarantines:** Blocks: Batch 04 performs no case association at all.
- **Inspect:** Nothing to change in Batch 04; association is future authorized work only.
- **You may change:** Nothing in this batch; do not attempt association here.
- **Do not guess:** Do not link a bundle to any real case during Batch 04.
- **New export required:** NO

## CASE_COVERAGE_INCOMPATIBLE

- **Meaning:** A mapping's required session coverage is incompatible with the bundle's coverage.
- **Why it blocks/quarantines:** Future-work guard: coverage compatibility is checked only in later authorized work.
- **Inspect:** Not applicable in Batch 04.
- **You may change:** Nothing in this batch.
- **Do not guess:** Do not force a coverage match during Batch 04.
- **New export required:** NO

## CASE_INTERVAL_INCOMPATIBLE

- **Meaning:** A mapping's required interval is incompatible with the bundle's interval.
- **Why it blocks/quarantines:** Future-work guard: interval compatibility is checked only in later authorized work.
- **Inspect:** Not applicable in Batch 04.
- **You may change:** Nothing in this batch.
- **Do not guess:** Do not force an interval match during Batch 04.
- **New export required:** NO

## CASE_SYMBOL_INCOMPATIBLE

- **Meaning:** A mapping's symbol is incompatible with the bundle's manifest symbol.
- **Why it blocks/quarantines:** Future-work guard: symbol compatibility is checked only in later authorized work.
- **Inspect:** Not applicable in Batch 04.
- **You may change:** Nothing in this batch.
- **Do not guess:** Do not force a symbol match during Batch 04.
- **New export required:** NO

## CONFLICTING_DUPLICATE_BAR

- **Meaning:** Two rows share a start time but disagree on values.
- **Why it blocks/quarantines:** Blocks the bundle: which conflicting bar is correct is never guessed.
- **Inspect:** The conflicting rows and why the export produced both.
- **You may change:** Obtain a clean export without conflicting duplicates.
- **Do not guess:** Do not pick one conflicting row over the other.
- **New export required:** YES

## CONTRADICTORY_ADJUSTMENT_SEMANTICS

- **Meaning:** Price adjustment and corporate-action handling disagree (e.g. adjusted price, raw handling).
- **Why it blocks/quarantines:** Blocks the bundle: the declared semantics are internally inconsistent.
- **Inspect:** price_adjustment_semantics against corporate_action_handling.
- **You may change:** Correct whichever field is mis-declared to match the export.
- **Do not guess:** Do not pick one field arbitrarily to resolve the conflict.
- **New export required:** NO

## COVERAGE_GAP

- **Meaning:** Consecutive bars leave a gap but continuity was required.
- **Why it blocks/quarantines:** Blocks the bundle when session_coverage_policy is REQUIRE_CONTINUOUS.
- **Inspect:** Whether gaps are expected (halts, closed session) for this data.
- **You may change:** Set session_coverage_policy to ALLOW_GAPS if gaps are legitimate.
- **Do not guess:** Do not synthesize filler bars to close the gap.
- **New export required:** NO

## CREDENTIAL_LIKE_VALUE_PRESENT

- **Meaning:** A field contains credential-like material (a login pass-phrase, API key, or token).
- **Why it blocks/quarantines:** Blocks the bundle: credentials must never enter intake artifacts.
- **Inspect:** Every manifest/profile value for accidentally pasted credential material.
- **You may change:** Remove the credential-like value; declare only provenance and semantics.
- **Do not guess:** Do not obfuscate credential material to pass the check.
- **New export required:** NO

## CURRENT_VALUE_AS_HISTORICAL

- **Meaning:** data_time_basis is CURRENT, so the values are a live view, not historical.
- **Why it blocks/quarantines:** Blocks the bundle: current values cannot substitute for historical ones.
- **Inspect:** Whether the export is a live snapshot or a true historical extract.
- **You may change:** Provide a genuinely historical export and declare HISTORICAL.
- **Do not guess:** Do not relabel a current view as historical.
- **New export required:** YES

## DATA_TIME_BASIS_UNKNOWN

- **Meaning:** data_time_basis is UNKNOWN, so it is unclear whether values are historical or current.
- **Why it blocks/quarantines:** Blocks the bundle: current values must not be ingested as historical.
- **Inspect:** Whether the export is a historical snapshot or a live/current view.
- **You may change:** Set data_time_basis to HISTORICAL only when the export truly is historical.
- **Do not guess:** Do not declare HISTORICAL to get past the check.
- **New export required:** SOMETIMES

## DUPLICATE_TIMESTAMP

- **Meaning:** Two or more rows share the same bar start time.
- **Why it blocks/quarantines:** Identical duplicates quarantine (collapse); under REJECT_ALL_DUPLICATES they reject.
- **Inspect:** Whether the duplicates are truly identical and the duplicate_policy setting.
- **You may change:** Choose the duplicate_policy that matches your intent for identical rows.
- **Do not guess:** Do not delete rows to remove duplicates silently.
- **New export required:** NO

## EVENT_TIME_OUTSIDE_COVERAGE

- **Meaning:** A bar falls outside the manifest's declared expected_start_time/expected_end_time.
- **Why it blocks/quarantines:** Blocks the row: the bundle claims a coverage window the data exceeds.
- **Inspect:** The declared coverage window against the actual first/last bar times.
- **You may change:** Widen expected_start_time/expected_end_time to the true coverage if intended.
- **Do not guess:** Do not drop or move the out-of-window bar.
- **New export required:** NO

## INVALID_BOUNDARY_DURATION

- **Meaning:** A bar's computed end is not strictly after its start.
- **Why it blocks/quarantines:** Blocks the row: the bar has no positive duration.
- **Inspect:** timestamp_semantics and bar_interval against the row timestamp.
- **You may change:** Correct timestamp_semantics or bar_interval if mis-declared.
- **Do not guess:** Do not extend the bar to a positive duration by hand.
- **New export required:** NO

## INVALID_OHLC_RELATIONSHIP

- **Meaning:** A bar violates high >= max(open,close,low) or low <= min(open,close,high).
- **Why it blocks/quarantines:** Blocks the row: the OHLC values are internally impossible.
- **Inspect:** The OHLC column mapping; a swapped high/low is a common cause.
- **You may change:** Fix the OHLC column mapping if columns were transposed.
- **Do not guess:** Do not reorder or clamp OHLC values to make them valid.
- **New export required:** SOMETIMES

## INVALID_TIMESTAMP

- **Meaning:** A row timestamp is missing or unparseable.
- **Why it blocks/quarantines:** Blocks the row: the bar cannot be placed in time.
- **Inspect:** The timestamp column mapping and timestamp_format against the raw rows.
- **You may change:** Correct timestamp_column/date_column/time_column/timestamp_format in the profile.
- **Do not guess:** Do not fill in a plausible timestamp for a broken row.
- **New export required:** SOMETIMES

## MALFORMED_DECIMAL

- **Meaning:** A numeric field is not a valid decimal under the profile's separators.
- **Why it blocks/quarantines:** Blocks the row: the value cannot be parsed deterministically.
- **Inspect:** decimal_separator and thousands_separator_policy against the raw numbers.
- **You may change:** Correct decimal_separator/thousands_separator_policy to match the export.
- **Do not guess:** Do not rewrite the raw number to a clean form.
- **New export required:** SOMETIMES

## MALFORMED_MANIFEST

- **Meaning:** The manifest JSON is not a valid IntakeManifest (missing/invalid fields).
- **Why it blocks/quarantines:** Blocks at load: preflight cannot build the manifest object.
- **Inspect:** The manifest against the intake-manifest template and field guidance.
- **You may change:** Fix the manifest JSON: add required fields, correct types, remove guidance keys.
- **Do not guess:** Do not invent provenance values to satisfy the schema.
- **New export required:** NO

## MALFORMED_ROW

- **Meaning:** A row cannot be split into the expected fields.
- **Why it blocks/quarantines:** Blocks the row: the record is structurally broken.
- **Inspect:** delimiter and has_header against the raw line.
- **You may change:** Correct delimiter/has_header if the profile mis-describes the CSV.
- **Do not guess:** Do not hand-edit the broken raw line.
- **New export required:** SOMETIMES

## MANIFEST_SCHEMA_MISMATCH

- **Meaning:** The manifest declares a schema/contract version this batch does not accept.
- **Why it blocks/quarantines:** Blocks the bundle: the declared contract does not match this workflow.
- **Inspect:** schema_version and intake_contract_version against the template defaults.
- **You may change:** Set the versions to the values in the current template.
- **Do not guess:** Do not force an unsupported version through.
- **New export required:** NO

## MARKET_VENUE_MISMATCH

- **Meaning:** A row's venue disagrees with the manifest market_or_venue.
- **Why it blocks/quarantines:** Blocks the row: the bundle would mix venues.
- **Inspect:** The venue column values against market_or_venue.
- **You may change:** Correct market_or_venue, or the venue_column mapping, to match the export.
- **Do not guess:** Do not overwrite the row venue to match.
- **New export required:** NO

## MISSING_ADJUSTMENT_SEMANTICS

- **Meaning:** A price/volume/corporate-action semantic is UNKNOWN, so adjustment meaning is undefined.
- **Why it blocks/quarantines:** Blocks the bundle: adjustment cannot be inferred from the numbers.
- **Inspect:** The provider's documentation for how prices and volume are adjusted.
- **You may change:** Set price/volume adjustment and corporate_action_handling to declared values.
- **Do not guess:** Do not guess raw vs adjusted from the price magnitudes.
- **New export required:** NO

## MISSING_INTERVAL

- **Meaning:** No bar_interval is declared, so bar duration is undefined.
- **Why it blocks/quarantines:** Blocks at load: the manifest requires an explicit interval.
- **Inspect:** The export's actual bar interval.
- **You may change:** Declare bar_interval to match the export.
- **Do not guess:** Do not infer interval from row spacing.
- **New export required:** NO

## MISSING_OHLC_VALUE

- **Meaning:** A required open/high/low/close value is missing for a row.
- **Why it blocks/quarantines:** Blocks the row: OHLC is never inferred.
- **Inspect:** The OHLC column mappings and null_tokens against the raw rows.
- **You may change:** Fix the OHLC column mapping if a real value was misread as null.
- **Do not guess:** Do not fill a missing price from a neighboring bar.
- **New export required:** SOMETIMES

## MISSING_TIMESTAMP_SEMANTICS

- **Meaning:** timestamp_semantics is not START or END, so bar boundaries are undefined.
- **Why it blocks/quarantines:** Blocks the bundle: whether a timestamp labels the bar start or end is unknown.
- **Inspect:** The provider's documentation for whether timestamps mark bar open or close.
- **You may change:** Set timestamp_semantics to START or END per the provider's definition.
- **Do not guess:** Do not assume START without confirming the provider's convention.
- **New export required:** NO

## MIXED_INTERVALS_UNDECLARED

- **Meaning:** Rows imply more than one bar interval but a single interval was declared.
- **Why it blocks/quarantines:** Blocks the bundle: mixed intervals are not silently reconciled.
- **Inspect:** Row spacing against the declared bar_interval.
- **You may change:** Split the export into single-interval bundles, each declared correctly.
- **Do not guess:** Do not resample mixed bars into one interval.
- **New export required:** SOMETIMES

## NAN_OR_INFINITY

- **Meaning:** A numeric field is NaN or infinity.
- **Why it blocks/quarantines:** Blocks the row: non-finite values are never accepted.
- **Inspect:** Whether the export emitted NaN/inf placeholders for missing data.
- **You may change:** If NaN means null, map it via null_tokens; otherwise the row stays blocked.
- **Do not guess:** Do not replace NaN/inf with a fabricated number.
- **New export required:** SOMETIMES

## NEGATIVE_TRADE_COUNT

- **Meaning:** A row carries a negative trade count.
- **Why it blocks/quarantines:** Blocks the row: trade count cannot be negative.
- **Inspect:** The trade_count column mapping and the raw values.
- **You may change:** Fix the trade_count_column mapping if a wrong column was mapped.
- **Do not guess:** Do not take the absolute value of a negative trade count.
- **New export required:** SOMETIMES

## NEGATIVE_VOLUME

- **Meaning:** A row carries negative volume.
- **Why it blocks/quarantines:** Blocks the row: volume cannot be negative.
- **Inspect:** The volume column mapping and the raw values.
- **You may change:** Fix the volume_column mapping if a non-volume column was mapped.
- **Do not guess:** Do not take the absolute value of negative volume.
- **New export required:** SOMETIMES

## NONEXISTENT_LOCAL_TIME

- **Meaning:** A local timestamp falls in a daylight-saving spring-forward gap that never occurred.
- **Why it blocks/quarantines:** Blocks the row: the instant does not exist, so it is never invented.
- **Inspect:** Whether the export mislabels timezone, or provides UTC/explicit offset.
- **You may change:** Re-declare event_timezone as UTC or an explicit offset if the export supports it.
- **Do not guess:** Do not shift the time into the adjacent valid hour.
- **New export required:** SOMETIMES

## NON_MONOTONIC_ORDER

- **Meaning:** Rows are not sorted by time but the profile requires presorted input.
- **Why it blocks/quarantines:** Blocks the bundle when sort_expectation is REQUIRE_PRESORTED.
- **Inspect:** The raw row order and the sort_expectation setting.
- **You may change:** Set sort_expectation to STABLE_SORT_BY_EVENT_START if unordered input is acceptable.
- **Do not guess:** Do not reorder the raw rows in place to fake presorting.
- **New export required:** NO

## OVERLAPPING_BARS

- **Meaning:** A later bar starts before the previous bar's end.
- **Why it blocks/quarantines:** Blocks the bundle: overlapping bars are inconsistent.
- **Inspect:** bar_interval and timestamp_semantics against the row spacing.
- **You may change:** Correct bar_interval/timestamp_semantics if mis-declared.
- **Do not guess:** Do not trim bars to remove the overlap.
- **New export required:** SOMETIMES

## SYMBOL_MISMATCH

- **Meaning:** A row's symbol disagrees with the manifest provider_symbol.
- **Why it blocks/quarantines:** Blocks the row: the bundle would mix instruments.
- **Inspect:** The symbol column values against provider_symbol.
- **You may change:** Correct provider_symbol, or the symbol_column mapping, to match the export.
- **Do not guess:** Do not overwrite the row symbol to match.
- **New export required:** NO

## SYNTHETIC_VALUE_AS_HISTORICAL

- **Meaning:** A SYNTHETIC_FIXTURE bundle is declared as HISTORICAL_EVIDENCE.
- **Why it blocks/quarantines:** Blocks the bundle: synthetic values cannot represent historical evidence.
- **Inspect:** value_authenticity against intended_use.
- **You may change:** Set intended_use to INFRASTRUCTURE_FIXTURE for synthetic data.
- **Do not guess:** Do not relabel synthetic data as vendor-supplied historical evidence.
- **New export required:** YES

## UNKNOWN_BOUNDARY_ID

- **Meaning:** A case-association mapping references a boundary id not in the known set.
- **Why it blocks/quarantines:** Future-work guard: association validates references only, and only later.
- **Inspect:** Not applicable in Batch 04.
- **You may change:** Nothing in this batch.
- **Do not guess:** Do not substitute a real boundary id during Batch 04.
- **New export required:** NO

## UNKNOWN_CASE_ID

- **Meaning:** A case-association mapping references a case id not in the known set.
- **Why it blocks/quarantines:** Future-work guard: association validates references only, and only later.
- **Inspect:** Not applicable in Batch 04; the case-association template is placeholder-only.
- **You may change:** Nothing in this batch.
- **Do not guess:** Do not substitute a real case id into the template during Batch 04.
- **New export required:** NO

## UNKNOWN_TIMEZONE

- **Meaning:** event_timezone could not be resolved (unknown name, or IANA data unavailable).
- **Why it blocks/quarantines:** Blocks the bundle: timestamps cannot be anchored to an instant.
- **Inspect:** event_timezone; prefer UTC or an explicit offset like -05:00 when IANA data is absent.
- **You may change:** Set event_timezone to UTC, an explicit offset, or a resolvable IANA zone.
- **Do not guess:** Do not infer the timezone from the symbol or venue.
- **New export required:** NO

## UNSUPPORTED_ADJUSTMENT_SEMANTICS

- **Meaning:** A declared adjustment semantic is outside the supported set.
- **Why it blocks/quarantines:** Blocks the bundle: the declared adjustment cannot be represented.
- **Inspect:** The supported price/volume adjustment options in the adjustment guide.
- **You may change:** Re-declare using a supported adjustment value if it matches the export.
- **Do not guess:** Do not map an unsupported adjustment onto a supported one.
- **New export required:** SOMETIMES

## UNSUPPORTED_ENCODING

- **Meaning:** The declared profile.encoding is not one this batch can decode.
- **Why it blocks/quarantines:** Blocks the bundle: the text cannot be decoded deterministically.
- **Inspect:** The real file encoding; supported values are utf-8, utf-8-sig, ascii, latin-1.
- **You may change:** Set profile.encoding to the export's actual supported encoding.
- **Do not guess:** Do not guess an encoding that silently corrupts characters.
- **New export required:** SOMETIMES

## UNSUPPORTED_FORMAT

- **Meaning:** artifact_format is a declared format this batch does not normalize (only CSV).
- **Why it blocks/quarantines:** Blocks the bundle: only CSV is normalized this batch.
- **Inspect:** The export's real format; whether a delimited CSV export is available.
- **You may change:** Provide a CSV export and set artifact_format to CSV.
- **Do not guess:** Do not relabel a non-CSV file as CSV.
- **New export required:** SOMETIMES

## UNSUPPORTED_INTERVAL

- **Meaning:** bar_interval is a session-based or otherwise unsupported interval this batch cannot bound.
- **Why it blocks/quarantines:** Blocks the bundle: daily/irregular bars are not silently converted.
- **Inspect:** Whether a supported fixed interval (1/5/15/30 minute or 1 hour) export exists.
- **You may change:** Provide an export at a supported fixed interval and declare it.
- **Do not guess:** Do not resample or convert bars to a supported interval by hand.
- **New export required:** SOMETIMES
