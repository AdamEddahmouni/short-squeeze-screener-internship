# Phase 2D Design: Evidence Alignment and Readiness Diagnostics

## 1. Purpose and boundary

Phase 2D answers objective, structural questions about a **point-in-time evidence
bundle** (the output of Phase 1's `build_point_in_time_evidence`) and, optionally, a
set of already-computed Phase 2A/2B/2C metric results: which required evidence
domains are present as of a given time, which are missing/unavailable/conflicted/
cancelled/partial, how old each domain's evidence is, whether reporting periods
align, and whether the inputs required for one **named, already-implemented**
downstream calculation are structurally sufficient.

Phase 2D does **not** decide whether a symbol is a good candidate, whether a squeeze
is likely, or whether to trade. "Readiness" in this phase means *objective structural
sufficiency for a named deterministic downstream operation under a versioned input
contract* -- never trading readiness, quality, or attractiveness. The four allowed
structural states (`SUFFICIENT`, `INSUFFICIENT`, `UNKNOWN`, `CONFLICTED`) describe an
**input contract**, not a candidate. No score, rank, confidence percentage, Prime/
Subprime label, or recommendation appears anywhere in this phase's models, code, or
CLI output.

## 2. Architectural decision: build on `PointInTimeEvidenceBundle`, don't reparse it

Phase 1 already computes, per domain, a `CoverageState` (`PRESENT/MISSING/STALE/
DELAYED/UNKNOWN_FRESHNESS/CONFLICTED/INVALID/PARTIAL`), a list of `EvidenceConflict`s,
per-observation `ObservationAge`, `RevisionRelationship`s, and domain-tagged
`EvidenceDiagnostic`s -- all already point-in-time filtered (no observation whose
`source_timestamp`/`received_timestamp`/`effective_timestamp` is after `as_of` is
ever included). Re-deriving eligibility from raw observations in Phase 2D would
duplicate Phase 1 logic and risk drifting from it.

**Decision**: Phase 2D readiness functions take an already-built
`PointInTimeEvidenceBundle` (`squeeze_core.evidence.PointInTimeEvidenceBundle`) as
their primary evidence input, plus an optional tuple of already-computed metric
results (`MetricResult | NormalizedMetricResult | PressureMetricResult`) for
`INPUT_SUFFICIENCY` checks that want to reference an existing computation instead of
re-running it. No-look-ahead is therefore inherited for free: if the bundle is
point-in-time eligible, every Phase 2D diagnostic built from it is too. This mirrors
Phase 2A-2C's own pattern of consuming Phase 1 evidence rather than re-normalizing
raw provider records.

Phase 2D's own vocabulary (`DomainCoverageState`) is intentionally **not** identical
to Phase 1's `CoverageState` -- see Section 5 -- because readiness needs a
cancellation-aware, freshness-orthogonal classification that Phase 1's evidence layer
does not itself compute (freshness is Phase 1's concern; "is this domain's *current*
active record cancelled" is not something `CoverageState` currently distinguishes).

## 3. Reused vocabulary (not reinvented)

Per audit of the existing codebase, Phase 2D reuses, unmodified:

- `squeeze_core.contracts.quality.Quality` / `QualityState` -- every readiness result
  carries `quality: Quality`. Because every Phase 2D result is a *description*, not a
  measured value, `quality.state` is `KNOWN_VALUE` whenever the diagnostic
  computation itself completed (even an `INSUFFICIENT` or `CONFLICTED` structural
  state is a successfully computed, known answer). `quality.state` is non-`KNOWN_VALUE`
  only when the *diagnostic computation itself* could not be produced (e.g. an
  unsupported operation name or an unsupported policy version was requested).
- `squeeze_core.adapters.diagnostics.DiagnosticSeverity` (`INFO/WARNING/ERROR`) for
  `ReadinessDiagnostic.severity`, exactly as `MetricDiagnostic` does.
- `squeeze_core.metrics.identifiers.METRIC_NAMESPACE` and `deterministic_metric_id` --
  Phase 2D mints no new UUID namespace. Every readiness result's identity dict has a
  structurally distinct key set from every prior phase's (verified by
  `tests/readiness/test_identifiers.py`), so cross-phase collision remains
  cryptographically negligible, exactly as Phase 2B/2C's namespace-reuse rationale
  states.
- `squeeze_core.metrics.source_age.build_source_age` -- both `EVIDENCE_AGE_ALIGNMENT`
  and `REPORTING_PERIOD_ALIGNMENT` call this directly for each representative
  observation rather than reimplementing age arithmetic.
- `squeeze_core.evidence.CoverageDomain`, `CoverageState`, `EvidenceConflict`,
  `ConflictClassification`, `ObservationAge`, `PointInTimeEvidenceBundle`.
- `squeeze_core.serialization.canonical_json.canonical_hash` /
  `canonical_json_bytes` for every new `*_hash` / `serialize_*` helper.

Nothing above is subclassed or mutated in place; Phase 2D's own models
(`src/squeeze_core/readiness/models.py`) are new, standalone, frozen Pydantic models,
following the "each phase gets its own result shape" rule established in
`phase-2c-design.md` Section 2 -- adding a field to `PointInTimeEvidenceBundle` or
`MetricResult` would change their canonical bytes and therefore every already-
anchored hash of that type.

## 4. New enums

```python
class DomainCoverageState(StrEnum):
    PRESENT = "PRESENT"
    MISSING = "MISSING"
    UNAVAILABLE = "UNAVAILABLE"
    CONFLICTED = "CONFLICTED"
    CANCELLED = "CANCELLED"
    PARTIAL = "PARTIAL"
    UNKNOWN = "UNKNOWN"

class StructuralState(StrEnum):
    SUFFICIENT = "SUFFICIENT"
    INSUFFICIENT = "INSUFFICIENT"
    UNKNOWN = "UNKNOWN"
    CONFLICTED = "CONFLICTED"

class AgeDimension(StrEnum):
    AVAILABILITY_AGE = "AVAILABILITY_AGE"
    REPORTING_PERIOD_AGE = "REPORTING_PERIOD_AGE"
```

Only two `AgeDimension` members are defined because those are the only two age
concepts Phase 1/2C evidence already computes deterministically for every domain
that has them (`SourceAgeMetadata.availability_age_seconds` and
`.reporting_period_age_days`). `PUBLICATION_LAG`, `EVENT_AGE`, `CAPTURE_AGE`, and
`RECEIPT_AGE` from the handoff's suggested list are not added as `AgeDimension`
members because `EVIDENCE_AGE_ALIGNMENT`/`REPORTING_PERIOD_ALIGNMENT` only ever
compare one dimension at a time across domains, and only these two dimensions have
an existing, tested, cross-domain-comparable computation
(`build_source_age`). Publication lag remains available as raw per-domain metadata
(`SourceAgeMetadata.publication_lag_seconds`) but is not promoted to a comparable
cross-domain alignment axis in this phase -- adding it later is additive.

## 5. Domain coverage classification (`DomainCoverageState`)

Computed per requested domain from the bundle alone, precedence high to low:

1. **`UNKNOWN`** -- the bundle has no `SourceCoverage` entry at all for this domain
   (the evidence-bundle policy that built the bundle never evaluated it, e.g.
   `include_news_domain=False`). Phase 2D cannot distinguish "missing" from
   "unavailable" without Phase 1 having looked, so it reports the honest answer:
   unknown, not missing.
2. **`CANCELLED`** -- the domain has at least one point-in-time-eligible observation,
   and *every* eligible observation's per-domain lifecycle status field (see table
   below) indicates cancellation/withdrawal/deletion. A domain with one active
   record and one older cancellation is `PRESENT`, not `CANCELLED` -- this precedence
   only fires when cancellation is the *entire* eligible set, matching the handoff's
   "a cancelled record must not count as active presence unless the domain policy
   explicitly preserves another eligible active record" (and the converse: a
   domain whose *only* eligible evidence is cancelled must not silently read as
   ordinary `PRESENT`).
