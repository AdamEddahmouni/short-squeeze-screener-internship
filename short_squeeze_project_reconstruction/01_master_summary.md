# Short-Squeeze Project Reconstruction — Master Summary

## Document purpose

This package organizes and synthesizes:

1. Advisor meeting transcripts
2. Original coder demonstration transcripts
3. Advisor email logs
4. Adam’s written clarification regarding TTM Squeeze

The aim is to reconstruct what the project was supposed to do, what the inherited system actually did, where the concepts or implementations diverged, and what the rebuilt system must preserve, revise, validate, or reject.

## Source key

- **AM** — `00_source_material/advisor_meetings.txt`
- **DT** — `00_source_material/original_coder_demo_transcripts.txt`
- **EL** — `00_source_material/advisor_email_log.txt`

---

# 1. Executive summary

The inherited application is best understood as a **low-float momentum screener with a short-float filter and experimental headline sentiment**, not a validated real-time short-squeeze detector.

Its original Prime/Subprime classifications were based mainly on:

- Float below 20 million shares
- Relative volume above 5
- Daily gain of at least 10%
- Price between $2 and $20
- Short float of at least 5%
- Positive news as an intended criterion, although sentiment was not reliably integrated into the main screener

The system used Finviz data, refreshed approximately every 10–15 seconds, and classified stocks as Prime when they met all scored numerical criteria and Subprime when they missed one. It did **not** possess a validated real-time short-interest formula. Its original coder explicitly stated that this remained unfinished.

During Adam’s handoff period, the project’s objective expanded. The advisor wanted the system to:

- Operate in real time or approximately once per minute
- Use Interactive Brokers securities-lending information
- Add TTM Squeeze
- Integrate Charles Schwab/TD Ameritrade data
- Compare multiple independent sources
- Restore or replace news sentiment
- Identify opportunities early enough to support actionable entries
- Become reproducible, modular, deployable, and suitable for integration into a broader trading platform

The advisor later observed that the inherited Prime/Subprime results did not correspond well with real market behavior. Examples included:

- Prime classifications despite neutral news
- Prime classifications with zero or missing IBKR borrow fees
- Stocks gaining only about 13% being treated similarly to stocks undergoing much larger moves
- Low-short-interest movers appearing despite the project’s stated squeeze focus
- TTM results missing from the table
- stale or confusing “as of” timestamps
- chart or API fields returning `None`

The largest finding is that three different concepts were repeatedly blended together:

1. **Published short interest** — a delayed position snapshot
2. **Securities-lending pressure** — borrow fees, availability, utilization, and changes
3. **TTM Squeeze** — volatility compression derived from Bollinger Bands and Keltner Channels

These are not interchangeable. TTM Squeeze does not measure short interest or short covering. Borrow pressure does not equal official short interest. The rebuilt system must preserve them as separate dimensions.

---

# 2. Original inherited system

## 2.1 Intended market thesis

The original coder’s research drew heavily from low-float momentum-trading material associated with Ross Cameron. The premise was that a stock was more likely to produce a short-squeeze-style move when it had:

- A low float
- Highly abnormal volume
- Strong positive price movement
- A lower share price
- Positive news
- Some minimum level of short float

This is a plausible **candidate-discovery heuristic**, but it is not by itself proof that shorts are covering or that a squeeze is occurring.

## 2.2 Original screening criteria

| Criterion | Original threshold | Role |
|---|---:|---|
| Float | Below 20 million | Limited supply / volatility potential |
| Relative volume | Above 5 | Unusual participation |
| Daily price change | At least +10% | Positive momentum |
| Share price | $2–$20 | Practical low-priced trading universe |
| News catalyst | Positive | Intended explanation for demand |
| Short float | At least 5% | Hidden minimum filter |

The screener prefiltered float and price through Finviz, then scored the remaining numerical conditions. In the demonstrated implementation:

- **Prime Setup** meant all scored criteria passed.
- **Subprime Setup** meant one scored criterion failed.
- Positive news was conceptually important but was not consistently included in the main table.
- Borrow fee, borrow availability, TTM Squeeze, live order flow, spread, and halt risk were not part of the inherited Prime/Subprime formula.

## 2.3 Original data sources and cadence

