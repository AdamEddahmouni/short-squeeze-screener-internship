# Batch 05 — Completion Report

**Task:** Phase 3D IBKR Historical-Bar Collection and Offline Preflight Batch 05
**Status:** Complete. Phase 3E not started.
**Schema:** `1.0.0` (unchanged).

## Official API provisioning

- Downloaded `TWS API Install 1048.01.msi` (API 10.48, "Latest" Windows w/ Python API) from
  `https://interactivebrokers.github.io/downloads/`. No redirect; direct 200 from the
  official host.
  - SHA-256 `B7F519E015E545C7A43B764E32D224D9F77C56045179494436F82A7B3ACFEC26`, 23,388,160 bytes.
  - Authenticode: **Valid**, signer `CN="Interactive Brokers Group, Inc.", OU=TWS API`,
    issuer DigiCert Trusted G4.
- Installed to `C:\TWS API` via elevated `msiexec /qn` (one operator UAC approval).
- Official Python source `C:\TWS API\source\pythonclient`, **ibapi 10.48.1**.
- Referenced into the project venv by `.pth` (`.venv/Lib/site-packages/ibapi_official.pth`);
  no IBKR source copied into the repo.
- ibapi's declared runtime dependency `protobuf==5.29.5` installed into the venv with
  explicit operator authorization (its own `setup.py` pins it; local system only had an
  incompatible protobuf 7.x for Python 3.13). No unofficial API package; no `ib_insync`.

## Collection result

- Connection: `127.0.0.1:4001`, client ID `27185`, Gateway server version `223`
  (4002 probed first, not accepting TCP).
- **All 13 contracts resolved** (unique conId), outcome-blind.
- **All 26 historical requests** returned data (`HISTORICAL_REQUEST_SUCCESS`).
- **All 26 preflights `PREFLIGHT_REJECTED`** (`MISSING_ADJUSTMENT_SEMANTICS`) — the honest
  result of declaring IBKR TRADES adjustment/volume semantics `UNKNOWN`.
- Private hash verification run twice: 26 artifacts, 0 mismatches.

See `batch-05-ibkr-collection-summary.md` for the full sanitized per-symbol table and the
critical **Limitations** (weekend boundary; IBKR returned the same pre-boundary Friday
session for both requests; the `FROZEN_FORWARD_24H` artifacts are not forward-outcome data).

## Boundaries honored

- No orders; no account/position/balance/margin/execution/P&L/portfolio requests.
- `managedAccounts` identifiers never stored or logged; no account IDs in any output.
- No case association, no outcome computation, no reference price/return/±25%/labels.
- No Phase 3A/3B/3C records; **Phase 3E not started**.
- No licensed market data committed; all provider data under Git-ignored
  `intake/local-bars/ibkr-batch-05/`.
- Batch 01–04 fixtures, committed acquisition source, and archived evidence unchanged.

## Deliverables

- Preregistered plan: `docs/batch-05-ibkr-historical-bar-collection-plan.md`
- Exporter: `tools/ibkr_historical_export/` (read-only, isolated from the runtime)
- Tests: `tests/tools/ibkr_historical_export/` (71 synthetic tests)
- Docs: architecture, connection/safety boundary, request contract, sanitized collection
  summary, test/verification report, this completion report, and the Batch 06 handoff.

## Definition of done

All Definition-of-Done items in the handoff are satisfied: checkpoint and baseline verified;
plan preregistered and committed before Gateway access; isolated read-only localhost-only
exporter with no forbidden API method; official `ibapi` used; all 13 symbols attempted in
frozen order; transparent outcome-blind resolution; both frozen requests attempted per
resolved contract; all data and diagnostics preserved privately; exact hashes/byte lengths
verified; every nonempty CSV honestly preflighted; missing/ambiguous/unavailable handled
explicitly; no licensed data committed; no account data requested or stored; no case
association or outcome; dedicated and full tests pass; prior and archived artifacts
unchanged; completion report and real Batch 06 handoff present; Phase 3E unstarted.