3. **`CONFLICTED`** -- the domain's `SourceCoverage.state` is `CONFLICTED`, or any
   `EvidenceConflict` in the bundle names an observation belonging to this domain.
4. **`PARTIAL`** -- `SourceCoverage.state` is `PARTIAL` (Phase 1 already flags this
   for SEC filings/trading halts with partial metadata, and for in-progress bars).
5. **`UNAVAILABLE`** -- `SourceCoverage.state` is `MISSING`, but the bundle's
   `diagnostics` contain at least one domain-tagged entry (an
   `EVIDENCE_*_NOT_YET_PUBLISHED`/`EVIDENCE_*_NOT_YET_RECEIVED`/
   `EVIDENCE_EXCLUDED_AFTER_AS_OF`-family code with `domain` set to this domain) --
   evidence exists but was point-in-time ineligible, which is a different fact than
   no evidence existing at all. Also fires when the domain's eligible observations
   all carry `quality.state in {UNAVAILABLE, INVALID}` (a shell of a record whose
   value is not usable).
6. **`MISSING`** -- `SourceCoverage.state` is `MISSING` and nothing above fired: no
   evidence, eligible or excluded, exists for this domain at all.
7. **`PRESENT`** -- everything else, including Phase 1's `STALE`/`DELAYED`/
   `UNKNOWN_FRESHNESS` coverage states. Freshness is a real, useful fact, but it is
   an *age* fact (Section 6), not a presence fact -- collapsing it into `PRESENT`
   here is what keeps `DOMAIN_COVERAGE_SNAPSHOT` free of any staleness threshold or
   judgment, per the handoff's explicit "no stale/fresh classification" rule for
   readiness state.

