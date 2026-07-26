# Batch 08 — Phase 3A Request and Result Freeze Plan (preregistration)

Phase 3D controlled curation. Preregistered **before** any real Phase 3A request was
constructed and before any permitted private OHLCV was opened.

Task name: **Phase 3D Phase 3A Request and Result Freeze Batch 08**

This batch is **not** Phase 3B publication, outcome acquisition, outcome labelling,
expanded Phase 3C analysis, or Phase 3E.

## 1. Starting checkpoint (verified before any modification)

| Gate | Expected | Observed |
| --- | --- | --- |
| Branch | `batch/phase-3d-operation-specific-readiness-07` | matched |
| HEAD | `238986695c2bc053d54a6fd1037cdb145e9c5781` | matched |
| Working tree | clean except untracked `docs/phase-3c-complete-handoff.md` | matched |
| Remotes | none | matched |
| `phase-1-rc1^{}` | `f903d4d144d3f7e9717b1ab8e684da406d7968fb` | matched |
| Baseline suite | 2,256 passed / 1 skipped / 0 failed | 2,257 tests, 1 skipped, 0 failures, 0 errors |
| Batch 05 private raw hashes | 26 artifacts / 0 mismatches | matched |
| Archived parent HEAD | `0897562e05d75b812dd284de81dfafdfa1dea916` | matched |
| Archived nested submodule | `6dbefd1a6b271bfc48106c4aa002f211735551cd` | matched |

Batch 08 branch: `batch/phase-3d-phase3a-freeze-08`, created from the Batch 07 HEAD.

Schema version stays `1.0.0`.

## 2. Frozen cohort and source order

Exact source order, never reordered:

`XNCR, PESI, SLS, ZNTL, GPRE, SSPC, LBGJ, TRVI, LMNX, MGNX, BHVN, OBE, AVTX`

Case ids `BATCH01_<SYMBOL>_20260718`. The cohort, order, case ids, boundary, Batch 01
identities/eligibility, Batch 01/02 registry bytes, Batch 05 raw artifacts, Batch 06
semantics, and Batch 07 readiness results are all consumed read-only and unchanged.

Cohort and boundary are reused from the existing
`squeeze_core.acquisition.operation_readiness.evidence_inputs` (`FROZEN_COHORT`,
`FROZEN_BOUNDARY`, `boundary_id_for`). No second cohort list is created.

Frozen detection boundary: `2026-07-18T13:37:55.017661Z`.

## 3. Frozen policy versions

| Policy | Frozen value | Source |
| --- | --- | --- |
| Phase 3A request/result policy | `phase_3a_transparent_candidate_policy.v1` | `src/squeeze_core/evaluation/policies/phase_3a_transparent_candidate_policy_v1.json` |
| Phase 3A evaluation version | `candidate_evaluation.v1` | same policy file |
| Batch 07 readiness policy | `phase_3d_operation_readiness_policy.v1` | `operation_readiness.models` |
| Batch 06 semantic resolution | `phase_3d_ibkr_semantics_resolution.v1` | `operation_readiness.models` |
| Timestamp uncertainty | `bidirectional_1min_envelope.v1` | `operation_readiness.models` |
| Phase 2 readiness policy | `phase_2d_readiness_policy.v1` | `readiness.policies` |
| Metric calculation policy | `close_to_close_completed.v1` (metric version `1.0.0`) | `metrics.returns` |
| Batch 08 freeze policy (new) | `phase_3d_phase3a_freeze_policy.v1` | this batch |
| Receipt modeling policy (new) | `PROVIDER_AVAILABILITY_AS_RECEIPT.v1` | this batch, §7 |

No threshold, rule category, rule policy, or the 25-rule inventory is altered.

## 4. Global preflight is unchanged

The Batch 04 global preflight for the real IBKR detection-context bundles remains
`PREFLIGHT_REJECTED`. Batch 08 does not modify, suppress, reinterpret, or weaken it, and
creates no competing global-ready status. Batch 03 and Batch 04 validators are untouched.

Every frozen request and result cites **both**:

- the unchanged global preflight rejection (`PREFLIGHT_REJECTED`), and
- the Batch 07 per-case operation-specific admissibility record authorising the narrower
  operations actually used.

## 5. Admissible inputs (what a request may contain)

Only these, from Batch 07's authorisation:

- frozen case identity (`case_id`, symbol) and frozen boundary (`boundary_id`, `as_of`);
- outcome-blind Batch 01 candidate-discovery provenance (identifiers only);
- Batch 05 detection-context artifact identity (filename, request name, SHA-256, byte
  length, coverage metadata);
