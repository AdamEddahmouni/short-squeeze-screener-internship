# Batch 14 Test and Verification Report

Baseline (after the eleven provider commits, before implementation):

- 2,555 passed;
- 1 skipped;
- 0 failures;
- 0 errors;
- 316.18 seconds;
- JUnit: `.pytest-run-b14-implementation-baseline-3/baseline.xml`.

Focused verification:

- 109 tests passed across methodology, API/deployment, packaging, dashboard contracts,
  current-screen behavior, current guards, and meeting-demo smoke.

Manual smoke:

- local `run_screener.ps1`: passed;
- startup: 1,273 ms;
- current candidate and provider refresh: 34,480 ms;
- comparison ready: 34,542 ms;
- five detail comparison rows: present;
- frozen export: 13 rows;
- cloud-mode headless browser: passed;
- browser console errors: 0;
- response secret markers: 0.

Offline benchmark:

- frozen demo load: 0.556 ms;
- methodology projection, 3 candidates: 1.032 ms;
- methodology detail: 0.497 ms;
- cloud start to health: 15.113 ms;
- health: 25.899 ms;
- readiness: 1.465 ms;
- comparison response, 3 rows: 16.209 ms;
- methodology API detail: 1.851 ms;
- frozen response, 13 rows: 1.091 ms.

Authoritative final suite:

- tests: 2,588;
- passed: 2,587;
- skipped: 1;
- failures: 0;
- errors: 0;
- duration: 158.287 seconds;
- JUnit: `.pytest-run-b14-independent-final-2/batch14-final.xml`.

An earlier final-path attempt was invalidated by Windows denying creation under `C:\tmp`
before JUnit could be written. The first valid workspace-path run found three
compatibility-guard failures; those narrow fixes were committed and the authoritative
run above is the required post-change rerun.

Frozen research remains exactly 97 PASS / 20 FAIL / 208 UNKNOWN.
