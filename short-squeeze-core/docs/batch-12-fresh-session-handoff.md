# Batch 12 — Fresh Session Handoff

Branch: `batch/full-operational-live-screener-11` (or new `batch/...-12`)
Parent: `0895731` (Batch 11 completion)

## What Batch 11 delivered

A fully operational two-mode research screener:
- **Frozen Research**: 13 cases, 325 evaluations, canonical Batch 08 freeze
- **Current Operational**: Live IBKR scanner, round-robin refresh, current Phase 3A evaluation, auto-refresh, charts, filters, export
- 706 tests passing, 0 failures

## What remains for Batch 12

### 1. Live field entitlement upgrade (P1)
The current IB Gateway entitlement returns PERMISSION_UNAVAILABLE for:
- Real-time quotes (error 10167)
- Shortability indicator (generic tick 236)

With upgraded market data subscriptions:
- Wire `last`, `bid`, `ask` from streaming quotes
- Wire `shortable_indicator` from generic tick 236
- Wire `shortable_shares` from size tick 89
- Investigate generic ticks: 258 (fundamental ratios), 292 (short interest)

See `apps/research_screener/ibkr_session.py` for the tick mapping.

### 2. Weekday market-session verification (P1)
The smoke test was conducted on Saturday. During market hours:
- Verify REALTIME market data mode
- Verify PRICE_RANGE evaluates with fresh prices
- Verify quote ticks populate all price fields
- Verify freshness shows CURRENT (not STALE)

### 3. Phase 3E predictive validation (P2)
The batch brief repeatedly mentions Phase 3E as unstarted. This is:
- Predictive validation of the research system
- Operating characteristics calculation
- Retrospective performance analysis
- **Not** forward-looking trading signals

See the original Phase 3x documentation for details.

### 4. News integration (P3)
Current status: NOT_CONFIGURED
Options to investigate:
- IBKR news bulletins via `reqNewsBulletins` (if entitled)
- Lawful RSS/API news sources
- FinBERT sentiment over headlines (labeled EXPERIMENTAL)

### 5. Float/short-interest (P3)
Current status: NOT_CONFIGURED
Options:
- IBKR `reqFundamentalData` for market cap/float
- FINRA short interest data (public, delayed)
- Published SEC filings

## Important: do not touch
- `docs/phase-3c-complete-handoff.md` (pre-existing, unrelated)
- Batch 05 raw artifacts
- Batch 08 freeze
- Batch 09 preview
- Canonical Phase 3B registry
- Any `src/squeeze_core/` isolation guards

## Quick-start
```powershell
cd <repo-root>\short-squeeze-core
.\run_screener.ps1
# => http://127.0.0.1:8787/

# Run tests
.\.venv\Scripts\python.exe -m pytest tests/app/ -p no:cacheprovider --basetemp C:\Temp\pytest
```

## Architecture note
The application lives in `apps/research_screener/`, NOT in `src/squeeze_core/`.
`src/squeeze_core` is a closed research core with an allowlist guard that forbids
`tools/` and `ibapi` imports. Do not move application code into `src/`.