- Finviz screener data was the primary screener source.
- Finviz news or an API was used for headlines.
- Yahoo Finance was used for embedded charts.
- The interface refreshed approximately every 10–15 seconds.
- Faster polling caused rate-limit or token problems.
- Finviz token regeneration could stop the application and require manual repair.
- An automatic token-retrieval method using cURL Impersonate was later proposed.

A fast refresh interval does not guarantee fresh underlying data. Source timestamps and data entitlement must be tracked independently of polling frequency.

## 2.4 Original news classifier

The inherited sentiment system used:

- A random forest classifier
- Slightly more than 800 manually labeled headlines
- Labels of positive, neutral, or negative
- Confidence scores
- Five recent ticker headlines for ticker-specific analysis
- A 0.70 confidence threshold for positive alerts
- A 0.60 confidence threshold for the Breaking News panel

Strengths:

- Duplicate prevention was attempted.
- URLs, timestamps, and ticker associations were retained.
- The model could be saved and reloaded.
- The system separated newly detected articles to avoid repeated alerts.

Weaknesses:

- Labels were based on subjective headline interpretation.
- No train/test methodology or out-of-sample performance was reported.
- No precision, recall, confusion matrix, calibration, or temporal validation was described.
- Headline tone was treated as a substitute for financial event interpretation.
- Materially dilutive announcements could be linguistically positive.
- The model was sometimes retrained after dataset changes without documented versioning.
- The main screener removed or disabled sentiment because per-ticker API calls caused reliability and performance problems.

## 2.5 Original target and stop methodology

The original concept used a fixed 8% profit target and 8% stop.

A later version used formulas involving:

- Weekly volatility
- RSI
- Analysis of a collected spreadsheet
- ChatGPT Advanced Data Analysis

However, the demonstrations did not provide:

- Exact final formulas
- Training/test separation
- Sample size adequacy
- Slippage assumptions
- Outcome definitions
- Comparative baselines
- Evidence that the formulas improved results

These formulas must be recovered from code and revalidated before reuse.

## 2.6 Unfinished real-time short-interest work

The original coder attempted to collect data for a live short-interest estimator but explicitly concluded that:

- Official short interest was delayed.
- The first dataset contained only about 10 largely irrelevant large-cap stocks.
- A later API version expanded collection to roughly 80 stocks.
- There were not enough reporting cycles or observations.
- At least another month of data collection was believed necessary.
- No reliable formula was completed.

Any inherited “real-time short interest” value must therefore be treated as unvalidated unless Adam’s later code introduced a new, documented method.

---

# 3. Advisor requirements and project evolution

## 3.1 Core educational and ownership terms

The advisor described the project as shared educational work:

- Work may be retained and distributed to future students.
- Adam may continue using the work and knowledge.
- The project is not exclusive or confidential.
- Results must be verifiable and reproducible by another person.
- Code and documentation should support future handoff.
- The work may be described on a résumé and verified by the advisor.

These conditions make documentation, reproducibility, and traceability formal project requirements rather than optional improvements.

## 3.2 Initial handoff requirements

The first explicit handoff instructions were:

- Watch the two original demonstrations.
- Get the attached code running.
- Build a real-time screener, possibly updating as quickly as once per minute.
- Bring new sentiment into the system.
- Make the system operational and bug-free within approximately ten days.
- Prepare it for integration by a higher-level team.

## 3.3 Requested data sources

The advisor named:

1. Interactive Brokers
2. TD Ameritrade / Charles Schwab
3. ShortSqueeze.com
4. Cboe short-volume products
5. Finviz
6. TradingView as a later screener
7. Yahoo Finance and Finnhub as less desirable delayed sources

Interactive Brokers was expected to provide:

- Shares available to borrow
- Borrowing cost or fee
- Securities-lending information
- Near-real-time market data when properly entitled

Schwab/TD Ameritrade was expected to provide:

- Account/API integration
- Market data
- A TTM Squeeze capability or the inputs needed to calculate it

Finviz was expected to provide:

- Fast screener data
- Candidate discovery
- News
- Token-based access

The advisor also wanted multiple sources compared so that overlapping signals could increase confidence.

## 3.4 Infrastructure requirements

- MongoDB compatibility with the integration team
- Local operation initially
- Potential Vercel or Railway deployment
- Modular components suitable for integration
- Frequent advisor demonstrations
- Eventually one broader multi-tab platform containing Short Squeeze, Long-Term Investment, CVD, Level 2, Options, and Futures

The present reconstruction is focused on the short-squeeze component, but its architecture should not prevent later integration.

