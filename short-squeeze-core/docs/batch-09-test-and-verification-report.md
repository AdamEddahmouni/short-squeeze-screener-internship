# Batch 09 — Test and Verification Report

Branch `batch/phase-3d-phase3b-registry-preview-09`, from Batch 08
`c93f704104429468f920b0d0d88002a821c68b63`.

---

## Verification sequence

| # | Step | Result |
|---|---|---|
| 1 | Batch 08 checkpoint verified | `c93f704104429468f920b0d0d88002a821c68b63`, branch `batch/phase-3d-phase3a-freeze-08`, clean except the pre-existing untracked `docs/phase-3c-complete-handoff.md` |
| 2 | Baseline reproduced (authoritative JUnit XML) | **2,320 collected / 2,319 passed / 1 skipped / 0 failed / 0 errors** |
| 3 | `phase-1-rc1` tag verified | `phase-1-rc1^{}` = `f903d4d144d3f7e9717b1ab8e684da406d7968fb` |
| 4 | Batch 05 private raw integrity | **26/26 artifacts hash-match, 0 mismatches** |
| 5 | Batch 08 Phase 3A freeze integrity | **26/26 request+result artifacts hash-match, 0 mismatches**; 13/13 `REQUEST_AND_RESULT_FROZEN`; 13/13 `LEAKAGE_AUDIT_PASSED`; `forward_ohlcv_accessed` false ×13; `outcome_accessed` false ×13 |
| 6 | Archived topology verified read-only | parent `0897562e05d75b812dd284de81dfafdfa1dea916`; nested submodule `6dbefd1a6b271bfc48106c4aa002f211735551cd`; unmodified |
| 7 | Phase 3B contract audited | `PREVIEW_COMPATIBLE_WITH_LIMITATIONS` — see `docs/batch-09-phase3b-contract-audit.md` |
| 8 | Plan preregistered and committed | `321ddfa6a799613461a4677942cd00af0b65c7d5` |
| 9 | 13-case preview generated | 13 candidates, source order preserved |
| 10 | Before/after diffs computed | 18 fields × 13 cases = 234 field observations |
| 11 | Existing detection policy executed | `UNEVALUABLE` ×13 |
| 12 | Outcome state confirmed unchanged | `outcome_observation_path` null ×13 |
| 13 | Publication dry run to isolated path | 0 results, 13 skipped, 0 dataset rows |
| 14 | JSON/JSONL/CSV serialized twice | 14 files, both runs |
| 15 | Bytes compared | **0 differences across all 14 files** |
| 16 | Phase 3C structural compatibility | registry loads, 13/13 included, no crash, no assumed outcome |
| 17 | Focused Batch 09 tests | pass |
| 18 | Acquisition / research / analysis / compatibility / validation suites | pass |
| 19 | Authoritative final full suite | see below |
| 20 | Canonical Phase 3B registries unchanged | 4 files, sha256 identical |
| 21 | No forward OHLCV read | confirmed |
| 22 | No outcome access | confirmed |
| 23 | No network / no `ibapi` | confirmed by import-line guard |
| 24 | Prior artifacts unchanged | Batch 01–08 committed artifacts untouched |
| 25 | Archived topology re-verified | unchanged |

---

## Determinism

The full preview was regenerated into a second isolated directory and compared byte-for-byte:

```
files compared: 14   byte-differences: 0
```

Covered files: `phase3b-registry-preview.json`, `registry-preview.jsonl`,
`registry-preview.csv`, `dataset-dry-run.json`, `dataset-dry-run.jsonl`,
`dataset-dry-run.csv`, `batch-dry-run.json`, `candidate-previews.json`,
`registry-field-diff.json`, `registry-field-diff.md`, `detection-preview.json`,
`phase3c-compatibility.json`, `preview-summary.json`, `preview-summary.md`.

The synthetic dry-run publication was also executed twice in-process and compared across all
seven serialized products, byte-identically.

Identity inputs exclude wall clock, absolute paths, credentials, outcomes, unordered
iteration, and the professor's decision. Serialization is the project's existing
`canonical_json_bytes`: UTF-8, LF, sorted keys, explicit nulls, exact `Decimal` strings, no
NaN, no infinity.

---

## Canonical artifact integrity

| File | sha256 | Bytes |
|---|---|---|
| `tests/fixtures/acquisition/batch01/phase3b-registry-candidates.json` | `c16b49386f96705d43bb110fa76796ce998299599a49528dc799e1a17e678c73` | 12,668 |
| `tests/fixtures/acquisition/batch02/phase3b-registry-candidates.json` | `af691a27e5568dc4aca9fe94adb07f4efe8ceabe490cb7d88ad9c7ddff9656a2` | 12,707 |
| `tests/fixtures/acquisition/phase_3d_phase3b_registry_candidates.json` | `28d5b14cb7be31665174121011a353eea6afb182c22c43e388fc9e162ba72b07` | 6,851 |
| `tests/fixtures/research/phase_3b_case_registry.json` | `5684ecd6e9f9e5b194379be411654cb5f15f5b24b638339605a2cc232bcb9b79` | 15,473 |

