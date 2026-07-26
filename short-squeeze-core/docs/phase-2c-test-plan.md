# Phase 2C Test-First Implementation Plan

Companion to `docs/phase-2c-design.md`. Written and committed before any Phase 2C runtime
source change, per handoff §8/§40.

## 1. Test file layout

```
tests/metrics/
├── test_source_age.py                # SourceAgeMetadata construction, both age concepts kept separate
├── test_pressure_models.py           # PressureMetricResult / DaysToCoverComponents field/validator shape
├── test_pressure_identifiers.py      # deterministic ID stability, non-collision, unavailable-result distinctness
├── test_pressure_selection.py        # short-interest period resolution, revision/cancellation/conflict, borrow boundary resolution, point-in-time gates
├── test_short_interest_changes.py    # ABSOLUTE_CHANGE + PERCENTAGE_CHANGE (required cases §23 of handoff)
├── test_short_interest_revision_delta.py  # REVISION_DELTA (required cases §24)
├── test_days_to_cover.py             # DAYS_TO_COVER_COMPONENTS + DAYS_TO_COVER (required cases §25)
├── test_borrow_fee_changes.py        # BORROW_FEE_ABSOLUTE_CHANGE + _RELATIVE_PERCENTAGE_CHANGE (§26)
├── test_borrow_availability_changes.py    # BORROW_AVAILABILITY_ABSOLUTE_CHANGE + _PERCENTAGE_CHANGE (§27)
├── test_pressure_lifecycle.py        # cross-cutting revision/cancellation/no-look-ahead proofs (§12 of design doc)
├── test_pressure_cross_domain.py     # §28 of handoff: days-to-cover unit/provider isolation, no cross-domain substitution
├── test_pressure_cli.py              # CLI request/response cases (§31 of handoff)
├── test_pressure_anchors.py          # deterministic anchor manifest regeneration + byte identity (§30)
└── test_isolation.py                 # extended in place (§14 of design doc), not a new file
tests/compatibility/
└── test_phase_2c_compatibility.py    # Phase 1 + Phase 2A + Phase 2B anchor/byte-identity, one-directional import check
```

Every existing `tests/metrics/*.py` and `tests/compatibility/*.py` file is **not modified**
except `test_isolation.py` (§14 of the design doc) — every prior assertion in them must
continue to pass unchanged.

## 2. Fixture and helper reuse

New helpers live in `tests/metrics/conftest.py` (extended additively): `make_short_interest`
(wraps `normalize_finra_short_interest_record`), `make_borrow_fee`/`make_borrow_availability`
(wrap `normalize_ibkr_borrow_record`), and `make_daily_bar` (thin wrapper already implied by
existing bar-fixture helpers, reused for `DAYS_TO_COVER`'s volume half exactly as
`test_volume_baselines.py` already builds bars). No parallel FINRA/IBKR record-construction
helper is written outside `conftest.py` — every new test file imports these fixtures.

## 3. Case-by-case coverage (handoff §23–§27 numbering preserved for traceability)

### `PUBLISHED_SHORT_INTEREST_ABSOLUTE_CHANGE` / `_PERCENTAGE_CHANGE` (`test_short_interest_changes.py`, §23)

All 29 required cases map directly to `short_interest_changes.build_short_interest_change_result`
unit tests: positive/negative/zero absolute and percentage change, zero starting denominator,
missing starting/ending value, starting/ending record unavailable at `as_of`, publication-
after-`as_of`, receipt-after-`as_of`, explicit starting/ending reporting period, reversed
periods (`PRESSURE_METRIC_START_AFTER_END`), same period supplied twice
(`PRESSURE_METRIC_IDENTICAL_INPUT`), mixed providers (rejected — provider is single and
explicit per §11), explicit provider selection, mixed units (structurally unreachable per
§13 — asserted as "no such diagnostic is ever emitted" rather than skipped), duplicate
records, same-period conflict, out-of-order inputs, deterministic input reordering, exact
`Decimal` behavior, availability-age/reporting-period-age/publication-lag metadata present
on `starting_source_age`/`ending_source_age`, and a `model_fields` scan proving no
qualitative pressure label exists on the result.

### `PUBLISHED_SHORT_INTEREST_REVISION_DELTA` (`test_short_interest_revision_delta.py`, §24)

All 16 required cases against `short_interest_changes.build_short_interest_revision_delta_result`:
positive/negative/zero delta, revision unavailable before publication, revision unavailable
before receipt, original+revision same reporting period (the only shape this metric accepts
— enforced by construction, not a separate check), different reporting periods rejected
(structurally impossible since the request takes one period, not two — asserted as a request-
shape test, not a runtime rejection), explicit revision link, missing revision link,
cancellation-is-not-a-revision, duplicate-is-not-a-revision, same-ID-changed-content
(conflict, not revision), historical metric before revision unchanged, metric after revision
uses the eligible revised record, stable deterministic ID, stable serialization.

