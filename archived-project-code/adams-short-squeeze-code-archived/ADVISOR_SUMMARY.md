# Advisor Meeting Brief — July 12, 2026

> **Updated 2026-07-17** to reflect work completed since 2026-07-16: a third evidence-gathering
> backtest specifically for cross-provider corroboration - your own explicit ask from the
> 2026-07-12 call, which had shipped as a label on every row but was never checked against real
> outcomes until now - plus a per-component Squeeze Score breakdown (so a reader can see which
> factor is driving a number, not just the final composite), small-sample honesty notes on both
> Track Record panels, and a SPY benchmark comparison added to both panels so a hit rate or avg
> return is never read in isolation - each band now also shows how much it beat (or lagged) just
> holding the S&P 500 over the same holding period. See the new bullets below; everything from the
> 2026-07-16 update remains accurate and is kept as-is.

> **Updated 2026-07-16** to reflect work completed since 2026-07-13: a composite Squeeze Score
> (short float + IB borrow cost + days-to-cover), a live IB borrow-cost signal, the TTM Squeeze
> indicator, a new local web UI (desktop app is unchanged and still runs the whole pipeline), a
> timestamp-consistency fix, and two evidence-gathering backtests that check the Squeeze Score and
> the target/stop-loss formula against what prices actually did afterward. See the new sections
> below; everything from the 2026-07-13 update remains accurate and is kept as-is.

> **Updated 2026-07-13** to reflect work completed since the call: Schwab's Trader API is now a
> fully live second provider, the short-interest/days-to-cover formula is implemented, and
> cross-provider corroboration — the trust model the advisor described on the call — is built and
> live-verified with both providers connected simultaneously.

> **Pricing correction:** A $500 deposit is not required if Finviz Elite is accepted as the
> baseline live source. The current IB account returns delayed/unentitled API data, and IBKR's API
> documentation says live API data and historical bars require paid Level 1 subscriptions. If the
> professor requires live data specifically through IB, the normal requirement is $500 equity plus
> applicable fees. The fresh audit, code defects, short-interest formulas, and implementation are in
> `FRESH_START_DATA_AND_SHORT_INTEREST_PLAN.md`.

## 30-second opening

