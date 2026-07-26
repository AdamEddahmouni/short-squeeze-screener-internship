# Batch 10 — Completion Report

**Professor-Demo Truthful Operational Short-Squeeze Screener**

Status: **complete**. The application launches with one command and demonstrates the full
§28 walkthrough. This was an application / integration batch: no research artifact was
produced, no canonical registry was changed, and Phase 3E remains unstarted.

## 1. Checkpoints

| | Branch | HEAD |
| --- | --- | --- |
| Starting | `batch/phase-3d-phase3b-registry-preview-09` | `663954ca14744653167b5f634b2ff0365ec25ed2` |
| Final | `batch/professor-demo-operational-screener-10` | the `chore: finalize professor demo screener` commit; verify with `git rev-parse HEAD` |

Verified before any change: branch, HEAD, clean tree apart from the pre-existing untracked
`docs/phase-3c-complete-handoff.md` (left untouched), `phase-1-rc1` →
`f903d4d144d3f7e9717b1ab8e684da406d7968fb`.

## 2. Commits

| Subject |
| --- |
| docs: preregister professor demo operational screener |
| feat: add truthful research screener application |
| test: add operational screener meeting-smoke coverage |
| docs: add professor meeting guide and original feature parity audit |
| chore: finalize professor demo screener (final HEAD) |

No approved checkpoint was amended or rewritten.

## 2a. Test totals

| | Result |
| --- | --- |
| Baseline (Batch 09 HEAD) | 2,378 passed / 1 skipped / 0 failed |
| Final (Batch 10 HEAD) | 2,436 passed / 1 skipped / 0 failed |
| Net new tests | +58 |

The single pre-existing skip is unchanged. No prior test was modified, skipped or
weakened. Five pre-existing compatibility and isolation tests went red mid-batch and were
made green by moving the application out of the runtime, not by relaxing the guards — see
deviation 0.

## 3. What was built

`apps/research_screener/` — a read-only view/controller layer, plus `run_screener.ps1`.

The UI is a localhost browser dashboard served by a stdlib `http.server`. No framework, no
build step, no external asset, no new dependency. Tkinter was not restored.

Three modes, never silently interchanged:

- **Frozen Research** — the 13 real Batch 01 cases with their frozen Batch 08 Phase 3A
  requests and results. Works with every provider down.
- **Current** — read-only local IB Gateway access via the already-validated Batch 05
  session. Publishes no rule outcome.
- **Manual Symbol** — any ticker, through the same read-only path.

## 4. Truthfulness protections

| Protection | Mechanism |
| --- | --- |
| Missing is never zero | `FieldValue` raises if a non-`KNOWN` status carries a value, and raises again if no reason is given |
| `UNKNOWN` never reads as `PASS` | textual outcome label always rendered, independent of colour |
| No fake `LIVE` label | `LIVE` is only produced by an explicit `DataMode.LIVE`; current-mode bars are labelled `HISTORICAL` with a computed age |
| No synthetic fallback | `DataMode.REPLAY` exists in the enum but no code path produces it; a test asserts that |
| No score or ranking | no score field, no rank, no weight; sort keys are evidence counts only |
| No forward-window read | `guard_readable()` raises on `frozen-forward` / `FROZEN_FORWARD`; every artifact read goes through it |
| No orders or account access | source-level test scans the whole package for 12 order and 9 account identifiers |
| No access-control bypass | source-level test asserts `curl_cffi`, `impersonate`, `finviz_auth`, `login_submit` appear nowhere |
| No credentials in exports | exporter walks the payload and raises on any credential-shaped key |
| No metric re-implementation | AST test forbids `× 100`; `Decimal` is absent; a behavioural test asserts the displayed percentage equals the frozen metric value byte-for-byte |
| Localhost only | server raises on any non-localhost bind; provider probe raises on any non-localhost host |

## 5. What the demo shows, and what it does not