### `DAYS_TO_COVER_COMPONENTS` / `DAYS_TO_COVER` (`test_days_to_cover.py`, §25)

All 33 required cases against `days_to_cover.build_days_to_cover_components` and
`days_to_cover.build_days_to_cover_result`: 3-sample and 5-sample valid calculations, exact
`Decimal` division, zero/missing volume baseline, insufficient volume history (surfaced via
the reused `VOLUME_BASELINE_INSUFFICIENT_SAMPLES`/`VOLUME_BASELINE_WINDOW_EMPTY`
diagnostics, §13 of the design doc), zero/missing short interest, incompatible volume
interval (`DAYS_TO_COVER_INCOMPATIBLE_VOLUME_INTERVAL` when a non-daily interval is
requested), mixed volume providers rejected, explicit volume provider, mixed sessions
rejected (reuses `resolve_trailing_window`'s own session filtering — a session outside
`volume_session_scope` is excluded upstream, never seen as a "mixed session" candidate),
current/future target-adjacent bar exclusion (`exclude_current_bar=True` against
`target_start=as_of`), corrected/cancelled volume sample before/after correction receipt,
original/revised/cancelled short-interest record before/after availability, publication lag
preserved, reporting-period age preserved, availability age preserved, supporting
short-interest observation ID, supporting volume observation IDs, supporting volume-baseline
metric ID, stable component-model identity, stable final-metric identity, input-reordering
invariance, and a `model_fields`/output-text scan proving no high/low or squeeze
interpretation exists anywhere in either model.

### `BORROW_FEE_ABSOLUTE_CHANGE` / `_RELATIVE_PERCENTAGE_CHANGE` (`test_borrow_fee_changes.py`, §26)

