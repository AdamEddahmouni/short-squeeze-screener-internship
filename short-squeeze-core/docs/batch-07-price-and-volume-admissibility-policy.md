# Batch 07 — Price and Volume Admissibility Policy

How the resolved (Batch 06) and unresolved semantics map to per-operation admissibility.
Conservative by construction: `UNKNOWN` never collapses to a FAIL, missing evidence is
never treated as zero, and no value is inferred from bar magnitudes. Source of truth:
`src/squeeze_core/acquisition/operation_readiness/admissibility.py`.

## Price semantics

Resolved: `SPLIT_ADJUSTED`, **not** dividend-adjusted.

### Ratio operations → `ADMISSIBLE_WITH_CONSTRAINTS`

`PERCENTAGE_RETURN`, `PERCENTAGE_SESSION_GAP`, `PERCENTAGE_BAR_RANGE`,
`PERCENTAGE_RETURN_Z_SCORE`, and the Phase 3A `PERCENTAGE_CHANGE_MINIMUM` rule use a
within-series price ratio. IBKR applies a single uniform split factor to the whole
returned series, so the factor cancels in the ratio (proof in the dependency matrix doc).
Dividend adjustment is not needed for an intraday close-to-close ratio. Admissible under
two explicitly stated constraints:

1. both boundary bars must be **definitely completed** under the timestamp-uncertainty
   policy (satisfied for this cohort — see the timestamp policy doc);
2. no ex-dividend instant is assumed inside the window (prices are not dividend-adjusted);
   this does not change a split-invariant ratio materially for intraday bars and is
   recorded as a stated constraint rather than a silent assumption.

Reason codes: `PRICE_RATIO_SPLIT_INVARIANT`, `DIVIDEND_ADJUSTMENT_NOT_APPLIED`,
`MARKET_BARS_PRESENT`.

### Absolute-price-level operations → `BLOCKED_MISSING_SEMANTICS`

`ABSOLUTE_RETURN`, `ABSOLUTE_SESSION_GAP`, `ABSOLUTE_BAR_RANGE`, and the Phase 3A
`PRICE_RANGE` rule ($2–$20 band) compare an **absolute** price level to a fixed external
threshold. A split factor scales such values, so they are **not** invariant. A split
occurring between the frozen boundary (2026-07-18) and the Batch 05 retrieval instant
(2026-07-24) would move the split-adjusted level away from the boundary-time level.
Corporate-action evidence to confirm no such split is **not** collected in Batch 07 and is
never inferred. This is **not** "require RAW because history once used RAW" — it is a
genuine non-invariance to an unresolved corporate-action state over the boundary→retrieval
gap.

Reason code: `PRICE_ABSOLUTE_LEVEL_CORPORATE_ACTION_UNCONFIRMED`. No conversion to raw
prices; no reverse corporate-action reconstruction.

## Volume semantics → all volume operations `BLOCKED_MISSING_SEMANTICS`

Batch 06 left `volume_adjustment_semantics = UNKNOWN`, `volume_unit = UNRESOLVED`; the
historical feed is provider-filtered. `MEAN_VOLUME_BASELINE`, `RELATIVE_VOLUME`,
`VOLUME_Z_SCORE`, and the Phase 3A `RELATIVE_VOLUME_MINIMUM` rule are all blocked.

The tempting multiplicative-unit-invariance argument for the `RELATIVE_VOLUME` **ratio**
(`target / trailing_mean`) is **insufficient**, on three independent grounds, each of
which alone blocks:

1. **Unit constancy is not established.** `volume_unit` is UNRESOLVED and may not be
   inferred from magnitudes; if the unit regime differed between the target bar and any
   baseline bar the ratio would not be unit-invariant.
2. **Volume corporate-action handling is UNKNOWN.** A split inside the trailing window
   could scale bars non-uniformly, breaking the cancellation.
3. **Provider-filter fraction is not shown stationary.** Historical TRADES data is
   filtered; if the filtered fraction varies across the window the numerator and
   denominator are filtered by different fractions and the ratio is not invariant.

Reason codes: `VOLUME_UNIT_UNRESOLVED`, `VOLUME_CORPORATE_ACTION_UNKNOWN`,
`VOLUME_FILTER_STATIONARITY_UNPROVEN`. A future admissibility claim for any volume
operation must be explicit, mathematical, unit-tested, and outcome-independent, and must
establish a constant, known-compatible unit/filter regime from evidence — not magnitudes.

## Session / provider-filtering

`useRTH=0` is a request parameter, not proof of complete 24-hour or consolidated-market
coverage. Filtering is **irrelevant to price-only operations**, which are therefore not
blocked merely because volume is filtered. An operation that genuinely requires complete
session coverage or consolidated volume is `BLOCKED_MISSING_EVIDENCE`
(`SESSION_COMPLETENESS_UNEVIDENCED`); none of the price-ratio or availability operations
declares that dependency, so none is blocked on this ground.
