> Companion to [batch-08-phase3a-request-result-freeze-plan.md](batch-08-phase3a-request-result-freeze-plan.md).

# Batch 08 — Phase 3A Request Construction

How each of the 13 frozen requests was built, and the two structural decisions that
shaped it.

## 1. Pipeline

```
detection-context CSV  (guarded read: only *-detection-context.csv)
  -> Batch 03 delimited row parser
  -> definitely-completed filter (label + 60s <= frozen boundary)
  -> canonical MarketBarRecord
  -> squeeze_core.adapters.market_bars.normalize_market_bar_records
  -> EventType.BAR observations
       |
       +-> squeeze_core.metrics.returns.build_return_result  (PERCENTAGE_RETURN)
       +-> build_point_in_time_evidence -> coverage / conflicts / sufficiency records
       |
  -> squeeze_core.evaluation.models.RuleEvaluationRequest
  -> squeeze_core.evaluation.evaluate_candidate   (the existing evaluator)
```

Nothing in this chain is a Batch 08 reimplementation. The freeze package parses no
timestamps, validates no OHLC relationship, computes no percentage, and evaluates no rule
of its own.

## 2. Frozen request fields (identical shape for all 13 cases)

| Field | Frozen value |
| --- | --- |
| `symbol` | the frozen Batch 01 symbol |
| `asset_class` | `EQUITY` |
| `as_of` | `2026-07-18T13:37:55.017661Z` |
| `policy_version` | `phase_3a_transparent_candidate_policy.v1` |
| `enabled_rule_ids` | all 25, sorted |
| `provider_scope` | `()` — see §3 |
| `market_interval` | `1_MINUTE` |
| `market_session` | `()` — session completeness is unevidenced (Batch 06), so none is declared |
| `volume_window` | `null` |
| `short_interest_provider` / `borrow_provider` / `news_provider` | `null` |
| `input_observations` | the definitely-completed bars the admissible metric consumed |
| `input_metrics` | exactly one `PERCENTAGE_RETURN` result |
| `input_readiness_results` | coverage, conflicts, sufficiency |
| `default_substitution_fields` | `()` |

## 3. Decision 1 — empty request-level provider scope

The Phase 3A request contract carries one shared `input_observations` tuple and has no
per-rule evidence scoping. A `BAR` observation supplied so `MARKET_DATA_AVAILABLE` can be
evaluated inherently carries `close`, which `PRICE_RANGE` would then consume as an
absolute price level — exactly what Batch 07 blocked.

The policy's own `provider_scope_required` flag is the contract-supported gate, and it
happens to sit on precisely the rules Batch 07 blocked:

| `provider_scope_required` | Rules | Batch 07 status |
| --- | --- | --- |
| `true` | `PRICE_RANGE`, `FLOAT_MAXIMUM`, `PUBLISHED_SHORT_INTEREST_AVAILABLE`, `BORROW_FEE_MINIMUM`, `BORROW_AVAILABILITY_MAXIMUM` | all blocked |
| `false` | `MARKET_DATA_AVAILABLE`, `COMPLETED_BAR_AVAILABLE`, `PERCENTAGE_CHANGE_MINIMUM` (and the rest) | all admissible |

With `provider_scope = ()`:

- `PRICE_RANGE` returns `UNKNOWN` / `EVALUATION_PROVIDER_SCOPE_REQUIRED` **before reading
  any close price** — verified by a test asserting its `observed_value` is `null`;
- `FLOAT_MAXIMUM` short-circuits before any float lookup;
- the admissible rules still receive their evidence, because an empty scope disables
  provider filtering rather than excluding evidence.

Two consequences are disclosed rather than hidden:

1. `PROVIDER_SCOPE_EXPLICIT` resolves `UNKNOWN`. This reflects the deliberate request-level
   omission, not ignorance of the provider: `IBKR` is recorded in every observation's
   provenance and on the metric record.
2. Three short-pressure availability rules report `EVALUATION_PROVIDER_SCOPE_REQUIRED`
   instead of the more specific `..._UNAVAILABLE`. The outcome is `UNKNOWN` either way;
   only the explanation code differs.

This is a granularity limitation of the request contract. It is not an evaluator defect —
the evaluator behaves exactly as specified — and no evaluator code was changed.

## 4. Decision 2 — bounded observation supply

The existing `build_point_in_time_evidence` conflict detection is superlinear in
observation count. Measured on this machine:

