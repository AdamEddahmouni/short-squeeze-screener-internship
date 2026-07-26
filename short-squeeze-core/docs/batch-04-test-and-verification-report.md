# Batch 04 — Test and Verification Report

## Baseline (Batch 03 final, before Batch 04)

```
2,056 passed
1 skipped
0 failed
```

Reproduced from a fresh basetemp with authoritative counts via JUnit XML
(2,057 collected − 1 skipped = 2,056 passed).

## Final (Batch 04)

```
2,126 passed
1 skipped
0 failed
```

70 new tests were added (2,127 collected − 1 skipped). The single skip is the
pre-existing environment skip carried over from the baseline; no Batch 04 test is
skipped.

## New test files

- `tests/acquisition/test_batch04.py` — generation determinism, template validity
  and completeness, no real case IDs, no credential-like values, no
  outcome/prediction tokens, reason-code troubleshooting coverage, operator
  checklist coverage, determinism anchors, fixture metadata, submission-kit
  manifest, and Batch 01/02/03 fixture-unchanged guard.
- `tests/acquisition/test_batch04_preflight.py` — synthetic-valid passes preflight,
  report field completeness, constant-false booleans, ready-flag semantics, explicit
  nulls, no absolute path in identity, raw byte-identity before/after preflight,
  hash/byte-length correctness, LF-vs-CRLF hash divergence, preflight determinism,
  no case-registry inputs, every executed invalid scenario is not-ready, key reason
  codes, documented-scenario coverage, and absolute-path rejection at load.
- `tests/acquisition/test_batch04_cli.py` — hash, preflight, preflight-report
  (byte-identical, matches committed fixture), raw never overwritten, and
  submission-kit-generate byte-identity.
- `tests/acquisition/test_batch04_documentation.py` — required docs and operator-kit
  files exist; completion-report scope boundary; security/credential/network/
  entitlement boundary; preflight statuses; Batch 05 conditional next task.

## Verification performed

1. Verified starting branch `batch/phase-3d-local-historical-bar-intake-03` and HEAD
   `1c3b9329ea63fbfffe68281542bdf692170d50fc`, clean status (only the pre-existing
   untracked `docs/phase-3c-complete-handoff.md`), no remotes, tag
   `phase-1-rc1 -> f903d4d144d3f7e9717b1ab8e684da406d7968fb`.
2. Verified archived parent (`0897562e05d75b812dd284de81dfafdfa1dea916`) and nested
   submodule (`6dbefd1a6b271bfc48106c4aa002f211735551cd`) unchanged and clean.
3. Reproduced the baseline via JUnit XML.
4. Recorded Batch 01/02/03 fixture digests.
5. Generated the kit twice and compared bytes (identical).
6. Ran every new CLI twice and compared bytes (identical); the preflight report
   matches the committed fixture byte-for-byte.
7. Regenerated committed fixtures and compared exactly.
8. Ran focused Batch 04 tests, the acquisition suite, isolation and documentation
   tests, and the full suite with a fresh basetemp.
9. Confirmed Batch 01/02/03 fixtures and archived evidence unchanged.
10. Confirmed no real case ID, no credential-like value, no network access, no
    outcome logic, and no Phase 3A/3B records were introduced.

## Notes

- IANA time-zone data is unavailable in this environment, so `UTC` and explicit
  offsets resolve while named IANA zones resolve as unknown. Ambiguous and
  nonexistent-local-time scenarios are therefore documented (not executed) in the
  invalid-scenario index; the behavior and remediation are still described.
- `.pytest-run-*` basetemps and the `PytestCacheWarning` cache issue are handled with
  `-p no:cacheprovider` and fresh basetemps, matching prior batches.
