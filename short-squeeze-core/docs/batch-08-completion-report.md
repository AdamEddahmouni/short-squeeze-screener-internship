# Batch 08 — Completion Report

**Phase 3D Phase 3A Request and Result Freeze Batch 08**

Status: **complete**. Exactly 13 canonical Phase 3A requests and 13 canonical Phase 3A
results were constructed from Batch 07-admissible evidence only, evaluated by the existing
Phase 3A evaluator, and frozen deterministically. Phase 3E remains unstarted.

## 1. Checkpoints

| | Branch | HEAD |
| --- | --- | --- |
| Starting | `batch/phase-3d-operation-specific-readiness-07` | `238986695c2bc053d54a6fd1037cdb145e9c5781` |
| Final | `batch/phase-3d-phase3a-freeze-08` | the `chore: finalize Phase 3A freeze batch 08` commit below; verify with `git rev-parse HEAD` |

## 2. Commits

| Hash | Subject |
| --- | --- |
| `a1fe11d808c0be16537fa15743dfaab06f73a657` | docs: preregister Phase 3A freeze batch 08 |
| `2bf541f086c988032f3b76762f8faa19333c01b0` | feat: add admissible Phase 3A request construction and result freeze |
| `bb2973e54b320f4616857a2c970534a531b040dd` | test: add Batch 08 evaluation and leakage coverage |
| `f59fe5374efd4ccb3b3a0ba81ab0e8adb5241805` | docs: report Batch 08 evaluation findings, professor brief, and Batch 09 handoff |
| this commit | chore: finalize Phase 3A freeze batch 08 (final HEAD) |

No approved checkpoint was amended or rewritten.

One same-session correction was made: an earlier attempt at the documentation commit
accidentally staged the pre-existing untracked file `docs/phase-3c-complete-handoff.md`,
which the handoff required to be left untouched. That commit was never a checkpoint and
was never pushed (the repository has no remotes); it was replaced by
`f59fe5374efd4ccb3b3a0ba81ab0e8adb5241805`, which contains the nine Batch 08 documents
only. The file is untracked again and its content is unmodified.

## 3. Test totals

| | Result |
| --- | --- |
| Baseline (Batch 07 HEAD) | 2,256 passed / 1 skipped / 0 failed |
| Final (Batch 08 HEAD) | 2,319 passed / 1 skipped / 0 failed |
| Net new tests | +63 |

The single pre-existing skip is unchanged. No prior test was modified, skipped, or weakened.

## 4. Policies

| Policy | Value |
| --- | --- |
| Phase 3A request/result policy | `phase_3a_transparent_candidate_policy.v1` |
| Phase 3A evaluation version | `candidate_evaluation.v1` |
| Batch 08 freeze policy | `phase_3d_phase3a_freeze_policy.v1` |
| Receipt modeling (primary) | `PROVIDER_AVAILABILITY_AS_RECEIPT.v1` |
| Receipt modeling (disclosed sensitivity) | `LOCAL_RETRIEVAL_RECEIPT.v1` |
| Observation supply | `ADMISSIBLE_METRIC_BOUNDARY_BARS` |
| Timestamp interpretation (serialization) | `LABEL_IS_INTERVAL_START` (value-invariant) |
| Schema | `1.0.0` |

No threshold, rule category, rule policy, or the 25-rule inventory was altered.

## 5. Counts

- Requests frozen: **13**
- Results frozen: **13**
- Leakage audits passed: **13 / 13**
- Rule-case pairs: **325** (25 rules × 13 cases)
- Outcomes: `PASS` 97, `FAIL` 20, `UNKNOWN` 208, `CONFLICTED` 0, `INSUFFICIENT_DATA` 0,
  `NOT_APPLICABLE` 0

By category:

| Category | `PASS` | `FAIL` | `UNKNOWN` | Denominator |
| --- | --- | --- | --- | --- |
| `MOMENTUM_DISCOVERY` | 32 | 7 | 39 | 78 |
| `SHORT_PRESSURE_CONFIRMATION` | 0 | 0 | 91 | 91 |
| `CATALYST_EVIDENCE` | 0 | 0 | 65 | 65 |
| `EVIDENCE_VALIDITY` | 65 | 13 | 13 | 91 |

Full per-rule and per-case tables:
[batch-08-phase3a-rule-outcome-summary.md](batch-08-phase3a-rule-outcome-summary.md).

## 6. Confirmations

