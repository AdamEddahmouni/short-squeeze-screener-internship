# Batch 06 — IBKR Historical-Bar Semantics Resolution and Offline Re-Preflight — Preregistration Plan

Status: preregistered before any semantic-declaration or code change.

Branch: `batch/phase-3d-ibkr-semantics-resolution-06`
Parent HEAD: `fe7ba9d0ecfdaaaf84edfef413fa3fecbd2ccf0b` (Batch 05).
Schema: remains `1.0.0`. Intake contract: remains `phase_3d_local_bar_intake_contract.v1`.

This batch resolves the IBKR historical `TRADES` bar metadata semantics that Batch 05
honestly declared `UNKNOWN`, using **official Interactive Brokers documentation** plus the
**installed official `ibapi` contract**, and re-runs the **existing** Batch 04 offline
preflight against the **already-collected** 13 `DETECTION_CONTEXT_PRECEDING_24H` CSV
artifacts. No new historical bars are requested. This is Phase 3D only; Phase 3E is not begun.

---

## 1. Evidence hierarchy (frozen)

Evidence is classified into four disjoint, never-blurred classes:

1. **Official IBKR documented fact** — a statement in official IBKR documentation
   (`interactivebrokers.github.io/tws-api/*`, `ibkrcampus.com`) or the installed official
   `ibapi` source (`C:\TWS API\source\pythonclient\ibapi\client.py`).
2. **Local Batch 05 observation** — a fact recorded in the private Batch 05 artifacts
   (request manifest, probe result, coverage).
3. **Local Gateway configuration observation** — a read-only fact from `C:\Jts\...` config.
4. **Project inference** — a conclusion the project draws from the above. Inference is never
   presented as an official fact and never used to force a preflight verdict.

Precedence for a given field: official documented fact > installed API contract > local
observation. Absence of an official fact means the field remains `UNKNOWN`; inference does
not fill it.

## 2. Official documentation sources (frozen)

- `https://interactivebrokers.github.io/tws-api/historical_bars.html` — TRADES split/dividend
  adjustment; whatToShow; useRTH.
- `https://interactivebrokers.github.io/tws-api/historical_data.html` — historical trade
  filtering vs unfiltered volume.
- `https://interactivebrokers.github.io/tws-api/market_data.html` — US-stock size in lots vs
  shares, TWS 985 migration, compatibility setting.
- Installed official `ibapi` `client.py` `reqHistoricalData` docstring — formatDate=2 = epoch
  seconds GMT; useRTH values.

Every conclusion cites an exact source in `docs/batch-06-official-ibkr-semantics-evidence.md`.

## 3. Fields to resolve, and expected disposition

| Field | Disposition | Basis |
|---|---|---|
| `price_adjustment_semantics` | `SPLIT_ADJUSTED` | official: "TRADES data is adjusted for splits, but not dividends" |
| `corporate_action_handling` | `ADJUSTMENTS_APPLIED` | official: splits are applied |
| `volume_adjustment_semantics` | `UNKNOWN` (remains) | official docs silent on volume corporate-action; inference forbidden |
| `timestamp` representation / `event_timezone` | epoch seconds → `UTC` | installed ibapi: formatDate=2 = "seconds since 1/1/1970 GMT" |
| `timestamp_semantics` (bar start/end) | `UNKNOWN` (remains) | official docs give only the daily-bar close-date rule; intraday start/end absent |
| `session_coverage` (requested) | `EXTENDED` | ibapi useRTH=0 = all data incl. outside RTH |
| historical-feed filtering | disclosure only | official: filtered for trades away from NBBO; unfiltered volume generally larger |
| volume unit (shares vs round lots) | `HISTORICAL_VOLUME_UNIT_UNRESOLVED` | not a manifest field; see §6 |

## 4. Fields that may remain UNKNOWN

`volume_adjustment_semantics` and `timestamp_semantics` (bar start/end) remain `UNKNOWN`
when official evidence is silent. This is expected and preserved honestly. Because the
Batch 03 normalizer treats an `UNKNOWN` adjustment field as fatal
`MISSING_ADJUSTMENT_SEMANTICS` and a non-{START,END} timestamp as `MISSING_TIMESTAMP_SEMANTICS`,
the honest re-preflight result for all 13 detection-context artifacts is expected to be
`PREFLIGHT_REJECTED` — reduced from Batch 05's three `UNKNOWN` adjustment fields to one
adjustment field plus timestamp. A rejected preflight is a valid honest outcome, not a failure.

## 5. Price-adjustment resolution policy

`whatToShow=TRADES` with official split-adjusted/not-dividend-adjusted → the existing
`PriceAdjustmentSemantics.SPLIT_ADJUSTED` (no new enum value; schema unchanged). `TRADES`
must never map to `RAW_UNADJUSTED` (splits are applied) nor to `SPLIT_AND_DIVIDEND_ADJUSTED`
(dividends are not). If official docs ever contradicted representability, stop with
`PRICE_ADJUSTMENT_SEMANTIC_NOT_REPRESENTABLE`; they do not here.

## 6. Volume-unit resolution policy (evidence hierarchy §9 of handoff)

