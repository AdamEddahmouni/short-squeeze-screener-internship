# Batch 07 — Operation-Specific Evidence Admissibility and Phase 3A Readiness Audit (Preregistration)

Status: PREREGISTERED (frozen before implementation)
Branch: `batch/phase-3d-operation-specific-readiness-07`
Parent checkpoint: `ae1aa4e4cc82cc8aea5b49a58e2d6d3ed15a1e17` (Batch 06)
Baseline reproduced: 2,227 passed / 1 skipped / 0 failed (2,228 collected)
Phase: 3D / readiness-integration. **Not** Phase 3E. No outcome access. No new market data.

---

## 0. Purpose and non-goal

**Purpose.** Determine, per operation and per Phase 3A rule, which Phase 2 metrics
and Phase 3A rules can be *honestly supported* by the already-collected Batch 05
`DETECTION_CONTEXT_PRECEDING_24H` bars plus existing pre-outcome evidence, which
remain blocked, and exactly why.

**Non-goal.** This batch does **not** evaluate any Phase 3A rule (no PASS/FAIL), does
not construct or execute Phase 3A requests, does not read forward/outcome bar values,
does not weaken the Batch 04 global preflight, and does not begin Phase 3E.

The Batch 04 **global** preflight verdict for the 13 detection-context bundles stays
`PREFLIGHT_REJECTED`. Batch 07 introduces a strictly narrower, additional concept —
**operation-specific admissibility** — that answers *"can this evidence be used for
this exact operation under explicitly stated constraints?"* It never answers *"is the
artifact globally ready for unrestricted use?"* The two remain separate records.

---

## 1. Frozen cohort (exact source order — do not reorder)

| # | symbol | case_id |
|---|--------|---------|
| 1 | XNCR | BATCH01_XNCR_20260718 |
| 2 | PESI | BATCH01_PESI_20260718 |
| 3 | SLS  | BATCH01_SLS_20260718 |
| 4 | ZNTL | BATCH01_ZNTL_20260718 |
| 5 | GPRE | BATCH01_GPRE_20260718 |
| 6 | SSPC | BATCH01_SSPC_20260718 |
| 7 | LBGJ | BATCH01_LBGJ_20260718 |
| 8 | TRVI | BATCH01_TRVI_20260718 |
| 9 | LMNX | BATCH01_LMNX_20260718 |
| 10 | MGNX | BATCH01_MGNX_20260718 |
| 11 | BHVN | BATCH01_BHVN_20260718 |
| 12 | OBE  | BATCH01_OBE_20260718 |
| 13 | AVTX | BATCH01_AVTX_20260718 |

Frozen detection boundary (all 13): `2026-07-18T13:37:55.017661Z`.
Case membership, source order, case IDs, boundary, identity records, Batch 01/02
registry bytes are **immutable** in this batch.

---

## 2. Evidence inputs (frozen, read-only, no OHLCV)

Batch 07 reads only the following, all frozen and local:

1. **Batch 05 provenance manifests** (private, gitignored `intake/local-bars/ibkr-batch-05/`):
   - `requests/request-manifest.json` — per-request coverage **metadata only**:
     `first_timestamp_utc`, `last_timestamp_utc`, `bar_count`, `end_datetime`,
     `duration_str`, `bar_size_setting`, `use_rth`, `what_to_show`, `status`.
   - `provenance/artifact-manifest.json` and `provenance/sha256-manifest.json` —
     `csv_sha256`, `csv_byte_length` per artifact.
   These are **provenance/coverage** facts, never OHLCV values.
2. **Batch 06 resolved semantics** — `OFFICIAL_TRADES_EVIDENCE` →
   `resolve_ibkr_semantics(...)` = `ResolvedIbkrSemantics` (price=SPLIT_ADJUSTED,
   dividend=not adjusted, volume_adjustment=UNKNOWN, volume_unit=UNRESOLVED,
   timestamp=UNKNOWN/ABSENT, session=EXTENDED (useRTH=0), provider-filtered).
3. **Batch 01 frozen boundary** = the boundary above.

Only the `DETECTION_CONTEXT_PRECEDING_24H` request class is eligible for readiness
analysis. `FROZEN_FORWARD_24H` artifacts are **not** used as forward evidence; they
may be referenced by **filename/sha256/byte_length only** to prove they were not
touched. Their OHLCV contents are never opened. No re-classification, window shift,
or replacement request.

