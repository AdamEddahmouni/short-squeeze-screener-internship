# Phase 2V Outcome-Data Limitations

- The outcome bars are a later public historical acquisition, not evidence available to
  the original candidate decision.
- The one-minute source returned 3,295 rows; 2,838 normalized and 457 were rejected with
  diagnostics. Several longer windows are therefore marked `PARTIAL`.
- Provider-recorded prices use a consistent adjusted policy. BIYA's 1:10 reverse split
  became effective on July 13, before the July 16–21 outcome range; the action is
  preserved explicitly so pre-split and post-split prices are not silently mixed.
- No authoritative halt history was acquired. Bar gaps are not reclassified as halts.
- No eligible published short-interest record was acquired, so no historical
  days-to-cover metric is produced.
- FINRA daily short-sale volume is venue-scoped transaction volume and is not a position
  measure. It is never substituted for published short interest.
- Historical borrow fee and availability were unavailable through already-configured
  local sources. Current values were not backfilled into history.
- News retains publication time separately from retrieval time. Later news never enters
  the original detection replay.
- A maximum price is an observed high, not a simulated exit. A reference close is a
  comparison basis, not an entry or assumed fill.
- One historical case cannot validate a generalized methodology or establish causation.

