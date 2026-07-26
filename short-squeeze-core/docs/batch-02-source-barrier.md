# Outcome-Acquisition Batch 02 — Source Barrier

This document records the lawful-source search performed for Batch 02 and the
exact barrier that prevented capturing the forward 24-hour outcome window. The
machine-readable record is committed as
`tests/fixtures/acquisition/batch02/outcome-source-search.json`.

## What was required

For each of the 13 frozen Batch 01 cases (boundary
`ORIGINAL_PLATFORM_SURFACED_TIMESTAMP` at `2026-07-18T13:37:55Z`), the outcome
policy `phase_3b_outcome_label_policy.v1` needs the forward market bars over the
24 hours after the boundary, at trade-bar (intraday) resolution, from a source
that is **public, lawful, non-authenticated, terms/robots-permitting, offline
reproducible, and provenance-preserving**.

## Sources evaluated and why each was unacceptable

| Source | Kind | Disposition |
| --- | --- | --- |
| SEC EDGAR | Government filings | Permissive automated access, but **no price/trade bars** (filings only) |
| Stooq | File download | `robots.txt` = `User-agent: * / Disallow: /` (only Googlebot/Bingbot) → **robots-disallowed** |
| Yahoo Finance chart endpoint | Undocumented JSON | Returns JSON without a key, but **Terms of Service prohibit** robot/scraper/automated access |
| Alpha Vantage | REST API | **API key / registration required** |
| EODHD | REST API | **API token / registration required** |
| StockData.org | REST API | **API token / registration required** |
| marketstack | REST API | **API access key required** |
| Financial Modeling Prep | REST API | **API key required** |
| Tiingo | REST API | **API token required** |
| Polygon.io | REST API | **API key required** |
| Nasdaq Data Link (Quandl) | REST API | **API key required** |
| Kibot free samples | File download | No registration, but **coverage excludes the case symbols** (demo tickers only) |
| MarketData.app free tier | REST API | No-token access limited to a **demo ticker**; others need an account |

## Conclusion

`NO_ACCEPTABLE_LAWFUL_NONAUTHENTICATED_SOURCE`

Every source that carries forward intraday bars for these specific symbols either
requires authentication (an API key or registration) — excluded by the
non-authentication constraint — or prohibits automated access in its terms or
robots rules — excluded by the no-terms-violation rule. The one clearly
permissive public source (SEC EDGAR) does not serve trade bars.

The outcome window is therefore not obtainable lawfully, reproducibly, and with
preserved provenance. Consistent with the handoff and explicit user
authorization, **no outcome value is fabricated and no current value is
represented as a historical value**. All 13 cases remain registry-only with the
limitation `OUTCOME_WINDOW_NO_LAWFUL_PUBLIC_SOURCE`, and the outcome manifest is
empty with status `UNAVAILABLE_NO_LAWFUL_PUBLIC_SOURCE`. Zero promoted complete
cases is an authorized, honest result under these conditions.
