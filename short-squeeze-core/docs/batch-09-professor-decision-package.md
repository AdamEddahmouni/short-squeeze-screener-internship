# Phase 3B Registry Revision — Decision Package

Prepared: Batch 09 (Phase 3D). Branch `batch/phase-3d-phase3b-registry-preview-09`.
Nothing in this package has been published. The canonical Phase 3B research registry is
byte-for-byte unchanged.

---

## 1. What changed since the previous meeting

- **13 real symbols** were frozen from an outcome-blind scanner snapshot (Batch 01), boundary
  `2026-07-18T13:37:55.017661Z`.
- **Official IBKR historical data was acquired and preserved** (Batch 05): 26 raw artifacts,
  hash-verified, read-only, under a private Git-ignored path.
- **Semantic limitations were documented rather than guessed** (Batch 06): price adjustment
  resolved as `SPLIT_ADJUSTED` from official evidence; volume adjustment, intraday timestamp
  meaning, and volume unit remain officially unresolved and are recorded as unresolved.
- **Operation-specific admissibility was added** (Batch 07): price *ratios* are admissible;
  absolute price levels and volume are blocked, because their semantics are unresolved.
- **13 Phase 3A requests were frozen** (Batch 08).
- **13 Phase 3A results were frozen** (Batch 08).
- **325 rule-case evaluations now exist** (25 rules × 13 cases).
- **The leakage audit passed for every case** (13/13 `LEAKAGE_AUDIT_PASSED`).
- **No outcomes were used** anywhere in the above. `forward_ohlcv_accessed = false` and
  `outcome_accessed = false` on all 13 frozen records.

---

## 2. Current Phase 3A findings

**325 rule-case pairs:**

| Outcome | Count |
|---|---|
| PASS | 97 |
| FAIL | 20 |
| UNKNOWN | 208 |
| CONFLICTED | 0 |
| INSUFFICIENT_DATA | 0 |
| NOT_APPLICABLE | 0 |

**By category:**

| Category | PASS | FAIL | UNKNOWN | n |
|---|---|---|---|---|
| MOMENTUM_DISCOVERY | 32 | 7 | 39 | 78 |
| SHORT_PRESSURE_CONFIRMATION | 0 | 0 | 91 | 91 |
| CATALYST_EVIDENCE | 0 | 0 | 65 | 65 |
| EVIDENCE_VALIDITY | 65 | 13 | 13 | 91 |

**Availability rules: 26/26 PASS.** `MARKET_DATA_AVAILABLE` PASS ×13 and
`COMPLETED_BAR_AVAILABLE` PASS ×13. The data we acquired is genuinely present and usable for
the operations it is admissible for.

**`PERCENTAGE_CHANGE_MINIMUM`: 6 PASS, 7 FAIL.**

- PASS: XNCR, PESI, SLS, SSPC, LBGJ, TRVI
- FAIL: ZNTL, GPRE, LMNX, MGNX, BHVN, OBE, AVTX

**Short-pressure: 91 UNKNOWN. Catalyst: 65 UNKNOWN.**

**`UNKNOWN` is intentional missing-evidence handling, not failure.** The evaluator
distinguishes "this rule was tested and did not hold" (FAIL) from "no admissible evidence
existed to test this rule" (UNKNOWN). Short interest, borrow fee, borrow availability, float,
news, and SEC filing evidence do not exist in the acquired data at all — so those rules
correctly report UNKNOWN instead of silently defaulting to a value. Treating them as FAIL, or
as zero, would fabricate evidence.

---

## 3. Why Phase 3B is still incomplete

Research detection under the fixed policy `phase_3b_research_detection_policy.v1` requires all
three of:

- `PRICE_RANGE`
- `MARKET_DATA_AVAILABLE`
- `COMPLETED_BAR_AVAILABLE`

Two of the three now PASS for all 13 cases. **`PRICE_RANGE` remains blocked** because it needs
an absolute price level, and absolute-price semantics remain unresolved (Batch 07 reason code
`ABSOLUTE_PRICE_LEVEL_BLOCKED_BY_BATCH07`). It resolves `UNKNOWN` for all 13.

Under the policy's fixed resolution rule (all PASS → `DETECTED`; any FAIL → `NOT_DETECTED`;
otherwise → `UNEVALUABLE`), detection is therefore **`UNEVALUABLE` for all 13 cases**. That
status was produced by executing the existing policy, not assigned by hand.

**Forward outcome evidence is also unavailable.** The frozen boundary falls on a weekend, and
IBKR returned previous-available-Friday bars for the forward window. Those responses are not
valid forward-outcome evidence, so no outcome exists for any of the 13 cases.

