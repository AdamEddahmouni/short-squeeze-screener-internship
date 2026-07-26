# Batch 07 — Operation Dependency Matrix

Declarative dependencies for every Phase 2 operation reachable from the Batch 05
`DETECTION_CONTEXT_PRECEDING_24H` bars, plus the semantic fields whose resolution state
materially affects each. Source of truth:
`src/squeeze_core/acquisition/operation_readiness/dependencies.py`. Pure data — no
formula logic, no trading threshold.

Present evidence domains in this evidence set: **`{MARKET_BARS}`** only.

Resolved semantics consumed (Batch 06): price = `SPLIT_ADJUSTED` (not dividend-adjusted);
volume adjustment = `UNKNOWN`; volume unit = `UNRESOLVED`; timestamp START/END = `UNKNOWN`
(epoch-seconds/UTC representation known); session = `EXTENDED` (`useRTH=0`); historical
feed is provider-filtered.

## Semantic-field dependency legend

| field | meaning |
|-------|---------|
| price_adjustment_absolute | correctness depends on an ABSOLUTE price level (adjustment-sensitive) |
| price_adjustment_ratio | uses a within-series price RATIO (uniform split factor cancels) |
| dividend_adjustment | correctness needs a dividend-adjustment stance |
| volume_unit | depends on the volume unit (shares vs lots) |
| volume_corporate_action | depends on volume corporate-action handling |
| volume_filter_stationarity | needs a constant provider-filter fraction across the window |
| timestamp_boundary | needs START/END disambiguation against a boundary |
| session_completeness | needs complete session coverage |

## Phase 2 operations

| operation | kind | required domains | required metrics | semantic dependencies |
|-----------|------|------------------|------------------|-----------------------|
| PERCENTAGE_RETURN | PRICE_ONLY_RATIO | MARKET_BARS | — | price_adjustment_ratio, dividend_adjustment |
| PERCENTAGE_SESSION_GAP | PRICE_ONLY_RATIO | MARKET_BARS | — | price_adjustment_ratio, dividend_adjustment |
| PERCENTAGE_BAR_RANGE | PRICE_ONLY_RATIO | MARKET_BARS | — | price_adjustment_ratio, dividend_adjustment |
| PERCENTAGE_RETURN_Z_SCORE | PRICE_ONLY_RATIO | MARKET_BARS | — | price_adjustment_ratio, dividend_adjustment |
| ABSOLUTE_RETURN | PRICE_ONLY_ABSOLUTE_LEVEL | MARKET_BARS | — | price_adjustment_absolute |
| ABSOLUTE_SESSION_GAP | PRICE_ONLY_ABSOLUTE_LEVEL | MARKET_BARS | — | price_adjustment_absolute |
| ABSOLUTE_BAR_RANGE | PRICE_ONLY_ABSOLUTE_LEVEL | MARKET_BARS | — | price_adjustment_absolute |
| MEAN_VOLUME_BASELINE | VOLUME_DEPENDENT | MARKET_BARS | — | volume_unit, volume_corporate_action, volume_filter_stationarity |
| RELATIVE_VOLUME | VOLUME_DEPENDENT | MARKET_BARS | MEAN_VOLUME_BASELINE | volume_unit, volume_corporate_action, volume_filter_stationarity |
| VOLUME_Z_SCORE | VOLUME_DEPENDENT | MARKET_BARS | — | volume_unit, volume_corporate_action, volume_filter_stationarity |

## Why ratios and absolute differences diverge

`PERCENTAGE_RETURN = (end − start) / start`. A split applies one uniform factor `k` to
every bar of a single returned series: `(k·end − k·start)/(k·start) = (end − start)/start`.
The factor cancels — split-invariant.

`ABSOLUTE_RETURN = end − start`. Under the same factor: `k·end − k·start = k·(end − start)`.
The dollar value is scaled by `k`, so a fixed dollar threshold is **not** invariant. The
same holds for `ABSOLUTE_SESSION_GAP` and `ABSOLUTE_BAR_RANGE` (all differences of prices).
`PERCENTAGE_*` range/gap and the return z-score are ratios / scale-standardized and remain
invariant.

## Volume operations

All three depend on the volume unit, volume corporate-action handling, and the constancy
of the provider-filter fraction. None is resolved by Batch 06, and none may be inferred
from bar magnitudes. The ratio-invariance argument for `RELATIVE_VOLUME` is insufficient
(see `docs/batch-07-price-and-volume-admissibility-policy.md`), so every volume operation
is blocked. `DAYS_TO_COVER` additionally requires `PUBLISHED_SHORT_INTEREST`, which is
absent from this evidence set.

## Availability / alignment operations (Phase 3A rule inputs)

| operation | kind | semantic dependency |
|-----------|------|---------------------|
| MARKET_DATA_AVAILABLE | MARKET_BAR_AVAILABILITY | (existence only) |
| COMPLETED_BAR_AVAILABLE | MARKET_BAR_AVAILABILITY | timestamp_boundary |

These read no price or volume value — only whether bars exist and (for the completed-bar
rule) whether a bar is definitely completed before the boundary under timestamp
uncertainty.
