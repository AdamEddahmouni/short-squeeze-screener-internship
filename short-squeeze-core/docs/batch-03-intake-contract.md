# Batch 03 — Local Bar Intake Contract

Contract version: `phase_3d_local_bar_intake_contract.v1` · schema `1.0.0`

The intake contract is rendered deterministically by
`squeeze_core.acquisition.local_bar_intake.contract.build_intake_contract` and
committed as `tests/fixtures/acquisition/batch03/intake-contract.json`.

## Bundle structure

```text
<private-intake-root>/            # intake/local-bars/ is gitignored (never real data)
  <bundle-id>/
    intake-manifest.json          # IntakeManifest
    raw/<original-export-file>     # bytes preserved exactly, never modified
    profiles/<profile>.json        # ColumnMappingProfile
```

## Manifest (`IntakeManifest`)

Explicit, canonical fields (explicit `null` required for unknowns):

| field | meaning |
|---|---|
| `schema_version`, `intake_contract_version` | contract identity |
| `bundle_id` | stable bundle key (no absolute path) |
| `provider_name`, `provider_product_or_export_name` | provider provenance |
| `user_entitlement_assertion` | user's provenance assertion — **not** a legal determination |
| `license_or_terms_reference` | optional terms pointer |
| `retrieval_time`, `export_time` | distinct from each other and from event time |
| `artifact_relative_path` | relative path only; absolute paths are rejected |
| `artifact_sha256`, `artifact_byte_length`, `artifact_media_type`, `artifact_format` | raw-artifact integrity |
| `provider_symbol`, `canonical_symbol`, `market_or_venue` | identity |
| `bar_interval`, `event_timezone`, `timestamp_semantics`, `session_coverage`, `session_coverage_policy` | temporal semantics |
| `price_adjustment_semantics`, `volume_adjustment_semantics`, `corporate_action_handling` | adjustment semantics |
| `data_time_basis`, `value_authenticity`, `intended_use` | historical/current + synthetic/vendor + declared use |
| `expected_start_time`, `expected_end_time` | declared coverage window |
| `column_mapping_profile_id`, `notes` | parsing profile ref; `notes` never affects identity |

## Canonical bar (`CanonicalMarketBar`)

`canonical_symbol, provider_symbol, market_or_venue, interval, event_start_time,
event_end_time, event_timezone, session, open, high, low, close, volume,
trade_count, vwap, currency, price_adjustment_semantics,
volume_adjustment_semantics, value_authenticity, source_artifact_id,
source_row_number, source_record_id`.

- Decimals are exact (`Decimal`, serialized by the repository canonical encoder).
  No NaN, no ±infinity, no locale parsing, no thousands separators unless the
  profile declares them.
- OHLCV is never inferred; missing required values reject the row.

## Supported input

One reference **CSV / delimited-text** adapter driven by `ColumnMappingProfile`
(delimiter, encoding, header, timestamp/date+time columns, optional symbol/venue
columns, OHLCV columns, optional trade-count/VWAP/currency, decimal separator,
thousands-separator policy, null tokens, sort expectation, duplicate policy). A
canonical JSON adapter is deliberately out of scope for this batch.

## CLI (offline, never network)

```text
intake-validate-bundle              intake-inspect-artifact
intake-normalize-bars               intake-summary
intake-validate-case-association
```
