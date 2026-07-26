# Batch 09 — Phase 3B Registry Contract Audit

**Question:** can the existing Phase 3B registry contract legally reference the newly frozen
Batch 08 Phase 3A request/result artifacts while the outcome remains absent?

**Answer: yes.** Conclusion `PREVIEW_COMPATIBLE_WITH_LIMITATIONS`.

Every finding below is read off the repository at runtime by
`squeeze_core.acquisition.phase3b_preview.contract.audit_phase3b_contract`, not restated from
a document. If any of these facts change, the audit raises `Phase3BContractError` instead of
producing a stale claim.

---

## The contract

Authoritative model: `squeeze_core.research.models.CandidateCaseRegistryEntry`
(`extra="forbid"`, `frozen=True`, `schema_version = "1.0.0"`).

| Field | Type | Batch 01 value |
|---|---|---|
| `schema_version` | `str` | `"1.0.0"` |
| `case_id` | `str` | `BATCH01_<SYM>_20260718` |
| `symbol` | `str` | the ticker |
| `asset_class` | `AssetClass` | `EQUITY` |
| `case_type` | `CandidateCaseType` | `ORIGINAL_PLATFORM_SURFACED` |
| `case_status` | `CandidateCaseStatus` | `ARTIFACT_DISCOVERY_ONLY` |
| `original_platform_status` | `OriginalPlatformStatus` | `SURFACED` |
| `detection_time_evidence_id` | `str \| None` | the case ID |
| `evaluation_as_of` | `datetime \| None` | `null` |
| `evaluation_request_path` | `str \| None` | `null` |
| `evaluation_result_path` | `str \| None` | `null` |
| `outcome_observation_path` | `str \| None` | `null` |
| `original_platform_artifact_ids` | `tuple[str, ...]` | `("batch01-screener-snapshot-raw",)` |
| `historical_dataset_ids` | `tuple[str, ...]` | `()` |
| `phase_3a_policy_version` | `str` | `phase_3a_transparent_candidate_policy.v1` |
| `limitations` | `tuple[str, ...]` | sorted set, includes `REGISTRY_ONLY_NO_PHASE_3A_EVALUATION` |
| `fixture_classification` | `FixtureClassification` | `SANITIZED_LOCAL_ARTIFACT` |
| `deterministic_id` | `str \| None` | UUIDv5, auto-assigned |

---

## Finding 1 — `EVALUATION_REFERENCE_WITHOUT_OUTCOME_IS_LEGAL`

`evaluation_request_path`, `evaluation_result_path`, and `outcome_observation_path` are three
independent `str | None` fields, each defaulting to `None`. There is no cross-field validator,
no model validator, and no policy anywhere in `squeeze_core.research` or
`squeeze_core.acquisition.publication` that requires an outcome when an evaluation is present.

**Stop condition 5 ("Phase 3B contract cannot reference a Phase 3A result without an outcome")
does not fire.**

## Finding 2 — `EVALUATION_AS_OF_REQUIRED_BY_LOADER`

`squeeze_core.research.io.load_phase_3a_result` raises
`RESEARCH_CASE_IDENTITY_CONFLICT` when `result.as_of != entry.evaluation_as_of`.

Consequence: attaching an evaluation reference **forces** `evaluation_as_of` to be set to the
frozen boundary `2026-07-18T13:37:55.017661Z`. This is a contract requirement, not a
discretionary edit, and it is the reason candidate identity moves (Finding 4).

The same function also enforces `result.policy_version == entry.phase_3a_policy_version`. Both
are `phase_3a_transparent_candidate_policy.v1`, so the check passes without any policy change.

## Finding 3 — `ARTIFACT_PATHS_RELATIVE_AND_CONFINED`

`squeeze_core.research.io.resolve_artifact_path` rejects absolute paths and confines a
declared path to `registry_path.parent.parent`.

Consequence for the dry run: the preview registry is written to
`intake/local-bars/ibkr-batch-05/phase3b-preview-batch-09/phase3b-registry-preview.json`,
exactly one level under the Batch 05 root, so the declared references
`../phase3a/batch-08/requests/<CASE_ID>.json` and
`../phase3a/batch-08/results/<CASE_ID>.json` resolve legally. Verified end to end: all 13
entries load through `load_phase_3a_result` with matching symbol and `as_of`.

