# Batch 09 — Canonical Registry Field Diff

Every field of `CandidateCaseRegistryEntry` for every one of the 13 candidates, before and
after the proposed revision. The pinned fields are listed as explicitly as the changed ones,
so "nothing else moved" is visible rather than asserted.

Machine-readable equivalents:
`tests/fixtures/acquisition/batch09/registry-field-diff.json` (per-case diff) and
`tests/fixtures/acquisition/batch09/registry-revision-preview.json` (full preview).

Change kinds:

| Kind | Meaning |
|---|---|
| `ADDED` | was `null`/empty, carries a value in the preview |
| `CHANGED` | had a value, carries a different value in the preview |
| `UNCHANGED` | identical, and permitted to move in principle |
| `FORBIDDEN_TO_CHANGE` | identical, and pinned by the preregistered plan |

---

## Aggregate field-change frequency

All 13 cases behave identically, so every row below is 13/13.

| Field | Kind | Cases | Rationale |
|---|---|---|---|
| `evaluation_request_path` | ADDED | 13 | `REFERENCE_TO_FROZEN_PHASE3A_REQUEST` |
| `evaluation_result_path` | ADDED | 13 | `REFERENCE_TO_FROZEN_PHASE3A_RESULT` |
| `evaluation_as_of` | ADDED | 13 | `CONTRACT_REQUIRED_BY_LOAD_PHASE_3A_RESULT` |
| `case_status` | CHANGED | 13 | `EVALUATION_PRESENT_OUTCOME_ABSENT_STATE` |
| `limitations` | CHANGED | 13 | `EVALUATION_LIMITATION_TEXT_MUST_STOP_ASSERTING_NO_EVALUATION` |
| `deterministic_id` | CHANGED | 13 | `MECHANICAL_UUIDV5_RECOMPUTATION` |
| `asset_class` | FORBIDDEN_TO_CHANGE | 13 | pinned |
| `case_id` | FORBIDDEN_TO_CHANGE | 13 | pinned |
| `case_type` | FORBIDDEN_TO_CHANGE | 13 | pinned |
| `detection_time_evidence_id` | FORBIDDEN_TO_CHANGE | 13 | pinned |
| `fixture_classification` | FORBIDDEN_TO_CHANGE | 13 | pinned |
| `historical_dataset_ids` | FORBIDDEN_TO_CHANGE | 13 | pinned |
| `original_platform_artifact_ids` | FORBIDDEN_TO_CHANGE | 13 | pinned |
| `original_platform_status` | FORBIDDEN_TO_CHANGE | 13 | pinned |
| **`outcome_observation_path`** | **FORBIDDEN_TO_CHANGE** | **13** | **outcome truth is untouched** |
| `phase_3a_policy_version` | FORBIDDEN_TO_CHANGE | 13 | pinned |
| `schema_version` | FORBIDDEN_TO_CHANGE | 13 | pinned, stays `1.0.0` |
| `symbol` | FORBIDDEN_TO_CHANGE | 13 | pinned |

18 fields per case × 13 cases = 234 field observations. 78 move (6 × 13); 156 are pinned and
verified identical (12 × 13).

---

## The change, stated once (identical for every case)

**ADDED** `evaluation_request_path`
`null` → `"../phase3a/batch-08/requests/<CASE_ID>.json"`

**ADDED** `evaluation_result_path`
`null` → `"../phase3a/batch-08/results/<CASE_ID>.json"`

**ADDED** `evaluation_as_of`
`null` → `"2026-07-18T13:37:55.017661Z"`

**CHANGED** `case_status`
`"ARTIFACT_DISCOVERY_ONLY"` → `"EVALUATION_ONLY"`

**CHANGED** `limitations`
removed: `REGISTRY_ONLY_NO_PHASE_3A_EVALUATION`
added: `PHASE_3A_EVALUATION_FROZEN_BATCH_08`,
`RESEARCH_DETECTION_UNEVALUABLE_PRICE_RANGE_UNRESOLVED`,
`GLOBAL_PREFLIGHT_REJECTED_EVIDENCE_ADMISSIBILITY_LIMITED`
retained: `OUTCOME_WINDOW_NOT_ACQUIRED_OFFLINE`,
`IDENTITY_PARTIALLY_RESOLVED_ISSUER_EXCHANGE_UNKNOWN`, and every
`DETECTION_DOMAIN_MISSING:*` entry for that case

