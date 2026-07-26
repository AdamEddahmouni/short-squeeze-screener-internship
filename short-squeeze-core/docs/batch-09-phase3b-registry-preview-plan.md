# Batch 09 — Phase 3B Registry Revision Preview Plan (Preregistered)

Task name: **Phase 3D Phase 3B Registry Revision Preview Batch 09**

Branch: `batch/phase-3d-phase3b-registry-preview-09`
Parent commit: `c93f704104429468f920b0d0d88002a821c68b63` (Batch 08)
Baseline reproduced before any change: **2,319 passed / 1 skipped / 0 failed** (2,320 collected).

This document is written and committed **before** any preview artifact is generated. Everything
below is frozen. Deviations discovered later are recorded in
`docs/batch-09-completion-report.md`, never by silently editing this plan.

---

## 1. Purpose and scope

Construct a deterministic, **non-publishing** preview showing exactly how the 13 Batch 01
registry-only Phase 3B candidates would change if they referenced their newly frozen Batch 08
Phase 3A requests/results, while their outcome status remains incomplete.

This batch is a **DRY RUN**. It does not publish, does not mutate the canonical Phase 3B
registry, does not acquire data, and does not begin Phase 3E.

### Not in scope

Actual Phase 3B publication; outcome acquisition; outcome labelling; Phase 3C empirical
expansion; Phase 3E; any change to Phase 3A results, thresholds, or the Phase 3B detection
policy.

---

## 2. Frozen cohort

Source order (preserved exactly, never re-sorted for identity purposes):

| # | Symbol | Case ID |
|---|--------|---------|
| 1 | XNCR | `BATCH01_XNCR_20260718` |
| 2 | PESI | `BATCH01_PESI_20260718` |
| 3 | SLS | `BATCH01_SLS_20260718` |
| 4 | ZNTL | `BATCH01_ZNTL_20260718` |
| 5 | GPRE | `BATCH01_GPRE_20260718` |
| 6 | SSPC | `BATCH01_SSPC_20260718` |
| 7 | LBGJ | `BATCH01_LBGJ_20260718` |
| 8 | TRVI | `BATCH01_TRVI_20260718` |
| 9 | LMNX | `BATCH01_LMNX_20260718` |
| 10 | MGNX | `BATCH01_MGNX_20260718` |
| 11 | BHVN | `BATCH01_BHVN_20260718` |
| 12 | OBE | `BATCH01_OBE_20260718` |
| 13 | AVTX | `BATCH01_AVTX_20260718` |

Frozen boundary: `2026-07-18T13:37:55.017661Z`.

Case membership, source order, case IDs, identities, frozen boundaries, original discovery
provenance, Batch 01 eligibility, Batch 01 registry provenance, and outcome state are **not**
changed by this batch.

---

## 3. Current registry source (frozen input A)

Canonical committed Batch 01 Phase 3B registry:

`tests/fixtures/acquisition/batch01/phase3b-registry-candidates.json`

- sha256 `c16b49386f96705d43bb110fa76796ce998299599a49528dc799e1a17e678c73`, 12,668 bytes
- `registry_version = phase_3d_batch_01_registry.v1`
- registry `deterministic_id = 15241fb5-d53d-57a2-9d79-5bec6d2519d5`
- 13 entries, every one with `evaluation_request_path = null`,
  `evaluation_result_path = null`, `outcome_observation_path = null`,
  `evaluation_as_of = null`, `case_status = ARTIFACT_DISCOVERY_ONLY`.

These bytes must be **byte-identical** at the end of Batch 09.

Additional canonical registries that must also remain byte-identical:

| Path | sha256 | bytes |
|---|---|---|
| `tests/fixtures/acquisition/batch02/phase3b-registry-candidates.json` | `af691a27e5568dc4aca9fe94adb07f4efe8ceabe490cb7d88ad9c7ddff9656a2` | 12,707 |
| `tests/fixtures/acquisition/phase_3d_phase3b_registry_candidates.json` | `28d5b14cb7be31665174121011a353eea6afb182c22c43e388fc9e162ba72b07` | 6,851 |
| `tests/fixtures/research/phase_3b_case_registry.json` | `5684ecd6e9f9e5b194379be411654cb5f15f5b24b638339605a2cc232bcb9b79` | 15,473 |