All 21 required cases against `borrow_fee_changes.build_borrow_fee_change_result`: positive/
negative/zero absolute (percentage-point) change, positive/negative/zero relative
(percentage) change, zero starting denominator, missing starting/ending fee, explicit zero
fee, mixed providers rejected, mixed units (structurally unreachable — `annualized_fee_percent`
is always normalized to one unit before this file ever sees it, §13), percentage-vs-
percentage-point distinction (`unit` differs between the two metric names, never a flag),
starting/ending record unavailable at `as_of`, out-of-order inputs, duplicate record,
conflict record, exact `Decimal` behavior, stable deterministic result, and a `model_fields`/
diagnostic-code scan proving no hard-to-borrow classification exists anywhere in the result
or diagnostics (`payload.hard_to_borrow` is read by no Phase 2C code path — asserted via a
source-text check mirroring `test_isolation.py`'s own pattern).

### `BORROW_AVAILABILITY_ABSOLUTE_CHANGE` / `_PERCENTAGE_CHANGE` (`test_borrow_availability_changes.py`, §27)

All 21 required cases against `borrow_availability_changes.build_borrow_availability_change_result`:
positive/negative/zero absolute change, positive/negative/zero percentage change, zero
starting denominator, missing starting/ending availability, explicit zero availability,
mixed providers rejected, mixed units (structurally unreachable, same reasoning as fee),
mixed scope (IBKR has no venue/scope field at all, §2.7 of the research brief — asserted as
"no scope field exists to mix," not a runtime rejection), starting/ending record unavailable
at `as_of`, out-of-order inputs, duplicate record, conflict record, exact arithmetic, stable
deterministic result, and a `model_fields` scan proving no tightening/loosening
classification exists.

## 4. Cross-cutting lifecycle proof (`test_pressure_lifecycle.py`)

One before/after-`as_of` pair per resolver path, proving byte-identical `deterministic_id`
and a stable `canonical_hash` when a revision/correction/cancellation is not yet available,
and a changed value only once it becomes available (mirrors
`test_normalized_lifecycle.py`'s exact shape):

1. `PUBLISHED_SHORT_INTEREST_ABSOLUTE_CHANGE` — ending-period revision before/after
   publication receipt.
2. `PUBLISHED_SHORT_INTEREST_REVISION_DELTA` — revision before/after availability.
3. `PUBLISHED_SHORT_INTEREST_ABSOLUTE_CHANGE` — ending-period cancellation before/after
   receipt.
4. `DAYS_TO_COVER` — short-interest revision before/after availability.
5. `DAYS_TO_COVER` — volume-sample correction before/after receipt.
6. `DAYS_TO_COVER` — volume-sample cancellation before/after receipt.
7. `BORROW_FEE_ABSOLUTE_CHANGE` — later-arriving fee observation does not change an
   earlier-`as_of` result (IBKR has no revision concept, so this proves ordinary point-in-time
   exclusion, not lifecycle resolution).
8. `BORROW_AVAILABILITY_ABSOLUTE_CHANGE` — same shape as 7.

## 5. Cross-domain compatibility (`test_pressure_cross_domain.py`, handoff §28)

- `DAYS_TO_COVER` combines only `SHARES`-unit short interest with `SHARES`-unit volume; no
  implicit conversion path exists to test against (asserted by source-text absence, not a
  runtime case, since no conversion code exists to exercise).
- `short_interest_provider` and `volume_provider` are recorded as two separately-named
  fields on `DaysToCoverComponents` and never coalesced into one `provider` field.
- A stale short-interest numerator (`reporting_period_age_days` large) still produces a
  `KNOWN_VALUE` result — age is metadata, not a gate; explicit test with a deliberately old
  settlement date and a fresh `as_of`.
- Recent volume does not change `short_interest_source_age`'s reported age — the two ages are
  computed independently from their own observations, never blended.
- `payload.short_float_percent` (a different FINRA field) is never read by
  `PUBLISHED_SHORT_INTEREST_ABSOLUTE_CHANGE`/`DAYS_TO_COVER` — only `payload.short_shares`.
- Phase 2A's `MEAN_VOLUME_BASELINE`/Phase 2B's `RELATIVE_VOLUME` are never used as a
  days-to-cover denominator substitute — `DAYS_TO_COVER` only ever constructs its own
  `MEAN_VOLUME_BASELINE`-shaped `MetricResult` internally (§8.3 of the design doc); a test
  asserts the internally-constructed result's `calculation_policy_version` matches Phase 2A's
  own `"trailing_mean_exclude_current.v1"` for the reused arithmetic, proving no divergent
  parallel volume-averaging formula was introduced.
- `payload.hard_to_borrow`/`payload.days_to_cover` (FINRA's own provider-published
  days-to-cover) are never read by any Phase 2C builder — source-text absence check.

## 6. Fixtures (handoff §29)

```
tests/fixtures/metrics/
├── phase_2c_short_interest_records.jsonl   # FINRA-shaped provider records, SYNTHETIC_EDGE_CASE
├── phase_2c_borrow_records.jsonl           # IBKR-shaped provider records, SYNTHETIC_EDGE_CASE
├── phase_2c_daily_volume_bars.jsonl        # MARKET_BAR-shaped provider records for DAYS_TO_COVER, SYNTHETIC_EDGE_CASE
├── phase_2c_metric_cases.json              # CLI spec list
├── expected_phase_2c_metric_metadata.json  # generated by scripts/generate_phase_2c_anchors.py
└── phase_2c_fixture_metadata.json          # provenance declaration, mirrors phase_2b_fixture_metadata.json's shape
```

All new JSONL/JSON fixtures declare `"fixture_origin": "SYNTHETIC_EDGE_CASE"` per record, use
synthetic symbols (`TESTA`/`TESTC`), contain no credentials, account identifiers, private
URLs, or environment-specific paths. Most individually-enumerated edge cases in §23–§27 remain
executable pytest cases (parametrized fixtures inline in the test files above) rather than
duplicated JSON records — `phase_2c_fixture_metadata.json` documents this choice explicitly,
matching the handoff's own "acceptable provided the choice is documented" allowance (§29).

## 7. Deterministic anchors (`test_pressure_anchors.py`, `scripts/generate_phase_2c_anchors.py`)

Mirrors `scripts/generate_phase_2b_anchors.py` exactly in structure (deterministic `AS_OF`,
synthetic FINRA/IBKR/bar record builders, `build_anchor_results() -> dict[str, object]`, then
a `main()` that hashes each and writes
`tests/fixtures/metrics/expected_phase_2c_metric_metadata.json` with `schema_version`,
`anchor_result_order`, and `anchors`). The required anchor names (handoff §30):

```
positive_short_interest_absolute_change, negative_short_interest_absolute_change,
positive_short_interest_percentage_change, negative_short_interest_percentage_change,
positive_short_interest_revision_delta, negative_short_interest_revision_delta,
three_sample_days_to_cover, five_sample_days_to_cover, days_to_cover_components,
positive_borrow_fee_absolute_change, negative_borrow_fee_absolute_change,
positive_borrow_fee_relative_change, negative_borrow_fee_relative_change,
positive_borrow_availability_absolute_change, negative_borrow_availability_absolute_change,
positive_borrow_availability_percentage_change, negative_borrow_availability_percentage_change,
before_short_interest_revision_result, after_short_interest_revision_result,
before_short_interest_cancellation_result, after_short_interest_cancellation_result,
before_borrow_update_result, after_borrow_update_result,
mixed_phase_2c_metric_output, phase_2c_cli_output, serialized_phase_2c_metric_collection
```

`test_pressure_anchors.py` asserts: all names present; `build_anchor_results()` run twice
produces identical hashes for every name; regenerated hashes match the committed metadata
file exactly; the composite `mixed_phase_2c_metric_output`/`serialized_phase_2c_metric_collection`
pair matches and is the one expected linked coincidence; `phase_2c_cli_output` is stable
across two subprocess invocations and matches the committed value; no anchor hash collides
with any Phase 1/Phase 2A/Phase 2B anchor hash (explicit cross-check against all three prior
metadata files) and no two Phase 2C anchors unexpectedly collide with each other.

## 8. CLI tests (`test_pressure_cli.py`, handoff §31)

Valid-request cases (one per metric family: short-interest change, revision delta,
days-to-cover, borrow-fee change, borrow-availability change) run the actual `python -m
squeeze_core build-market-metrics` subprocess against a mixed `phase_2c_*` input file
(short-interest + borrow + bar observations in one JSONL, exactly like Phase 1's own
cross-domain fixtures) and assert exit code 0 and a well-formed canonical JSON array.
Invalid-request cases: unsupported metric name, unsupported metric version, missing `as_of`,
missing provider, missing reporting period, missing input file, zero denominator (reports
`quality.state=INVALID` with exit 0, not a process failure — mirrors
`test_normalized_cli.py::test_insufficient_history_reports_unavailable_not_nonzero_exit`),
missing value (`quality.state=UNAVAILABLE`, exit 0), unit incompatibility (structurally
unreachable — asserted absent), deterministic repeated output (stdout byte-diff across two
runs), nonzero exit only for genuinely invalid *requests* (bad JSON shape, unknown metric
name), no qualitative language in output (`strong/weak/bullish/bearish/tight/loose/squeeze/
pressure` absent from stdout, extending `test_normalized_cli.py`'s existing needle list),
local-only behavior (no `http://`/`ftp://`/database-scheme strings in output).

## 9. Compatibility tests (`tests/compatibility/test_phase_2c_compatibility.py`)

- `tests/fixtures/compatibility/phase_1_anchor_manifest.json`,
  `tests/fixtures/metrics/expected_phase_2a_metric_metadata.json`, and
  `tests/fixtures/metrics/expected_phase_2b_metric_metadata.json` byte-identical to the Phase
  2B completion commit (`git show b2a75e3e:<path>` compared against the working-tree file via
  `subprocess.run(["git", "diff", "--exit-code", ...])`, read-only, no repository mutation).
- Full Phase 1 + Phase 2A + Phase 2B suites still pass — enforced implicitly by the full-suite
  run in §10, not re-run in isolation a second time here.
- `Observation.model_fields["schema_version"]` still pins `"1.0.0"`.
- `PressureMetricResult`/`DaysToCoverComponents` define no `schema_version` field.
- No file under `src/squeeze_core/{contracts,evidence,adapters,replay,serialization}` imports
  `squeeze_core.metrics` (same AST-walk pattern as Phase 2A/2B's own compatibility test,
  re-run because Phase 2C adds new files to the directory being scanned).

## 10. Isolation tests (extended `test_isolation.py`, handoff §33)

`FORBIDDEN_MODULES`/`FORBIDDEN_CALLS` AST scans re-run unchanged (already glob every `*.py`
in `metrics/`, now including the seven new files automatically).
`FORBIDDEN_IDENTIFIER_SUBSTRINGS` gains the Phase 2C-specific set from design-doc §14:
`short_pressure_score, borrow_pressure_score, cost_to_borrow_score, hard_to_borrow_score,
squeeze_probability, fail_to_deliver, gamma_exposure, open_interest`.
`test_no_result_field_could_carry_a_ratio_ranking_or_recommendation` is extended with
`PressureMetricResult`/`DaysToCoverComponents` field-name checks.

## 11. Final verification sequence (handoff §41, executed after all above pass)

1. `pytest --basetemp=.pytest-run-phase2c-final` — full suite, expect prior count (995 passed
   / 1 skipped) plus every new Phase 2C test, 0 failed.
2. `pytest tests/metrics --basetemp=.pytest-run-phase2c-metrics`
3. `pytest tests/compatibility --basetemp=.pytest-run-phase2c-compat`
4. `scripts/generate_phase_2c_anchors.py` run twice; diff the two in-memory results for byte
   identity before the second run overwrites the file.
5. `build-market-metrics` CLI run twice with identical arguments; diff stdout bytes.
6. `git diff --exit-code b2a75e3e -- tests/fixtures/compatibility/phase_1_anchor_manifest.json
   tests/fixtures/metrics/expected_phase_2a_metric_metadata.json
   tests/fixtures/metrics/expected_phase_2b_metric_metadata.json`
7. Git state checks (`status`, `branch`, `rev-parse HEAD`, `tag --list`, `show phase-1-rc1
   --no-patch`) confirming a clean tree, no remotes, `phase-1-rc1` unchanged.
