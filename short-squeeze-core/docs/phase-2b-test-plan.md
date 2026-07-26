# Phase 2B Test-First Implementation Plan

Companion to `docs/phase-2b-design.md`. Written and committed before any Phase 2B runtime source
change, per handoff §8/§40.

## 1. Test file layout

```
tests/metrics/
├── test_statistics.py              # Decimal population mean/variance/stddev/sqrt utilities
├── test_normalized_models.py       # BaselineStatistics / NormalizedMetricResult / ReturnCountWindow
├── test_normalized_identifiers.py  # deterministic ID stability, non-collision, unavailable-result distinctness
├── test_normalized_selection.py    # volume/return distribution sample selection, target exclusion, point-in-time
├── test_relative_volume.py         # RELATIVE_VOLUME + VOLUME_PERCENT_DEVIATION (required cases §21/§22 of handoff)
├── test_volume_standardization.py  # VOLUME_Z_SCORE (required cases §23)
├── test_return_baselines.py        # MEAN_PERCENTAGE_RETURN_BASELINE + PERCENTAGE_RETURN_STANDARD_DEVIATION_BASELINE (§24/§25)
├── test_return_standardization.py  # PERCENTAGE_RETURN_Z_SCORE (§26)
├── test_normalized_lifecycle.py    # cross-cutting correction/cancellation/no-look-ahead proofs (§11 of design doc)
├── test_normalized_cli.py          # CLI request/response cases (§29)
├── test_normalized_anchors.py      # deterministic anchor manifest regeneration + byte identity
└── test_isolation.py               # extended in place (§14 of design doc), not a new file
tests/compatibility/
└── test_phase_2b_isolation.py      # Phase 1 + Phase 2A anchor/byte-identity, one-directional import check
```

Existing Phase 2A test files (`test_returns.py`, `test_volume_baselines.py`, `test_selection.py`,
`test_models.py`, `test_identifiers.py`, `test_diagnostics.py`, `test_cli.py`,
`test_compatibility.py`, `test_anchors.py`) are **not modified** except `test_isolation.py` (§14 of
the design doc) — every Phase 2A assertion in them must continue to pass unchanged.

## 2. Fixture and helper reuse

`tests/metrics/conftest.py` (`make_bar`, `bar_boundary`, `context`, `bar_record`) is imported as-is
by every new Phase 2B test file — no parallel bar-construction helper is written. Phase 2B request
objects are built directly from Phase 2A `Observation`s the same way `test_volume_baselines.py`
already does.

## 3. Case-by-case coverage (handoff §21–§26 numbering preserved for traceability)

### `RELATIVE_VOLUME` / `VOLUME_PERCENT_DEVIATION` (`test_relative_volume.py`, §21/§22)

One parametrized fixture family covers cases 1–17 (above/below/equal/zero target, zero/missing
baseline, missing target, 3- and 5-sample baselines, current-bar exclusion, accidental target
inclusion, mixed provider/interval/session/unit, partial target). Cases 18–28 (correction/
cancellation before/after receipt for both target and baseline samples, out-of-order, duplicate,
same-boundary conflict) reuse the exact before/after `as_of` pattern from
`test_volume_baselines.py::test_corrected_bar_before_and_after_correction_receipt`. Cases 29–32
(exact Decimal preservation, repeated byte-identical result, no qualitative label anywhere in the
model, no threshold classification) are asserted once against `NormalizedMetricResult.model_fields`
and a `metric_result_hash`-style stable-hash check, mirroring
`test_volume_baselines.py::test_stable_series_and_result_hash_across_two_runs`.

### `VOLUME_Z_SCORE` (`test_volume_standardization.py`, §23)

Cases 1–16 (positive/negative/zero z-score, 2/3/5-sample baselines, insufficient samples, zero
variance, zero-volume retained, missing-volume excluded, exact population variance, exact Decimal
sqrt, deterministic precision, no float conversion, current/future exclusion) are direct unit
tests against `volume_standardization.build_volume_z_score_result`. Cases 17–24 (correction/
cancellation before/after, mixed provider/session/interval/unit rejection) reuse the
`resolve_trailing_window`-level compatibility already proven by Phase 2A's own volume-baseline
tests — Phase 2B re-asserts them at the `VOLUME_Z_SCORE` result level specifically (same
underlying selector, different call site, both must be independently verified per handoff §33).
Cases 25–30 (input-order invariance, repeated serialization invariance, stable baseline-statistics
identity, stable normalized-result identity, no "extreme" classification, no alert threshold) are
asserted against `deterministic_id` stability and `BaselineStatistics`/`NormalizedMetricResult`
field names.

### `MEAN_PERCENTAGE_RETURN_BASELINE` / `PERCENTAGE_RETURN_STANDARD_DEVIATION_BASELINE`
(`test_return_baselines.py`, §24/§25)