Per-domain lifecycle status fields used for cancellation detection (read from
`Observation.provenance.provider_metadata`, matching Phase 1's own lifecycle-linking
fields exactly):

| Domain | Metadata key | Cancelled values |
|---|---|---|
| `PUBLISHED_SHORT_INTEREST` | `revision_status` | `CANCELLED` |
| `SEC_FILINGS` | `filing_status` | `CANCELLED` |
| `TRADING_HALTS` | `revision_status` | `CANCELLED` |
| `NEWS` | `status` | `WITHDRAWN`, `DELETED` |
| `MARKET_BARS` | `status` | `CANCELLED` |
| `TRADES`, `QUOTES` | `status` | `CANCELLED`, `DELETED` |
| `BORROW_FEE`, `BORROW_AVAILABILITY`, `CANDIDATE_SNAPSHOT` | -- | no lifecycle/cancellation concept; never `CANCELLED` |

An unmapped or absent metadata key is treated as "not cancelled," never as an error
-- a missing lifecycle tag must not silently promote a domain to `CANCELLED`.

## 6. Age alignment (`EvidenceAgeAlignment`)

`EVIDENCE_AGE_ALIGNMENT` compares one explicit `AgeDimension` (default
`AVAILABILITY_AGE`, documented as the default because it is the one dimension every
domain type can produce) across a caller-specified set of domains. For each domain,
the *representative* age is the **minimum** (freshest) `availability_age_seconds`
among that domain's point-in-time-eligible observations, computed via
`build_source_age(observation, as_of)` -- using the freshest record is the least
surprising choice: it answers "how current can this domain's evidence be treated as
of `as_of`," not "how old is the oldest thing we happen to still have." Domains with
zero eligible observations, or whose eligible observations lack a resolvable
`effective_timestamp` (never true in this codebase, but defensively handled),
contribute to `missing_age_domains` and are excluded from
`youngest/oldest/spread/mean`. All arithmetic is exact integer seconds (or Decimal
for the mean, via the existing `metrics.statistics.decimal_mean`); no float. A
single comparable domain yields `age_spread_seconds = 0`; zero comparable domains
yields `youngest_age_seconds = oldest_age_seconds = age_spread_seconds =
mean_age_seconds = None`. No threshold, no "stale" judgment, is ever attached.

