# Claude Fresh-Session Handoff — Batch 09

## Purpose

Continue the short-squeeze research reconstruction from the completed Batch 08 checkpoint.

Batch 08 froze 13 canonical Phase 3A requests and 13 canonical Phase 3A results for the 13
frozen Batch 01 cases, using only evidence Batch 07 declared operation-specifically
admissible, and executed the existing Phase 3A evaluator to produce every rule outcome.

**Batch 09 is not yet scoped.** The next task depends on a decision the supervisor has been
asked to make (see §8). Do not begin implementation work until that decision is recorded, or
until the user names a different task explicitly.

This remains Phase 3D controlled curation and evaluation infrastructure. Phase 3E is not
started.

---

## 1. Exact starting checkpoint

Implementation repository:

`<repo-root>\short-squeeze-core`

Expected current branch:

`batch/phase-3d-phase3a-freeze-08`

Expected exact HEAD: see the "Exact final HEAD" line in
`docs/batch-08-completion-report.md`.

Previous approved checkpoints:

| Batch | Commit |
| --- | --- |
| Phase 3D | `a92906d395e17ee8dff15c69395f0b37427bc66a` |
| Batch 01 | `37ac03ab196057398f1f6c3463118633316f58f2` |
| Batch 02 | `06e3a97039a04b7247350bd57ed5f801998fe97b` |
| Batch 03 | `1c3b9329ea63fbfffe68281542bdf692170d50fc` |
| Batch 04 | `437c596b0fa53a0a555053b066c9b1e7363d3205` |
| Batch 05 | `fe7ba9d0ecfdaaaf84edfef413fa3fecbd2ccf0b` |
| Batch 06 | `ae1aa4e4cc82cc8aea5b49a58e2d6d3ed15a1e17` |
| Batch 07 | `238986695c2bc053d54a6fd1037cdb145e9c5781` |

Phase 1 release-candidate tag: `phase-1-rc1` → `f903d4d144d3f7e9717b1ab8e684da406d7968fb`

Archived parent expected HEAD: `0897562e05d75b812dd284de81dfafdfa1dea916`
Archived nested submodule expected HEAD: `6dbefd1a6b271bfc48106c4aa002f211735551cd`

The workspace root contains an inert empty `.git` directory. Do not modify it.

Pre-existing untracked files may exist (for example `docs/phase-3c-complete-handoff.md`).
Leave them and every unrelated untracked file untouched.

Known pytest rules: use a fresh explicit `--basetemp`; use `-p no:cacheprovider` when
useful; do not use the locked `.pytest-tmp`; do not broadly delete `.pytest-run-*`.

Before modifying anything, verify:

```
git branch --show-current
git rev-parse HEAD
git status --short
git remote -v
git rev-parse phase-1-rc1^{}
git log --oneline -15
```

Verify archived topology read-only. Reproduce the Batch 08 final baseline (recorded in the
completion report) using authoritative JUnit XML if ordinary output truncates. Verify the
private Batch 05 artifact hashes with the existing offline verifier — expect 26 artifacts,
0 mismatches:

```bash
./.venv/Scripts/python.exe -m tools.ibkr_historical_export verify-private-batch
```

Verify the Batch 08 freeze is reproducible:

```bash
./.venv/Scripts/python.exe -m squeeze_core.acquisition.phase3a_freeze verify-phase3a-freeze
```

Do not proceed unless every gate passes.

---

## 2. What Batch 08 delivered

- `src/squeeze_core/acquisition/phase3a_freeze/` — an additive package that builds
  admissible Phase 3A requests, runs the **existing** evaluator, and freezes both bytes
  deterministically. It duplicates no metric formula, no rule logic, no UUID
  infrastructure, no serializer, and no leakage-audit engine.
- Three offline CLI commands: `generate-phase3a-freeze`, `verify-phase3a-freeze`,
  `render-phase3a-freeze-report`.
