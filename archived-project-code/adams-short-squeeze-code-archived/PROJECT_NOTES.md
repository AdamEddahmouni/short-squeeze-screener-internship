# Short Squeeze Screener — Technical Project Notes

Technical reference for the codebase: architecture, what works, what's broken, and the backlog.
For advisor/course context, see **[RESEARCH_LOG.md](RESEARCH_LOG.md)**. For exact step-by-step
history of every change (commands run, exact code diffs), see `git log` in both this repo and the
`app/ScreenerProject` submodule — every entry below has a matching commit with full detail.

## 1. Codebase context

- Prior author: William "Will" Gray. Original repo: `github.com/wtg5058-byte/SHORTSQUEEZE`.
- A separate "integration team" needs this screener's output eventually. **Decided:** the
  schema-v1 API (§9) is the deliverable stub they build against — it is not blocked on a formal
  spec from them first, and getting one is not an outstanding task.

## 2. Repo layout

```
short-squeeze-code/
├── app/
│   ├── ScreenerProject/     ACTIVE app. Own git repo (submodule).
│   └── vercel-api/          Cloud-hosted read API (FastAPI + MongoDB), see §9a. Not a submodule.
├── data-workbooks/          Excel workbooks, not wired to the app
├── diagrams/                 Gantt/flow/PERT charts
├── docs/                     misc reference PDFs
└── archive/                  superseded prototypes/scripts, nothing here is used by the live app
```

```
app/ScreenerProject/
├── main.py                    entrypoint — starts the Tk app + the integration API server
├── api_server.py               local FastAPI: GET /screener, GET /health (§9)
├── core/
│   ├── finviz_api.py           Finviz Elite fetchers, optional, needs FINVIZ_API_KEY
│   ├── finviz_auth.py          optional: auto-fetches FINVIZ_API_KEY via real login, run manually
│   ├── ib_api.py                IB scanner discovery + price/short data (discovery source)
│   ├── schwab_api.py            Schwab Trader API discovery + quote/history/movers (discovery
│   │                            source, scaffolded pending app approval - see §7/§9c)
│   ├── schwab_auth.py            one-time manual OAuth bootstrap for core/schwab_api.py, run manually
│   ├── finnhub_api.py          free real-time price backup, needs FINNHUB_KEY, last-resort only
│   ├── yfinance_news_api.py     free, keyless news fetcher (primary news source)
│   ├── newsapi_news_api.py     optional third-tier news backup, needs NEWSAPI_KEY
│   ├── filters.py               squeeze filter/scoring logic, shared target/stop-loss formula
│   ├── short_interest.py        pure shares_short/float_shares/days-to-cover formulas (§2 of
│   │                            FRESH_START_DATA_AND_SHORT_INTEREST_PLAN.md)
│   ├── provider_utils.py        tiny numeric/date helpers shared across provider modules
│   ├── technical_indicators.py  shared RSI/weekly-volatility math (used by ib_api.py, schwab_api.py)
│   ├── yfinance_float_api.py    shared float/short-interest lookup+cache (ib_api.py, schwab_api.py
│   │                            both lack fundamentals data natively; this is the one shared fallback)
│   ├── mongo_client.py          optional: mirrors results to MongoDB, needs MONGODB_URI (§9a)
│   ├── snapshot_store.py        atomic JSON persistence + schema/freshness health metadata
│   └── sentiment.py             FinBERT headline classifier (positive/neutral/negative)
├── controller/controller.py    glues everything together - configurable provider-priority
│                                dispatch (SCREENER_PROVIDER_PRIORITY, default ib→schwab→finviz)
├── ui/view.py                   Tkinter GUI (Screener / Chart / Breaking News tabs)
├── tests/                       see §"How to reproduce" below
├── .env.example                 copy to .env — every key in it is optional
└── requirements.txt
```

## 3. How to reproduce / run this from scratch

1. `cd app/ScreenerProject && pip install -r requirements.txt`.
2. Copy `.env.example` → `.env`. Every value is optional; leave blank to use free fallbacks.
3. Optional: install IB Gateway, log in, enable API access in its settings (Configure → API →
   Settings). Free or paper accounts both work. Without it, the app falls back to Schwab (if
   configured) or Finviz for discovery only — everything else still works.
4. Optional: once a Schwab Trader API app exists and shows "Ready For Use" on the Dev Portal, set
   `SCHWAB_APP_KEY`/`SCHWAB_APP_SECRET` in `.env`, then run `python core/schwab_auth.py` once to
   complete the OAuth consent flow (see §7/§9c). Skip entirely until the app is approved.
