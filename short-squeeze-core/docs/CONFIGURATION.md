# Configuration

## Precedence

For each supported setting, the resolver applies:

1. explicit command-line argument;
2. process environment variable;
3. explicitly supplied configuration file;
4. explicitly supplied private provider file in `LOCAL_FULL`;
5. safe default.

The resolved mode controls private-file eligibility. `CLOUD_PROVIDER_MODE` and
`FROZEN_DEMO` never load the private provider file. Tests and fake providers call
the resolver without a private path.

## Variables

| Variable | Required | Purpose |
|---|---|---|
| `SQUEEZE_APP_MODE` | Recommended | Runtime mode |
| `PORT` | Optional | HTTP port |
| `LOG_LEVEL` | Optional | Application log level |
| `FINVIZ_ENABLED` | Optional | Enable or disable Finviz |
| `FINVIZ_API_KEY` | When Finviz is enabled | Finviz Elite export token |
| `NEWSAPI_ENABLED` | Optional | Enable or disable NewsAPI |
| `NEWSAPI_KEY` | When NewsAPI is enabled | NewsAPI credential |
| `FINNHUB_ENABLED` | Optional | Enable or disable Finnhub |
| `FINNHUB_KEY` | When Finnhub is enabled | Finnhub credential |
| `SEC_ENABLED` | Optional | Enable or disable SEC EDGAR |
| `SEC_USER_AGENT` | When SEC is enabled | Organization and contact user agent |
| `SEC_CONTACT_EMAIL` | Optional | Administrative contact |
| `IBKR_ENABLED` | Optional | Enable local IBKR configuration |
| `IBKR_HOST` | When IBKR is enabled | Local gateway host |
| `IBKR_PORT` | When IBKR is enabled | Gateway API port |
| `IBKR_CLIENT_ID` | When IBKR is enabled | Read-only client identifier |

## Provider dependencies

| Methodology field | Requires |
|---|---|
| Published SI % | `FINVIZ_API_KEY` |
| Days to Cover | `FINVIZ_API_KEY` |
| Float Shares | `FINVIZ_API_KEY` |
| Relative Volume | `FINVIZ_API_KEY` |
| Borrow Avail % Float | `IBKR_ENABLED` + `FINVIZ_API_KEY` |
| Cost to Borrow | `IBKR_ENABLED` + fundamental-ratios entitlement |
| Bar Acceleration | `IBKR_ENABLED` |
| % Change | `IBKR_ENABLED` |
| Catalyst Age | Any news provider or SEC EDGAR |
| News Count | Any news provider |
| Sentiment | FinBERT local model (not available in cloud) |
| Shortable Indicator | `IBKR_ENABLED` |
| Halt Status | `IBKR_ENABLED` |

## Borrow fee

Borrow fee (cost to borrow) uses a secondary IBKR market-data request for
generic tick 258. This request fires after the base quote has completed so
that permission-scoped fundamentals failures cannot block primary price data.

The `BorrowFeeProvider` in `borrow_fee_live.py` manages this separate request
path. When IBKR fundamental-ratios entitlement is not available, borrow fee
reports `NOT_CONFIGURED` and the Pressure dimension remains constrained to
65/100 supported weight (below the 70% evaluation threshold).

To enable: ensure IBKR connection has fundamental-ratios market data
entitlement, then the provider will populate `borrow_fee` automatically
during each refresh cycle.

All changes require process restart.

## Doctor

```bash
python -m apps.research_screener.config doctor
python -m apps.research_screener.config doctor --json
python -m apps.research_screener.config doctor --config .env --no-ibkr-probe
```

The doctor reports configuration presence and compatibility, never values or
private absolute paths.