- 13 frozen Phase 3A requests and 13 frozen Phase 3A results, private, under
  `intake/local-bars/ibkr-batch-05/phase3a/batch-08/`.
- 13 of 13 leakage audits passed.
- A committed synthetic golden fixture and 63 new tests.
- Documentation: plan, admissible-evidence mapping, request construction, rule-outcome
  summary, leakage/determinism report, Phase 3B publication-readiness preview, test and
  verification report, professor brief, completion report, and this handoff.

Rule outcomes across 325 rule-case pairs: 97 `PASS`, 20 `FAIL`, 208 `UNKNOWN`. Three of 25
rules are substantively evaluable; 22 remain unknown for documented reasons.

---

## 3. Frozen invariants — do not change

Cohort, exact source order:

`XNCR, PESI, SLS, ZNTL, GPRE, SSPC, LBGJ, TRVI, LMNX, MGNX, BHVN, OBE, AVTX`

Case ids `BATCH01_<SYMBOL>_20260718`. Frozen detection boundary
`2026-07-18T13:37:55.017661Z`. Schema version `1.0.0`.

Do not change: case membership, source order, case ids, boundaries, Batch 01 identities or
eligibility, Batch 01/02 registry bytes, Batch 05 raw artifacts, Batch 06 semantics, Batch
07 readiness results, or Batch 08 frozen request/result bytes.

The Batch 04 global preflight remains `PREFLIGHT_REJECTED`. Do not modify, suppress,
reinterpret, or weaken it, and do not create a competing global-ready status.

Frozen policy versions:

| Policy | Value |
| --- | --- |
| Phase 3A request/result | `phase_3a_transparent_candidate_policy.v1` |
| Phase 3A evaluation | `candidate_evaluation.v1` |
| Batch 07 readiness | `phase_3d_operation_readiness_policy.v1` |
| Batch 06 semantics | `phase_3d_ibkr_semantics_resolution.v1` |
| Batch 08 freeze | `phase_3d_phase3a_freeze_policy.v1` |
| Receipt modeling (primary) | `PROVIDER_AVAILABILITY_AS_RECEIPT.v1` |

---

## 4. Private evidence scope

Openable for bar values: **only** `raw/<SYMBOL>-detection-context.csv`
(`DETECTION_CONTEXT_PRECEDING_24H`) for the 13 frozen symbols.

`FROZEN_FORWARD_24H` artifacts must never be opened for values. They may be referenced only
by filename, request id, SHA-256, byte length, existence, and preserved blocked status.
Never inspect their open, high, low, close, volume, WAP, or trade count.

Do not access Phase 3B outcome artifacts or labels.

The `phase3a_freeze` package already enforces all of this at the file reader
(`ForwardArtifactAccessError`, `OutcomeArtifactAccessError`,
`NonDetectionContextArtifactError`). Reuse it rather than opening files directly.

---

## 5. Two documented constraints to be aware of

**Request-level provider scope.** The Phase 3A request contract has request-level, not
per-rule, evidence scoping. Batch 08 keeps blocked absolute-price and float evidence away
from `PRICE_RANGE` / `FLOAT_MAXIMUM` by leaving `provider_scope` empty, which makes those
rules short-circuit at the policy's own `provider_scope_required` gate. A side effect is
that `PROVIDER_SCOPE_EXPLICIT` resolves `UNKNOWN` and three short-pressure rules report
`EVALUATION_PROVIDER_SCOPE_REQUIRED` rather than a more specific unavailability code. This
is a contract granularity limitation, not an evaluator defect. Do not "fix" it by patching
the evaluator without separate authorization.

**Superlinear point-in-time bundling.** `build_point_in_time_evidence` conflict detection
scales superlinearly (12.73 s at 200 observations) and the evaluator rebuilds the bundle per
bar-dependent rule. Batch 08 therefore attaches only the observations the canonical metric
consumed. If a future batch needs many observations in one request, this is the bottleneck
to address — as its own authorized task, with its own preregistration.