---

## 4. Batch 08 Phase 3A references (frozen input B)

Private (Git-ignored) root: `intake/local-bars/ibkr-batch-05/phase3a/batch-08/`

- `requests/<CASE_ID>.json` — 13 canonical Phase 3A requests
- `results/<CASE_ID>.json` — 13 canonical Phase 3A results
- `leakage/<CASE_ID>.json` — 13 leakage audits, all `LEAKAGE_AUDIT_PASSED`
- `batch-summary.json` — per-case freeze record carrying request/result IDs, artifact
  sha256/byte_length, boundary id, freeze status, global preflight status, and the exact
  25 rule outcomes.

Verified before any work in this batch: **26/26 request+result artifacts hash-match, 0
mismatches**; all 13 `freeze_status = REQUEST_AND_RESULT_FROZEN`; all 13
`leakage_audit_status = LEAKAGE_AUDIT_PASSED`; `forward_ohlcv_accessed = false` and
`outcome_accessed = false` for every case.

Batch 08 results are **authoritative**. Phase 3A is not re-run. The frozen result bytes are
deserialized read-only through the existing
`squeeze_core.evaluation.serialization.deserialize_candidate_evaluation`.

---

## 5. Phase 3B contract audit (what the repository actually says)

Authoritative model: `squeeze_core.research.models.CandidateCaseRegistryEntry`
(`extra="forbid"`, `frozen=True`, `schema_version="1.0.0"`).

Fields: `schema_version`, `case_id`, `symbol`, `asset_class`, `case_type`, `case_status`,
`original_platform_status`, `detection_time_evidence_id`, `evaluation_as_of`,
`evaluation_request_path`, `evaluation_result_path`, `outcome_observation_path`,
`original_platform_artifact_ids`, `historical_dataset_ids`, `phase_3a_policy_version`,
`limitations`, `fixture_classification`, `deterministic_id`.

Findings that govern this batch:

1. **An evaluation reference without an outcome is legal.** `evaluation_request_path`,
   `evaluation_result_path`, and `outcome_observation_path` are independent
   `str | None` fields with no cross-field validator tying them together. There is no
   "outcome required" constraint anywhere in the entry, the registry, or the publication
   adapter. **Stop condition 5 does not fire.**
2. **`squeeze_core.research.io.load_phase_3a_result` requires `result.as_of ==
   entry.evaluation_as_of`.** Therefore attaching an evaluation reference *forces*
   `evaluation_as_of` to be set to the frozen boundary. This is a contract-required change,
   not a discretionary one.
3. **Artifact paths must be relative and must resolve inside `registry_path.parent.parent`**
   (`squeeze_core.research.io.resolve_artifact_path`; absolute paths raise). This dictates
   where the preview registry file is written (Section 9).
4. **Identity.** `CandidateCaseRegistryEntry.deterministic_id` is UUIDv5 over a canonical
   identity dict containing `case_status`, `evaluation_as_of`, and `limitations` — but **not**
   the three path fields. So paths alone would not move the ID; `evaluation_as_of` (forced by
   finding 2) and the limitation/status updates do.
5. **`CandidateCaseRegistry` uniqueness** is over `case_id` and over
   `(symbol, evaluation_as_of)`. All 13 symbols are distinct, so a shared boundary
   `evaluation_as_of` raises no `RESEARCH_CASE_IDENTITY_CONFLICT`.
