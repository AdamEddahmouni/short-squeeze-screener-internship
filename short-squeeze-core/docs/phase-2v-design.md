# Phase 2V Design: BIYA Validation Bridge

## 1. Purpose and boundary

Phase 2V reconstructs, from evidence, **why the original screener surfaced BIYA**,
what information was genuinely available at that moment, which original rules survive
scrutiny, and whether the recorded case supports a repeatable research methodology.

It is an *empirical validation and case-reconstruction* phase. It produces historical
timelines, original-versus-rebuilt comparisons, methodology classifications, structural
diagnostics, point-in-time availability findings, and a professor-facing research
demonstration.

It produces **no** composite squeeze score, candidate ranking, trade recommendation,
buy/sell signal, entry/exit logic, P&L, portfolio simulation, Prime/Subprime label,
bullish/bearish label, alert, or generalized strategy backtest. No model, function,
diagnostic code, CLI field, or exported JSON key in this phase carries trading meaning.

The critical distinction Phase 2V exists to enforce:

> **"The stock moved afterward" and "the methodology was valid" are different claims,
> supported by different evidence, and Phase 2V never allows one to stand in for the
> other.**

## 2. What the evidence actually supports

`docs/phase-2v-biya-artifact-inventory.md` is the authoritative evidence record. Three
findings from it shape this entire design, and each one removes an option the brief
assumed was available.

**Finding 1 — the archived working tree is the wrong code.** The advisor observed the
application at `2026-07-17T12:46:15` local. The archived `ScreenerProject` checkout
(`6dbefd1a`) includes the Prime/Subprime redesign committed at `15:39:27` the same day —
**2h53m after the meeting**. Reconstructing "the original rules" from the checked-out
tree would describe `classify_tier()`, a function that did not exist when BIYA was
surfaced. The original-rule manifest is therefore reconstructed from commit
**`b016d92f` (2026-07-17T11:56:43)**, the last commit preceding the meeting, read
read-only via `git show`.

**Finding 2 — no original BIYA value survives.** The only direct platform record
(`app.log`) contains 43 BIYA lines, all of them failures: IB `Error 10089`
(subscription missing → delayed data) and Schwab DNS resolution failures. It carries no
price, change, relative volume, float, short float, days to cover, borrow fee, news,
score, or label — and no timestamps of any kind. Consequently **every** original BIYA
field value is `UNKNOWN`, and this phase must be able to represent a case that is
almost entirely unknown without collapsing into vacuity.

**Finding 3 — no BIYA market data exists locally, at any interval, on any date.** The
outcome observation the brief asks for is therefore not computable from local evidence.
Rather than fabricate it or fetch it, Phase 2V implements the outcome-observation
contract fully, tests it against clearly-labelled synthetic fixtures, and records the
real BIYA outcome as an explicit acquisition gap.

## 3. Architectural decision: additive package, no second point-in-time engine

Phase 2V adds `src/squeeze_core/validation/` and modifies no prior-phase module. It
consumes, never reimplements:

- `squeeze_core.evidence.build_point_in_time_evidence` — the *only* as-of eligibility
  engine. Phase 2V's replay is a thin orchestration over it. No observation filtering,
  no-look-ahead logic, or lifecycle handling is written in this phase.
- `squeeze_core.metrics.*` — Phase 2A/2B/2C metric results, computed by their existing
  builders.
- `squeeze_core.readiness.*` — all coverage, age, reporting-period, conflict,
  missingness, and sufficiency diagnostics. Phase 2V creates no competing framework.
- `squeeze_core.serialization.canonical_json` — canonical bytes and hashing.
- `squeeze_core.metrics.identifiers.METRIC_NAMESPACE` / `deterministic_metric_id` —
  reused exactly as Phase 2D reuses them; **no new UUID namespace is minted**. Every
  Phase 2V identity dict begins with a literal `result_type` unique to its model, so no
  cross-phase collision is structurally possible.

