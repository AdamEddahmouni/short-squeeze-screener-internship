# Historical Source Collection Batch 01 — Completion Report

## Repository state

| Field | Value |
| --- | --- |
| Path | `C:\Users\adame\Desktop\short-squeeze-project\short-squeeze-core` |
| Branch | `batch/phase-3d-historical-source-collection-01` |
| Starting HEAD (Phase 3D) | `a92906d395e17ee8dff15c69395f0b37427bc66a` |
| Merge base with Phase 3C | `14d35abfc9aacc6f2f4adaa3ad264950ec556d17` (unchanged) |
| Working tree | clean except pre-existing untracked `docs/phase-3c-complete-handoff.md` |
| Remotes | none |
| Push / merge / rebase | none performed |
| Tag `phase-1-rc1` | unchanged → `f903d4d144d3f7e9717b1ab8e684da406d7968fb` |
| Commits on branch | 6 (see below) |

Commits (from Phase 3D HEAD):

```
docs: preregister historical source collection batch 01
feat: import batch 01 archived scanner discovery
fix: write batch 01 intake as LF for cross-platform determinism
feat: curate and publish batch 01 registry candidates
test: add batch 01 acquisition and phase 3c cases
docs: report batch 01 curation results and limitations
chore: finalize historical source collection batch 01
```

## Verification

| Suite | Result |
| --- | --- |
| Baseline (before batch) | 1949 passed, 1 skipped, 0 failed |
| Final full suite | 1971 passed, 1 skipped, 0 failed (1972 total; +22) |
| tests/acquisition | 73 passed |
| tests/analysis | 122 passed |
| tests/research | 65 passed |
| tests/evaluation | 50 passed |
| tests/validation | 367 passed |
| tests/readiness | 124 passed |
| tests/metrics | 453 passed |
| tests/compatibility | 133 passed |

- Batch generator run twice → byte-identical; matches committed fixtures exactly.
- Acquisition CLIs (`validate-acquisition-plan`, `curate-historical-cases`,
  `render-acquisition-report`) run twice → byte-identical; CLI-produced ledger
  matches the committed ledger.
- Phase 3C analyzer run twice → byte-identical.
- Prior Phase 1–3D fixtures/anchors: no committed file modified (additions only);
  the Phase 3D fixture-regeneration test passes unchanged.

## Acquisition plan

`phase-3d-historical-source-batch-01` (`phase_3d_historical_source_batch_01.v1`,
det. ID `b46ad576-b729-5572-b2e9-cf0a164820dc`), status `PREREGISTERED`,
`OUTCOME_BLINDED`. Date range `2026-07-18…2026-07-18`; population = US-listed
equities surfaced by the archived scanner; universe = 13 distinct tickers in
`screener_snapshot.json`. Sampling `SOURCE_ORDER_THEN_UNIQUE_SECURITY_IDENTITY_
SCORE_BLIND`; attempt target ≤30, minimum 0. Policies reuse the completed Phase
3D inclusion/exclusion/boundary/dedup/leakage versions. Outcome-blind confirmed:
no outcome data was accessed at any point. Full detail in
[batch-01-acquisition-plan.md](batch-01-acquisition-plan.md).

## Source collection

One archived original-platform scanner snapshot (`ARCHIVED_MARKET_SCANNER`), raw
SHA-256 `4e5fbec4…f667d598` (20104 bytes), captured `2026-07-18T13:37:55Z`. One
provider provenance record. Raw artifact is restricted-local (referenced by hash,
not copied); the committed sanitized rows are a derived normalized artifact.
Retrieval/capture time preserved separately from event time. Known biases:
scanner gapper/high-activity selection, single-snapshot, borrow-feed-down.
Score/tier/target predictions dropped and never used for selection. Detail in
[batch-01-source-strategy.md](batch-01-source-strategy.md).

## Artifact inventory

2 artifacts, 2 hash-valid, 0 hash-failed, 0 missing, 0 duplicate, 1
restricted-local (referenced), 1 sanitized-derived (committed), 0 unsupported;
both `HISTORICAL`. No raw provider-embedded artifact copied into the repository.

## Case ledger

13 attempted, 13 unique identities, 0 duplicate discoveries, 0 included
(complete-dataset track), 13 registry-only, 0 complete dataset candidates, 0
excluded, 0 partial, 0 blocked, 0 dependent secondary boundaries. Exclusion-code
counts: `CASE_REQUIRES_FABRICATED_EVIDENCE` × 13 (declining to fabricate an
offline Phase 3A request; retained as registry-only). Every attempt retained.

## Identity and boundary review

