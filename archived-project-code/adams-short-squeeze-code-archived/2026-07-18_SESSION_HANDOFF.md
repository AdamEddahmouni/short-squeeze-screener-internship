# Session Handoff — 2026-07-18

**Status at end of session: app fully shut down, uncommitted code changes, live demo data frozen
on disk (gitignored, local-only).** This doc exists so another agent or a human picking this repo
up later doesn't have to reverse-engineer what happened from `git status` alone.

## 1. Shutdown state (verified, not assumed)

- No `python`/`python3` process running anywhere on this machine (`Get-Process python*` returns
  nothing).
- Port 8000 confirmed not listening (`curl http://localhost:8000/health` → connection refused).
- The app (`app/ScreenerProject/main.py`) was running via a local preview server
  (`.claude/launch.json`'s `squeeze-gui` config) for a live demo earlier this session, then
  stopped cleanly. Nothing needs to be killed to restart clean.
- **IB Gateway/TWS itself** (the external broker application, separate from this app) was not
  touched by this session — if it's still running on the operator's machine, that's independent
  of this app's shutdown.

## 2. Uncommitted code changes (in `app/ScreenerProject`, the git submodule)

Two features were designed (via explicit plan-mode sessions), implemented, tested, and
live-verified today, but **not committed**:

```
M controller/controller.py
M core/ib_api.py
M core/squeeze_score.py
M static/app.js
M tests/test_controller_snapshot.py
M tests/test_ib_api.py
M tests/test_squeeze_score.py
M ui/view.py
```

### 2a. TTM Squeeze "fire" detection (`ttm_squeeze_fired`)

Answers "catch it before it jumps" — the advisor's repeated complaint that this app only
confirms a squeeze *after* a big move already happened. New signal: true exactly on the cycle a
ticker's TTM Squeeze compression releases (was compressed last time this ticker was seen, isn't
now, momentum not contradicting a bullish move). Independent of Prime/Subprime tier and
`squeeze_score` — a leading counterpart to the existing (lagging) `squeeze_confirmed`.

- `core/squeeze_score.py::is_ttm_squeeze_fired()` — pure function, the transition logic.
- `controller/controller.py::Controller._apply_ttm_fired()` — the first cross-cycle, in-memory
  per-ticker state this codebase has ever needed (`self._ttm_state`), with a provider-switch guard
  (IB↔Schwab failover between cycles must not masquerade as a real fire event) and `None`-gap
  preservation (a transient "not enough bars" reading doesn't erase memory of a real prior state).
- Web UI: overlays a third badge state ("Just Released", `badge-critical`) onto the existing
  "Vol. Compression" cell in `static/app.js` — no new column.
- **Honest limitation, disclosed in code comments**: real time-resolution is bounded by how often
  the underlying daily bars refresh (see 2b) — not instant.
- Threaded through `controller.py`'s shared positional row tuple (now 33 elements,
  `TtmSqueezeFired` appended last) — see §3.5 of `SQUEEZE_FORMULA_REDESIGN_HANDOFF.md` for why
  this specific tuple is the highest-risk touch point in this codebase if extended again.

### 2b. IB historical-bar rate limiter + shorter cache TTL

Prompted by a user request for "everything real time" — correctly pushed back on (short interest
can never be real-time, it's FINRA's twice-monthly reporting cadence, not an engineering
limitation) and re-scoped to the one part that was both safe and valuable: refreshing TTM
Squeeze/RSI/weekly-volatility/average-volume faster than the previous flat 1-hour cache.

**Critical finding from this session**: there was previously **no rate-limiting mechanism at all**
for `reqHistoricalData` calls — the 1-hour cache TTL was the entire safety margin against IB's
documented ~60-requests/10-minute pacing limit. Shortening the TTL alone, without adding real
pacing, would have risked a burst of 50 concurrent historical-bar requests on a cache-cold cycle —
an immediate limit violation and a real risk of the live IB connection getting throttled.

