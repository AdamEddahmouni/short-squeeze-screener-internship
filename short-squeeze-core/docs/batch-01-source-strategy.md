# Batch 01 — Source and Sampling Strategy

## Discovery source

A single **archived original-platform market-scanner snapshot** is the sole
systematic discovery source:

| Property | Value |
| --- | --- |
| Source class | `ARCHIVED_MARKET_SCANNER` (preferred source order #1/#3) |
| Archived path (read-only) | `archived-project-code/adams-short-squeeze-code-archived/app/ScreenerProject/data/screener_snapshot.json` |
| Raw SHA-256 | `4e5fbec4e1b8f77071752c90c814b60bb465ffe2d8119f3603e6d5d0f667d598` |
| Raw byte length | 20104 |
| Capture timestamp | `2026-07-18T13:37:55.017661Z` (single point-in-time) |
| Rows (symbols) | 13 distinct US-listed tickers |

Symbols, in snapshot (source) order: XNCR, PESI, SLS, ZNTL, GPRE, SSPC, LBGJ,
TRVI, LMNX, MGNX, BHVN, OBE, AVTX.

## Why this source is outcome-blind

The snapshot was written by the scanner **at scan time**. Every field it carries
is either detection-time market state (price, relative volume, intraday percent
change, short-float percent, days-to-cover, shares short, float) or the
platform's *contemporaneous prediction*. None of it is a forward 24-hour outcome.
Using this snapshot for discovery therefore cannot leak the ±25% / 24-hour
outcome the Phase 3B outcome policy would later measure.

The scanner can and does surface symbols that later went up, down, nowhere, or
became unevaluable — it selects on detection-time criteria, not on results.

## Score-blind and prediction-blind selection

The raw row also carries the platform's own opinions: `squeeze_score`,
`squeeze_score_breakdown`, `setup_tier` (the deprecated prime/subprime concept),
`squeeze_confirmed`, `target_percent`, `stop_loss_percent`, `corroboration_score`,
and sentiment. These are **dropped** by the collection utility
(`scripts/acquisition/import_batch01_discovery.py`) and never enter the sanitized
discovery rows or any generated artifact. Selection and ordering use the natural
snapshot order only — never the platform score/tier. This keeps the deprecated
Prime/Subprime and scoring concepts out of the new deterministic outputs
(handoff §31) and avoids any score-driven (outcome-adjacent) selection.

`squeeze_score_history.csv` (a timestamped score log in the same archived
directory) was deliberately **rejected** as a discovery source for the same
reason: selecting from it would be score-driven.

## Known selection biases (disclosed)

- **Gapper / high-activity bias.** The scanner surfaces names with elevated
  relative volume, notable intraday percent change, and/or elevated short float.
  All 13 rows were tagged `subprime` by the platform. The candidate stream is
  therefore not a random sample of the market; it is the scanner's detection-time
  watchlist. This bias is preserved and disclosed, not corrected.
- **Single-snapshot bias.** One capture instant on one day; not a multi-day or
  multi-session sample.
- **Provider-availability bias.** IB borrow-rate and shortable-share feeds were
  down at capture (`quality_flags`), so borrow evidence is absent for every case.

## Provenance discipline

- The raw provider-embedded artifact is **referenced by hash, not copied** into
  the repository, because it embeds IB/Schwab/yfinance-derived borrow data that is
  retained locally but not redistributed. Classification:
  `RESTRICTED_LOCAL_ARTIFACT`.
- The committed derived artifact is the **sanitized** discovery rows at
  `intake/batches/phase-3d-historical-source-collection-01/normalized/batch01_discovery_rows.json`
  (`DERIVED_NORMALIZED_ARTIFACT` / `SANITIZED_LOCAL_ARTIFACT`).
- Retrieval/capture time is preserved separately from historical event time; no
  current value is represented as a historical point-in-time value.

## Collection vs. curation separation

- **Collection** (`scripts/acquisition/import_batch01_discovery.py`) reads the
  archived artifact once and writes the sanitized rows. It is **not** part of the
  deterministic runtime and is **not** imported by any test.
- **Curation** (`squeeze_core.acquisition.batch01`) is pure, offline, and
  deterministic: given the committed sanitized rows it regenerates every batch
  document byte-for-byte, with no network, environment, clock, or randomness.