**Hard prohibition:** the `operation_readiness` runtime must never open a `raw/*.csv`
or `raw/*.jsonl` OHLCV artifact. A test asserts the package reads no `raw/` bar file.

---

## 3. Admissibility status vocabulary (deterministic, closed set)

```
ADMISSIBLE                 evidence supports this operation with no residual constraint
ADMISSIBLE_WITH_CONSTRAINTS evidence supports it only under explicitly stated constraints
BLOCKED_MISSING_SEMANTICS  a required semantic field is UNKNOWN/unresolved
BLOCKED_MISSING_EVIDENCE   a required evidence domain is absent from this evidence set
BLOCKED_ALIGNMENT          temporal/boundary alignment cannot be established conservatively
BLOCKED_CONFLICT           evidence conflicts materially
NOT_APPLICABLE             the operation does not depend on this evidence class at all
```

Rules:
- `UNKNOWN` is **never** collapsed into `FAIL`/`BLOCKED_CONFLICT`; it maps to
  `BLOCKED_MISSING_SEMANTICS`.
- Missing evidence is **never** treated as zero.
- No numeric confidence scores; no ranking; no recommendation.

---

## 4. Operation dependency model

Each operation declares two dependency layers:

**A. Evidence-domain dependencies** — reuses the existing Phase 2D
`OperationRequirementPolicy` (`required_domains`, `required_metric_names`,
`requires_trailing_window`). Batch 07 does not fork or mutate that policy set.

**B. Semantic-field dependencies (new, additive)** — each operation declares which of
these resolved/unresolved IBKR semantic fields materially affect its correctness:

```
price_adjustment_absolute   true if the operation compares an ABSOLUTE price level
price_adjustment_ratio      true if the operation uses a price RATIO within one series
dividend_adjustment         true if correctness needs a dividend-adjustment stance
volume_unit                 true if correctness depends on the volume unit
volume_corporate_action     true if correctness depends on volume corp-action handling
volume_filter_stationarity  true if correctness needs a constant provider-filter fraction
timestamp_boundary          true if the operation needs bar START/END disambiguation
session_completeness        true if the operation needs complete session coverage
```

An operation is admissible only if **every** declared semantic dependency is satisfied
by resolved evidence (or shown formally invariant), and every required evidence domain
is present in the evidence set, and temporal alignment (if required) is established.

The dependency matrix is pure declarative data (`dependencies.py`), no formula logic.

---

## 5. Timestamp-uncertainty policy (frozen)

Batch 06 established timestamp representation = epoch seconds / UTC, but **not** whether
the epoch marks interval START or END. Bar size = 1 minute (60 s).

For each bar timestamp `t`, the true 1-minute interval is exactly one of:
- interpretation A (t = START): `[t, t + 60s]`
- interpretation B (t = END):   `[t - 60s, t]`

Derived predicates (exact `datetime`/`timedelta` arithmetic, no float):
- **definitely completed before** boundary `B` ⟺ `max(A.end, B.end) = t + 60s ≤ B`
  AND `t ≤ B` — i.e. the later of the two possible completion instants (`t + 60s`) is
  `≤ B`. (Because A.end = t+60s ≥ B.end = t, the binding instant is `t + 60s`.)
- **definitely outside** a window `[w0, w1]` ⟺ both interpretations lie entirely
  outside `[w0, w1]`.
- **straddles** a critical boundary ⟺ neither "definitely before" nor "definitely
  after" holds ⟹ `BLOCKED_ALIGNMENT`.

The original event timestamp is never mutated. Uncertainty is represented explicitly as
an envelope `[t - 60s, t + 60s]` of possible completion instants.

Edge cases unit-tested at `boundary ± {61, 60, 59, 0} seconds`.

Observed fact for this cohort: last detection-context bar `t = 2026-07-17T23:59:00Z`;
`t + 60s = 2026-07-18T00:00:00Z ≤ boundary 2026-07-18T13:37:55.017661Z` ⟹ the final bar
is **definitely completed before** the boundary under both interpretations; no bar
straddles the boundary.

---

## 6. Price-semantic policy (frozen)

Resolved: `SPLIT_ADJUSTED`, **not** dividend-adjusted.

- **Ratio operations** (e.g. `PERCENTAGE_RETURN`): a split applies one uniform
  multiplicative factor to *every* bar in a single returned series, so it cancels in a
  within-series price ratio. Percentage return is therefore **invariant** to split
  adjustment and does not require dividend adjustment for an intraday close-to-close
  window ⟹ eligible for `ADMISSIBLE_WITH_CONSTRAINTS` (constraint: both boundary bars
  definitely completed; no ex-dividend instant inside the window — the latter is not
  disprovable here but does not change a split-invariant ratio materially for intraday
  bars, and is recorded as a stated constraint).