Cases 1–14 (2/3-return means, positive+negative mix, zero return retained, `N+1`-bar requirement,
target exclusion, missing close, zero starting close, partial-bar exclusion, correction/
cancellation before/after) exercise `return_baselines.build_return_distribution_statistics`
directly (the shared internal `BaselineStatistics` builder both public metrics read from) plus the
two public wrapper builders. Cases 15–25 (mixed provider/interval/session rejection, explicit
close-to-close policy, out-of-order/duplicate bars, conflicted boundary, future-bar exclusion,
insufficient history, stable ordering, exact Decimal mean) reuse the same `evidence.bars`-level
guarantees Phase 2A's return tests already establish, re-verified at this call site.
`test_return_baselines.py` cases 1–15 of the stddev-specific list (§25: 2/3-return population
stddev, exact variance, exact sqrt, insufficient history, mixed-policy rejection, target exclusion,
future exclusion, stable repeated output, no annualization, no volatility classification) share
fixtures with the mean tests since both read one `BaselineStatistics` object.

### `PERCENTAGE_RETURN_Z_SCORE` (`test_return_standardization.py`, §26)

All 28 required cases map directly to `return_standardization.build_percentage_return_z_score_result`
unit tests: positive/negative/zero z-score, target-equals-mean, zero variance, missing
target/baseline-mean/baseline-stddev, insufficient history, target exclusion, mixed provider/
session/interval/price-field/calculation-policy rejection, correction/cancellation before/after,
future exclusion (target and baseline), input reordering invariance, exact Decimal behavior,
stable ID, stable serialization, and three explicit negative assertions (no momentum
classification, no candidate score, no recommendation) checked against `model_fields` and a
docstring/source-text scan shared with `test_isolation.py`.

## 4. Cross-cutting lifecycle proof (`test_normalized_lifecycle.py`)

One before/after-`as_of` pair per new selector path (not per metric — the underlying mechanism is
identical across metrics that share a selector), proving byte-identical `deterministic_id` and
`metric_result_hash`/`normalized_metric_result_hash` when a correction or cancellation is not yet
available, and a changed value only once it becomes available:

1. `RELATIVE_VOLUME` — target-bar correction before/after receipt.
2. `RELATIVE_VOLUME` — baseline-sample correction before/after receipt.
3. `VOLUME_Z_SCORE` — distribution-sample cancellation before/after receipt.
4. `MEAN_PERCENTAGE_RETURN_BASELINE` — historical-bar correction before/after receipt.
5. `PERCENTAGE_RETURN_Z_SCORE` — target-return-bar cancellation before/after receipt.

## 5. Anchors (`test_normalized_anchors.py`, `scripts/generate_phase_2b_anchors.py`)

Mirrors `scripts/generate_phase_2a_anchors.py` exactly in structure (deterministic `AS_OF`,
synthetic `_daily`/`_bar_record` builders, `build_anchor_results() -> dict[str, object]`, then a
`main()` that hashes each and writes `tests/fixtures/metrics/expected_phase_2b_metric_metadata.json`
with `schema_version`, `anchor_result_order`, and `anchors`). The twenty required anchor names
(handoff §28) are produced by one `build_anchor_results()` function; `test_normalized_anchors.py`
asserts:

- all twenty names present;
- `build_anchor_results()` run twice produces identical hashes for every name (byte-identity);
- regenerated hashes match the committed metadata file exactly;
- the composite `mixed_phase_2b_metric_output` (canonical hash of the sorted-by-name result list)
  and `serialized_phase_2b_metric_collection` (sha256 of concatenated canonical JSON bytes) match;
- `phase_2b_cli_output` (sha256 of `build-market-metrics` stdout for a dedicated
  `tests/fixtures/metrics/phase_2b_cli_demo_bars.jsonl` + `phase_2b_normalized_metric_cases.json`
  spec) is stable across two subprocess invocations and matches the committed value;