| Confirmation | Status |
| --- | --- |
| Batch 04 global preflight unchanged | `PREFLIGHT_REJECTED`, echoed in every record; the report model raises on any other value |
| No forward OHLCV opened | reader hard-blocks; every record carries `forward_ohlcv_accessed = false`, computed from an access log |
| No outcome accessed | reader hard-blocks; every record carries `outcome_accessed = false` |
| No new data fetched | no network import anywhere in the package (AST-verified); no `ibapi` import |
| No Phase 3B publication | `phase3b_published = false`; the preview model raises if publication is ever recorded |
| Phase 3E unstarted | `phase3e_started = false` |
| Batch 05 raw integrity | 26 artifacts, 0 mismatches |
| Prior committed artifacts | unchanged; full suite green |
| Archived parent topology | `0897562e05d75b812dd284de81dfafdfa1dea916` |
| Archived nested submodule | `6dbefd1a6b271bfc48106c4aa002f211735551cd` |
| Determinism | private generation run twice, byte-identical; `verify-phase3a-freeze` 26/0; committed golden byte-identical |
| Real data committed | none — private root is gitignored; committed artifacts are synthetic only |

## 7. Private output path

```
intake/local-bars/ibkr-batch-05/phase3a/batch-08/
  requests/                 13 canonical Phase 3A requests
  results/                  13 canonical Phase 3A results
  metrics/                  13 PERCENTAGE_RETURN metric records
  evidence-associations/    13 frozen evidence associations
  leakage/                  13 per-case freeze records with audit status
  manifests/case-manifest.json
  sensitivity/local-retrieval-receipt-summary.json
  batch-summary.json
  determinism-anchors.json
  freeze-report.md
```

Real freeze report id: `a800d6a2-947a-5ee7-b1d5-f55842a9c0e7`.
Committed synthetic golden report id: `2f633db9-e7b9-5b16-a734-0f7f8c0d94ef`.

## 8. Deviations from the preregistered plan

Two, both recorded in the plan itself and neither changing a rule outcome:

**A1 — bounded observation supply.** The plan assumed every definitely-completed bar could
be attached to a request. Measured during implementation,
`build_point_in_time_evidence` conflict detection is superlinear (12.73 s at 200
observations) and the evaluator rebuilds that bundle per bar-dependent rule; at 1,164–1,440
bars per artifact the freeze does not terminate in practical time. The engine was not
modified. The request now carries exactly the observations the canonical metric consumed.
The metric is still computed over the full admissible window, and a committed test proves
the wider supply yields identical outcomes and an identical metric value. The only visible
effect is that the two availability rules report the supplied count (2) rather than the
artifact count, both of which are recorded.

**A2 — declared receipt modeling.** Not a departure from the plan, which preregistered it,
but the most consequential assumption in the batch and worth restating here: the
point-in-time engine gates on `received_timestamp <= as_of`, and the application really
received these bars after the boundary. The primary freeze models receipt as the
conservative provider-availability instant; the literal local-receipt reading is computed
and reported as a disclosed sensitivity, under which the three bar-dependent rules move to
`UNKNOWN`.

## 9. Limitations

- The frozen boundary falls on a weekend; the forward window is not a trading window.
- No valid forward-outcome data exists and none was accessed, so there are no outcome
  labels and no predictive claim of any kind is made.
- Volume semantics remain unresolved, so every volume-dependent operation stays blocked.
- Absolute-price corporate-action semantics remain unconfirmed, so price-band screening
  stays blocked.
- Float, short-pressure, and catalyst evidence were never collected at detection time — 13
  of 25 rules have no evidence at all.
- `PERCENTAGE_CHANGE_MINIMUM` is evaluated over the whole definitely-completed detection
  window, not the original platform's intraday reference, because session boundaries are
  unevidenced. It should not be read as a replication of the original scanner metric.
- The `PERCENTAGE_CHANGE_MINIMUM` threshold is still marked `provisional` in the policy.
- `PROVIDER_SCOPE_EXPLICIT` resolves `UNKNOWN` as a consequence of the deliberate
  request-level provider-scope omission, not because the provider is unknown.
- No P&L, backtest, alerting, or trading capability exists or was built.

## 10. Phase 3E stop statement

**Phase 3E was not started in Batch 08 and remains unstarted.** No Phase 3E module, model,
document, test, or artifact was created, and every frozen record carries
`phase3e_started = false`, enforced by a model validator that raises on any other value.

## 11. Key documents

| Document | Path |
| --- | --- |
| Preregistered plan | `docs/batch-08-phase3a-request-result-freeze-plan.md` |
| Admissible evidence mapping | `docs/batch-08-admissible-evidence-mapping.md` |
| Request construction | `docs/batch-08-phase3a-request-construction.md` |
| Rule outcome summary | `docs/batch-08-phase3a-rule-outcome-summary.md` |
| Leakage and determinism | `docs/batch-08-leakage-and-determinism-report.md` |
| Phase 3B publication-readiness preview | `docs/batch-08-phase3b-publication-readiness-preview.md` |
| Test and verification report | `docs/batch-08-test-and-verification-report.md` |
| Professor brief | `docs/batch-08-professor-brief.md` |
| Batch 09 handoff | `docs/batch-09-fresh-session-handoff.md` |

## 12. Recommended next task

Exactly one: **await the supervisor's decision on the Phase 3B registry revision** described
in the professor brief, then execute whichever branch of `docs/batch-09-fresh-session-handoff.md`
§8 that decision selects. Batch 08 does not start it.