## Finding 4 — `CANDIDATE_IDENTITY_MOVES_VIA_AS_OF_STATUS_AND_LIMITATIONS`

`CandidateCaseRegistryEntry.assign_deterministic_id` builds its UUIDv5 identity from:

`result_type`, `schema_version`, `case_id`, `symbol`, `asset_class`, `case_type`,
`case_status`, `original_platform_status`, `detection_time_evidence_id`, `evaluation_as_of`,
`phase_3a_policy_version`, `original_platform_artifact_ids`, `historical_dataset_ids`,
`limitations`, `fixture_classification`.

The three path fields are **not** in the identity. So the paths alone would leave the
candidate ID untouched; the ID moves because `evaluation_as_of` (forced by Finding 2),
`case_status`, and `limitations` move.

All 13 preview candidates therefore receive a new, deterministic candidate ID. The original
candidates are not overwritten: the canonical registry is untouched and the preview registry
carries its own `registry_version = phase_3d_batch_09_registry_preview.v1`.

**Stop condition 6 does not fire** — no historical case identity is rewritten. `case_id`,
`symbol`, discovery provenance, and the frozen boundary are all unchanged; only the
completeness-state identity of the *registry entry object* is recomputed.

Registry-level uniqueness is over `case_id` and over `(symbol, evaluation_as_of)`. All 13
symbols are distinct, so a shared boundary raises no conflict.

## Finding 5 — `INCOMPLETE_CANDIDATE_IS_SKIPPED_NOT_FAILED`

`squeeze_core.research.batch.run_research_batch` marks an entry incomplete when

```
case_status is not COMPLETE
or (evaluation_result_path is None and evaluation_request_path is None)
or outcome_observation_path is None
```

and, with `fail_fast=False`, appends it to `skipped_cases` with
`RESEARCH_CASE_STATUS_INCOMPLETE` and `RESEARCH_CASE_OUTCOME_MISSING` diagnostics, then
continues. Evaluation-present / outcome-absent is a first-class, non-crashing state.

Observed in the real dry run: 13 entered, **13 skipped**, 0 case results, diagnostics exactly
`{RESEARCH_CASE_OUTCOME_MISSING, RESEARCH_CASE_STATUS_INCOMPLETE}`. Note that
`RESEARCH_CASE_EVALUATION_MISSING` is **absent** — the runner recognises the new evaluation
reference. That absence is the machine-checkable proof that the revision did what it claims.

**Stop condition 10 does not fire.**

## Finding 6 — `RESEARCH_CLASSIFICATION_SUPPRESSED_WITHOUT_OUTCOME`

`classify_research_case` is reachable only from `_build_case`, which is reachable only for
complete candidates. A candidate with no outcome can never receive a TP/FP/TN/FN. No guard in
Batch 09 is needed to prevent classification; the existing contract already prevents it, and
Batch 09 records that fact rather than re-implementing it.

## Finding 7 — `REGISTRY_PUBLICATION_ADAPTER_NEUTRAL_ON_EVALUATION_REFERENCE`

`squeeze_core.acquisition.publication.build_phase3b_registry_candidate` validates only that
the curated bundle's case ID and symbol match the registry entry, then returns the entry
unchanged. It neither requires nor forbids an evaluation reference. Dataset publication is
separately gated on a complete, leakage-passing, non-synthetic bundle — which these 13 are
not, and are not claimed to be.

---

## Consequences for Batch 09

| Question | Answer |
|---|---|
| Can Phase 3B reference the new artifacts? | Yes |
| Which fields must change? | `evaluation_request_path`, `evaluation_result_path`, `evaluation_as_of`, `case_status`, `limitations`, `deterministic_id` |
| Which fields must not change? | the 12 immutable fields, including `outcome_observation_path` |
| Does candidate identity change? | Yes, deterministically, for all 13 |
| Does the schema validate? | Yes — schema `1.0.0`, unchanged |
| Does research detection change? | No: still `UNEVALUABLE` for all 13 |
| Does outcome status change? | No: still absent for all 13 |
| Is a classification produced? | No, and the existing contract makes that structural |
| Is the revision backward-compatible? | Yes: the canonical registry is untouched and Phase 3C loads the preview without assuming an outcome |

**Contract audit conclusion: `PREVIEW_COMPATIBLE_WITH_LIMITATIONS`.**
