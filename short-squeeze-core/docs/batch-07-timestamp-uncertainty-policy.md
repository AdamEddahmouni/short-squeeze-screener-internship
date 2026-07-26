# Batch 07 — Timestamp Uncertainty Policy

Batch 06 established that the IBKR bar timestamp is **epoch seconds in UTC** but did
**not** establish whether the epoch marks the interval **START** or **END**
(`timestamp_semantics = UNKNOWN`, official docs silent for intraday bars). Bar size is
**1 minute (60 s)**. Batch 07 reasons conservatively over *both* interpretations and
never chooses one. Source of truth:
`src/squeeze_core/acquisition/operation_readiness/timestamp_uncertainty.py`.

## Envelope

For a bar timestamp `t` and interval `d = 60 s` the true interval is exactly one of:

- interpretation **A** (`t` = START): `[t, t + d]`, completion (END) at `t + d`
- interpretation **B** (`t` = END): `[t − d, t]`, completion (END) at `t`

Possible completion instants: `{t, t + d}` (earliest `t`, latest `t + d`).
Possible start instants: `{t − d, t}` (earliest `t − d`, latest `t`).

## Predicates (exact `datetime`/`timedelta`, no float)

- **definitely completed at/before boundary `B`** ⟺ `t + d ≤ B`
  (the *latest* possible completion is at/before `B`, so completion holds either way).
- **definitely starts at/after `B`** ⟺ `t − d ≥ B`
  (the *earliest* possible start is at/after `B`).
- **straddles `B`** ⟺ neither of the above ⟹ `BLOCKED_ALIGNMENT`.

The original event timestamp is never mutated; the uncertainty is represented explicitly
as the completion envelope `[t, t + d]`.

## Edge behavior (unit-tested)

| `t` relative to boundary `B` | `t + d` vs `B` | definitely completed? | straddles? |
|------------------------------|----------------|-----------------------|------------|
| `B − 61 s` | `B − 1 s` ≤ B | **True** | False |
| `B − 60 s` | `B` (exact) | **True** | False |
| `B − 59 s` | `B + 1 s` > B | False | **True** |
| `B` | `B + 60 s` > B | False | **True** |

A bar completing exactly at `B` is treated as completed as-of the boundary (`≤`).

## Applied to the frozen cohort

All 13 detection-context artifacts share:
- observed last bar timestamp `t = 2026-07-17T23:59:00Z` (Friday),
- frozen boundary `B = 2026-07-18T13:37:55.017661Z` (Saturday).

`t + 60 s = 2026-07-18T00:00:00Z ≤ B`, so the final bar is **definitely completed before
the boundary under both interpretations**; no bar straddles the boundary. Therefore
`COMPLETED_BAR_AVAILABLE` and the temporal-alignment check are `ADMISSIBLE` for all 13
cases without choosing START or END.

The interval from the latest-possible final-bar completion (`2026-07-18T00:00:00Z`) to the
boundary is **49,075 seconds (~13 h 38 m)** — a weekend coverage gap. This is a temporal
coverage fact used only for alignment/readiness; it is never read as an outcome and never
triggers a forward-window read.
