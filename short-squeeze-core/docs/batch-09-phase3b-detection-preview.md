# Batch 09 — Phase 3B Research Detection Preview

The detection status below was **produced by executing the existing policy**, not assigned.
`squeeze_core.research.detection.evaluate_research_detection` was run against each frozen
Batch 08 `CandidateEvaluationResult` using `load_detection_policy(...)` on the unchanged
policy file.

---

## The policy (unchanged)

`src/squeeze_core/research/policies/phase_3b_research_detection_policy_v1.json`

```json
{
  "policy_version": "phase_3b_research_detection_policy.v1",
  "required_rule_ids": ["PRICE_RANGE", "MARKET_DATA_AVAILABLE", "COMPLETED_BAR_AVAILABLE"],
  "allowed_pass_outcomes": ["PASS"],
  "unknown_handling": "UNEVALUABLE",
  "conflict_handling": "UNEVALUABLE",
  "insufficient_data_handling": "UNEVALUABLE",
  "not_applicable_handling": "UNEVALUABLE",
  "provisional": true
}
```

Resolution: all required rules PASS → `DETECTED`; any required rule FAIL → `NOT_DETECTED`;
anything else → `UNEVALUABLE`.

Batch 09 did not edit this file, the required-rule set, the resolution order, or any
threshold.

---

## Executed result — all 13 cases

| # | Symbol | `PRICE_RANGE` | `MARKET_DATA_AVAILABLE` | `COMPLETED_BAR_AVAILABLE` | Detection |
|---|---|---|---|---|---|
| 1 | XNCR | UNKNOWN | PASS | PASS | `UNEVALUABLE` |
| 2 | PESI | UNKNOWN | PASS | PASS | `UNEVALUABLE` |
| 3 | SLS | UNKNOWN | PASS | PASS | `UNEVALUABLE` |
| 4 | ZNTL | UNKNOWN | PASS | PASS | `UNEVALUABLE` |
| 5 | GPRE | UNKNOWN | PASS | PASS | `UNEVALUABLE` |
| 6 | SSPC | UNKNOWN | PASS | PASS | `UNEVALUABLE` |
| 7 | LBGJ | UNKNOWN | PASS | PASS | `UNEVALUABLE` |
| 8 | TRVI | UNKNOWN | PASS | PASS | `UNEVALUABLE` |
| 9 | LMNX | UNKNOWN | PASS | PASS | `UNEVALUABLE` |
| 10 | MGNX | UNKNOWN | PASS | PASS | `UNEVALUABLE` |
| 11 | BHVN | UNKNOWN | PASS | PASS | `UNEVALUABLE` |
| 12 | OBE | UNKNOWN | PASS | PASS | `UNEVALUABLE` |
| 13 | AVTX | UNKNOWN | PASS | PASS | `UNEVALUABLE` |

Detection status counts: `UNEVALUABLE` ×13. `DETECTED` ×0. `NOT_DETECTED` ×0.

Per-case reason code: `REQUIRED_RULE_UNKNOWN:PRICE_RANGE` — the single required rule that is
not PASS.

**A preview in which all 13 detections remain `UNEVALUABLE` is a valid, expected result. It is
not a failure of this batch.**

---

## Why `PRICE_RANGE` is `UNKNOWN`

`PRICE_RANGE` tests an absolute price level. Batch 07 classified absolute price levels as
inadmissible under blocking reason `ABSOLUTE_PRICE_LEVEL_BLOCKED_BY_BATCH07`, because IBKR's
official documentation does not resolve the semantics needed to interpret an absolute level
(volume adjustment, intraday timestamp meaning, and volume unit all remain officially
unresolved from Batch 06; price adjustment resolved as `SPLIT_ADJUSTED`).

Price *ratios* are unaffected by the unresolved parts and are admissible — which is why
`PERCENTAGE_CHANGE_MINIMUM` could be evaluated substantively (6 PASS, 7 FAIL) while
`PRICE_RANGE` could not.

`PRICE_RANGE` therefore appears in every frozen result with outcome `UNKNOWN` and blocking
reason codes `ABSOLUTE_PRICE_LEVEL_BLOCKED_BY_BATCH07` /
`REQUIRED_DOMAIN_ABSENT_FROM_EVIDENCE`. `UNKNOWN` records "no admissible evidence existed to
test this", which is not the same as FAIL.

---

## What was explicitly not done

- `PERCENTAGE_CHANGE_MINIMUM` was **not** substituted for `PRICE_RANGE`. They answer different
  questions — a relative move versus an absolute level. A committed test asserts that the
  required-rule set is exactly the three policy rules and that
  `PERCENTAGE_CHANGE_MINIMUM` is not among them.
- The required-rule set was **not** changed.
- No detection status was hand-assigned; each came from the policy engine.
- No threshold was relaxed, optimized, or reinterpreted.
- `UNEVALUABLE` was **not** treated as `NOT_DETECTED` anywhere, including downstream.

---

## Consequence for research classification

`squeeze_core.research.classification.classify_research_case` is reachable only for candidates
that are `COMPLETE` with both an evaluation and an outcome. With no outcome, it is never
called: no TP, FP, TN, or FN exists for any of the 13 cases, and none was fabricated.

Research classification status: `NOT_PRODUCED_OUTCOME_INCOMPLETE` ×13.

This separation is the point of the batch:

| Dimension | State |
|---|---|
| evaluation completeness | complete (13/13 frozen Phase 3A results) |
| research detection completeness | not complete (13/13 `UNEVALUABLE`) |
| outcome completeness | not complete (13/13 absent) |