5. Run `python main.py`.
6. Offline tests, no live accounts needed: `python -m pytest tests/` runs all 116 (or run any
   individual file directly, e.g. `python tests/test_filters.py`) - covers filtering, IB/Schwab
   scaffolding, technical indicators, float/short-interest lookups, short-interest formulas,
   controller/snapshot behavior, the shared scoring rubric, news relevance filtering, and
   integration delivery. The Vercel health test is `python ../vercel-api/tests/test_health.py`
   from the active app directory (4 more). `tests/test_sentiment_finbert.py`,
   `tests/test_newsapi_news_sentiment.py`, and `tests/test_yfinance_news_sentiment.py` are
   standalone model-comparison/live-smoke scripts, not part of the pytest suite - run directly
   with `python tests/<name>.py` when needed, not via pytest.
7. To wire in optional free/paid extras, see the matching `.env` key: `FINVIZ_API_KEY`,
   `FINNHUB_KEY`, `NEWSAPI_KEY`, `MONGODB_URI` (cloud sync, see `app/vercel-api/README.md`),
   `SCHWAB_APP_KEY`/`SCHWAB_APP_SECRET`/`SCHWAB_CALLBACK_URL`. Use `SCREENER_PROVIDER_PRIORITY`
   to reorder/restrict which discovery source runs (default `ib,schwab,finviz`).
8. Everything is additive — the app runs end-to-end with zero keys and no IB Gateway at all.

## 4. What currently works

- App launches, all three tabs render.
- Discovery via IB's live scanner (falls back to Finviz if IB isn't connected).
- News/sentiment via free yfinance headlines (falls back to Finviz, then NewsAPI).
- Filter/scoring logic matches the original design: price $2-$20, float <20M, change ≥10%,
  relative volume ≥5, short-float ≥5% → Prime (4/4) or Subprime (3/4).
- Sentiment classifier: FinBERT, fine-tuned on this app's own data, ~72% accuracy.
- Local integration API (`GET /screener`, `GET /health`) and an optional cloud mirror via MongoDB.
- Screener refreshes every 15 seconds.
- IB enrichment targets the same **15-second start-to-start cadence** instead of sleeping 25
  seconds after each completed pass. Cached passes normally fit inside that window; a slow initial
  historical/float cache fill may exceed it, in which case the next pass starts immediately.
- The GUI and Breaking News tabs each have one 15-second timer chain. Duplicate startup timers
  that previously caused overlapping refreshes and redundant snapshot writes were removed.
- **120 offline checks pass** (116 in `app/ScreenerProject/tests/` + 4 in `app/vercel-api/tests/`,
  count re-verified 2026-07-14 - up from the 101 last counted here, as corroboration/scoring/news
  tests were added since) across filtering, IB calculations/config/health-tracking, the Schwab API
  scaffold (fully mocked - no live credentials needed) including the hard-to-borrow signal, shared
  technical-indicator/float-lookup modules, news relevance filtering, short-interest formulas,
  schema output, optional sentiment, atomic persistence, local API behavior, Mongo delivery, and
  cloud health.
- **Full live end-to-end run completed 2026-07-13** (`python main.py`, real IB Gateway connection,
  real Schwab-approved account, real network calls throughout - not just the screener/API layer
  covered above). Found and fixed two additional real bugs beyond the Schwab movers one:
  1. `refresh_news_cache()` treated "a Finviz key is configured" as equivalent to "Finviz is
     working" - the key in `.env` is dead (401 Unauthorized), so news_cache was always empty and
     every row's `sentiment_label` was silently `null`, with no fallback ever firing. Fixed: any
     empty result now falls through to yfinance, then NewsAPI, regardless of why Finviz came back
     empty.
  2. Once headlines started flowing, many were wrong: yfinance's unofficial `.news` endpoint
     returns Yahoo's general "trending on this ticker's page" carousel, not strictly relevant
     single-company news - confirmed live, obscure tickers were getting headlines entirely about
     unrelated companies tagged as their own. Fixed with a whole-word ticker-mention filter
     (title or summary) before accepting a headline; verified live afterward that real sentiment
     now flows only from genuinely relevant headlines.
  Verified live after both fixes: real IB-connected discovery, real scored Prime/Subprime rows,
  real short-interest data, real sentiment correctly attributed, local REST API reachable, zero
  crashes across hundreds of scan cycles.