- **Absolute-price-level operations** (e.g. `PRICE_RANGE`, a fixed \$2–\$20 band): the
  comparison is against an external fixed dollar threshold, so it is **not** invariant to
  the adjustment factor. A split occurring between the frozen boundary (2026-07-18) and
  the Batch 05 retrieval instant (2026-07-24) would shift the split-adjusted level away
  from the boundary-time level. Corporate-action evidence to confirm no such split is
  **not** collected in Batch 07 and must not be inferred ⟹ `BLOCKED_MISSING_SEMANTICS`
  (reason: absolute level needs corporate-action confirmation over the boundary→retrieval
  gap). This is *not* "require RAW because history once used RAW"; it is a genuine
  non-invariance to an unresolved corporate-action state.

No conversion to raw prices; no reverse corporate-action reconstruction.

---

## 7. Volume-semantic policy (frozen)

Batch 06 left `volume_adjustment_semantics = UNKNOWN`, `volume_unit = UNRESOLVED`;
the feed is provider-filtered.

Conservative default: **every volume-dependent operation is `BLOCKED_MISSING_SEMANTICS`**
unless its requirement is proven formally invariant to *all* unresolved fields under the
actual implementation and evidence. The multiplicative-unit-invariance argument for a
ratio (`RELATIVE_VOLUME`) is **insufficient** because:
1. unit constancy across target bar and trailing baseline is not established by evidence
   (`volume_unit` UNRESOLVED) and may not be inferred from magnitudes;
2. `volume_corporate_action` handling is UNKNOWN, so a split inside the trailing window
   could scale bars non-uniformly;
3. the provider-filter fraction is not shown stationary across the window, so the ratio's
   numerator and denominator may be filtered by different fractions.

No inference of shares vs lots. No projection of the current Gateway lots setting backward
onto Batch 05. No inference from bar magnitudes. Any future invariance claim must be
explicit, mathematical, unit-tested, and outcome-independent.

---

## 8. Session / provider-filtering policy (frozen)

`useRTH = 0` (extended session eligible) is a *request parameter*, not proof of complete
24-hour or consolidated-market coverage. Historical TRADES data is provider-filtered.

- Operations requiring **complete session coverage / consolidated volume** ⟹
  `BLOCKED_MISSING_EVIDENCE` (completeness not evidenced).
- Filtering is **irrelevant to price-only operations**; such operations are not blocked
  merely because volume is filtered. Dependency-specific reasoning governs.

---

## 9. Coverage policy (frozen, per artifact)

Record, from frozen provenance metadata only:
`requested_window` (end = boundary, duration 86400 s), `observed_coverage_start/end`,
`bar_count`, `bar_interval`, frozen boundary, `max_possible_final_bar_completion` (last
`t + 60s`), `gap_from_definitely_completed_to_boundary`. Never inspect price direction or
compute forward returns. The Saturday-boundary / Friday-last-data relationship is a
temporal coverage fact used only for readiness/alignment.

---

## 10. Phase 3A rule dependency audit (all 25 rules)

For each of the 25 enabled rules in
`evaluation/policies/phase_3a_transparent_candidate_policy_v1.json` record: rule_id,
category, required evidence domains, required metrics, required semantic fields, whether
the Batch 05 detection-context evidence touches them, resulting operation-specific
admissibility status, and reason codes. **No PASS/FAIL. No rule evaluation.**

Categories: MOMENTUM_DISCOVERY, SHORT_PRESSURE_CONFIRMATION, CATALYST_EVIDENCE,
EVIDENCE_VALIDITY.

Frozen mapping of the 6 rules that touch MARKET_BARS (the only domain Batch 05 supplies):

| rule | dependency character | frozen expected status |
|------|----------------------|------------------------|
| MARKET_DATA_AVAILABLE | MARKET_BARS existence only | ADMISSIBLE |
| COMPLETED_BAR_AVAILABLE | MARKET_BARS + timestamp boundary | ADMISSIBLE (final bar definitely completed) |
| PERCENTAGE_CHANGE_MINIMUM | PERCENTAGE_RETURN (price ratio) | ADMISSIBLE_WITH_CONSTRAINTS |
| PRICE_RANGE | absolute price level | BLOCKED_MISSING_SEMANTICS |
| RELATIVE_VOLUME_MINIMUM | RELATIVE_VOLUME (volume) | BLOCKED_MISSING_SEMANTICS |
| FLOAT_MAXIMUM | CANDIDATE_SNAPSHOT domain | NOT_APPLICABLE (bars) / BLOCKED_MISSING_EVIDENCE (rule) |

