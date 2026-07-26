# Intake — historical source collection batch 01

Local intake for the preregistered batch
`phase-3d-historical-source-batch-01`.

## Contents

- `normalized/batch01_discovery_rows.json` — the committed **sanitized** discovery
  rows: 13 symbols from the archived scanner snapshot, detection-time factual
  fields only. Produced once by `scripts/acquisition/import_batch01_discovery.py`
  and consumed by the deterministic curator `squeeze_core.acquisition.batch01`.

## Raw artifact (intentionally NOT stored here)

The raw scanner export is a `RESTRICTED_LOCAL_ARTIFACT` (embeds IB/Schwab/yfinance
provider-derived borrow data) and is **referenced by hash, not copied**:

| Field | Value |
| --- | --- |
| Archived path (read-only) | `archived-project-code/adams-short-squeeze-code-archived/app/ScreenerProject/data/screener_snapshot.json` |
| SHA-256 | `4e5fbec4e1b8f77071752c90c814b60bb465ffe2d8119f3603e6d5d0f667d598` |
| Byte length | 20104 |
| Capture timestamp | `2026-07-18T13:37:55.017661Z` |

## Generated outputs

Curation writes to `build/acquisition/batch-01/` (gitignored, regenerable) with
byte-identical canonical copies committed under
`tests/fixtures/acquisition/batch01/`. See `docs/batch-01-*.md`.