Recorded before any change and asserted by
`test_canonical_phase3b_registries_remain_byte_identical`.

---

## Coverage added

`tests/acquisition/test_batch09_phase3b_preview.py` covers:

- Batch 08 checkpoint is an ancestor of this work
- exact 13-case source order and case IDs
- canonical Phase 3B registries byte-identical (parametrized over 4 files)
- Batch 01 entries still registry-only with `REGISTRY_ONLY_NO_PHASE_3A_EVALUATION`
- all 13 frozen requests, results, and leakage audits present
- Batch 08 artifact hashes verify
- all 13 leakage audits passed, no forward/outcome access
- contract audit permits evaluation without outcome
- allowed and immutable field sets disjoint
- preview entry moves only allowed fields
- preview keeps outcome absent and retires only the stale limitation
- preview refuses a source entry that already has an outcome
- diff refuses a change to a forbidden field
- diff and field-change frequency deterministic
- exactly 13 cases in source order
- no publication, no Phase 3E, no forward/outcome access flags
- `outcome_path` null and outcome status incomplete ×13
- detection `UNEVALUABLE` because `PRICE_RANGE` is `UNKNOWN`, availability rules `PASS`
- no `PERCENTAGE_CHANGE_MINIMUM` substitution
- candidate identity changes deterministically, 13 distinct new IDs
- changed/unchanged field sets match the preregistered plan
- field-change frequency is 13 for every field
- no market-value field names in the committed fixture
- no TP/FP/TN/FN anywhere in the preview (parametrized)
- detection policy file unchanged
- detection resolves `UNEVALUABLE` on the synthetic evaluation
- synthetic registry is evaluation-present / outcome-absent
- synthetic evaluation reference resolves through the existing loader
- batch runner skips rather than fails; no `RESEARCH_CASE_EVALUATION_MISSING`
- Phase 3C structural loader accepts the synthetic preview
- synthetic dry run serializes JSON/JSONL/CSV deterministically
- real preview regenerates byte-identically (private tree)
- real preview matches the committed fixture identity (private tree)
- real preview references the frozen request/result IDs and hashes (private tree)
- real preview registry loads all 13 evaluations (private tree)
- real dry-run publication produces an empty dataset (private tree)
- output root cannot collide with a canonical registry directory
- preview package imports no `ibapi` and no network client
- no real OHLCV committed under the Batch 09 fixtures
- no forbidden field name in any preview model
- generation script is offline and compiles
- Batch 09 documentation is present

Private-tree tests skip cleanly when the Batch 05/08 data is absent, so the suite is green on
a fresh checkout while still asserting the private facts where the data lives.

---

## Final full suite

Run once, authoritatively, at the end of the batch with a fresh `--basetemp` and
`-p no:cacheprovider`:

**2,320 collected → 2,379 collected after Batch 09 additions.**
Final: **2,378 passed / 1 skipped / 0 failed / 0 errors.**

Delta versus baseline: **+59 passed, 0 regressions.** The one skip is the same pre-existing
skip present at the Batch 08 baseline.

Batch 09 added 44 test functions, which expand to 59 cases through parametrization.

---

## No-forward-OHLCV and no-outcome-access: exactly what was and was not read

Stated precisely, because "never opened" would be imprecise:

- **Read for values:** the committed Batch 01 Phase 3B registry, and the Batch 08
  `requests/`, `results/`, and `batch-summary.json` artifacts. The Batch 08 results are frozen
  Phase 3A rule outcomes; they contain no bar values. No Batch 05 raw CSV or JSONL was parsed,
  and no bar field was read into any code path, artifact, or document.
- **Read as bytes for hashing only:** the 26 Batch 05 raw artifacts, including the 13
  `*-frozen-forward-24h.csv` files, were opened and passed to `hashlib.sha256` for the
  integrity gate required by the handoff. No value was decoded, interpreted, stored, or
  reported — only a digest and a byte length, both compared against the existing
  `provenance/sha256-manifest.json`.
- **Never accessed at all:** any outcome observation, reference price, ±25% crossing,
  retrospective label, or research classification. None exists for these 13 cases.

Every Batch 08 record carries `forward_ohlcv_accessed = false` and `outcome_accessed = false`,
and each Batch 09 preview record repeats both flags with a model validator that refuses to
construct the record if either were true.

---

## Deviations from the preregistered plan

One, recorded rather than silently applied:

- **Preview output directory name.** The plan's Section 9 named
  `intake/local-bars/ibkr-batch-05/phase3b-preview-batch-09/` and explained the depth
  requirement; the earlier handoff had suggested `.../phase3b-preview/batch-09/`. The deeper
  nesting is impossible: `resolve_artifact_path` confines declared references to
  `registry_path.parent.parent`, and at that depth `../../phase3a/batch-08/...` escapes the
  confinement root. The plan already froze the corrected path, so the implementation matches
  the plan; this note exists only because it differs from the incoming handoff's example.

No other deviation. No stop condition fired.