Modelling conventions follow Phase 2D exactly: Pydantic `BaseModel` with
`ConfigDict(extra="forbid", frozen=True)`, `StrEnum` vocabularies, sorted tuple fields
enforced by validators, deterministic diagnostic ordering, and UTC-aware timestamps via
`contracts.validation.require_aware_utc`.

## 4. Separation of concerns

Seven separations are enforced structurally — each pair lives in different modules and
different models, so no code path can conflate them:

| Kept apart | Why |
| --- | --- |
| Artifact discovery / interpretation | A file's existence is not a claim about its meaning |
| Detection-time evidence / market outcome | When we found it is independent of what happened next |
| Original behavior / corrected behavior | The original platform is a frozen baseline, never edited |
| Point-in-time replay / outcome observation | Replay may see only pre-detection evidence; outcome is explicitly retrospective |
| Field comparison / rule classification | A value differing is not the same as a rule being wrong |
| Methodology conclusion / candidate scoring | The conclusion judges the *method*, never the stock |
| Internal provenance / public export | Sensitive paths and credentials never reach the demo |

## 5. Detection-time evidence model

`DetectionTimeState` has exactly three members: `EXACT_TIMESTAMP`,
`BOUNDED_TIME_WINDOW`, `UNKNOWN`.

`EXACT_TIMESTAMP` requires an artifact that *directly records the candidate event
time* — a stored candidate timestamp, an application-log timestamp, a database record
time, an alert time, or a platform-produced timestamped snapshot. Filesystem metadata
never qualifies. Screenshot creation times, file mtimes, emails, and session times
produce `BOUNDED_TIME_WINDOW` at best.

For BIYA the resolved state is **`BOUNDED_TIME_WINDOW`**, `2026-07-17T14:23:58Z` to
`2026-07-17T16:54:58Z` (America/New_York `10:23:58`–`12:54:58`) — the interval bounded
below by the screener run's start and above by `app.log`'s last write. Time zone is
explicit in every field; no naive datetime is accepted anywhere in the package.

The narrower 8m43s meeting window (`16:46:15Z`–`16:54:58Z`, from the machine-generated
recording filename `20260717_124615.mp4`) bounds when BIYA was *discussed on screen*,
which is a different question. BIYA's first log line sits at file line 4, so the
screener surfaced it essentially at startup. Using the meeting window as the detection
time would claim roughly 17× more precision than the evidence supports, so the wider
window is the resolved one and the narrower one is recorded as corroboration.

Because that width is real, the design mandates replay at **both** window edges.
Selecting whichever replay looks more favourable is prohibited; both are emitted, both
are anchored, and divergence between them is itself a reported finding.

## 6. Artifact provenance

`ValidationArtifact` is immutable and carries `artifact_id`, `artifact_type`,
`repository_or_source`, `relative_path`, `content_hash`, known created/modified/embedded
event times, `timezone_if_known`, `reliability_class`, `limitations`, `sensitive`, and
`included_in_public_demo`.

Six reliability classes: `DIRECT_PLATFORM_RECORD`, `DERIVED_FROM_PLATFORM_RECORD`,
`EXTERNAL_CORROBORATION`, `FILESYSTEM_METADATA_ONLY`, `USER_RECOLLECTION`, `UNKNOWN`.

Two rules are enforced in code, not merely documented:

- **Absolute local paths never enter canonical serialization.** `relative_path` is
  validated to reject drive-letter and UNC-rooted paths. A path that cannot be made
  workspace-relative is rejected outright.
- **`sensitive=True` artifacts are excluded from public export by construction**, and
  the public exporter drops provenance fields rather than redacting them in place, so a
  new sensitive field cannot leak by being forgotten.

Content hashing lets the same bytes at two different paths be recognized as one logical
artifact (duplicate detection) while remaining two provenance entries.

## 7. Original platform baseline

The original platform is a **frozen historical baseline** (ADR 0041). Phase 2V
describes what it did; it never edits, re-runs, or corrects it, and never writes to any
archived repository.

