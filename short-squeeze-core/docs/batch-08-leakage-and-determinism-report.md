> Companion to [batch-08-phase3a-request-result-freeze-plan.md](batch-08-phase3a-request-result-freeze-plan.md).

# Batch 08 — Leakage and Determinism Report

## 1. Freeze ordering (all 13 cases)

Each case was frozen in the mandated order, with no outcome access at any point:

| # | Stage | Artifact |
| --- | --- | --- |
| 1 | acquisition/case plan | frozen in Batch 01, consumed read-only |
| 2 | frozen case identity verified | case id and symbol checked against the Batch 07 record |
| 3 | frozen boundary verified | boundary id recomputed with the project's own identifier and compared |
| 4 | admissibility policy frozen | Batch 07 record id + association id bound |
| 5 | evidence-association manifest frozen | `EvidenceAssociation`, UUIDv5 |
| 6 | Phase 3A request serialized and frozen | canonical JSON bytes |
| 7 | request SHA-256 + byte length recorded | `FrozenArtifactRef` |
| 8 | existing evaluator executed | `squeeze_core.evaluation.evaluate_candidate` |
| 9 | Phase 3A result serialized and frozen | canonical JSON bytes |
| 10 | result SHA-256 + byte length recorded | `FrozenArtifactRef` |
| 11 | leakage audit run | existing Phase 3D audit engine |
| 12 | sanitized summary generated | aggregate report |

Construction raises rather than proceeds if the Batch 07 record, boundary id, or artifact
hash disagrees, so a mismatched case cannot be silently frozen.

## 2. Leakage audit

The audit is the existing `acquisition.leakage_guards.audit_outcome_leakage`; no second
engine was written. Freeze stage times are logical ordinals anchored on the frozen
boundary, so re-running produces byte-identical audit inputs and no wall clock enters
identity.

Result: **13 of 13 passed**, every one with diagnostic codes exactly
`("LEAKAGE_AUDIT_PASSED",)`.

What the audit proves per case:

| Property | How |
| --- | --- |
| plan precedes result | ordinal 0 < ordinal 4 |
| boundary precedes result | ordinal 1 < ordinal 4 |
| evidence association precedes result | ordinal 2 < ordinal 4, checked explicitly by `ordering_holds` |
| request precedes result | ordinal 3 < ordinal 4 |
| result precedes any hypothetical outcome stage | ordinal 4 < the no-outcome sentinel at ordinal 5 |
| no outcome field entered any layer | token scan over the declared discovery / eligibility / boundary / evaluation field names |
| discovery and outcome manifests are separate | distinct manifest ids |
| no outcome-aware or maximum-return selection | all four selection flags false |

## 3. Structural isolation guards

Beyond the audit, isolation is **observed** rather than asserted. The evidence reader
appends every accepted open to an access log, and `forward_ohlcv_accessed` /
`outcome_accessed` on each frozen record are computed from that log.

| Guard | Behaviour | Test |
| --- | --- | --- |
| forward artifact | `ForwardArtifactAccessError`, nothing opened | `test_forward_artifact_access_hard_fails` |
| Phase 3B outcome artifact | `OutcomeArtifactAccessError`, nothing opened | `test_phase3b_outcome_artifact_access_hard_fails` |
| any non-detection-context path | `NonDetectionContextArtifactError` | `test_only_detection_context_artifacts_may_be_opened` |
| row-level request-name check | a detection-context file containing a forward request name raises | in `load_detection_context_bars` |
| no network, no `ibapi` | AST import scan over every package module | `test_package_imports_no_network_or_ibapi` |

Forward artifacts are still cited — by filename, request id, SHA-256, byte length,
existence, and preserved `PREFLIGHT_REJECTED` status — which is exactly the evidence that
they were left untouched.

All 13 records carry `outcome_accessed = false`, `forward_ohlcv_accessed = false`,
`phase3b_published = false`, `phase3e_started = false`. The model raises on any other
value, so these cannot be set true even by mistake.

## 4. Determinism

Identity is UUIDv5 over canonical JSON via the project's existing
`deterministic_acquisition_id` and `canonical_json_bytes`. Excluded from identity: wall
clock, retrieval time, absolute local paths, random ids, credentials, outcomes, forward
artifacts, unordered iteration. A test parses `serialization.py` and fails on any use of
`now`, `utcnow`, `time`, `random`, `uuid4`, or on any string mentioning retrieval,
absolute paths, ingestion, or receipt.

| Check | Result |
| --- | --- |
| Private real generation run twice, full recursive byte diff | identical |
| `verify-phase3a-freeze` against on-disk artifacts | 26 artifacts, 0 mismatches |
| Synthetic golden generation run twice | identical |
| Committed golden JSON + Markdown compared byte-for-byte in tests | identical |
| Same case frozen twice: request id, result id, record id, request bytes, result bytes | identical |
| Tamper detection: one byte appended to a request | `verify` returns 1 |

Ordering guarantees: stable case order (frozen source order), stable rule order (sorted
rule id), stable evidence order (sorted ids), exact `Decimal` strings, explicit nulls,
UTF-8, LF, no NaN, no infinity.

## 5. Determinism anchors

| Anchor | Value |
| --- | --- |
| Real freeze report id | `a800d6a2-947a-5ee7-b1d5-f55842a9c0e7` |
| Committed synthetic golden report id | `2f633db9-e7b9-5b16-a734-0f7f8c0d94ef` |
| Frozen boundary | `2026-07-18T13:37:55.017661Z` |
| Requests frozen | 13 |
| Results frozen | 13 |
| Leakage audits passed | 13 |

Per-case request and result ids are listed in
[batch-08-phase3a-rule-outcome-summary.md](batch-08-phase3a-rule-outcome-summary.md) §4,
and per-case anchors are written to the private `determinism-anchors.json`.

## 6. Prior-artifact integrity

| Artifact set | Verification | Result |
| --- | --- | --- |
| Batch 05 private raw bars | `ibkr_historical_export verify-private-batch` | 26 artifacts, 0 mismatches |
| Batch 01–07 committed fixtures and goldens | full test suite | unchanged |
| Batch 04 global preflight | echoed and asserted in every record and in the report validator | `PREFLIGHT_REJECTED`, unchanged |
| Archived parent repository | `git rev-parse HEAD` | `0897562e05d75b812dd284de81dfafdfa1dea916` |
| Archived nested submodule | `git submodule status` | `6dbefd1a6b271bfc48106c4aa002f211735551cd` |

Batch 08 writes only under `intake/local-bars/ibkr-batch-05/phase3a/batch-08/`, which is
inside the gitignored private root. No prior artifact was read-write at any point.