- **Full-audit live testing session, 2026-07-14** (`python main.py` launched and left running
  unattended overnight, ~6.7 hours, real IB Gateway + real Schwab account). Found and fixed four
  more real bugs, none caught by the existing offline suite because none of them are exercisable
  without actually running the live entrypoint:
  1. **Startup crash under redirected/non-console stdout.** `core/finviz_api.py`'s dead-Finviz-key
     handler (see above) does `print(f"❌ ...")` on the exception path - fine in an interactive
     Windows console (UTF-8 per PEP 528), but the moment stdout isn't an attached console (a log
     file, a process supervisor, or simply how this was launched during testing), Windows falls
     back to the OS locale encoding (cp1252 here), which can't encode the emoji. That `print()`
     itself raised `UnicodeEncodeError`, uncaught, killing `Controller.__init__()` before the
     window ever opened - a hard crash on every single startup in that context, not an edge case.
     ~30 other `print()` calls across `core/`/`controller/`/`ui/` carry the same emoji risk.
     Fixed once at the source in `main.py`: reconfigures `sys.stdout`/`sys.stderr` to UTF-8 with
     `errors="replace"` at startup, neutralizing all of them instead of patching each call site.
  2. **Misleading reconnect-exhausted log line.** `core/ib_api.py::_reconnect_loop()` printed
     "staying on the Finviz fallback for this run" once its 5 attempts were exhausted - stale text
     from before Schwab existed as a provider. `controller.py`'s `_select_provider()` actually
     tries Schwab before Finviz, confirmed live when IB Gateway auto-restarted overnight and the
     app correctly kept serving from Schwab, not Finviz. Log message corrected; also now notes
     that IB never retries again within the same process even after Gateway comes back - a
     restart is required to pick it back up, confirmed live the same night.
  3. **Breaking News tab stuck on a hardcoded placeholder watchlist.** `get_positive_news()`
     unconditionally called `refresh_news_cache(DEFAULT_WATCHLIST)` - GME/AMC/KOSS/PLTR/SOFI -
     regardless of what discovery actually found that cycle, contradicting `DEFAULT_WATCHLIST`'s
     own comment that it's "superseded automatically once discovery returns real tickers." It
     never was: this method never looked at real tickers at all, so the tab stayed pinned to 5
     fixed symbols and looked frozen once those specific 5 ran dry of fresh headlines. Fixed:
     `get_screener_results()` (which runs on its own independent 15s timer and is the only place
     real discovered tickers are known each cycle) now records them on `self._last_watchlist`;
     `get_positive_news()` reuses that instead, falling back to `DEFAULT_WATCHLIST` only before
     the first screener cycle has run.
  4. **Sentiment classification running the model N times sequentially on the Tkinter main
     thread.** `get_screener_results()` called `classify_headlines()` once per ticker - and, for
     Prime tickers specifically, a second time again in a separate loop - each call its own FinBERT
     forward pass, all synchronous on the UI thread. Observed live as the window periodically
     reporting "Not Responding" mid-refresh. Fixed: one batched `classify_headlines()` call across
     every distinct headline the cycle actually needs (transformer inference batches far more
     efficiently than N single-item calls), with results looked up by ticker afterward - also
     eliminates the Prime double-classification outright. Kept single-threaded/synchronous rather
     than moving classification to a background thread: lower-risk fix, no new locking around
     Tkinter widgets to get wrong, and batching should address the actual cost driver directly.
  All four fixed with the offline suite re-run clean afterward (120/120) and the app re-verified
  live after each fix: real scored rows, real IB→Schwab fallback and back, zero crashes/tracebacks
  across the full overnight run and subsequent restarts.

## 5. Known gaps / caveats

- **Target/stop-loss formula is a rough heuristic, not a validated model.** The prior author
  derived it by feeding a small personal spreadsheet into ChatGPT for curve-fitting. Treat the
  numbers as approximate, especially before any downstream consumer relies on them as rigorous.
- **Live IB API price/historical data requires paid Level 1 entitlement.** IBKR's general pricing
  page advertises free non-consolidated Cboe One/IEX data, but its API-specific documentation warns
  that free on-platform data may not be available through the API and says live API data and
  historical bars require paid subscriptions. The current account actually returns delayed/
  unentitled API data. Paid A/B/C data normally requires $500 equity plus the fees. Finviz Elite is
  the zero-new-deposit real-time baseline; see `FRESH_START_DATA_AND_SHORT_INTEREST_PLAN.md`.