`REPORTING_PERIOD_AGE` alignment (used only by `REPORTING_PERIOD_ALIGNMENT`, not
`EVIDENCE_AGE_ALIGNMENT`) is a structurally separate output built the same way but
comparing `reporting_period_age_days * 86400` -- never mixed into the same
min/max/spread computation as `AVAILABILITY_AGE`, because a recent *receipt* of an
old *report* and an old receipt of a recent report are different facts (the
handoff's "old short-interest reporting period with recent receipt" test case
exists specifically to prevent collapsing these two).

## 7. Reporting-period alignment (`ReportingPeriodAlignment`)

Applies only to domains with a genuine reporting-period concept in the existing
payload models: `PUBLISHED_SHORT_INTEREST` (`payload.settlement_date`) and
`SEC_FILINGS` (`payload.period_of_report`, nullable). No other domain has a
reporting-period field, so no other domain is ever eligible for this output --
publication time and receipt time are never substituted. A requested domain with no
reporting-period concept, or whose eligible observation's `period_of_report` is
`None`, is recorded in `missing_reporting_period_domains`, never fabricated. Earliest/
latest end dates and their spread (in whole seconds, via `date` arithmetic times
86400) are reported with no alignment score and no freshness judgment.

## 8. Conflict summary (`EvidenceConflictSummary`)

A thin, deterministic aggregation over `bundle.conflicts` (already computed and
already excluding revisions/corrections/temporal-differences per Phase 1's
`evidence/conflicts.py` -- Phase 2D adds no new conflict-detection logic, only
groups the existing `EvidenceConflict` records by domain). `conflict_categories` is
the sorted set of `ConflictClassification` values seen. No provider-preference
resolution, no averaging -- consistent with Phase 1's own guarantee.

## 9. Missingness summary (`EvidenceMissingnessSummary`)

Distinguishes, per the handoff's required taxonomy, using only facts already visible
on the bundle/coverage snapshot/policy -- no new value-level scanning beyond what
`Quality`/`DomainCoverageState` already expose:

- `MISSING_DOMAIN` -- `DomainCoverageState.MISSING` for a *required* domain.
- `UNKNOWN_AVAILABILITY` -- `DomainCoverageState.UNKNOWN` for a *required* domain.
- `MISSING_REQUIRED_METRIC` -- a policy-required `metric_name` not found among the
  supplied metric results.
- `INSUFFICIENT_HISTORY` -- a policy that `requires_trailing_window` whose
  referenced metric result (if supplied) carries a `SampleCounts` with `used <
  requested`, surfaced via the existing `SampleCounts` model, never invented.
- Zero-valued evidence (`Quality.state is KNOWN_VALUE` with a numeric `0`/`Decimal
  ("0")`) is explicitly *not* counted anywhere in this summary -- only `Quality.state
  in {MISSING, UNAVAILABLE}` values are missing. This mirrors
  `contracts/quality.py`'s existing "missing versus zero" rule verbatim.
- `MISSING_REQUIRED_FIELD` is reserved for a future per-field contract; this phase's
  policies operate at domain/metric granularity, so no `MISSING_REQUIRED_FIELD`
  case is currently emitted (documented, not a silent gap -- see Known Limitations
  in `docs/phase-2d-progress.md`).

## 10. Operation requirement policies (`OperationRequirementPolicy`)

A versioned, declarative, data-only registry
(`src/squeeze_core/readiness/policies.py::OPERATION_REQUIREMENT_POLICIES`) mapping
each of the 17 already-implemented Phase 2A/2B/2C `MetricName` values named in the
handoff to a `policy_version="phase_2d_readiness_policy.v1"` policy stating
`required_domains`, `optional_domains`, `required_metric_names` (only for
operations, like `RELATIVE_VOLUME`/`DAYS_TO_COVER`, that structurally build on
another named metric), and `requires_trailing_window: bool`. Policies contain no
formula logic and no trading threshold -- they are reused, not recomputed, by
`sufficiency.py`. Every metric-shaped field a policy could name (`required_units`,
`required_provider_scope`, `required_session_scope`, `required_interval_scope`)
is present on the model for forward compatibility but is only populated where the
existing metric contract already fixes it (e.g. `DAYS_TO_COVER`'s
`required_interval_scope` is unset because volume interval is caller-chosen, not
formula-fixed).

