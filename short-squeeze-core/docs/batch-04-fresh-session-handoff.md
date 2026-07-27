# Claude Fresh-Session Handoff — After Phase 3D Local Bar Intake (Batch 03)

## Current state

Batch 03 (Phase 3D Local Historical Market-Bar Intake) is complete. A
deterministic, offline, vendor-neutral intake workflow validates user-supplied or
licensed historical bar exports, normalizes supported CSV artifacts into canonical
bars with preserved provenance, and validates a non-executing case-association
mapping. No market data was acquired, no outcome was computed, no Phase 3A/3B
record was created, and **Phase 3E was not started**.

### Repository

- Workspace root: `<repo-root>`
- Implementation repo: `<repo-root>\short-squeeze-core`
- Branch: `batch/phase-3d-local-historical-bar-intake-03`
- Final HEAD: resolve with `git rev-parse HEAD`. It is the Batch 03 finalize
  documentation commit on the branch above (the commit that added this handoff and
  `docs/batch-03-completion-report.md`). Record the full 40-character hash in your
  first report.
- No remotes; do not push, merge, or rebase.

### Known checkpoints

```text
Batch 02 final (Batch 03 start): 06e3a97039a04b7247350bd57ed5f801998fe97b
Batch 03 final:                  resolve with git rev-parse HEAD (this branch)
Phase 3D final: a92906d395e17ee8dff15c69395f0b37427bc66a
Batch 01 final: 37ac03ab196057398f1f6c3463118633316f58f2
phase-1-rc1 tag -> f903d4d144d3f7e9717b1ab8e684da406d7968fb
```

### Expected baseline for the next session

```text
2,056 passed, 1 skipped, 0 failed
```

Reproduce with a fresh basetemp and the cache provider disabled (the Windows
`.pytest_cache` `PytestCacheWarning` is benign):

```bash
.venv/Scripts/python.exe -m pytest -p no:cacheprovider --basetemp=.pytest-run-next -q
```

### Invariants to preserve

- Schema version stays `1.0.0`.
- Batch 01 fixtures unchanged: dir digest
  `a4a6ece91800e215baeb197a6f178505c526d49c672f3274365bde4f624b407a`.
- Batch 02 fixtures unchanged: dir digest
  `eefed973fb1c7e709c52060c274bf57b6d641993ac96e9e08687e75e818e30c4`.
- Batch 03 fixtures under `tests/fixtures/acquisition/batch03/` regenerate exactly
  via `python scripts/generate_batch03_local_bar_intake_outputs.py`.
- Archived parent repo `HEAD 0897562e05d75b812dd284de81dfafdfa1dea916` and
  submodule `HEAD 6dbefd1a6b271bfc48106c4aa002f211735551cd` remain clean.
- The private real-data intake root `intake/local-bars/` is gitignored; never
  commit real user-supplied licensed data without explicit per-file authorization.

## What exists now

- `src/squeeze_core/acquisition/local_bar_intake/` — the intake package.
- `src/squeeze_core/acquisition/batch03.py` + generator script.
- CLIs: `intake-validate-bundle`, `intake-inspect-artifact`,
  `intake-normalize-bars`, `intake-summary`,
  `intake-validate-case-association`.
- Docs `batch-03-*.md` (plan, contract, validation policy, determinism,
  security boundary, case-association boundary, test report, completion report).

## Exactly one recommended next task

**Author a preregistered plan for a separately authorized Batch 04 curation dry
run that consumes a validated intake bundle through the existing non-executing
case-association boundary — still with no outcome capture and no Phase 3B
publication.**

Concretely: design (and only preregister — do not yet implement) a batch that,
given a validated `NormalizedBarSet` plus a `CaseAssociationMapping` whose
`case_id` and `frozen_detection_boundary_id` resolve against the real Batch 01/02
case registry, produces a deterministic *readiness* record describing whether the
bundle's coverage and interval are compatible with the case's requested window —
**without** opening the outcome window, computing any return, creating any Phase
3A/3B record, or promoting any candidate. This extends the case-association
boundary toward real cases while keeping every evidence, leakage, and determinism
rule intact, and it does not begin Phase 3E.

Do not start this task now. Begin the next session by verifying the checkpoint
(branch, full HEAD, clean status, remotes, tag, archived topology) and reproducing
the `2,056 passed, 1 skipped, 0 failed` baseline before writing anything.