The volume UNIT (shares vs round lots) is a scaling concern distinct from corporate-action
adjustment, and the `IntakeManifest` has **no** volume-unit field, so it never gates preflight.
- Level 1 (Batch 05 capture): not captured — request manifest and probe hold no lots setting.
- Level 2 (read-only local config): the setting lives only in IB Gateway's obfuscated binary
  `ibg.*.xml`; `jts.ini` has no such key. Not recoverable as plaintext without decoding an
  obfuscated file → not a safe/unambiguous establishment.
- Level 3 (live Gateway UI): declined — invasive on the live authenticated Gateway and does
  not affect any preflight verdict.
- Level 4: record `HISTORICAL_VOLUME_UNIT_UNRESOLVED`. Never inferred from bar values or build
  number.

## 7. Volume corporate-action policy

Resolved only if officially documented. Official docs establish split adjustment for TRADES
**price** but say nothing isolating **volume**. Per handoff, do not assume volume adjustment
from price adjustment → `VolumeAdjustmentSemantics.UNKNOWN`.

## 8. Timestamp resolution policy

Representation and timezone are resolved from the installed ibapi contract (formatDate=2 =
epoch seconds GMT → UTC). Bar start/end semantics are **not** officially documented for
intraday bars (only daily bars, which our contract treats as SESSION_BASED/unsupported), so
`timestamp_semantics` remains `UNKNOWN`. Start/end is never inferred from spacing.

## 9. Session-coverage interpretation

`useRTH=0` establishes only the **requested** session policy (extended-hours eligible), kept
separate from **observed** coverage and from provider filtering. No claim that every
extended-hours trade is present or that a complete 24h session is contained.

## 10. Filtered-feed disclosure

Recorded as a provenance/limitation statement (not a rejection): IBKR historical trade data
is provider-filtered (trades away from NBBO excluded) and may have lower volume than an
unfiltered feed. IBKR historical TRADES volume is never described as complete consolidated
volume.

## 11. Manifest-update policy / raw-byte immutability

Raw CSV and JSONL bytes are never modified. New **versioned private overlays** are written
under `intake/local-bars/ibkr-batch-05/semantics/batch-06/` (Git-ignored). Batch 05 originals
are preserved unchanged. Each overlay links back to the original artifact SHA-256, byte length,
Batch 05 request id/class, official evidence, and local config evidence.

## 12. Re-preflight cohort

Exactly the 13 `DETECTION_CONTEXT_PRECEDING_24H` CSVs (XNCR, PESI, SLS, ZNTL, GPRE, SSPC,
LBGJ, TRVI, LMNX, MGNX, BHVN, OBE, AVTX). The 13 `FROZEN_FORWARD_24H` CSVs are **excluded**
from forward-outcome use; their status remains "request succeeded but returned coverage does
not represent the frozen forward window". They are not re-preflighted as forward evidence.

## 13. Hard rules

No new API/historical request; no Gateway market-data connection; no window shift/extend/
replace; no Monday substitute; no account/credential access; no case association; no outcome/
returns/thresholds; no Phase 3A/3B/3C expansion; no Phase 3E; schema stays 1.0.0; validators
unchanged to obtain READY.

## 14. Implementation surface

- `src/squeeze_core/acquisition/ibkr_semantics/` — pure deterministic resolver + frozen
  official-evidence constants. No network, Gateway, account, or OHLCV access.
- `tools/ibkr_historical_export/` (or a sibling tool module) — private-overlay generator that
  reads Batch 05 manifests, builds resolved `IntakeManifest`s, runs the existing offline
  preflight on the exact raw bytes, and writes private overlays. Web research and local config
  inspection are evidence tooling, kept out of the pure resolver.

## 15. Tests (synthetic fixtures only)

Resolver: TRADES→SPLIT_ADJUSTED; never RAW_UNADJUSTED; never DIVIDEND/FULLY adjusted;
volume documented-checked/unchecked→unit; volume unknown→UNKNOWN; no inference from numeric
volume or OHLCV; filtered-feed disclosure preserved; formatDate=2→epoch/UTC; useRTH=0→request
policy; unknown bar start/end stays UNKNOWN. Integrity: raw Batch 05 bytes unchanged; all 13
detection-context hashes unchanged; forward artifacts never promoted; no Gateway historical
API calls; no order/account methods; no case association; no outcomes; Batch 01–05 committed
artifacts unchanged; deterministic outputs (generate twice, compare bytes); re-preflight
behavior; full suite passes.

## 16. Expected statuses

Per-artifact re-preflight: `PREFLIGHT_REJECTED` for all 13, with reason codes
`MISSING_ADJUSTMENT_SEMANTICS` (volume) and `MISSING_TIMESTAMP_SEMANTICS`. Preserved honestly.

## 17. Stop conditions

The handoff §25 stop conditions. A rejected preflight is not a stop condition. Volume-unit
unresolved and volume corporate-action unknown are recorded honestly and do not, by themselves,
halt the batch, because the manifest cannot represent them any other way and the batch's job is
to record the honest state — not to force acceptance.

## 18. Completion criteria

Handoff §27: checkpoint verified; baseline reproduced; private bytes verified; plan
preregistered; official evidence cited; price semantics resolved; volume-unit + volume
corporate-action + intraday timestamp honestly recorded; timestamp representation/session/
filtering documented; raw bytes unchanged; overlays versioned separately; 13 detection-context
artifacts re-preflighted; forward artifacts excluded; no new fetch/case/outcome; tests pass;
prior committed + archived artifacts unchanged; reports + Batch 07 handoff written; final HEAD
reported; Phase 3E unstarted; stop.
