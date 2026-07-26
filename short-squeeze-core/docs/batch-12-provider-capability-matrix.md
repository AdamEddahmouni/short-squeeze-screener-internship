# Provider Capability Matrix — Batch 12

## IBKR (Interactive Brokers)
Connected: YES (127.0.0.1:4001, DELAYED market data)

| Capability | Status | Detail |
|-----------|--------|--------|
| DISCOVERY | AVAILABLE | Scanner subscriptions |
| DELAYED_QUOTE | AVAILABLE | Generic tick list: 236,49,258,411 |
| REALTIME_QUOTE | PERMISSION_UNAVAILABLE | Market data subscription required |
| HISTORICAL_BARS | AVAILABLE | 1-min trailing window |
| SHORTABILITY | AVAILABLE | Generic tick 236 |
| HALTS | AVAILABLE | Generic tick 49 |
| VOLUME | AVAILABLE | Raw provider volume (unit unresolved) |
| FUNDAMENTALS | AVAILABLE | Generic ticks 258, 411 (shares outstanding etc.) |
| BORROW_FEE | PERMISSION_UNAVAILABLE | Not in market data entitlement |
| SHORTABLE_SHARES | PERMISSION_UNAVAILABLE | Not in market data entitlement |
| FLOAT | NOT_SUPPORTED | IBKR does not provide float |
| SHORT_INTEREST | NOT_SUPPORTED | IBKR does not provide short interest |
| NEWS | NOT_SUPPORTED | IBKR does not provide news in this setup |

## SEC EDGAR
Connected: YES (public API, no key required)

| Capability | Status | Detail |
|-----------|--------|--------|
| FILINGS | AVAILABLE | 8-K, 10-K, 10-Q, S-1 via data.sec.gov |
| All others | NOT_SUPPORTED | SEC provides filing data only |

## NOT_CONFIGURED Providers

| Provider | Missing Keys | Used For |
|----------|-------------|----------|
| NewsAPI | NEWSAPI_KEY | News headlines |
| Finnhub | FINNHUB_API_KEY | Market data, news |
| Alpha Vantage | ALPHA_VANTAGE_API_KEY | Market data |
| Schwab | SCHWAB_APP_KEY, SCHWAB_SECRET | Market data |
| Finviz | FINVIZ_ELITE_TOKEN | Screener data |

## Research Admissibility

| Field | Display Available | Research Admissible | Reason |
|-------|------------------|---------------------|--------|
| Last | YES | YES (current price) | Within 900s admissibility window |
| Bid, Ask | YES | NO | Display only |
| Open, High, Low | YES | NO | Display only |
| Previous Close | YES | NO | Display only |
| Percentage Change | YES | YES | Canonical PERCENTAGE_RETURN metric |
| Relative Volume | NO | NO | Batch 06 volume semantics unresolved |
| Shortability | YES | NO | Raw provider indicator only |
| Halt Status | YES | NO | Raw provider indicator only |
| SEC Filings | YES | NO | Public filing count only |
| Shares Outstanding | YES | NO | Provider fundamental data |
| Float, Short Float | NO | NO | No provider configured |
| Borrow Fee | NO | NO | No provider configured |