- `core/ib_api.py::_hist_rate_limit_allows()` — new sliding-window limiter, pure/sync, capped at
  **55** calls/600s (deliberately below IB's documented "~60" for margin against an
  approximately-specified external limit).
- `HIST_CACHE_TTL_SECONDS` shortened from `3600` (1hr) to `300` (5min nominal) — real achieved
  freshness settles around 5-10 min under realistic scanner load (50 tickers, gated by the rate
  limiter, not the TTL alone).
- Deliberately **not** touched: `core/schwab_api.py`'s independent 1-hour cache (no
  independently-verified Schwab rate limit exists anywhere in this codebase to safely tune
  against).
- Live-verified over 60+ real seconds spanning multiple 15s enrichment cycles: zero pacing-related
  errors in logs, TTM/RSI-derived fields still populating normally on real rows, no spurious
  `historical_bars_unavailable` degradation.

### Test status

All 269 tests pass (`python -m pytest tests/ -q` from `app/ScreenerProject/`) as of this session,
including 13 new tests for 2a and 8 new tests for 2b.

### To pick this back up

```
cd app/ScreenerProject
python -m pytest tests/ -q      # confirm still 269 passing
git diff                         # review the two features above
git log --oneline -5             # last real commit was the squeeze formula redesign (2026-07-17)
```
If committing, this project's established pattern (see recent `git log`) is: commit inside the
`app/ScreenerProject` submodule first, then a second commit in the superproject to bump the
submodule pointer.

## 3. Live demo data (frozen, local-only, not in git)

`app/ScreenerProject/data/*` is gitignored (`data/*` in `.gitignore`) — these files exist only on
this machine, not visible to another agent working from git history alone:

- `screener_snapshot.json` — the last live snapshot served by `/screener` before shutdown
  (13 real IB-sourced Subprime setups, 0 Prime, as of the last demo run today).
- `squeeze_score_history.csv` / `corroboration_history.csv` — per-cycle time series, used for the
  web UI's sparklines and the (currently still-empty, "picks need to age a day") Track Record
  panels.
- `prime_log.csv`, `news_snapshot.json`, `schwab_tokens.json` — supporting state, all frozen at
  their last-write timestamp since the process stopped.

None of this was cleared or modified this session — it's exactly as the app left it. If a fresh
demo is needed later, restarting `main.py` will resume writing to these same files.

### Live demo reference point

Top-ranked ticker during today's demo was **BHVN** (`squeeze_score: 68.1`, Subprime — just under
the 70 Prime threshold), driven mainly by `days_to_cover: 9.2` (near the 10-day saturation
ceiling) and `ttm_squeeze_on: true` (volatility compression present); `short_float` was moderate
(16.5%) and `borrow_fee` was unavailable (see §4). Neither `squeeze_confirmed` nor
`ttm_squeeze_fired` were true for BHVN — the reading reflected a squeeze-conducive setup, not an
active/confirmed squeeze in progress.

## 4. Known outstanding issue (pre-existing, not from this session)

**IB's borrow-fee feed is still down** — `ib_borrow_fee_rate` is `null` on every live row,
`borrow_fee_feed_down` quality flag firing systemically. This was already documented in
`SQUEEZE_FORMULA_REDESIGN_HANDOFF.md` §2 (confirmed unreachable at the TCP level on 2026-07-17)
and remains unresolved as of this session. It means the squeeze-score composite is currently
running on 3 of its 4 intended inputs for every IB-sourced row.

## 5. Where else to look

- `SQUEEZE_FORMULA_REDESIGN_HANDOFF.md` — the squeeze-tier classification redesign (done, committed
  2026-07-17), including the shared-positional-tuple footgun this session's `TtmSqueezeFired`
  addition had to work around carefully.
- `PROJECT_NOTES.md` — the long-running engineering notes doc; **not updated this session** (its
  §4/§10 predate the squeeze formula redesign and are stale - worth a pass next time someone's
  doing doc cleanup, not done here to keep this handoff focused).
- Claude's persistent memory (if using Claude Code with memory enabled) has entries on advisor
  priorities and data-source status - worth checking for anything that's shifted since this was
  written.
