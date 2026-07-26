# Batch 16 Fresh-Session Handoff

## Starting point

Begin from the final Batch 15 branch
`batch/professional-source-handoff-15`. Verify the exact current HEAD, clean
tracked worktree, release checksum, privacy audit, and authoritative JUnit totals
before changing source.
The former untracked Phase 3C handoff is preserved in a private archive outside
the repository and must not be reintroduced.

## Preserved boundaries

- Do not modify or expose the local private provider file.
- Do not change frozen totals, canonical registries, or archived repositories.
- Do not substitute current provider values for historical evidence.
- Do not add trading, order, position, or account access.
- Do not perform predictive validation, backtesting, P&L analysis, or threshold
  optimization.
- Phase 3E remains not started.

## Known state

- Release `0.15.0` builds from an allowlist and passes privacy audit.
- Extracted frozen-mode HTTP acceptance passes.
- The full offline suite has 2,623 tests: 2,622 passed and 1 skipped.
- Local providers are configured and the local IBKR socket is reachable.
- Railway CLI authentication is not available in the completed session.
- The allowlisted release is clean, but the tracked repository still contains
  redacted audit findings in legacy internal records and deliberate negative
  scanner/compatibility tests.

## Exactly one recommended next task

Classify and sanitize or externally archive the remaining tracked-source audit
findings without changing frozen artifacts, canonical registries, compatibility
machine IDs, or the already-clean release boundary.