`OriginalRuleDefinition` records `rule_id`, `display_name`, `implemented_formula`,
`intended_meaning`, `actual_input_fields`, `providers`, `thresholds`,
`missing_value_behavior`, `timestamp_behavior`, `unit_behavior`,
`original_output_field`, `known_mislabeling`, `source_file`, and
`source_lines_or_symbol` — all as *descriptive evidence*, reconstructed from
`b016d92f`. A rule whose implementation contradicts its documentation is recorded with
both, and the contradiction is the finding. Nothing is silently corrected.

The full manifest is `docs/phase-2v-original-rule-manifest.md`. Its central result:
at detection, Prime/Subprime came from `core/scoring.py::score_setup()` — four binary
points (price in [2,20], change% ≥ 10, relative volume ≥ 5, short float ≥ 5), Prime at
4/4 and Subprime at 3/4 — and that rubric **never reads borrow fee, days to cover, or
TTM Squeeze**. The label presented as a squeeze classification was computed by a
price/momentum/liquidity screener.

## 8. Original candidate snapshot with first-class unknowns

`OriginalCandidateSnapshot` must faithfully represent a case where almost nothing is
recoverable. Each field is an `OriginalFieldValue` carrying an explicit
`OriginalValueState`:

`RECOVERED`, `MISSING_IN_ARTIFACT`, `DEFAULT_SUBSTITUTED`, `DERIVED`, `AMBIGUOUS`,
`UNKNOWN`.

`UNKNOWN` is the default. A missing value is **never** rendered as `0`, `""`, or
`False`, and a value absent from the artifacts is never reconstructed from later data
and presented as original — the distinction between "the original system recorded a
zero" and "we do not know what the original system recorded" is preserved end to end,
including through serialization.

For BIYA every displayed field resolves to `UNKNOWN`, with two exceptions grounded in
ART-001: the symbol itself and the IB market-data state (`delayed`, forced by
`Error 10089`).

## 9. Replay

`build_rebuilt_as_of_snapshot` takes observations, a symbol, and an `as_of`, and
returns eligible observation/metric ids, the Phase 2D coverage snapshot, age alignment,
reporting-period alignment, conflict summary, missingness summary, operation
sufficiency, relevant metric results, diagnostics, and a deterministic id.

Only metrics whose inputs are actually available are computed. An unavailable metric is
**absent**, never zero. Where a bounded detection window exists, `earliest` and `latest`
replays are produced and anchored separately.

## 10. Comparison and classification

`FieldComparisonEntry` uses ten comparison states: `MATCH`,
`MATCH_WITH_NORMALIZATION`, `DIFFERENT_VALUE`, `DIFFERENT_SEMANTICS`,
`ORIGINAL_MISSING`, `REBUILT_UNAVAILABLE`, `ORIGINAL_DEFAULT_SUBSTITUTION`,
`ORIGINAL_MISLABELED`, `INCOMPARABLE`, `UNKNOWN`.

Semantically incompatible quantities are never compared as equivalent; that is what
`DIFFERENT_SEMANTICS` and `INCOMPARABLE` exist for. Comparing a short-float percentage
against an absolute short-interest share count yields `DIFFERENT_SEMANTICS`, not
`DIFFERENT_VALUE`.

`RuleValidationEntry` classifies each original rule as exactly one of `SUPPORTED`,
`SUPPORTED_WITH_CORRECTION`, `MOMENTUM_DISCOVERY_ONLY`, `MISLABELED`, `STALE`,
`UNAVAILABLE_AT_DETECTION`, `MISSING_DEFAULT_SUBSTITUTION`, `REDUNDANT`, `UNSUPPORTED`,
`UNKNOWN`. These are **methodology** judgements about a rule, never quality judgements
about a stock. The model has no score, rank, recommendation, or trading-label field,
and a test asserts that no such field is ever added.

`STALE` is descriptive only. Phase 2V applies no staleness threshold, because no
versioned policy defines one — consistent with ADR 0035 and 0039.