- **IB data requires a live, logged-in Gateway/TWS account on the operator's machine.** Operators
  do not need to share credentials because connection settings are per-machine, but the long-term
  account owner and paid-subscription owner still need to be decided. See §9b.
- No retry-forever reconnect watchdog (capped at 5 attempts on purpose) and no incremental UI
  redraws (full redraw every cycle) — both intentional scope cuts, not bugs.

## 6. Data source comparison (decided 2026-07-07; priority order set by advisor 2026-07-13)

Advisor's explicit priority order (2026-07-13 email, with specific links) — this is the standing
order to follow, independent of current code capability: (1) Interactive Brokers — open account
ASAP; (2) TD Ameritrade, via the TTM Squeeze Indicator (now Schwab/thinkorswim — note: TTM Squeeze
is a volatility chart study, not a short-interest data source; the actual data path there is the
Schwab Trader API); (3) shortsqueeze.com; (4) CBOE DataShop. 10-day operational deadline:
2026-07-23. See `RESEARCH_LOG.md` §2 for the full research writeup on each link.
**Minimum bar confirmed 2026-07-13: the final product must ship with both IB and TD
Ameritrade/Schwab implemented — shortsqueeze.com and CBOE remain optional/backup, but IB and
Schwab are both mandatory.**

- **Interactive Brokers** — useful for free scanner discovery, free non-consolidated Cboe One/IEX
  ticks, and broker-specific shortable-share inventory. Shortable shares are a live borrow-
  availability signal, not official short interest. Downside: needs a locally-running, logged-in
  Gateway session tied to one account (see §9b).
- **TD Ameritrade** — retired and replaced by Schwab's Trader API. The advisor has now explicitly
  requested a full Schwab Individual Trader API setup, including authentication and market data.
  This is a required first-class provider, not merely a future supplement. **Hard requirement
  confirmed 2026-07-13: the final delivered product must have both IB and TD Ameritrade/Schwab
  implemented — mandatory, not either/or.** **Code-side scaffold completed 2026-07-13** (see §7/§9c)
  — `core/schwab_api.py`/`core/schwab_auth.py` are fully built and tested against mocked responses;
  what's still pending is the advisor's own Schwab Developer Portal app reaching "Ready For Use" so
  the OAuth bootstrap and real endpoints can be validated live (registration is in progress, see
  `RESEARCH_LOG.md` §2 for the walkthrough).
- **shortsqueeze.com — deferred, cost.** No free tier at all; paid-only, and still only
  20-minute-delayed data even on paid plans. Doesn't solve the real-time problem at any price.
  Not signing up unless the advisor specifically wants to pay for it.
- **CBOE DataShop — deferred, cost.** No free or self-serve tier shown; pricing requires a direct
  sales inquiry and is likely priced for institutions. Not pursuing without a specific price quote
  and a documented reason Finviz/IB/Schwab don't already cover.
- **Finviz** — never actually requested by the advisor. Kept as an optional/opportunistic source
  (used automatically if a real key exists — one now does, see §8a), but the app never depends on it.

## 7. Backlog status

- ~~Required next deliverable (advisor call 2026-07-12, see `RESEARCH_LOG.md` §5): cross-provider
  corroboration~~ — **done 2026-07-13.** See §9d for the shipped design; all 6 open questions in
  `CROSS_PROVIDER_CORROBORATION_PLAN.md` §3 are resolved there.