## 3.5 Later corrective requirements

As the project progressed, the advisor requested:

- Correct the IBKR API integration.
- Integrate Schwab.
- Add TTM Squeeze to the table.
- Make TTM sortable.
- Combine TTM with IBKR-derived lending pressure.
- Calculate or estimate squeeze conditions minute by minute.
- Correct timestamp and timezone issues.
- Resolve `None` or unavailable fields.
- Revisit Prime/Subprime criteria.
- Compare outputs with real observed market movers.
- Determine why zero borrow fees could still yield Prime classifications.
- Identify candidates earlier rather than after major price expansion.

---

# 4. Conceptual findings

## 4.1 Published short interest is not real time

Published short interest is a delayed snapshot of open short positions. It can be useful for structural context, but it cannot confirm minute-by-minute covering.

It should be stored with:

- Observation date
- Publication date
- Age
- Source
- Float methodology
- Confidence

It must never be displayed as current without a visible “as of” date.

## 4.2 IBKR lending pressure is not official short interest

IBKR borrow fee and shares available can provide timely evidence of stress in one broker’s securities-lending inventory. They may help estimate crowding or borrow scarcity.

They do not directly reveal:

- Total market-wide short positions
- Exact real-time short interest
- Exact covering volume
- Other brokers’ inventories
- Private margin pressure

The rebuilt system should call this **borrow pressure**, **lending stress**, or **shortability pressure**, not real-time short interest.

## 4.3 TTM Squeeze is volatility compression, not a short-squeeze detector

TTM Squeeze generally compares Bollinger Bands with Keltner Channels.

When Bollinger Bands sit inside Keltner Channels, recent volatility is compressed. A momentum companion may suggest directional bias.

It does not use:

- Short interest
- Borrow fees
- Shares available
- Short-sale volume
- Covering data

It may help identify a stock that is “coiled,” but it cannot independently establish that a short squeeze is developing.

## 4.4 Price increase does not identify the cause

A stock can rise 100% because of:

- A genuine short squeeze
- News-driven repricing
- Low-float momentum
- A pump
- A merger
- An offering-related anomaly
- Options hedging
- A halt cascade
- Thin liquidity

GMM’s approximately 147% rise was specifically discussed as likely news-driven rather than a short squeeze, despite the dramatic percentage move.

The system must separate:

- **What happened to price**
- **What catalyst occurred**
- **Whether structural short pressure existed**
- **Whether live behavior was squeeze-like**

## 4.5 The original Prime/Subprime logic is under-specified

The original classification uses equal pass/fail points for variables that do not have equal meaning.

Examples:

- A $19 stock and a $2.10 stock both pass price.
- A 5.1 short-float value and 40% short float both pass.
- RVOL 5.1 and RVOL 50 both pass.
- A 10.1% gain and a 150% gain both pass.
- Missing borrow data has no defined penalty.
- News was intended but not reliably included.

This binary scoring loses magnitude, uncertainty, source quality, and interaction effects.

## 4.6 “Catch it early” conflicts with some original filters

Requiring the stock to already be up at least 10%, or judging quality by whether it later gains 80–300%, risks detecting moves after they are already underway.

The rebuild needs distinct states:

- Structural candidate
- Pre-activation
- Activation
- Entry window
- Expansion
- Overextended
- Climax/failure

A move’s eventual maximum gain cannot be used as a real-time entry input.

## 4.7 News sentiment should become catalyst intelligence

The key question is not whether a headline sounds positive. The system should determine:

- Event type
- Source reliability
- Novelty
- Materiality
- Direction
- Dilution impact
- Timing
- Whether the event is already priced in
- Confidence and unresolved ambiguity

A deterministic event taxonomy should control trade eligibility. An LLM or classifier can assist extraction, but it should not directly authorize a trade.

---

# 5. Known implementation and data-quality problems

## Data problems

- Possible delayed or stale data presented as current
- Incorrect or confusing timestamps
- Unclear timezone
- Official short interest displayed without sufficient age emphasis
- IBKR borrow fee shown as zero or unavailable
- Missing values represented as zero, `None`, or not applicable without a consistent distinction
- Potential mixing of feeds with different latencies and definitions
- Finviz token expiration/regeneration
- API rate limits
- Yahoo Finance chart cleanup issues

## Strategy problems

