# Batch 01 — Preregistered Acquisition Plan

**Plan ID:** `phase-3d-historical-source-batch-01`
**Plan version:** `phase_3d_historical_source_batch_01.v1`
**Deterministic ID:** `b46ad576-b729-5572-b2e9-cf0a164820dc`
**Status:** `PREREGISTERED` (lifecycle: `DRAFT → PREREGISTERED → ACTIVE → CLOSED`)
**Outcome-blinding state:** `OUTCOME_BLINDED`
**Created from policy:** `phase_3d_acquisition_plan_policy.v1`

This plan is frozen and committed **before any retrospective outcome data is
accessed**. In fact this batch accesses no outcome data at all (see the outcome
section below), so outcome-blindness holds trivially and by construction.

## Research question

Can independent real symbols surfaced by an archived point-in-time market
scanner be curated point in time through the Phase 3D pipeline while preserving
provenance and outcome-blindness?

The batch objective is **defensible, auditable historical-source curation of
independent real symbols**, not a favorable performance result.

## Population, period, and universe

| Field | Value |
| --- | --- |
| Target population | US-listed equities surfaced by the archived original-platform market scanner on the frozen scan date |
| Fixed date range | `2026-07-18` → `2026-07-18` (single scan day) |
| Market-session scope | `REGULAR` (scan captured 13:37:55Z ≈ 09:37 ET) |
| Symbol universe | Distinct US-listed equity tickers present in the frozen archived scanner snapshot `screener_snapshot.json` captured `2026-07-18T13:37:55Z` |

### Period deviation from the preferred 2024 window

The handoff prefers `2024-01-01 … 2024-12-31`. No systematic 2024 scanner export
exists in the archived evidence; the only archived original-platform systematic
scanner output is the single July-2026 snapshot (the archived BIYA acquisition is
also 2026-dated). Per handoff §11 a different fixed period is permitted when the
available systematic discovery source cannot support 2024. The 2026-07-18 period
was chosen **from the availability of the discovery artifact, not from any
knowledge of later outcomes**, and is frozen here before outcome review.

## Discovery

| Field | Value |
| --- | --- |
| Discovery source class | `ARCHIVED_MARKET_SCANNER` |
| Discovery source | `screener_snapshot.json` (archived original-platform scanner export) |
| Discovery query / filter | Archived scanner surface (detection-time relative-volume / percent-change / short-float criteria) |
| Sampling method | `SOURCE_ORDER_THEN_UNIQUE_SECURITY_IDENTITY_SCORE_BLIND` |
| Source ordering | Natural snapshot row order (never re-ordered by the platform's score/tier) |
| Maximum attempt count | 30 |
| Minimum target count | 0 (attempts are never forced) |

## Policies (reused from completed Phase 3D)

| Policy | Version |
| --- | --- |
| Deduplication | `phase_3d_unique_security_deduplication_policy.v1` |
| Detection boundary | `phase_3d_detection_boundary_policy.v1` |
| Inclusion | `phase_3d_historical_inclusion_policy.v1` |
| Exclusion | `phase_3d_historical_exclusion_policy.v1` |
| Provider priority | `phase_3d_provider_priority_policy.v1` |

## Identity, dedup, boundary

- **Identity policy:** resolve each ticker; issuer/exchange/security-type are not
  present in the scanner row, so identities resolve `PARTIALLY_RESOLVED`.
- **Deduplication:** unit `UNIQUE_SECURITY_IDENTITY`; the snapshot contains 13
  distinct tickers with no duplicates, so no duplicate groups arise.
- **Detection-boundary policy:** freeze at
  `ORIGINAL_PLATFORM_SURFACED_TIMESTAMP` (the objective scanner-surfaced
  timestamp), which is outcome-blind. Outcome-aware rules such as
  `MAXIMUM_LATER_RETURN` are forbidden.

## Required artifacts / substitutions

| Field | Value |
| --- | --- |
| Required artifacts | `DISCOVERY`, `IDENTITY`, `MARKET` |
| Allowed substitutions | none |
| Forbidden substitutions | `CURRENT_FOR_HISTORICAL`, `SYNTHETIC_FOR_HISTORICAL` |

## Treatment rules

- **Duplicate symbols:** retain all records, select one primary by the
  preregistered outcome-blind rule, mark secondaries dependent. (None occur.)
- **Missing short-pressure evidence:** retained as missing/`UNKNOWN`; never
  fabricated and never converted to a `FAIL`.
- **Inaccessible provider data:** the raw provider-embedded scanner export is
  referenced by hash and not copied; no live provider access is performed.

## Outcome handling (this batch)

This batch performs **no retrospective outcome capture**. Forward trade-bar
windows for these symbols are not available offline, and fabricating them is
prohibited. All cases are therefore curated as **registry-only** Phase 3B
candidates. The outcome manifest is intentionally empty and kept separate from
discovery, eligibility, and boundary inputs. See
[batch-01-curation-report.md](batch-01-curation-report.md).
