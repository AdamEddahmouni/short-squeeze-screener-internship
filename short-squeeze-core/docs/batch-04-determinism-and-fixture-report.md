# Batch 04 — Determinism and Fixture Report

## Determinism guarantees

Every committed byte is a pure function of in-memory synthetic inputs with fixed
instants. There is no wall-clock, random, network, disk-order, environment, or
machine-path input to any committed artifact. Identity-bearing models reuse the
acquisition `_FrozenAcquisitionModel` base (UUIDv5 over canonical JSON,
`extra='forbid'`, frozen). Serialization is canonical (`canonical_json_bytes`):
sorted keys, exact Decimal strings, explicit nulls, UTF-8, LF endings, no NaN or
infinity. Reason codes, diagnostics, files, and fixtures are emitted in stable
order.

Verified by running the generator twice, every new CLI twice, and comparing bytes;
by regenerating the committed fixtures and comparing exactly; and by confirming LF
endings and LF-vs-CRLF hash divergence.

## Synthetic-valid example (recorded exactly)

| Property | Value |
| --- | --- |
| bundle_id | `demo-zzq1-5m-2026-07-15` |
| profile_id | `demo-historical-ohlcv-csv.v1` |
| provider | `DEMO_FIXTURE_FEED` (fictional) |
| symbol / venue | `ZZQ1` / `DEMO_VENUE_X` (fictional) |
| raw artifact SHA-256 | `7025f1bdfd147106cc148a81ece75337396b70519382e1d91cdc4820db454a50` |
| raw artifact byte length | `551` |
| normalized bar count | `6` |
| preflight status | `READY_FOR_FUTURE_ASSOCIATION` |
| preflight report id | `fd213024-7924-5f87-8318-98b31d5854dc` |

## Committed fixtures

`tests/fixtures/acquisition/batch04/`:

```
submission-kit-manifest.json
intake-manifest.template.json
column-mapping-profile.template.json
case-association.template.json
synthetic-valid-intake-manifest.json
synthetic-valid-column-mapping-profile.json
synthetic-valid-bars.csv
synthetic-valid-preflight-report.json
invalid-scenario-index.json
troubleshooting-index.json
operator-checklist.json
determinism-anchors.json
fixture-metadata.json
```

The operator kit under `operator-kits/historical-market-bars/` is regenerated
byte-for-byte by the same generator; `submission-kit-manifest.json` records a
SHA-256 for every kit file, so any drift in a guide, template, or example is caught.

## Prior-artifact digests (no-regression guard)

Recorded before Batch 04 began and asserted unchanged by
`test_batch01_02_03_fixtures_are_unchanged`:

```
batch01  a4a6ece91800e215baeb197a6f178505c526d49c672f3274365bde4f624b407a
batch02  eefed973fb1c7e709c52060c274bf57b6d641993ac96e9e08687e75e818e30c4
batch03  39bbf1e52a19deb81a0b80bf1d93449dc08be3407d2697a9a0690ccef406a82e
```

## Classifications

Fixtures are classified `SYNTHETIC_EDGE_CASE` / `SYNTHETIC_FIXTURE`. The metadata
asserts `real_market_data_committed: false`, `outcome_work_performed: false`,
`sensitive_content_included: false`, `phase_3e_started: false`.