- Batch 06 documented price semantics (`SPLIT_ADJUSTED`) as provenance;
- Batch 07 operation-specific admissibility record ids and statuses;
- canonical `EventType.BAR` observations built from the **detection-context** artifact for
  bars that are *definitely completed* under the Batch 07 timestamp-uncertainty envelope;
- exactly one canonical `PERCENTAGE_RETURN` metric result (`MetricUnit.PERCENT`);
- canonical readiness records: one `DomainCoverageSnapshot`, one
  `EvidenceConflictSummary`, one `InputSufficiencyResult`.

## 6. Blocked inputs (omitted, never substituted)

Omitted entirely; missing fields stay missing, never zero, never fabricated:

- absolute-price evidence for `PRICE_RANGE`;
- any volume evidence or `RELATIVE_VOLUME` metric for `RELATIVE_VOLUME_MINIMUM`;
- `float_shares` (no detection-time float evidence exists);
- short interest, days-to-cover, borrow fee, borrow availability (no detection-time
  evidence exists);
- news, SEC filings, corporate actions (no detection-time evidence exists);
- scanner score, scanner tier, targets, sentiment predictions;
- current values represented as historical; synthetic values represented as historical;
- any future data; any outcome label.

### 6.1 How blocked evidence is withheld — request-level provider scope

The Phase 3A request contract (`RuleEvaluationRequest`) carries **one** shared
`input_observations` tuple; it has no per-rule evidence scoping. A `BAR` observation
supplied so `MARKET_DATA_AVAILABLE` can be evaluated inherently carries `close`, which
`PRICE_RANGE` would then consume as an absolute price level — evidence Batch 07 declared
`BLOCKED_MISSING_SEMANTICS`.

The contract's own supported mechanism for withholding is the `provider_scope_required`
gate. In the frozen Phase 3A policy that flag is set on exactly the rules Batch 07
blocked and unset on exactly the rules Batch 07 admitted:

| `provider_scope_required` | Rules |
| --- | --- |
| `true` | `PRICE_RANGE`, `FLOAT_MAXIMUM`, `PUBLISHED_SHORT_INTEREST_AVAILABLE`, `BORROW_FEE_MINIMUM`, `BORROW_AVAILABILITY_MAXIMUM` |
| `false` | `MARKET_DATA_AVAILABLE`, `COMPLETED_BAR_AVAILABLE`, `PERCENTAGE_CHANGE_MINIMUM`, `RELATIVE_VOLUME_MINIMUM`, and all remaining rules |

**Frozen decision:** the request sets `provider_scope = ()` (empty). Consequences, all
verified empirically against the existing evaluator before this plan was committed:

- `PRICE_RANGE` short-circuits at the provider-scope gate and **never reads a close
  price** — the blocked absolute-price operation is not performed;
- `FLOAT_MAXIMUM` short-circuits before any float lookup;
- `MARKET_DATA_AVAILABLE`, `COMPLETED_BAR_AVAILABLE`, and `PERCENTAGE_CHANGE_MINIMUM`
  still receive their admissible evidence (empty scope disables provider filtering rather
  than excluding evidence);
- `PROVIDER_SCOPE_EXPLICIT` resolves `UNKNOWN`. This is a consequence of the deliberate
  request-level omission, **not** a claim that the provider is unknown: the provider
  (`IBKR`) is recorded in every observation's provenance and in the metric record.
- three short-pressure availability rules report
  `EVALUATION_PROVIDER_SCOPE_REQUIRED` rather than the more specific
  `..._UNAVAILABLE`. Both are `UNKNOWN`; only the explanation code differs.

This is a **granularity limitation of the request contract**, documented rather than
patched. It is not an evaluator defect — the evaluator behaves exactly as its contract
specifies — and no evaluator code is modified.

## 7. Private OHLCV read boundary

Openable for bar values: **only** `raw/<SYMBOL>-detection-context.csv` for the 13 frozen
symbols (`DETECTION_CONTEXT_PRECEDING_24H`).

`FROZEN_FORWARD_24H` artifacts are hard-rejected for value access. A guard in
`evidence_adapter` raises `ForwardArtifactAccessError` on any path or request name
matching the forward request, and the reader accepts only paths whose filename ends
`-detection-context.csv`. Forward artifacts are referenced only by filename, request
name, SHA-256, byte length, existence, and preserved blocked status — never open, high,
low, close, volume, WAP, or trade count.