- no anchor hash collides with any Phase 2A anchor hash (explicit cross-check against
  `expected_phase_2a_metric_metadata.json`'s `anchors` dict) and no two Phase 2B anchors
  unexpectedly collide with each other (`len(set(anchors.values())) == len(anchors)` after removing
  intentionally-linked composite pairs, mirroring Phase 2A's own
  `mixed_..._sha256 == serialized_..._sha256` coincidence check pattern).

## 6. Fixtures (handoff §27)

```
tests/fixtures/metrics/
├── phase_2b_normalized_metric_cases.json     # CLI spec list, SYNTHETIC_EDGE_CASE
├── phase_2b_cli_demo_bars.jsonl              # CLI input bars, SYNTHETIC_EDGE_CASE
├── expected_phase_2b_metric_metadata.json    # generated by scripts/generate_phase_2b_anchors.py
└── phase_2b_fixture_metadata.json            # provenance declaration, mirrors fixture_metadata.json's shape
```

Both new JSON/JSONL fixtures declare `"fixture_origin": "SYNTHETIC_EDGE_CASE"` per record (matching
the existing `_bar_record()` convention already used throughout `tests/`), contain no credentials,
private URLs, or environment-specific paths, and use the same synthetic `TESTA` symbol / `2026-01`
date range Phase 2A's own fixtures use for continuity. Most of the individually-enumerated edge
cases in §21–§26 remain executable pytest cases (parametrized fixtures inline in the test files
above) rather than duplicated JSON records — `phase_2b_fixture_metadata.json` documents this
choice explicitly, matching the handoff's own "acceptable provided the choice is documented"
allowance (§27).

## 7. CLI tests (`test_normalized_cli.py`, handoff §29)

Valid-request cases (one per new metric family: relative volume, volume z-score, return z-score)
run the actual `python -m squeeze_core build-market-metrics` subprocess against
`phase_2b_cli_demo_bars.jsonl` and assert exit code 0 and a well-formed canonical JSON array.
Invalid-request cases (unsupported metric name/version/standard-deviation-policy, missing `as_of`,
missing target, invalid input file path, insufficient history, zero baseline, zero variance) assert
non-zero exit status and that stderr contains no live-URL, credential, or database string. A
determinism test runs the same request twice and diffs stdout bytes.

## 8. Compatibility tests (`tests/compatibility/test_phase_2b_isolation.py`)

- `tests/fixtures/compatibility/phase_1_anchor_manifest.json` byte-identical to the Phase 2A
  completion commit (`git show d776e30e:tests/fixtures/compatibility/phase_1_anchor_manifest.json`
  compared against the working-tree file, executed as a `subprocess.run(["git", "diff",
  "--exit-code", ...])` inside the test — read-only, no repository mutation).
- `tests/fixtures/metrics/expected_phase_2a_metric_metadata.json` likewise byte-identical to the
  same commit.
- Full Phase 1 + Phase 2A suites (`tests/adapters`, `tests/evidence`, `tests/compatibility`
  excluding the new file itself, `tests/metrics` excluding new Phase 2B files) still pass —
  enforced implicitly by the full-suite run in §9, not re-run in isolation a second time here.
- `Observation.model_fields["schema_version"]` still pins `"1.0.0"` (same assertion pattern as
  Phase 2A's own `test_compatibility.py`, applied once more for defense-in-depth).
- `NormalizedMetricResult`/`BaselineStatistics` define no `schema_version` field (mirrors
  `MetricResult`'s own compatibility test).
- No file under `src/squeeze_core/{contracts,evidence,adapters,replay,serialization}` imports
  `squeeze_core.metrics` (same AST-walk pattern as Phase 2A's `test_compatibility.py`, re-run
  because Phase 2B adds new files to the directory being scanned).

## 9. Isolation tests (extended `test_isolation.py`, handoff §31/§33)

`FORBIDDEN_MODULES`/`FORBIDDEN_CALLS` AST scans are re-run unchanged (they already glob every
`*.py` in `metrics/`, which now includes the six new files automatically).
`FORBIDDEN_IDENTIFIER_SUBSTRINGS` is updated per design-doc §14 (removing `relative_volume`/`rvol`
as forbidden *concepts* while keeping `rvol` itself never emitted; keeping every scoring/trading
substring forbidden). A new substring set specific to Phase 2B is added and scanned the same way:
`squeeze_score`, `is_squeeze_confirmed`, `weekly_volatility`, `annualiz`, `sharpe`, `atr`,
`true_range`, `bollinger`, `ewma`, `percentile`, `median_absolute_deviation`, confirming none of
the explicitly-excluded-from-Phase-2B concepts (§20 of the design doc) leak into source even
incidentally (e.g. via a copy-pasted inherited comment).

## 10. Final verification sequence (handoff §39, executed after all above pass)

1. `pytest --basetemp=.pytest-run-phase2b-final` — full suite, expect prior count (837 passed / 1
   skipped) plus every new Phase 2B test, 0 failed.
2. `pytest tests/metrics --basetemp=.pytest-run-phase2b-metrics`
3. `pytest tests/compatibility --basetemp=.pytest-run-phase2b-compat`
4. `scripts/generate_phase_2b_anchors.py` run twice; diff the two in-memory results (not just the
   committed file) for byte identity before the second run overwrites the file.
5. `build-market-metrics` CLI run twice with identical arguments; diff stdout bytes.
6. `git diff --exit-code d776e30e -- tests/fixtures/compatibility/phase_1_anchor_manifest.json
   tests/fixtures/metrics/expected_phase_2a_metric_metadata.json`
7. Git state checks (`status`, `branch`, `rev-parse HEAD`, `tag --list`, `show phase-1-rc1
   --no-patch`) confirming a clean tree, no remotes, `phase-1-rc1` unchanged.
