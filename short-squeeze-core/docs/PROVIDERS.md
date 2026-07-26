# Providers

## Provider capabilities

| Provider | Capabilities | Credential | Cloud |
|---|---|---|---|
| Finviz Elite | Scanner fields, Float, Short Float (SI %), Short Ratio (DTC), Relative Volume, Shares Outstanding, news export | `FINVIZ_API_KEY` | Yes |
| NewsAPI | Timestamped symbol-associated display news | `NEWSAPI_KEY` | Yes |
| Finnhub | Current quote fallback, company news | `FINNHUB_KEY` | Yes |
| Finnhub News | Company-news endpoint for headline aggregation | `FINNHUB_KEY` (plan-dependent) | Yes |
| SEC EDGAR | Public filings and filing metadata | Descriptive `SEC_USER_AGENT` | Yes |
| FinBERT Sentiment | Local sentiment analysis (POSITIVE/NEUTRAL/NEGATIVE/MIXED) | Local model deployment | No |
| IBKR local | Read-only market data, bars, scanner, shortability, shortable shares, halted status | Host, port, client ID | No |
| IBKR Borrow Fee | Secondary market-data request (generic tick 258) | IBKR fundamental-ratios entitlement | No |

## Evidence admissibility

Fields carry a `research_admissibility` tag:

- `RESEARCH_ADMISSIBLE`: The field meets unit, time-basis, provenance, and
  freshness requirements for methodology evaluation.
- `RESEARCH_INADMISSIBLE`: The field is display-only; a matching provider field
  name does not imply semantic compatibility.
- `DISPLAY_ONLY`: The field is rendered but never enters a methodology or rule.

### Research-admissible fields (current pipeline)

| Field | Provider | Admissibility |
|---|---|---|
| `float_shares` | Finviz Elite | `RESEARCH_ADMISSIBLE` |
| `published_short_interest` (SI %) | Finviz Elite | `RESEARCH_ADMISSIBLE` |
| `days_to_cover` | Finviz Elite | `RESEARCH_ADMISSIBLE` |
| `relative_volume` | Finviz Elite | `RESEARCH_ADMISSIBLE` |
| `percentage_change` | IBKR | `RESEARCH_ADMISSIBLE` |
| `completed_bar_acceleration` | IBKR (computed) | `RESEARCH_ADMISSIBLE` |
| `catalyst_age_hours` | Computed (news + SEC) | `RESEARCH_ADMISSIBLE` |
| `borrow_availability_pct_float` | IBKR + Finviz (computed) | `RESEARCH_ADMISSIBLE` |
| `borrow_fee` | IBKR (secondary) | `RESEARCH_ADMISSIBLE` |

## Configuration

Each credential-bearing provider has an `*_ENABLED` switch. Disabled providers
report `DISABLED`. Enabled providers without required credentials report
`NOT_CONFIGURED`.

Providers retain last-good cached results where implemented and surface failures
without converting stale data into fresh evidence. Rate limits and entitlements
remain the provider account owner's responsibility.