- Prime/Subprime criteria were inherited rather than validated.
- Borrow pressure was absent from the original classification.
- TTM was missing from the main table.
- News was intended but inconsistently integrated.
- The system did not distinguish a news-driven mover from a short squeeze.
- No demonstrated exit-state model existed.
- Entry was effectively “when first flagged.”
- Target/stop formulas lacked documented validation.
- No replay-based evaluation was described.
- No realistic slippage, spread, halt, or partial-fill model was described.

## Interface problems

- Important evidence was omitted from the main table.
- Users had to open stocks individually for some values.
- `None` values appeared without clear explanation.
- Time and “as of” fields were confusing.
- Prime/Subprime labels implied confidence unsupported by evidence.
- Neutral news and zero borrow fees could coexist with Prime labels.
- No visible source-provenance or data-health indicators were described.

---

# 6. Contradictions and ambiguities requiring resolution

## C1 — “IBKR is free” versus paid data

The advisor described IBKR/account access as free but separately acknowledged that market-data subscriptions may be required and offered to reimburse one month.

Resolution needed:

- Record exact account type.
- Record exact market-data subscriptions.
- Distinguish free account access from paid data entitlements.
- Document whether each field is live, delayed, snapshot, or unavailable.

## C2 — TTM from Schwab versus locally calculated TTM

The advisor referred to TTM Squeeze as available through TD Ameritrade/Schwab. Adam clarified that the implementation calculated the standard formula locally from IBKR OHLC data and did not retrieve a proprietary Schwab value.

Resolution:

- Preserve the local standard implementation.
- Name it accurately.
- Record parameters and timeframe.
- Do not claim parity with proprietary thinkorswim output until tested.
- Compare local calculations against thinkorswim samples if access is available.

## C3 — News required versus removed

Positive news was part of the original trading thesis, but the inherited main screener removed sentiment due API and performance issues.

Resolution:

- News must be an asynchronous event stream, not one API request per ticker per refresh.
- Cache and deduplicate articles centrally.
- Classify event type once.
- Join results to tickers.

## C4 — Prime classification versus borrow data

The original Prime calculation did not include borrow fee. Later, the advisor expected borrow fee to be central and questioned Prime results with zero fee.

Resolution:

- Retire the old Prime meaning.
- Create separate structural, borrow-pressure, catalyst, activation, and trade-quality scores.
- Missing borrow data must be `UNKNOWN`, not zero.

## C5 — Short-squeeze estimation versus exact short interest

The advisor sometimes described the desired output as a minute-by-minute short-interest figure, while the cited inputs concern borrow conditions or technical compression.

Resolution:

- Do not fabricate a real-time short-interest percentage.
- Produce a transparent probabilistic or ranked **squeeze-potential estimate**.
- Show contributing evidence and uncertainty.

## C6 — 10% threshold versus dramatic squeeze magnitude

The inherited candidate threshold was +10%. The advisor later contrasted a 13% move with 80–300% squeeze outcomes.

Resolution:

- Use +10% only as one possible activation threshold if validated.
- Do not define a squeeze by eventual return.
- Report move stage and remaining risk/reward separately.

---

# 7. What should be preserved

## Likely reusable after audit

- Finviz candidate-universe retrieval, especially if Elite access is confirmed
- Finviz token-refresh work, subject to licensing and account rules
- Data normalization helpers
- Duplicate-news handling
- Basic ticker/news association
- Saved-model loading infrastructure
- GUI sorting/table patterns
- Prime-event logging pattern
- IBKR authentication and data adapters
- Standard TTM Squeeze calculation
- MongoDB connection setup
- Deployment scaffolding
- Original demonstrations as behavioral documentation

## Preserve only as historical reference

- Prime/Subprime scoring thresholds
- Random-forest sentiment model
- 0.60/0.70 headline-confidence thresholds
- Fixed 8% target/stop
- RSI/weekly-volatility target formulas
- “Squeeze occurred” N/S/M/L labels
- Any field labeled “real-time short interest”
- Any missing-value behavior that substitutes zero
- Any direct use of eventual price gain as a real-time classifier

---

# 8. Recommended rebuilt model

Use five independent dimensions.

## 8.1 Structural squeeze potential

Slow-moving context:

- Published short interest percentage
- Days to cover
- Float and float confidence
- Insider/institutional constraints where relevant
- Dilution and offering risk
- Historical volatility
- Listing and corporate-action status

## 8.2 Borrow pressure