No Phase 3B outcome artifact or label is opened. A guard rejects any path under the
Phase 3B outcome roots.

## 8. Receipt-modeling policy (declared assumption)

`build_point_in_time_evidence` and `build_bar_series` gate on
`received_timestamp <= as_of`. The application actually received these bars on
2026-07-23 (Batch 05 collection), which is **after** the frozen boundary. Under a literal
local-receipt reading, every bar-dependent rule resolves `UNKNOWN`.

Batch 08 therefore declares its receipt modeling explicitly and reports both readings:

- **Primary — `PROVIDER_AVAILABILITY_AS_RECEIPT.v1`.** Each bar's `source_timestamp`
  (provider publication) is its conservative latest-possible completion instant
  (`label + 60 s`). The adapter's single `ingested_at` is the conservative availability
  instant of the *last included bar*, i.e. `max(label) + 60 s`, which is `<= as_of` for
  all 13 cases. This models what the *provider* had published by the boundary, which is
  the question a point-in-time replay asks, and is conservative (never earlier than the
  bar could possibly have completed). It is a declared reconstruction assumption, not a
  claim about local receipt.
- **Disclosed sensitivity — `LOCAL_RETRIEVAL_RECEIPT.v1`.** `ingested_at` is the Batch 05
  `retrieval_completed_at`. Reported as a deterministic sensitivity summary so the
  dependence is explicit and no reading is quietly preferred. This mirrors the existing
  Phase 2V practice of computing every boundary replay and reporting divergence as a
  finding rather than resolving it.

The canonical freeze is exactly 13 requests and 13 results under the primary policy. The
sensitivity is a summary artifact only and mints no request/result identity.

## 9. Temporal selection policy

Included bars: every detection-context bar whose label satisfies
`label + 60 s <= FROZEN_BOUNDARY` — "definitely completed" under the Batch 07
bidirectional 1-minute envelope, i.e. completed under **both** the START and END
interpretations. Bars that straddle the boundary are excluded, never repaired.

Observed for all 13 cases from the frozen request manifest: coverage
`2026-07-16T16:00:00Z .. 2026-07-17T23:59:00Z`; last label `+ 60 s = 2026-07-18T00:00:00Z`
`<= 2026-07-18T13:37:55.017661Z`. Every detection-context bar is therefore definitely
completed; no bar is excluded by the envelope.

### 9.1 Not arbitrarily choosing START or END

Bar boundaries are constructed under interpretation A (label = interval START, so
`[t, t+60)`), because `resolve_bar_at_boundary` matches boundaries by exact equality and
some convention must be declared. The choice is **not arbitrary**: it is value-invariant.

- The *set* of included bars is interpretation-independent (the envelope test
  `t + 60 <= boundary` holds under both readings).
- The *order* of bars is interpretation-independent.
- Reference and comparison bars are chosen by ordinal position within that set, not by
  absolute boundary matching, so the same two physical rows are selected either way and
  their `close` values are identical.

A committed test recomputes the metric under interpretation B (label = interval END,
`[t-60, t)`) and asserts the metric **value** and the selected close prices are
identical. Recorded bar-boundary references are interpretation-dependent provenance
labels and are disclosed as such.

### 9.2 Amendment A1 — bounded observation supply (found during implementation)

Preregistration assumed the request could carry every definitely-completed bar. Measured
during implementation, the existing `build_point_in_time_evidence` conflict detection is
superlinear in observation count (0.11 s at n=25, 0.42 s at n=50, 1.82 s at n=100, 12.73 s
at n=200), and the evaluator rebuilds that bundle once per bar-dependent rule. At the
observed 1,164–1,440 bars per artifact the freeze does not terminate in practical time.

That engine is **not** modified (§8 of the handoff forbids it, and it is not defective —
only superlinear). Instead the request's observation supply is bounded and declared:

`observation_supply_policy = ADMISSIBLE_METRIC_BOUNDARY_BARS`

The request carries exactly the observations the canonical `PERCENTAGE_RETURN` metric
consumed, taken from that metric's own `input_observation_ids` — the reference and
comparison boundary bars. Nothing is hand-picked.

What this does and does not change:

- The **metric is still computed over the full admissible window** (the Phase 2 metric
  path is linear: `build_bar_series` is 0.01–0.03 s at every size measured). The metric
  value is unaffected.
