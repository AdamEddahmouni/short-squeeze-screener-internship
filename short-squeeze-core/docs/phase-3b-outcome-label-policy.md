# Phase 3B Outcome Label Policy

Version `phase_3b_outcome_label_policy.v1` is explicit, provisional, and unoptimized. The reference price is the first eligible trade-bar close at or after the detection boundary. The fixed horizon is `24_HOURS`; thresholds are exactly `+25%` and `-25%`, with equality counting as a crossing.

Both crossings produce `MIXED_OR_VOLATILE`; upward only produces `SUBSTANTIAL_UPWARD_MOVE`; downward only produces `SUBSTANTIAL_DOWNWARD_MOVE`. A complete horizon with neither produces `NO_SUBSTANTIAL_UPWARD_MOVE`. A partial horizon with neither produces `OUTCOME_INSUFFICIENT_DATA`. No objective observation produces `OUTCOME_UNKNOWN`.

Coverage is deliberately asymmetric: partial coverage may establish a directly observed crossing, but it cannot establish that no crossing occurred. Every result preserves the reference policy and price, boundary, horizon, favorable and adverse extrema, completeness, and supporting observation IDs. It never calculates P&L, infers an entry or exit, confirms a squeeze, or modifies Phase 3A results.

Limitations: the horizon and thresholds are provisional and unoptimized; incomplete or public-source coverage may differ from original-provider coverage; observed price movement does not establish short-squeeze causation or trading profitability.