Identity: 0 resolved, 13 partially resolved, 0 conflicted, 0 unresolved; 0
corporate-action issues; 0 symbol-reuse issues. Boundaries: 13 frozen (rule
`ORIGINAL_PLATFORM_SURFACED_TIMESTAMP`), 0 missing, 0 ambiguous, 0 manual
reconstructions; all `frozen_before_outcome_access = True`.

## Evaluation freeze

Phase 3A requests frozen: 0. Phase 3A results frozen: 0. (Registry-only; a full
request is not constructible offline without fabrication.) Missing evidence
domains: normalized point-in-time evidence, retrospective outcome window,
issuer/exchange identity (all cases); short-float and days-to-cover (SSPC, LMNX);
IB borrow (all cases). Phase 3A policies unchanged.

## Outcome capture

Complete windows 0, partial 0, unknown 13 (not captured), upward crossings 0,
downward crossings 0, mixed 0, no-substantial-move 0. Outcome manifest
(`phase-3d-batch-01-outcome-not-captured`) is separate and empty.

## Leakage audit

13 passed, 0 failed, 0 publication-blocked. No diagnostics beyond
`LEAKAGE_AUDIT_PASSED`. Freeze-ordering enforcement confirmed (plan → boundary →
evaluation-request → evaluation-result → outcome-sentinel). Fail-path covered by
test. Detail in [batch-01-leakage-audit-report.md](batch-01-leakage-audit-report.md).

## Publication

Phase 3B registry candidates 13 (`phase_3d_batch_01_registry.v1`, det. ID
`15241fb5-d53d-57a2-9d79-5bec6d2519d5`); complete dataset candidates 0;
registry-only 13; excluded 0; partial 0; blocked 0. Phase 3B schema unchanged
(`1.0.0`). Detail in
[batch-01-phase3b-publication-summary.md](batch-01-phase3b-publication-summary.md).

## Phase 3C descriptive results

Historical case-boundary count 0 (registry-only). Unique-symbol count 13.
Synthetic exclusion confirmed (0 synthetic). Dependence: none (all unique).
Sample-size assessment: descriptive only; predictive/causal/statistical
validation forbidden. Confusion-matrix counts: none (no complete cases). Defined
rates: none; undefined: detection/outcome/rule prevalence (no complete cases).
Missingness: all registry-only. **No predictive validation is claimed.** Detail
in [batch-01-phase3c-descriptive-summary.md](batch-01-phase3c-descriptive-summary.md).

## Outputs and hashes (committed canonical copies)

Under `tests/fixtures/acquisition/batch01/` (25 files); regenerable to
`build/acquisition/batch-01/`. Key IDs: batch `741672c2-23cb-5370-a49f-616a6a621b0e`;
sanitized rows SHA-256 `87364d5eb4a2ecc722375f7db6c3fa2c58d9472265f5de3b297864a519fc059a`.
Byte-identical regeneration verified. No sensitive data included.

## Compatibility

Schema version `1.0.0`. All Phase 1–3D anchors unchanged (additions only). No
prior fixture or CLI output impacted. Full prior suite passes.

## Environment notes (recorded, not modified)

- Inert workspace-root `.git`: untouched.
- `.pytest_cache` permission warning: present, non-blocking (`-p no:cacheprovider`
  used for clean runs).
- Verification basetemp directories (`.pytest-run-*`): present, gitignored.
- Archived parent `0897562e…` / submodule `6dbefd1a…`: unchanged, read-only.
- Pre-existing untracked `docs/phase-3c-complete-handoff.md`: left untouched.

## Deviations

1. **Period 2026-07-18 instead of the preferred 2024.** No 2024 systematic
   scanner export exists in the archived evidence; the deviation was chosen from
   discovery-artifact availability, not from outcomes, and frozen before any
   outcome access (handoff §11).
2. **Registry-only, offline.** No live network fetching was performed. Forward
   outcome windows and normalized Phase 3A evidence are unavailable offline;
   fabricating them is prohibited, so all cases are registry-only. Explicitly
   permitted by handoff §9 and §34.
3. **Fewer than 20 cases (13).** The single clean snapshot yielded 13 defensible
   attempts; forcing 20 is prohibited (handoff §9).

## Remaining limitations

This batch does NOT include: predictive validation, threshold optimization, rule
weighting, composite scoring, candidate ranking, recommendations, alerts,
entry/exit logic, P&L, backtesting, portfolio simulation, machine learning,
permanent live integrations, database persistence, authentication, paper trading,
or live trading.

## Batch decision

```text
Historical source collection batch 01 approved.
```

## Recommended next task

Run one **outcome-acquisition batch** that fetches the frozen 24-hour forward
trade-bar windows for these 13 registry-only symbols from a public, lawful,
non-authenticated historical source (retrieval time recorded separately from
event time), through a separate collection utility, then re-curates them to
promote eligible cases toward complete Phase 3B dataset candidates. Do not begin
it automatically.