- No **rule outcome** changes: `MARKET_DATA_AVAILABLE` and `COMPLETED_BAR_AVAILABLE`
  resolve `PASS` on any non-empty completed-bar set.
- The **observed value** those two availability rules report is the count of bars *supplied
  to the request*, not the count in the artifact. Both numbers are recorded — the artifact
  count in `TemporalSelection.included_bar_count` and
  `EvidenceAssociation.observed_bar_count`, the supplied count in
  `TemporalSelection.supplied_observation_count` — so the distinction is explicit rather
  than hidden. Reported as a limitation.

## 10. Percentage-metric construction policy

Confirmed from the Phase 3A rule implementation before freezing:

| Property | Frozen value |
| --- | --- |
| Metric id | `PERCENTAGE_RETURN` (`MetricName.PERCENTAGE_RETURN`) |
| Metric version / policy | `1.0.0` / `close_to_close_completed.v1` |
| Input prices | `close` only (`PriceField.CLOSE`) |
| Reference observation | earliest definitely-completed detection-context bar |
| Comparison observation | latest definitely-completed detection-context bar |
| Threshold | `10` |
| Operator | `GREATER_THAN_OR_EQUAL` (inclusive) |
| Unit | `PERCENT` (`MetricUnit.PERCENT`) |
| Representation | exact `Decimal`, context precision 28 |

Computed **only** through the existing Phase 2 canonical path
`squeeze_core.metrics.returns.build_return_result` with
`MetricName.PERCENTAGE_RETURN`. No percentage formula is reimplemented, and a committed
test asserts the freeze package contains no arithmetic percentage expression.

Batch 07 authorised this as `ADMISSIBLE_WITH_CONSTRAINTS` with constraints "both boundary
bars must be definitely-completed under timestamp uncertainty" and "no ex-dividend instant
is assumed inside the window (prices are not dividend-adjusted)". Both are satisfied: both
boundary bars are definitely completed (§9), and the window is recorded so the
dividend assumption is inspectable. No absolute price level is used for any blocked
operation. No volume is used anywhere.

**Declared divergence.** This is the percentage close-to-close change across the whole
definitely-completed detection-context window. It is **not** a reproduction of the
original platform's intraday percentage-change reference, which would require session
boundaries that Batch 06 left `SESSION_COMPLETENESS_UNEVIDENCED`. The window definition
avoids session inference entirely. Reported as a limitation, not as an equivalent metric.

If the canonical inputs turn out to be unavailable, the request is preserved and the rule
resolves through canonical missingness behaviour. The metric is never fabricated.

## 11. Availability-rule evidence

`MARKET_DATA_AVAILABLE` and `COMPLETED_BAR_AVAILABLE` receive canonical
`EventType.BAR` observations carrying, per bar, verified artifact identity (SHA-256, byte
length), observed coverage metadata, `status = COMPLETED`, and boundaries from the frozen
envelope. Forward artifacts are not used. The existing evaluator determines
`PASS`/`FAIL`/`UNKNOWN`; no outcome is assigned by hand.

## 12. Blocked-rule behaviour

For every rule Batch 07 marked blocked, substantive evidence is omitted, the relevant
readiness/missingness record is included where the contract supports it, `null` is never
replaced by zero, no metric is fabricated, and no `FAIL` is forced. The existing
evaluator produces whatever canonical outcome follows.

Exact rule ids verified against the committed 25-rule inventory (this plan's shorthand is
not relied on):

- absolute price: `PRICE_RANGE`
- volume: `RELATIVE_VOLUME_MINIMUM`
- float: `FLOAT_MAXIMUM`
- seven short-pressure: `PUBLISHED_SHORT_INTEREST_AVAILABLE`,
  `SHORT_INTEREST_PERCENTAGE_CHANGE_MINIMUM`, `DAYS_TO_COVER_MINIMUM`,
  `BORROW_FEE_MINIMUM`, `BORROW_FEE_CHANGE_MINIMUM`, `BORROW_AVAILABILITY_MAXIMUM`,
  `BORROW_AVAILABILITY_CHANGE_MAXIMUM`
- five catalyst: `NEWS_AVAILABLE`, `NEWS_AVAILABLE_BEFORE_AS_OF`,
  `NEWS_TIMESTAMP_KNOWN`, `SEC_FILING_AVAILABLE`,
  `CORPORATE_ACTION_CONTEXT_AVAILABLE`

## 13. Readiness records and EVIDENCE_VALIDITY behaviour

