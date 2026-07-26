# Phase 2B Design Specification: Normalized Market-Activity Metrics

## 1. Purpose and boundary

Phase 2A established `ABSOLUTE_RETURN`, `PERCENTAGE_RETURN`, `ABSOLUTE_SESSION_GAP`,
`PERCENTAGE_SESSION_GAP`, `ABSOLUTE_BAR_RANGE`, `PERCENTAGE_BAR_RANGE`, and `MEAN_VOLUME_BASELINE`
— all derived exclusively from Phase 1H `MARKET_BARS` evidence. ADR 0031 deliberately deferred
relative volume ("the numerator-comparison half") to this phase. Phase 2B is that next layer:

- **In scope**: `RELATIVE_VOLUME`, `VOLUME_PERCENT_DEVIATION`, `VOLUME_Z_SCORE`,
  `MEAN_PERCENTAGE_RETURN_BASELINE`, `PERCENTAGE_RETURN_STANDARD_DEVIATION_BASELINE`,
  `PERCENTAGE_RETURN_Z_SCORE`. All derived exclusively from Phase 1H `MARKET_BARS` evidence and
  Phase 2A metric contracts, with explicit baselines, exact `Decimal` policies, and no look-ahead.
- **Out of scope**: unchanged from Phase 2A §11/handoff §11/§35 plus this phase's own additions —
  dollar volume, turnover, volume acceleration/slope/momentum/percentile, return percentile,
  robust z-score, MAD, EWMA, annualized/realized volatility, ATR, moving averages, RSI, MACD,
  Bollinger/Keltner, TTM Squeeze, breakout/trend/gap classification, any score, rank, Prime/
  Subprime, recommendation, alert, or live/network/database/GUI/ML code.

A Phase 2B result is a **normalized descriptive statistic**, not an interpretation. `relative
volume = 2.75` is a fact about a ratio; "volume is strong" is a judgment. No Phase 2B code path
produces, stores, or can be extended to produce the latter (enforced by the same isolation-test
pattern as Phase 2A — see §14).

## 2. Architectural placement

No new top-level package. Six new modules are added inside the existing `src/squeeze_core/metrics/`
package, alongside Phase 2A's `returns.py` / `volume_baselines.py` / `selection.py`:

