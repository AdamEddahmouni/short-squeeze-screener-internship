# Claude Fresh-Session Handoff — Batch 07 Authoritative Resolution of Remaining IBKR Historical-Bar Semantics

## Purpose

Continue the short-squeeze research reconstruction project from the completed Batch 06
checkpoint.

Your only authorized task is:

Attempt an **authoritative** resolution of the two IBKR historical-bar semantic fields that
Batch 06 left honestly `UNKNOWN` — **(a) volume corporate-action adjustment** and **(b) the
intraday bar timestamp start/end boundary** — using exhaustive official Interactive Brokers
documentation and the installed official `ibapi` contract, plus, only if explicitly permitted
in-session, one read-only live-Gateway UI observation for the **volume unit** (shares vs round
lots). Then re-run the existing Batch 04 offline preflight against the already-collected 13
`DETECTION_CONTEXT_PRECEDING_24H` artifacts and record the honest result.

Do not request any new historical bars. Do not reconnect to IB Gateway for market-data
collection. Do not shift/extend/replace any window. Do not associate data with research cases.
Do not calculate outcomes. Do not begin Phase 3E.

This is a Phase 3D evidence-semantics and offline-preflight batch only. If official evidence
still does not establish a field, preserve `UNKNOWN` and the resulting `PREFLIGHT_REJECTED`
honestly — do not force acceptance and do not change schema `1.0.0` or any validator to obtain
`READY`.

Do not ask routine clarification questions. Inspect the repository, the private Batch 05/06
artifacts, and official IBKR documentation first. Ask only if a true stop condition is reached.

---

## 1. Repository checkpoint

Implementation repository: `<repo-root>\short-squeeze-core`

Expected current branch: `batch/phase-3d-ibkr-semantics-resolution-06`

Expected current HEAD: the tip of that branch — the Batch 06 finalize commit
("docs: report batch 06 completion and add batch 07 handoff"). Verify with:

```
git branch --show-current
git rev-parse HEAD
git log --oneline -8
git status --short
```

Batch 06 commit chain (all must be present):

- `07a97330caa1591757c05086b664db8b8bc53384` docs: preregister IBKR semantics resolution batch 06
- `91b862bf1572538ce4570dce8079d49182537c52` feat: add deterministic IBKR historical semantics resolver
- `d65c58a06cec1269e31529f96c37fe7888eca4d2` test: add IBKR semantics and re-preflight coverage
- `c9300caf5d565ee7950d7ee8521d04a2cf607b69` docs: record official IBKR historical-data semantics evidence
- (finalize commit) docs: report batch 06 completion and add batch 07 handoff

Prior checkpoints: Batch 05 `fe7ba9d0ecfdaaaf84edfef413fa3fecbd2ccf0b`; Batch 04
`437c596b0fa53a0a555053b066c9b1e7363d3205`; Batch 03 `1c3b9329ea63fbfffe68281542bdf692170d50fc`;
Phase 3D `a92906d395e17ee8dff15c69395f0b37427bc66a`; `phase-1-rc1` =
`f903d4d144d3f7e9717b1ab8e684da406d7968fb`.

Archived parent HEAD `0897562e05d75b812dd284de81dfafdfa1dea916`; nested submodule
`app/ScreenerProject` `6dbefd1a6b271bfc48106c4aa002f211735551cd`. Workspace root has an inert
empty `.git`; do not modify it. Pre-existing untracked files (`docs/phase-3c-complete-handoff.md`)
must be left untouched.

Expected starting full-suite baseline: **2227 passed, 1 skipped, 0 failed.**

Pytest rules: fresh explicit `--basetemp`; `-p no:cacheprovider` when useful; never the locked
`.pytest-tmp`; do not broadly delete `.pytest-run-*`.

Before modifying anything: verify branch/HEAD, reproduce the baseline, verify Batch 01–06
committed artifacts, verify private Batch 05 raw hashes
(`python -m tools.ibkr_historical_export verify-private-batch` → 26 artifacts, 0 mismatches),
and verify the Batch 06 overlays regenerate byte-identically
(`python -m tools.ibkr_historical_export resolve-semantics`). Do not proceed unless all gates
pass.

## 2. Frozen Batch 06 facts

- Official record establishes: TRADES price is split-adjusted, not dividend-adjusted
  (`PriceAdjustmentSemantics.SPLIT_ADJUSTED`, `CorporateActionHandling.ADJUSTMENTS_APPLIED`);
  `formatDate=2` = epoch seconds GMT → `event_timezone = UTC`; `useRTH=0` → requested
  `BarSession.EXTENDED`.
- Official record is SILENT on: volume corporate-action adjustment; intraday bar start/end.
  These remain `UNKNOWN`. Do not carry forward Batch 05's assumed `START`.
- Volume unit is `HISTORICAL_VOLUME_UNIT_UNRESOLVED` (not a manifest field; provenance only).
- All 13 detection-context artifacts are `PREFLIGHT_REJECTED`
  (`MISSING_ADJUSTMENT_SEMANTICS` + `MISSING_TIMESTAMP_SEMANTICS`).
