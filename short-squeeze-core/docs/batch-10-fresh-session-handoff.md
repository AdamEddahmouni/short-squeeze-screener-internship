# Claude Fresh-Session Handoff — Batch 10

**Do not start Batch 10 until the professor's decision is recorded.** This handoff branches on
that decision and must not guess it.

---

## 1. Starting checkpoint

Implementation repository:

```
<repo-root>\short-squeeze-core
```

Expected current branch:

```
batch/phase-3d-phase3b-registry-preview-09
```

Expected exact HEAD: the Batch 09 final commit (see
`docs/batch-09-completion-report.md` §4 and the Batch 09 session report).

Expected baseline: **2,378 passed / 1 skipped / 0 failed** (2,379 collected).

Previous approved checkpoints:

| Batch | Commit |
|---|---|
| Phase 3D | `a92906d395e17ee8dff15c69395f0b37427bc66a` |
| Batch 01 | `37ac03ab196057398f1f6c3463118633316f58f2` |
| Batch 02 | `06e3a97039a04b7247350bd57ed5f801998fe97b` |
| Batch 03 | `1c3b9329ea63fbfffe68281542bdf692170d50fc` |
| Batch 04 | `437c596b0fa53a0a555053b066c9b1e7363d3205` |
| Batch 05 | `fe7ba9d0ecfdaaaf84edfef413fa3fecbd2ccf0b` |
| Batch 06 | `ae1aa4e4cc82cc8aea5b49a58e2d6d3ed15a1e17` |
| Batch 07 | `238986695c2bc053d54a6fd1037cdb145e9c5781` |
| Batch 08 | `c93f704104429468f920b0d0d88002a821c68b63` |

Phase 1 release-candidate tag `phase-1-rc1` → `f903d4d144d3f7e9717b1ab8e684da406d7968fb`.

Archived parent expected HEAD `0897562e05d75b812dd284de81dfafdfa1dea916`; nested submodule
`6dbefd1a6b271bfc48106c4aa002f211735551cd`. Verify read-only.

The workspace root contains an inert empty `.git` directory. Do not modify it. A pre-existing
untracked file `docs/phase-3c-complete-handoff.md` may exist; leave it and every unrelated
untracked file untouched.

Pytest rules: fresh explicit `--basetemp`; `-p no:cacheprovider` when useful; do not use the
locked `.pytest-tmp`; do not broadly delete `.pytest-run-*`.

---

## 2. Mandatory gates before any change

1. `git branch --show-current`, `git rev-parse HEAD`, `git status --short`, `git remote -v`,
   `git rev-parse 'phase-1-rc1^{}'`, `git log --oneline -15`
2. Reproduce the baseline (authoritative JUnit XML).
3. Verify Batch 01–09 committed artifacts.
4. Verify Batch 05 private raw: **26 artifacts, 0 mismatches**.
5. Verify Batch 08 Phase 3A freeze: **26 request/result artifacts, 0 mismatches**.
6. Verify the Batch 09 preview regenerates byte-identically (14 files, 0 differences) —
   `python -m squeeze_core.acquisition.phase3b_preview generate` then compare.
7. Verify the canonical Phase 3B registries are still byte-identical:

| File | sha256 |
|---|---|
| `tests/fixtures/acquisition/batch01/phase3b-registry-candidates.json` | `c16b49386f96705d43bb110fa76796ce998299599a49528dc799e1a17e678c73` |
| `tests/fixtures/acquisition/batch02/phase3b-registry-candidates.json` | `af691a27e5568dc4aca9fe94adb07f4efe8ceabe490cb7d88ad9c7ddff9656a2` |
| `tests/fixtures/acquisition/phase_3d_phase3b_registry_candidates.json` | `28d5b14cb7be31665174121011a353eea6afb182c22c43e388fc9e162ba72b07` |
| `tests/fixtures/research/phase_3b_case_registry.json` | `5684ecd6e9f9e5b194379be411654cb5f15f5b24b638339605a2cc232bcb9b79` |

Do not proceed unless all gates pass.

---

## 3. Read the recorded decision first

The professor's decision is **governance metadata**. It must be recorded verbatim in
`docs/batch-10-supervisor-decision.md` before any code changes, and it must never enter any
scientific identity, hash, or UUIDv5 input.

If no decision has been recorded, **stop and ask**. Do not infer one.

---

## 4. Branch A — **APPROVE**

