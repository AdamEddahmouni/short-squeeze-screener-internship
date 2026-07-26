# Phase 3C Cohort Policy

Phase 3C constructs cohorts only from an explicitly supplied Phase 3B dataset or registry. It never scans paths or infers evidence. Historical completed, synthetic, all-registered, partial/blocked, and mixed-provenance cohorts are distinct.

The primary historical view is `UNIQUE_SYMBOL_POLICY_SELECTED_BOUNDARY`: one concrete row per symbol selected by the versioned outcome-blind boundary policy. `UNIQUE_SYMBOL` is aggregate-only. Case-boundary views remain available and disclose dependent observations. Every exclusion retains its case ID, symbol, fixture classification, reason code, and required evidence.

Synthetic rows never enter historical rates or intervals. Registry reports preserve incomplete `KLRS`, `LBGJ`, `SG`, `TRVI`, and `SLS`, plus conflicted `KLOS`, without fabricating inputs.
