# Integration Team Handoff

## Delivery options

- Local: `http://127.0.0.1:8000/screener` and `/health` while `ScreenerProject/main.py` runs.
- Cloud: deploy `app/vercel-api`, configure `MONGODB_URI`, and use the same endpoint paths.
- The response contract is the same for both delivery paths.

## Schema v1

`GET /screener` returns a JSON list. A fresh empty `[]` is valid: the completed scan found no
Prime/Subprime matches. Check `/health` rather than treating an empty list as an outage.

Example with built-in sentiment enabled (the default) — a real row captured 2026-07-13 during
live IB + Schwab verification:

```json
[
  {
    "schema_version": 1,
    "ticker": "AGEN",
    "price": 6.12,
    "float_shares": 38852805.0,
    "rel_volume": 226.44,
    "change_percent": 82.69,
    "short_float_percent": 15.43,
    "target_percent": 25.69,
    "stop_loss_percent": -10.5,
    "setup_tier": "prime",
    "source": "ib",
    "timestamp": "2026-07-13T19:57:30.990234-04:00",
    "shares_short": 5994778,
    "days_to_cover": 11.98,
    "short_interest_as_of": "2026-06-30",
    "short_interest_source": "yfinance",
    "float_as_of": "2026-07-13T23:54:58.796204+00:00",
    "float_source": "yfinance",
    "ib_shortable_shares": 0,
    "ib_shortable_shares_as_of": "2026-07-13T23:57:08.384806+00:00",
    "schwab_htb_quantity": null,
    "schwab_htb_rate": null,
    "schwab_is_hard_to_borrow": null,
    "schwab_htb_as_of": null,
    "corroboration_score": 3,
    "corroborated_by": ["schwab"],
    "quality_flags": [],
    "sentiment_label": "Positive",
    "sentiment_confidence": 0.77
  }
]
```

Field notes:

- `shares_short`/`days_to_cover`/`short_interest_*`: officially reported open short interest and its
  source/provenance. Can lag up to several weeks (FINRA settlement cadence) — never intraday.
- `ib_shortable_shares`/`ib_shortable_shares_as_of`: IB's own broker-inventory borrow signal (tick
  236). A different concept from `shares_short` — broker-available-to-borrow, not official short
  interest. `null` when the row's source isn't IB.
- `schwab_htb_quantity`/`schwab_htb_rate`/`schwab_is_hard_to_borrow`/`schwab_htb_as_of`: Schwab's
  equivalent borrow-availability signal from `/quotes`. Same "broker inventory, not official short
  interest" caveat. `null` when the row's source isn't Schwab.
- `corroboration_score`/`corroborated_by`: cross-provider corroboration (added 2026-07-13). When IB
  wins the cycle and Schwab is independently available, Schwab's own data for that same ticker is
  rescored against the identical 0–4 Prime/Subprime rubric; `corroboration_score` carries that
  result and `corroborated_by` lists which other provider(s) agreed (currently only ever `[]` or
  `["schwab"]`). **This is a confidence label, not a filter** — a ticker is never dropped from the
  results for lacking corroboration, and both fields are simply `null`/`[]` (never fabricated) when
  corroboration wasn't attempted that cycle (Schwab unavailable, or a different provider won).
- `quality_flags`: a list of strings noting data-quality caveats for that row (e.g. a provider/local
  short-float discrepancy, missing data). Empty list when nothing to flag.

The integration team is developing its own sentiment component. Set this in the local
`ScreenerProject/.env` to omit the two replaceable sentiment fields before local or cloud delivery:

```env
INCLUDE_SENTIMENT_OUTPUT=false
```

All other fields and `schema_version` remain unchanged — the same row as above, minus
`sentiment_label`/`sentiment_confidence`, with the replaceable sentiment output disabled.

## Health and freshness

`GET /health` returns `200` only when the latest snapshot is at most 60 seconds old:

```json
{
  "status": "ok",
  "schema_version": 1,
  "snapshot_available": true,
  "snapshot_age_seconds": 8.3,
  "last_updated": "2026-07-12T19:30:00+00:00"
}
```

Non-ready states return `503`: local `starting`/`unavailable`/`stale`; cloud `misconfigured`, `starting`,
`unavailable`, or `stale`.

Field freshness is intentionally mixed:

- Price and IB borrow enrichment: 15-second best-effort cadence after cache warm-up.
- API/local/MongoDB snapshot: 15-second cadence.
- RSI, volatility, and historical volume: cached for one hour.
- Float and short-float: cached for 24 hours; official short-interest data is not intraday.
- yfinance news: cached for 10 minutes; NewsAPI fallback: 30 minutes.

## Configuration and ownership

- Copy `app/ScreenerProject/.env.example` to `.env`; never share or commit the real `.env`.
- Each operator supplies its own IB Gateway/TWS account and `IB_HOST`/`IB_PORT`/`IB_CLIENT_ID`.
- The quoted **$4.50/month** applies to one qualified non-professional IBKR Pro user subscribing to
  Network A, B, and C at $1.50 each. IB normally also requires $500 account equity and completion of
  its Market Data API acknowledgement. Code may be shared for development; the subscribed user's
  live feed remains local to that user.
- `MONGODB_URI` is optional for local delivery and required only for the cloud read API.
- The screener is read-only and does not place trades.

## Verification before consumption

1. Confirm `/health` returns HTTP 200 and `status: "ok"`.
2. Confirm every non-empty row has `schema_version: 1`.
3. Decide whether this app or the integration team's component owns sentiment output.
4. Treat `null` numeric values as unavailable data, not zero.
5. Treat a healthy empty list as a valid no-matches scan.
