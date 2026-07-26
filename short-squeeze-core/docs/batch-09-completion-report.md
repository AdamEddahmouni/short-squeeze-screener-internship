# Batch 09 — Completion Report

**Task:** Phase 3D Phase 3B Registry Revision Preview Batch 09
**Branch:** `batch/phase-3d-phase3b-registry-preview-09`
**Parent:** `c93f704104429468f920b0d0d88002a821c68b63` (Batch 08)
**Status:** complete. Dry run only. Nothing published. Phase 3E not started.

---

## 1. What was asked and what was produced

Construct a deterministic, non-publishing preview showing exactly how the 13 Batch 01
registry-only Phase 3B candidates would change if they referenced their newly frozen Batch 08
Phase 3A requests/results while their outcome status remains incomplete.

Delivered: a preregistered plan, a runtime contract audit, a 13-case preview, a canonical
field diff, an executed detection preview, a publication dry run in all three formats, a
Phase 3C structural compatibility proof, 53 new tests, and the professor-facing decision
package and talking points.

---

## 2. The seven questions, answered

**1. Can the existing Phase 3B registry contract legally reference these new Phase 3A
request/result artifacts?**
Yes. The three path fields are independent optionals with no cross-field constraint, and the
publication adapter is neutral on evaluation references. Conclusion
`PREVIEW_COMPATIBLE_WITH_LIMITATIONS`.

**2. Exactly which fields would change for each of the 13 cases?**
Six: `evaluation_request_path` (ADDED), `evaluation_result_path` (ADDED), `evaluation_as_of`
(ADDED, contract-required), `case_status` (`ARTIFACT_DISCOVERY_ONLY` → `EVALUATION_ONLY`),
`limitations` (retire one false claim, add three accurate ones), and `deterministic_id`
(mechanical recomputation).

**3. Which fields must remain unchanged?**
Twelve, including `outcome_observation_path`, `case_id`, `symbol`,
`detection_time_evidence_id`, `original_platform_artifact_ids`, and `phase_3a_policy_version`.
All verified identical across all 13 cases.

**4. Does the preview validate against the existing Phase 3B schema/policies?**
Yes. Schema `1.0.0`, unmodified. The preview registry loads through
`load_case_registry`, all 13 evaluation references resolve through `load_phase_3a_result`, and
the existing batch runner, dataset builder, and JSON/JSONL/CSV serializers all accept it.

**5. Would any existing research classification or outcome status change?**
No. No classification exists before or after — the existing contract makes classification
unreachable without an outcome. Outcome status stays
`OUTCOME_INCOMPLETE_NO_VALID_FORWARD_EVIDENCE` for all 13.

**6. Is the proposed revision deterministic and backward-compatible?**
Yes. Regeneration is byte-identical across 14 files. The canonical registries are unchanged.
The preview carries a distinct registry version so it cannot be confused with Batch 01.
Consumers filtering on `COMPLETE` are unaffected.

**7. What exactly should the professor approve or reject?**
See `docs/batch-09-professor-decision-package.md` §6. One question, three recorded outcomes.

---

## 3. Headline results

| Metric | Value |
|---|---|
| Candidate previews | **13** |
| Candidate identity changed | **13/13**, deterministic UUIDv5 |
| Research detection | **`UNEVALUABLE` ×13** (`PRICE_RANGE` `UNKNOWN`; both availability rules `PASS`) |
| Outcome status | **`OUTCOME_INCOMPLETE_NO_VALID_FORWARD_EVIDENCE` ×13**, `outcome_path` null ×13 |
| Research classification | **`NOT_PRODUCED_OUTCOME_INCOMPLETE` ×13** |
| Preview compatibility | **`PREVIEW_COMPATIBLE_WITH_LIMITATIONS` ×13** |
| Publication dry run | 0 case results, **13 skipped**, **0 dataset rows** |
| Regeneration determinism | 14 files, **0 byte differences** |
| Canonical registries | 4 files, **byte-identical** |
| Batch 05 raw integrity | **26/26**, 0 mismatches |
| Batch 08 freeze integrity | **26/26**, 0 mismatches |

---

## 4. Commits

| Hash | Subject |
|---|---|
| `321ddfa6a799613461a4677942cd00af0b65c7d5` | docs: preregister Phase 3B registry preview batch 09 |
| `fca96fbf87b39ce61fbbdbec4e23cedf7a9c8cf5` | feat: add deterministic Phase 3B registry revision preview |
| `5651c4ff95e283cb30c771ef2a513f76dcf1670a` | test: add Batch 09 registry compatibility coverage |
| `2f11eb77dd09a881ada0c33440057c28302474c8` | docs: add Phase 3B preview findings and professor decision package |
| (final) | chore: finalize Phase 3B registry preview batch 09 |

The finalizing commit's hash is reported in the session summary.

---

## 5. What was deliberately not done

No canonical Phase 3B registry mutation. No publication. No new market-data request. No IBKR
connection. No forward OHLCV access. No outcome access. No change to `PRICE_RANGE` policy, the
detection policy, the outcome policy, or any Phase 3A result or threshold. No substitution of
`PERCENTAGE_CHANGE_MINIMUM` for `PRICE_RANGE`. No fabricated outcome label or research
classification. No scoring, ranking, rule weighting, ML, predictive validation, new Phase 3C
empirical analysis, backtest, P&L, alert, trade recommendation, paper trade, or live trade.
Phase 3E was not started.

Schema remains `1.0.0`.

---

## 6. Limitations

- All 13 research detections remain `UNEVALUABLE`. This is the correct, expected result under
  the unchanged policy, not a defect — but it means the registry revision adds an evidence
  link, not evidence of detection.
- No outcomes exist, so the revision adds zero rows to the empirical dataset. Predictive
  validation remains impossible.
- `PRICE_RANGE` stays blocked until absolute-price semantics are authoritatively resolved or
  an alternative source with documented semantics is admitted.
- The global preflight verdict remains `PREFLIGHT_REJECTED`.
- The preview's real artifacts live under a Git-ignored private path; only sanitized
  identifiers, hashes, and statuses are committed.
- Candidate deterministic IDs change for all 13. That is a property of the existing identity
  contract, not a choice — but it means the revised entries are new objects by identity, and
  any external reference to a Batch 01 candidate ID would need updating.

---

## 7. Definition of done — checklist

- [x] exact Batch 08 checkpoint verified
- [x] baseline reproduced (2,319 passed / 1 skipped / 0 failed)
- [x] Batch 08 freeze verified (26/26)
- [x] Phase 3B contract audited
- [x] plan preregistered and committed before generation
- [x] exactly 13 registry revision previews exist
- [x] exact before/after diffs exist
- [x] frozen Phase 3A references validate and load
- [x] outcome paths remain null
- [x] outcomes remain incomplete
- [x] existing detection policy executed unchanged
- [x] detection status reported honestly (`UNEVALUABLE` ×13)
- [x] dry-run JSON/JSONL/CSV validate
- [x] preview outputs regenerate byte-identically
- [x] canonical registry remains byte-identical
- [x] Phase 3C structural compatibility proven
- [x] no outcome or forward data accessed
- [x] tests pass (final full suite: 2,378 passed / 1 skipped / 0 failed)
- [x] prior artifacts unchanged
- [x] archived evidence unchanged
- [x] professor decision package exists
- [x] professor talking points exist
- [x] completion report exists
- [x] actual Batch 10 handoff exists
- [x] Phase 3E remains unstarted
- [x] work stops