## 11. Input sufficiency (`InputSufficiencyResult`)

For one named operation: look up its policy; classify each `required_domain` via
Section 5; if a `required_metric_names` entry is supplied, check the corresponding
metric result's `quality.state`, `SampleCounts` (if any), `unit`, and provider/scope
fields for compatibility; produce disjoint sets of `missing_inputs`,
`conflicted_inputs`, `incompatible_inputs` (unit/scope), and
`insufficient_history_inputs`. `structural_state` resolves as:

- `CONFLICTED` if any required input is conflicted and the policy does not
  `allow_conflicts`.
- `UNKNOWN` if any required domain is `UNKNOWN` (availability could not even be
  determined) and the policy does not `allow_unknown_availability`.
- `INSUFFICIENT` if any required input is missing, incompatible, or has
  insufficient history.
- `SUFFICIENT` otherwise.

This never recomputes the downstream metric -- it only validates presence/
compatibility of what the metric would need, optionally cross-checking an already-
computed result's own `quality`/`SampleCounts` when one is supplied.

## 12. Readiness snapshot (`EvidenceReadinessSnapshot`)

Aggregates `DomainCoverageSnapshot`, `EvidenceAgeAlignment`, `ReportingPeriodAlignment`
(when applicable domains are present), `EvidenceConflictSummary`,
`EvidenceMissingnessSummary`, and `InputSufficiencyResult` for one named operation
into one immutable result, referencing the component results **by their
deterministic ID**, not by embedding them -- keeping the snapshot small and each
component independently anchorable/testable. `structural_state` is copied from the
`InputSufficiencyResult`. No score, rank, or recommendation field exists on this or
any Phase 2D model.

## 13. Deterministic identity and serialization

Every Phase 2D result model self-assigns `deterministic_id` via the same
`model_validator(mode="after")` + `object.__setattr__` pattern as
`PressureMetricResult`/`DaysToCoverComponents`, calling
`squeeze_core.metrics.identifiers.deterministic_metric_id` under the existing
`METRIC_NAMESPACE`. Each model has its own `*_identity(result) -> dict` builder in
`readiness/identifiers.py`, excluding only fields that do not affect the described
facts (`diagnostics`, `deterministic_id`; `quality.reasons` text is excluded but
`quality.state` is included since it's a structural fact). Every identity dict
includes `result_type` (a literal string per model, e.g. `"DOMAIN_COVERAGE_SNAPSHOT"`)
so that two different result types can never collide even if every other field
happened to coincide. `symbol`, `as_of`, `requested_domains` (sorted),
`input_observation_ids` (sorted), `input_metric_ids` (sorted), and `conflict_ids`
(sorted) are always included when present on a model -- never wall-clock, never
random, never Python set/dict iteration order (all collections are sorted before
hashing). Canonical JSON serialization reuses
`squeeze_core.serialization.canonical_json` verbatim; `readiness/serialization.py`
provides one `serialize_*`/`deserialize_*`/`*_hash` triple per model, mirroring
`metrics/serialization.py` exactly.

## 14. No-look-ahead

Guaranteed structurally, not by a Phase-2D-specific check: every fact Phase 2D
reports is read from a `PointInTimeEvidenceBundle` already built for a specific
`as_of`, or from a metric result whose own `as_of` is passed through unchanged and
compared for equality against the bundle's `as_of` (a mismatch is a usage error, not
silently ignored). Phase 2D performs no new timestamp comparisons against wall-clock
time anywhere.

## 15. What Phase 2D explicitly does not do

No composite score, no weighting, no rank, no Prime/Subprime or strong/weak label,
no bullish/bearish classification, no accept/reject decision, no recommendation, no
alert, no threshold-based freshness judgment, no live data access, no database, no
GUI. `StructuralState` values describe an input contract only; `docs/evidence-
readiness-contract.md` states this distinction explicitly for any future phase that
consumes Phase 2D's output.
