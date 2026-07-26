# Phase 2V BIYA Historical Data Acquisition Plan

## Request envelope

- Symbol: `BIYA`
- Intraday/event start: `2026-07-16T00:00:00-04:00`
- Daily-context start: `2026-07-01T00:00:00-04:00`
- End: the actual acquisition timestamp, explicitly supplied to every command
- Request timezone: `America/New_York`
- Preferred intraday interval: one minute; fallback: five minutes
- Sessions: regular and extended, preserved separately
- Output root: `data/acquisition/biya`

No deterministic path silently defaults to now. The orchestration command captures now
once, renders it as an explicit argument, and records it in every manifest.

## Attempt sequence

1. Record the completed local-data search as `EMPTY`.
2. Record IBKR intraday and daily attempts. If no gateway/entitlement is available,
   preserve `UNAVAILABLE` or `ENTITLEMENT_REQUIRED`, including the exposed market-data
   type (`LIVE`, `DELAYED`, `DELAYED_FROZEN`, `FROZEN`, `UNAVAILABLE`, or `UNKNOWN`).
3. Record Schwab attempts without invoking archived authentication helpers or allowing
   token refresh. Archived credentials and token files remain unchanged. If safe
   read-only access cannot be proven, record `UNAVAILABLE` explicitly.
4. Retrieve FINRA daily short-sale volume for each available trade date from July 16
   onward. Preserve raw public files and market/venue scope. Do not treat the data as
   short interest.
5. Attempt public historical news and official halt/corporate-action sources. Preserve
   publication and retrieval times separately.
6. Use a stable public historical market source only after steps 1-3 are represented in
   manifests. Acquire one-minute bars when available, otherwise five-minute bars, plus
   daily bars from July 1.
7. Attempt historical published short-interest records. Record settlement and
   publication dates independently.
8. Attempt borrow fee and availability only from already-local historical sources. If
   none exists, record `UNAVAILABLE`; never substitute a current quote.

Every attempt produces a manifest, including failures and fallbacks. Provider failure
is evidence, not an empty success.

## Immutable layout

```text
data/acquisition/biya/
  README.md
  raw/
    market_bars/
    news/
    halts/
    short_interest/
    short_sale_volume/
    borrow/
    corporate_actions/
  normalized/
  manifests/
```

Raw names include symbol, provider, data type, requested start/end, and retrieval time.
If a target already exists, acquisition fails rather than overwriting it. Raw SHA-256
is computed over exact bytes before normalization. Relative paths only are stored.

## Dataset requirements

Market-bar raw data retains OHLCV, timestamps, interval, trade count/VWAP when supplied,
provider, session, timezone, adjustment state, and retrieval time. Daily bars cover at
least July 1 through the retrieval boundary.

Halt evidence retains halt/resume times and code. News retains headline, publisher,
publication/update/retrieval times, sanitized public identifier, lifecycle state, and
classification relative to both detection boundaries. Published short interest retains
settlement date, publication date, shares short, provider, and revision state. FINRA
short-sale volume retains date, short volume, short-exempt volume, total volume, and
venue scope as its own evidence type. Borrow attempts retain source, historical
timestamp, fee/availability units, and limitations. Corporate-action evidence includes
the July 13 reverse split and any other supported action affecting comparability.

## Failure handling

DNS failures, rate limits, missing subscriptions, delayed entitlements, unsupported
instruments, insufficient historical depth, partial sessions, and unknown adjustment
states map to stable manifest states and diagnostic codes. Error text is sanitized and
must not contain credentials, token material, account IDs, private URLs, or absolute
paths. A partial response records its actual earliest/latest timestamp and missing
coverage.

## Processing commands

The acquisition script requires explicit `--symbol`, `--provider`, `--data-type`,
`--start`, `--end`, `--timezone`, `--session-scope`, and `--output`. Deterministic
normalization requires an explicit manifest and output directory. Amendment building
requires the immutable original case and normalized evidence inputs. Invalid requests
exit nonzero with canonical structured error output. No command writes a database,
opens a GUI, or exposes a trading operation.

