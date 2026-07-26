# Phase 3B Research Detection Policy

Version `phase_3b_research_detection_policy.v1` is explicit, provisional, and unoptimized. It is applied identically to every registered case.

The required Phase 3A rules are exactly `PRICE_RANGE`, `MARKET_DATA_AVAILABLE`, and `COMPLETED_BAR_AVAILABLE`. All three `PASS` means `DETECTED`. Any required `FAIL` means `NOT_DETECTED`. Any required `UNKNOWN`, `CONFLICTED`, `INSUFFICIENT_DATA`, or `NOT_APPLICABLE` means `UNEVALUABLE`.

The detection result preserves all supporting Phase 3A rule-result IDs. It does not mutate those results. Original-platform surfaced status is a separate comparison field and is not an input to detection. The policy has no weight, score, percentage, rank, recommendation, alert, trade, or P&L semantics and will not be tuned during Phase 3B.

Limitations: this provisional predicate is not statistical validation, its thresholds are not optimized, missing inputs can dominate the result, and detection neither proves a short squeeze nor authorizes a trading action.