---

## 6. Forbidden work

Do not: request new IBKR data; connect to IBKR; download external market data; open forward
OHLCV; access outcomes; change the frozen boundary; shift the weekend window; weaken the
global preflight; infer volume units; infer corporate-action semantics; use blocked
absolute-price or volume evidence; fabricate float, short-pressure, or catalyst evidence;
alter rule thresholds, weights, categories, or the 25-rule inventory; create a second
evaluator; manually assign rule outcomes; expand Phase 3C; begin Phase 3E; score or rank
candidates; optimize thresholds; run machine learning; backtest; calculate P&L; recommend
trades; create alerts; paper trade; live trade; place orders; or redesign the GUI.

---

## 7. Stop conditions

Stop and report without improvising if: the checkpoint differs; the Batch 08 baseline cannot
be reproduced; prior committed artifacts are unexpectedly modified; Batch 05 private hashes
do not match; the Batch 08 freeze is not byte-reproducible; work would require weakening the
global preflight, opening forward OHLCV, or accessing an outcome; a genuine defect is found
in existing code; deterministic freezing would change prior serialized bytes; or the work
would begin Phase 3E.

A result dominated by `UNKNOWN` or `INSUFFICIENT_DATA` is not failure. Preserve it honestly.

---

## 8. The open decision that scopes Batch 09

The supervisor has been asked exactly one question (see `docs/batch-08-professor-brief.md`):

> Whether to approve a Phase 3B registry revision that references the new frozen Phase 3A
> evaluations while retaining all cases as outcome-incomplete and explicitly non-predictive.

**If approved**, Batch 09 is: a Phase 3B registry revision that adds, per case, a reference
to the frozen Phase 3A request id / result id / SHA-256 / byte length, while keeping every
case outcome-incomplete, unlabelled, and non-predictive. It would publish references, never
outcomes. Everything it needs is already frozen in
`intake/local-bars/ibkr-batch-05/phase3a/batch-08/manifests/case-manifest.json`.

**If not approved**, the two substantive alternatives, in the order the evidence gaps
suggest, are:

1. **Missing-evidence acquisition design.** Thirteen of 25 rules have no detection-time
   evidence at all (float, seven short-pressure, five catalyst). A batch that designs — not
   executes — a lawful, outcome-blind acquisition plan for those domains would unblock more
   of the evaluation than anything else. Batch 02 already established the source barrier for
   forward outcomes; this is the analogous question for detection-time evidence.
2. **Volume-semantics resolution follow-up.** Resolving the volume unit and
   corporate-action handling would unblock `RELATIVE_VOLUME_MINIMUM`. Batch 06 established
   that IBKR's official documentation is silent, so this needs a different evidence source
   rather than a re-read.

Do not choose between these yourself. Ask, or wait for the user to name the task.

---

## 9. Definition of done for Batch 09

Whatever Batch 09 turns out to be, it is complete only when: the Batch 08 checkpoint is
verified; the Batch 08 baseline is reproduced; a plan is preregistered and committed before
implementation; the global preflight remains rejected and unchanged; no forward OHLCV is
opened; no outcome is accessed; no new data is fetched; real outputs remain private;
synthetic fixtures are committed; generators are byte-identical; focused and full tests
pass; prior and archived artifacts remain unchanged; a completion report and an actual Batch
10 handoff exist; the exact final HEAD is reported; Phase 3E remains unstarted; and work
stops.

---

## 10. Useful commands

```bash
./.venv/Scripts/python.exe -m pytest -q -p no:cacheprovider --basetemp=.pytest-run-b09-baseline --junitxml=.pytest-run-b09-baseline/junit.xml
```

```bash
./.venv/Scripts/python.exe -m squeeze_core.acquisition.phase3a_freeze render-phase3a-freeze-report
```

```bash
./.venv/Scripts/python.exe scripts/generate_batch08_phase3a_freeze_outputs.py --skip-private
```