6. **`squeeze_core.research.batch.run_research_batch`** classifies an entry as incomplete when
   `case_status is not COMPLETE` **or** both evaluation paths are null **or**
   `outcome_observation_path` is null. Incomplete entries are **skipped** (with
   `RESEARCH_CASE_STATUS_INCOMPLETE` + `RESEARCH_CASE_OUTCOME_MISSING` diagnostics) rather
   than failing, and never reach `classify_research_case`. Evaluation-present /
   outcome-absent is therefore a first-class, non-crashing state. **Stop condition 10 does
   not fire.**
7. **`squeeze_core.acquisition.publication.build_phase3b_registry_candidate`** validates
   `case_id` and `symbol` agreement and returns the source entry unchanged; it neither
   requires nor forbids an evaluation reference.

**Contract audit conclusion: `PREVIEW_COMPATIBLE_WITH_LIMITATIONS`.** The revision is legal
under the existing schema and policies. The limitation is scientific, not structural:
detection stays `UNEVALUABLE` and the candidates stay outside the empirical dataset.

Full audit is written to `docs/batch-09-phase3b-contract-audit.md`.

---

## 6. Allowed mutations (exhaustive)

Only these fields may differ between the current entry and the preview entry:

| Field | From | To | Why |
|---|---|---|---|
| `evaluation_request_path` | `null` | relative path to the frozen Batch 08 request | the reference being previewed |
| `evaluation_result_path` | `null` | relative path to the frozen Batch 08 result | the reference being previewed |
| `evaluation_as_of` | `null` | `2026-07-18T13:37:55.017661Z` | **contract-required** by `io.load_phase_3a_result` |
| `case_status` | `ARTIFACT_DISCOVERY_ONLY` | `EVALUATION_ONLY` | the enum member that exactly denotes evaluation-present / outcome-absent; leaving it would make the entry self-contradictory |
| `limitations` | see below | see below | must stop asserting "no Phase 3A evaluation" and must start asserting why detection is still unevaluable |
| `deterministic_id` | Batch 01 value | recomputed UUIDv5 | mechanical consequence of the above |

Limitation edits, exactly:

- **removed:** `REGISTRY_ONLY_NO_PHASE_3A_EVALUATION` (no longer true)
- **added:** `PHASE_3A_EVALUATION_FROZEN_BATCH_08`
- **added:** `RESEARCH_DETECTION_UNEVALUABLE_PRICE_RANGE_UNRESOLVED`
- **added:** `GLOBAL_PREFLIGHT_REJECTED_EVIDENCE_ADMISSIBILITY_LIMITED`
- **retained unchanged:** `OUTCOME_WINDOW_NOT_ACQUIRED_OFFLINE`,
  `IDENTITY_PARTIALLY_RESOLVED_ISSUER_EXCHANGE_UNKNOWN`, and every
  `DETECTION_DOMAIN_MISSING:*` entry.

`limitations` is normalized by the existing model validator (`sorted(set(...))`); the preview
relies on that existing behaviour rather than sorting independently.

---

## 7. Forbidden mutations (immutable fields)

These must be **identical** in the preview, and a committed test asserts each one:

`schema_version`, `case_id`, `symbol`, `asset_class`, `case_type`,
`original_platform_status`, `detection_time_evidence_id`,
`original_platform_artifact_ids`, `historical_dataset_ids`, `phase_3a_policy_version`,
`fixture_classification`, `outcome_observation_path`.

Also immutable, outside the entry model: case membership, source order, the frozen boundary
`2026-07-18T13:37:55.017661Z`, Batch 01 discovery provenance and eligibility, the Batch 01
raw artifact identity `batch01-screener-snapshot-raw`, the detection boundary, the Phase 3B
detection policy `phase_3b_research_detection_policy.v1`, the outcome label policy, and all
Batch 08 Phase 3A request/result bytes.

`outcome_observation_path` stays `null` for all 13 cases. Outcome status stays incomplete.

---

## 8. Identity and candidate-version behaviour

Because `evaluation_as_of`, `case_status`, and `limitations` all participate in the entry
identity dict, **every preview candidate receives a new deterministic UUIDv5**:

