# Source Traceability Index

## Advisor meetings (`00_source_material/advisor_meetings.txt`)

Key sections:

- **2026-07-05 ownership/project terms**
  - Shared educational ownership
  - Reproducibility requirement
  - Existing code passed across students
- **2026-07-05 project orientation**
  - Short squeeze as first module
  - Future broader tabs
  - IBKR and Schwab account requirements
- **2026-07-09**
  - Finviz token refresh with cURL Impersonate
  - Finnhub/Yahoo delay concern
  - IBKR market-data subscription
  - IBKR + Schwab integration
  - MongoDB and deployment
- **2026-07-12**
  - TTM Squeeze requested
  - GMM example
  - Multi-source confirmation
- **2026-07-16**
  - Delayed official short interest rejected as live signal
  - Minute-by-minute estimate requested
  - Timestamp, timezone, `None`, and chart issues
  - TTM + IBKR combination
- **2026-07-17**
  - KLOS, BIYA, LBGJ review
  - Neutral news and low short interest
  - Zero borrow fee contradiction
  - Add sortable TTM
  - Revisit Prime/Subprime formula
  - Need earlier detection

## Original coder demos (`00_source_material/original_coder_demo_transcripts.txt`)

Key topics:

- Short-selling and short-squeeze explanation
- Ross Cameron-derived heuristic criteria
- Float <20M
- RVOL >5
- Gain >=10%
- Price $2–$20
- Positive news
- Short float >=5%
- Prime/Subprime logic
- Finviz scraping/API and token limitations
- Random-forest sentiment model
- ~800 manually labeled headlines
- 0.70 positive-alert and 0.60 Breaking News thresholds
- 10–15 second refresh
- Fixed and later formula-based targets/stops
- Data-collection attempts for real-time short-interest estimation
- Explicit acknowledgement that live estimator was not completed
- Proposed future alerts and automated trading

## Advisor emails (`00_source_material/advisor_email_log.txt`)

Key items:

- 2026-07-06 immediate handoff and near-real-time goal
- 2026-07-06 preferred data/source options and deadline
- 2026-07-17 TTM status request
- 2026-07-17 question about TD/Schwab developer access
- Adam’s clarification that TTM was locally calculated from regular OHLC using the standard Bollinger/Keltner formulation
