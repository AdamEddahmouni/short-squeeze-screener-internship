# Phase 2V Test Plan

Tests live under `tests/validation/`, mirroring the layout of `tests/readiness/`.
Fixtures live under `tests/fixtures/validation/`. No test requires network access, a
database, credentials, or wall-clock time.

## 1. Fixture provenance discipline

Every fixture is classified, and the classification is asserted:

| Class | Meaning | Use |
| --- | --- | --- |
| `LOCAL_RECORDED_ARTIFACT` | Byte-faithful local evidence | Not used — all local evidence is sensitive |
| `SANITIZED_LOCAL_ARTIFACT` | Real local evidence, credentials/paths redacted | BIYA artifacts, detection-time evidence, original rules |
| `SANITIZED_REPRESENTATIVE_SAMPLE` | Structurally real, values generalized | Comparison-case manifest |
| `SYNTHETIC_EDGE_CASE` | Constructed to exercise a branch | Outcome windows, replay lifecycle, conflict cases |

A synthetic artifact is **never** classified as recorded. A test asserts that every
fixture claiming `SANITIZED_LOCAL_ARTIFACT` traces to an artifact id present in
`docs/phase-2v-biya-artifact-inventory.md`, and that no fixture byte matches the
redacted Finviz credential pattern.

## 2. Artifact provenance (14 cases)

Direct platform record; derived platform record; filesystem-metadata-only; user
recollection; unknown provenance; stable content hash across reads; stable artifact id;
**absolute local path rejected by canonical serialization**; **`sensitive=True`
artifact absent from public export**; duplicate artifact detection by content hash;
same content at two paths yields two provenance entries but one content hash;
unreadable artifact; missing artifact; deterministic ordering under input permutation.

## 3. Detection time (12 cases)

Exact timestamp from a platform record; bounded window from two artifacts; one-sided
lower bound; one-sided upper bound; unknown; conflicting timestamp evidence resolves to
a widened window (never a silent pick); time-zone normalization to UTC;
**filesystem mtime alone never yields `EXACT_TIMESTAMP`**; screenshot time treated as
bounded; email time treated as corroboration only and never as a detection time;
deterministic identity; byte-stable serialization.

The BIYA case is asserted specifically: state `BOUNDED_TIME_WINDOW`, bounds
`2026-07-17T14:23:58Z`–`2026-07-17T16:54:58Z`, both source artifacts present, and the
narrower meeting interval **not** substituted for the surfacing window.

## 4. Original rule reconstruction (15 cases)

Price filter; float filter; relative-volume filter; short-float rule; news rule;
days-to-cover rule; missing-value substitution; **field-label mismatch** (the
`Short Interest (%)` header over a short-float value); provider ambiguity; unit
ambiguity; threshold extraction; duplicate rules; rule present in docs but absent from
code; rule present in code but absent from docs; stable manifest ordering.

A dedicated test asserts the manifest's `source_lines_or_symbol` references resolve
against commit `b016d92f`, not the archived HEAD — guarding the design's most
consequential decision against silent regression.

## 5. As-of replay (17 cases)

Exact-timestamp replay; earliest bounded-window replay; latest bounded-window replay;
future observation excluded; future correction excluded; later correction included in a
later replay; future cancellation excluded; later cancellation included in a later
replay; news published after detection excluded; short-interest publication after
detection excluded; receipt after detection excluded; market bars after detection
excluded; borrow update after detection excluded; input-order invariance; byte
stability across runs; Phase 2D readiness objects reused verbatim;
**no second point-in-time implementation** — asserted by verifying the replay module
imports `build_point_in_time_evidence` and defines no own as-of filtering.

## 6. Field comparison (17 cases)

Exact match; match after unit normalization; different value; different semantics;
original missing; rebuilt unavailable; original default substitution; original
mislabeled; incomparable; unknown; days-to-cover numerator mismatch; days-to-cover
denominator mismatch; short-interest reporting-period mismatch; news-time mismatch;
provider mismatch; stable ordering; deterministic identity.

Semantic guard: short-float percent versus absolute short-interest shares must yield
`DIFFERENT_SEMANTICS`, never `DIFFERENT_VALUE`.

## 7. Rule classification (15 cases)

One per classification (10); same rule with different evidence state yields a different
identity; and four **negative-space** assertions — the serialized entry contains no
`score`, no `rank`, no `recommendation`, and no trading label. The negative tests scan
canonical JSON keys against a forbidden-substring list (`score`, `rank`, `prime`,
`subprime`, `buy`, `sell`, `signal`, `recommend`, `bullish`, `bearish`, `alert`) so a
future field cannot quietly reintroduce one.

## 8. Outcome observation (16 cases)

Positive; negative; flat; maximum observed price; minimum observed price; maximum
return; maximum adverse move; time to maximum; missing evaluation window; halt event
present; no halt event; detection window rather than exact time; **no P&L field**; **no
simulated entry**; **no causal squeeze claim**; deterministic output.

All sixteen run against `SYNTHETIC_EDGE_CASE` fixtures, since no BIYA market data
exists. A separate test asserts the real BIYA outcome observation emits
`VALIDATION_OUTCOME_DATA_INCOMPLETE` for every window and computes no value.

## 9. Case conclusion (12 cases)

One per conclusion (5); exact timestamp with complete evidence; bounded window with
divergent replays; missing original snapshot; missing outcome data; **later evidence
cannot retroactively validate an original decision**; stable deterministic conclusion;
no candidate-quality classification.

The retroactivity test is the important one: a case with no recoverable original values
plus a strongly positive outcome observation must still conclude
`INSUFFICIENT_EVIDENCE`.

## 10. Anchors and determinism

`tests/fixtures/validation/expected_phase_2v_validation_metadata.json` anchors the
twenty required Phase 2V outputs. Anchors are generated at least twice and compared
byte-for-byte. Investigated explicitly: semantically different results sharing a hash;
unknown results with too few identity fields; input-order-sensitive hashes; unstable
artifact ordering; and sensitive local paths leaking into canonical bytes.

Prior-phase anchors are re-verified unchanged against Phase 2D HEAD `9406032a`:
`phase_1_anchor_manifest.json`, `expected_phase_2a/2b/2c_metric_metadata.json`,
`expected_phase_2d_readiness_metadata.json`. Any unexplained change is a blocker, and
no prior hash is ever updated to make a Phase 2V test pass.

## 11. CLI and export

`build-candidate-validation` and `export-validation-demo`: valid input exits 0 with
canonical JSON; invalid input exits nonzero with a structured error on stderr; repeated
runs are byte-identical; output contains no credential, absolute path, or personal
name; and the public export of a case containing a `sensitive=True` artifact omits that
artifact entirely.

## 12. Isolation

Mirroring `tests/readiness`: the validation package imports no HTTP client, provider
SDK, database driver, GUI toolkit, pandas, numpy, scipy, or ML library; contains no
`random`/`uuid4`; and reads no wall clock in any identity path.

## 13. Compatibility

Full suite green at 1283 + new tests, with the one established IANA timezone skip. No
prior-phase module, fixture, or serialized byte changes. Schema stays `1.0.0`.
