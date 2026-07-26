# Batch 09 — Phase 3C Structural Compatibility Preview

**Structural only.** No new empirical Phase 3C analysis was run on the real cohort, and no new
predictive or descriptive statistic was produced for the 13 real symbols.

The question here is narrow: can the downstream research and analysis layers *represent* a
candidate that has an evaluation but no outcome, without crashing and without silently
inventing a value?

**Answer: yes, on all four failure modes.**

---

## 1. Phase 3B batch runner — real preview registry

`run_research_batch` over the 13 preview candidates:

| Metric | Value |
|---|---|
| case results | **0** |
| skipped cases | **13** |
| dataset rows | **0** |
| skipped diagnostic codes | `RESEARCH_CASE_OUTCOME_MISSING`, `RESEARCH_CASE_STATUS_INCOMPLETE` |
| `RESEARCH_CASE_EVALUATION_MISSING` present? | **no** |
| exception raised? | no |

The absence of `RESEARCH_CASE_EVALUATION_MISSING` is the machine-checkable proof that the
runner recognised the newly attached evaluation reference. Before the revision, that
diagnostic is emitted; after it, only the outcome-related ones remain.

Also verified end to end: all 13 declared references resolve through
`squeeze_core.research.io.load_phase_3a_result`, with `symbol` and `as_of` matching the entry
and `policy_version` matching `phase_3a_transparent_candidate_policy.v1`. The references are
live, not decorative.

## 2. Phase 3C registry cohort — real preview registry

`squeeze_core.analysis.cohorts.build_registry_cohort` over the preview registry:

| Metric | Value |
|---|---|
| registry loaded | yes |
| entries | 13 |
| included cases | 13 |
| excluded cases | 0 |
| evaluation-present entries | 13 |
| outcome-absent entries | 13 |
| loader raised | no |

Cohort membership ID `bbfe3532-efa2-504f-8653-8db1d5d8f08d`; preview registry ID
`33c21783-0424-50b1-8920-aa3beef4de39`.

Only membership resolution was executed. No prevalence, confusion matrix, interval, or
proportion was computed for the real cohort — the analysis path that produces those is
exercised against synthetic data instead (Section 3).

## 3. Synthetic compatibility fixture (committed)

`tests/fixtures/acquisition/batch09/synthetic-preview/` holds a fully synthetic,
single-candidate registry in exactly the previewed state: `case_status = EVALUATION_ONLY`,
`evaluation_result_path` set, `outcome_observation_path = null`, and a Phase 3A evaluation in
which `PRICE_RANGE` is `UNKNOWN` while both availability rules are `PASS`.

Committed tests assert against it that the pipeline:

- loads the registry and resolves the evaluation reference;
- resolves detection to `UNEVALUABLE` (not `NOT_DETECTED`);
- **skips** the candidate rather than failing the batch;
- emits `RESEARCH_CASE_OUTCOME_MISSING` but not `RESEARCH_CASE_EVALUATION_MISSING`;
- produces a 0-row dataset with no research classification;
- serializes valid JSON, JSONL, and CSV, byte-identically across two runs.

No real symbol and no licensed value appears anywhere in this fixture.

## 4. The four failure modes, checked

| Failure mode | Result |
|---|---|
| assumes an outcome exists | **no** — the incomplete branch is taken before any outcome load |
| interprets `UNKNOWN` as zero | **no** — `UNKNOWN` propagates as `UNKNOWN`; the 0-row dataset has no rule counts to zero-fill |
| interprets `UNEVALUABLE` as `NOT_DETECTED` | **no** — `NOT_DETECTED` requires a required-rule `FAIL`; there is none |
| crashes on evaluation-present / outcome-absent | **no** — skipped with diagnostics, batch completes |

---

## Backward compatibility

- The canonical Phase 3B registries are byte-identical (four files, sha256-guarded by test).
- The preview carries a distinct registry version, `phase_3d_batch_09_registry_preview.v1`, so
  it can never be mistaken for `phase_3d_batch_01_registry.v1`.
- Schema stays `1.0.0`; no model, policy, or serializer was modified.
- Existing consumers that filter on `case_status is COMPLETE` are unaffected: the previewed
  candidates were excluded before the revision and remain excluded after it.

**Phase 3C compatibility result: `PREVIEW_COMPATIBLE_WITH_LIMITATIONS`.** The single limitation
is that the candidates contribute zero empirical rows — which is the correct behaviour, not a
defect.
