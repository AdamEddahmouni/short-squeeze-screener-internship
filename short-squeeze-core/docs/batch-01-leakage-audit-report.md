# Batch 01 — Leakage Audit Report

The full Phase 3D outcome-leakage audit (`phase_3d_outcome_leakage_policy.v1`) was
run for every one of the 13 registry candidates.

| Result | Count |
| --- | --- |
| Passed | 13 |
| Failed | 0 |
| Publication-blocked | 0 |

**Leakage audit collection deterministic ID:** derived from batch
`741672c2-23cb-5370-a49f-616a6a621b0e`.

## Ordering enforcement (per case)

The audit confirms every freeze stage precedes any outcome access. The frozen
instants used are deterministic (never wall-clock):

```
plan_frozen_at              2026-07-22T12:00:00Z
boundary_frozen_at          2026-07-22T12:01:00Z
evaluation_request_frozen   2026-07-22T12:02:00Z   (placeholder; not constructed)
evaluation_result_frozen    2026-07-22T12:03:00Z   (placeholder; not constructed)
outcome_captured_at         2026-07-22T12:04:00Z   (sentinel; NO outcome captured)
```

Because no evaluation request/result and no outcome were actually produced for a
registry-only case, the evaluation and outcome instants are ordering
placeholders. The `outcome_captured_at` sentinel is strictly after every freeze
stage, so the ordering invariant holds and the audit confirms that **no outcome
artifact could have influenced any earlier stage** — which is trivially true here
because no outcome artifact exists.

## What the audit checked and confirmed

- Plan froze before any outcome access. ✅ (no outcome access at all)
- Detection boundary froze before any outcome access. ✅
- Phase 3A request/result "froze" before any outcome access. ✅ (not constructed)
- Discovery input fields contain no outcome fields. ✅
  (`symbol, observed_at, price, rel_volume, change_percent, short_float_percent,
  days_to_cover, shares_short, float_shares` — none are forward-outcome fields;
  `change_percent` is the detection-time intraday change, not the forward return)
- Eligibility input fields contain no outcome fields. ✅
- Boundary input fields contain no outcome fields. ✅ (`platform_surfaced_timestamp`)
- Evaluation input fields contain no outcome fields. ✅ (empty)
- Outcome manifest is separate from the discovery manifest. ✅
  (`phase-3d-batch-01-outcome-not-captured` ≠ `phase-3d-batch-01-source`)
- No maximum-return or favorable-outcome selection occurred. ✅
- No post-event article was used as an undisclosed discovery source. ✅

## Fail-path coverage

A dedicated test (`test_leakage_audit_fails_when_outcome_field_present`) injects a
`maximum_return` field into the discovery input and confirms the audit returns
`passed = False`, `publication_blocked = True`. A failed audit would block
publication; no case in this batch fails.