I took the inherited short-squeeze screener from a partially working, Finviz-dependent desktop app
to a system with two independently verified live providers — Interactive Brokers and Schwab's
Trader API — that now corroborate each other's signals before a setup is trusted, matching the
trust model you described on the call ("if TD Ameritrade is telling me... and interactive broker
is telling me... then we know we have the right to invest"). I also implemented the
short-interest/days-to-cover formula, improved measured sentiment accuracy from about 40% to
72.3%, fixed the missing float/short-float path, verified MongoDB Atlas, and hardened the handoff
so stale or malformed data is detectable. Since then I've added a composite Squeeze Score that
combines short float, live IB borrow cost, and days-to-cover into one 0-100 ranking, the TTM
Squeeze volatility-breakout indicator, and a new local web UI that includes a Track Record panel -
I built three evaluators that check, using real subsequent price data, whether the Squeeze Score,
the target/stop-loss formula, and cross-provider corroboration itself actually predicted anything,
rather than asking anyone to trust the formulas on faith - all three now compare against SPY over
the same holding period so a result is never read against nothing, and all three run on an
automatic daily schedule, alongside a watchdog that keeps the screener itself alive. From my side,
the code, 219 passing checks, and handoff package are ready; the
remaining decisions are account ownership, paid IB market data, and whether to pursue the two
deferred paid sources (shortsqueeze.com, CBOE).

## Suggested 5-minute presentation order

1. **Problem (30 seconds):** inherited app depended on unstable Finviz access, had weak sentiment,
   missing short-float values, and no dependable integration handoff.
2. **Engineering result (90 seconds):** IB and Schwab as two independently verified live providers,
   cross-provider corroboration, the short-interest/days-to-cover formula, a composite Squeeze
   Score (with a per-component breakdown), TTM Squeeze, live IB borrow cost, 72.3% sentiment,
   portable account configuration, and 219 passing checks.
3. **Integration result (60 seconds):** schema-v1 `/screener`, truthful `/health`, atomic snapshots,
   non-blocking Mongo delivery, optional sentiment, and the handoff guide.
4. **Web UI + evidence demo (90 seconds):** open `http://127.0.0.1:8000` - sortable Squeeze Score
   table (expand a row to see the score's own per-component breakdown) → Breaking News → Chart tab
   (price + Squeeze Score history side by side for a ticker) → Squeeze Score Track Record and
   Corroboration Track Record panels (real hit-rate/avg-return by band, each also showing return
   relative to SPY over the same holding period, and each stating its own sample size, not a
   claimed number).
5. **Desktop demo (60 seconds):** desktop rows → a corroborated Prime setup (`corroboration_score`,
   `corroborated_by: ["schwab"]`) → `/health` → `/screener` → `INTEGRATION_HANDOFF.md`.
6. **Ask (60 seconds):** decide IB account/subscriptions, cloud owner, sentiment ownership, whether
   to spend on shortsqueeze.com/CBOE, and confirm auto-trading stays out of scope.

## What I inherited

- Desktop Python/Tkinter screener built by William Gray.
- Strong basic idea, but discovery depended heavily on dead/unstable Finviz credentials.
- Placeholder sentiment model measured around 40% accuracy.
- Float and short-float frequently showed `N/A`.
- No stable integration contract, cloud delivery path, health/freshness signal, or reliable offline
  regression suite.

## What I delivered

- **Schwab's Trader API is a fully live second provider.** Full OAuth lifecycle, real-time market
  data, and output that matches IB's exact row shape field-for-field — live-validated against the
  real approved account, not just mocked. See `PROJECT_NOTES.md` §9c.
- **Cross-provider corroboration — your own follow-up ask from the call.** When IB and Schwab are
  both live, Schwab's own data for whichever tickers IB flagged that cycle is independently
  rescored against the same Prime/Subprime rubric. This produces a graduated 0–4 confidence score
  (`corroboration_score`) and a `corroborated_by` list — a trust signal layered on top of the
  existing results, never a filter that hides anything. Live-verified end-to-end with both
  providers connected: most flagged tickers scored 3/4 and were marked confirmed by Schwab, a few
  scored lower and correctly weren't. See `PROJECT_NOTES.md` §9d.
- **Short-interest and days-to-cover formula implemented.** Official FINRA-style calculation
  (shares_short/float_shares, shares_short/average_daily_volume), plus a flag when a provider's own
  reported percentage disagrees with the locally calculated one by more than 2 points. Threaded
  through both the IB and Finviz discovery paths, the API, and the GUI. See `PROJECT_NOTES.md` §7.
- **Two real IB code defects fixed.** A row used to be discarded entirely if historical bars
  failed, even when a live price was available — now only RSI/volatility/relative-volume (the
  fields that genuinely need historical bars) degrade, with a quality flag. Separately, "connected"
  and "producing usable data" were being conflated — a connected-but-stuck IB session now correctly
  falls through to Schwab/Finviz instead of silently returning nothing.
- **Interactive Brokers is the primary scanner, Schwab is the verified second provider.** Finviz
  remains optional; yfinance, Finnhub, and NewsAPI provide fallbacks where appropriate.
- **15-second target cadence.** IB enrichment is start-to-start every 15 seconds after cache warm-up;
  duplicate UI/news timer loops were removed.
- **Sentiment improved from ~40% to 72.3%.** FinBERT was fine-tuned and evaluated on project data.
- **Sentiment is replaceable.** The integration team is building its own model, so
  `INCLUDE_SENTIMENT_OUTPUT=false` removes our two sentiment fields without affecting the screener.
- **Float and short-float now work.** yfinance fills the fundamentals gap in IB and Schwab data, and
  `short_float_percent` now reaches the GUI and API instead of always becoming `null`.
- **Operator configuration is portable.** `IB_HOST`, `IB_PORT`, `IB_CLIENT_ID`, and the Schwab app
  credentials all live in `.env`, so each operator can use their own accounts without editing source
  or sharing credentials.
- **Integration API is handoff-ready.** Local and cloud paths share schema version 1; atomic file
  writes prevent partial JSON; MongoDB delivery is non-blocking and latest-snapshot-wins.
- **Health checks are meaningful.** `/health` distinguishes starting, malformed/unavailable, stale,
  and healthy data. Data older than 60 seconds returns HTTP 503.
- **Cloud architecture is proven.** MongoDB Atlas was verified end-to-end. The Vercel read API is
  implemented and tested offline — deploying it is a decision for whoever owns that account, not a
  pending engineering task.
- **116 offline checks pass**, covering filters, IB/Schwab calculations and configuration,
  corroboration, short-interest, schema output, optional sentiment, atomic snapshots, API behavior,
  Mongo delivery, and cloud health.
- Prime alert, ticker news search, reconnection handling, secrets cleanup, and repository
  organization are also complete.

## Delivered since 2026-07-13

- **Composite Squeeze Score.** A single 0-100 ranking combining short float, live IB borrow cost,
  and days-to-cover into one number, inspired by Tapeboard's published squeeze methodology. It's
  the primary signal in the new web UI's table (sortable, color-graded), rather than asking a
  reader to mentally combine 29 separate columns themselves.
- **TTM Squeeze indicator.** The thinkorswim volatility-breakout study (Bollinger Bands inside
  Keltner Channels) - this was the thing your 2026-07-13 email actually pointed at when it said
  "TD Ameritrade, via the TTM Squeeze Indicator." Implemented as a genuine technical indicator, not
  a short-interest data source (that distinction was flagged back to you at the time).
- **Live IB borrow-cost signal.** Reads IB's public FTP short-borrow-rate feed directly (not the
  TWS socket API) for real borrow fee/rebate rates, feeding both its own column and the Squeeze
  Score above.
- **New local web UI**, a read-only viewer alongside the existing Tkinter desktop app (Tkinter is
  unchanged and still owns the actual scan/refresh pipeline) at `http://127.0.0.1:8000`:
  sortable Squeeze Score table with an expandable detail row for every other field, Breaking News
  with a ticker filter, a Stock Chart tab (5-day price plus, once enough history has accumulated,
  a Squeeze Score history overlay plotted as its own chart rather than a second y-axis, so the two
  differently-scaled measures aren't visually correlated in a way that isn't real), and the Track
  Record panel described below.
- **Two evidence-gathering backtests**, both following the same pattern: log a pick, wait for it to
  age, check what price actually did, and report the aggregate - not a single anecdote.
  - `tests/evaluate_squeeze_score_outcomes.py` checks whether higher Squeeze Score bands (90+,
    70-89, 40-69, 0-39) actually correlate with better subsequent returns, and its results are
    served live in the web UI's **Track Record panel** so this is something you can pull up in a
    meeting, not just terminal output someone has to remember to run and paste in.
  - `tests/evaluate_target_stoploss_outcomes.py` checks the *other* unvalidated formula (the
    inherited target/stop-loss heuristic, still just a curve-fit from a spreadsheet - see "Honest
    limitations" below) by walking each pick's actual daily highs/lows to see whether price
    reached the target level or the stop-loss level first.
  - **Both are new as of today and don't have enough graded picks yet for a statistically
    meaningful conclusion** - see "Honest limitations" below. The infrastructure and live UI
    surface are real and verified; the evidence itself will accumulate over the coming days.
- **Timestamp consistency fix.** The API's per-row `timestamp` field was using local time while
  every other provenance field (`short_interest_as_of`, `float_as_of`, `ib_borrow_rate_as_of`,
  `schwab_htb_as_of`, `/health`'s `last_updated`) used UTC - same instant, but looked like a
  multi-hour discrepancy when compared in the same payload. This is very likely the timestamp
  confusion you flagged directly - normalized everything to UTC. (Also localized to the *viewer's*
  own timezone for on-screen display, and fixed a stale-browser-cache issue that could otherwise
  make a fixed timestamp still look wrong.)
- **A third evidence-gathering backtest, specifically for cross-provider corroboration.** This is
  the one piece of your own explicit ask from the 2026-07-12 call that had never actually been
  checked against real outcomes: corroboration shipped as a label on every row
  (`corroboration_score`, `corroborated_by`), but nobody had verified whether a corroborated pick
  (IB and Schwab agree) actually performs better than one that isn't.
  `tests/evaluate_corroboration_outcomes.py` answers that directly - same pattern as the other two
  backtests, served live in a new **Corroboration Track Record** panel next to the Squeeze Score
  one. Also new as of today; see "Honest limitations."
- **Squeeze Score breakdown.** The composite 0-100 number now comes with its three per-component
  sub-scores (short float / borrow fee / days-to-cover) visible on click-to-expand, so a reader can
  see *what's actually driving* a ticker's score instead of trusting a single opaque number.
- **Sample-size honesty built into the UI itself.** Both Track Record panels now state the total
  graded-pick count and say plainly when it's too few (under 10) to draw a conclusion, rather than
  showing a percentage that looks more authoritative than a 2-pick sample actually is.
- **A SPY benchmark comparison, so a hit rate is never read in isolation.** Both Track Record
  panels previously reported a pick's own return with no reference point - "62% hit rate" invites
  the question "compared to what?" `core/benchmark.py` fetches SPY's actual return over the exact
  same holding period as each graded pick, and both panels now show a "vs SPY" column (the
  average outperformance/underperformance versus just holding the market that same window). The
  same evidence-over-formula backtest pattern used throughout, extended to answer the follow-up
  question a skeptical reader asks next.
- **All three backtests now run on an automatic daily schedule**, along with a separate hourly
  watchdog that keeps the screener itself running (and specifically detects and recovers from an
  IB Gateway disconnection that the app's own capped reconnect logic can't self-heal from) - so
  evidence keeps accumulating toward 2026-07-23 without anyone needing to remember to run anything
  by hand.
- **219 offline checks pass** (up from 116 on 2026-07-13), covering all of the above plus the
  existing coverage.

## What to demonstrate

1. Launch `app/ScreenerProject/main.py` and show the three desktop tabs.
2. Show Prime/Subprime rows, including Float, Short Float, and Days to Cover.
3. Point out a corroborated row: `Corroboration Score` and `Corroborated By` columns, and explain
   that a low/no score never removes a row — it's a confidence signal, not a filter.
4. Explain the 15-second refresh/enrichment target and the mixed freshness of supporting fields.
5. Open `http://127.0.0.1:8000` (the new web UI) and show the sortable Squeeze Score table, a row
   expanded for full field detail, Breaking News, and the Chart tab for a live Prime ticker.
6. Open the **Squeeze Score Track Record** and **Corroboration Track Record** panels and explain
   what they are and aren't: live views of the backtest evaluators' graded results, not a claimed
   accuracy number - each panel states its own total sample size, and says plainly when that's
   still too small to mean anything. Point out the **vs SPY** column specifically: it's the
   pre-emptive answer to "a hit rate compared to what?" - each band's return relative to just
   holding the S&P 500 over the same window, not just the pick's own return in isolation. Be ready
   to say honestly whether either has enough graded picks yet (see "Honest limitations").
7. Open `http://127.0.0.1:8000/health` and show freshness/readiness.
8. Open `http://127.0.0.1:8000/screener` and show `schema_version: 1` and the corroboration fields.
9. Show `INTEGRATION_HANDOFF.md` as the integration team's contract and checklist.
10. Explain that sentiment can be omitted with one `.env` switch because their team has its own.

## Measured and verified results

| Area | Before | Current |
|---|---|---|
| Live data providers | none (Finviz only) | IB and Schwab, both live-validated |
| Cross-provider trust signal | single-provider-wins, no agreement check | graduated 0–4 corroboration score, IB vs. Schwab |
| Short-interest/days-to-cover | not implemented | FINRA-style formula + provider-discrepancy flagging |
| Sentiment accuracy | ~40% | 72.3% |
| Discovery dependency | Finviz-heavy | IB-first; Schwab and free fallbacks |
| Refresh behavior | overlapping timers / slower enrichment | one 15-second target cadence |
| Short float in API | always `null` | numeric when available |
| Integration contract | informal | documented schema v1 |
| Snapshot safety | direct write/read race | atomic replacement |
| Mongo delivery | could block UI | background latest-wins worker |
| Health endpoint | always said `ok` | readiness + 60-second freshness |
| Offline verification | limited | 219 passing checks |
| Ranking signal | 29 flat fields, no single ranking | composite Squeeze Score (0–100), with a per-component breakdown |
| Formula validation | trusted on faith | three live backtests (Squeeze Score, target/stop-loss, corroboration) checking real subsequent price data, each compared against SPY over the same holding period |
| Evidence gathering | manual, if run at all | automatic daily schedule + hourly screener watchdog |
| Timestamp consistency | local time mixed with UTC in the same payload | UTC everywhere, localized for on-screen display |
| User interface | Tkinter desktop only | Tkinter (unchanged) + read-only web UI |

## Decisions needed from the advisor

1. **Whose IB account owns production operation?** Each operator can now configure their own
   account, but a long-term owner is still needed.
2. **Approve real-time exchange subscriptions?** For the confirmed single non-professional IBKR Pro
   user setup, the quote is **$4.50/month total**: Network A (NYSE) $1.50, Network B
   (NYSE American/ARCA/BATS/IEX/regionals) $1.50, and Network C (NASDAQ) $1.50. The account must
   also maintain IB's required equity balance (normally $500; this is funding, not a monthly fee)
   and enable the Market Data API acknowledgement. The code already requests Level-1 live data.
3. **Do you want to spend on shortsqueeze.com or CBOE DataShop?** Per your own priority order
   (2026-07-13 email, 10-day operational deadline of 2026-07-23), these are priorities #3/#4 behind
   IB and Schwab (both now done). Neither has been built: shortsqueeze.com is paid-only and still
   20-minute-delayed even on paid plans; CBOE has no self-serve pricing and requires a direct sales
   inquiry. Not pursuing either without your explicit approval of the spend.
4. **Who deploys and owns MongoDB/Vercel?** Atlas works end-to-end; Vercel's code/config is the
   deliverable, but nobody has deployed it publicly yet — that's an account-ownership decision, not
   a blocked engineering task.
5. **Does the integration team want sentiment fields disabled by default?** Their own component can
   replace ours without changing the rest of the contract.
6. **Confirmed already, restating for the record:** auto-trading remains out of scope (read-only,
   places no orders), and both IB and Schwab are mandatory in the final product, not either/or.

## Honest limitations to state clearly

- A 15-second delivery target does not mean every field is 15-second data: price/IB borrow enrichment
  targets 15 seconds, historical indicators are cached one hour, short-float one day, and news ten
  minutes. Official short interest is not an intraday dataset — it can lag up to a few weeks.
- Cross-provider corroboration is specifically IB vs. Schwab, by design — Finviz never participates,
  since it was never part of your own framing of the trust model. The corroboration score reflects
  that one cycle's data only; it isn't smoothed or tracked over time.
- The target/stop-loss formula is a rough inherited heuristic, not a validated financial model - a
  backtest against it now exists (`tests/evaluate_target_stoploss_outcomes.py`), but see the next
  point.
- **All three backtests (Squeeze Score, target/stop-loss, and corroboration outcomes) are recent
  and do not yet have enough graded picks for a statistically meaningful result** - Squeeze Score
  and target/stop-loss started 2026-07-16, corroboration started 2026-07-17. A pick only gets
  graded once it's at least a day old, so the Track Record panels will likely still say "no graded
  outcomes yet" or show single-digit sample sizes for the next several days. The infrastructure,
  live logging, daily scheduling, and web UI surface are all real and verified end-to-end; the
  evidence itself needs time to accumulate. Both panels state their own sample size and flag when
  it's too small - state this plainly rather than reading an early small-sample number as a
  conclusion either way. The same applies to the "vs SPY" column: it's computed from the same
  graded rows, so it carries the identical small-sample caveat as everything else on the panel.
- The free IB entitlement is non-consolidated Cboe One/IEX data for U.S.-listed symbols; it does
  not equal the consolidated A/B/C tapes or full NBBO.
- The $4.50 quote covers the active app's US-stock Level-1 data only. It does not include options,
  Level-2 depth, OTC stocks, paid IB news, or a separate data-redistribution license; none of those
  are required by the active project. Development can share code, while the live feed remains tied
  to the one subscribed non-professional user.
- The Vercel endpoint is built but not deployed.
- Reconnect attempts are intentionally capped at five; this is a scoped handoff, not a 24/7
  production operations platform.

## Current handoff status

- Code, tests, API contract, examples, and operating notes are complete locally, including Schwab
  and cross-provider corroboration.
- Start with `INTEGRATION_HANDOFF.md` for the receiving team.
- No secrets are committed; the real `.env` must never be shared.
- Remaining work requires external account ownership, a spend decision, or advisor/integration-team
  decisions — not more core implementation from the student side.

## Quick run instructions

1. `cd app/ScreenerProject`
2. `pip install -r requirements.txt`
3. Copy `.env.example` to `.env` and configure the operator's optional keys/account settings.
4. Start IB Gateway/TWS and enable API access if IB discovery is required.
5. If Schwab discovery is desired and tokens aren't already cached, run `core/schwab_auth.py` once
   (or again whenever `health()` reports `needs_reauth`) to complete the one-time OAuth consent.
6. Run `python main.py`.
7. Verify `/health` returns HTTP 200 before consuming `/screener`.
