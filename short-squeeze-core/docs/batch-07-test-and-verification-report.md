# Batch 07 — Test and Verification Report

## Baseline and final test totals

| run | tests | passed | skipped | failed | errors |
|-----|-------|--------|---------|--------|--------|
| Baseline (checkpoint `ae1aa4e`) | 2228 | 2227 | 1 | 0 | 0 |
| Final (Batch 07) | 2257 | 2256 | 1 | 0 | 0 |

29 tests added (`tests/acquisition/test_operation_readiness.py`); the single pre-existing
skip is unchanged. Authoritative counts from JUnit XML.

## Dedicated coverage (all passing)

- **Global preflight isolation** — report echoes `PREFLIGHT_REJECTED` /
  `global_preflight_unchanged=True`; a static test asserts no
  `squeeze_core.evaluation` / `squeeze_core.research` import anywhere in the
  `operation_readiness` package.
- **Price/volume independence** — `PERCENTAGE_RETURN` declares no volume dependency; a
  split-adjusted ratio is `ADMISSIBLE_WITH_CONSTRAINTS`; `ABSOLUTE_RETURN` blocks
  (`PRICE_ABSOLUTE_LEVEL_CORPORATE_ACTION_UNCONFIRMED`); `RELATIVE_VOLUME` blocks on all
  three unresolved volume fields; resolving only the unit still blocks; toggling the
  provider-filter flag toggles only the stationarity reason.
- **No magnitude / lot inference** — the admissibility context exposes no
  volume-magnitude, lot, or shares field.
- **Timestamp uncertainty** — edge cases at boundary − 61/−60/−59/0 s;
  envelope does not mutate the timestamp; straddle ⟹ `BLOCKED_ALIGNMENT`.
- **Session dependency** — a session-completeness op blocks unless evidenced.
- **OHLCV / outcome isolation** — the manifest guard raises `OhlcvAccessError` on any
  `raw/` path, `.csv`, `.jsonl`, or non-manifest file; forward artifacts are exposed by
  identity only; `CaseOperationReadiness` and `OperationReadinessReport` carry no
  outcome/score/rank/recommendation field.
- **25-rule audit** — the matrix covers exactly the 25 policy `enabled_rule_ids`; every
  status is from the admissibility vocabulary and none is PASS/FAIL; the six market-bar
  rules resolve as designed.
- **Request readiness** — all 13 cases `PHASE3A_REQUEST_READY`; the determination is pure
  (a missing-identity case yields `PHASE3A_REQUEST_BLOCKED`); nothing is executed.
- **Association / determinism** — 13 cases in frozen source order; association and
  deterministic ids stable across two builds; boundary id recomputation stable; schema
  `1.0.0`; generator byte-identical across two runs and equal to the committed golden JSON
  and Markdown.
- **Coverage from provenance only** — observed coverage, final-bar completion, and the
  49,075 s weekend gap derived from manifest metadata.

## Integrity gates

| gate | result |
|------|--------|
| Checkpoint (branch/HEAD) | verified `ae1aa4e…` at start |
| Baseline reproduced | 2227 passed / 1 skipped / 0 failed |
| Prior committed bytes unchanged | `git diff --name-status ae1aa4e..HEAD` = additions only (no M/D) |
| Batch 05 private raw hashes | `verify-private-batch`: 26 artifacts, 0 mismatches |
| Forward artifacts | referenced by filename/sha/byte-length only; OHLCV never opened (guard + tests) |
| Archived topology | parent `0897562e…`, submodule `6dbefd1a…` unchanged |
| No new market data / network / ibapi | none; package imports no `ibapi`, opens no socket |
| No outcome access | no forward OHLCV read; no returns/thresholds computed |
| Schema | remains `1.0.0` |
| Determinism | canonical JSON + Markdown byte-identical across two regenerations |

## Commands (from repo root)

```bash
python -m pytest -q -p no:randomly --basetemp=<scratch>/full --junitxml=<scratch>/junit.xml
python -m tools.ibkr_historical_export verify-private-batch
python scripts/generate_batch07_operation_readiness_outputs.py
```