> "Do you approve revising the Phase 3B research registry so these 13 existing real-symbol
> candidates reference their frozen Phase 3A evaluations while remaining explicitly
> `UNEVALUABLE` for research detection and outcome-incomplete?" → **APPROVE**

Branch name: `batch/phase-3d-phase3b-registry-revision-10`
Task name: Phase 3D Phase 3B Registry Revision Batch 10

Perform the **real** deterministic Phase 3B registry revision, exactly matching the Batch 09
preview.

**Required equivalence.** The revised canonical registry must be byte-identical to what the
Batch 09 preview predicted, modulo only the registry version and file location. Assert
per-candidate that the produced `deterministic_id` equals the
`preview_registry_candidate_id` already committed in
`tests/fixtures/acquisition/batch09/registry-revision-preview.json`:

| Symbol | Expected revised candidate ID |
|---|---|
| XNCR | `5184e1c6-eb33-580b-8408-cc960eadfff6` |
| PESI | `6cbab464-94e1-57c9-aa6a-9b7a98290996` |
| SLS | `e6d3a124-e4c8-54b9-91ab-d087d4fd5b15` |
| ZNTL | `eaf0273f-7162-5047-9759-7c1250ab278b` |
| GPRE | `23afdb21-5f96-59a0-9f2c-e28c8a82a73e` |
| SSPC | `8772bf7e-4357-5b24-9594-ece6ee62bd0f` |
| LBGJ | `7cdfa914-5d0f-5020-91d0-783ce07606c0` |
| TRVI | `944a5499-a6b3-532c-b964-85525a78cb7b` |
| LMNX | `9b11753d-1f75-5c63-80d2-a5805c2d74b7` |
| MGNX | `73bcf3b6-a518-5c45-9526-188e2596cbcc` |
| BHVN | `c5a92c9d-44a4-55bb-ae14-385a7b5bd4d7` |
| OBE | `0a59fb6a-b746-5f4f-9a18-d2ea67560cfb` |
| AVTX | `2eda5211-d9a4-565b-8fa3-a00c4260bd81` |

If any produced ID differs, **stop** — the revision has drifted from what was approved.

Steps:

1. Preregister `docs/batch-10-phase3b-registry-revision-plan.md` and commit it before touching
   the registry.
2. Decide and document the registry-version policy: bump `phase_3d_batch_01_registry.v1` to a
   successor version, or publish a new registry document. **Do not overwrite the Batch 01
   registry's historical bytes** — the prior version must remain retrievable, and the Batch 09
   sha256 guard test must be updated deliberately, with the old hash recorded in the plan, not
   silently deleted.
3. Reuse `squeeze_core.acquisition.phase3b_preview.build_preview_entry` and
   `build_registry_field_diff` to produce and verify the revision. Do not write a second
   implementation.
4. Confirm outcome fields untouched: `outcome_observation_path` null ×13, outcome status
   incomplete ×13.
5. Confirm detection is still executed, not assigned, and still `UNEVALUABLE` ×13.
6. Re-run the publication path: expect 0 case results, 13 skipped, 0 dataset rows.
7. Update every downstream fixture and anchor that references the Batch 01 registry ID
   `15241fb5-d53d-57a2-9d79-5bec6d2519d5` or any of the 13 prior candidate IDs.
8. Update `docs/batch-01-phase3b-publication-summary.md` and any Phase 3C descriptive summary
   that quotes the old registry state.
9. Record the approval in `docs/batch-10-supervisor-decision.md`.
10. Run one authoritative final full suite.

Forbidden in Branch A: creating outcomes; changing `PRICE_RANGE`, the detection policy, or the
outcome policy; changing Phase 3A results or thresholds; publishing dataset rows; starting
Phase 3E.

---

## 5. Branch B — **REVISE**

Branch name: `batch/phase-3d-phase3b-registry-revision-preview-10`
Task name: Phase 3D Phase 3B Registry Revision Re-Preview Batch 10

Apply **only** the supervisor-requested methodological changes, and only after preregistering
them.

Steps:

1. Record the requested changes verbatim in `docs/batch-10-supervisor-decision.md`.
2. Preregister `docs/batch-10-revised-preview-plan.md` stating, for each requested change:
   what it changes, why the supervisor asked for it, what it does *not* change, and how it
   affects identity. Commit before implementing.
3. Implement only what was requested. Do not opportunistically widen scope.
4. Regenerate the preview and produce a **three-way** comparison: Batch 01 current, Batch 09
   preview, Batch 10 revised preview.
