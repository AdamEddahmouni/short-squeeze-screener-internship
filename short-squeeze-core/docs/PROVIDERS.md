# Providers

## Provider capabilities

| Provider | Capabilities | Credential | Cloud |
|---|---|---|---|
| Finviz Elite | Scanner fields, Float, Short Float (SI %), Short Ratio (DTC), Relative Volume, Shares Outstanding, news export | `FINVIZ_API_KEY` | Yes |
| NewsAPI | Timestamped symbol-associated display news | `NEWSAPI_KEY` | Yes |
| Finnhub | Current quote fallback, company news | `FINNHUB_KEY` | Yes |
| Finnhub News | Company-news endpoint for headline aggregation | `FINNHUB_KEY` (plan-dependent) | Yes |
| SEC EDGAR | Public filings and filing metadata (`filed_at` for catalyst age) | Descriptive `SEC_USER_AGENT` | Yes |
| FinBERT Sentiment | Local sentiment analysis (POSITIVE/NEUTRAL/NEGATIVE/MIXED) | Local model deployment | No |
| IBKR local / remote | Read-only market data, bars, scanner, shortability, shortable shares, halted status | Host, port, client ID (+ login for Gateway containers) | Remote only in cloud |
| IBKR Borrow Fee | Secondary market-data request (generic tick 258) | IBKR fundamental-ticks entitlement | Remote entitlement |

## Evidence admissibility

Fields carry a `research_admissibility` tag:

- `RESEARCH_ADMISSIBLE`: Meets unit, time-basis, provenance, and freshness requirements for methodology evaluation.
- `RESEARCH_INADMISSIBLE`: Display or supplemental; a matching provider field name does not imply semantic compatibility.
- `DISPLAY_ONLY`: Rendered but never enters a methodology or rule.

### Research-admissible fields (current pipeline)

| Field | Provider | Admissibility |
|---|---|---|
| `float_shares` | Finviz Elite | `RESEARCH_ADMISSIBLE` |
| `published_short_interest` (SI %) | Finviz Elite | `RESEARCH_ADMISSIBLE` |
| `days_to_cover` | Finviz Elite Short Ratio | `RESEARCH_ADMISSIBLE` |
| `relative_volume` | Finviz Elite | `RESEARCH_ADMISSIBLE` |
| `percentage_change` | IBKR canonical return | `RESEARCH_ADMISSIBLE` |
| `completed_bar_acceleration` | IBKR (computed) | `RESEARCH_ADMISSIBLE` |
| `catalyst_age_hours` | Computed (news + SEC `filed_at`) | `RESEARCH_ADMISSIBLE` |
| `borrow_availability_pct_float` | IBKR + Finviz (both legs required) | `RESEARCH_ADMISSIBLE` |
| `borrow_fee` | IBKR (secondary) | `RESEARCH_ADMISSIBLE` |

Display-only / research-inadmissible proxies (shown, not scored): estimated DTC from
Short Float / Avg Volume, and Finviz day-change when IBKR `PERCENTAGE_RETURN` is
missing. Conflicting Finviz field mappings are withheld from scoring.

## Configuration

Each credential-bearing provider has an `*_ENABLED` switch. Disabled providers
report `DISABLED`. Enabled providers without required credentials report
`NOT_CONFIGURED`.

Providers retain last-good cached results where implemented and surface failures
without converting stale data into fresh evidence. Rate limits and entitlements
remain the provider account owner's responsibility.

Setup recipes: [how-to-guides.md](how-to-guides.md#enable-providers-ibkr--finviz--news--sec).
Variable reference: [CONFIGURATION.md](CONFIGURATION.md).