| Observations | `build_bar_series` | `build_point_in_time_evidence` |
| --- | --- | --- |
| 2 | 0.00 s | 0.00 s |
| 25 | 0.02 s | 0.11 s |
| 50 | 0.01 s | 0.42 s |
| 100 | 0.01 s | 1.82 s |
| 200 | 0.03 s | 12.73 s |

The evaluator rebuilds that bundle once per bar-dependent rule, and the artifacts hold
1,164–1,440 bars each, so attaching every bar does not terminate in practical time. The
engine is not modified.

Instead the supply is declared: `observation_supply_policy =
ADMISSIBLE_METRIC_BOUNDARY_BARS`. The request carries exactly the observations the
canonical `PERCENTAGE_RETURN` metric consumed, taken from that metric's own
`input_observation_ids` — nothing is hand-picked.

What this changes and does not change:

- the metric is still computed over the **full** admissible window (that path is linear),
  so the metric value is unaffected;
- no rule outcome changes — a committed test freezes the same case under
  `ALL_DEFINITELY_COMPLETED_BARS` and asserts identical outcomes and an identical metric
  value;
- the count `MARKET_DATA_AVAILABLE` and `COMPLETED_BAR_AVAILABLE` report is the number of
  bars *supplied to the request* (2), not the number in the artifact. Both are recorded:
  `TemporalSelection.included_bar_count` and `EvidenceAssociation.observed_bar_count` hold
  the artifact count, `TemporalSelection.supplied_observation_count` the supplied count.

## 5. Temporal selection

A bar is included only when `label + 60 s <= 2026-07-18T13:37:55.017661Z`, i.e. completed
under **both** timestamp interpretations. Observed across all 13 cases:

- coverage `2026-07-16T16:00:00Z .. 2026-07-17T23:59:00Z`;
- last possible completion `2026-07-18T00:00:00Z`, comfortably before the boundary;
- 0 straddling bars excluded, 0 post-boundary bars excluded;
- 1,164–1,440 definitely-completed bars per case.

Bar boundaries are serialized under the label-is-START reading. The choice is
value-invariant, not arbitrary: the included set and its order are interpretation
independent, and the reference/comparison bars are chosen by ordinal position, so the same
two rows and the same closes are selected either way. A committed test recomputes the
metric under the label-is-END reading and asserts identical values and identical selected
closes for every case.

## 6. Percentage metric

| Property | Value |
| --- | --- |
| Metric | `PERCENTAGE_RETURN`, version `1.0.0`, policy `close_to_close_completed.v1` |
| Price field | `close` |
| Reference | earliest definitely-completed detection-context bar |
| Comparison | latest definitely-completed detection-context bar |
| Threshold | `10`, `GREATER_THAN_OR_EQUAL` (inclusive), unit `PERCENT` |
| Provider | `IBKR` (declared at the metric layer, where a provider is required) |

Both Batch 07 constraints hold: both boundary bars are definitely completed, and the
window is recorded so the "prices are not dividend-adjusted" assumption stays inspectable.

**Declared divergence.** This is the close-to-close change across the whole
definitely-completed detection-context window. It is not a reproduction of the original
platform's intraday percentage-change reference, which would need session boundaries that
Batch 06 left `SESSION_COMPLETENESS_UNEVIDENCED`. The window definition avoids session
inference entirely, and the rule outcome should be read as a window-return evaluation
rather than a replication of the original scanner metric.

## 7. Receipt modeling

`build_point_in_time_evidence` gates on `received_timestamp <= as_of`. The application
really received these bars on 2026-07-23, after the boundary, so the modeling is declared
rather than assumed:

- **Primary, `PROVIDER_AVAILABILITY_AS_RECEIPT.v1`** — each bar's provider publication is
  its conservative latest-possible completion (`label + 60 s`), and the adapter's single
  `ingested_at` is the availability instant of the last included bar. This models what the
  provider had published by the boundary, which is the question a point-in-time replay
  asks.
- **Disclosed sensitivity, `LOCAL_RETRIEVAL_RECEIPT.v1`** — `ingested_at` is the real
  Batch 05 retrieval time. Under it every bar is point-in-time ineligible and the three
  bar-dependent rules move to `UNKNOWN` (counts: `PASS` 65, `FAIL` 13, `UNKNOWN` 247).
  Diverging rules: `MARKET_DATA_AVAILABLE`, `COMPLETED_BAR_AVAILABLE`,
  `PERCENTAGE_CHANGE_MINIMUM`.

Both are frozen deterministically. Neither is presented as the single correct reading.