All 19 non-MARKET_BARS rules are `NOT_APPLICABLE` to the detection-context bars, and
`BLOCKED_MISSING_EVIDENCE` at rule level (their domains are not in this evidence set).
EVIDENCE_VALIDITY meta-rules are recorded with `PHASE3A_REQUEST_SCHEMA_REVIEW_REQUIRED`-
style dependency notes (they depend on the full assembled request, not on the bars alone).

---

## 11. Phase 3A request-readiness (per case, no execution)

Question: can a syntactically **and** semantically valid `RuleEvaluationRequest` be
constructed **without fabrication**? The Phase 3A contract
(`evaluation/models.py::RuleEvaluationRequest`) defaults `input_observations`,
`input_metrics`, `input_readiness_results` to empty tuples, and `RuleOutcome` includes
`INSUFFICIENT_DATA` / `UNKNOWN`. Therefore a request built from **frozen identity only**
(symbol, `as_of` = frozen boundary, `policy_version`, the 25 `enabled_rule_ids`,
`asset_class=EQUITY`) is valid and requires no guessed values; absent-evidence rules
resolve to `INSUFFICIENT_DATA`/`UNKNOWN` as the contract permits.

Per-case value vocabulary:
```
PHASE3A_REQUEST_READY               a non-fabricated schema-valid request is constructible
PHASE3A_REQUEST_BLOCKED             the schema requires evidence that cannot be supplied
PHASE3A_REQUEST_SCHEMA_REVIEW_REQUIRED  construction would cross into evaluation/ambiguous
```

Frozen determination: all 13 cases = `PHASE3A_REQUEST_READY` (skeleton constructible from
frozen identity). This "READY" is explicitly narrow: it does **not** assert that Batch 05
bars can be admitted as request inputs for the momentum market-bar rules — that admission
is governed per-operation by §6–§8 and, where admissible, is deferred to a future batch
because it would require reading OHLCV and passing intake (both out of Batch 07 scope).
Batch 07 records the determination but **does not instantiate or execute** any request.

If, during implementation, constructing the determination were found to require actually
building/evaluating a request, the batch stops at readiness and reports
`PHASE3A_REQUEST_SCHEMA_REVIEW_REQUIRED` instead (stop condition §17.9 of the handoff).

---

## 12. Case-association boundary (frozen)

Each `DETECTION_CONTEXT_PRECEDING_24H` artifact is associated with its case using only:
frozen symbol, frozen case_id, Batch 05 request provenance, Batch 05 resolved contract,
Batch 01 frozen boundary, artifact sha256, artifact byte_length. Never using: bar
outcomes, future price movement, research classification, scanner score/tier, sentiment,
targets, later outcome labels. Association is a new Batch 07 readiness artifact — **not**
Phase 3B publication — and does not alter Batch 01/02 registry records.

---

## 13. Output schemas (schema_version = 1.0.0)

Per-case readiness record fields (§18 of handoff), all present, no outcome/score/ranking/
recommendation fields:
`case_id, symbol, frozen_boundary_id, detection_context_artifact_sha256,
artifact_byte_length, requested_window, observed_coverage_start, observed_coverage_end,
bar_interval, timestamp_representation, timestamp_interval_semantics,
timestamp_uncertainty_policy, price_adjustment_semantics, volume_adjustment_semantics,
volume_unit_semantics, session_request_policy, provider_filtering_disclosure,
price_operation_readiness, volume_operation_readiness, temporal_alignment_readiness,
phase2_metric_readiness, phase3a_rule_dependency_readiness, phase3a_request_readiness,
blocking_reason_codes, supporting_evidence_ids, supporting_semantic_resolution_ids`.

Aggregate outputs: operation dependency matrix, Phase 2 metric readiness matrix, 25-rule
Phase 3A dependency matrix, 13-case readiness matrix, missing-evidence frequency summary,
semantic-blocker frequency summary, alignment-blocker summary, request-readiness summary.
All summaries descriptive with explicit denominators. No "accuracy/performance/predictive/
validation success" language.