- `candidate_identity_changed = true` for all 13 cases;
- `current_registry_candidate_id` and `preview_registry_candidate_id` are both recorded;
- the original candidate is **not** overwritten — the canonical Batch 01 registry is untouched
  and the preview is written to a separate location;
- the preview registry gets its own `registry_version =
  phase_3d_batch_09_registry_preview.v1`, so the preview registry document also has its own
  deterministic ID and cannot be mistaken for `phase_3d_batch_01_registry.v1`.

The identity transition is documented per case in `docs/batch-09-registry-field-diff.md`.

---

## 9. Output locations (dry-run only)

**Private, Git-ignored** (real Phase 3A references):
`intake/local-bars/ibkr-batch-05/phase3b-preview-batch-09/`

That exact depth is required: `resolve_artifact_path` resolves declared paths against
`registry_path.parent` and confines them to `registry_path.parent.parent`. With the preview
registry at `intake/local-bars/ibkr-batch-05/phase3b-preview-batch-09/phase3b-registry-preview.json`,
the confinement root is `intake/local-bars/ibkr-batch-05/` and the declared references
`../phase3a/batch-08/requests/<CASE_ID>.json` and `../phase3a/batch-08/results/<CASE_ID>.json`
resolve legally.

Private files written:

- `phase3b-registry-preview.json` — the preview `CandidateCaseRegistry`
- `registry-preview.jsonl`, `registry-preview.csv` — deterministic projections
- `dataset-dry-run.json`, `dataset-dry-run.jsonl`, `dataset-dry-run.csv` — existing Phase 3B
  dataset serializers applied to the dry-run batch result
- `batch-dry-run.json` — the `BatchEvaluationResult` (0 case results, 13 skipped)
- `candidate-previews.json`, `registry-field-diff.json`, `detection-preview.json`,
  `phase3c-compatibility.json`, `preview-summary.json`

**Committed, sanitized** (IDs, hashes, statuses; no OHLCV-derived values):
`tests/fixtures/acquisition/batch09/`

- `registry-revision-preview.json` — the 13 preview records
- `registry-field-diff.json` — the canonical before/after diff
- `synthetic-registry/` — a fully synthetic registry + Phase 3A artifacts used by the
  compatibility tests, mirroring the Batch 08 convention of committing synthetic mirrors only

Nothing is written over any existing Batch 01, Batch 02, or Phase 3D Phase 3B artifact.

---

## 10. Detection behaviour (policy executed, never assigned)

The existing `phase_3b_research_detection_policy.v1` is loaded unchanged via
`squeeze_core.research.policies.load_detection_policy` and executed by the existing
`squeeze_core.research.detection.evaluate_research_detection` against each deserialized
Batch 08 result.

Required rules: `PRICE_RANGE`, `MARKET_DATA_AVAILABLE`, `COMPLETED_BAR_AVAILABLE`.
Resolution: all PASS → `DETECTED`; any FAIL → `NOT_DETECTED`; otherwise → `UNEVALUABLE`.

Expected (to be confirmed by execution, not assumed): `MARKET_DATA_AVAILABLE = PASS` and
`COMPLETED_BAR_AVAILABLE = PASS` for all 13; `PRICE_RANGE = UNKNOWN` for all 13, because
absolute-price semantics remain blocked by Batch 07
(`ABSOLUTE_PRICE_LEVEL_BLOCKED_BY_BATCH07`). Therefore detection resolves `UNEVALUABLE`.

Explicitly forbidden and test-guarded: substituting `PERCENTAGE_CHANGE_MINIMUM` for
`PRICE_RANGE`; editing the required-rule set; hand-assigning any detection status.

**A preview in which all 13 detections remain `UNEVALUABLE` is a valid, expected result and
is not a failure.**

---

## 11. Outcome and research-classification behaviour

Binding: the 13 cases still have **no valid frozen forward outcome data**. The Batch 05
`FROZEN_FORWARD_24H` responses are not valid forward-outcome evidence (the frozen boundary
falls on a weekend and IBKR returned previous-available-Friday bars).