- The 13 `FROZEN_FORWARD_24H` artifacts are excluded from forward-outcome use and are never
  re-preflighted as forward evidence.
- The pure resolver lives at `src/squeeze_core/acquisition/ibkr_semantics/` (evidence.py +
  resolver.py); the offline overlay generator at
  `tools/ibkr_historical_export/semantics_overlay.py`; CLI subcommand `resolve-semantics`.
- Private overlays: `intake/local-bars/ibkr-batch-05/semantics/batch-06/` (Git-ignored).

## 3. New branch and task identity

After all gates pass, create `batch/phase-3d-ibkr-semantics-resolution-07` from the Batch 06
HEAD. Task name: "Phase 3D Authoritative Resolution of Remaining IBKR Historical-Bar Semantics
(Batch 07)". This is not Phase 3E.

## 4. Evidence policy (unchanged)

Official IBKR documentation only (`interactivebrokers.github.io/tws-api/*`, `ibkrcampus.com`,
`interactivebrokers.com/campus`) and the installed `ibapi` source. No forums, blogs, Q&A
sites, third-party tutorials, AI summaries, or unofficial mirrors. Every conclusion cites an
exact official source with access date, section, paraphrase, and the field it supports. Keep
official-fact / installed-API / local-observation / project-inference classes distinct.

Suggested additional official pages not yet exhausted in Batch 06:
`realtime_bars.html` (5-second bar time meaning — note it is a different endpoint; use only to
compare, not to assert historical semantics), `historical_time_and_sales.html`,
`head_timestamp.html`, and the current ibkrcampus historical-data lessons. If none establishes
the field, keep `UNKNOWN`.

## 5. Volume-unit Level-3 policy

Only if the user explicitly authorizes a live-Gateway UI observation this session: read-only,
navigate Configure → API → Settings, read the volume-scaling checkbox state, change nothing,
read no account/portfolio screens, record a sanitized `SHARES`/`ROUND_LOTS` result plus the
caveat that the current UI state may differ from the state during Batch 05 collection.
Otherwise keep `HISTORICAL_VOLUME_UNIT_UNRESOLVED`. Never infer from bar values or build number.

## 6. Implementation

If a field becomes officially established, update the frozen evidence constant
(`OFFICIAL_TRADES_EVIDENCE`) and citations in
`src/squeeze_core/acquisition/ibkr_semantics/evidence.py` — never the resolver's mapping logic
to force a result — regenerate the private overlays, and re-run the offline preflight. Preserve
raw Batch 05 bytes; write new versioned overlays (e.g. `semantics/batch-07/`) rather than
rewriting Batch 06 overlays. Add tests mirroring Batch 06 for any newly resolved field. Keep
schema `1.0.0`.

## 7. Expected outcome

If official evidence remains silent (the most likely case), the honest result is unchanged:
13 `PREFLIGHT_REJECTED`. That is a valid completion, not a failure. Document what was searched
and why each field stays `UNKNOWN`.

## 8. Required committed documentation

`docs/batch-07-...-plan.md`, evidence report, re-preflight summary, test/verification report,
completion report, and a real `docs/batch-08-fresh-session-handoff.md`. Do not start Batch 08.

## 9. Stop conditions

The Batch 06 handoff §25 stop conditions carry forward. A rejected preflight is not a stop
condition — preserve it honestly. Stop only if the checkpoint differs, the baseline cannot be
reproduced, committed or raw artifacts are already modified, resolving a field would require
contradicting official documentation or changing schema/validators, or completing the task
would require a new fetch, account/credential access, case association, outcome work, or
beginning Phase 3E.

## 10. Forbidden work

Same as Batch 06 §26: no new historical bars, no market-data connection, no window
shift/extend/replace, no Monday substitute, no account/credential access, no orders, no case
association, no outcomes/returns/thresholds, no Phase 3B publication, no Phase 3C expansion, no
Phase 3E, no scoring/ranking/optimization/ML/backtests/P&L/trading, no modification of archived
evidence, no schema change to obtain READY.

## 11. Definition of done

Checkpoint verified; baseline reproduced; private bytes verified; plan preregistered; official
evidence exhaustively searched and cited; any newly resolvable field resolved without forcing;
remaining fields preserved `UNKNOWN`; raw Batch 05 bytes unchanged; overlays versioned
separately; exactly 13 detection-context artifacts re-preflighted; forward artifacts excluded;
no new fetch/case/outcome; tests pass; Batch 01–06 committed + archived artifacts unchanged;
reports + Batch 08 handoff written; exact final HEAD reported; Phase 3E unstarted; work stops.

## 12. One recommended next task (do not start it in Batch 06)

Execute Batch 07 exactly as scoped above: exhaustively re-check official IBKR documentation for
the two remaining fields, apply any honestly-established resolution, and re-run the offline
preflight — preserving `UNKNOWN`/`PREFLIGHT_REJECTED` where the official record is still silent.
