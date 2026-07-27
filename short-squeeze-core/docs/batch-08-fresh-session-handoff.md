# Claude Fresh-Session Handoff — Batch 08 Operation-Specific Phase 3A Request/Result Freeze

## Purpose

Continue the short-squeeze research reconstruction from the completed Batch 07 checkpoint.

Your only authorized next task is:

**Construct and freeze Phase 3A requests and results for the 13 frozen Batch 01 cases
using ONLY the operation-specifically-admissible Batch 05 detection-context evidence
established by Batch 07 — the two market-bar availability rules (`MARKET_DATA_AVAILABLE`,
`COMPLETED_BAR_AVAILABLE`) and the split-invariant `PERCENTAGE_CHANGE_MINIMUM` rule —
letting every rule that Batch 07 marked BLOCKED or NOT_APPLICABLE resolve to
`INSUFFICIENT_DATA`/`UNKNOWN` under the existing Phase 3A contract.**

This is the sanctioned "requests are constructible" continuation from Batch 07 §17: Batch
07 established that a non-fabricated, schema-valid `RuleEvaluationRequest` skeleton is
constructible for all 13 cases (`PHASE3A_REQUEST_READY`) and that a small, well-defined
subset of momentum rules is admissible against the detection-context bars.

This is a Phase 3D/3A readiness→evaluation-integration batch. **Do NOT begin Phase 3E.**

Hard constraints (unchanged from Batch 07 and still binding):

- Do NOT weaken, bypass, reinterpret, or modify the Batch 04 **global** preflight; it must
  remain `PREFLIGHT_REJECTED` for the detection-context bundles. Operation-specific
  admissibility is the only sanctioned narrower path.
- Do NOT admit any BLOCKED operation's evidence: `PRICE_RANGE` (absolute price level),
  `RELATIVE_VOLUME_MINIMUM` and all volume operations, and all non-market-bar-domain rules
  stay `INSUFFICIENT_DATA`/`UNKNOWN`. Do not guess the unresolved volume/timestamp/corp-
  action semantics.
- Do NOT read or use `FROZEN_FORWARD_24H` bars, outcomes, substantial-move labels, forward
  OHLCV, confusion matrices, or later scanner results. No outcome access.
- Do NOT request new market data, connect to IBKR, or modify raw Batch 05 artifacts.
- Do NOT score, rank, weight, optimize thresholds, backtest, compute P&L, or trade.
- You WILL, for the admissible momentum rules only, need to read the detection-context
  OHLCV values (that is authorized for Batch 08 because those operations are admissible);
  keep a hard guard against reading the forward artifacts' OHLCV.

## 1. Exact starting checkpoint

Implementation repository:
`<repo-root>\short-squeeze-core`

Expected current branch: `batch/phase-3d-operation-specific-readiness-07`

Expected exact HEAD: the Batch 07 finalizing commit
(`chore: finalize operation-specific readiness batch 07`) — the tip of the branch above.
Verify with `git rev-parse HEAD`; the Batch 07 session reported the exact full hash in its
completion summary. Do not proceed if the working tree is dirty beyond the known untracked
`docs/phase-3c-complete-handoff.md`.

Prior committed anchors within Batch 07 (in order):
- `4b02053` docs: preregister operation-specific readiness batch 07
- `62a73e6` feat: add operation-specific evidence admissibility and phase 3a readiness
- `26039f1` test: add operation readiness and temporal uncertainty coverage
- `eae33d5` docs: report batch 07 evidence-readiness findings
- (tip) chore: finalize operation-specific readiness batch 07

Previous approved checkpoints:
- Batch 06: `ae1aa4e4cc82cc8aea5b49a58e2d6d3ed15a1e17`
- Batch 05: `fe7ba9d0ecfdaaaf84edfef413fa3fecbd2ccf0b`
- Batch 04: `437c596b0fa53a0a555053b066c9b1e7363d3205`
- Batch 03: `1c3b9329ea63fbfffe68281542bdf692170d50fc`
- Batch 02: `06e3a97039a04b7247350bd57ed5f801998fe97b`
- Batch 01: `37ac03ab196057398f1f6c3463118633316f58f2`
- Phase 3D: `a92906d395e17ee8dff15c69395f0b37427bc66a`
- Phase 1 RC tag `phase-1-rc1`: `f903d4d144d3f7e9717b1ab8e684da406d7968fb`
- Archived parent: `0897562e05d75b812dd284de81dfafdfa1dea916`
- Archived nested submodule: `6dbefd1a6b271bfc48106c4aa002f211735551cd`

Expected baseline: **2,256 passed / 1 skipped / 0 failed** (2,257 collected).

Before modifying anything, verify: `git branch --show-current`, `git rev-parse HEAD`,
`git status --short`, `git remote -v`, `git rev-parse phase-1-rc1^{}`, `git log --oneline
-15`; reproduce the baseline with a fresh `--basetemp` and authoritative JUnit counts;
`python -m tools.ibkr_historical_export verify-private-batch` (expect 26 artifacts, 0
mismatches); verify archived topology read-only. Do not proceed unless all gates pass.

## 2. New branch

After verification create `batch/phase-3d-phase3a-request-freeze-08` from the Batch 07
tip. Task name: "Phase 3D Operation-Specific Phase 3A Request/Result Freeze Batch 08".
This is **not** Phase 3E.

## 3. Frozen cohort (unchanged, exact source order)

XNCR, PESI, SLS, ZNTL, GPRE, SSPC, LBGJ, TRVI, LMNX, MGNX, BHVN, OBE, AVTX — case ids
`BATCH01_<SYM>_20260718`, frozen boundary `2026-07-18T13:37:55.017661Z`. Do not change
membership, order, ids, boundary, identity/eligibility records, or Batch 01/02 registry
bytes. Reuse the Batch 07 associations
(`src/squeeze_core/acquisition/operation_readiness`).

