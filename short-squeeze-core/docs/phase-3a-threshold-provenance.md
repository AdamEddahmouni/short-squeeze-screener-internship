# Phase 3A Threshold Provenance

Every threshold carries an ID, policy version, operator, unit, source type, source
reference, rationale code, and `provisional` flag.

| Threshold family | Source | Status |
|---|---|---|
| Price 2–20, change 10 percent, relative volume 5 | surviving original platform rubric documented by Phase 2V | provisional; preserved/corrected into momentum discovery |
| Float maximum 20 million shares | Phase 3A handoff/advisor guidance | provisional; source remains a snapshot contract |
| Short-interest change 10 percent | Phase 3A research policy | provisional, not a universal squeeze threshold |
| Days to cover 2 days | Phase 3A research policy | provisional, not a universal truth |
| Borrow fee 10 percent and change 2 percentage points | Phase 3A research policy | provisional; provider and units required |
| Availability 100,000 shares and change -10,000 shares | Phase 3A research policy | provisional; zero remains a known value |

The canonical details live in
`src/squeeze_core/evaluation/policies/phase_3a_transparent_candidate_policy_v1.json`.
Changing any policy version changes rule and candidate identities even when evidence is
otherwise identical.

