# Phase 2C Design Specification: Short-Interest and Borrow-Pressure Metrics

## 1. Purpose and boundary

Phase 1D (`PUBLISHED_SHORT_INTEREST`, FINRA-shaped) and Phase 1B (`BORROW_FEE`/
`BORROW_AVAILABILITY`, IBKR-shaped) established objective, point-in-time evidence for
published short interest and stock-loan pressure. Phase 2A/2B added foundational and
normalized *market-activity* metrics from `MARKET_BARS` only. Phase 2C is the next,
independent layer: deterministic, objective, **descriptive** comparisons over the two
domains Phase 2A/2B never touch, plus one cross-domain metric (days to cover) that
combines a Phase 1D short-interest observation with a Phase 2A `MEAN_VOLUME_BASELINE`.

- **In scope**: `PUBLISHED_SHORT_INTEREST_ABSOLUTE_CHANGE`,
  `PUBLISHED_SHORT_INTEREST_PERCENTAGE_CHANGE`, `PUBLISHED_SHORT_INTEREST_REVISION_DELTA`,
  `DAYS_TO_COVER_COMPONENTS`, `DAYS_TO_COVER`, `BORROW_FEE_ABSOLUTE_CHANGE`,
  `BORROW_FEE_RELATIVE_PERCENTAGE_CHANGE`, `BORROW_AVAILABILITY_ABSOLUTE_CHANGE`,
  `BORROW_AVAILABILITY_PERCENTAGE_CHANGE`.
- **Out of scope**: everything named in handoff §11/§37 — short-float recalculation,
  synthetic/estimated short interest, fail-to-deliver, options analytics, any
  hard-to-borrow/pressure/squeeze score, candidate rank, Prime/Subprime, recommendation,
  alert, threshold classification, backtesting, live integration, deployment, GUI,
  database, paper/live trading, ML. A Phase 2C result states a magnitude and a direction
  of change; it never states whether that change is "high," "tightening," or
  "squeeze-ready." Enforced structurally (§14, isolation tests) exactly as Phase 2A/2B are.

## 2. Architectural placement