## 4. What Batch 07 established (your admissibility contract)

- `MARKET_DATA_AVAILABLE` → ADMISSIBLE (bars exist).
- `COMPLETED_BAR_AVAILABLE` → ADMISSIBLE (final bar `2026-07-17T23:59:00Z` definitely
  completed before the boundary under both timestamp interpretations; no straddle).
- `PERCENTAGE_CHANGE_MINIMUM` (`PERCENTAGE_RETURN`) → ADMISSIBLE_WITH_CONSTRAINTS
  (split-invariant ratio; both boundary bars must be definitely completed; prices not
  dividend-adjusted).
- `PRICE_RANGE` → BLOCKED_MISSING_SEMANTICS (absolute level, corp-action unconfirmed).
- `RELATIVE_VOLUME_MINIMUM` and all volume ops → BLOCKED_MISSING_SEMANTICS (unit +
  corp-action + filter stationarity unresolved).
- 13 non-market-bar rules → BLOCKED_MISSING_EVIDENCE; 7 EVIDENCE_VALIDITY meta-rules →
  NOT_APPLICABLE (they validate the assembled request).
- All 13 cases → `PHASE3A_REQUEST_READY` (skeleton).

Full detail: `docs/batch-07-*` and the `operation_readiness` package. Global preflight
stays `PREFLIGHT_REJECTED`.

## 5. Required work (preregister first)

1. Preregister `docs/batch-08-phase3a-request-freeze-plan.md`: cohort, admissible-evidence
   whitelist (exactly the three momentum rules above), a **narrow operation-specific
   admission path** for the detection-context bars into a Phase 3A request that admits ONLY
   the whitelisted operations' inputs and never depends on the unresolved
   volume/absolute-price/timestamp-START-END semantics, the treatment that leaves all other
   rules at `INSUFFICIENT_DATA`/`UNKNOWN`, deterministic identity, output schema (keep
   1.0.0), tests, stop conditions, completion criteria. Commit before implementation.
2. Build the detection-context OHLCV reader used ONLY for the admissible operations, with a
   static and runtime guard that forbids reading the forward artifacts' OHLCV and that
   refuses to feed any BLOCKED operation.
3. Construct `RuleEvaluationRequest` objects for the 13 cases from frozen identity +
   admissible inputs; evaluate via the existing Phase 3A evaluator; freeze
   `RuleEvaluationResult`/`CandidateEvaluationResult` records. Non-admissible rules must
   come back `INSUFFICIENT_DATA`/`UNKNOWN`, not FAIL. Do not fabricate any input.
4. Assert the global Batch 04 preflight is untouched and still `PREFLIGHT_REJECTED`.
5. Determinism: generate twice, compare bytes. Synthetic fixtures for tests; do not commit
   real IBKR bar data or its derived per-bar values.

## 6. Tests (at least)

Global preflight unchanged; only whitelisted rules evaluate to PASS/FAIL, everything else
`INSUFFICIENT_DATA`/`UNKNOWN`; blocked operations never admitted; no forward OHLCV read; no
outcome fields; percentage-change uses definitely-completed boundary bars; determinism
byte-identical; Batch 01–07 committed bytes unchanged; Batch 05 private hashes unchanged;
schema 1.0.0; full suite green.

## 7. Required committed documentation

`docs/batch-08-phase3a-request-freeze-plan.md`, `docs/batch-08-phase3a-results-summary.md`,
`docs/batch-08-test-and-verification-report.md`, `docs/batch-08-completion-report.md`,
`docs/batch-09-fresh-session-handoff.md` (a complete real file whose next task depends on
the Batch 08 result — e.g. if the thin Phase 3A results are frozen, the following task is
to lawfully acquire the single broadest still-blocking evidence domain, corporate-action
context for the cohort over the boundary→retrieval gap, to widen admissibility).

## 8. Stop conditions

Checkpoint differs; baseline not reproducible; prior artifacts modified; private hashes
mismatch; admitting an operation would require the global preflight to weaken; a whitelisted
rule cannot be evaluated without fabricating input; evaluation would require reading forward
/ outcome bars; completing would require new market data, guessing unresolved semantics, or
beginning Phase 3E. Conservative INSUFFICIENT_DATA/UNKNOWN results are valid.

## 9. Definition of done

Checkpoint verified; baseline reproduced; plan preregistered; the three admissible momentum
rules evaluated and frozen for all 13 cases with all other rules INSUFFICIENT_DATA/UNKNOWN;
global preflight unchanged; no outcome/forward access; deterministic byte-identical outputs;
tests pass; Batch 01–07 + Batch 05 bytes unchanged; archived topology unchanged; completion
report + real Batch 09 handoff exist; exact final HEAD reported; Phase 3E unstarted; stop.

## 10. Final response format

Report: decision/status; starting and final branch + exact full HEAD; commit list with full
hashes; baseline and final test totals; admissible-rule evaluation summary; the 13-case
Phase 3A result table (admissible rules only, others INSUFFICIENT_DATA/UNKNOWN); global
preflight unchanged confirmation; Batch 05 raw-integrity confirmation; forward-artifact
non-use confirmation; no-outcome-access confirmation; no-new-fetch confirmation;
determinism verification; prior-artifact compatibility; archived-topology verification;
deviations; limitations; exact Phase 3E stop statement; path to Batch 08 completion report;
path to actual Batch 09 handoff; exactly one recommended next task. Do not start it.
