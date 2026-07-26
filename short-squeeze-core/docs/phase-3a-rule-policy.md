# Phase 3A Rule Policy

Policy `phase_3a_transparent_candidate_policy.v1` contains 25 independent rules. It has no
weights, category importance, score, rank, label, or recommendation. Each threshold is a
provisional research parameter stored in the policy JSON, never hidden in evaluator code.

| Category | Rule IDs | Requirement |
|---|---|---|
| Momentum discovery | `PRICE_RANGE` | completed-bar close from 2 through 20 |
| | `PERCENTAGE_CHANGE_MINIMUM` | Phase 2A/2B percentage return at least 10 percent |
| | `RELATIVE_VOLUME_MINIMUM` | Phase 2B relative volume at least 5 ratio |
| | `FLOAT_MAXIMUM` | snapshot float no more than 20,000,000 shares |
| | `MARKET_DATA_AVAILABLE`, `COMPLETED_BAR_AVAILABLE` | market bar exists; completed bar exists |
| Short-pressure confirmation | `PUBLISHED_SHORT_INTEREST_AVAILABLE` | point-in-time published record exists |
| | `SHORT_INTEREST_PERCENTAGE_CHANGE_MINIMUM` | Phase 2C change at least 10 percent |
| | `DAYS_TO_COVER_MINIMUM` | Phase 2C value at least 2 days |
| | `BORROW_FEE_MINIMUM` | annualized fee at least 10 percent |
| | `BORROW_FEE_CHANGE_MINIMUM` | Phase 2C change at least 2 percentage points |
| | `BORROW_AVAILABILITY_MAXIMUM` | available shares no more than 100,000 |
| | `BORROW_AVAILABILITY_CHANGE_MAXIMUM` | Phase 2C change no more than -10,000 shares |
| Catalyst evidence | `NEWS_AVAILABLE`, `NEWS_AVAILABLE_BEFORE_AS_OF`, `NEWS_TIMESTAMP_KNOWN` | objective news presence and timing only |
| | `SEC_FILING_AVAILABLE` | point-in-time accepted filing exists |
| | `CORPORATE_ACTION_CONTEXT_AVAILABLE` | descriptive action context exists |
| Evidence validity | `REQUIRED_DOMAINS_PRESENT`, `NO_MATERIAL_CONFLICTS`, `POINT_IN_TIME_ELIGIBLE`, `REQUIRED_UNITS_COMPATIBLE`, `REQUIRED_HISTORY_SUFFICIENT`, `NO_DEFAULT_SUBSTITUTION`, `PROVIDER_SCOPE_EXPLICIT` | reuse Phase 1/2D structural evidence |

Deferred: `SHORT_FLOAT_MINIMUM`, `TTM_SQUEEZE_STATE`, `RSI`, `MACD`,
`BOLLINGER_BAND_STATE`, `OPTIONS_GAMMA_EXPOSURE`, `FAILS_TO_DELIVER`,
`SOCIAL_SENTIMENT`, `SYNTHETIC_SHORT_INTEREST`, and `REAL_TIME_SHORT_INTEREST`.

