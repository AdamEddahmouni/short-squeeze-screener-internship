> Companion to [batch-08-phase3a-request-result-freeze-plan.md](batch-08-phase3a-request-result-freeze-plan.md).

# Batch 08 — Phase 3A Rule Outcome Summary (sanitized)

Every outcome below was produced by the existing Phase 3A evaluator
(`squeeze_core.evaluation.evaluate_candidate`). None was assigned by hand; a committed test
asserts the freeze package's executable code never names `PASS`, `FAIL`, `UNKNOWN`,
`CONFLICTED`, or `INSUFFICIENT_DATA`, and another asserts each recorded outcome is
byte-equal to the evaluator's own `RuleEvaluationResult`.

No raw OHLCV and no derived price or return value appears in this document. These are
descriptive evidence-coverage results, **not** predictive performance.

## 1. Headline counts

- 13 requests frozen, 13 results frozen, 13/13 leakage audits passed.
- 25 rules × 13 cases = **325 rule-case pairs**.

| Outcome | Count | Share of 325 |
| --- | --- | --- |
| `PASS` | 97 | 29.8 % |
| `UNKNOWN` | 208 | 64.0 % |
| `FAIL` | 20 | 6.2 % |
| `CONFLICTED` | 0 | 0 % |
| `INSUFFICIENT_DATA` | 0 | 0 % |
| `NOT_APPLICABLE` | 0 | 0 % |

A result dominated by `UNKNOWN` is the honest finding, not a failure: it is the direct
consequence of six of seven required evidence domains never having been collected at
detection time, and of two operations Batch 07 blocked for unresolved provider semantics.

## 2. Counts by category

| Category | `PASS` | `FAIL` | `UNKNOWN` | Denominator |
| --- | --- | --- | --- | --- |
| `MOMENTUM_DISCOVERY` | 32 | 7 | 39 | 78 |
| `SHORT_PRESSURE_CONFIRMATION` | 0 | 0 | 91 | 91 |
| `CATALYST_EVIDENCE` | 0 | 0 | 65 | 65 |
| `EVIDENCE_VALIDITY` | 65 | 13 | 13 | 91 |

## 3. The 25-rule matrix (uniform across cases unless noted)

| Rule | Category | Batch 07 | Outcome across 13 cases |
| --- | --- | --- | --- |
| `MARKET_DATA_AVAILABLE` | MOMENTUM | ADMISSIBLE | `PASS` ×13 |
| `COMPLETED_BAR_AVAILABLE` | MOMENTUM | ADMISSIBLE | `PASS` ×13 |
| `PERCENTAGE_CHANGE_MINIMUM` | MOMENTUM | ADMISSIBLE_WITH_CONSTRAINTS | `PASS` ×6, `FAIL` ×7 |
| `PRICE_RANGE` | MOMENTUM | BLOCKED_MISSING_SEMANTICS | `UNKNOWN` ×13 |
| `RELATIVE_VOLUME_MINIMUM` | MOMENTUM | BLOCKED_MISSING_SEMANTICS | `UNKNOWN` ×13 |
| `FLOAT_MAXIMUM` | MOMENTUM | BLOCKED_MISSING_EVIDENCE | `UNKNOWN` ×13 |
| `PUBLISHED_SHORT_INTEREST_AVAILABLE` | SHORT_PRESSURE | BLOCKED_MISSING_EVIDENCE | `UNKNOWN` ×13 |
| `SHORT_INTEREST_PERCENTAGE_CHANGE_MINIMUM` | SHORT_PRESSURE | BLOCKED_MISSING_EVIDENCE | `UNKNOWN` ×13 |
| `DAYS_TO_COVER_MINIMUM` | SHORT_PRESSURE | BLOCKED_MISSING_EVIDENCE | `UNKNOWN` ×13 |
| `BORROW_FEE_MINIMUM` | SHORT_PRESSURE | BLOCKED_MISSING_EVIDENCE | `UNKNOWN` ×13 |
| `BORROW_FEE_CHANGE_MINIMUM` | SHORT_PRESSURE | BLOCKED_MISSING_EVIDENCE | `UNKNOWN` ×13 |
| `BORROW_AVAILABILITY_MAXIMUM` | SHORT_PRESSURE | BLOCKED_MISSING_EVIDENCE | `UNKNOWN` ×13 |
| `BORROW_AVAILABILITY_CHANGE_MAXIMUM` | SHORT_PRESSURE | BLOCKED_MISSING_EVIDENCE | `UNKNOWN` ×13 |
| `NEWS_AVAILABLE` | CATALYST | BLOCKED_MISSING_EVIDENCE | `UNKNOWN` ×13 |
| `NEWS_AVAILABLE_BEFORE_AS_OF` | CATALYST | BLOCKED_MISSING_EVIDENCE | `UNKNOWN` ×13 |
| `NEWS_TIMESTAMP_KNOWN` | CATALYST | BLOCKED_MISSING_EVIDENCE | `UNKNOWN` ×13 |
| `SEC_FILING_AVAILABLE` | CATALYST | BLOCKED_MISSING_EVIDENCE | `UNKNOWN` ×13 |
| `CORPORATE_ACTION_CONTEXT_AVAILABLE` | CATALYST | BLOCKED_MISSING_EVIDENCE | `UNKNOWN` ×13 |
| `REQUIRED_DOMAINS_PRESENT` | EVIDENCE_VALIDITY | NOT_APPLICABLE | `FAIL` ×13 |
| `NO_MATERIAL_CONFLICTS` | EVIDENCE_VALIDITY | NOT_APPLICABLE | `PASS` ×13 |
| `POINT_IN_TIME_ELIGIBLE` | EVIDENCE_VALIDITY | NOT_APPLICABLE | `PASS` ×13 |
| `REQUIRED_UNITS_COMPATIBLE` | EVIDENCE_VALIDITY | NOT_APPLICABLE | `PASS` ×13 |
| `REQUIRED_HISTORY_SUFFICIENT` | EVIDENCE_VALIDITY | NOT_APPLICABLE | `PASS` ×13 |
| `NO_DEFAULT_SUBSTITUTION` | EVIDENCE_VALIDITY | NOT_APPLICABLE | `PASS` ×13 |
| `PROVIDER_SCOPE_EXPLICIT` | EVIDENCE_VALIDITY | NOT_APPLICABLE | `UNKNOWN` ×13 |

