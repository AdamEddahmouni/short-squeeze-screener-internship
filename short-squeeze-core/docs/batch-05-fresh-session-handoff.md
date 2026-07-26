# Claude Fresh-Session Handoff — Batch 05 Real-Bundle Preflight Validation

## Purpose

Continue the short-squeeze research reconstruction project from the completed and
approved Batch 04 checkpoint (the Historical Data Submission Kit and offline
preflight workflow).

Your only authorized next task is:

```
Validate one real user-supplied or licensed historical-bar bundle through the
Batch 04 preflight workflow, without real-case association or outcome capture.
```

Do not start that task until the user has separately supplied a specific file and
explicitly authorized its use for this exact purpose. If no such file and
authorization are present, stop and ask; do not fetch, download, or fabricate data.

This is an operator-assisted validation batch only. It runs the existing offline
preflight against one real bundle and reports readiness. It creates no new intake
semantics, associates no case, computes no outcome, and begins no later phase.

Do not ask routine clarification questions. Inspect the repository, the Batch 03
`local_bar_intake` contracts, and the Batch 04 submission kit first. Resolve ordinary
implementation decisions conservatively from existing code and project policy. Ask
only if a true stop condition below is reached.

---

## 1. Workspace and repository

Workspace root:

```
C:\Users\adame\Desktop\short-squeeze-project
```

Implementation repository:

```
C:\Users\adame\Desktop\short-squeeze-project\short-squeeze-core
```

Archived parent evidence repository (do not modify):

```
C:\Users\adame\Desktop\short-squeeze-project\archived-project-code\adams-short-squeeze-code-archived
```

Archived nested submodule (do not modify):

```
...\adams-short-squeeze-code-archived\app\ScreenerProject
```

The workspace root contains an inert empty `.git` directory. Do not modify, remove,
initialize, clean, or repurpose it. Leave every unrelated untracked file (for
example `docs/phase-3c-complete-handoff.md`) untouched.

Known test-environment issues (unchanged):

- `.pytest_cache` may be unwritable (`PytestCacheWarning: [WinError 5]`); use
  `-p no:cacheprovider`.
- Always use a fresh explicit `--basetemp`; do not use the locked `.pytest-tmp`.
- Do not broadly delete `.pytest-run-*` directories.
- IANA time-zone data is unavailable; prefer `UTC` or explicit offsets in examples.

---

## 2. Exact current checkpoint

Expected current branch:

```
batch/phase-3d-historical-data-submission-kit-04
```

Expected starting full-suite baseline:

```
2,126 passed
1 skipped
0 failed
```

Previous approved checkpoints:

```
Batch 01 final: 37ac03ab196057398f1f6c3463118633316f58f2
Batch 02 final: 06e3a97039a04b7247350bd57ed5f801998fe97b
Batch 03 final: 1c3b9329ea63fbfffe68281542bdf692170d50fc
Phase 3D final: a92906d395e17ee8dff15c69395f0b37427bc66a
Phase 1 rc tag: phase-1-rc1 -> f903d4d144d3f7e9717b1ab8e684da406d7968fb
```

The exact final Batch 04 HEAD is reported in the session that produced this file and
in `docs/batch-04-completion-report.md`.

Before modifying anything, verify and record:

```powershell
git branch --show-current
git rev-parse HEAD
git status --short
git remote -v
git rev-parse phase-1-rc1^{}
git log --oneline -12
```

Verify the archived parent and nested submodule HEADs and clean status without
modifying them. Reproduce the baseline with a fresh basetemp and authoritative JUnit
XML counts. Do not proceed unless the starting-state gates pass.

---

## 3. Completed Batch 04 state

Batch 04 is approved. It implemented, on top of Batch 03:

- `src/squeeze_core/acquisition/historical_data_submission_kit/` — templates,
  synthetic-valid example, operator guides, reason-code troubleshooting, a
  deterministic invalid-scenario index, an operator checklist, an offline preflight
  workflow with a deterministic `PreflightReport`, and SHA-256/byte-length tooling;
