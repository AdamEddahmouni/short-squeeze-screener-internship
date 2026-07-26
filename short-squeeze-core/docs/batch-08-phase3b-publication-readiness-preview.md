> Companion to [batch-08-phase3a-request-result-freeze-plan.md](batch-08-phase3a-request-result-freeze-plan.md).

# Batch 08 — Phase 3B Publication-Readiness Preview

**This document publishes nothing.** No Phase 3B registry was written, revised, or read
for outcomes. No outcome classification was computed. No case is outcome-complete.

The preview answers four narrow questions per case and nothing else.

## 1. The four questions

| Question | Answer for all 13 cases |
| --- | --- |
| Does the case now have a frozen Phase 3A **request**? | yes |
| Does the case now have a frozen Phase 3A **result**? | yes |
| Did the leakage audit **pass**? | yes |
| Could a future Phase 3B registry revision **reference** these paths? | yes |

| Case | Frozen request | Frozen result | Leakage passed | Outcome complete | Referenceable |
| --- | --- | --- | --- | --- | --- |
| `BATCH01_XNCR_20260718` | true | true | true | **false** | true |
| `BATCH01_PESI_20260718` | true | true | true | **false** | true |
| `BATCH01_SLS_20260718` | true | true | true | **false** | true |
| `BATCH01_ZNTL_20260718` | true | true | true | **false** | true |
| `BATCH01_GPRE_20260718` | true | true | true | **false** | true |
| `BATCH01_SSPC_20260718` | true | true | true | **false** | true |
| `BATCH01_LBGJ_20260718` | true | true | true | **false** | true |
| `BATCH01_TRVI_20260718` | true | true | true | **false** | true |
| `BATCH01_LMNX_20260718` | true | true | true | **false** | true |
| `BATCH01_MGNX_20260718` | true | true | true | **false** | true |
| `BATCH01_BHVN_20260718` | true | true | true | **false** | true |
| `BATCH01_OBE_20260718` | true | true | true | **false** | true |
| `BATCH01_AVTX_20260718` | true | true | true | **false** | true |

`outcome_complete` is `false` for every case and the model raises if it is ever set true in
Batch 08. All 13 cases remain **outcome-incomplete** and explicitly **non-predictive**.

## 2. What "referenceable" means

Only that a future authorised Phase 3B revision *could* point at a stable, hashed,
deterministic artifact. It carries no claim that publication should happen, that a case is
a positive or negative example, or that any rule outcome predicts anything.

Concretely, a future revision could cite, per case: the case id, the boundary id, the
Phase 3A request id with its SHA-256 and byte length, the Phase 3A result id with its
SHA-256 and byte length, the candidate evaluation id, the leakage-audit status, and the
Batch 07 readiness record id. All are recorded in the private case manifest.

## 3. What is still missing before any real publication

| Gap | Status |
| --- | --- |
| Forward outcome data | none exists; Batch 02 established there is no lawful non-authenticated source for the forward windows, and the Batch 05 forward artifacts remain `PREFLIGHT_REJECTED` and unopened |
| Outcome labels | none; Phase 3B labelling is not started |
| Batch 04 global preflight | still `PREFLIGHT_REJECTED` — unchanged and not weakened |
| Volume semantics | still unresolved, so relative-volume screening stays blocked |
| Absolute-price semantics | corporate-action confirmation still absent, so price-band screening stays blocked |
| Float, short-pressure, catalyst evidence | never collected at detection time |

## 4. Where the decision sits

The single open decision for the supervisor is stated in
[batch-08-professor-brief.md](batch-08-professor-brief.md): whether to approve a Phase 3B
registry revision that *references* these frozen Phase 3A evaluations while retaining every
case as outcome-incomplete and explicitly non-predictive.

Batch 08 does not take that decision and does not pre-empt it.
