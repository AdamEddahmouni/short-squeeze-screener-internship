# Batch 12 Completion Report — Live Provider Wiring

**Branch:** `batch/live-provider-wiring-12`
**Started from:** `9236e4123d401066913b53b3d5ea264c519e61a5` (Batch 11 HEAD)
**Final HEAD:** (see git log)

## Summary

Batch 12 wired live data sources into the operational screener, expanding 
provider coverage from IBKR-only to IBKR + SEC EDGAR, implementing a 
provider capability registry, and enabling field-level provider selection.

## What Was Done

### 1. Provider Capability Registry (`provider_capabilities.py`)
- Independent capability tracking per provider
- Status per capability: AVAILABLE, PERMISSION_UNAVAILABLE, NOT_CONFIGURED, NOT_SUPPORTED, ERROR, UNTESTED
- Field-level provider selection with deterministic ordering
- Provider merge safety (never silently overwrite)
- Credential non-disclosure (only key NAMES exposed, never values)

### 2. SEC EDGAR Integration (`sec_edgar.py`)
- Public SEC API (no API key required)
- Ticker→CIK lookup via company_tickers.json
- Recent filings: 8-K, 10-K, 10-Q, S-1, and more
- Proper User-Agent with contact info (SEC requirement)
- Gzip decompression handling
- Rate limiting (respects SEC fair-access policy)
- In-memory CIK cache

### 3. IBKR Expansion
- Added generic tick 49 (halted) to quote requests
- Added generic ticks 258, 411 (fundamental ratios) to quote requests
- Updated QuoteTicks to carry fundamentals dict
- Updated tickString handler for fundamental data
- Parse IBKR fundamental ratios for shares outstanding

### 4. UI Updates
- Added `/api/capabilities` endpoint — full provider capability matrix
- Added `/api/coverage` endpoint — field-level coverage summary
- Added `/api/refresh/all` endpoint — Refresh All Available Evidence
- Added SEC EDGAR and Trading Halts to provider health panel
- Live Provider statuses include SEC and Halts status

### 5. Phase 3A Integration
- SEC filings now flow through catalyst_fields with provenance
- Halt status available via IBKR generic tick
- Shares outstanding parsed from fundamentals
- All new fields carry provider, event time, freshness, evidence mode

## Provider Capability Matrix

| FIELD | PROVIDER | CONFIGURED | STATUS |
|-------|----------|-----------|--------|
| Last, Bid, Ask, Open, High, Low | IBKR | YES | AVAILABLE (DELAYED) |
| Previous Close | IBKR | YES | AVAILABLE (DELAYED) |
| Volume (raw) | IBKR | YES | AVAILABLE (unresolved unit) |
| Relative Volume | — | — | NOT_ADMISSIBLE (Batch 06) |
| Float | — | — | NOT_CONFIGURED |
| Shares Outstanding | IBKR | YES | AVAILABLE (if fundamentals tick) |
| Short Float % | — | — | NOT_CONFIGURED |
| Published Short Interest | — | — | NOT_CONFIGURED |
| Days to Cover | — | — | NOT_CONFIGURED |
| Borrow Fee | — | — | NOT_CONFIGURED |
| Shortable Shares | IBKR | YES | PERMISSION_UNAVAILABLE |
| Shortability | IBKR | YES | AVAILABLE (generic tick 236) |
| Trading Halts | IBKR | YES | AVAILABLE (generic tick 49) |
| SEC Filings | SEC EDGAR | YES | AVAILABLE (public API) |
| News | — | — | NOT_CONFIGURED (NEWSAPI_KEY) |
| Sentiment | — | — | NOT_CONFIGURED (model not loaded) |

## Test Results

- **Before Batch 12:** 2496 passed, 1 skipped, 0 failed
- **After Batch 12:** 2528 passed, 1 skipped, 0 failed
- **New tests:** 32 (provider capabilities, SEC EDGAR, IBKR ticks, parse functions)

## Real Provider Smoke Test

| Provider | Status | Detail |
|----------|--------|--------|
| IBKR | CONNECTED | Port 4001 |
| SEC EDGAR | AVAILABLE | CIK lookup + filings working |
| Capability Registry | OK | All categories tracked |

## Frozen Research Integrity

- 13 cases — UNCHANGED
- 97 PASS / 20 FAIL / 208 UNKNOWN — UNCHANGED
- No current→historical substitution
- No forward outcome use
- No fabricated evidence
- No credential leakage
- No account-data access
- No order functionality

## Remaining Unavailable Fields

| Field | Exact Reason |
|-------|-------------|
| Float | No float provider configured. Not in IBKR data. |
| Short Float % | No short interest provider. FINRA data integration needed. |
| Published Short Interest | No provider configured. |
| Borrow Fee | IBKR entitlement insufficient for fee data. |
| News | No NEWSAPI_KEY in environment. |
| Sentiment | FinBERT model not loaded in runtime. |
| Real-time quotes | IBKR market data subscription required. |

## Phase 3E

NOT STARTED. Deliberately deferred per explicit priority.