- CLI subcommands `submission-kit-generate`, `historical-bar-hash`,
  `historical-bar-preflight`, `historical-bar-preflight-report`;
- the operator kit under `operator-kits/historical-market-bars/`;
- canonical fixtures under `tests/fixtures/acquisition/batch04/`;
- 70 new passing tests; no network, no credentials, no case association, no outcome
  work, no Phase 3A/3B records, no Phase 3E; schema still `1.0.0`.

Preflight statuses: `READY_FOR_FUTURE_ASSOCIATION`, `NOT_READY_QUARANTINED`,
`NOT_READY_REJECTED`. `READY_FOR_FUTURE_ASSOCIATION` means only that the local bundle
passed the current intake and normalization checks — not that data is accurate, the
license is sufficient, a case is covered, an outcome window is complete, or any later
phase may run.

Do not redesign or replace the Batch 03 intake system or the Batch 04 kit. Use them.

---

## 4. Authorized task for Batch 05

If, and only if, the user supplies a specific real historical-bar export and
explicitly authorizes its use:

1. Create a new branch from the Batch 04 final HEAD, e.g.
   `batch/phase-3e-preflight-real-bundle-05` **only if** the user confirms; otherwise
   keep work on a clearly named non-3E branch. Naming does not begin Phase 3E work.
2. Place the file under the git-ignored private intake root
   `intake/local-bars/<bundle>/raw/` — never commit it.
3. Compute its SHA-256 and byte length with `historical-bar-hash`.
4. Author a manifest and mapping profile from the kit templates.
5. Run `historical-bar-preflight` (and `historical-bar-preflight-report`) offline.
6. Report the readiness status, reason codes, and diagnostics to the user.
7. Stop.

Do not associate the bundle with any case, do not compute any outcome, do not create
any Phase 3A/3B record, and do not begin Phase 3E. Do not commit the real export
unless the user explicitly authorizes that exact file.

---

## 5. Standing credential, entitlement, and source rule

Do not: request, access, read, log, or print credentials; log into or create
provider accounts; call provider APIs; scrape; automate downloads; bypass
authentication, rate limits, robots rules, anti-bot systems, or paywalls; execute
archived authentication or impersonation helpers; touch `schwab_tokens.json`; or
redact, rewrite, rotate, or clean credentials as a side task. The software records
the user's entitlement assertion and makes no legal determination. Instruct the user
to supply only exports they are entitled to use.

---

## 6. Explicit forbidden work

No web searching for market data, downloading, API calls, provider integrations,
account creation, credential handling, scraping, authentication/rate-limit/robots/
anti-bot/paywall bypass, real-case association, BIYA or Batch 01/02 association,
outcome capture or calculation, Phase 3A/3B records, Phase 3C expansion, Phase 3E,
predictive validation, scoring, ranking, weighting, threshold tuning, feature
importance, ML, recommendations, alerts, buy/sell language, entry/exit logic, P&L,
backtesting, portfolio/paper/live trading, broker orders, database persistence,
authentication systems, or GUI redesign. Do not change schema version `1.0.0`.

---

## 7. True stop conditions

Stop and report without improvising if: the current branch/HEAD does not match the
Batch 04 checkpoint; the baseline cannot be reproduced (beyond the known cache
warning); Batch 01/02/03/04 canonical artifacts are already modified; the task would
require network access, credentials, modifying archived evidence, real-case
association, outcome access, fabricating provider or entitlement semantics, changing
prior serialized bytes or schema, or beginning Phase 3E; no authorized real file is
supplied; or a required operator instruction would tell the user to violate a source
restriction. Routine implementation decisions are not stop conditions.

---

## 8. Definition of done (Batch 05)

Batch 05 is complete only when the starting checkpoint is verified and the baseline
reproduced; a single real, authorized bundle has been validated offline through the
Batch 04 preflight workflow with its readiness status reported; no case association,
outcome, or later-phase record was produced; no real export was committed without
explicit per-file authorization; prior artifacts and archived evidence remain
unchanged; Phase 3E remains unstarted; and the exact final HEAD is reported.

Do not start this task until a real file is supplied and explicitly authorized.
