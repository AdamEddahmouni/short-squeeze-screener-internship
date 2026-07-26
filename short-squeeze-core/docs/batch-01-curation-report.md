# Batch 01 — Curation Report

**Batch ID:** `741672c2-23cb-5370-a49f-616a6a621b0e`
**Acquisition plan:** `phase-3d-historical-source-batch-01` (`PREREGISTERED`, `OUTCOME_BLINDED`)
**Discovery source:** archived market scanner snapshot (`ARCHIVED_MARKET_SCANNER`), 2026-07-18.

Generated artifacts live under `build/acquisition/batch-01/` (regenerable) with
byte-identical canonical copies committed under
`tests/fixtures/acquisition/batch01/`.

## Case ledger

| Metric | Count |
| --- | --- |
| Attempted cases | 13 |
| Unique security identities | 13 |
| Duplicate discoveries | 0 |
| Included (complete-dataset track) | 0 |
| Registry-only candidates | 13 |
| Complete Phase 3B dataset candidates | 0 |
| Excluded | 0 |
| Partial | 0 |
| Blocked | 0 |
| Dependent secondary boundaries | 0 |

Every attempted case is retained. No attempt disappears.

## Per-stage results

- **Identity:** 13 resolved `PARTIALLY_RESOLVED` (ticker present; issuer,
  exchange, and security type not present in the scanner row). No conflicts, no
  symbol-reuse flags.
- **Eligibility:** 13 decisions, all `included = False` for the complete-dataset
  track, each with the single exclusion code
  `CASE_REQUIRES_FABRICATED_EVIDENCE`. This is accurate and deliberate: a full
  Phase 3A request cannot be built offline from a flat scanner row without
  fabricating the normalized point-in-time evidence layers. Rather than fabricate,
  the cases are retained as registry-only (handoff §35.9).
- **Detection boundary:** 13 boundaries frozen under
  `ORIGINAL_PLATFORM_SURFACED_TIMESTAMP`, all `frozen_before_outcome_access =
  True`, `review_status = FROZEN`. The boundary timestamp is the objective
  scanner-surfaced timestamp — outcome-blind by construction.
- **Evidence sufficiency:** 13 reviews `SUFFICIENT_FOR_REGISTRY_ONLY`
  (detection-time market snapshot + boundary present; normalized Phase 3A
  evidence and outcome absent).
- **Phase 3A evaluation freeze:** 0 requests and 0 results frozen — no evaluation
  was performed for registry-only cases (see the evaluation-freeze manifest note).
- **Outcome capture:** none. The outcome manifest
  (`phase-3d-batch-01-outcome-not-captured`) is empty and separate from all
  discovery/eligibility/boundary inputs.
- **Leakage audit:** 13 audits, all `passed = True`, all `publication_blocked =
  False`. See [batch-01-leakage-audit-report.md](batch-01-leakage-audit-report.md).
- **Review:** each curated bundle records
  `review_decision = APPROVED_WITH_LIMITATIONS`, diagnostic
  `REGISTRY_ONLY_CANDIDATE`.

## Publication

- **Phase 3B registry candidates:** 13 (`registry_version =
  phase_3d_batch_01_registry.v1`, deterministic ID
  `15241fb5-d53d-57a2-9d79-5bec6d2519d5`). Every entry is
  `ARTIFACT_DISCOVERY_ONLY` / `ORIGINAL_PLATFORM_SURFACED` /
  `SANITIZED_LOCAL_ARTIFACT`.
- **Phase 3B complete dataset candidates:** 0.

## Why zero complete cases is the correct, honest result

Offline, and without fabricating evidence, these 13 real symbols can be curated
only as far as a frozen detection boundary with preserved discovery provenance
and identity. The forward outcome window and the normalized Phase 3A evaluation
evidence are genuinely unavailable. Handoff §9 and §34 explicitly make this a
successful batch: *"Zero new complete cases is not a blocker when source evidence
is insufficient and all attempts are honestly retained."* The value delivered is
13 auditable, outcome-blind, independent registry candidates plus a fully
exercised provenance/identity/boundary/leakage pipeline.

## What this batch does NOT do

No predictive validation, threshold optimization, rule weighting, composite
scoring, candidate ranking, recommendations, alerts, entry/exit logic, P&L,
backtesting, portfolio simulation, machine learning, live integrations, database
persistence, authentication, paper trading, or live trading. Phase 3E is not
started.
