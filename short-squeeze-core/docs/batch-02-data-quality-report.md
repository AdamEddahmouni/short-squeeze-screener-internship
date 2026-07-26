# Outcome-Acquisition Batch 02 — Data Quality Report

## Artifact inventory

2 artifacts (inherited from batch 01, referenced not re-collected): 1
restricted-local raw scanner export (`REFERENCED_NOT_COPIED`, referenced by
SHA-256) and 1 sanitized derived rows artifact (hash re-validated against the
committed bytes). 0 hash failures, 0 missing, 0 duplicate. No raw
provider-embedded artifact is copied into the repository; no sensitive content is
included.

## Case-level completeness

| Domain | Status |
| --- | --- |
| Discovery provenance | Present (13/13) |
| Detection-time market snapshot | Present (13/13) |
| Detection boundary | Frozen (13/13), byte-identical to batch 01 |
| Issuer / exchange identity | Missing (13/13) — ticker-only, `PARTIALLY_RESOLVED` |
| Normalized point-in-time evidence | Missing (13/13) — not reconstructible without fabrication |
| Phase 3A request / result | Not constructed (13/13) |
| Retrospective outcome window | **Unavailable (13/13)** — no lawful non-authenticated source |
| Short-float / days-to-cover | Missing for SSPC, LMNX |
| IB borrow | Missing (13/13) |

## Missingness handling

All missing domains are recorded as missing; none are imputed, fabricated, or
substituted. The outcome window is marked unavailable with an explicit barrier
code rather than filled. The machine-readable metadata records
`outcome_window_captured = false` and `outcome_values_fabricated = false`, and the
outcome manifest records `current_values_used_as_historical = false` and
`fabricated_bars_used = false`.

## Determinism

Generator run twice → byte-identical, and identical to the 26 committed fixtures.
Acquisition CLIs (`validate-acquisition-plan`, `curate-historical-cases`,
`render-acquisition-report`, `audit-outcome-leakage`) run twice → byte-identical;
the CLI-rendered report matches the committed `curation-report.md`. No prior
Phase 1–3D or batch-01 fixture, anchor, or CLI output changed (additions only).