Seven new modules inside the existing `src/squeeze_core/metrics/` package (a peer of
Phase 2A/2B's own files, following the same "new module per concern" convention):

| File | Purpose |
|---|---|
| `source_age.py` | `SourceAgeMetadata` (new, standalone frozen model) + `build_source_age` helper computing it from one `Observation` and an `as_of`. |
| `pressure_models.py` | `PressureMetricResult` (new, standalone frozen model — **not** `MetricResult`, **not** `NormalizedMetricResult`), `DaysToCoverComponents` (new, standalone frozen model with no scalar `value`), enums (`PressureUnit` additions live on the existing `MetricUnit`, not a new enum — see §9). |
| `pressure_identifiers.py` | `pressure_metric_identity()` / `deterministic_pressure_metric_id()` and `days_to_cover_components_identity()` / `deterministic_days_to_cover_components_id()`, reusing `metrics/identifiers.py`'s existing generic `deterministic_metric_id(identity: dict) -> str` function and the existing `METRIC_NAMESPACE` UUID directly (no new namespace — see §6). |
| `pressure_selection.py` | Point-in-time eligibility, lifecycle resolution, and conflict/cancellation handling for `PUBLISHED_SHORT_INTEREST`, `BORROW_FEE`, and `BORROW_AVAILABILITY` observations — the domain-specific analogue of Phase 2A's `selection.py`, since that module is hard-wired to `MARKET_BARS`/`BarInterval` shapes and is not reusable as-is (confirmed by direct reading of `selection.py` and by both research passes; see §5). |
| `short_interest_changes.py` | `PUBLISHED_SHORT_INTEREST_ABSOLUTE_CHANGE`, `PUBLISHED_SHORT_INTEREST_PERCENTAGE_CHANGE`, `PUBLISHED_SHORT_INTEREST_REVISION_DELTA`. |
| `days_to_cover.py` | `DAYS_TO_COVER_COMPONENTS`, `DAYS_TO_COVER` — combines `pressure_selection`'s short-interest resolver with Phase 2A's `selection.resolve_trailing_window` + `volume_baselines.compute_mean_volume` (reused directly, not `build_volume_baseline_result` wholesale — see §8.3 for why). |
| `borrow_fee_changes.py` / `borrow_availability_changes.py` | `BORROW_FEE_ABSOLUTE_CHANGE`/`BORROW_FEE_RELATIVE_PERCENTAGE_CHANGE` and `BORROW_AVAILABILITY_ABSOLUTE_CHANGE`/`BORROW_AVAILABILITY_PERCENTAGE_CHANGE` respectively. |

`metrics/models.py` and `metrics/diagnostics.py` receive **additive-only** changes (new
`MetricName`/`MetricUnit`/`MetricDiagnosticCode` members, §6/§9/§13); `metrics/registry.py`
receives nine new dispatch branches; `metrics/__init__.py` exports the new public names.
No existing Phase 1/2A/2B file's *behavior* changes for any Phase 1/2A/2B-shaped request
(proven in §15/compatibility tests).

**Why not extend `MetricResult`.** Confirmed directly (`metrics/models.py:112-134`):
`MetricResult.source_interval: BarInterval` is a required, non-optional field with no
default. Every Phase 2C metric except `DAYS_TO_COVER` has no bar interval at all (published
short interest and borrow observations are not bar-shaped), so `MetricResult` cannot
represent them without a fabricated placeholder interval — exactly the kind of "stuffing
unrelated concepts into one model" the Phase 2A design doc's own `DerivedIndicatorPayload`
rejection (ADR 0029) already warned against. `canonical_json.canonicalize()` also serializes
every field of a Pydantic model unconditionally (`model_dump(mode="python")`, no
`exclude_defaults`), so any field added to `MetricResult` would change the canonical bytes,
and therefore the hash, of every already-anchored Phase 2A/2B result — unacceptable per
handoff §32/§40. Phase 2C therefore defines its own `PressureMetricResult`, mirroring
exactly the precedent Phase 2B set with `NormalizedMetricResult` (`docs/phase-2b-design.md`
§2): a wholly separate frozen model, not a variant of an existing one.

**Why not extend `NormalizedMetricResult` either.** That model's identity and fields
(`standard_deviation_policy`, `target_boundary: BarBoundaryRef | None`, `window: TrailingWindow
| ReturnCountWindow | None`) are shaped around a target-vs-baseline-distribution comparison
over bars/returns — Phase 2C's comparisons are a two-sided *point-in-time record* diff
(starting observation vs. ending observation), a structurally different shape (§7). Reusing
it would either leave most of its fields permanently `None` (a code smell already avoided
elsewhere in this codebase) or require widening its meaning past what it was anchored for.

## 3. Two domains, two selection problems, one shared pattern

Both `PublishedShortInterestPayload` and the borrow payloads are point *observations* over
time, not a `BarSeries`. Confirmed directly against the FINRA and IBKR normalizers
(`src/squeeze_core/adapters/finra/normalizer.py`, `src/squeeze_core/adapters/ibkr/normalizer.py`):

- **Published short interest** (FINRA) has a genuine *lifecycle*: a settlement period
  (`payload.settlement_date`) can have an `ORIGINAL` record, then zero or more
  `CORRECTED`/`REVISED` records linked via `Observation.parent_observation_ids` (populated
  from `supersedes_source_record_id` in a second normalization pass), or a `CANCELLED`
  record (still a full `Observation`, `Quality.state=UNAVAILABLE`, reason `"provider record
  is cancelled"` — never a deleted/absent record). Unlinked same-period conflicting records
  are marked `Quality.state=CONFLICTED`. `source_timestamp` is the publication-availability
  boundary (ADR 0011); `effective_timestamp = max(publication, received_timestamp)`;
  `received_timestamp` is local receipt. All three gate eligibility (ADR 0011/0012,
  `docs/published-short-interest-semantics.md`).
- **Borrow fee / borrow availability** (IBKR) have **no lifecycle at all** — no
  `supersedes`/`revision_number` concept exists on `IbkrBorrowRecord`. Fee and availability
  are two independent `Observation`s per input row (`event_type=BORROW_FEE` /
  `BORROW_AVAILABILITY`), each a simple point sample at `effective_timestamp ==
  source_timestamp`. Only duplicate/conflict detection exists (grouped by `(event_type,
  symbol, effective_timestamp)`; differing payloads within a group are marked
  `Quality.state=CONFLICTED`, no winner selected).

`pressure_selection.py` therefore has two resolver families sharing one eligibility gate
and one conflict-handling shape, mirroring `metrics/selection.py`'s own internal shape
(`_group_by_boundary` / `_resolve_group`) without depending on any of its bar-specific
helpers:

```python
@dataclass(frozen=True)
class PressureSelectionRequest:
    symbol: str
    as_of: datetime
    provider: str          # explicit and required for every Phase 2C metric (§11) --
                            # never optional-with-ambiguity-detection like Phase 2A's bars

def _eligible(observations: Iterable[Observation], *, event_type: EventType,
              request: PressureSelectionRequest) -> tuple[Observation, ...]:
    """symbol + event_type + provider match, then source_timestamp <= as_of AND
    received_timestamp <= as_of AND effective_timestamp <= as_of -- the identical three-gate
    rule already documented for PUBLISHED_SHORT_INTEREST in
    docs/point-in-time-evidence-policy.md and applied uniformly to borrow observations (which
    have no separate publication/receipt distinction: source_timestamp == effective_timestamp
    for IBKR, so the gate degenerates to two equivalent checks plus received_timestamp, never
    fewer checks)."""
```

### 3.1 Short-interest resolution (`resolve_short_interest_at_period`)

Groups eligible `PUBLISHED_SHORT_INTEREST` observations for `(symbol, provider)` by
`payload.settlement_date` (the reporting period — the exact key FINRA's own normalizer
groups conflicts by, `normalizer.py:601-605`). Within the group at the requested period:

1. Any member with `Quality.state is CONFLICTED` → no winner, `SHORT_INTEREST_CONFLICTED_INPUT`.
2. Otherwise pick the member with the highest `(revision_number, effective_timestamp,
   observation_id)` — `revision_number` read from `provenance.provider_metadata`, mirroring
   `metrics/selection.py::bar_revision_number`'s exact tie-break tuple shape, `0` when absent.
3. If the chosen record's `provenance.provider_metadata["revision_status"] == "CANCELLED"` →
   `SHORT_INTEREST_CANCELLED_INPUT`, unavailable (never silently falls back to an earlier
   revision — a cancellation is itself the latest eligible fact).
4. If `Quality.state is MISSING` or `payload.short_shares is None` →
   `SHORT_INTEREST_MISSING_VALUE`, unavailable (missing is never coerced to `0`).
5. Otherwise usable: `payload.short_shares` (exact `int`) is the value.

No period in the group is ever synthesized, interpolated, or borrowed from an adjacent
period. `previous_short_shares`/`average_daily_volume` in `provenance.provider_metadata` are
**never** read as canonical evidence (confirmed unverified/provenance-only by direct read of
`normalizer.py:313-333`) — every comparison always independently resolves two full
observations through this same function.

### 3.2 Revision-delta resolution

`PUBLISHED_SHORT_INTEREST_REVISION_DELTA` calls §3.1 once for the requested period to get the
*latest eligible* record (`ending`), then follows `ending.parent_observation_ids[0]` (if
non-empty) to fetch the immediate prior record by `observation_id` directly from the supplied
observation set as `starting`. Both are subject to the identical eligibility gate — a parent
that somehow fails eligibility (defensive; should not occur since a revision cannot be
eligible before its own parent under any real publication order) produces
`SHORT_INTEREST_REVISION_LINK_MISSING`, same as an empty `parent_observation_ids`. Before a
revision is itself eligible, §3.1 simply resolves `ending` to the original record — which
then has no parent, so revision delta correctly reports "no revision available yet"
(`SHORT_INTEREST_REVISION_NOT_FOUND`) rather than fabricating a self-comparison. A
cancellation is never treated as a revision (§3.1 step 3 already stops it earlier, before any
parent-chasing).

### 3.3 Borrow resolution (`resolve_borrow_observation_at`)

For `event_type in {BORROW_FEE, BORROW_AVAILABILITY}`: groups eligible observations for
`(symbol, provider, event_type)` by `effective_timestamp` (the exact key IBKR's own
normalizer groups conflicts by, `normalizer.py:540-544`); the caller supplies an **explicit**
`effective_timestamp` boundary to select one observation (mirroring
`resolve_bar_at_boundary`'s exact-boundary-match shape, applied to a single timestamp instead
of a `(start, end)` pair, since a borrow observation has no duration). A `CONFLICTED` group at
that boundary → `BORROW_CONFLICTED_INPUT`, no winner. No revision/lifecycle concept exists to
resolve (§3), so there is no cancellation/correction branch here — only "found" / "not found
at that exact boundary" / "conflicted."

## 4. `SourceAgeMetadata` (`source_age.py`)

```python
class SourceAgeMetadata(BaseModel):  # frozen, extra="forbid"
    provider_publication_time: datetime          # observation.source_timestamp
    local_receipt_time: datetime                 # observation.received_timestamp
    effective_time: datetime                     # observation.effective_timestamp
    availability_age_seconds: int                # as_of - effective_time, >= 0 by construction (eligibility already enforced effective_time <= as_of)
    reporting_period_end: date | None = None     # payload.settlement_date; None for borrow (no reporting period concept)
    reporting_period_age_days: int | None = None # (as_of.date() - reporting_period_end).days; None for borrow
    publication_lag_seconds: int | None = None   # provider_publication_time - (reporting_period_end as UTC midnight); None for borrow
```

Two distinct age concepts are kept separate per handoff §16, never collapsed into one
generic "age": `availability_age_seconds` (evidence-freshness — how long ago did this
become usable) and `reporting_period_age_days` (report-staleness — how old is the fact
itself, independent of when we received it). `reporting_period_age_days` deliberately
reuses the exact name and semantics already established at
`squeeze_core.evidence.models.ObservationAge.reporting_period_age_days`
(`src/squeeze_core/evidence/models.py:227`) and the exact formula already used by
`evidence/builder.py:664-670` (`(policy.as_of.date() - settlement_date).days`) — not the
handoff's literal `reporting_period_age_seconds` suggestion, because this codebase already
has one established, tested convention for this concept and introducing a second,
differently-typed one for the same fact would be the kind of "two point-in-time policies"
duplication ADR 0030/the point-in-time-evidence-policy doc explicitly warns against. This is
a deliberate, documented deviation from the handoff's literal suggested field name,
permitted under handoff §36/§43 ("ordinary backward-compatible implementation decisions").
`availability_age_seconds`/`publication_lag_seconds` are kept in seconds (no established
prior-phase convention exists for those two, so the handoff's literal suggestion is used
as-is). `build_source_age(observation, as_of) -> SourceAgeMetadata` is the one function that
constructs this model; every Phase 2C selector calls it once per resolved observation side,
never recomputing ages inline.

## 5. `PressureMetricResult` (`pressure_models.py`)

```python
class PressureMetricResult(BaseModel):  # frozen, extra="forbid"
    metric_name: MetricName
    metric_version: str
    calculation_policy_version: str
    symbol: str
    asset_class: AssetClass
    as_of: datetime
    provider_scope: ProviderScopeMode          # always SINGLE_PROVIDER in Phase 2C (§11)
    provider: str | None                        # the domain-owning provider (short-interest or borrow)
    volume_provider: str | None = None          # DAYS_TO_COVER only -- the (separately explicit) volume provider
    starting_observation_id: str | None = None
    ending_observation_id: str | None = None
    starting_reporting_period: date | None = None    # PUBLISHED_SHORT_INTEREST_* only
    ending_reporting_period: date | None = None
    starting_source_age: SourceAgeMetadata | None = None
    ending_source_age: SourceAgeMetadata | None = None
    days_to_cover_components_id: str | None = None    # DAYS_TO_COVER only
    value: Decimal | None                        # None iff quality.state is not KNOWN_VALUE
    unit: MetricUnit
    input_observation_ids: tuple[str, ...] = ()   # sorted
    input_metric_ids: tuple[str, ...] = ()        # sorted; DAYS_TO_COVER's components id lives here too
    quality: Quality
    diagnostics: tuple[MetricDiagnostic, ...] = ()
    deterministic_id: str | None = None
```

One model serves every Phase 2C metric except the days-to-cover component breakdown (§8.2).
`starting_*`/`ending_*` fields are `None` together when a metric has no two-sided comparison
shape (there is none such in Phase 2C today, but the fields are independently nullable, not
coupled, for forward compatibility — mirrors `MetricResult`'s own "`None` where the concept
doesn't apply" convention). `value is None` exactly when `quality.state is not KNOWN_VALUE`,
identical validator shape to `MetricResult`/`NormalizedMetricResult`. No field named
`score`/`rank`/`recommendation`/`signal`/`pressure_level`/anything interpretive exists on
this model — enforced by the extended isolation test (§14).

## 6. `DaysToCoverComponents` (`pressure_models.py`)

```python
class DaysToCoverComponents(BaseModel):  # frozen, extra="forbid"
    component_version: str
    calculation_policy_version: str              # the denominator policy, §8.1
    symbol: str
    asset_class: AssetClass
    as_of: datetime
    short_interest_provider: str
    short_interest_observation_id: str
    short_interest_reporting_period: date
    short_interest_value: int                     # shares, exact int -- payload.short_shares verbatim
    short_interest_unit: MetricUnit                # SHARES
    short_interest_source_age: SourceAgeMetadata
    volume_provider: str
    volume_baseline_metric_id: str                 # deterministic_id of the MEAN_VOLUME_BASELINE MetricResult
    volume_baseline_value: Decimal | None
    volume_unit: MetricUnit                        # SHARES
    volume_interval: BarInterval
    volume_session_scope: tuple[BarSession, ...]
    volume_window: TrailingWindow
    volume_sample_counts: SampleCounts | None
    input_observation_ids: tuple[str, ...] = ()    # sorted; short-interest obs id + every volume sample id
    input_metric_ids: tuple[str, ...] = ()          # sorted; contains volume_baseline_metric_id
    quality: Quality
    diagnostics: tuple[MetricDiagnostic, ...] = ()
    deterministic_id: str | None = None
```

No `value` field — per handoff §10.4, this is a structured, auditable breakdown, not a
scalar result. `DAYS_TO_COVER` (§8.4) is the `PressureMetricResult` that reads this
component's numerator/denominator and divides them, recording
`days_to_cover_components_id = components.deterministic_id`.

## 7. Deterministic identity (`pressure_identifiers.py`)

Reuses `metrics/identifiers.py`'s existing `METRIC_NAMESPACE` UUID and its existing generic
`deterministic_metric_id(identity: dict) -> str` function directly — **no new namespace and
no reimplemented UUID5/JSON-encoding logic**, an even more direct form of reuse than Phase 2B
took (Phase 2B duplicated the two-line encoding helper into `normalized_identifiers.py`
rather than importing it; `pressure_identifiers.py` imports `deterministic_metric_id` and
`_identity_default`'s behavior transitively since `deterministic_metric_id` already handles
`datetime`/`date`/`Decimal`/`Enum` values). Two identity-dict builders:

- `pressure_metric_identity(result: PressureMetricResult) -> dict` — every field except
  `value`, `diagnostics`, `deterministic_id`.
- `days_to_cover_components_identity(components: DaysToCoverComponents) -> dict` — every
  field except `diagnostics`, `deterministic_id` (no `value` to exclude).

Both dict shapes are structurally distinct from each other, from Phase 2A's `MetricResult`
identity (`metric_identity()`), and from Phase 2B's two identity shapes
(`baseline_identity()`/`normalized_metric_identity()`) — none share the same key set, so an
accidental cross-model ID collision under the shared namespace remains cryptographically
negligible and is verified absent by the anchor cross-collision test (§ test plan, mirroring
Phase 2B's `test_no_unexplained_anchor_collisions`). An unavailable result still gets a
stable, request-derived ID (`value`/`diagnostics` excluded from the hash), so re-running an
unavailable request twice is idempotent, and two different unavailable *reasons* for the same
request shape are only expected to collide when every non-`diagnostics` field is genuinely
identical (verified, not assumed, per handoff §19).

## 8. Metric contracts

All Phase 2C metrics use `metric_version = "1.0.0"` (first release).

### 8.1 Published short-interest absolute / percentage change

`calculation_policy_version = "explicit_reporting_period_pair.v1"`. Caller supplies
`symbol, asset_class, as_of, provider, starting_reporting_period, ending_reporting_period`
(both settlement dates, explicit — never an inferred "nearest" period, per handoff §15).
`starting_reporting_period == ending_reporting_period` is rejected before any resolution
(`PRESSURE_METRIC_IDENTICAL_INPUT`); `starting > ending` is rejected
(`PRESSURE_METRIC_START_AFTER_END`, periods must be supplied in chronological order — the
handoff never asks for a signed/auto-ordered diff). Both periods resolved via §3.1 against
the *same* `PressureSelectionRequest` (same provider, so cross-provider mixing is
structurally impossible — one shared request threads through both resolutions, mirroring
Phase 2B's own "one `MetricSelectionRequest` per call" discipline, §10 of `phase-2b-design.md`).

- **Absolute**: `value = ending.short_shares - starting.short_shares`, `unit = SHARES`.
- **Percentage**: `value = (ending.short_shares - starting.short_shares) /
  starting.short_shares * 100`, `unit = PERCENT`; `starting.short_shares == 0` →
  `SHORT_INTEREST_ZERO_START_DENOMINATOR`, `quality.state = INVALID` (zero is a valid
  absolute-change input but never a valid percentage-change denominator, per handoff §10.2).
- Either side missing/cancelled/conflicted → the corresponding §3.1 diagnostic, `quality.state
  = UNAVAILABLE` (missing) or `CONFLICTED`/`INVALID` as appropriate; **no directional
  interpretation is ever attached to the sign of `value`.**
- Exact `Decimal` arithmetic (`short_shares` is `int`; promoted to `Decimal` before division,
  `localcontext(prec=28)` matching Phase 2A's own precision guard).

### 8.2 Published short-interest revision delta

`calculation_policy_version = "explicit_revision_link.v1"`. Caller supplies `symbol,
asset_class, as_of, provider, reporting_period` (one period, not two — the "starting"/"ending"
sides are the original and its latest eligible revision of that *same* period, resolved per
§3.2, not two caller-chosen periods). `value = revision.short_shares -
original.short_shares`, `unit = SHARES`. A cancellation is never a revision (§3.1 already
routes it to `SHORT_INTEREST_CANCELLED_INPUT` before revision-chasing runs). A duplicate
(unlinked, non-conflicting identical payload) is never treated as a revision either — it
cannot occur here by construction, since §3.1's group-resolution only ever returns the single
highest-`(revision_number, effective_timestamp, observation_id)` record for a period; a true
duplicate has identical `revision_number` and is disambiguated by `observation_id` only,
never surfaced as a "revision."

### 8.3 Days-to-cover components and ratio — denominator policy

`calculation_policy_version =
"published_short_interest_divided_by_trailing_mean_completed_daily_share_volume.v1"` for both
`DAYS_TO_COVER_COMPONENTS` and `DAYS_TO_COVER` (one policy governs the whole calculation, not
two independently-versioned halves). Caller supplies `symbol, asset_class, as_of,
short_interest_provider, short_interest_reporting_period, volume_provider, volume_interval
(must be the daily bar interval -- any other interval is rejected before resolution with
DAYS_TO_COVER_INCOMPATIBLE_VOLUME_INTERVAL, closing the "do not silently use intraday
volume" requirement structurally), volume_session_scope, volume_window (TrailingWindow)`.

**Numerator**: the short-interest observation resolved via §3.1 at
`short_interest_reporting_period` for `short_interest_provider`. `short_interest_value =
payload.short_shares` (exact `int`, in `SHARES`); its `SourceAgeMetadata` is recorded in full
(`short_interest_source_age`), so a stale numerator is always visible, never silently treated
as fresh (handoff §16/§17) and never treated as *unavailable* merely because it is old (age is
metadata, not a gate — no staleness threshold is invented here, per handoff §16's explicit
prohibition on inventing arbitrary freshness thresholds).

**Denominator**: `selection.resolve_trailing_window` (Phase 2A, imported and called
directly) walking backward from `target_start = as_of` over `MARKET_BARS` observations for
`volume_provider`/`volume_interval`/`volume_session_scope`, then `compute_mean_volume` (Phase
2A, imported and called directly) over the returned samples. **This does not call
`volume_baselines.build_volume_baseline_result` wholesale**, unlike Phase 2B's reuse pattern
— that function requires a concrete `target_bar_start`/`target_bar_end` pair to resolve a
"current bar" purely to exclude it from its own baseline and learn its volume unit (§8 of
`phase-2b-design.md`), a concept days-to-cover has no analogue for: there is no specific bar
"being measured" here, only "the trailing mean volume as of `as_of`." Requiring callers to
invent a synthetic target-bar boundary just to satisfy an unrelated API shape would be the
kind of accidental complexity the handoff's simplicity guidance warns against, and the
handoff's own §31 CLI example already omits a target-bar boundary from the `DAYS_TO_COVER`
request shape (only `volume_interval`/`volume_session`/`volume_window` appear). Calling
`resolve_trailing_window(target_start=as_of, window=..., target_volume_unit=None)` directly
is still full reuse of Phase 2A's *selection* (eligibility, lifecycle resolution, provider
ambiguity, current/future-bar exclusion via `exclude_current_bar=True`, missing-vs-zero-volume
handling) and of its *arithmetic* (`compute_mean_volume`) — only the unrelated "resolve one
named target bar" half is skipped, and this is documented here as a deliberate, narrower
composition than Phase 2B's, not a reimplementation of either function.

`DAYS_TO_COVER_COMPONENTS.volume_baseline_metric_id` is **not** produced by
`build_volume_baseline_result` (since that function is not called); instead
`days_to_cover.py` constructs one Phase 2A `MetricResult` with
`metric_name=MEAN_VOLUME_BASELINE` directly from the same `WindowResolution` (reusing
`volume_baselines.compute_mean_volume`'s output and `metrics/identifiers.py`'s existing
`deterministic_metric_id`/`metric_identity` unmodified) purely so a real, independently
verifiable Phase 2A metric ID is available to reference — this is a thin, additive
construction, not a second calculation path: the mean, sample counts, and quality are
computed exactly once and reused for both the `MetricResult`'s own fields and
`DaysToCoverComponents`' fields.

**Ratio**: `DAYS_TO_COVER.value = short_interest_value / volume_baseline_value`, `unit =
DAYS`. `volume_baseline_value` missing or `== 0` → `DAYS_TO_COVER_ZERO_VOLUME_BASELINE` /
`DAYS_TO_COVER_VOLUME_BASELINE_UNAVAILABLE`, `quality.state = INVALID`/`UNAVAILABLE`
respectively (division never proceeds). Short interest missing/cancelled/conflicted →
`DAYS_TO_COVER_SHORT_INTEREST_NOT_FOUND` plus the underlying §3.1 diagnostic, `UNAVAILABLE`.
`2.5` is documented (docs/days-to-cover-semantics.md) as "2.5 average daily-volume periods
under `published_short_interest_divided_by_trailing_mean_completed_daily_share_volume.v1`,"
never as a literal calendar-day forecast.

### 8.4 Borrow-fee absolute / relative-percentage change

`calculation_policy_version = "explicit_observation_pair.v1"`. Caller supplies `symbol,
asset_class, as_of, provider, starting_effective_timestamp, ending_effective_timestamp`, both
resolved via §3.3 against `event_type=BORROW_FEE`.

- **Absolute**: `value = ending.annualized_fee_percent - starting.annualized_fee_percent`,
  `unit = PERCENTAGE_POINTS` (never `PERCENT` — `BorrowFeePayload.annualized_fee_percent` is
  already stored in percentage-point units by the IBKR normalizer regardless of input unit,
  §1 finding; a difference of two percentage-point values is itself in percentage points, not
  a percentage-of-a-percentage).
- **Relative**: `value = (ending.annualized_fee_percent - starting.annualized_fee_percent) /
  starting.annualized_fee_percent * 100`, `unit = PERCENT`; `starting == 0` →
  `BORROW_FEE_ZERO_START_DENOMINATOR`, `INVALID` (an explicit zero starting fee is a valid
  absolute-change input but never a valid relative-change denominator — same asymmetry as
  §8.1). Missing fee on either side → `BORROW_FEE_MISSING_VALUE`, `UNAVAILABLE`. No
  hard-to-borrow classification is derived from the fee magnitude anywhere in this file.

### 8.5 Borrow-availability absolute / percentage change

Identical shape to §8.4 against `event_type=BORROW_AVAILABILITY` and
`payload.available_shares` (exact `int`). Absolute `unit = SHARES` (sign preserved — a
negative value is a legitimate, non-relabeled decrease); percentage `unit = PERCENT`,
`starting == 0` → `BORROW_AVAILABILITY_ZERO_START_DENOMINATOR`. `payload.hard_to_borrow` is
never read by this file — it is preserved only as raw evidence on the source `Observation`,
never consumed by any Phase 2C arithmetic or diagnostic.

## 9. Units

`MetricUnit` (existing `StrEnum`) gains two members — additive, existing members
(`PRICE, PERCENT, SHARES, UNKNOWN, RATIO, STANDARD_DEVIATIONS`) unchanged in value/meaning:

```python
PERCENTAGE_POINTS = "PERCENTAGE_POINTS"
DAYS = "DAYS"
```

No implicit conversion between `PERCENT`, `PERCENTAGE_POINTS`, `RATIO`, or a decimal fraction
ever occurs anywhere in Phase 2C code — every formula in §8 states its unit explicitly, and
`BORROW_FEE_ABSOLUTE_CHANGE`/`BORROW_FEE_RELATIVE_PERCENTAGE_CHANGE` are the two metrics that
most directly enforce the handoff's "never call percentage-point change a percentage change"
requirement (§8.4) by construction (two different `MetricUnit` values, two different metric
names, never one metric with a unit flag).

## 10. Missing, zero, cancelled, and conflicted semantics

| Situation | `value` | `quality.state` | Diagnostic |
|---|---|---|---|
| Requested period/boundary has no eligible record | `None` | `UNAVAILABLE` | `SHORT_INTEREST_START_NOT_FOUND` / `_END_NOT_FOUND` / `BORROW_FEE_START_NOT_FOUND` / etc. |
| Resolved record is `CANCELLED` (short interest only) | `None` | `UNAVAILABLE` | `SHORT_INTEREST_CANCELLED_INPUT` |
| Resolved record group is `CONFLICTED` | `None` | `CONFLICTED` | `PRESSURE_METRIC_CONFLICTED_INPUT` |
| Resolved record's value field is `None` (missing) | `None` | `UNAVAILABLE` | `SHORT_INTEREST_MISSING_VALUE` / `BORROW_FEE_MISSING_VALUE` / `BORROW_AVAILABILITY_MISSING_VALUE` |
| Resolved record's value field is explicit `0` | usable as-is | `KNOWN_VALUE` | none — zero is a known value, never coerced from missing and never treated as missing |
| Starting value is `0` and an absolute-change metric is requested | usable as-is | `KNOWN_VALUE` | none |
| Starting value is `0` and a *relative/percentage*-change metric is requested | `None` | `INVALID` | `*_ZERO_START_DENOMINATOR` |
| No revision exists yet for the requested period | `None` | `UNAVAILABLE` | `SHORT_INTEREST_REVISION_NOT_FOUND` |
| Revision exists but `parent_observation_ids` is empty/unresolvable | `None` | `UNAVAILABLE` | `SHORT_INTEREST_REVISION_LINK_MISSING` |
| `starting_reporting_period == ending_reporting_period` | `None` | `INVALID` | `PRESSURE_METRIC_IDENTICAL_INPUT` |
| `starting > ending` (period or timestamp) | `None` | `INVALID` | `PRESSURE_METRIC_START_AFTER_END` |
| Days-to-cover volume baseline missing | `None` | `UNAVAILABLE` | `DAYS_TO_COVER_VOLUME_BASELINE_UNAVAILABLE` |
| Days-to-cover volume baseline `== 0` | `None` | `INVALID` | `DAYS_TO_COVER_ZERO_VOLUME_BASELINE` |
| Days-to-cover volume interval is not the daily bar interval | `None` | `INVALID` | `DAYS_TO_COVER_INCOMPATIBLE_VOLUME_INTERVAL` |

Every "missing" row is `value=None`, never `Decimal(0)`/`0` — the direct, domain-specific
continuation of the same fix Phase 2B already made for volume (`docs/phase-2b-design.md`
§9/§12) and the fix ADR 0004 established project-wide, now applied to the two inherited
anti-patterns the archived-repo research reconfirmed in this domain specifically: `core/
filters.py`'s `df["Short Float"] = 0` default-on-missing-column, and `core/ib_borrow_rate.py`
stamping local fetch time as `as_of` instead of the feed's own (discarded) business
timestamp. Phase 2C's `SourceAgeMetadata` (§4) is, in part, the structural fix to that second
defect: it always records the observation's own `source_timestamp` verbatim, never a fetch
time standing in for it.

## 11. Provider and scope policy

Every Phase 2C metric requires an **explicit** `provider` (short-interest metrics) or
`volume_provider`/`short_interest_provider` pair (days to cover) — there is no
`provider=None`-with-ambiguity-detection mode as Phase 2A/2B's bar selectors have. This is a
deliberately more conservative initial policy than Phase 2A/2B (handoff §21: "Begin
conservatively with explicit single-provider comparisons"). `provider_scope` is always
`ProviderScopeMode.SINGLE_PROVIDER` on every Phase 2C result;
`EXPLICIT_PROVIDER_SET_PRESERVED_SEPARATELY` is not implemented (same
`NotImplementedError` stance Phase 2A/2B already take for it). Short-interest and borrow
metrics never average, blend, or silently prefer one provider over another; days-to-cover's
two explicit provider roles (`short_interest_provider`, `volume_provider`) are recorded as
two clearly distinct fields specifically so the cross-domain combination can never be
mistaken for "the same source" (handoff §21's explicit requirement).

## 12. No-look-ahead enforcement

Structural, not conventional, exactly mirroring Phase 2A/2B's own approach
(`docs/point-in-time-evidence-policy.md`):

- `pressure_selection.py`'s `_eligible()` is the *only* place any Phase 2C code path reads a
  raw, unfiltered `Observation` stream; every builder in §8 calls it (or, for the volume half
  of days to cover, Phase 2A's own `resolve_trailing_window`, which enforces the identical
  discipline through `evidence.bars.build_bar_series`) — no Phase 2C module ever holds a bare
  observation list plus a separately, later-applied `as_of` cutoff.
- A correction/revision/cancellation participates only once its own `source_timestamp`,
  `received_timestamp`, and `effective_timestamp` are all `<= as_of` — re-executed by
  `_eligible()` on every call, never special-cased.
- A `PressureMetricResult`/`DaysToCoverComponents` computed at an earlier `as_of` is a pure
  function of `(observations, as_of, request)` and is never mutated; a later `as_of` may
  legitimately resolve a different (later-eligible) record, producing a new, separately
  identified result — the old one's serialized bytes are untouched (proven by the
  before/after revision and before/after cancellation anchors, § test plan, byte-identical
  re-serialization exactly like Phase 2A/2B's own lifecycle tests).
- Days-to-cover's volume window can never include a bar at or after `as_of` (Phase 2A's own
  guarantee, inherited unmodified) and never includes a bar published/received after `as_of`
  even if its `bar_start` predates `as_of` — the identical rule Phase 2A already enforces for
  every trailing-window consumer.

## 13. Diagnostics

`MetricDiagnosticCode` (existing `StrEnum`) gains the Phase 2C codes actually reachable by an
implemented code path (mirroring Phase 2A/2B's own stated practice of never defining a dead
enum member, `phase-2a-design.md` §9, `phase-2b-design.md` §16):

```
PRESSURE_METRIC_NO_ELIGIBLE_INPUT
PRESSURE_METRIC_AMBIGUOUS_PROVIDER
PRESSURE_METRIC_CONFLICTED_INPUT
PRESSURE_METRIC_START_AFTER_END
PRESSURE_METRIC_IDENTICAL_INPUT

SHORT_INTEREST_START_NOT_FOUND
SHORT_INTEREST_END_NOT_FOUND
SHORT_INTEREST_MISSING_VALUE
SHORT_INTEREST_ZERO_START_DENOMINATOR
SHORT_INTEREST_CANCELLED_INPUT
SHORT_INTEREST_REVISION_NOT_FOUND
SHORT_INTEREST_REVISION_LINK_MISSING

DAYS_TO_COVER_SHORT_INTEREST_NOT_FOUND
DAYS_TO_COVER_VOLUME_BASELINE_UNAVAILABLE
DAYS_TO_COVER_ZERO_VOLUME_BASELINE
DAYS_TO_COVER_INCOMPATIBLE_VOLUME_INTERVAL

BORROW_FEE_START_NOT_FOUND
BORROW_FEE_END_NOT_FOUND
BORROW_FEE_MISSING_VALUE
BORROW_FEE_ZERO_START_DENOMINATOR

BORROW_AVAILABILITY_START_NOT_FOUND
BORROW_AVAILABILITY_END_NOT_FOUND
BORROW_AVAILABILITY_MISSING_VALUE
BORROW_AVAILABILITY_ZERO_START_DENOMINATOR
```

Codes named in the handoff's suggested list (§22) but never reachable by an implemented
Phase 2C policy — e.g. `SHORT_INTEREST_REPORTING_PERIOD_MISMATCH`,
`SHORT_INTEREST_UNIT_MISMATCH`, `DAYS_TO_COVER_INSUFFICIENT_VOLUME_HISTORY`,
`DAYS_TO_COVER_INCOMPATIBLE_VOLUME_SESSION`, `*_UNIT_MISMATCH` for borrow — are intentionally
omitted: unit mismatch cannot occur because every Phase 2C payload field has exactly one
fixed unit already normalized by its adapter (§1 of the research brief: `short_shares` is
always exact shares, `annualized_fee_percent` is always percentage points post-normalization,
`available_shares` is always exact shares), so no Phase 2C selector ever receives a
mixed-unit candidate to reject; insufficient volume history is reported through
`resolve_trailing_window`'s own reused `VOLUME_BASELINE_INSUFFICIENT_SAMPLES`/
`VOLUME_BASELINE_WINDOW_EMPTY` diagnostics (surfaced verbatim on `DaysToCoverComponents`,
not re-coded under a new name) rather than a duplicate Phase-2C-specific code. `PRESSURE_
METRIC_AMBIGUOUS_PROVIDER` and `_NO_ELIGIBLE_INPUT` are defined for completeness/forward
use inside `pressure_selection.py`'s shared helpers even though §11's "provider is always
explicit" policy means ambiguity is unreachable from any of the nine public builders today
— retained because `_eligible()` is written as a genuinely shared, provider-optional-capable
primitive (defensive, tested, but not exposed through any current public request shape).
Severity levels and the sort key `(code.value, observation_ids, message)` are unchanged
(`sort_diagnostics` reused as-is, no new sorting logic).

## 14. Isolation boundary

`tests/metrics/test_isolation.py::FORBIDDEN_IDENTIFIER_SUBSTRINGS` gains Phase 2C-specific
entries for concepts that must never leak into source even incidentally:
`short_pressure_score, borrow_pressure_score, cost_to_borrow_score, hard_to_borrow_score,
squeeze_probability, fail_to_deliver, gamma_exposure, open_interest`. Existing entries are
untouched. `test_no_result_field_could_carry_a_ratio_ranking_or_recommendation` is extended
with an identical field-name check against `PressureMetricResult.model_fields` and
`DaysToCoverComponents.model_fields`. `test_no_forbidden_imports_in_metrics_source` and
`test_no_wall_clock_or_random_uuid_calls_in_metrics_source` already scan every `*.py` in
`metrics/` via AST, so the seven new files are covered with zero changes to those two tests.

## 15. Compatibility guarantee

- `MetricResult`, `NormalizedMetricResult`, `BaselineStatistics`, `TrailingWindow`, and every
  existing `MetricName`/`MetricUnit`/`MetricDiagnosticCode`/`WindowType` member are
  byte-identical in behavior and serialization to Phase 2B.
- `metrics/selection.py`, `metrics/volume_baselines.py`, `metrics/returns.py`,
  `metrics/gaps.py`, `metrics/ranges.py`, `metrics/relative_volume.py`,
  `metrics/volume_standardization.py`, `metrics/return_baselines.py`,
  `metrics/return_standardization.py` are **not modified** — Phase 2C only calls their
  existing public functions (`resolve_trailing_window`, `compute_mean_volume`,
  `deterministic_metric_id`, `metric_identity`).
- `src/squeeze_core/adapters/finra/*`, `src/squeeze_core/adapters/ibkr/*`,
  `src/squeeze_core/evidence/*`, `src/squeeze_core/contracts/*` are **not modified**.
- `tests/fixtures/compatibility/phase_1_anchor_manifest.json`,
  `tests/fixtures/metrics/expected_phase_2a_metric_metadata.json`, and
  `tests/fixtures/metrics/expected_phase_2b_metric_metadata.json` are not written to by any
  Phase 2C code or script; a new, separate
  `tests/fixtures/metrics/expected_phase_2c_metric_metadata.json` is created instead.
  `tests/metrics/test_phase_2c_compatibility.py` diffs all three prior files against the
  Phase 2B completion commit (`b2a75e3e`) and asserts zero delta.

## 16. Inherited-formula disposition (archived-repository research, read-only)

Both archived repositories (`0897562e`, `6dbefd1a`) and the third Phase-1-release-candidate
target were confirmed clean and unmodified before and after inspection (§ completion report
git diffs); a pre-existing Phase 0 reconstruction (`docs/reconstruction/`, 14 docs) was
cross-checked against, not duplicated.

| Inherited formula | Source | Disposition in Phase 2C |
|---|---|---|
| `calculate_days_to_cover(shares_short, average_daily_volume)` | `core/short_interest.py` (current app) | Formula *shape* reused (`shares_short / average_daily_volume`, §8.3); the null-safe/denominator-validated pattern (return `None` + a reason rather than `0`/an exception) is reused as the general missing/zero-denominator discipline (§10). Not reused wholesale: the function's own "average_daily_volume" input has no defined provenance/window — Phase 2C replaces that ambiguity with an explicit, versioned, `MEAN_VOLUME_BASELINE`-backed denominator policy (§8.3) instead of an opaque caller-supplied number. |
| `calculate_short_float_percent` | `core/short_interest.py` | **Not implemented** — short-float recalculation is explicitly out of Phase 2C scope (handoff §11); `payload.short_float_percent` remains provider-published, untouched evidence. |
| `check_short_float_discrepancy(tolerance_points=2.0)` | `core/short_interest.py` | **Not reused** — a cross-provider agreement *check* is a quality/conflict concept (already covered structurally by §3's conflict handling), and the specific `2.0`-point tolerance is an unvalidated heuristic threshold, exactly the kind of invented threshold handoff §16/§18 prohibits introducing without an established policy. |
| IB FTP borrow fee/rebate/available parser (`fee`, `rebate`, `available` fields; null-on-absent) | `core/ib_borrow_rate.py` | Null-on-missing discipline reused (§10); the `as_of`-mislabeling defect (stamps local fetch time, discards the feed's own business-timestamp line) is the exact defect Phase 1B's `source_timestamp`/`received_timestamp`/`effective_timestamp` split already structurally prevents (confirmed: IBKR's `_timestamp()` always parses the *provider's own* timestamp, never substitutes ingestion time except as an explicitly-diagnosed uncertain placeholder) — Phase 2C's `SourceAgeMetadata` (§4) surfaces this distinction explicitly rather than re-introducing the ambiguity. `rebate_rate` has no Phase 1 evidence domain (not modeled anywhere in `short-squeeze-core`) and is out of scope. |
| `AVAILABLE` (shares available to borrow), parsed but never surfaced or differenced | `core/ib_borrow_rate.py` | **New work in Phase 2C** (`BORROW_AVAILABILITY_ABSOLUTE_CHANGE`/`_PERCENTAGE_CHANGE`, §8.5) — no inherited comparison formula exists to adapt; the delta arithmetic itself is a generic two-point subtraction/ratio with no domain-specific precedent to reuse or reject. |
| Composite squeeze score (saturating normalization + missing-weight renormalization); Prime `>=70 and short_float>=5` / Subprime `>=40` gates | `core/squeeze_score.py` | Rejected outright — scoring/tiering/threshold classification, explicitly prohibited (handoff §9/§11/§37). Confirms short interest and borrow fee were only ever consumed as scoring *inputs* in the inherited system, never exposed as bare objective deltas the way Phase 2C requires. |
| `df["Short Float"] = 0` on missing Finviz column; Prime gate's `(short_float_percent or 0)` | `core/filters.py` | Rejected — the textbook missing-to-zero anti-pattern (§10); the direct motivating example, alongside ADR 0004, for why every Phase 2C "missing" row above is `value=None`. |
| `clean_float`/`Milli_refitting` (`int(value) * 1_000_000`) applied to `Shares Float` and, in `Formula_logger.py`, reapplied to a `Short Interest` export column | `core/filters.py`, `Formula_logger.py` | Rejected — confirmed unit-ambiguous/incorrect (breaks on decimal/suffix input; the `Short Interest` reapplication has no verified basis). Phase 2C never applies any such shorthand-unit multiplier: `payload.short_shares`/`payload.available_shares` are consumed as the exact integers Phase 1's adapters already validated, with no secondary scaling step anywhere in `metrics/`. |
| IB relative volume (`core/ib_api.py`, `today / mean(history[:-1])`, `0.0` on missing history) | referenced by Phase 2A/2B research, re-confirmed here | Not a short-interest/borrow formula; already dispositioned in `phase-2a-design.md`/`phase-2b-design.md`. Relevant to Phase 2C only as the same "never fabricate `0.0` on missing" lesson, applied here to a different domain (§10). |
| Silent per-field provider fallback chains (IB tick → Finnhub → historical close; shared Yahoo float/short metadata) | Phase 0 `06-data-source-map.md`, confirmed by this pass | Not adopted — Phase 2C never selects an implicit "winning" provider (§11); every metric requires an explicit provider and reports ambiguity/conflict rather than silently falling back. |

No look-ahead-prone formula was found *inside* the short-interest/borrow calculations
themselves (both are pure functions over caller-supplied inputs); the look-ahead risk Phase 0
flags elsewhere (`P0-VAL-002`, target/stop evaluation using an alert day's own bar) is
adjacent to, not inside, this domain and is already out of Phase 2C's scope (no
entries/exits/targets/stops are implemented here).

## 17. Excluded from Phase 2C (restated for completeness)

Unchanged from handoff §11/§37: short-float recalculation, estimated/synthetic short
interest or naked-short estimates, fail-to-deliver analytics, options/gamma/open-interest
analytics, cost-to-borrow/hard-to-borrow/borrow-pressure/short-pressure score, squeeze
probability, composite squeeze score, candidate rank, Prime/Subprime, threshold/strong-weak/
bullish-bearish labels, entries/exits/targets/stops, backtesting, live integration,
deployment, GUI, database, paper/live trading, machine learning. Verified absent by the
extended isolation tests (§14) and the completion report.
