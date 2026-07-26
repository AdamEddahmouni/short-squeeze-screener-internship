# Adjustment-Semantics Guide

Adjustment meaning cannot be inferred from the numbers, so you must declare it.

- `price_adjustment_semantics` — one of: RAW_UNADJUSTED, SPLIT_ADJUSTED, SPLIT_AND_DIVIDEND_ADJUSTED, UNKNOWN.
  `RAW_UNADJUSTED` (raw prices), `SPLIT_ADJUSTED`, `SPLIT_AND_DIVIDEND_ADJUSTED`
  (fully adjusted), or `UNKNOWN` (which blocks the bundle).
- `volume_adjustment_semantics` — one of: RAW_UNADJUSTED, SPLIT_ADJUSTED, UNKNOWN.
- `corporate_action_handling` — one of: RAW_NO_ADJUSTMENT, ADJUSTMENTS_APPLIED, UNKNOWN.

Rules the workflow enforces:

- Price and volume adjustment are declared **separately**; they can differ.
- If any of the three is `UNKNOWN`, the bundle is blocked — adjustment is never
  guessed from price magnitudes.
- Price adjustment and corporate-action handling must be consistent (for example,
  an adjusted price with raw corporate-action handling is contradictory and
  blocks the bundle).
- `data_time_basis` — one of: HISTORICAL, CURRENT, UNKNOWN. Current values cannot be
  ingested as historical; only declare `HISTORICAL` when the export truly is.
- `value_authenticity` — one of: VENDOR_SUPPLIED, SYNTHETIC_FIXTURE; `intended_use` —
  one of: HISTORICAL_EVIDENCE, INFRASTRUCTURE_FIXTURE. Synthetic values declared as historical evidence
  are blocked. Synthetic data cannot represent historical evidence.
