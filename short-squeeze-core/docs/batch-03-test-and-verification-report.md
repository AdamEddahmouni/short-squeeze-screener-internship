# Batch 03 — Test and Verification Report

## Baseline

Reproduced the Batch 02 checkpoint before any change:

```text
Branch: batch/phase-3d-outcome-acquisition-02
HEAD:   06e3a97039a04b7247350bd57ed5f801998fe97b
Baseline: 1,993 passed, 1 skipped, 0 failed
```

(Confirmed via JUnit XML: `tests=1994, failures=0, errors=0, skipped=1`.)

## New tests

| file | tests |
|---|---|
| `tests/acquisition/test_local_bar_intake.py` | 40 |
| `tests/acquisition/test_batch03.py` | 13 |
| `tests/acquisition/test_batch03_cli.py` | 7 |
| `tests/acquisition/test_batch03_documentation.py` | 3 |
| **total new** | **63** |

The acquisition isolation guard (`test_isolation.py`) already scans the whole
acquisition package and now covers the new `local_bar_intake` package and
`batch03.py` unchanged.

## Coverage of the required test matrix

- valid CSV bundle accepted; repeated generation byte-identical; committed
  fixture regeneration matches exactly;
- SHA-256 tamper rejected; byte-length tamper rejected; missing artifact rejected;
  non-CSV format rejected;
- malformed manifest raises; missing interval rejected; session-based interval
  unsupported; unknown timezone rejected; ambiguous-timezone reason mapping
  (plus a gated end-to-end when the IANA DB is available); missing timestamp
  semantics; missing/contradictory adjustment semantics;
- invalid OHLC; negative volume; negative trade count; malformed decimal;
  NaN/infinity; missing OHLC never inferred; event time outside coverage; symbol
  and venue mismatch;
- identical duplicates collapsed + quarantined per policy; conflicting duplicates
  rejected; overlapping bars rejected; coverage gap rejected (and allowed under
  `ALLOW_GAPS`); non-monotonic rejected under `REQUIRE_PRESORTED`;
- source-row provenance preserved after stable sort; price-adjustment and session
  semantics preserved on bars; event time distinct from retrieval/export time;
- current-for-historical rejected; synthetic-for-historical rejected; absolute
  path excluded from identity (and rejected at construction);
- case mapping requires known case + boundary IDs; mapping never computes an
  outcome and never creates Phase 3A/3B records; incompatible symbol/interval
  detected;
- Batch 01 and Batch 02 fixture directory digests unchanged; no credential-like
  values in any fixture; no outcome/prediction tokens leak into outputs.

## Determinism verification

- `build_batch03_documents()` twice → byte-identical.
- `scripts/generate_batch03_local_bar_intake_outputs.py` writes
  `build/acquisition/batch-03/`; all 15 documents byte-identical to the committed
  `tests/fixtures/acquisition/batch03/` copies.
- All five CLIs run twice → byte-identical; `intake-normalize-bars` output matches
  the committed `normalized-bars.jsonl` / `normalized-bars.csv` exactly.
- All generated documents contain no CR/CRLF.

## Compatibility verification

- Batch 01 fixture digest: `a4a6ece91800e215baeb197a6f178505c526d49c672f3274365bde4f624b407a` (unchanged).
- Batch 02 fixture digest: `eefed973fb1c7e709c52060c274bf57b6d641993ac96e9e08687e75e818e30c4` (unchanged).
- Archived parent repo `HEAD 0897562e05d75b812dd284de81dfafdfa1dea916`, clean.
- Archived submodule `HEAD 6dbefd1a6b271bfc48106c4aa002f211735551cd`, clean.
- Schema version remains `1.0.0`.

## Final full suite

```text
2,056 passed, 1 skipped, 0 failed   (+63 over the 1,993 baseline)
```

Run with a fresh `--basetemp`; the only known-benign warning is the
`.pytest_cache` `PytestCacheWarning` on Windows (mitigated with
`-p no:cacheprovider`).
