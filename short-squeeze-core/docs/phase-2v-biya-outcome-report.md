# Phase 2V BIYA Historical Outcome Report

## Result

The additive outcome amendment concludes
`OUTCOME_CONFIRMED_METHODOLOGY_UNVERIFIED`. This does not replace the original Phase 2V
`INSUFFICIENT_EVIDENCE` forensic result. No original BIYA field, score, label, news
value, days-to-cover value, or provider response was recovered.

The fixed policy is
`first_eligible_trade_bar_close_at_or_after_boundary.v1`. At the earliest boundary
(`2026-07-17T14:23:58Z`) the reference close is 4.340000152587891. At the latest
boundary (`2026-07-17T16:54:58Z`) it is 4.230000019073486. The retained maximum is
9.890000343322754, corresponding to maximum observed moves of 127.88% and 133.81%,
respectively. Both exceed the predeclared 25% confirmation threshold.

The maximum-through-dataset-end windows are `PARTIAL`: retained one-minute data has
diagnosed gaps and does not cover an indefinitely closed future period. The earliest
boundary's retained minimum is 2.759999990463257 (-36.41%); the latest boundary's is
the same price (-34.75%). These are descriptive extrema, not fills or performance.

## Evidence acquired

The acquisition event occurred at `2026-07-21T21:00:34.865603Z`. Public fallback data
preserved 3,295 one-minute provider rows, 14 daily rows, seven news records, one 1:10
reverse-split event, and BIYA FINRA short-sale-volume rows for July 16, 17, and 20.
Normalization accepted 2,838 intraday observations and rejected 457 rows with stable
diagnostics rather than repairing them silently.

IBKR, Schwab, local borrow history, published short interest, and Nasdaq halt history
were unavailable through permitted local access. The July 21 FINRA daily file was not
available at retrieval. Each state has its own committed acquisition manifest.

FINRA daily short-sale volume is retained only as transactional-volume context. It is
not published short interest, short float, or a days-to-cover numerator. Because no
eligible published short-interest numerator was acquired, historical days to cover
remains unavailable.

## Interpretation boundary

The result supports only this statement: BIYA experienced a substantial subsequent
price move from both defensible detection-window boundaries in the retained dataset.
It does not prove a short squeeze, causation, execution, profitability, or the quality
of the original algorithm. Later price movement can confirm the outcome but cannot
reconstruct or validate missing original platform inputs.