5. Re-run the detection policy unchanged and report the status honestly, whatever it is.
6. Keep the canonical registry unchanged unless the supervisor explicitly also approved
   publication. **REVISE alone is not approval to publish.**
7. Produce a fresh decision package for the next meeting.

Likely revision requests and the honest answer to each:

- *"Keep `case_status = ARTIFACT_DISCOVERY_ONLY`."* — Possible. It changes candidate identity
  (the field is in the identity dict) and makes the entry internally less descriptive, but the
  contract permits it. Regenerate and re-report the IDs.
- *"Do not change candidate identity at all."* — Not possible while attaching an evaluation:
  `load_phase_3a_result` requires `evaluation_as_of` to match the result's `as_of`, and
  `evaluation_as_of` is in the identity dict. Document this and ask which constraint to
  relax; do not quietly weaken the loader.
- *"Use different limitation codes."* — Straightforward; identity changes accordingly.
- *"Wait for `PRICE_RANGE` before touching the registry."* — That is effectively Branch C.

---

## 6. Branch C — **DO NOT PROCEED**

Branch name: `batch/phase-3d-phase3b-decision-record-10`
Task name: Phase 3D Supervisor Decision Record Batch 10

Leave the registry unchanged and document the decision.

Steps:

1. Record the decision and the stated reasons verbatim in
   `docs/batch-10-supervisor-decision.md`.
2. Assert — with a committed test — that the canonical Phase 3B registries remain
   byte-identical to the hashes in Section 2.
3. Write `docs/batch-10-completion-report.md` stating that the Batch 09 preview stands as an
   unexecuted proposal, that Phase 3A evaluations remain frozen and referenced only in the
   private preview, and that Phase 3B remains registry-only for these 13 cases.
4. Do **not** delete the Batch 09 preview, its fixtures, or its documentation. A rejected
   proposal is evidence and must be retained.
5. Write `docs/batch-11-fresh-session-handoff.md` describing what would unblock the two real
   barriers (absolute-price semantics for `PRICE_RANGE`; a lawful forward-window source or a
   non-weekend boundary cohort for outcomes).
6. Run one authoritative final full suite.

---

## 7. Frozen cohort (all branches)

Source order — never re-sorted, never re-membered:

`XNCR, PESI, SLS, ZNTL, GPRE, SSPC, LBGJ, TRVI, LMNX, MGNX, BHVN, OBE, AVTX`

Case IDs `BATCH01_<SYMBOL>_20260718`. Frozen boundary `2026-07-18T13:37:55.017661Z`.

Never change: case membership, source order, case IDs, identities, frozen boundaries, original
discovery provenance, Batch 01 eligibility, Batch 01 registry provenance, or outcome state.

---

## 8. Binding constraints (all branches)

- Schema stays `1.0.0`.
- Outcome state stays incomplete. The Batch 05 `FROZEN_FORWARD_24H` responses are **not** valid
  forward-outcome evidence (weekend boundary; IBKR returned previous-Friday bars).
- No forward OHLCV read. No outcome access. No new market-data request. No IBKR connection. No
  network. No `ibapi`.
- `PRICE_RANGE` policy unchanged; no substitution of `PERCENTAGE_CHANGE_MINIMUM` for it.
- Detection and outcome policies unchanged.
- Phase 3A results and thresholds unchanged.
- No score, rank, rule weighting, ML, predictive validation, new Phase 3C empirical analysis,
  backtest, P&L, alert, trade recommendation, paper trade, or live trade.
- **Phase 3E remains unstarted.**

---

## 9. True stop conditions

Stop and report without improvising if: the Batch 09 checkpoint differs; the baseline cannot
be reproduced; prior canonical artifacts are unexpectedly modified; Batch 05 or Batch 08
private hashes fail; the Batch 09 preview no longer regenerates byte-identically; a produced
revised candidate ID differs from the approved preview ID; the recorded decision is absent,
ambiguous, or contradicts itself; executing the decision would require outcome access, forward
OHLCV, a Phase 3A change, a policy change, or Phase 3E.

---

## 10. Required deliverables (all branches)

`docs/batch-10-supervisor-decision.md` (verbatim decision, governance metadata only),
a preregistered plan committed before implementation, a test-and-verification report,
`docs/batch-10-completion-report.md`, and `docs/batch-11-fresh-session-handoff.md`.

Report the exact final HEAD. Then stop.