| File | Purpose |
|---|---|
| `statistics.py` | Deterministic `Decimal`-only population mean/variance/standard-deviation/sqrt helpers. Pure functions, no model dependencies. |
| `normalized_models.py` | `BaselineStatistics` (new, standalone frozen model), `NormalizedMetricResult` (new, standalone frozen model — **not** `MetricResult`), `ReturnCountWindow`, `StandardDeviationPolicy`, `BaselineKind` enums. |
| `normalized_identifiers.py` | `baseline_identity()` / `deterministic_baseline_id()` and `normalized_metric_identity()` / `deterministic_normalized_metric_id()`, mirroring `metrics/identifiers.py`'s pattern under the same `METRIC_NAMESPACE` (distinct identity-dict shape already prevents collision; see §7). |
| `relative_volume.py` | `RELATIVE_VOLUME`, `VOLUME_PERCENT_DEVIATION` — built directly on Phase 2A's `build_volume_baseline_result`. |
| `volume_standardization.py` | `VOLUME_Z_SCORE` — builds a `BaselineStatistics(baseline_kind=VOLUME)` on top of `selection.resolve_trailing_window` + `volume_baselines.compute_mean_volume`, then standardizes the target volume against it. |
| `return_baselines.py` | `MEAN_PERCENTAGE_RETURN_BASELINE`, `PERCENTAGE_RETURN_STANDARD_DEVIATION_BASELINE` — both read from one shared `BaselineStatistics(baseline_kind=PERCENTAGE_RETURN)` built by pairing adjacent trailing bars and calling Phase 2A's `compute_percentage_return` on each pair. |
| `return_standardization.py` | `PERCENTAGE_RETURN_Z_SCORE` — combines a target `PERCENTAGE_RETURN` (via Phase 2A's `build_return_result`) with the return-distribution `BaselineStatistics`. |

`metrics/models.py` and `metrics/diagnostics.py` receive **additive-only** changes (new enum
members, described exhaustively in §9/§16); `metrics/registry.py` receives six new dispatch
branches. No existing Phase 2A file's *behavior* changes for any Phase 2A-shaped request — proven
in §13/compatibility tests.

**Why not extend `MetricResult` or `TrailingWindow` in place.** `canonical_json.canonicalize()`
calls `model_dump(mode="python")` with no `exclude_defaults`, so *every* field on a Pydantic model
is always serialized — adding even an optional, defaulted field to `MetricResult` would append a
new key to the canonical JSON of **every already-anchored Phase 2A result**, changing its hash.
That is unacceptable per handoff §32/§38 ("preserve every Phase 2A anchor"). `MetricResult` and
`TrailingWindow` are therefore left byte-for-byte untouched; Phase 2B defines `NormalizedMetricResult`
and (where a richer window is needed) `ReturnCountWindow` as wholly separate frozen models. This is
the "compatible Phase 2B extension model" path the handoff names as the fallback when field
extension isn't safe (§12/§32).

## 3. Metric identity and versioning

`MetricName` (an existing `StrEnum` in `metrics/models.py`) gains six new members — additive,
since existing members' serialized string values are unchanged and no exhaustive `match` over
`MetricName` exists anywhere in Phase 2A (`registry.py` uses `if/elif` chains that fall through to
an explicit `ValueError` for unrecognized names, not an exhaustiveness check that could break):

`RELATIVE_VOLUME`, `VOLUME_PERCENT_DEVIATION`, `VOLUME_Z_SCORE`,
`MEAN_PERCENTAGE_RETURN_BASELINE`, `PERCENTAGE_RETURN_STANDARD_DEVIATION_BASELINE`,
`PERCENTAGE_RETURN_Z_SCORE`.

Each `NormalizedMetricResult` carries the same identity discipline as Phase 2A's `MetricResult`:
`metric_version` ("1.0.0" for every Phase 2B metric — first release), a `calculation_policy_version`
naming the *selection* policy (mirrors Phase 2A: e.g. `"trailing_mean_ratio.v1"` for relative
volume), and — new to Phase 2B — `standard_deviation_policy: StandardDeviationPolicy | None`
(`None` for the three metrics that never divide by a standard deviation: `RELATIVE_VOLUME`,
`VOLUME_PERCENT_DEVIATION`, `MEAN_PERCENTAGE_RETURN_BASELINE`).

```python
class StandardDeviationPolicy(StrEnum):
    POPULATION_DECIMAL_V1 = "population_standard_deviation_decimal.v1"
```

Only one policy is defined in Phase 2B (§8 explains why population, not sample). It is still an
explicit, versioned, extensible field rather than a hardcoded formula — a future
`SAMPLE_DECIMAL_V1` would be a new enum member and a new `calculation_policy_version`, never a
silent behavior change under the same version string.

## 4. `BaselineStatistics` (`normalized_models.py`)

```python
class BaselineKind(StrEnum):
    VOLUME = "VOLUME"
    PERCENTAGE_RETURN = "PERCENTAGE_RETURN"

class BaselineStatistics(BaseModel):  # frozen, extra="forbid"
    baseline_kind: BaselineKind
    baseline_version: str                              # "1.0.0"
    calculation_policy_version: str                     # window/pairing policy, e.g. "trailing_bar_count_exclude_current.v1" / "adjacent_close_to_close_return_count.v1"
    standard_deviation_policy: StandardDeviationPolicy
    symbol: str
    asset_class: AssetClass
    as_of: datetime
    source_interval: BarInterval
    session_scope: tuple[BarSession, ...]
    provider_scope: ProviderScopeMode
    provider: str | None
    price_field: PriceField | None                       # PERCENTAGE_RETURN baselines only
    window: TrailingWindow | ReturnCountWindow
    sample_counts: SampleCounts
    mean: Decimal | None
    variance: Decimal | None
    standard_deviation: Decimal | None
    unit: MetricUnit                                      # SHARES (volume) / PERCENT (return)
    input_observation_ids: tuple[str, ...]                # sorted
    input_metric_ids: tuple[str, ...]                      # sorted; Phase 2A PERCENTAGE_RETURN ids for return baselines, () for volume
    input_bar_boundaries: tuple[BarBoundaryRef, ...]
    quality: Quality
    diagnostics: tuple[MetricDiagnostic, ...]
    deterministic_id: str | None
```

One `BaselineStatistics` instance answers "was the baseline statistically usable, and with what
exact mean/variance/stddev" for either a volume distribution or a return distribution — the model
makes which one explicit via `baseline_kind` and `unit`, never leaves it implicit. It carries no
interpretation field (no "is_high", no "percentile", no "label").

`mean`/`variance`/`standard_deviation` are `None` exactly when `quality.state is not KNOWN_VALUE`
(mirrors `MetricResult`'s own value/quality coupling validator, duplicated here rather than shared
because `BaselineStatistics` has three nullable numeric fields, not one).

## 5. `NormalizedMetricResult` (`normalized_models.py`)

```python
class NormalizedMetricResult(BaseModel):  # frozen, extra="forbid"
    metric_name: MetricName
    metric_version: str
    calculation_policy_version: str
    standard_deviation_policy: StandardDeviationPolicy | None
    symbol: str
    asset_class: AssetClass
    as_of: datetime
    source_interval: BarInterval
    session_scope: tuple[BarSession, ...]
    provider_scope: ProviderScopeMode
    provider: str | None
    price_field: PriceField | None
    window: TrailingWindow | ReturnCountWindow | None
    target_boundary: BarBoundaryRef | None
    baseline_metric_id: str | None       # deterministic_id of the MetricResult/BaselineStatistics used as denominator/distribution
    value: Decimal | None
    unit: MetricUnit
    input_observation_ids: tuple[str, ...]
    input_bar_boundaries: tuple[BarBoundaryRef, ...]
    input_metric_ids: tuple[str, ...]     # sorted; e.g. (target_return_id, baseline_id)
    sample_counts: SampleCounts | None
    quality: Quality
    diagnostics: tuple[MetricDiagnostic, ...]
    deterministic_id: str | None
```

This is every field the handoff's §19 identity list and §29 CLI-audit list name, given a
dedicated home instead of overloading `MetricResult`. `sample_counts` is populated only for
`VOLUME_Z_SCORE` (mirrors the underlying `BaselineStatistics`); `None` for the two-value ratio/
deviation metrics and the two single-baseline-read metrics, matching Phase 2A's own "`None` where
the concept doesn't apply" convention (§4 there).

## 6. Selection: reused, not reimplemented

Every Phase 2B metric is built by composing Phase 2A functions, never by re-deriving point-in-time
eligibility, lifecycle resolution, or provider-ambiguity handling:

- **Target bar** (for `RELATIVE_VOLUME`, `VOLUME_PERCENT_DEVIATION`, `VOLUME_Z_SCORE`): resolved
  with `selection.resolve_bar_at_boundary` — the identical function Phase 2A's return/gap/range
  metrics use.
- **Volume baseline mean** (for `RELATIVE_VOLUME`, `VOLUME_PERCENT_DEVIATION`): the literal
  Phase 2A `volume_baselines.build_volume_baseline_result(...)` is called and its `MetricResult`
  is used whole — its `.value` is the mean, its `.deterministic_id` becomes `baseline_metric_id`,
  its `.quality`/`.diagnostics` are inspected to decide availability. This is the strongest form
  of reuse available and directly satisfies ADR 0031's deferred "numerator-comparison half."
- **Volume distribution** (for `VOLUME_Z_SCORE`): `selection.resolve_trailing_window` (the same
  selector `build_volume_baseline_result` calls internally) supplies the same eligible,
  lifecycle-resolved, current-bar-excluded sample set; `volume_baselines.compute_mean_volume` is
  reused for the mean; only variance/stddev (new in Phase 2B, §8) are computed on top.
- **Target return** (for `PERCENTAGE_RETURN_Z_SCORE`): the literal Phase 2A
  `returns.build_return_result(..., MetricName.PERCENTAGE_RETURN)` is called; its `.value` is the
  target return, its `.deterministic_id` is recorded in `input_metric_ids`.
- **Return distribution** (for `MEAN_PERCENTAGE_RETURN_BASELINE`,
  `PERCENTAGE_RETURN_STANDARD_DEVIATION_BASELINE`, and as an input to `PERCENTAGE_RETURN_Z_SCORE`):
  `selection.resolve_trailing_window` supplies `N + 1` trailing, lifecycle-resolved, completed/
  corrected bars (current/target bar excluded); adjacent pairs `(bar[i+1], bar[i])`, walked from
  the most recent pair backward, are each passed through Phase 2A's own
  `returns.compute_percentage_return(start_price, end_price)` using `PriceField.CLOSE` — the exact
  same arithmetic function Phase 2A's `PERCENTAGE_RETURN` metric uses, not a reimplementation.

No selector in `metrics/selection.py` is modified. `resolve_trailing_window`'s `WindowResolution`
already reports `requested`/`eligible`/`used`/`missing`, which both new baseline-statistics paths
reuse verbatim for `SampleCounts`.

### `ReturnCountWindow`

```python
class ReturnCountWindow(BaseModel):  # frozen, extra="forbid"
    window_type: Literal[WindowType.RETURN_COUNT] = WindowType.RETURN_COUNT
    requested_count: int = Field(gt=0)     # number of RETURNS requested (N)
    exclude_current_bar: bool = True       # always True in Phase 2B; the target return is never in its own baseline
    minimum_samples: int = Field(gt=0)     # minimum usable RETURNS
```

`WindowType` (existing `StrEnum`) gains one new member, `RETURN_COUNT` — additive; Phase 2A's
`TrailingWindow.window_type is not WindowType.BAR_COUNT -> NotImplementedError` guard is untouched
and still fires exactly as before for any Phase 2A caller (it never constructs `RETURN_COUNT`).
`ReturnCountWindow` is a **new, separate** model, not a `TrailingWindow` variant — this keeps the
"only `BAR_COUNT` is implemented" guarantee on `TrailingWindow` itself literally true, and avoids
threading a second `window_type` branch through code Phase 2A already ships and anchors.

Internally, a `ReturnCountWindow(requested_count=N, minimum_samples=M)` is translated to
`TrailingWindow(window_type=BAR_COUNT, requested_count=N + 1, minimum_samples=M + 1,
exclude_current_bar=True)` before calling `resolve_trailing_window` — implementing the handoff's
"a return count of N normally requires at least N + 1 eligible bars" rule as one line of
arithmetic at the call site, not a new selector code path.

## 7. Deterministic identity

`normalized_identifiers.py` defines two identity-dict builders under the *same*
`METRIC_NAMESPACE` UUID Phase 2A already defines (`metrics/identifiers.py`):

- `baseline_identity(stats: BaselineStatistics) -> dict` — every field that affects the baseline's
  numeric output: `baseline_kind, baseline_version, calculation_policy_version,
  standard_deviation_policy, symbol, asset_class, as_of, source_interval, session_scope,
  provider_scope, provider, price_field, window, input_observation_ids (sorted), input_metric_ids
  (sorted), input_bar_boundaries (sorted)`. `mean/variance/standard_deviation` and `diagnostics`
  are excluded, mirroring Phase 2A's `metric_identity()` rationale exactly (§7 there): identical
  inputs and policy always yield the identical ID regardless of the numeric outcome.
- `normalized_metric_identity(result: NormalizedMetricResult) -> dict` — every
  `NormalizedMetricResult` field except `value`, `diagnostics`, and `deterministic_id` itself,
  including the new `baseline_metric_id` and `target_boundary` fields (so two requests that differ
  only in which baseline/target they reference never collide).

Reusing one namespace UUID with two structurally distinct identity-dict shapes (one has
`baseline_kind`+`variance`-adjacent keys that a `NormalizedMetricResult` identity never has, and
vice versa) makes an accidental collision between a `BaselineStatistics` ID and a
`NormalizedMetricResult` ID cryptographically negligible and, in the tested fixture set, verified
absent (§12 compatibility tests). A `NormalizedMetricResult` ID and a Phase 2A `MetricResult` ID
are likewise structurally distinct (different key sets) under the same namespace, so
`baseline_metric_id` pointing at either a Phase 2A `MEAN_VOLUME_BASELINE` ID or a Phase 2B
`BaselineStatistics` ID is unambiguous by construction, not by convention.

An unavailable result (`value is None`) still has a stable, request-derived ID — the identity dict
never includes `value`, so "no eligible target" and "insufficient history" for the *same* request
shape produce IDs that differ only if their `diagnostics`-independent input fields differ (they do:
e.g. `input_observation_ids` differs when zero vs. some samples were found), satisfying §19's "two
semantically different unavailable results must not collide" requirement — verified by test, not
assumed.

## 8. Statistics (`metrics/statistics.py`) — the core new arithmetic

```python
DECIMAL_STATISTICS_PRECISION = 50  # calculation-only guard precision; see rationale below

def decimal_mean(values: Sequence[Decimal]) -> Decimal:
    with localcontext() as ctx:
        ctx.prec = DECIMAL_STATISTICS_PRECISION
        return sum(values, Decimal(0)) / Decimal(len(values))

def decimal_population_variance(values: Sequence[Decimal], mean: Decimal) -> Decimal:
    with localcontext() as ctx:
        ctx.prec = DECIMAL_STATISTICS_PRECISION
        total = sum(((value - mean) ** 2 for value in values), Decimal(0))
        return total / Decimal(len(values))

def decimal_sqrt(value: Decimal) -> Decimal:
    with localcontext() as ctx:
        ctx.prec = DECIMAL_STATISTICS_PRECISION
        return value.sqrt()

def population_standard_deviation(values: Sequence[Decimal]) -> tuple[Decimal, Decimal, Decimal]:
    """Returns (mean, variance, standard_deviation)."""
    mean = decimal_mean(values)
    variance = decimal_population_variance(values, mean)
    return mean, variance, decimal_sqrt(variance)
```

**Population, not sample, standard deviation** (`population_standard_deviation_decimal.v1`):

```
mean = Σxᵢ / N
variance = Σ(xᵢ - mean)² / N
standard_deviation = sqrt(variance)
```

The handoff recommends population as the initial policy and explicitly says "do not implement
sample standard deviation unless the design proves it is required." Nothing in Phase 2B's scope
(descriptive z-scores over an explicit, fully-enumerated trailing window, not an inference about a
larger unseen population) requires Bessel's correction — the trailing window *is* the entire
population being described, not a sample drawn from a larger one. The inherited archived-repository
`core/technical_indicators.py:compute_weekly_volatility` and `compute_ttm_squeeze` both use Python's
`statistics.stdev` (sample, `N-1` denominator) — noted in §13 as a formula **not** reused as-is,
since Phase 2B's population framing is the deliberately different, documented choice (ADR 0033).

**Precision policy** (`DECIMAL_STATISTICS_PRECISION = 50`, a local, non-global
`decimal.localcontext()` guard — never mutates the ambient `Decimal` context, exactly matching
Phase 2A's `compute_percentage_return`/`compute_mean_volume` pattern of `with localcontext() as
ctx: ctx.prec = 28`). Phase 2B increases the guard from Phase 2A's 28 to 50: variance squares each
deviation before summing, and volume samples can be large (billions of shares → an 18-19 digit
squared term); summing several such terms and then taking a square root needs headroom beyond the
28 digits sufficient for a single division. 50 significant digits is far beyond any realistic bar
volume or price-return magnitude in this system's fixtures and leaves a wide, documented margin
rather than a value tuned to just pass the anchor set.

**`Decimal.sqrt()`** is used directly — it is deterministic under a fixed, explicit context
precision (no platform-dependent `math.sqrt` float conversion anywhere in `metrics/`), matching the
handoff's explicit requirement. No `numpy`/`scipy`/`statistics` module call is used for any Phase 2B
arithmetic (`statistics.stdev`/`.pstdev` use the same `N`/`N-1` formulas but operate on `float` or
un-contexted `Decimal` — Phase 2B's own `decimal_population_variance`/`decimal_sqrt` are used
instead so the guard precision is explicit and local at every call site, not implicit in a stdlib
helper).

**Minimum samples**: volume z-score defaults to `minimum_samples=2` (handoff-recommended floor);
return-baseline windows require the caller to state `minimum_samples` explicitly (`ReturnCountWindow`
has no default), consistent with Phase 2A's own "minimum_samples is always caller-specified, never
implied" convention (`TrailingWindow.minimum_samples: int = Field(gt=0)`, no default).

**Zero variance**: `standard_deviation == 0` (all samples identical) is a valid, computable
statistic in its own right — `BaselineStatistics.standard_deviation` is still populated as
`Decimal(0)`. It is any metric that *divides* by that standard deviation (`VOLUME_Z_SCORE`,
`PERCENTAGE_RETURN_Z_SCORE`) that becomes `INVALID`/no-value with a `*_ZERO_VARIANCE` diagnostic —
the baseline computation itself does not fail.

## 9. Zero, missing, and insufficient-history semantics

| Situation | Value | `QualityState` | Diagnostic |
|---|---|---|---|
| Target bar not found at requested boundary | `None` | `UNAVAILABLE` | `RELATIVE_VOLUME_TARGET_NOT_FOUND` / `RETURN_TARGET_NOT_FOUND` |
| Target bar found, `payload.volume is None` | `None` | `UNAVAILABLE` | `RELATIVE_VOLUME_TARGET_MISSING_VOLUME` |
| Target bar volume `== 0` | `Decimal(0)` (relative volume) / `Decimal(-100)` (deviation, if baseline > 0) | `KNOWN_VALUE` | none (zero is a valid target, not missing) |
| Volume baseline unavailable (Phase 2A `MEAN_VOLUME_BASELINE` not `KNOWN_VALUE`) | `None` | `UNAVAILABLE` | `RELATIVE_VOLUME_BASELINE_UNAVAILABLE` |
| Volume baseline mean `== 0` | `None` | `INVALID` | `RELATIVE_VOLUME_BASELINE_ZERO` / `NORMALIZED_METRIC_ZERO_BASELINE` |
| Volume/return distribution has zero usable samples | `None` | `UNAVAILABLE` | `VOLUME_DISTRIBUTION_WINDOW_EMPTY` / `RETURN_DISTRIBUTION_WINDOW_EMPTY` |
| Distribution below `minimum_samples` | `None` | `UNAVAILABLE` | `VOLUME_DISTRIBUTION_INSUFFICIENT_SAMPLES` / `RETURN_DISTRIBUTION_INSUFFICIENT_RETURNS` |
| Trailing bars available but `< N + 1` (return count window) | `None` | `UNAVAILABLE` | `RETURN_DISTRIBUTION_INSUFFICIENT_BARS` |
| Distribution standard deviation `== 0` and a z-score was requested | `None` | `INVALID` | `NORMALIZED_METRIC_ZERO_VARIANCE` / `VOLUME_DISTRIBUTION_ZERO_VARIANCE` / `RETURN_DISTRIBUTION_ZERO_VARIANCE` |
| Ambiguous provider (target or any distribution sample) | `None` | `UNAVAILABLE` | `METRIC_AMBIGUOUS_PROVIDER` (reused verbatim from Phase 2A) |
| Same-boundary conflict / cancelled / partial input | `None` | `CONFLICTED`/`UNAVAILABLE` | `METRIC_CONFLICTED_INPUT` / `METRIC_CANCELLED_INPUT` / `METRIC_PARTIAL_INPUT` (reused verbatim) |

Every "missing" row above is `value=None`, never `Decimal(0)` — this is the direct fix to the
inherited `ib_api.py:499`/`schwab_api.py`'s `rel_volume = 0.0` fallback when history is missing
(§13), which conflated "we don't know" with "the answer is exactly zero." `BaselineStatistics`
follows the identical `value is None iff quality.state is not KNOWN_VALUE` discipline as
`MetricResult` (own validator, §4).

## 10. Provider, interval, session, and unit compatibility

Every Phase 2B builder constructs exactly one `MetricSelectionRequest` (Phase 2A's existing
dataclass) per call and threads it through every selector call it makes (target resolution,
baseline resolution, distribution resolution) — the same `symbol`, `as_of`, `source_interval`,
`session_scope`, `provider_scope`, `provider` values reach every sample. This structurally
prevents mixing:

- **Provider**: identical `MetricSelectionRequest.provider`/`provider_scope` on every call;
  ambiguity is `METRIC_AMBIGUOUS_PROVIDER` from the reused selector, not re-detected.
- **Interval/session**: `evidence.bars.build_bar_series` (called once per selector invocation,
  itself parameterized by the one shared request) filters both target and baseline candidates to
  the same `source_interval`/`session_scope` before any Phase 2B code sees them — a mixed-interval
  or mixed-session candidate is excluded upstream, exactly like Phase 2A's volume baseline
  (`docs/volume-baseline-semantics.md`: "there is no separate 'mixed interval' diagnostic because
  the metric structurally cannot receive one").
- **Volume unit**: `RELATIVE_VOLUME`/`VOLUME_PERCENT_DEVIATION` inherit Phase 2A's
  `build_volume_baseline_result`'s own `target_volume_unit` cross-check verbatim (its
  `VOLUME_BASELINE_MIXED_UNITS` diagnostic). `VOLUME_Z_SCORE`'s own
  `resolve_trailing_window(..., target_volume_unit=...)` call passes the target bar's resolved
  unit through the identical parameter.
- **Price field**: return metrics fix `PriceField.CLOSE` for both the target return and every
  distribution pair in one call path — there is no second code path that could read a different
  field, so no "mixed price field" diagnostic is reachable (documented as an intentionally omitted
  code, §16, exactly like Phase 2A omits unreachable codes).

## 11. No-look-ahead enforcement

Unchanged mechanism from Phase 2A (ADR 0030, design §6), inherited for free by composition: every
Phase 2B selector call is one of `resolve_bar_at_boundary` / `resolve_trailing_window`, both of
which start from `evidence.bars.build_bar_series(..., as_of=...)`. No Phase 2B module holds a
direct, unfiltered observation list plus a separately-applied `as_of` cutoff. The target/current
bar or target return is always excluded from its own baseline (`exclude_current_bar=True` is the
only value Phase 2B ever constructs — never exposed as a toggle in the six new metrics' public
request shape, unlike Phase 2A's `MEAN_VOLUME_BASELINE` which allows an explicit opt-out). A
correction or cancellation participates in a baseline or target resolution only once its own
`source_timestamp`/`received_timestamp`/`effective_timestamp` are `<= as_of` — the identical gate,
re-executed, not re-implemented, for every additional selector call Phase 2B introduces.
`tests/metrics/test_normalized_lifecycle.py` proves byte-identical before/after-correction and
before/after-cancellation results for `RELATIVE_VOLUME`, `VOLUME_Z_SCORE`, and
`PERCENTAGE_RETURN_Z_SCORE` (one representative metric family from each new selector path).

## 12. Inherited-formula disposition (archived-repository research, read-only)

All three archived repositories were confirmed clean and at their required commits
(`0897562e`, `6dbefd1a`, `84f770dd`) before any inspection; no file in any of them was modified.

| Inherited formula | Source | Disposition in Phase 2B |
|---|---|---|
| `rel_volume = today_volume / hist["avg_volume"]` | `core/ib_api.py:497` (and `schwab_api.py:332-333`, cited in Phase 2A's own research) | Formula *shape* reused (`target/baseline`); the original's `else: rel_volume = 0.0` fallback (`ib_api.py:499`) when history is missing — silently treating "unknown" as "zero" — is explicitly **not** reused. Phase 2B returns `value=None` with `RELATIVE_VOLUME_BASELINE_UNAVAILABLE` instead. |
| `avg_volume = statistics.mean(volumes[:-1])` | `core/ib_api.py:643` | Already reused *by Phase 2A* (`MEAN_VOLUME_BASELINE`); Phase 2B calls that same Phase 2A function rather than re-deriving it (§6). |
| `compute_weekly_volatility`: `statistics.stdev(daily_returns) * 100` | `core/technical_indicators.py:28-41` | **Not reused as-is.** Two problems: (1) `statistics.stdev` is *sample* standard deviation (`N-1`); Phase 2B's z-scores describe the trailing window itself, not an inference about a larger population, so population (`N`) is used instead (ADR 0033). (2) it is a fixed 5-day window with no explicit minimum-sample or point-in-time gate — Phase 2B's `ReturnCountWindow` makes both explicit and caller-controlled. The *shape* (stdev of period-over-period percentage returns) is the one part reused. |
| `compute_ttm_squeeze` Bollinger basis: `statistics.stdev(recent_closes)` | `core/technical_indicators.py:96` | Not reused — this stdev is over raw closing *prices* (for a band width), not over *returns* or *volumes* standardized against a baseline; also feeds the explicitly excluded TTM Squeeze indicator (handoff §11/§35). Confirms the inherited codebase never computed a return or volume z-score anywhere — Phase 2B's `VOLUME_Z_SCORE`/`PERCENTAGE_RETURN_Z_SCORE` have no inherited precedent to adapt, only the general "population vs. sample" lesson above. |
| `is_squeeze_confirmed(rel_volume, change_percent, ...)`: `rel_volume < 5 or abs(change_percent) < 50` | `core/squeeze_score.py:124-137` | Rejected — a hardcoded threshold classification over relative volume and percentage change, exactly the "no threshold classification" prohibition (handoff §10.1/§10.2). Confirms relative volume was only ever consumed for scoring in the inherited system, never exposed as a bare descriptive ratio the way Phase 2B requires. |
| Premarket vs. regular-session volume/return comparison | searched `core/*.py` (`ib_api.py`, `schwab_api.py`, `filters.py`, `technical_indicators.py`) | **Not present** — no inherited file distinguishes premarket from regular-session bars at all (Phase 0's own known-gap). Phase 2B's session compatibility rule (§10) is new, not adapted from any inherited pattern. |
| Rolling-window calculations (`ib_api.py` historical-bar cache) | `core/ib_api.py:640-646` | Formula-adjacent only (feeds `avg_volume`, already covered above); no rolling z-score or standardized-return window existed to inherit. |

**Summary classification** (handoff §8.9): the `avg_volume`/`rel_volume` division shape is
*objectively reusable* (already reused, via Phase 2A's baseline + this phase's own ratio); the
`rel_volume = 0.0`-on-missing fallback and the sample-stdev choice are *incorrect for this
system's semantics* (fixed, not reused); TTM Squeeze's stdev and the squeeze-score threshold logic
are *out of Phase 2B scope* (indicator/classification, excluded outright); no inherited formula is
*look-ahead prone* in a way distinct from what Phase 2A's research and ADR 0030 already closed
structurally (the archived repos' relative volume always reads a single "latest" live tick against
a historical average, which Phase 2B's point-in-time boundary resolution already supersedes for
every metric, not case-by-case).

## 13. Standard-deviation policy — ADR summary (see `docs/adr/0033-*.md`)

Population, not sample. Rationale is architectural, not merely "the handoff recommended it": every
Phase 2B distribution is an **explicit, fully-enumerated, closed window** (exactly `N` trailing
bars/returns the caller asked for and the selector found) — the population/sample distinction only
matters when a sample is being used to *infer* a parameter of a larger, unobserved population.
Phase 2B never makes such an inference (no confidence interval, no hypothesis test, no forecast);
it reports "how far is this point from the mean *of the window I was given*," which is a population
statistic over that window by construction. Sample standard deviation remains available as a future
`StandardDeviationPolicy` member without touching `POPULATION_DECIMAL_V1`'s meaning.

## 14. Isolation boundary — required test-file change

`tests/metrics/test_isolation.py::FORBIDDEN_IDENTIFIER_SUBSTRINGS` currently forbids the literal
substrings `"relative_volume"` and `"rvol"` anywhere in `src/squeeze_core/metrics/*.py` — a
Phase-2A-only guarantee ("relative volume is out of scope for *this* phase," ADR 0031), not a
permanent prohibition. Phase 2B's handoff explicitly requires implementing `RELATIVE_VOLUME` as a
descriptive, non-scored ratio. This test is updated (not weakened) as part of Phase 2B: the two
literal-relative-volume entries are removed from `FORBIDDEN_IDENTIFIER_SUBSTRINGS`; every other
entry (`moving_average, bollinger, keltner, ttm_squeeze, candidate_score, candidate_rank,
prime_subprime, recommendation, order_placement, place_order, cancel_order, paper_trade,
live_trade`) is left untouched, and the handoff's own naming instruction ("Do not call this ‘RVOL
signal.’") is honored by never introducing the substring `rvol` anywhere in Phase 2B source — kept
forbidden. `test_no_result_field_could_carry_a_ratio_ranking_or_recommendation` (which checks
`MetricResult.model_fields`, not source text) is extended with an identical check against
`NormalizedMetricResult.model_fields` and `BaselineStatistics.model_fields`, still forbidding
`score, rank, recommendation, signal` (and, separately, still forbidding `rvol` — `relative_volume`
itself is now a legitimate field name and is not added to that forbidden set).

## 15. Serialization

`NormalizedMetricResult` and `BaselineStatistics` are frozen Pydantic `BaseModel`s; the existing
`canonicalize()` (§ above) already handles arbitrary `BaseModel`s including nested ones with no
changes needed. New thin wrappers in `metrics/serialization.py` (additive):
`serialize_normalized_metric_result` / `deserialize_normalized_metric_result` /
`normalized_metric_result_hash`, and the equivalent trio for `BaselineStatistics` — mirroring the
existing `serialize_metric_result` family exactly, one new function pair per new model rather than
a generic dispatcher (matches the existing file's own style: two small, explicit functions per
model, not a registry).

## 16. Diagnostics

`MetricDiagnosticCode` (existing `StrEnum` in `metrics/diagnostics.py`) gains the following new
members — additive; no existing member's value or meaning changes:

```
NORMALIZED_METRIC_ZERO_BASELINE
NORMALIZED_METRIC_ZERO_VARIANCE
NORMALIZED_METRIC_INSUFFICIENT_HISTORY

RELATIVE_VOLUME_TARGET_NOT_FOUND
RELATIVE_VOLUME_TARGET_MISSING_VOLUME
RELATIVE_VOLUME_BASELINE_UNAVAILABLE
RELATIVE_VOLUME_BASELINE_ZERO

VOLUME_DISTRIBUTION_WINDOW_EMPTY
VOLUME_DISTRIBUTION_INSUFFICIENT_SAMPLES
VOLUME_DISTRIBUTION_ZERO_VARIANCE

RETURN_DISTRIBUTION_WINDOW_EMPTY
RETURN_DISTRIBUTION_INSUFFICIENT_BARS
RETURN_DISTRIBUTION_INSUFFICIENT_RETURNS
RETURN_DISTRIBUTION_ZERO_VARIANCE
RETURN_TARGET_NOT_FOUND
RETURN_TARGET_EXCLUDED_FROM_BASELINE
```

Codes named in the handoff but never reachable by any Phase 2B code path are intentionally omitted,
matching Phase 2A's own stated practice (design §9): `*_INCOMPATIBLE_PROVIDER/_INTERVAL/_SESSION/
_UNIT/_PRICE_FIELD` are not separately defined because §10 shows every one of those mismatches is
structurally excluded upstream (one shared selection request, one shared price field) and already
surfaces as the reused `METRIC_AMBIGUOUS_PROVIDER` or `VOLUME_BASELINE_MIXED_UNITS` codes, not a
new Phase-2B-specific code; `*_CANCELLED_INPUT/_CONFLICTED_INPUT/_PARTIAL_INPUT/
_UNKNOWN_AVAILABILITY` are reused verbatim from Phase 2A rather than redefined per-metric-family.
Severity levels and the sort key `(code.value, observation_ids, message)` are unchanged
(`sort_diagnostics` reused as-is).

## 17. Quality mapping

Identical `QualityState` reuse as Phase 2A (design §9), applied to both `NormalizedMetricResult`
and `BaselineStatistics`: `KNOWN_VALUE` (computed), `UNAVAILABLE` (missing input/history/ambiguous
scope), `INVALID` (zero baseline or zero variance being divided by), `CONFLICTED` (unresolved
same-boundary conflict, reused verbatim). No new `QualityState` member is added — the handoff's
"UNKNOWN" row is, as in Phase 2A, folded into `UNAVAILABLE` with a specific diagnostic reason.

## 18. CLI

No new subcommand. `metrics/registry.py::build_metric_result` gains six new `if metric_name is
MetricName.X:` branches that parse the same JSON spec shape (`build-market-metrics --spec ...`,
unchanged) into the appropriate Phase 2B request dataclass and call the corresponding builder —
`__main__.py` itself needs zero changes, since it already dispatches generically through
`build_metric_results`. This directly satisfies "prefer preserving `build-market-metrics`... add
Phase 2B metric names to the existing registry and request format." Each of the six new
`NormalizedMetricResult`/`BaselineStatistics`-shaped outputs serializes through the same
`canonical_json_bytes` the CLI already prints with, so `build-market-metrics` output for a mixed
Phase 2A + Phase 2B spec list is one canonical JSON array, offline, deterministic, network-free
— exactly like today.

## 19. Compatibility guarantee

- `MetricResult`, `TrailingWindow`, and every existing `MetricDiagnosticCode`/`MetricName`/
  `WindowType` member are byte-identical in behavior and serialization to Phase 2A.
- `metrics/selection.py`, `metrics/returns.py`, `metrics/volume_baselines.py`,
  `metrics/gaps.py`, `metrics/ranges.py` are **not modified** — Phase 2B only calls their existing
  public functions.
- No file outside `src/squeeze_core/metrics/`, `tests/`, `docs/`, and `scripts/` is touched.
- `tests/fixtures/compatibility/phase_1_anchor_manifest.json` and
  `tests/fixtures/metrics/expected_phase_2a_metric_metadata.json` are not written to by any
  Phase 2B code or script; a new, separate
  `tests/fixtures/metrics/expected_phase_2b_metric_metadata.json` is created instead (§ test plan).
  Compatibility tests (`tests/compatibility/test_phase_2b_isolation.py`) diff both files against
  the Phase 2A completion commit (`d776e30e`) and assert zero delta.

## 20. Excluded from Phase 2B (restated for completeness)

Unchanged list from handoff §11/§35: relative-volume ranking/categories/"unusual volume" labels,
dollar volume, turnover, float-adjusted volume, volume acceleration/slope/momentum/percentile,
return percentile, robust z-score, MAD, EWMA statistics, rolling Sharpe, annualized/realized
volatility, ATR/true range, moving averages (simple/exponential), RSI, MACD, Bollinger/Keltner,
TTM Squeeze, breakout/trend/gap classification, candlestick patterns, order-flow/aggressor
inference, sentiment, catalyst classification, any score/rank/Prime-Subprime/recommendation/alert/
entry/exit logic, backtesting, live integration, deployment, GUI, database, paper/live trading,
machine learning. Verified absent by the extended isolation tests (§14) and the completion report.
