# Batch 01 — Data-Quality Report

## Artifact inventory

| Metric | Count |
| --- | --- |
| Artifacts recorded | 2 |
| Hash-valid | 2 |
| Hash-failed | 0 |
| Missing | 0 |
| Duplicate | 0 |
| Restricted-local (referenced, not copied) | 1 (raw scanner export) |
| Sanitized derived (committed) | 1 (discovery rows) |
| Unsupported | 0 |
| Historical / current | both `HISTORICAL` |

- Raw scanner export: `RESTRICTED_LOCAL_ARTIFACT`, SHA-256
  `4e5fbec4…f667d598`, 20104 bytes, `content_status = REFERENCED_NOT_COPIED`.
- Sanitized discovery rows: `DERIVED_NORMALIZED_ARTIFACT`, re-hashed against the
  committed bytes at generation time (`artifact-verification.json`, `valid =
  true`).

## Identity quality

| State | Count |
| --- | --- |
| `RESOLVED` | 0 |
| `PARTIALLY_RESOLVED` | 13 |
| `CONFLICTED` | 0 |
| `UNRESOLVED` | 0 |

All 13 are partially resolved because the scanner row carries the ticker only.
No corporate-action or symbol-reuse conflicts were asserted (none are evidenced,
and none are fabricated). Note that SLS, LBGJ, and TRVI also appear in the prior
Phase 3D migrated registry; batch-01 keeps them distinct via batch-scoped case
IDs (`BATCH01_<SYMBOL>_20260718`) and does not merge with prior fixtures.

## Detection-time evidence completeness (per case)

Present for all 13: price, relative volume, intraday percent change (detection
time, **not** a forward outcome), float shares, shares short.

Missing domains recorded honestly (never imputed):

| Missing domain | Affected symbols |
| --- | --- |
| `IB_BORROW_FEE_RATE` | all 13 (borrow feed down at capture) |
| `IB_SHORTABLE_SHARES` | all 13 |
| `SCHWAB_HTB_QUANTITY` | all 13 |
| `SHORT_FLOAT_PERCENT` | SSPC, LMNX |
| `DAYS_TO_COVER` | SSPC, LMNX |

Every case additionally records the structurally missing domains
`NORMALIZED_POINT_IN_TIME_EVIDENCE`, `RETROSPECTIVE_OUTCOME_WINDOW`, and
`ISSUER_EXCHANGE_IDENTITY`.

## Phase 3C descriptive data-quality analysis

The batch registry was run through the existing Phase 3C descriptive analyzer
(`all-registered` and `partial-blocked` cohorts). Results are summarized in
[batch-01-phase3c-descriptive-summary.md](batch-01-phase3c-descriptive-summary.md).
Headline: 13 registered cases, 13 unique symbols, 0 boundaries, no confusion
matrix (no complete cases), and explicit limitations that the output is registry
data quality — *not* a performance estimate.

## Missingness summary

- Borrow/short-lending evidence: absent for all cases (provider feed down).
- Outcome evidence: absent for all cases (not acquired offline).
- Normalized Phase 3A evaluation evidence: absent for all cases (not
  reconstructed; would require fabrication).

No missing value was filled, defaulted, or converted to a `FAIL`.