**CHANGED** `deterministic_id` — see the identity table below.

---

## Candidate identity transition

The candidate ID moves because `evaluation_as_of`, `case_status`, and `limitations` all
participate in the entry's UUIDv5 identity. The three path fields do not. The original
candidates are **not** overwritten: the canonical Batch 01 registry is untouched, and the
preview carries its own registry version `phase_3d_batch_09_registry_preview.v1`.

Source order preserved.

| # | Symbol | Current candidate ID | Preview candidate ID |
|---|---|---|---|
| 1 | XNCR | `8c875a89-a4fd-52ed-ac1a-f1b7c1c7400c` | `5184e1c6-eb33-580b-8408-cc960eadfff6` |
| 2 | PESI | `eb88d7b1-300f-583b-9e33-2472a48c28fc` | `6cbab464-94e1-57c9-aa6a-9b7a98290996` |
| 3 | SLS | `6b633588-9b5a-55ae-9396-b18088e4634a` | `e6d3a124-e4c8-54b9-91ab-d087d4fd5b15` |
| 4 | ZNTL | `a4cee82a-010f-5be4-96c5-88e5bbc648a2` | `eaf0273f-7162-5047-9759-7c1250ab278b` |
| 5 | GPRE | `0654c8fe-6f98-5560-b461-1a5ced90d6b2` | `23afdb21-5f96-59a0-9f2c-e28c8a82a73e` |
| 6 | SSPC | `730ec07d-072e-5ea2-a231-b089f0b6fc97` | `8772bf7e-4357-5b24-9594-ece6ee62bd0f` |
| 7 | LBGJ | `256f58cf-5185-5cca-8a0b-cc9f69cc8051` | `7cdfa914-5d0f-5020-91d0-783ce07606c0` |
| 8 | TRVI | `d61059ef-ccae-5cec-985e-6bfa740d7d48` | `944a5499-a6b3-532c-b964-85525a78cb7b` |
| 9 | LMNX | `0cdcb9f7-419d-5cbb-a599-c7e0050b7cf0` | `9b11753d-1f75-5c63-80d2-a5805c2d74b7` |
| 10 | MGNX | `e3cc7156-3a0a-5f3b-9c08-ac144f54b864` | `73bcf3b6-a518-5c45-9526-188e2596cbcc` |
| 11 | BHVN | `617e3007-4aa1-59b1-a35f-07d469be1cc7` | `c5a92c9d-44a4-55bb-ae14-385a7b5bd4d7` |
| 12 | OBE | `c3a5c954-7d39-514f-aa43-75fab64b518b` | `0a59fb6a-b746-5f4f-9a18-d2ea67560cfb` |
| 13 | AVTX | `4130b752-f6b3-5fc9-8812-66f4c15168e6` | `2eda5211-d9a4-565b-8fa3-a00c4260bd81` |

Registry-level identity:

| | Version | ID |
|---|---|---|
| Source (canonical, unchanged) | `phase_3d_batch_01_registry.v1` | `15241fb5-d53d-57a2-9d79-5bec6d2519d5` |
| Preview (dry run only) | `phase_3d_batch_09_registry_preview.v1` | `33c21783-0424-50b1-8920-aa3beef4de39` |

Batch 09 preview document ID: `c6b08f21-065d-5e96-b100-acc5b86fc4e9`.
Contract audit record ID: `ec5976ce-d840-5189-943d-23e9fa124e3e`.

---

## Referenced frozen artifacts

Each preview entry references exactly the Batch 08 artifacts whose bytes were hash-verified
before the preview was built (26/26 match, 0 mismatches). Per-case request/result IDs and full
sha256 values are in `tests/fixtures/acquisition/batch09/registry-revision-preview.json`.

All 13 references were resolved and loaded end-to-end through the existing
`squeeze_core.research.io.load_phase_3a_result`, with symbol and `as_of` matching the entry —
so these are live references, not just text.