Built with the existing canonical builders; nothing is reimplemented:

| Record | Builder | Requested scope |
| --- | --- | --- |
| `DomainCoverageSnapshot` | `readiness.coverage.build_domain_coverage_snapshot` | union of `required_domains` across the 25 policy rules, derived from the policy file (not hand-picked) |
| `EvidenceConflictSummary` | `readiness.conflicts.build_conflict_summary` | same domain set |
| `InputSufficiencyResult` | `readiness.sufficiency.build_input_sufficiency_result` | operation `PERCENTAGE_RETURN` — the one Phase 2 metric operation Batch 07 admitted and the only metric the request supplies |

The seven `EVIDENCE_VALIDITY` meta-rules are readiness-level `NOT_APPLICABLE` in Batch 07.
Batch 08 does **not** force their Phase 3A result outcomes. The request is built per the
actual contract and the existing evaluator decides. Observed canonical behaviour is
documented as-is and not adjusted for presentation.

Note in advance, so no reader is surprised: `REQUIRED_DOMAINS_PRESENT` is expected to
resolve `FAIL` because required non-market-bar domains are genuinely missing. That is a
statement about **evidence completeness of the request**, not about the candidate.

## 14. Freeze ordering

Per case, in this order, with no outcome access at any point:

1. acquisition/case plan (already frozen in Batch 01);
2. frozen case identity verified;
3. frozen boundary verified;
4. admissibility policy frozen (Batch 07 record);
5. evidence-association manifest frozen;
6. Phase 3A request serialized and frozen;
7. request SHA-256 and byte length recorded;
8. existing Phase 3A evaluator executed;
9. Phase 3A result serialized and frozen;
10. result SHA-256 and byte length recorded;
11. leakage audit run;
12. sanitized summary generated.

All 13 cases remain represented even if construction or evaluation fails for one.

## 15. Leakage audit

Reuses the existing Phase 3D infrastructure
(`acquisition.leakage_guards.audit_outcome_leakage` with `LeakageAuditRequest`). No second
audit engine is written. The audit proves, per case: plan precedes result; boundary
precedes result; evidence association precedes result; request precedes result; result
exists before any hypothetical outcome stage; no outcome artifact accessed; no forward
OHLCV accessed. `outcome_captured_at` is set to a sentinel strictly after every freeze
stage, since no outcome was captured at all.

Independent structural guards additionally record `forward_ohlcv_accessed = false` and
`outcome_accessed = false` from the reader's own access log, so the flags are observed,
not asserted.

## 16. Identity

UUIDv5 over canonical JSON via the existing `deterministic_acquisition_id`
(acquisition namespace) and the existing `canonical_json_bytes` serializer.

Request identity depends only on frozen pre-outcome inputs: `case_id`, `boundary_id`,
Phase 3A policy version, evaluation version, Batch 07 readiness policy version, Batch 06
semantic-resolution policy version, Batch 08 freeze policy version, receipt-modeling
policy, detection-context artifact SHA-256 and byte length, sorted enabled rule ids,
sorted admissible evidence ids, sorted metric ids, sorted readiness ids, and the frozen
temporal-selection descriptor.

Result identity additionally depends on the frozen request id, the ordered 25 rule
outcomes, per-rule supporting metric/evidence/readiness ids, and the evaluator's own
`CandidateEvaluationResult.deterministic_id`.

Excluded from identity: wall clock, retrieval time, absolute local paths, random ids,
credentials, outcomes, forward artifacts, unordered iteration. Stable case order, stable
rule order, stable evidence order, exact `Decimal` strings, explicit nulls, UTF-8, LF, no
NaN, no infinity. Every generator runs twice and bytes are compared.

## 17. Private versus committed outputs

Private (gitignored) real artifacts under
`intake/local-bars/ibkr-batch-05/phase3a/batch-08/`:

```
requests/BATCH01_<SYMBOL>_20260718.json
results/BATCH01_<SYMBOL>_20260718.json
metrics/BATCH01_<SYMBOL>_20260718.json
evidence-associations/BATCH01_<SYMBOL>_20260718.json
leakage/BATCH01_<SYMBOL>_20260718.json
manifests/case-manifest.json
sensitivity/local-retrieval-receipt-summary.json
batch-summary.json
determinism-anchors.json
freeze-report.md
```

Never committed: real bars, real metrics, real Phase 3A requests, real Phase 3A results,
private evidence associations, per-case values.