Therefore, for every previewed candidate:

- `outcome_observation_path = null`
- `outcome_status = OUTCOME_INCOMPLETE_NO_VALID_FORWARD_EVIDENCE`
- `research_classification_status = NOT_PRODUCED_OUTCOME_INCOMPLETE`

No outcome observation, reference price, +25% crossing, −25% crossing, retrospective label,
TP/FP/TN/FN, or outcome-derived classification is created. No forward OHLCV value is read.
`classify_research_case` is **not** called for any real case.

The preview establishes three separate dimensions that must not be conflated:

| Dimension | State after the proposed revision |
|---|---|
| Phase 3A **evaluation** completeness | complete (13/13 frozen) |
| Phase 3B **research detection** completeness | not complete (13/13 `UNEVALUABLE`) |
| Phase 3B **outcome** completeness | not complete (13/13 absent) |

---

## 12. Publication simulation

The existing publication path is reused; no second implementation is written.

1. Build a `BatchEvaluationRequest` over the 13 case IDs against the preview registry version.
2. Run the existing `run_research_batch` against the **preview** registry path.
3. Build the dataset with the existing `build_research_dataset`.
4. Serialize with the existing `serialize_research_json`, `serialize_research_jsonl`,
   `serialize_research_csv`, and `serialize_research_model`.
5. Regenerate everything a second time in a separate directory and compare bytes.

Expected: 0 case results, 13 skipped cases, a 0-row dataset, valid JSON/JSONL/CSV. That is
the honest structural proof that the revision publishes cleanly *and* adds no empirical row.

If any step required mutating a canonical artifact, the batch stops (stop condition 9).

---

## 13. Phase 3C compatibility

Structural only. No new empirical Phase 3C analysis on the real cohort.

- On the **real preview**: `load_case_registry` succeeds, `build_registry_cohort` includes the
  13 entries, `build_registry_data_quality` runs, and nothing crashes on
  evaluation-present / outcome-absent entries. Membership counts are recorded; no new
  predictive or descriptive statistics for the real cohort are published.
- On a **synthetic** registry committed under `tests/fixtures/acquisition/batch09/`: the full
  `run_research_analysis` registry-cohort path executes, proving Phase 3C does not assume
  outcome existence, does not read `UNKNOWN` as zero, does not read `UNEVALUABLE` as
  `NOT_DETECTED`, and does not crash.

---

## 14. Preview decision vocabulary

```
PREVIEW_COMPATIBLE
PREVIEW_COMPATIBLE_WITH_LIMITATIONS
PREVIEW_BLOCKED_SCHEMA
PREVIEW_BLOCKED_IDENTITY
PREVIEW_BLOCKED_POLICY
PREVIEW_BLOCKED_INTEGRITY
```

Per case, the question answered is: *can this candidate be safely revised to reference its
frozen Phase 3A evaluation without changing discovery or outcome truth?* A `yes` is compatible
with detection remaining `UNEVALUABLE`; the two are separate concepts.

Supporting vocabularies (deterministic, closed sets):

- `outcome_status`: `OUTCOME_INCOMPLETE_NO_VALID_FORWARD_EVIDENCE`
- `research_classification_status`: `NOT_PRODUCED_OUTCOME_INCOMPLETE`
- diff change kinds: `ADDED`, `CHANGED`, `UNCHANGED`, `FORBIDDEN_TO_CHANGE`

---

## 15. Required per-case preview record

`case_id`, `symbol`, `current_registry_candidate_id`, `preview_registry_candidate_id`,
`candidate_identity_changed`, `current_evaluation_reference`,
`preview_evaluation_request_id`, `preview_evaluation_result_id`,
`preview_evaluation_request_sha256`, `preview_evaluation_result_sha256`,
`frozen_boundary_id`, `discovery_provenance_unchanged`, `global_preflight_status`,
`phase3a_freeze_status`, `phase3a_leakage_status`, `research_detection_status`,
`research_detection_reason`, `outcome_status`, `outcome_path`,
`research_classification_status`, `changed_fields`, `unchanged_fields`,
`compatibility_status`, `publication_ready_if_approved`, `phase3b_published = false`,
`phase3e_started = false`.

