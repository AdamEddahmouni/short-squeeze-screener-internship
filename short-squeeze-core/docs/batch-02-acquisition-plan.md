# Outcome-Acquisition Batch 02 — Preregistered Plan

`phase-3d-outcome-acquisition-batch-02`
(`phase_3d_outcome_acquisition_batch_02.v1`)

## Purpose

Batch 01 produced 13 outcome-blind, registry-only Phase 3B candidates with frozen
detection boundaries but no captured forward outcomes. This batch is the
preregistered attempt to capture the **forward 24-hour outcome window** for those
already-frozen boundaries — freezing a Phase 3A request and result **before** any
outcome access — so that eligible cases could be promoted to complete Phase 3B
dataset candidates.

This plan is frozen **before** any outcome data is accessed. It is not Phase 3E
and claims no predictive, scoring, ranking, recommendation, alerting,
backtesting, P&L, or trading behaviour.

## Cases (unchanged from Batch 01)

The universe is exactly the 13 distinct US-listed equity tickers already frozen
as Batch 01 registry cases, with their case IDs, source order, and detection
boundaries preserved unchanged:

```
AVTX BHVN GPRE LBGJ LMNX MGNX OBE PESI SLS SSPC TRVI XNCR ZNTL
```

Every detection boundary remains `ORIGINAL_PLATFORM_SURFACED_TIMESTAMP` at
`2026-07-18T13:37:55Z`. Discovery, eligibility inputs, and boundaries are **not**
re-derived from outcomes and remain outcome-blind.

## Outcome policy (preregistered, unchanged)

`phase_3b_outcome_label_policy.v1`

| Parameter | Value |
| --- | --- |
| Horizon | 24 hours after the frozen detection boundary |
| Upward threshold | +25% |
| Downward threshold | −25% |
| Reference | first eligible trade-bar close at/after the boundary |

## Ordering invariant (non-negotiable)

For any case to reach outcome capture, the following must already be frozen, in
order, **before** any outcome field is read:

1. acquisition plan (this document),
2. detection boundary (inherited from Batch 01, frozen),
3. Phase 3A request (hashed + frozen),
4. Phase 3A result (hashed + frozen),
5. **then** retrospective outcome capture into a *separate* outcome manifest.

The existing Phase 3D leakage audit enforces this ordering and is not weakened.

## Source policy

Forward market bars may be obtained **only** from a public, lawful,
**non-authenticated** historical source, without bypassing paywalls,
authentication, rate limits, anti-bot protections, or a source's terms/robots
rules. Retrieval time is recorded separately from event time. Current values are
never represented as historical values (`CURRENT_FOR_HISTORICAL` and
`SYNTHETIC_FOR_HISTORICAL` are forbidden substitutions). Where a lawful source is
unavailable, the affected case is retained honestly (registry-only / partial /
blocked) — never fabricated.

## Outcome of the source search

See [batch-02-source-barrier.md](batch-02-source-barrier.md) and the committed
`outcome-source-search.json`. No public, non-authenticated, terms-permitting
source was found that provides the required forward 24-hour bars for these 13
symbols. Consequently **zero** complete dataset candidates were promoted; all 13
cases remain registry-only with an explicit source-barrier limitation, and the
outcome manifest is empty with status `UNAVAILABLE_NO_LAWFUL_PUBLIC_SOURCE`. This
is an authorized, honest result: zero promoted complete cases is not a blocker
when historical outcome data cannot be obtained lawfully, reproducibly, and with
preserved provenance.
