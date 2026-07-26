# Batch 01 — Phase 3B Publication Summary

Publication is written to a **separate** batch location and never overwrites
existing Phase 3B fixtures. The Phase 3B / 3C / 3D schema version remains
`1.0.0`.

## Outputs

| Output | Count | File |
| --- | --- | --- |
| Phase 3B registry candidates | 13 | `phase3b-registry-candidates.json` |
| Phase 3B complete dataset candidates | 0 | `phase3b-dataset-candidates.json` |
| Registry-only cases | 13 | `registry-only-cases.json` |
| Excluded cases | 0 | `excluded-cases.json` |
| Partial cases | 0 | `partial-cases.json` |
| Blocked cases | 0 | `blocked-cases.json` |
| Dependent secondary boundaries | 0 | `dependent-secondary-boundaries.json` |
| Failed-leakage cases | 0 | `failed-leakage-cases.json` |
| Batch summary | — | `batch-summary.json` |

**Registry deterministic ID:** `15241fb5-d53d-57a2-9d79-5bec6d2519d5`
**Registry version:** `phase_3d_batch_01_registry.v1`

## Registry candidates

All 13 entries share this shape (values differ only by symbol / case ID):

| Field | Value |
| --- | --- |
| `case_id` | `BATCH01_<SYMBOL>_20260718` |
| `asset_class` | `EQUITY` |
| `case_type` | `ORIGINAL_PLATFORM_SURFACED` |
| `case_status` | `ARTIFACT_DISCOVERY_ONLY` |
| `original_platform_status` | `SURFACED` |
| `evaluation_as_of` / `*_path` | `None` (registry-only) |
| `original_platform_artifact_ids` | `("batch01-screener-snapshot-raw",)` |
| `phase_3a_policy_version` | `phase_3a_transparent_candidate_policy.v1` |
| `fixture_classification` | `SANITIZED_LOCAL_ARTIFACT` |

Case IDs: `BATCH01_{AVTX, BHVN, GPRE, LBGJ, LMNX, MGNX, OBE, PESI, SLS, SSPC,
TRVI, XNCR, ZNTL}_20260718`.

## Why registry-only (not complete dataset candidates)

Only cases passing provenance validation, artifact validation, identity review,
eligibility, boundary freeze, **evaluation freeze**, leakage audit, and review
approval may become complete Phase 3B dataset candidates. These cases have no
Phase 3A evaluation freeze and no captured outcome (both unavailable offline
without fabrication), so they qualify as **registry candidates only** — exactly
the disposition the handoff prescribes for incomplete cases (§25).

## Compatibility

- No prior Phase 1–3D manifest, fixture, or CLI anchor is modified.
- The batch registry is a new additive output with a new registry version and a
  distinct deterministic ID; it is not merged into
  `tests/fixtures/research/phase_3b_case_registry.json`.
- Overlapping symbols (SLS, LBGJ, TRVI) use batch-scoped case IDs and remain
  distinguishable from the prior migrated cases.