- ~~Fix the two remaining IB code defects from `FRESH_START_DATA_AND_SHORT_INTEREST_PLAN.md` §4~~
  — done 2026-07-13:
  - **Historical-data hard gate removed.** `core/ib_api.py::_build_row()` previously discarded a
    row entirely if `_get_hist_stats()` failed, before ever checking the live tick or Finnhub. It
    now degrades gracefully via `_hist_stats_or_degraded()`: price/change% still resolve through
    the existing fallback chain, and only RSI/weekly-volatility/relative-volume (which genuinely
    require historical bars) fall back to neutral defaults plus a new `historical_bars_unavailable`
    quality flag. The row is only discarded now if no price/prev_close source exists at all.
  - **Connection is no longer mistaken for usable data.** `ib_api.is_ib_available()` (what
    `controller.py`'s provider-priority dispatch calls, §9c) now factors in enrichment health via
    `_record_enrichment_result()`/`_record_enrichment_exception()`: a session connected but unable
    to enrich any of 3+ consecutive non-empty raw scanner passes reports itself unavailable,
    correctly falling through to Schwab/Finviz instead of getting stuck on a broken-but-connected
    IB session. A genuinely empty *scored* result (zero Prime/Subprime matches) still isn't treated
    as a failure - only zero *enriched rows* from a non-empty raw candidate list is. Failure count
    resets on a fresh (re)connect and on any healthy pass.
  - Tests: 9 new cases in `test_ib_api.py` covering both fixes directly (including an end-to-end
    `_build_row()` test proving a row survives a historical-data failure when a live tick price
    exists, and the previous discard behavior is gone).
- ~~Charles Schwab Trader API integration~~ — **app approved and live-validated 2026-07-13.** App
  reached "Ready For Use" the same day it was created; `core/schwab_auth.py`'s OAuth bootstrap
  completed successfully against the real account. First live test against real endpoints found
  and fixed one real bug: `fetch_movers()`'s live response uses `lastPrice`, not `last` as the
  public OpenAPI spec's schema names it - `run_scan_cycle()`'s $2-$20 price-band filter was
  silently matching zero candidates. `fetch_quotes()`/`fetch_price_history()`'s field assumptions
  were confirmed correct against real responses, no changes needed there. Full pipeline
  (`rank_and_group_stocks_schwab()`) verified end-to-end against live data, producing a real
  scored result. New regression test
  (`test_run_scan_cycle_filters_by_price_band_using_real_lastprice_field`) exercises the actual
  candidate-filtering path with the real field name so this class of bug can't silently
  reintroduce itself. See §9c for the full architecture. Trading/order endpoints remain
  unimplemented because this screener is read-only.
  - **Schwab hard-to-borrow signal — wired in 2026-07-13.** `/quotes`' `reference.isHardToBorrow`/
    `htbQuantity`/`htbRate` are now carried through as `schwab_htb_quantity`/`schwab_htb_rate`/
    `schwab_is_hard_to_borrow`/`schwab_htb_as_of` end-to-end (row dicts → controller.py's row
    shape and schema-v1 API → GUI columns), kept under their own `schwab_htb_*` name rather than
    folded into `ib_shortable_shares` since it's a different provider's inventory figure - same
    "broker inventory, not official short interest" caveat applies. Missing data (e.g. no
    `reference` block) is flagged `schwab_htb_unavailable` rather than fabricated. IB/Finviz rows
    carry the same four keys as `None` so every provider's row shape stays identical. Verified
    live against the real account (AGEN: `htbQuantity` ~597k, `isHardToBorrow: true`).
  - **Still open:** multi-session market-hours freshness/rate-limit observation and the 7-day
    refresh-token renewal behavior haven't been exercised over time yet, only a single live call.
- ~~Short-interest calculation and formula~~ — done 2026-07-13. New pure module
  `core/short_interest.py` implements `calculate_short_float_percent()` (shares_short/float_shares
  * 100), `calculate_days_to_cover()` (FINRA's shares_short/average_daily_volume), and
  `check_short_float_discrepancy()` (flags when a provider-supplied percentage disagrees with the
  local calculation by more than 2 points). Wired into both data paths:
  - **IB/yfinance path** (`core/ib_api.py`): `_fetch_yfinance_float_sync()` now also pulls
    `sharesShort`/`dateShortInterest` from yfinance's `.info` (the actual reported open short
    position and its settlement date, not a proxy), and `_build_row()` prefers the locally
    calculated percentage over yfinance's own `shortPercentOfFloat`, falling back to the provider
    value only when `shares_short` is unavailable for that symbol.
  - **Finviz path** (`core/filters.py`): Finviz's export supplies Short Float% directly but no raw
    shares_short count or average-volume figure this app parses, so `shares_short`/`days_to_cover`
    stay explicitly `None` with a `quality_flags` reason rather than being fabricated.
  - `ib_shortable_shares` (tick 236 broker inventory) is now carried through ranking/GUI/API instead
    of being discarded (closes defect #3 in `FRESH_START_DATA_AND_SHORT_INTEREST_PLAN.md` §4) - kept
    as a clearly separate field from `shares_short`, never substituted for it.
  - New fields threaded end-to-end (IB/Finviz row dicts → `controller.py`'s row shape and
    `get_snapshot()` → schema-v1 API JSON → GUI Treeview columns): `shares_short`, `days_to_cover`,
    `short_interest_as_of`, `short_interest_source`, `float_as_of`, `float_source`,
    `ib_shortable_shares`, `ib_shortable_shares_as_of`, `quality_flags`.
  - Tests: new `tests/test_short_interest.py` (10 pure formula/validation cases), plus updated
    shape/provenance assertions in `test_filters.py`, `test_ib_api.py`, `test_controller_snapshot.py`.
- ~~Thread `short_float_percent` through to the integration API's JSON output~~ — done, no longer
  hardcoded `null` (`controller.py`'s row shape and `get_snapshot()` now carry it end-to-end, and
  the GUI has a matching Short Float column rather than silently receiving an extra row value).
- ~~Rotate/scrub hardcoded API keys~~ — done, moved to `.env`, dead keys archived.
- ~~Consolidate duplicate sentiment code~~ — done, `sentiment-rnd/` archived after confirming
  nothing live referenced it.
- ~~Convert `test_filters.py` to a real offline test~~ — done, 4 tests, no network needed.
- ~~Audible Prime-alert sound~~ — done. Found and fixed a real bug on first live run: it was
  playing once per ticker with a blocking call, freezing the UI for several seconds when many
  tickers qualified at once. Now fires once per cycle, non-blocking.
- ~~Ticker search bar in Breaking News tab~~ — done.
- **Auto-trade execution — confirmed out of scope, staying that way.** The prior author flagged it
  himself as high-risk. Not built, not planned.

## 8. IB real-time data — the actual story, condensed

> **2026-07-12 correction:** IBKR's general pricing page advertises free real-time non-consolidated
> Cboe One/IEX data, but API-specific documentation says free platform data is not necessarily
> available through the API and that live API data/historical bars require paid Level 1
> subscriptions. The user's delayed result confirms the free entitlement is not a usable live API
> path here. The code's historical-data hard gate is still a fallback defect, but fixing it will not
> create entitlement. See `FRESH_START_DATA_AND_SHORT_INTEREST_PLAN.md`.

- IB's scanner + shortable-share data implemented and live-verified 2026-07-08 (`core/ib_api.py`).
  Falls back to Finviz automatically if IB doesn't connect.
- Float/Short-Float showing "N/A" for IB rows — turned out to have a free fix: yfinance's `.info`
  endpoint carries this data. Implemented, IB scoring is back to the full 4-criteria scheme.
- IB's price data showing up delayed reflects missing paid API entitlement on this account. A
  separate code defect makes the outcome worse: `_build_row()` discards a symbol when historical
  bars are unavailable before it reads the live tick or invokes fallbacks. Removing that gate will
  restore alternate-source behavior, but will not make unsubscribed IB API data real-time.
- **Optional paid consolidated quote: $4.50/month total** — NYSE Network A $1.50, Network B
  (NYSE American/ARCA/BATS/IEX/regionals) $1.50, and NASDAQ Network C $1.50. This assumes one
  exchange-qualified non-professional IBKR Pro user consuming the live feed locally. It covers the
  consolidated Level-1 stock quotes and historical bars used by this app. Activating paid market
  data normally also requires $500 in account equity; this is excluded from the baseline plan.
- The quote does **not** include OPRA options, Level-2 depth, OTC, paid IB news, or redistribution.
  The active app uses none of those: news/sentiment/short-float come from its existing external
  fallbacks, and the IB path scans major US stocks plus shortable-shares tick 236. Developers may
  share the code, but the subscribed user's live market data should remain with that user unless a
  different distribution arrangement is approved.
- Finnhub was added as a free real-time backup earlier, then demoted to last-resort-only after its
  free tier hit rate limits under real load and the advisor flagged non-free tiers as costly.
- Basic reconnect handling exists (10s backoff, capped at 5 attempts) — verified live.

## 9. Integration API for other tools/teams

- Local, no-auth REST API (`GET /screener`, `GET /health`) backed by a JSON file the app rewrites
  every refresh cycle — this schema-v1 stub is the deliverable the integration team builds
  against, by decision, not a placeholder waiting on their sign-off.
- Handoff hardening: snapshots are atomically replaced so API readers never see half-written JSON;
  MongoDB delivery runs on a non-blocking latest-wins worker; local/cloud health endpoints report
  readiness and 60-second freshness; rows carry `schema_version: 1`. A fresh empty `[]` is a valid
  no-matches scan, distinguishable from startup/staleness through `/health`.
- **Sentiment fields are optional/replaceable:** the integration team confirmed it is developing
  its own sentiment component. `INCLUDE_SENTIMENT_OUTPUT=false` removes `sentiment_label` and
  `sentiment_confidence` from the local snapshot and therefore from MongoDB/Vercel too, without
  disabling the screener's own FinBERT-powered desktop display.
- **Optional cloud mirror (§9a):** the screener itself can't move to Vercel — it needs a
  persistent local IB Gateway connection, which serverless functions can't provide. Instead, the
  local app optionally mirrors results into MongoDB, and a separate small app in
  `app/vercel-api/` reads from MongoDB and serves the same API publicly. Verified working
  end-to-end against a real MongoDB Atlas cluster. **Decided:** actually running `vercel deploy` is
  not a pending action item — the code/config stub is the deliverable, not a blocked task.
- **Open operations question (§9b):** real-time IB data is tied to whichever live account operates
  Gateway/TWS. Per-machine configuration means credentials never need to be shared, but the advisor
  still needs to decide which single non-professional account owns the $4.50/month subscriptions
  and ongoing operation.
- **Per-machine config, no shared login needed (added 2026-07-11):** `IB_HOST`/`IB_PORT`/
  `IB_CLIENT_ID` in `.env` (see `.env.example`) let anyone point the app at their own locally-running
  Gateway/account without touching source — previously these were hardcoded in `core/ib_api.py`.
  `ib_api.py` loads that file directly, and blank/malformed numeric values fall back safely.
  Every other key (Finviz/Finnhub/NewsAPI/Mongo) was already `.env`-driven. So each team member (or
  the integration team) can run this against their own IB login and their own keys; only the
  account-ownership decision above (§9b) is still an open question, not the wiring.
- **Schwab Trader API scaffold, interchangeable-provider design (§9c, added 2026-07-13):** built
  ahead of the advisor's app approval so it can be slotted in immediately once ready, and so
  either broker can be swapped/reordered without touching code — see `RESEARCH_LOG.md` §2 for why
  this was built proactively during the approval wait.
  - **Provider contract:** `core/schwab_api.py`'s `rank_and_group_stocks_schwab()` returns the
    exact same dict shape as `core/ib_api.py`'s `rank_and_group_stocks_ib()` and
    `core/filters.py`'s `rank_and_group_stocks()` (same keys: `Ticker`, `Price`, `Float`,
    `ShortFloat`, `SharesShort`, `DaysToCover`, `QualityFlags`, etc.). `controller.py` never
    branches on which provider it's calling beyond picking one - every downstream consumer
    (scoring, GUI, schema-v1 API) is identical regardless of source.
  - **Configurable, not hardcoded:** `controller.py`'s `_select_provider()` reads
    `SCREENER_PROVIDER_PRIORITY` from `.env` (comma-separated, default `ib,schwab,finviz`) and
    picks the first available entry each cycle. The integration team can reorder, restrict to one
    provider, or add a provider back without editing `controller.py` at all.
  - **Shared infrastructure, not duplicated:** neither IB nor Schwab natively provide float shares
    or officially reported short interest, and both need the same RSI/weekly-volatility math from
    raw price bars. Rather than each provider reimplementing this, it was extracted into
    `core/technical_indicators.py` (RSI/volatility), `core/yfinance_float_api.py` (the shared
    yfinance-backed float/short-interest lookup, one 24h-TTL cache shared across providers so a
    symbol scanned by both doesn't double-fetch), and `core/provider_utils.py` (small numeric/date
    helpers). `core/ib_api.py` was refactored to import these instead of keeping its own private
    copies - re-exported under its original private names so no existing call site or test needed
    to change.
  - **OAuth/token lifecycle:** `core/schwab_api.py` implements the full `authorization_code` +
    `refresh_token` grant flow confirmed against Schwab's own documentation (2026-07-13): access
    tokens last 30 minutes (auto-refreshed with a 60s buffer), refresh tokens hard-expire after 7
    days with no renewal possible past that - `core/schwab_auth.py` is the one-time/weekly manual
    browser-consent script to run when `health()` reports `needs_reauth`. Tokens are cached in
    `data/schwab_tokens.json` (gitignored), never the app secret itself (stays in `.env`).
  - **Market data:** `fetch_movers()`/`fetch_quotes()`/`fetch_price_history()` map to Schwab's
    `/movers/{symbol_id}`, `/quotes`, `/pricehistory` endpoints (parameters/response fields
    confirmed against Schwab's public market-data OpenAPI spec, 2026-07-13, not guessed). Unlike
    IB's persistent Gateway connection, this is stateless REST - no background thread needed,
    `run_scan_cycle()` runs synchronously once per `controller.py` refresh cycle.
  - **Health/provenance:** `health()` reports `not_configured` / `not_yet_authorized` /
    `needs_reauth` / `ready`; `controller.py.__init__()` prints Schwab's status on every launch so
    setup progress is visible without a separate check. Order/trading endpoints are not
    implemented anywhere in the module - read-only by construction, not by a disabled flag.
  - **Unit-tested and live-validated:** `tests/test_schwab_api.py` (29 cases) mocks every HTTP call
    - OAuth bootstrap/refresh/expiry, all three market-data endpoints, row-building and scoring.
    `tests/test_technical_indicators.py` and `tests/test_yfinance_float_api.py` cover the newly
    shared modules directly. The app reached "Ready For Use" and was live-validated the same day
    (2026-07-13) - one real bug found and fixed (`fetch_movers()`'s `lastPrice` vs. `last` field
    name, see §7). Still open: multi-session market-hours freshness/rate-limit behavior and the
    7-day refresh-token renewal haven't been observed over time yet, only a single live call.

- **Cross-provider corroboration (§9d, shipped 2026-07-13):** the advisor's actual mental model
  (`RESEARCH_LOG.md` §5, transcript reviewed 2026-07-13) is that IB and Schwab agreeing on a signal
  is what makes it trustworthy - not "whichever provider happens to be connected." Full handoff and
  the 6 resolved open design questions are in `CROSS_PROVIDER_CORROBORATION_PLAN.md` §3; summary of
  what shipped:
  - **A graduated score, not a binary match or a gate.** When IB wins the cycle's provider dispatch
    and Schwab is independently available, `core/schwab_api.py`'s new
    `score_tickers_for_corroboration(tickers)` fetches Schwab's own quote/history/float data for
    just the tickers IB already flagged that cycle (never a broad `fetch_movers()` scan - cost
    scales with the handful of flagged tickers, not the market) and recomputes the exact same 0-4
    rubric (price band, change%, relvol, short-float) IB/Schwab already use for their own
    Prime/Subprime tiering, via a newly-shared `core/scoring.py::score_setup()` (also now the single
    source of truth `core/filters.py`, `core/ib_api.py`, and `core/schwab_api.py` all call, replacing
    three copies of the same 4-line block).
  - **Label, never a filter:** `controller.py`'s new `_apply_corroboration()` sets
    `CorroborationScore` (Schwab's recomputed 0-4 score) and `CorroboratedBy` (`["schwab"]` once
    that score is >= 3) on IB's rows - a row is never dropped for lacking corroboration. Both fields
    thread through `classify_batch()`/`get_snapshot()`'s `to_contract()` into the schema-v1 API as
    `corroboration_score`/`corroborated_by`, and into the GUI as two new Treeview columns, inserted
    immediately before `QualityFlags`/`quality_flags` everywhere so that field stays last (preserving
    `ui/view.py`'s existing list-join display logic, generalized to join any list-typed cell, not
    just the last one).
  - **Explicitly excluded:** Finviz never participates (it was never part of the advisor's own
    framing - see §6) and the fields simply stay `None`/`[]` whenever Schwab is unavailable or a
    different provider won the cycle, rather than fabricating a value.
  - **Tests:** `tests/test_scoring.py` (new, boundary cases for `score_setup()`),
    `tests/test_schwab_api.py` (new cases for `score_tickers_for_corroboration()`, including graceful
    omission when a ticker's quote/history is missing or Schwab errors), and
    `tests/test_controller_snapshot.py` (new cases for `_apply_corroboration()`'s gating logic and
    the snapshot contract carrying the two new fields).
  - **Live-verified end-to-end (2026-07-13).** With IB Gateway/TWS running, a live `python main.py`
    run had IB win the cycle and `_apply_corroboration()` correctly queried Schwab for all 20 real
    Prime/Subprime tickers that cycle. Results were genuinely graduated against live data (most
    scored 3/4 and got `corroborated_by: ["schwab"]`; a few scored 1-2 and correctly got
    `corroborated_by: []`), and every ticker still appeared in the output regardless of its score -
    confirming the label-not-gate design holds under real conditions, not just mocked tests. See
    `RESEARCH_LOG.md`'s 2026-07-13 entries for the full verification trail (including the earlier
    partial run before IB Gateway was up).

## 10. Full change history

See `git log` (both this repo and the `app/ScreenerProject` submodule) for the complete,
detailed, commit-by-commit record — every fix, every dead end, every verification step. See
`RESEARCH_LOG.md` §7 for the same history in short, dated, plain-English form. For the receiving
team's exact contract and checklist, see `INTEGRATION_HANDOFF.md`; for the current advisor
presentation, see `ADVISOR_SUMMARY.md`.
