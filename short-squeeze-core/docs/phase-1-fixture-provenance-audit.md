# Phase 1 Fixture-Provenance Audit

Every fixture family is classified with exactly one allowed provenance class. No fixture contains
credentials, account identifiers, emails, live/routable URLs, or environment-specific absolute
paths. All sample URLs use the reserved, non-routable `.invalid` TLD. These guarantees are
enforced by `tests/compatibility/test_phase_1_fixture_provenance.py`.

## Allowed provenance classes

- `SANITIZED_RECORDED_SAMPLE` — a real recorded row, sanitized. **Not currently used** by any
  family; every metadata file records `recorded_sample_found: false` (or equivalent). This is
  honest: no representative sample is overstated as recorded.
- `SANITIZED_REPRESENTATIVE_SAMPLE` — a hand-built record matching a documented provider shape,
  with invented values.
- `SYNTHETIC_EDGE_CASE` — a synthetic record constructed to exercise a specific edge case.

## Family classification

| Provider (phase) | Metadata shape | Declared classes | Notes |
| --- | --- | --- | --- |
| ibkr (1B) | inline per-case `metadata.origin` | REPRESENTATIVE, SYNTHETIC | Provenance is carried inline in each case file, not a separate `fixture_metadata.json`. |
| finviz (1C) | `families[].origin` | REPRESENTATIVE, SYNTHETIC | |
| finra (1D) | `allowed_origins` + inline case origins | REPRESENTATIVE, SYNTHETIC | |
| sec (1E) | `allowed_origins` + inline case origins | REPRESENTATIVE, SYNTHETIC | |
| halts (1F) | `allowed_origins` + inline case origins | REPRESENTATIVE, SYNTHETIC | |
| news (1G) | `allowed_origins` + inline case origins | REPRESENTATIVE, SYNTHETIC | URLs sanitized; `.invalid` hosts only. |
| market_bars (1H) | `allowed_origins` + inline case origins | REPRESENTATIVE, SYNTHETIC | |
| trades_quotes (1I) | `families[].origin` | REPRESENTATIVE, SYNTHETIC | |

### Finding FP-1 (INFORMATIONAL): fixture-metadata schema drift

The `fixture_metadata.json` shape is not uniform across phases: Phase 1B carries provenance inline
per case; finviz and trades_quotes use a `families` list; finra/sec/halts/market_bars/news use a
top-level `allowed_origins` list plus inline per-case `origin`. All shapes are honest and every
declared class is within the allowed set — the provenance test is deliberately shape-tolerant and
also scans every inline `origin` value across all fixtures. Converging on a single metadata schema
would change fixture bytes and therefore recorded provider content hashes, so it is **deferred**,
not applied, to preserve the deterministic anchors. Recorded as intentional/deferred in the
architecture-consistency notes.

## Sensitive-content scan results

| Check | Result |
| --- | --- |
| Credential / token / account-id patterns | none found |
| Email addresses | none found |
| Routable / live URLs | none — all URLs use `.invalid` hosts |
| Environment-specific absolute paths (`C:\Users`, `/home/`, `/Users/`) | none found |
| Real symbols | fixtures use synthetic symbols (`TESTA`/`TESTB` and provider-neutral tickers); each family declares `contains_real_symbols: false` |

## Content-vs-metadata agreement

Provider fixture file contents are hash-anchored in the committed
`expected_phase_1{h,i}_bundle_metadata.json` files and re-verified against the centralized
manifest by `tests/compatibility/test_phase_1_anchor_manifest.py`, so any silent edit to a
fixture body is caught. Expected normalization results declared in fixture metadata are exercised
by the per-provider `tests/adapters/*/test_provider_fixtures.py` suites.