The screener reproduces the Batch 08 freeze exactly: 13 cases, 325 rule-case evaluations,
97 `PASS` / 20 `FAIL` / 208 `UNKNOWN`, `PERCENTAGE_CHANGE_MINIMUM` 6 `PASS` / 7 `FAIL`,
91 short-pressure `UNKNOWN`, 65 catalyst `UNKNOWN`, 13 × `UNEVALUABLE` research detection,
13 × `INCOMPLETE` outcome, `PREFLIGHT_REJECTED` echoed throughout.

It does not show a prediction, an accuracy figure, a squeeze score, a tier, a target, a
stop, or a buy/sell control, because none of those is supported by the evidence.

## 6. Deviations from the preregistered plan

Three. None affects a displayed outcome. The preregistration was left exactly as
committed; the deviations are recorded here instead of being edited into it.

0. **The application lives at `apps/research_screener/`, not `src/squeeze_core/app/`.**
   The plan named the latter. Building it there turned five pre-existing compatibility and
   isolation tests red: `src/squeeze_core` is a closed runtime whose changes are restricted
   to an explicit package allowlist since Phase 2C, and a Phase 3D guard forbids the
   runtime from referencing `tools/` or `ibapi` at all — which the screener's read-only
   IBKR session must do. Those guards are correct and were not weakened. The package was
   moved to `apps/`, alongside the repository's existing `apps/biya-validation-demo`, which
   is where a view layer belongs. Only import paths changed; no behaviour did.

1. **Current mode publishes no Phase 3A rule outcome.** The plan allowed for a
   provider-backed mode; it did not commit to evaluating rules over live evidence. Live
   bars carry the semantics Batch 06 left unresolved and have never passed the Batch 07
   admissibility gate, so publishing outcomes over them would assert an admissibility that
   does not exist. All 25 rules report `UNKNOWN` with that reason stated.
2. **Automated candidate discovery is deferred.** The original's IB scanner path is
   reachable, but admitting a discovered cohort without a preregistered eligibility rule
   would reintroduce the selection effect this project was rebuilt to avoid. Manual Symbol
   mode provides the operational reach without defining a cohort by accident.

## 7. Test hermeticity

The current-mode tests do not contact a provider. An earlier draft called the real
gateway, which made part of the suite depend on whether IB Gateway happened to be running
on the executing machine. Both current-mode paths are now driven by a forced failure and
a fake session respectively, so the assertions hold identically on a machine with no
gateway. Current mode was separately verified against the user's live gateway by hand
during this batch: `XNCR` resolved and returned a completed bar close of `19.44` with
event time `2026-07-24T23:59:00Z`, labelled `HISTORICAL` / `STALE`, with all 25 rules
`UNKNOWN`.

## 8. Confirmations

| Confirmation | Status |
| --- | --- |
| Canonical Phase 3B registry unchanged | verified by digest before and after the full demo workflow |
| Batch 05 raw artifacts unchanged | 13 detection-context CSVs, digests identical after the demo |
| Batch 08 freeze unchanged | digests identical; `verify-phase3a-freeze` returns 0 after the demo |
| Batch 09 preview read, never published | `canonical_registry_mutated=false`, `phase3b_published=false` |
| Forward artifacts present but untouched | digests identical after the demo |
| Application writes only into the export directory | asserted by test |
| Runtime isolation intact | `src/squeeze_core` is byte-identical to Batch 09; the Phase 2C/2D/3B/3C/3D additive guards and the tool-isolation guard all pass |
| Phase 3E unstarted | `phase3e_started=false` on every record |
| Schema | `1.0.0` |

## 9. Known gaps

Short-pressure evidence, catalyst evidence, borrow data, news, sentiment and forward
outcomes are all absent, and the application says so on every affected cell rather than
filling them. Volume semantics and absolute price levels remain inadmissible. Automated
discovery, current-mode charting and auto-refresh are not implemented.
