# Outcome-Acquisition Batch 02 — Completion Report

## Repository state

| Field | Value |
| --- | --- |
| Path | `C:\Users\adame\Desktop\short-squeeze-project\short-squeeze-core` |
| Branch | `batch/phase-3d-outcome-acquisition-02` |
| Branched from (batch-01 HEAD) | `37ac03ab196057398f1f6c3463118633316f58f2` |
| Working tree | clean except pre-existing untracked `docs/phase-3c-complete-handoff.md` |
| Remotes | none |
| Push / merge / rebase | none performed |
| Tag `phase-1-rc1` | unchanged → commit `f903d4d144d3f7e9717b1ab8e684da406d7968fb` |

Commits on branch (from batch-01 HEAD):

```
docs: preregister outcome acquisition batch 02
feat: curate batch 02 source-barrier outputs
test: add batch 02 acquisition and phase 3c cases
docs: report batch 02 source barrier and results
chore: finalize outcome acquisition batch 02
```

## Verification

| Suite | Result |
| --- | --- |
| Baseline (batch-01 HEAD) | 1971 passed, 1 skipped, 0 failed (1972 total) |
| Final full suite | 1993 passed, 1 skipped, 0 failed (1994 total; +22) |
| tests/acquisition/test_batch02.py | 20 passed |
| tests/analysis/test_batch02_descriptive.py | 2 passed |

- Generator run twice → byte-identical; matches the 26 committed fixtures exactly.
- Acquisition CLIs (`validate-acquisition-plan`, `curate-historical-cases`,
  `render-acquisition-report`, `audit-outcome-leakage`) run twice → byte-identical;
  the CLI-rendered report matches the committed `curation-report.md`.
- No prior Phase 1–3D or batch-01 fixture, doc, anchor, or CLI output changed
  (verified `git diff --stat 37ac03a` over batch-01 paths is empty; additions only).

## What batch 02 attempted and found

Batch 02 preregistered an attempt to capture the **forward 24-hour outcome
window** (`phase_3b_outcome_label_policy.v1`: +25% / −25%, reference = first
eligible trade-bar close at/after the boundary) for the 13 registry-only cases
frozen by batch 01, freezing Phase 3A before any outcome access, to promote
eligible cases to complete Phase 3B dataset candidates.

**No public, lawful, non-authenticated source provides the required forward
intraday bars for these specific symbols.** Sources that carry the data require
authentication (API key / registration) — excluded by the non-authentication
rule — or prohibit automated access in their terms/robots rules (Stooq
`robots.txt` disallows all non-Google/Bing agents; the Yahoo Finance chart
endpoint is barred by Yahoo's Terms of Service) — excluded by the no-terms-
violation rule. The one clearly-permissive public source (SEC EDGAR) serves
filings, not trade bars. See [batch-02-source-barrier.md](batch-02-source-barrier.md)
and the committed `outcome-source-search.json`
(`NO_ACCEPTABLE_LAWFUL_NONAUTHENTICATED_SOURCE`, 13 candidate sources evaluated).

Per explicit user authorization, batch 02 was completed as an honest
**source-barrier batch**: no bar was fabricated, no current value was represented
as historical, no authentication was used, and no source restriction was bypassed.

## Preregistered plan

`phase-3d-outcome-acquisition-batch-02` (`phase_3d_outcome_acquisition_batch_02.v1`,
det. ID `1cb14787-f0b8-5b6a-88db-6f75ee01cbe5`), status `PREREGISTERED`,
`OUTCOME_BLINDED`. Forbidden substitutions include `CURRENT_FOR_HISTORICAL` and
`SYNTHETIC_FOR_HISTORICAL`. Cases, case IDs, source order, and detection
boundaries inherited unchanged from batch 01.

## Cases, boundaries, identity (unchanged from batch 01)

13 attempted, 13 unique identities, 0 duplicate discoveries. The
`boundary-freeze-manifest.json`, `identity-review.json`, `eligibility-review.json`,
`sufficiency-review.json`, and `registry-only-cases.json` are **byte-identical**
to the batch-01 committed fixtures — a direct proof that the cases and frozen
boundaries were not altered. Identity: 0 resolved, 13 partially resolved.
Boundaries: 13 frozen (`ORIGINAL_PLATFORM_SURFACED_TIMESTAMP`, `2026-07-18T13:37:55Z`),
all `frozen_before_outcome_access = True`.

## Evaluation and outcome

Phase 3A requests frozen: 0; results frozen: 0 (normalized point-in-time evidence
is not reconstructible without fabrication, so it is declined, exactly as batch
01). Outcome windows captured: 0. Outcome manifest
(`phase-3d-batch-02-outcome-unavailable`) is separate and empty with status
`UNAVAILABLE_NO_LAWFUL_PUBLIC_SOURCE`, `current_values_used_as_historical = false`,
`fabricated_bars_used = false`.

## Leakage audit

13 passed, 0 failed, 0 publication-blocked. Freeze-ordering enforced; the
fail-path is covered by a test that injects an outcome token and asserts the audit
blocks publication. Detail in [batch-02-leakage-audit-report.md](batch-02-leakage-audit-report.md).

## Publication

Phase 3B registry candidates 13 (`phase_3d_batch_02_registry.v1`, det. ID
`b5f89f9c-fa49-5e87-8933-92c672a4c608`); complete dataset candidates 0;
registry-only 13; excluded/partial/blocked 0. Each entry carries
`OUTCOME_WINDOW_NO_LAWFUL_PUBLIC_SOURCE`. Schema unchanged (`1.0.0`). Detail in
[batch-02-phase3b-publication-summary.md](batch-02-phase3b-publication-summary.md).

## Phase 3C descriptive results

13 registered, 13 unique symbols, 0 boundaries, 0 complete, 13 partial, confusion
matrix none, 0 synthetic; descriptive-only, no predictive validation. Detail in
[batch-02-phase3c-descriptive-summary.md](batch-02-phase3c-descriptive-summary.md).

## Outputs and hashes

26 committed canonical documents under `tests/fixtures/acquisition/batch02/`
(regenerable to `build/acquisition/batch-02/`). Batch ID
`b1e06e15-84b2-58a3-adf0-76730ba8ae28`. Byte-identical regeneration verified. No
sensitive data included; the raw provider artifact is referenced by hash, not
copied.

## Deviations

1. **Zero complete cases.** No lawful non-authenticated outcome source exists for
   these symbols; fabrication is prohibited. Explicitly authorized: zero promoted
   complete cases is not a blocker when outcome data cannot be obtained lawfully,
   reproducibly, and with preserved provenance.
2. **No new discovery or intake.** Batch 02 inherits the batch-01 cases unchanged;
   only the outcome-acquisition layer (plan, source search, empty outcome manifest,
   batch-02 registry, summary, report) is new.

## Remaining limitations

This batch does NOT include: outcome capture, predictive validation, threshold
optimization, rule weighting, composite scoring, candidate ranking,
recommendations, alerts, entry/exit logic, P&L, backtesting, portfolio
simulation, machine learning, live integrations, database persistence,
authentication, paper trading, or live trading.

## Batch decision

```text
Outcome-acquisition batch 02 completed as an honest source-barrier batch:
zero complete cases, every attempt retained, no fabrication, no ToS or
authentication boundary crossed.
```