Consequently:

| Dimension | Status |
|---|---|
| Phase 3A **evaluation** completeness | **complete** — 13/13 frozen |
| Phase 3B **detection** completeness | **not complete** — 13/13 `UNEVALUABLE` |
| Phase 3B **outcome** completeness | **not complete** — 13/13 absent |
| **Predictive validation** | **does not exist** |

These are four separate things. Having the first does not give us the others.

---

## 4. What the proposed registry revision would do

For each of the 13 existing registry candidates it would:

1. set `evaluation_request_path` to the frozen Batch 08 request;
2. set `evaluation_result_path` to the frozen Batch 08 result;
3. set `evaluation_as_of` to the frozen boundary (**required** by the Phase 3B loader, which
   cross-checks the result's `as_of` against the entry);
4. change `case_status` from `ARTIFACT_DISCOVERY_ONLY` to `EVALUATION_ONLY` — the enum member
   that means exactly "evaluation present, outcome absent";
5. retire the now-false limitation `REGISTRY_ONLY_NO_PHASE_3A_EVALUATION` and add three
   accurate ones (evaluation frozen; detection unevaluable because `PRICE_RANGE` is
   unresolved; global preflight rejected);
6. recompute the candidate's deterministic UUIDv5, which is a mechanical consequence of 3–5.

It would **not**:

- claim detection (all 13 stay `UNEVALUABLE`);
- invent, substitute, or relax `PRICE_RANGE`;
- create outcomes, reference prices, or ±25% crossings;
- claim predictive accuracy;
- create buy/sell recommendations;
- backtest;
- alter thresholds, the detection policy, or the outcome policy;
- change case membership, case IDs, symbols, discovery provenance, eligibility, the frozen
  boundary, or the raw source artifact identity.

**Verified consequence of publishing it:** running the existing Phase 3B pipeline over the
revised registry yields **0 dataset rows and 13 skipped cases**, with diagnostics
`RESEARCH_CASE_STATUS_INCOMPLETE` and `RESEARCH_CASE_OUTCOME_MISSING` — and *not*
`RESEARCH_CASE_EVALUATION_MISSING`. The revision adds a verifiable evidence link and adds
**zero** empirical rows. That is the honest result, and it is machine-checked.

---

## 5. Field-level summary

**Changed (6 fields × 13 cases):** `evaluation_request_path` (ADDED),
`evaluation_result_path` (ADDED), `evaluation_as_of` (ADDED), `case_status` (CHANGED),
`limitations` (CHANGED), `deterministic_id` (CHANGED).

**Pinned and verified unchanged (12 fields × 13 cases):** `schema_version`, `case_id`,
`symbol`, `asset_class`, `case_type`, `original_platform_status`,
`detection_time_evidence_id`, `original_platform_artifact_ids`, `historical_dataset_ids`,
`phase_3a_policy_version`, `fixture_classification`, **`outcome_observation_path`**.

Schema stays `1.0.0`. The canonical registry file's sha256
(`c16b4938…e678c73`) is unchanged and test-guarded.

---

## 6. The single decision requested

> **Do you approve revising the Phase 3B research registry so these 13 existing real-symbol
> candidates reference their frozen Phase 3A evaluations while remaining explicitly
> `UNEVALUABLE` for research detection and outcome-incomplete?**

This is **not** a request to approve predictive validity, detection, or any trading claim.

Recorded decision (one of):

- **APPROVE** — perform the real deterministic Phase 3B registry revision in Batch 10,
  exactly matching this preview.
- **REVISE** — specify methodological changes; Batch 10 preregisters them before applying.
- **DO NOT PROCEED** — leave the registry unchanged; Batch 10 documents the decision only.

The decision is governance metadata. It is recorded separately and never enters any
scientific identity, so it cannot retroactively alter what was frozen.

---

## 7. Supporting material

| Document | Contents |
|---|---|
| `docs/batch-09-phase3b-registry-preview-plan.md` | preregistered plan (committed before generation) |
| `docs/batch-09-phase3b-contract-audit.md` | why the revision is legal, read off the code |
| `docs/batch-09-registry-field-diff.md` | exact before/after diff, all fields, all 13 cases |
| `docs/batch-09-phase3b-detection-preview.md` | detection execution and rule outcomes |
| `docs/batch-09-phase3c-compatibility-preview.md` | downstream structural compatibility |
| `docs/batch-09-test-and-verification-report.md` | verification sequence and results |
| `docs/batch-09-professor-talking-points.md` | one-page Q&A for the meeting |
| `tests/fixtures/acquisition/batch09/` | sanitized machine-readable preview and diff |
