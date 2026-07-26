# Research Log — IST495 Internship

Academic/internship-facing log: advisor context, goals, meetings, and activity-log tracking.
For code/architecture detail, see **[PROJECT_NOTES.md](PROJECT_NOTES.md)** — that's the
engineering-facing doc, and `git log` has the full step-by-step history of every change.

## 1. Course & advisor context

- Course: IST495 (PSU), independent-study/internship.
- Advisor assigns tasks by email, expects at least one meeting per week.
- Course requires 25+ hours/week (self-tracked) and a weekly Activity Log (DOCX) with specific,
  verifiable entries — general statements don't count, and AI use must be disclosed.
- Prior codebase author: William "Will" Gray. Full handoff notes in `PROJECT_NOTES.md` §1.
- A separate "integration team" is waiting on this project's output — that's the reason for the
  original 10-day deadline.

## 2. Standing goals (from the advisor's original email)

- Get the app running (done — see Kaltura notes below for what it does and why).
- Screener should run close to real-time, ideally ~1 minute per cycle (currently 15s).
- Data source priority he gave: Interactive Brokers first, then TD Ameritrade, shortsqueeze.com,
  CBOE. **Decided:** IB is the primary source; the rest are optional backups.
- Deadline: operational by 2026-07-16, because the integration team is waiting.
- Standing ask, repeated across emails: "bring new sentiment into the mix." **Done** —
  accuracy went 40% → 72.3%, measured and logged (`PROJECT_NOTES.md` §4 and the app's evaluation
  logs).
- Integration-team handoff package: **done locally as of 2026-07-12** — schema-v1 API, optional
  sentiment output, freshness-aware health checks, examples, and receiving-team checklist.
- New required follow-up recorded 2026-07-12: add a defensible short-interest calculation/formula
  and include its definition, source, cadence, limitations, UI/API fields, and validation throughout
  the project. Formula selection is pending a fresh source audit; no proxy will be mislabeled as
  official short interest.
- Advisor requirement clarified 2026-07-12: complete the full replacement for the requested TD
  Ameritrade path using Charles Schwab's Individual Trader API, including developer-app setup,
  OAuth, real-time market data, normalization, validation, and operating documentation. The repo
  currently contains no Schwab implementation. Order placement remains out of scope.
- Fresh-start audit completed 2026-07-12: the baseline does not require a $500 deposit **if Finviz
  Elite supplies live screening data**. IBKR's general page advertises free Cboe One/IEX data, but
  its API documentation says live API data and historical bars require paid Level 1 subscriptions;
  the current account returns delayed/unentitled data. If live data must come through IB, the normal
  requirement is $500 equity plus fees. Full plan: `FRESH_START_DATA_AND_SHORT_INTEREST_PLAN.md`.