## 4. Per-case table

`PC` is `PERCENTAGE_CHANGE_MINIMUM` — the only rule whose outcome varies. Bar counts are
definitely-completed bars observed in the artifact.

| # | Case | PC | Bars | Request id | Result id |
| --- | --- | --- | --- | --- | --- |
| 1 | `BATCH01_XNCR_20260718` | `PASS` | 1164 | `12053e55-a31a-5d46-9174-6e455d124cca` | `878553cf-7783-5e7d-aec6-7c6c733a98b5` |
| 2 | `BATCH01_PESI_20260718` | `PASS` | 1348 | `5b548b50-c024-5bd7-b62e-0ed63ff4c431` | `475fcfbc-a4d4-512a-9275-a79739db5acf` |
| 3 | `BATCH01_SLS_20260718` | `PASS` | 1440 | `03faecb6-0945-513f-ae88-9872cba0c71e` | `ae82e570-ba62-5189-ba6c-3809662de0b3` |
| 4 | `BATCH01_ZNTL_20260718` | `FAIL` | 1338 | `985ea50f-c9d5-5f5c-9ebd-f20ce06ee96e` | `782a22e2-6716-5fa1-8645-d50aaa1649f7` |
| 5 | `BATCH01_GPRE_20260718` | `FAIL` | 1195 | `5854e479-14f9-5c0d-81d7-1fa2a6d2380f` | `be8981f4-1d7f-50ee-a614-eb91d0da63c6` |
| 6 | `BATCH01_SSPC_20260718` | `PASS` | 1440 | `2ead1b74-47f9-52e6-b545-02e86f18a372` | `1d4fdd0f-9422-5eb7-b526-df8474bcb0c0` |
| 7 | `BATCH01_LBGJ_20260718` | `PASS` | 1440 | `7e64fa42-27d9-5992-8769-98b90b4798c5` | `fd98e07e-5fe6-560e-a9c1-d37ae84a55ba` |
| 8 | `BATCH01_TRVI_20260718` | `PASS` | 1428 | `d7c38a7b-e976-52d5-a949-378916ab3f9b` | `ef550571-8a7a-5eb3-9b12-1001c9233b8e` |
| 9 | `BATCH01_LMNX_20260718` | `FAIL` | 1432 | `a23b85dc-079e-54b8-b64b-293cec611da6` | `2258ea56-de0c-5819-817b-66572c608c82` |
| 10 | `BATCH01_MGNX_20260718` | `FAIL` | 1333 | `a225a195-4dd7-5f63-905c-e8689be9604a` | `6852d9f1-2d4c-597a-afbf-8118343734d5` |
| 11 | `BATCH01_BHVN_20260718` | `FAIL` | 1399 | `7270ffbf-bf3f-5129-ace3-1249b59d7470` | `0293b6e8-2a42-53c5-a242-d118a31771b5` |
| 12 | `BATCH01_OBE_20260718` | `FAIL` | 1394 | `90d40489-7ad6-5223-9a99-894a6f5a38af` | `b73b2304-ae19-5e67-975f-b33b8f6ac09c` |
| 13 | `BATCH01_AVTX_20260718` | `FAIL` | 1413 | `e374717f-747a-524c-aa64-7bdd41b4f490` | `9dbcbed0-68e7-52f8-a4db-02596300f2ab` |

