# Phase 2A Design Specification: Foundational Market Metrics

## 1. Purpose and boundary

Phase 1 established ten objective, point-in-time evidence domains, including `MARKET_BARS`
(Phase 1H). `docs/phase-1-known-limitations.md` explicitly names "derived metrics of any kind:
relative-volume calculation, returns, gaps, ranges, volume baselines" as deliberately out of
scope for Phase 1. Phase 2A is that next layer, and only that layer:

- **In scope**: absolute/percentage return, absolute/percentage session gap, absolute/percentage
  bar range, mean volume baseline. All derived exclusively from Phase 1H `MARKET_BARS` evidence,
  with explicit point-in-time, lifecycle, session, and provider selection.
- **Out of scope**: relative volume, any technical indicator (moving averages, RSI, MACD, ATR,
  Bollinger/Keltner, TTM Squeeze), momentum/breakout/trend/gap classification, candidate scoring,
  ranking, Prime/Subprime, recommendations, live integration. See §11 for the full exclusion list.

A Phase 2A metric result is a **local calculation**, not a provider observation. It must never be
represented as if a data provider supplied it directly (`docs/field-semantics.md`: "A local
calculation cannot be labeled as a Schwab, thinkorswim, or other provider observation. Derived
records name the calculation/version and retain parent IDs and parameters.").

## 2. Architectural placement

New package: `src/squeeze_core/metrics/`, a peer of `src/squeeze_core/evidence/` — not a
modification to it. It reuses, rather than duplicates, existing conventions:

| Concern | Reused from Phase 1 | Phase 2A addition |
|---|---|---|
| Point-in-time bar eligibility, symbol/interval/session filtering, deterministic ordering, revision-pair linkage | `evidence.bars.build_bar_series` (`src/squeeze_core/evidence/bars.py`) | `metrics/selection.py` layers lifecycle resolution and provider-ambiguity handling on top of the returned `BarSeries` |
| Canonical JSON, SHA-256 content hashing | `serialization.canonical_json` | none — used as-is |
| Data-quality states | `contracts.quality.Quality` / `contracts.enums.QualityState` | none — reused as-is (see §9) |
| Deterministic ID pattern (UUIDv5 over a sorted-key JSON identity dict) | `contracts.identifiers.deterministic_observation_id` | `metrics/identifiers.py` mirrors the pattern with a metrics-specific namespace UUID (Phase 1 observation IDs and Phase 2A metric IDs must never collide or be mistaken for one another) |
| Structured diagnostics with a stable sort key | `evidence.bars.BarSeriesDiagnostic` / `adapters.diagnostics.NormalizationDiagnostic` | `metrics/diagnostics.py` — `MetricDiagnostic` model + `MetricDiagnosticCode` enum, same shape and sorting convention |

**Why not reuse the `Observation` model with `event_type=DERIVED_INDICATOR` directly as the
result type.** `contracts/payloads.py` already defines `DerivedIndicatorPayload` and the contract
already binds it to `EventType.DERIVED_INDICATOR` / `ObservationKind.DERIVED` /
`DataFreshness.DERIVED`, but nothing in `src/` constructs one yet. It was tempting to emit Phase
2A results as `Observation`s outright. We did not, for two reasons documented in
`docs/adr/0029-derived-metrics-are-not-provider-observations.md`: (1) `DerivedIndicatorPayload`
collapses to a single opaque `result: Decimal | str | bool | None`, which cannot carry
metric-specific structure (window definition, sample counts, price-field policy, input bar
boundaries) without stuffing it all into an untyped `parameters: dict[str, Any]` — the same
untyped-metadata pattern already flagged as a Phase 1H compromise; (2) `Observation` is,
throughout this codebase, a *provider evidence record* — reusing it for a locally computed value
risks exactly the confusion `field-semantics.md` warns against. Instead, `metrics/models.py`
defines a dedicated, explicitly-typed, frozen `MetricResult` model. It still **integrates
cleanly** with existing conventions: it serializes through the same `canonical_json_bytes` /
`canonical_hash` functions (which already handle arbitrary Pydantic models), it embeds the
existing `Quality` model verbatim, and its `input_observation_ids` field points back at real
Phase 1H `Observation.observation_id` values, so provenance remains traceable without a second
observation framework.

## 3. Metric identity and versioning

Every `MetricResult` carries:

- `metric_name: MetricName` — one of `ABSOLUTE_RETURN`, `PERCENTAGE_RETURN`,
  `ABSOLUTE_SESSION_GAP`, `PERCENTAGE_SESSION_GAP`, `ABSOLUTE_BAR_RANGE`, `PERCENTAGE_BAR_RANGE`,
  `MEAN_VOLUME_BASELINE`.
- `metric_version: str` — the formula/contract version, e.g. `"1.0.0"`. A breaking change to a
  formula's semantics (not its implementation) requires a new version string; old versions are
  never mutated in place.
- `calculation_policy_version: str` — the *selection policy* version (price-field default,
  denominator choice, current-bar exclusion default, etc.), independent of `metric_version`
  because the same formula can be run under different explicit policies. E.g.
  `"close_to_close.v1"`, `"low_denominator_range.v1"`, `"trailing_mean_exclude_current.v1"`.
- `symbol`, `asset_class`, `as_of`, `source_interval` (`BarInterval`), `session_scope`
  (`tuple[BarSession, ...]`, explicit — empty tuple means "no session filter was requested",
  which is itself an explicit, recorded choice, not an implicit default), `provider_scope`
  (`ProviderScopeMode`), `provider` (`str | None`, required when
  `provider_scope is SINGLE_PROVIDER` and more than one provider is present in eligible input).

All of the above participate in the deterministic identity (§7); none is optional metadata.

## 4. Result model (`metrics/models.py`)

```python
class MetricResult(BaseModel):  # frozen, extra="forbid"
    metric_name: MetricName
    metric_version: str
    calculation_policy_version: str
    symbol: str
    asset_class: AssetClass
    as_of: datetime
    source_interval: BarInterval
    session_scope: tuple[BarSession, ...]
    provider_scope: ProviderScopeMode
    provider: str | None
    price_field: PriceField | None          # returns/gaps/ranges only
    window: TrailingWindow | None           # volume baseline only
    value: Decimal | None                   # None iff quality.state is not KNOWN_VALUE
    unit: MetricUnit
    input_observation_ids: tuple[str, ...]  # sorted, deterministic order — see §7
    input_bar_boundaries: tuple[BarBoundaryRef, ...]
    sample_counts: SampleCounts | None      # volume baseline only
    quality: Quality                        # contracts.quality.Quality, reused verbatim
    diagnostics: tuple[MetricDiagnostic, ...]
    deterministic_id: str
```

`BarBoundaryRef` = `{bar_start: datetime, bar_end: datetime, observation_id: str}`, one entry per
bar that contributed to `value`. `SampleCounts` = `{requested, eligible, used, missing}` (all
`int`), populated only for the volume baseline (§10.7); `None` elsewhere because "requested vs.
used vs. missing" has no meaning for a two-bar return.

A missing value is represented as `value=None`, never `Decimal("0")` — enforced by a
`model_validator` that requires `value is None` exactly when `quality.state is not
QualityState.KNOWN_VALUE`, mirroring the model-level guarantee `Quality` already makes ("a reason
is required for a non-known quality state").

## 5. Selection (`metrics/selection.py`) — kept separate from calculation

Selection answers "which bar(s), exactly" before any arithmetic runs. It has two entry points,
both consuming the output of `evidence.bars.build_bar_series` (which already performs symbol,
interval, session, and point-in-time filtering with deterministic ordering — see
`docs/market-bar-availability-semantics.md` and ADR 0023/0024/0025):

1. **`resolve_bar_at_boundary(series, bar_start, bar_end, *, provider, require_completed) ->
   BoundaryResolution`** — used by returns (start bar, end bar), ranges (one bar), and gaps
   (prior-close bar, current-open bar). Groups the series' observations that share the requested
   `(bar_start, bar_end)` boundary, resolves competing revisions via the same
   `parent_observation_ids` / `supersedes_provider_record_id` linkage `evidence.bars` already
   establishes, and returns the single latest-eligible-as-of-`as_of` version, or a diagnostic
   explaining why none qualifies (no bar at that boundary, still partial, cancelled, ambiguous
   provider, ambiguous unresolved conflict).
2. **`resolve_trailing_window(series, target_bar_start, window, *, provider) ->
   WindowResolution`** — used by the volume baseline. Walks eligible, lifecycle-resolved,
   completed/corrected bars strictly ordered by `bar_start` descending from (but, per
   `exclude_current_bar`, not including) `target_bar_start`, collecting up to
   `window.requested_count` samples, and reports `SampleCounts`.

**Provider scope** (§14 of the handoff) is resolved first, before any boundary grouping: if
`provider_scope is SINGLE_PROVIDER` and `provider` is not explicitly given, the selector checks
how many distinct `provenance.provider_metadata["provider"]` values are present among the
point-in-time-eligible candidates for the requested boundary/window. Exactly one -> proceed
implicitly (not ambiguous, nothing to choose between). More than one -> `METRIC_AMBIGUOUS_PROVIDER`
diagnostic, `quality.state = UNAVAILABLE`, no value computed, no provider chosen, no average
taken. `EXPLICIT_PROVIDER_SET_PRESERVED_SEPARATELY` is defined as an enum value for forward
compatibility but is **not implemented** in Phase 2A (no metric currently needs to report
per-provider parallel results) — using it raises `NotImplementedError` with a clear message
rather than silently behaving like `SINGLE_PROVIDER`.

**Lifecycle resolution** (§13 of the handoff): among same-boundary, same-provider candidates,
the latest version is the one whose `revision_number` (from
`provenance.provider_metadata["revision_number"]`) is highest among observations eligible as of
`as_of` (i.e. `source_timestamp <= as_of`, `received_timestamp <= as_of`,
`effective_timestamp <= as_of` — already enforced by `build_bar_series`). This guarantees:
recalculating the same metric at an earlier `as_of` can only see revisions available by then;
recalculating at a later `as_of` may see a correction or cancellation that was not yet available
earlier; a previously computed and serialized `MetricResult` is never mutated (Phase 2A raw
inputs and calculation are both pure functions of `(observations, as_of, spec)` — same inputs
always produce byte-identical output, run once or run a hundred times, exactly per the repo's
existing replay-determinism guarantee).

- If the resolved latest version's `status` is `PARTIAL`: for metrics that require a completed
  bar (all range metrics, and returns/gaps under the default `close_to_close.v1` policy which
  reads `close` — a field a partial bar also has, but whose value is not yet final), this is
  `METRIC_PARTIAL_INPUT` / `RANGE_PARTIAL_BAR_UNSUPPORTED`, quality `UNAVAILABLE`.
- If `status` is `CANCELLED`: `METRIC_CANCELLED_INPUT` / `CANCELLED_INPUT` diagnostic, quality
  `UNAVAILABLE`. A cancellation is never silently treated as "no bar exists" (which would let an
  earlier, stale partial/completed version leak back in) nor as a usable zero-valued bar.
- If `status` is `COMPLETED` or `CORRECTED`: usable.
- Same-boundary, same-provider, *non-revision-linked* conflicting records (already flagged
  `BAR_CONFLICTING_RECORD` / `Quality.state=CONFLICTED` by the Phase 1H normalizer) propagate as
  `METRIC_CONFLICTED_INPUT`, quality `CONFLICTED` — no winner is picked at the metrics layer
  either.

No forward-fill, backfill, interpolation, or bar synthesis exists anywhere in `metrics/`.

## 6. No-look-ahead enforcement

No-look-ahead is enforced structurally, not by convention:

- All bar candidates first pass through `evidence.bars.build_bar_series`, which already rejects
  any observation with `source_timestamp > as_of`, `received_timestamp > as_of`, or
  `effective_timestamp > as_of` (ADR 0023). `metrics/selection.py` never bypasses this — it has
  no direct access to raw un-filtered observations; every selector takes a `BarSeries` (or the
  policy needed to build one) as input, never a bare observation list plus a separately-applied
  `as_of`.
- Lifecycle resolution (§5) additionally guarantees a correction/cancellation participates only
  once its own `source_timestamp`/`received_timestamp`/`effective_timestamp` are `<= as_of` —
  it is just another observation subject to the same `build_bar_series` filter, not a
  special-cased override.
- The trailing volume-window selector only walks bars with `bar_start` strictly before the
  target bar's `bar_start` (or `<=` only when `exclude_current_bar=False` is explicitly
  requested) — it can never pull a bar whose boundary is in the future relative to the target,
  independent of `as_of`.
- `tests/metrics/test_point_in_time.py` (§ test plan) directly tests all ten point-in-time
  scenarios enumerated in handoff §27, including that a later-arriving correction/cancellation
  never changes a `MetricResult` already computed at an earlier `as_of` (byte-identical
  re-serialization).

## 7. Deterministic identity (`metrics/identifiers.py`)

```python
METRIC_NAMESPACE = UUID("...")  # a fresh, fixed literal distinct from OBSERVATION_NAMESPACE

def deterministic_metric_id(identity: dict[str, Any]) -> str:
    encoded = json.dumps(identity, sort_keys=True, separators=(",", ":"),
                          ensure_ascii=False, default=_identity_default)
    return str(uuid5(METRIC_NAMESPACE, encoded))
```

reusing the same `_identity_default` shape (datetime/date -> isoformat, Decimal -> str, Enum ->
`.value`) as `contracts/identifiers.py`, duplicated rather than imported because
`contracts.identifiers` is intentionally a leaf module with no reason to import a sibling
`metrics` package, and the encoding rule is a two-line pure function — extracting a shared helper
for two call sites is deferred (matches the Phase 1 audit's own stance on speculative
abstraction, `phase-1-known-limitations.md` fixture/architecture notes).

The identity dict hashed is **every field that affects the result**: `metric_name,
metric_version, calculation_policy_version, symbol, asset_class, as_of, source_interval,
session_scope, provider_scope, provider, price_field, window, input_observation_ids` (sorted),
`input_bar_boundaries` (sorted by `(bar_start, bar_end, observation_id)`). `value` and
`diagnostics` are deliberately **excluded** from the identity — two computations with identical
inputs and policy always produce the identical ID (so a caller can check "did I already compute
this" before running the arithmetic), and the ID does not change if a formula bug fix changes
`value` under an unchanged `metric_version` (that scenario should bump `metric_version` instead,
per §3 — the ID staying stable when it shouldn't is a signal to look at versioning, not a
justification for including `value` in the hash).

`input_observation_ids` are sorted lexicographically before both hashing and serialization —
this, plus `build_bar_series`'s already-deterministic ordering, is what makes reordering the
input fixture file a no-op for the result (test case 24/"deterministic input reordering" in
several of the required case lists).

## 8. Serialization

`MetricResult` is a frozen Pydantic `BaseModel`; `canonicalize()` in
`serialization/canonical_json.py` already handles arbitrary `BaseModel` instances (including
nested ones) via `model_dump(mode="python")`, so `canonical_json_bytes(result)` and
`canonical_hash(result)` work unmodified — no new serialization code is needed, only new
call sites in `metrics/serialization.py` (`serialize_metric_result`, `deserialize_metric_result`,
mirroring `serialize_observation`/`deserialize_observation`) and in the CLI. Decimal formatting
(exact, no scientific notation, trailing zeros stripped, `"0"` for zero), datetime formatting
(UTC, `%Y-%m-%dT%H:%M:%S.%fZ`), and key ordering (`sort_keys=True`) are all inherited as-is.

## 9. Quality and diagnostics

`quality: Quality` reuses `contracts.quality.Quality` verbatim (see repo convention rationale in
§2). Mapping from the handoff's suggested result-quality states (§20) to the existing
`QualityState` enum:

| Handoff state | `QualityState` used | When |
|---|---|---|
| VALID | `KNOWN_VALUE` | value computed, no unresolved issue |
| PARTIAL | `KNOWN_VALUE` with `completeness=Completeness.PARTIAL` | volume baseline computed below `requested_count` but at/above `minimum_samples` |
| UNAVAILABLE | `UNAVAILABLE` | missing input, insufficient history, ambiguous provider, incompatible scope |
| INVALID | `INVALID` | zero/invalid denominator, invalid OHLC, invalid request shape |
| CONFLICTED | `CONFLICTED` | unresolved same-boundary conflicting bars |
| UNKNOWN | not modeled separately — `UNAVAILABLE` with reason `METRIC_UNKNOWN_AVAILABILITY` is used instead, since `QualityState` has no bare `UNKNOWN` and inventing a metrics-only quality enum would break the "reuse an existing quality model" instruction (handoff §20) | source bar publication/receipt timing itself could not be established |

`diagnostics: tuple[MetricDiagnostic, ...]` — `MetricDiagnostic = {code: MetricDiagnosticCode,
severity: DiagnosticSeverity, message: str, observation_ids: tuple[str, ...]}`, reusing
`adapters.diagnostics.DiagnosticSeverity` (`INFO/WARNING/ERROR`) rather than inventing a fourth
severity enum. `MetricDiagnosticCode` (`metrics/diagnostics.py`) implements the general and
per-metric-family codes from handoff §21 that Phase 2A actually emits (documented exhaustively
in `docs/foundational-market-metric-contract.md`; codes listed in the handoff but never emitted
by any implemented policy — e.g. codes for window types not built in Phase 2A — are not defined,
to avoid dead enum members). Diagnostics are sorted deterministically by
`(code.value, observation_ids, message)`, matching the `_sorted_diagnostics` /
`BarSeriesDiagnostic` sort convention exactly.

## 10. Price-field, denominator, and window policy (summary — full formulas in §10 of the task
and in the per-metric semantics docs)

- **Price field**: `PriceField.OPEN/HIGH/LOW/CLOSE`. Returns and gaps default to `CLOSE` (documented
  policy `close_to_close.v1`); only fields present on `BarPayload` are supported — no adjusted
  close, no VWAP-as-price, because Phase 1H does not define an adjustment policy.
- **Range denominator**: `low` of the same completed bar (`policy
  low_denominator_range.v1`) — chosen because `low` is always `<= open/close` for a valid bar and
  is never zero-forced (`BarPayload` requires `low > 0`), giving the smallest defensible
  denominator without inventing a mid-price. Documented and versioned per handoff §10.6; an
  alternative denominator would be a new, separately versioned policy, not a silent change.
- **Volume baseline window**: `BAR_COUNT` only in Phase 2A (`TIME_RANGE`/`SESSION_COUNT` are
  named in `metrics/models.py:WindowType` for forward compatibility but unimplemented — using
  them raises `NotImplementedError`). Trailing, current-bar-excluded by default
  (`exclude_current_bar=True`), arithmetic mean, zero-volume bars retained as valid `0` samples,
  `None`-volume bars excluded and separately counted (`missing`), never counted as `0`.

## 11. Explicitly excluded (unchanged from handoff §11/§38 — restated for completeness)

Relative volume, volume ratio/z-score/acceleration, dollar volume, turnover, rolling return,
momentum score, rate-of-change, ATR, true range, standard deviation, volatility score, RSI,
MACD, moving averages (simple/exponential), Bollinger Bands, Keltner Channels, TTM Squeeze,
breakout/trend/gap classification/gap-fill, candlestick patterns, order-flow/aggressor-side
metrics, candidate score/rank/Prime-Subprime/recommendation/entry/exit/target/stop/backtesting,
any live/network/database/GUI/ML code. Verified absent in §"Isolation checks" of the test plan
and the completion report.

## 12. Inherited-formula disposition (from archived-repo research)

| Inherited formula | Source | Disposition in Phase 2A |
|---|---|---|
| `change_from_close` percentage-change | `filters.py` (both archived repos) | Reused *shape* only (`(end-start)/start*100`); rebuilt from scratch in exact `Decimal` with an explicit zero-denominator diagnostic instead of the original's silent `'0'` string return |
| IB/Schwab `change_percent` | `ib_api.py:489`, `schwab_api.py:330` | Same formula shape; the original's look-ahead risk (comparing a possibly-partial live tick to a bar-derived prior close with no cross-validation) is closed by Phase 2A's explicit point-in-time + completed-bar-only selection |
| Finviz `Gap` column | provider CSV export | Not reusable — opaque provider-computed field, no local formula existed to inherit. Phase 2A's `absolute/percentage_session_gap` is a new, explicit, caller-supplied-boundary implementation |
| `classify_squeeze(open_price, high_price)` | `Formula_logger.py:33-52` | Rejected — mislabeled parameter (actually prior close), and look-ahead prone (uses same-session running high); not reused in any form; also out of scope as a classification |
| True Range / ATR | `technical_indicators.py:44-55` | Formula noted as correct in isolation but **out of Phase 2A scope** (feeds excluded TTM Squeeze); Phase 2A's bar range is a simpler `high-low` on one bar, not True Range across two bars |
| IB/Schwab relative volume | `ib_api.py:495-499`, `schwab_api.py:332-333` | **Not implemented** — relative volume is explicitly excluded from Phase 2A (handoff §11); the volume *baseline* half (denominator only) is implemented, its numerator-comparison half is deferred to Phase 2B by design |
| IB/Schwab average-volume baseline (`statistics.mean(volumes[:-1])`, ~30-day window) | `ib_api.py:643`, `schwab_api.py:278` | Formula shape (arithmetic mean, current-bar excluded) is reused; the inherited version's lack of a minimum-sample floor and lack of RTH-consistency guarantee across providers is fixed by Phase 2A's explicit `minimum_samples`, `SampleCounts`, and `SINGLE_PROVIDER` default |
| RSI(14), weekly volatility, days-to-cover, short-float%, TTM fire detection, Squeeze Score, Prime/Subprime, target/stop | various | Out of Phase 2A scope entirely (indicators/scoring/ranking, per handoff §11/§38) |

Full findings with file:line citations are preserved in this design doc's git history (research
was conducted read-only against the archived repositories; no archived file was modified).

## 13. Compatibility guarantee

`metrics/` imports from `evidence` and `contracts`/`serialization` but nothing in `evidence`,
`contracts`, `adapters`, or `replay` imports from `metrics` — a strictly one-directional
dependency. No existing file is modified by Phase 2A except additive `__main__.py` CLI
subcommand registration (new `elif` branches only) and additive documentation. Schema version
`1.0.0` is unchanged; no `Observation`, `Payload`, or fixture byte is touched; all Phase 1
anchors in `tests/fixtures/compatibility/phase_1_anchor_manifest.json` remain byte-identical.
