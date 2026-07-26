# Phase 3B Progress

Phase 3B implements the additive `squeeze_core.research` package, explicit historical and synthetic case registry, frozen/request-artifact Phase 3A reuse, provisional detection and outcome policies, immutable classification table, batch evaluation, matrices, descriptive summaries, missingness, filtered datasets, canonical JSON/JSONL, fixed CSV, offline CLI commands, deterministic fixtures, and isolation/compatibility guards.

Known incomplete historical symbols (`KLRS`, `LBGJ`, `SG`, `TRVI`, `SLS`) remain explicitly incomplete; conflicted `KLOS` is not silently equated with `KLRS`. No input was fabricated to force completion.

Interpretation limits: small sample, incomplete history, unknown platform status, outcomes do not prove causation, rule frequency is not predictive value, short-pressure data is often absent, public sources may differ from original providers, policies and thresholds are provisional and unoptimized, no statistical validation is claimed, and no P&L or trading simulation is performed.

## Completion verification

The complete fresh-temp suite passes with `1770 passed, 1 skipped`. Dedicated fresh-temp suites pass with research 65, evaluation 50, validation 367, readiness 124, metrics 453, and compatibility 127 tests.

All 38 committed research fixture files are identical before regeneration, after the first generation, and after the second. Independent repeated CLI hashes are:

| Artifact | SHA-256 |
| --- | --- |
| Multi-case batch | `3437165db91152c42f69bf222e83fbb97db54b44429301e1d3add62ed14c321e` |
| Dataset JSON | `55347a6b411fbb628df00edf6865b03c55e3b8509d8aaff29fa8e2d62cf32a82` |
| Dataset JSONL | `7681e769cf905f9ee835f67c81065a1113ad0ad7289ee022122894cc40153657` |
| Dataset CSV | `04a07003d97db46785cdea60fbcd88530a6616bb7f019550d46684adfa5beda4` |
| BIYA earliest batch | `10cf4c12e599214932fb309dbe521c5d78f8483377f2d87f328283909f652605` |
| BIYA latest batch | `8a4a9fa547c8d193dd8ce9415a303d53dcba55495e61f8ca305c1e3c18c2fc61` |

The underlying BIYA research-case anchors are `7558549c6cb8f4a229d42c4a466fc7698eba1cfcd01ad576f941b18c6ef6a8ed` and `6791f8855e0ed82ba78ee567aacf77b84842fcb518f88a5a6be262a99430dad9`. Pre-Phase-3B runtime packages and fixture families remain unchanged from `b7c7394d5fe8ee16bd3bd1482ce218a203162104`.

## Phase 3C handoff note

Phase 3C is an additive consumer of these completed artifacts. It preserves every Phase 3B fixture, manifest, model, identity, and serialized byte; Phase 3B completion totals above remain the Phase 3B record and are not rewritten.