Serialization: `squeeze_core.serialization.canonical_json_bytes` (UTF-8, sorted keys,
explicit nulls, exact Decimal strings, compact separators) + trailing LF for the
committed JSON artifact. Ordered `cases` list preserves frozen source order. Markdown
reports rendered from the same frozen model.

---

## 14. Deterministic identity (frozen)

Reuse `_FrozenAcquisitionModel` (UUIDv5 over canonical JSON via
`deterministic_acquisition_id`, `ACQUISITION_NAMESPACE`). Association/readiness identity
depends only on frozen pre-outcome inputs: case_id, boundary_id, artifact sha256,
artifact byte_length, semantic-resolution policy version, operation-readiness policy
version. No wall clock, absolute path, outcome, future bar, random value, unordered
iteration, or credential enters identity. All generators run twice and compared byte-for-
byte.

---

## 15. Implementation surface

`src/squeeze_core/acquisition/operation_readiness/`:
- `models.py` — status enums, reason-code enum, `SemanticDependency`, `OperationDependency`,
  `OperationAdmissibility`, `TimestampUncertaintyEnvelope`, `Phase3ARuleDependencyRecord`,
  `CaseOperationReadiness`, `OperationReadinessReport`. All frozen; schema 1.0.0.
- `dependencies.py` — declarative operation + 25-rule dependency data.
- `timestamp_uncertainty.py` — envelope predicates (exact datetime arithmetic).
- `admissibility.py` — deterministic (dependency + resolved semantics + coverage) → status.
- `phase3a_readiness.py` — 25-rule dependency records + per-case request readiness.
- `association.py` — deterministic association identity from frozen inputs.
- `evidence_inputs.py` — loads frozen provenance manifests (metadata only; refuses `raw/`).
- `report.py` / generator — assembles the `OperationReadinessReport`.
- `serialization.py` — canonical JSON + markdown rendering.

Generator script `scripts/generate_batch07_operation_readiness_outputs.py` and CLI
subcommands `generate-operation-readiness` / `render-operation-readiness-report`. No
`ibapi` import, no network, no DB, no live-data code.

Committed outputs: `docs/` reports + committed canonical fixtures under
`tests/fixtures/acquisition/batch07/` (synthetic coverage metadata mirroring the real
provenance shape, so tests never depend on the private gitignored bars).

---

## 16. Tests (must all pass; full suite green)

Global preflight remains REJECTED and is not mutated; operation readiness does not touch
it; price-only op does not require volume semantics; volume-dependent op blocks on
unresolved semantics unless formally invariant; no inference from volume magnitude; no
shares-vs-lots inference; timestamp envelope predicates; definitely-completed-before
logic; straddle → BLOCKED_ALIGNMENT; split-adjusted ratio readiness; absolute-price op
blocks; provider-filtering dependency behavior; session-policy dependency behavior;
observed-coverage handling; all 13 associations deterministic; association uses no outcome
data; 25-rule matrix covers all 25; no PASS/FAIL emitted; request readiness does not
execute Phase 3A; no forward-bar reads / no `raw/` OHLCV reads; no case scores / ranking /
recommendation fields; Batch 01–06 committed artifacts unchanged; Batch 05 private hashes
unchanged; schema stays 1.0.0; generator byte-identical across two runs. Synthetic
fixtures only; no real IBKR bar data committed.

---

## 17. Stop conditions (report and halt, do not improvise)

Checkpoint differs; baseline not reproducible; prior artifacts modified; private Batch 05
hashes mismatch; operation readiness would require weakening the global preflight;
readiness cannot be represented without changing schema 1.0.0; association would require
guessing identity; a dependency cannot be determined from the implementation; request
readiness cannot be assessed without executing Phase 3A; completion would require reading
forward/outcome bars, new market data, guessing unresolved semantics, outcome access, or
beginning Phase 3E. Conservative BLOCKED results are valid outcomes.

## 18. Completion criteria

All of handoff §29 satisfied: checkpoint verified, baseline reproduced, architecture
audited, plan preregistered, dependency matrix built, unresolved semantics preserved,
global preflight unchanged, temporal uncertainty conservative, price/volume evaluated
independently, exactly 13 associations for readiness only, every relevant Phase 2 metric
has readiness, all 25 rules have dependency readiness, each case has request readiness,
no Phase 3A evaluation, no outcome/forward access, deterministic byte-identical outputs,
tests pass, prior + Batch 05 bytes unchanged, archived topology unchanged, completion
report + real Batch 08 handoff exist, final HEAD reported, Phase 3E unstarted, work stops.