Excluded by construction and by a structural field-name guard: raw OHLCV, derived prices,
percentage-return values, forward values, outcome values, scores, ranks, recommendations.

---

## 16. Determinism and identity rules

Existing `canonical_json_bytes` (UTF-8, LF, sorted keys, explicit nulls, exact `Decimal`
strings, no NaN, no infinity) and existing UUIDv5 helpers (`deterministic_research_id`,
`deterministic_acquisition_id`) are reused; nothing is reimplemented.

Stable ordering for source cases, fields, rules, diffs, and diagnostics.

Never in identity: wall clock, absolute paths, credentials, outcomes, unordered iteration, or
the professor's decision. The professor's eventual APPROVE / REVISE / DO NOT PROCEED is
**governance metadata** and must never retroactively alter scientific identity.

---

## 17. Tests

Committed coverage for: the exact Batch 08 checkpoint; the exact 13-case source order; 13
frozen requests and 13 frozen results present; 13 leakage audits passed; Batch 08 artifact
hashes verify; canonical Phase 3B registries byte-unchanged; preview references the correct
request/result IDs and sha256s; `outcome_path` null and outcome status incomplete;
`PRICE_RANGE` unresolved/`UNKNOWN`; both availability rules `PASS`; the detection policy file
unchanged; detection resolving `UNEVALUABLE` when `PRICE_RANGE` is `UNKNOWN`; no
`PERCENTAGE_CHANGE_MINIMUM` substitution; no fabricated classification; deterministic
candidate IDs; deterministic diff; deterministic dry-run JSON/JSONL/CSV; Phase 3C structural
loader accepting evaluation-present/outcome-absent candidates; no real OHLCV committed; no
forward OHLCV read; no outcome access; no network; no `ibapi`; no canonical Phase 3B
publication; no Phase 3E; no score/rank/recommendation field; Batch 01–08 artifacts unchanged;
Batch 05 raw hashes unchanged; documentation presence.

---

## 18. True stop conditions

Stop and report without improvising if: the Batch 08 checkpoint differs; the baseline cannot
be reproduced; prior canonical artifacts are unexpectedly modified; Batch 05 or Batch 08
private hashes fail; Phase 3B cannot reference a Phase 3A result without an outcome; registry
identity would require rewriting historical case identity; attaching an evaluation would alter
discovery provenance; attaching an evaluation would silently alter detection or outcome
policy; publication cannot be dry-run without mutating canonical artifacts; Phase 3C cannot
represent evaluation-present/outcome-absent candidates; preview generation would require
outcome access or forward OHLCV; implementation would require changing Phase 3A
thresholds/results; implementation would require Phase 3E.

Gates already cleared before this plan was committed: checkpoint, baseline, Batch 05 raw
integrity (26/26), Batch 08 freeze integrity (26/26), archived topology, and the contract
audit (Section 5, findings 1 and 6).

---

## 19. Definition of done

Batch 09 is complete only when: the checkpoint and baseline are verified; the Batch 08 freeze
is verified; the Phase 3B contract is audited; this plan is preregistered; exactly 13 registry
revision previews exist; exact before/after diffs exist; frozen Phase 3A references validate;
outcome paths remain null and outcomes remain incomplete; the existing detection policy is
executed unchanged and reported honestly; dry-run JSON/JSONL/CSV validate and regenerate
byte-identically; the canonical registry remains byte-identical; Phase 3C structural
compatibility is proven; no outcome or forward data is accessed; the full suite passes; prior
and archived artifacts remain unchanged; the professor decision package, talking points,
completion report, and a real Batch 10 handoff exist; the exact final HEAD is reported; Phase
3E remains unstarted; and work stops.

Schema version remains `1.0.0` throughout.