Near-real-time securities-lending context:

- IBKR borrow fee
- Change in borrow fee
- Shares available
- Change in shares available
- Number of lenders, if available
- Hard-to-borrow status
- Data age and source coverage

## 8.3 Volatility setup

Technical preparation, including:

- TTM Squeeze state
- Squeeze duration
- Momentum companion
- ATR compression
- Bollinger bandwidth
- Keltner relationship
- Range contraction

## 8.4 Catalyst intelligence

Event-level analysis:

- Event type
- Primary source
- Publication time
- Novelty
- Materiality
- Direction
- Dilution impact
- Verification status
- Confidence

## 8.5 Live activation and trade quality

Real-time market behavior:

- Time-adjusted RVOL
- Price velocity and acceleration
- VWAP control
- Breakout acceptance
- Pullback quality
- Spread
- Trade and quote imbalance, when available
- Relative strength
- Halt/LULD risk
- Distance to invalidation
- Remaining reward/risk
- Overextension

No single dimension should independently create a “buy” signal.

---

# 9. Required state machine

1. **Discovered** — passes broad universe criteria.
2. **Candidate** — structural or borrow evidence is meaningful.
3. **Coiled** — volatility compression is present.
4. **Armed** — verified catalyst or strong abnormal participation appears.
5. **Entry Window** — live breakout/pullback and trade-quality conditions pass.
6. **Expansion** — momentum remains active; no new entry chase.
7. **Climax Risk** — parabolic acceleration, spread expansion, halt risk, or divergence.
8. **Invalidated** — structure fails or contradictory information appears.
9. **Closed** — hypothetical or paper position is complete.

The application should state why each transition occurred.

---

# 10. Validation requirements

Before live use, the rebuilt system needs:

- Raw event storage
- Exact source timestamps
- Receive timestamps
- Data-health flags
- Source provenance for every field
- Historical replay using the same production code
- Explicit outcome labels
- Walk-forward testing
- No look-ahead data
- Spread and slippage
- Halt behavior
- Partial and missed fills
- Maximum favorable excursion
- Maximum adverse excursion
- Performance by catalyst, float, time, and market regime
- Comparison against simple baselines
- Calibration of alert confidence
- False-positive review
- Human-readable evidence packages for every alert

Suggested baselines:

1. Original Prime/Subprime rules
2. Price + RVOL only
3. Structural short data only
4. TTM Squeeze only
5. Borrow pressure only
6. Combined model

The combined system should not be accepted unless it improves on simpler baselines out of sample.

---

# 11. Immediate next actions

## Evidence and code audit

1. Preserve the exact original handoff repository.
2. Preserve Adam’s archived versions separately.
3. Export Git history where available.
4. Remove or rotate active credentials.
5. Identify every executable entry point.
6. Map every GUI field to code and source.
7. Recover exact target/stop formulas.
8. Recover exact TTM parameters.
9. Identify how IBKR fields are requested and interpreted.
10. Confirm whether Finviz Elite is available and what access method is authorized.

## Data validation

1. Log Finviz, IBKR, and Schwab timestamps side by side.
2. Record data entitlement and delay status.
3. Distinguish zero from missing.
4. Normalize timezones to UTC internally and exchange-local time in the GUI.
5. Compare local TTM against thinkorswim examples.
6. Test IBKR borrow data on known hard-to-borrow and easy-to-borrow stocks.
7. Create an “as of” age badge for every slow field.

## Strategy reconstruction

1. Reimplement the original screener exactly as a baseline.
2. Do not modify it while establishing baseline results.
3. Build the new multi-dimensional scorer separately.
4. Replay both systems over identical sessions.
5. Document every change and result.

---

# 12. Bottom-line conclusion

The inherited work is valuable as:

- A prototype
- A candidate-universe screener
- A demonstration of the advisor’s intended direction
- A source of reusable adapters and interface concepts
- A baseline against which to test a better system

It is not yet evidence of a reliable short-squeeze trading strategy.

The project should be restarted at the architecture and validation level, while preserving the old code as a baseline. The rebuild must avoid claiming that any one of the following is a real-time short-interest measurement:

- TTM Squeeze
- Borrow fee
- Shares available
- Short-sale volume
- Price momentum

The defensible product is a **real-time, source-transparent short-squeeze potential and activation scanner** with explicit uncertainty, replayable evidence, and risk-managed entry/exit windows.
