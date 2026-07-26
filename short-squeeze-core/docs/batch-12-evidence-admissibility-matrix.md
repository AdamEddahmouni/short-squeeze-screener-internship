# Evidence Admissibility Matrix — Batch 12

Each field must prove semantic compatibility before admission to Phase 3A evaluation.

## Market Data Domain

| Evidence | Source | Admissible? | Rule | Reason |
|----------|--------|------------|------|--------|
| Price Level | IBKR (delayed) | YES | PRICE_RANGE | Latest completed bar within 900s |
| Percentage Change | IBKR bars | YES | PERCENTAGE_CHANGE_MINIMUM | Canonical PERCENTAGE_RETURN metric |
| Provider Volume | IBKR quote | NO | RELATIVE_VOLUME_MINIMUM | Unit unresolved (Batch 06) |
| Relative Volume | — | NO | RELATIVE_VOLUME_MINIMUM | Cannot compute without volume baseline |

## Short Pressure Domain

| Evidence | Source | Admissible? | Rule | Reason |
|----------|--------|------------|------|--------|
| Shortable Indicator | IBKR (tick 236) | NO | BORROW_AVAILABILITY_MAXIMUM | Provider indicator, not canonical |
| Shortable Shares | IBKR | NO | BORROW_AVAILABILITY_CHANGE_MAXIMUM | Permission unavailable |
| Halt Status | IBKR (tick 49) | DISPLAY ONLY | TRADING_HALTS | Provider indicator only |
| Shares Outstanding | IBKR fundamentals | DISPLAY ONLY | FLOAT_MAXIMUM | Not float; different concept |
| Float | — | NO | FLOAT_MAXIMUM | No provider |
| Short Float % | — | NO | SHORT_INTEREST_* | No provider |
| Short Interest | — | NO | PUBLISHED_SHORT_INTEREST_AVAILABLE | No provider |
| Days to Cover | — | NO | DAYS_TO_COVER_MINIMUM | No short interest or volume |
| Borrow Fee | — | NO | BORROW_FEE_MINIMUM | No provider |

## Catalyst Domain

| Evidence | Source | Admissible? | Rule | Reason |
|----------|--------|------------|------|--------|
| SEC Filings Count | SEC EDGAR | DISPLAY ONLY | SEC_FILING_AVAILABLE | Count, not individual filing |
| Individual Filing | SEC EDGAR | DISPLAY ONLY | SEC_FILING_AVAILABLE | Display only, not canonical evidence |
| News | — | NO | NEWS_AVAILABLE | No provider |
| Sentiment | — | NO | — | No model loaded |

## Evidence Validity Domain

| Rule | Status | Reason |
|------|--------|--------|
| NO_DEFAULT_SUBSTITUTION | PASS | No values substituted |
| PROVIDER_SCOPE_EXPLICIT | PASS | IBKR scope declared |
| REQUIRED_DOMAINS_PRESENT | PASS | Market data domain present |
| NO_MATERIAL_CONFLICTS | PASS | Single provider per domain |
| POINT_IN_TIME_ELIGIBLE | PASS | As-of instant established |
| REQUIRED_UNITS_COMPATIBLE | PASS | Price unit compatible |
| REQUIRED_HISTORY_SUFFICIENT | PASS | Trailing window sufficient |

## Phase 3A Rule Coverage

| Category | Rules | Evaluable Before B12 | Evaluable After B12 |
|----------|-------|---------------------|-------------------|
| Momentum | 6 | 2 (PRICE_RANGE, PERCENTAGE_CHANGE_MINIMUM) | 2 (unchanged) |
| Short Pressure | 7 | 0 | 0 (unchanged) |
| Catalyst | 5 | 0 | 0 (filings display only) |
| Evidence Validity | 7 | 7 | 7 (unchanged) |
| **Total** | **25** | **9** | **9** |

The evaluable rule count did not increase because:
1. SEC filings are display-only (not canonical evidence)
2. Shortability/halts are raw provider indicators (not admissible)
3. No float, short interest, or borrow fee providers are configured