Every case has freeze status `REQUEST_AND_RESULT_FROZEN` and leakage status
`LEAKAGE_AUDIT_PASSED`.

## 5. `PERCENTAGE_CHANGE_MINIMUM` in detail

The one substantively evaluated threshold rule.

- 6 of 13 cases meet the `>= 10 %` threshold across the definitely-completed
  detection-context window; 7 do not.
- Every case produced a `KNOWN_VALUE` metric, so no case fell back to missingness.
- The rule consumed only the metric: its supporting observation list is empty and its
  supporting metric list contains exactly the one `PERCENTAGE_RETURN` id.
- Actual return values are held only in the private artifacts and deliberately do not
  appear in any committed document.

`PASS` here means "this window return met the threshold under a provisional,
original-platform-derived cut-off". It is not a statement that the candidate squeezed, and
the threshold itself is still marked `provisional` in the policy.

## 6. Availability rules

`MARKET_DATA_AVAILABLE` and `COMPLETED_BAR_AVAILABLE` resolve `PASS` for all 13 cases,
each supported by observation ids and by artifact identity (SHA-256 + byte length). Both
report an observed count of 2, which is the number of bars supplied to the request under
the declared bounded-supply policy — not the number in the artifact, which ranges 1,164 to
1,440 and is recorded separately. See
[batch-08-phase3a-request-construction.md](batch-08-phase3a-request-construction.md) §4.

## 7. Blocked rules

All 18 blocked rules resolve `UNKNOWN` for all 13 cases. None was forced to `FAIL`, none
received a fabricated value, and no `null` was replaced with zero — a committed test
asserts every `UNKNOWN` result carries `observed_value = null`.

Explanation codes observed:

| Rule group | Explanation code |
| --- | --- |
| `PRICE_RANGE`, `FLOAT_MAXIMUM`, `PUBLISHED_SHORT_INTEREST_AVAILABLE`, `BORROW_FEE_MINIMUM`, `BORROW_AVAILABILITY_MAXIMUM` | `EVALUATION_PROVIDER_SCOPE_REQUIRED` |
| `RELATIVE_VOLUME_MINIMUM` | `EVALUATION_RELATIVE_VOLUME_UNAVAILABLE` |
| short-interest / days-to-cover / borrow-change rules | the matching `..._UNAVAILABLE` code |
| the five catalyst rules | the matching `..._UNAVAILABLE` code |

## 8. `EVIDENCE_VALIDITY` behaviour

Batch 07 marks these seven readiness-level `NOT_APPLICABLE`. Batch 08 did not force their
Phase 3A outcomes; the evaluator determined all of them. Observed canonical behaviour:

| Rule | Outcome | Why |
| --- | --- | --- |
| `NO_DEFAULT_SUBSTITUTION` | `PASS` | no field was defaulted anywhere in the request |
| `NO_MATERIAL_CONFLICTS` | `PASS` | the conflict summary found zero unresolved conflicts |
| `POINT_IN_TIME_ELIGIBLE` | `PASS` | the sufficiency record found no point-in-time failure |
| `REQUIRED_UNITS_COMPATIBLE` | `PASS` | the metric's unit matches the policy's required unit |
| `REQUIRED_HISTORY_SUFFICIENT` | `PASS` | no trailing-window shortfall for this operation |
| `REQUIRED_DOMAINS_PRESENT` | `FAIL` | six of seven policy-required domains are genuinely missing |
| `PROVIDER_SCOPE_EXPLICIT` | `UNKNOWN` | the request deliberately declares no request-level provider scope |

`REQUIRED_DOMAINS_PRESENT = FAIL` deserves emphasis: it is a **meta-rule about the
completeness of the evidence request**, not a judgement about a candidate. It says the
study currently holds market bars and nothing else.

## 9. What this evaluation cannot say

- Nothing about whether any candidate actually squeezed — no forward outcome data exists
  and none was accessed.
- Nothing about predictive validity, since no outcome labels exist to compare against.
- Nothing about short-pressure or catalyst conditions, which were never evidenced.
- Nothing about price-band or relative-volume screens, which remain blocked on unresolved
  provider semantics.