## 11. Outcome observation

`CandidateOutcomeObservation` is explicitly retrospective and explicitly **not** a
trade. It records reference price and time, per-window observations, maxima/minima,
time to maximum, adverse move, halt events, volume observations, sources, and
limitations.

Prohibited by construction — there is no field for any of these, so they cannot be
populated: fill price, entry, exit, position size, P&L, return on capital, stop,
target, or a "squeeze confirmed" verdict. Observed price movement, observed volume,
observed halts, short-interest evidence, borrow evidence, and causal interpretation are
kept in separate fields; the model never infers causation, and a price rise is never
auto-labelled a short squeeze.

Missing bars are never invented. For BIYA, no window is computable and the observation
records `VALIDATION_OUTCOME_DATA_INCOMPLETE` for every requested window.

## 12. Case conclusion

Exactly one `ValidationCaseConclusion` per case, from: `VALIDATED_AS_RECORDED`,
`PARTIALLY_VALIDATED`, `OUTCOME_CONFIRMED_METHODOLOGY_UNVERIFIED`,
`NOT_POINT_IN_TIME_VALID`, `INSUFFICIENT_EVIDENCE`.

The conclusion is **derived**, not authored: it is a deterministic function of the
detection-time state, the count of recovered versus unknown original values, the
replay's structural sufficiency, and the availability of outcome data. This prevents a
conclusion from drifting away from the evidence supporting it.

For BIYA the derivation yields **`INSUFFICIENT_EVIDENCE`**: no original value is
recoverable, so there is nothing to reproduce, compare, or invalidate. Note this is
*not* `OUTCOME_CONFIRMED_METHODOLOGY_UNVERIFIED` — that state requires a confirmed
outcome, and no BIYA outcome is confirmable from local evidence.

A rule enforced in code and asserted by test: **later evidence can never upgrade a
conclusion.** Adding outcome data to a case with no recoverable original values leaves
the conclusion at `INSUFFICIENT_EVIDENCE`.

## 13. Diagnostics

`ValidationDiagnosticCode` follows the Phase 2D convention that **only codes an
implemented path can actually emit are defined**. Ordering is deterministic
(`code`, `artifact_id`, `field_id`, `message`).

## 14. Public export

`build_public_validation_case` produces the demo's JSON by **whitelist projection** —
it constructs a new `PublicValidationCase` from named fields rather than copying and
stripping. Excluded unconditionally: absolute paths, `sensitive=True` artifacts,
credentials and tokens, personal names and email addresses, private URLs, and account
identifiers. The demo is a static page with no backend, no login, no tracker, and no
client-visible sensitive endpoint.

## 15. Isolation

The validation package contains no HTTP client, provider SDK, database write, GUI
framework, trading API, random id, wall-clock read in any identity path, pandas, numpy,
scipy, ML model, sentiment model, scoring, ranking, recommendation, alert, or order
placement. Tests require no network. These are asserted by isolation tests mirroring
`tests/readiness`'s existing ones.

## 16. Deliberate deviations from the brief

Recorded here so they are reviewable rather than silent:

1. **Original rules are reconstructed from `b016d92f`, not the archived HEAD.** The
   brief says to inspect the archived repositories; taken literally that would describe
   post-meeting code. Evidence (ART-004) overrides.
2. **The case conclusion is `INSUFFICIENT_EVIDENCE`.** The brief anticipates validating
   a successful prediction. The local record contains no such evidence and contains the
   advisor's contrary assessment.
3. **No outcome observation is produced for BIYA, and no public historical data is
   fetched.** Justified in §2/§11: the phase stays offline and deterministic, and the
   gap is recorded in the acquisition manifest.
4. **Only BIYA has a case.** KLRS, LBGJ, SG, TRVI, and SLS appear in ART-001 with no
   recoverable values, so they are registered as
   `ARTIFACT_DISCOVERY_ONLY`/`BLOCKED_MISSING_ORIGINAL_OUTPUT` rather than fabricated
   into cases.
