# Phase 3D Identity Resolution

`phase_3d_identity_resolution_policy.v1` preserves source claims for symbol, issuer, exchange, security type, provider identifier, effective dates, corporate actions, symbol changes, reverse splits, mergers, delistings, and reuse risk. Contradictory claims remain present; one source never overwrites another.

States are `RESOLVED`, `PARTIALLY_RESOLVED`, `CONFLICTED`, and `UNRESOLVED`. A symbol string alone is insufficient where reuse is plausible. Corporate-action or reuse risk prevents full resolution until reviewed. Conflicted or unresolved identity blocks empirical publication but the attempted case remains in the ledger.