Committed: implementation, tests, synthetic fixtures, schemas/policies, sanitized
aggregate summaries, documentation. Sanitized aggregates may include counts by rule
outcome / rule id / category, counts of requests and results frozen, leakage-audit pass
counts, case ids, request/result ids, hashes, byte lengths, readiness categories, and
blocking reason codes. No raw OHLCV and no derived price or return value appears in any
committed document.

## 18. Implementation surface

New additive package `src/squeeze_core/acquisition/phase3a_freeze/`:
`models.py`, `evidence_adapter.py`, `metric_adapter.py`, `readiness_adapter.py`,
`request_builder.py`, `result_runner.py`, `freeze.py`, `leakage.py`, `serialization.py`,
`report.py`, `cli.py`, `__main__.py`.

Nothing is duplicated: metric formulas, rule evaluator logic, UUID infrastructure, the
canonical serializer, and the leakage-audit framework are all imported from their existing
homes. Offline CLI commands `generate-phase3a-freeze`, `verify-phase3a-freeze`,
`render-phase3a-freeze-report`. No command touches the network; no command imports or
connects through `ibapi`.

## 19. Aggregate outputs

13-case request-freeze summary; 13-case result-freeze summary; 25-rule outcome matrix;
outcome counts by rule; outcome counts by category; evidence-use matrix; missingness
matrix; leakage-audit summary; request/result determinism anchors; Phase 3B
publication-readiness **preview**.

The preview publishes nothing. It answers only whether each case now has a frozen
request, a frozen result, a passing leakage audit, and whether a future Phase 3B registry
revision could reference these paths. No outcome classification is computed. Rule
outcomes are never described as predictive performance.

## 20. Tests

Focused committed tests, all on synthetic fixtures, covering: exact Batch 07 checkpoint
constants; exact 13-case source order; exact boundary; global preflight remains
`PREFLIGHT_REJECTED`; only detection-context OHLCV can be opened; forward OHLCV access
hard-fails; Phase 3B outcome access hard-fails; no network; no `ibapi`; canonical Phase 2
metric reused; no ad hoc percentage formula; START/END value invariance;
`MARKET_DATA_AVAILABLE` and `COMPLETED_BAR_AVAILABLE` request support;
`PERCENTAGE_CHANGE_MINIMUM` uses only admissible inputs; `PRICE_RANGE` receives no
blocked absolute-price evidence and never reads a close; `RELATIVE_VOLUME_MINIMUM`
receives no volume evidence; no float / short-pressure / catalyst fabrication; all 25
rules present and ordered; the existing evaluator executes; no manual outcome assignment;
request frozen before result; result frozen before any outcome stage; 13 leakage audits
pass; request and result ids deterministic; synthetic generation byte-identical; no real
data committed; no score/rank/recommendation fields; no Phase 3B publication; no Phase 3E;
Batch 01–07 committed artifacts unchanged; Batch 05 private raw hashes unchanged; schema
remains `1.0.0`.

## 21. Stop conditions

Stop and report without improvising if: the checkpoint differs; the baseline cannot be
reproduced; prior committed artifacts are unexpectedly modified; Batch 05 private hashes
mismatch; Batch 07 readiness artifacts are missing or inconsistent; the evaluator cannot
accept a schema-valid request with missing inputs; construction requires fabricated
evidence; `PERCENTAGE_CHANGE_MINIMUM` requires inputs Batch 07 did not authorise;
execution requires weakening the global preflight, forward OHLCV, or outcome access; a
genuine evaluator defect is found; deterministic freezing would change prior serialized
bytes; implementation would require Phase 3B publication or begin Phase 3E.

A result dominated by `UNKNOWN` or `INSUFFICIENT_DATA` is **not** failure and is preserved
honestly.

## 22. Completion criteria

Checkpoint verified; baseline reproduced; this plan preregistered and committed before any
real request or permitted OHLCV read; exactly 13 canonical requests and 13 canonical
results; only Batch 07-admissible evidence used; blocked evidence still missing; all rule
outcomes produced by the existing evaluator; 25 rules per case in stable order; requests
and results frozen deterministically; 13 leakage audits pass; global preflight rejected and
unchanged; no forward OHLCV opened; no outcome accessed; no new data fetched; no Phase 3B
publication; real outputs private; synthetic fixtures committed; generators byte-identical;
focused and full suites pass; prior and archived artifacts unchanged; professor brief,
completion report, and an actual Batch 09 handoff exist; exact final HEAD reported; Phase
3E unstarted; work stops.