- **2026-07-13 — advisor follow-up email, explicit priority order and links (supersedes the "IB
  primary, rest optional" framing above).** Kaamran sent specific links and said the whole thing
  must be operational and bug-free within 10 days (by 2026-07-23) because the integration team is
  waiting. His stated priority order, with the exact links he gave:
  1. **Interactive Brokers** — open an account ASAP.
     [Securities Lending Dashboard](https://www.interactivebrokers.com/en/trading/securities-lending-dashboard.php)
     (Orbisa-powered; free tier = Utilization/Lender Depth/Average Duration, premium tier = Short
     Interest Indicator/On-Loan Quantity; UI-only via Client Portal/TWS, API access unconfirmed) and
     [real-time short interest for the credit market](https://www.interactivebrokers.com/campus/traders-insight/securities/short-selling/real-time-short-interest-data-for-the-credit-market/)
     (this second link is about corporate-bond/credit-market short interest via EquiLend Orbisa, not
     equities).
  2. **TD Ameritrade, via the TTM Squeeze Indicator** — TD Ameritrade is now Schwab; TTM Squeeze is a
     thinkorswim chart study (Bollinger Bands vs. Keltner Channels for volatility breakouts), not a
     short-interest data feed. Action item: open/verify a Schwab account, add the study
     (Studies → Quick Study → John Carter's Studies → TTM_Squeeze), and use Stock Hacker to scan for
     squeeze conditions.
  3. [shortsqueeze.com](https://shortsqueeze.com/) — paid membership, no free tier, 20-minute-delayed
     data, no API found.
  4. [CBOE DataShop — US Equity Short Volume and Trades](https://datashop.cboe.com/us-equity-short-volume-and-trades) —
     nightly/monthly file downloads (not real-time), no self-serve pricing shown, needs a direct
     inquiry.
  This is now the authoritative priority order per the advisor's own instructions, independent of
  what the current codebase can or can't already do.

## 3. Early open questions — all resolved 2026-07-07

- Integration format: keep it universal/stack-agnostic (local REST API + file snapshot). Done.
- Finviz: never actually requested by the advisor — keep it optional, require a free fallback
  regardless. Done (yfinance + NewsAPI fallbacks).
- IB confirmed as the first data source to build. Done.
- Running IB locally (not cloud-hosted) is fine. Confirmed.
- IB and TD Ameritrade/Schwab are complementary, not either/or — both optional beyond IB. Confirmed.

## 4. Kaltura recording notes (reviewed via transcript, 2026-07-07)

- Explains short-squeeze mechanics: shorts get forced to buy back as price rises, which pushes
  the price up further.
- The five screener indicators (float <20M, price $2-$20, change ≥10%, rel-volume ≥5,
  short-float ≥5%) trace back to a day-trading YouTuber (Ross Cameron), not academic research —
  worth knowing when discussing methodology.
- The old Finviz API keys likely died from Finviz's own auto-token-regeneration behavior on
  long-running sessions, not a leak.
- Prior author tried and abandoned building his own live short-interest estimator — ran out of
  time before collecting enough data. Confirms IB's live borrow-fee data is the better approach.
- Target/stop-loss formula in the code was curve-fit by feeding a small personal spreadsheet into
  ChatGPT — not a validated model. Worth flagging as an accuracy caveat, separate from "is it a bug."
- Prior author's own backlog ideas (now implemented): Prime-alert sound, ticker search in news tab.
  He explicitly flagged auto-trade execution as high-risk and did not want it built casually.
- Screener refreshes every 15 seconds in the final shipped version (confirmed from his own code
  walkthrough).

## 5. Meeting log

| Date | Format | Topics | Outcome |
|---|---|---|---|
| 2026-07-09 | Call | Real-time data cost concerns; provided Finviz login; asked to check IB's free real-time entitlement; mentioned TD Ameritrade, MongoDB/Vercel, TradingView as future work; confirmed integration team has their own sentiment tool already. | Built the Finviz auto-login tool; found IB's free tier doesn't cover NYSE/NASDAQ; started MongoDB/Vercel groundwork. |
| 2026-07-10 (prep work) | Live testing | Confirmed IB's non-professional Network A/B/C list price ($4.50/mo total); confirmed TD Ameritrade is dead (Schwab replaced it); surfaced the account-owner question. | Findings and prerequisites carried into the current `ADVISOR_SUMMARY.md`. |
| 2026-07-12 | Advisor-meeting preparation | Final integration hardening, 15-second cadence, optional sentiment handoff, health/freshness semantics, and complete documentation review. | Code-side handoff is complete; remaining items require advisor/integration-team decisions or account-owned deployment. |
| 2026-07-12 | Advisor call (transcript reviewed 2026-07-13) | Confirmed TTM Squeeze's data path is TD Ameritrade/Schwab's API, not the indicator itself. Asked about schema/data granularity (confirmed 15s beats his "minute by minute" ask). Flagged that short-interest data can lag up to a week and that GME's 147% Friday rise was news-driven, not a mechanical squeeze, despite ~8% short float via IB - a methodology caveat, not a bug report. Explicit asks: "fix the interactive broker stuff," "get this calculation done," "begin integrating TD Ameritrade." Described his actual mental model for using the tool: he wants IB and Schwab to **corroborate** a signal before treating it as investable ("if TD Ameritrade is selling me [a signal]... if you are telling me from interactive broker [the same signal]... then we will know we have the right to invest") - a cross-provider confirmation check, not the current single-provider-wins dispatch. | All three explicit asks were already done independently by 2026-07-13 (IB defects fixed, short-interest formula built, Schwab live). Cross-provider corroboration is new work - full plan in `CROSS_PROVIDER_CORROBORATION_PLAN.md`. |

## 6. Weekly Activity Log tracker

Last known status from the project notes; verify the external DOCX before reporting completion.

| Week of | File | Notes |
|---|---|---|
| 2026-07-06 | `Activity-Log_IST495_Week-of-2026-07-06.docx` (in Downloads, not this repo) | Tuesday filled in with AI-use disclosure. Remaining days (2026-07-08 through 2026-07-10) still need entries — this is on the student, not something I can fill in. |

## 7. Change log (short version — see `git log` in both repos for full technical detail)

- **2026-07-07** — Repo reorganized; confirmed IB/TD Ameritrade accounts already exist; evaluated
  data sources and picked IB as primary (§2/§3).
- **2026-07-07** — Confirmed both old Finviz keys are dead. Confirmed Finviz was never actually
  required by the advisor — demoted to optional.
- **2026-07-07** — Reviewed Kaltura recordings, logged findings (§4).
- **2026-07-08** — Built free IB scanner discovery and free yfinance news fallback — app no longer
  needs Finviz to run at all.
- **2026-07-08** — Replaced the placeholder sentiment model with fine-tuned FinBERT. Accuracy
  40% → 72.3% across several rounds of data cleanup, expansion, and training improvements.
- **2026-07-09** — Closed remaining backlog: local integration API, offline tests, Prime-alert
  sound (fixed a real freeze bug found on first live run), news search bar.
- **2026-07-09** — Found the IB Float/Short-Float "N/A" issue had a free fix (yfinance), not a paid
  one — corrected an earlier wrong claim.
- **2026-07-09** — Added Finnhub as a real-time price backup, then found IB's own account already
  had a free real-time entitlement the code wasn't using — fixed, demoted Finnhub to backup-only.
- **2026-07-09** — Advisor call: built the Finviz auto-login tool per his request; started
  MongoDB + Vercel groundwork (screener stays local, only a read-only copy of results goes to the
  cloud, since the screener itself needs a live local IB connection).
- **2026-07-09** — Finviz auto-login fixed and confirmed working with real data, after finding the
  real token format and Finviz's updated URL structure.
- **2026-07-09** — MongoDB confirmed working end-to-end against a real Atlas cluster (found and
  fixed one real bug along the way — a blank env var wasn't falling back to its default).
- **2026-07-10** — Live-tested IB's free real-time entitlement against a real Gateway session:
  confirmed it genuinely doesn't cover NYSE/NASDAQ. For one qualified non-professional IBKR Pro
  user, Network A/B/C cost $1.50 each ($4.50/month total), plus IB's account-equity/API prerequisites.
  Raised the bigger question of long-term account/subscription ownership; later per-machine config
  removed any need to share credentials, but an operating owner is still required.
- **2026-07-11** — Made IB Gateway connection settings portable per operator (`IB_HOST`, `IB_PORT`,
  `IB_CLIENT_ID`) and carried Short Float through the GUI and API contract instead of returning
  `null`.
- **2026-07-12** — Made built-in sentiment output optional because the integration team is building
  its own component; disabling it removes only the two sentiment fields, not the screener/UI.
- **2026-07-12** — Tightened the scan path to a 15-second start-to-start target after cache warm-up
  and removed duplicate Tkinter timer chains that caused redundant refreshes.
- **2026-07-12** — Completed integration handoff hardening: atomic snapshots, non-blocking
  latest-wins Mongo delivery, schema version 1, freshness-aware local/cloud health checks, explicit
  empty-result semantics, example payloads, and an integration-team checklist.
- **2026-07-12** — Verification reached **29 passing offline checks** plus successful Python
  compilation. MongoDB Atlas remains verified; Vercel implementation is ready but not deployed.
- **2026-07-13** — Advisor follow-up email set an explicit, ordered priority list (IB → TD
  Ameritrade/TTM Squeeze → shortsqueeze.com → CBOE) with specific links and a hard 10-day
  operational deadline (2026-07-23). Researched all four links; found the TTM Squeeze indicator is
  a chart study, not a data source, and that the IB credit-market link is about bonds, not equities
  — both flagged back to the advisor. Logged in §2 as the standing priority order. Advisor also
  confirmed both IB and TD Ameritrade/Schwab are mandatory in the final product, not either/or.
- **2026-07-13** — Implemented the short-interest calculation/formula deliverable: new
  `core/short_interest.py` (shares_short/float_shares percentage, days-to-cover, provider-vs-local
  discrepancy flagging), wired through both the IB/yfinance and Finviz discovery paths, the
  controller's row shape and schema-v1 API contract, and the GUI. `ib_shortable_shares` (IB tick
  236) is now preserved end-to-end instead of discarded, kept clearly separate from `shares_short`
  per FINRA's definition. See `PROJECT_NOTES.md` §7 for the full field list and file-level detail.
- **2026-07-13** — While waiting on Schwab's app-approval step (registration submitted same day,
  approval can take up to a few days per Schwab's own docs), scaffolded the entire Schwab Trader
  API integration ahead of time so it can be slotted in the moment the app reaches "Ready For Use":
  `core/schwab_api.py` (full OAuth authorization_code/refresh_token lifecycle, movers/quotes/
  price-history clients against confirmed real endpoints, row building matching the exact same
  provider contract as `core/ib_api.py`/`core/filters.py`) and `core/schwab_auth.py` (one-time/
  weekly manual browser-consent bootstrap script). `controller.py` now dispatches to whichever
  provider is available via a `SCREENER_PROVIDER_PRIORITY` env var (default `ib,schwab,finviz`) so
  the integration team can reorder/restrict providers without touching code - the explicit ask
  behind this scaffolding work. Also extracted RSI/volatility math and the yfinance float/short-
  interest lookup (neither IB nor Schwab natively provide fundamentals) out of `core/ib_api.py`
  into shared modules (`core/technical_indicators.py`, `core/yfinance_float_api.py`,
  `core/provider_utils.py`) so Schwab doesn't duplicate that logic. See `PROJECT_NOTES.md` §9c for
  the full architecture writeup.
- **2026-07-13** — Fixed the two remaining open IB code defects from
  `FRESH_START_DATA_AND_SHORT_INTEREST_PLAN.md` §4 (the third, discarded borrow inventory, was
  already closed by the short-interest work above). `core/ib_api.py::_build_row()` no longer
  discards a row just because historical bars failed - price/change% now resolve through the live
  tick/Finnhub fallback chain regardless, with only the genuinely bar-dependent fields (RSI,
  weekly volatility, relative volume) falling back to neutral defaults plus a quality flag.
  Separately, `is_ib_available()` (what `controller.py`'s provider dispatch calls) now tracks
  enrichment health, not just the raw socket connection - a connected-but-structurally-broken IB
  session (3+ consecutive passes producing zero enriched rows from non-empty scanner candidates)
  correctly falls through to Schwab/Finviz instead of getting stuck. 89 offline tests pass total (9
  new, including an end-to-end proof that a row now survives a historical-data failure with a live
  price).
- **2026-07-13** — Schwab app approved same-day (Individual Developer role, Trader API - Individual
  product access with both Accounts and Trading Production and Market Data Production, app created
  and immediately "Ready For Use" - no multi-day wait this time). Ran `core/schwab_auth.py`'s OAuth
  bootstrap against the real account successfully. First live test against real endpoints found
  and fixed one real bug: `fetch_movers()`'s response uses `lastPrice`, not `last` as the public
  OpenAPI spec's schema names it, so `run_scan_cycle()`'s price-band filter was silently matching
  zero candidates. `fetch_quotes()`/`fetch_price_history()`'s field assumptions were confirmed
  correct against real responses. Verified the full pipeline end-to-end against live data - it
  produced a real scored result (AGEN, Subprime, 77.6% change, 15.4% short float via yfinance,
  correctly held out of Prime by relative volume). Also noticed Schwab's `/quotes` response
  includes a real hard-to-borrow signal (`reference.isHardToBorrow`/`htbQuantity`/`htbRate`)
  comparable to IB's tick 236, not yet wired in. 90 offline tests pass total. See `PROJECT_NOTES.md`
  §7/§9c for full detail.
- **2026-07-13** — shortsqueeze.com and CBOE DataShop (advisor's #3/#4 priorities) formally
  **deferred due to cost**, not just left as unstarted optional backups: neither has a free tier
  (shortsqueeze.com is paid-only and still 20-minute-delayed even paid; CBOE has no self-serve
  pricing at all, requires a direct sales inquiry). Not pursuing either without the advisor
  specifically approving the spend. See `PROJECT_NOTES.md` §6.
- **2026-07-13** — Ran a full live end-to-end test of the whole app (`python main.py` against the
  real IB Gateway connection and the now-approved Schwab account), not just the screener/API
  pieces already validated. Found and fixed two more real bugs: (1) `refresh_news_cache()` never
  fell back off a configured-but-dead Finviz key (401 Unauthorized), so Breaking News/sentiment
  were silently empty/null the entire time; (2) once news started flowing, yfinance's unofficial
  `.news` endpoint was returning generic "trending" stories unrelated to the actual ticker, so
  sentiment was being computed from the wrong text entirely. Both fixed and verified against real
  live data afterward - confirmed real, correctly-attributed sentiment now flows end-to-end. 98
  offline tests pass total. See `PROJECT_NOTES.md` §4 for full detail.
- **2026-07-13** — Implemented cross-provider corroboration (the advisor's own required next
  deliverable from the 2026-07-12 call, §5 above). All 6 open design questions in
  `CROSS_PROVIDER_CORROBORATION_PLAN.md` §3 resolved (three via direct check-in with the advisor's
  stand-in on this session, three by adopting the handoff doc's own reasoned defaults): a graduated
  0-4 corroboration score (not a binary tier-match) recomputed against Schwab's own data for
  whichever tickers IB flagged that cycle, added as new `corroboration_score`/`corroborated_by`
  fields (never a filter - IB's rows are never dropped for lacking corroboration), Finviz excluded
  entirely, and no broad Schwab market scan added (cost scales with the handful of IB-flagged
  tickers only). Extracted the Prime/Subprime scoring rubric - previously duplicated three times
  across `core/filters.py`, `core/ib_api.py`, `core/schwab_api.py` - into a single shared
  `core/scoring.py::score_setup()` that both the existing tiering logic and the new corroboration
  check now call. See `PROJECT_NOTES.md` §9d for the full shipped design. 116 offline tests pass
  total across the project's mocked/pure-function suite (15 new: `tests/test_scoring.py` plus new
  cases in `tests/test_schwab_api.py` and `tests/test_controller_snapshot.py`).
  **Live verification is partial, not complete:** ran the full app live (`python main.py`) with the
  real, approved Schwab account; IB Gateway/TWS was not running on this machine at the time (no
  listener on 7496/7497/4001/4002), so IB fell through to unavailable and Schwab won the cycle as
  designed - confirmed `corroboration_score`/`corroborated_by` correctly stay `None`/`[]` in that
  path, never fabricated. Separately called `schwab_api.score_tickers_for_corroboration(["AGEN"])`
  directly against the real live Schwab API (outside the running app) and got back a real score
  (3/4) from genuine quote/history/float data, confirming the new Schwab-side logic itself works
  against production endpoints. **Not yet verified:** the actual "IB wins the cycle and Schwab
  independently corroborates it" path end-to-end, since that requires IB Gateway/TWS running live
  at the same time - still outstanding, needs a follow-up live run once IB Gateway is up.
- **2026-07-13** — Completed live verification of cross-provider corroboration with IB Gateway/TWS
  now up (confirmed listening on port 4001). Ran `python main.py` live end-to-end: IB won the
  cycle's provider dispatch as expected (`source: "ib"`), and `_apply_corroboration()` correctly
  fired the new Schwab per-ticker check for all 20 real Prime/Subprime tickers IB flagged that
  cycle. Observed genuinely graduated results, not a binary pass/fail, exactly per the resolved
  design: most tickers scored 3/4 against Schwab's independently-fetched data and got
  `corroborated_by: ["schwab"]`, while a few (BRAI, CAST, CPIX scored 2; AMWL scored 1) correctly
  got `corroborated_by: []` while still remaining in the results - proving the label-not-gate design
  actually holds against live data (nothing was dropped for low/no corroboration). This closes the
  one remaining verification gap noted above; the feature is now fully live-validated end-to-end.
