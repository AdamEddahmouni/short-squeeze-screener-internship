# Phase 2V Progress

Branch `phase/2v-biya-validation-bridge`, based on Phase 2D HEAD
`9406032ab6f2422818e1986f78a60496daae8dd6`.

## Baseline and final

| | Command | Result |
| --- | --- | --- |
| Baseline | `pytest --basetemp=.pytest-run-phase2v-baseline` | 1283 passed, 1 skipped, 0 failed |
| Final | `pytest --basetemp=.pytest-run-phase2v-final` | 1557 passed, 1 skipped, 0 failed |

274 new tests. The single skip is the established IANA timezone-database portability
skip. Totals confirmed via JUnit XML rather than the terminal summary line.

## What was added

```text
src/squeeze_core/validation/          16 modules, additive
tests/validation/                     11 test modules
tests/fixtures/validation/            4 fixtures
scripts/generate_phase_2v_anchors.py  anchor generator
apps/biya-validation-demo/            static demonstration
docs/                                 9 documents, 4 ADRs
```

No prior-phase module, fixture, anchor, or serialized byte was modified. Schema remains
`1.0.0`.

## Determinism

- Anchor manifest regenerated 3× — byte-identical.
- `build-candidate-validation` run 3× — byte-identical stdout.
- `export-validation-demo` run 3× — byte-identical stdout.
- Demo payload regenerated — byte-identical.
- One hash collision, expected and documented: `mixed_phase_2v_output` equals
  `serialized_phase_2v_collection` because canonical JSON array serialization *is* the
  concatenation of element bytes. Phase 2C and 2D record the same property.

## Findings that changed the design mid-phase

Four issues surfaced by exercising the code, each fixed at the source rather than worked
around in a test:

1. **Detection windows were widened by irrelevant artifacts.** Treating every artifact's
   mtime as a bound let the advisor email — which never mentions BIYA — push the window
   a full day past the log's last write. Added `bounds_detection_event` so whether an
   artifact constrains a *particular* candidate's detection is an explicit provenance
   fact.
2. **Replay reported no eligible observations.** Eligibility was derived from a coverage
   snapshot scoped to an operation's required domains, so it was empty whenever no
   operation was named. Now taken from the evidence bundle.
3. **`AMBIGUOUS` could not carry a value.** Ambiguity is about a value's meaning or unit,
   not its absence.
4. **Two differing strings compared `INCOMPARABLE`.** Timestamps and headlines are
   perfectly comparable; `INCOMPARABLE` is now reserved for types that cannot be lined up.

A fifth was caught by git rather than by a test: the generator wrote CRLF on Windows
while `.gitattributes` stores LF, and two anchors hash file bytes — so those anchors
would have failed on any fresh checkout. Fixed by writing bytes directly.

## Prior-phase guards touched

Two, neither weakened on net:

- `test_phase_2d_isolation.py` — the additive-package guard now recognises
  `squeeze_core/validation` alongside `squeeze_core/readiness`. Pre-existing packages are
  still asserted unchanged by the neighbouring test.
- `test_phase_1_isolation.py` — the raw-text strategy scan skips the validation package,
  which must name `squeeze_score`, `backtest`, and `recommendation` in docstrings and
  descriptive data to *describe and disclaim* them. Compensated by a new AST scan of
  actual identifiers across every module, which prose cannot trip.

## Case outcome

| | |
| --- | --- |
| Detection time | `BOUNDED_TIME_WINDOW`, 2026-07-17T14:23:58Z – 16:54:58Z (2h31m) |
| Original values recovered | 0 of 12 — all `UNKNOWN` |
| Replays | 2 (both window edges), both returning no eligible evidence |
| Field comparisons | 0 — impossible without an original value |
| Rules classified | 7 of 7 |
| Outcome windows measured | 0 of 7 |
| Conclusion | `INSUFFICIENT_EVIDENCE` |
| Case status | `BLOCKED_MISSING_ORIGINAL_OUTPUT` |

## Deliberate deviations

1. **Rules reconstructed from `b016d92f`, not the archived HEAD.** The archived checkout
   post-dates the meeting by 2h53m and contains a redesigned classifier that did not
   exist at detection. Evidence overrides the literal instruction to read the archived
   repositories. See ADR 0041.
2. **No public market data was fetched.** The phase stays offline and deterministic; the
   gap is recorded in the acquisition manifest. An outcome could not have validated this
   case anyway — see ADR 0042.
3. **Only BIYA has a case.** KLRS, LBGJ, SG, TRVI, and SLS are registered
   `ARTIFACT_DISCOVERY_ONLY` with acquisition needs, because the log preserves no value
   for any of them. Cases were not fabricated to reach a count.
4. **The validation package was committed as one `feat` commit** rather than the seven
   suggested, because `__init__.py` makes intermediate splits non-importable. Tests, CLI,
   demo, fixes, and docs are separate commits.
5. **The brief's premise could not be verified.** The reported advisor message about BIYA
   squeezing is not in the workspace, and the only recorded statements about BIYA are
   contrary. Recorded as a finding, not treated as a defect in the brief.

## Not deployed

The Vercel CLI is installed but not authenticated (`The specified token is not valid`).
Nothing was published and no URL is claimed. `apps/biya-validation-demo/` is
deployment-ready and its README carries the exact commands; deploying requires the user's
own authenticated session.

## Out of scope, confirmed absent

No composite score, ranking, Prime/Subprime label, recommendation, buy/sell signal,
entry/exit logic, stop, target, P&L, portfolio simulation, alert, generalized backtest,
live provider connection, database persistence, authentication, paper trading, or live
trading. Asserted by isolation tests and by serialized-key scans over every result model.

Phase 3A is not started.
