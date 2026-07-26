# Phase 2A Test-First Implementation Plan

This plan is written and committed before any `src/squeeze_core/metrics/` source exists. It maps
every required case family from the Phase 2A handoff to concrete test files, fixture files, and
the order in which they will be written. Implementation source files are added only after this
plan (and `phase-2a-design.md`) are committed.

## 1. Fixture layout (`tests/fixtures/metrics/`)

Following the existing `tests/fixtures/providers/market_bars/*.json` convention (a JSON document
with `schema_version` + a `cases` array, each case having `metadata` + a payload), rather than
inventing a new fixture shape:

- `phase_2a_metric_cases.json` — small end-to-end cases used by CLI and mixed-metric-output
  tests; each case names a metric request and its expected result summary.
- `return_cases.json` — bar pairs + expected return values/diagnostics (handoff §23, 25 cases).
- `gap_cases.json` — session-pair bars + expected gap values/diagnostics (handoff §24, 24 cases).
- `range_cases.json` — single bars + expected range values/diagnostics (handoff §25, 18 cases).
- `volume_baseline_cases.json` — bar series + window policy + expected baseline (handoff §26, 28
  cases).
- `lifecycle_cases.json` — partial/completed/corrected/cancelled chains shared across all four
  metric families (handoff §13).
- `point_in_time_cases.json` — the ten point-in-time scenarios in handoff §27.
- `expected_phase_2a_metric_metadata.json` — machine-readable anchor hashes (handoff §34),
  regenerated and diffed for byte-identity as part of `tests/metrics/test_anchors.py`.
- `fixture_metadata.json` — provenance classification for the family (`SANITIZED_REPRESENTATIVE_SAMPLE`
  vs `SYNTHETIC_EDGE_CASE`, matching the two allowed classes from handoff §22). All Phase 2A bar
  fixtures are `SYNTHETIC_EDGE_CASE`: hand-built to exercise a specific boundary condition, not
  sampled from a real provider capture (Phase 1H already owns the provider-shaped fixtures; Phase
  2A fixtures are plain, already-normalized `Observation` JSONL built directly with `BarPayload`
  and the same `provenance.provider_metadata` shape the Phase 1H normalizer produces, since
  `metrics/` consumes normalized `Observation`s, not raw provider records).

No existing Phase 1H fixture file is edited. Where a Phase 2A test wants a "real-looking" bar, it
constructs a fresh `Observation` with the same field shapes as `normalize_market_bar_record`
produces, rather than mutating a Phase 1 fixture in place (mutating a shared file would risk an
accidental Phase 1 anchor change; keeping fixtures append-only per phase is the same discipline
Phase 1 used across 1A-1I).

## 2. Test files and what each proves

### `tests/metrics/test_models.py`
- `MetricResult` is frozen / rejects unknown fields (`extra="forbid"`).
- `value is None` iff `quality.state is not KNOWN_VALUE` (both directions).
- `MetricName`, `MetricUnit`, `PriceField`, `ProviderScopeMode`, `WindowType` enums have the
  exact stable string values documented in the design spec.
- `deterministic_id` is computed when absent, is stable for identical identity fields, and
  changes when any identity field changes (parametrized over each field independently) but does
  **not** change when only `value`/`diagnostics` change for an otherwise-identical identity
  (proves `value`/`diagnostics` are excluded from the identity hash, per design §7).
- Canonical serialization round-trip: `MetricResult` -> `canonical_json_bytes` -> parse -> same
  bytes on re-serialization (idempotence), and two independently-constructed but
  field-identical results serialize to byte-identical output.

### `tests/metrics/test_identifiers.py`
- `deterministic_metric_id` produces a stable `UUID` string (not a random UUID — same input,
  same output, called twice in the same process and across a fresh Python process via
  subprocess).
- `METRIC_NAMESPACE != OBSERVATION_NAMESPACE` and a metric ID never collides with an observation
  ID built from a structurally similar dict (regression guard against accidentally importing the
  wrong namespace constant).

### `tests/metrics/test_selection.py`
Covers the "Selection" required tests from handoff §36 plus lifecycle/point-in-time semantics:
- Symbol filter excludes non-matching symbols (delegated to `build_bar_series`, proven at this
  layer via a boundary resolution request against a mixed-symbol fixture).
- Asset-class filter (Phase 1H is equity-only; a non-equity record is rejected upstream by the
  normalizer, so this test proves `metrics/` never receives one and does not need its own guard
  — documented as a deliberate non-duplication).
- Interval filter: requesting `1_DAY` against a fixture containing `1_MINUTE` bars at the same
  boundary date yields `NO_ELIGIBLE_BARS`, not a silently-wrong bar.
- Session filter: requesting `REGULAR` excludes a `PREMARKET` bar at an adjacent boundary.
- Provider filter: explicit `provider="ALPACA_SHAPED"` selects only that provider's bar when two
  providers publish at the same boundary; omitting it when two providers are present yields
  `METRIC_AMBIGUOUS_PROVIDER` / `UNAVAILABLE`; omitting it when only one provider is present
  resolves without complaint.
- Point-in-time filter: reuses `point_in_time_cases.json` — event-before/publication-after,
  publication-before/receipt-after, and the fully-eligible case (handoff §27 cases 1-3).
- Lifecycle resolution: partial excluded when a completed/corrected version exists and is
  eligible; correction visible only after its own `source_timestamp <= as_of`; cancellation
  visible only after its own eligibility, and a bar computed *before* the cancellation arrived is
  never retroactively changed (handoff §27 cases 4-8, re-verified here at the selection layer
  directly, not just end-to-end).
- Deterministic order: shuffling the input observation list before calling the selector produces
  identical `BoundaryResolution`/`WindowResolution` output (handoff §27 case 8).
- Provider ambiguity is deterministic and does not depend on dict/set iteration order (parametrize
  the same two-provider fixture with several different input orderings).

### `tests/metrics/test_returns.py` — the 25 cases of handoff §23
Each case is one parametrized entry sourced from `return_cases.json` plus a handful of pure-Python
edge cases (out-of-order input, deterministic reordering invariance, exact Decimal preservation)
that don't need a JSON fixture because they assert on Python `Decimal` identity rather than a
provider-shaped record. Positive/negative/zero absolute and percentage return; zero
starting-price denominator -> `RETURN_PRICE_FIELD_UNAVAILABLE`/`METRIC_ZERO_DENOMINATOR` as
appropriate; missing start/end price -> `METRIC_MISSING_START_PRICE`/`METRIC_MISSING_END_PRICE`;
start/end bar unavailable at `as_of` -> `RETURN_START_BAR_NOT_FOUND`/`RETURN_END_BAR_NOT_FOUND`;
partial start/end bar -> `METRIC_PARTIAL_INPUT`; corrected end bar before/after correction
receipt (two `as_of` values against the same fixture, asserting the byte-identical-before /
different-after contract from design §6); cancelled bar before/after cancellation receipt
(same two-`as_of` pattern); mixed providers without explicit provider ->
`METRIC_AMBIGUOUS_PROVIDER`; explicit single-provider selection; mixed intervals ->
`METRIC_INCOMPATIBLE_INTERVAL`; mixed sessions -> `METRIC_INCOMPATIBLE_SESSION` (when the two
requested boundaries resolve to different `BarSession` values and the policy requires same
session); same input bar used twice -> `RETURN_IDENTICAL_INPUT_BAR` (zero return, `VALID`
quality — using one bar as both start and end is well-defined, not an error, per formula
literalism); out-of-order input observations and deterministic reordering invariance (same
result regardless of fixture line order); exact Decimal preservation (a return computed from
`10.10`/`10.25` never becomes a `float`-rounded value — asserted via `Decimal` equality and via
string round-trip through canonical JSON).

### `tests/metrics/test_gaps.py` — the 24 cases of handoff §24
Sourced from `gap_cases.json`. Positive/negative/zero absolute and percentage gap; zero
prior-close denominator; missing prior close/current open; prior/current session unavailable at
`as_of`; premarket-to-regular policy case (explicit boundaries spanning session types, allowed
because the caller supplied both boundaries explicitly — design §5 note on no built-in calendar);
prior-regular-close-to-next-regular-open (the primary supported case); same-session bars
incorrectly supplied as a gap pair -> `GAP_SESSION_DATE_MISMATCH` (both boundaries resolve to the
same `session_date`, which a gap by definition should not); nonadjacent-session policy (prior and
current boundaries separated by more than one session — accepted but flagged
`GAP_NONADJACENT_SESSION_POLICY` as an informational diagnostic, not an error, since Phase 2A has
no calendar to define "adjacent"); session-date mismatch; overnight UTC-date-crossing case
(a bar whose local session date and UTC calendar date differ — proves the metric uses
`session_date` metadata, never a naive UTC date, per handoff §15); mixed-provider ambiguity;
corrected prior close / corrected current open (before/after receipt, byte-identical-before
contract again); cancelled prior bar; unknown session (`BarSession.UNKNOWN` — computed but
flagged `BAR_SESSION_UNKNOWN`-equivalent informational diagnostic, not rejected, since "unknown"
is itself an objective, representable fact per Phase 1H convention); daily-bar session semantics
(`1_DAY` interval bars, where "gap" still means adjacent-daily-bar open/close, not intraday
session boundaries); deterministic input reordering.

### `tests/metrics/test_ranges.py` — the 18 cases of handoff §25
Sourced from `range_cases.json`. Positive/zero absolute range; positive percentage range; zero
denominator (`low == 0` is actually impossible per `BarPayload`'s `gt=0` constraint — this case
is instead realized as "low equals a value that makes the *chosen* denominator policy degenerate"
if the low-denominator policy is later swapped; documented explicitly as currently unreachable
under the `low_denominator_range.v1` policy and asserted as such, rather than faked); missing
high/low (upstream `BarPayload` requires both — this case is realized as a boundary that resolves
to no bar at all, i.e. `METRIC_NO_ELIGIBLE_BARS`, since a `BarPayload` missing either field cannot
exist as a normalized `Observation` in the first place — documented, not skipped silently);
invalid high-below-low (same reasoning — `BarPayload`'s own validator rejects this at
normalization time; the range test proves `metrics/` never has to handle it because it structurally
cannot receive it, with a regression test that constructing such a payload raises at the
`contracts` layer); partial bar -> `RANGE_PARTIAL_BAR_UNSUPPORTED`; completed bar (baseline
positive case); corrected bar before/after correction receipt; cancelled bar; mixed-provider
ambiguity; exact Decimal precision; unknown session; daily bar; intraday bar; deterministic
repeated output (same request run twice yields byte-identical `MetricResult`).

### `tests/metrics/test_volume_baselines.py` — the 28 cases of handoff §26
Sourced from `volume_baseline_cases.json`. Mean over 3 / mean over 5 completed bars; current bar
excluded (default policy); explicit target bar before the window / after the window (i.e. the
target's own `bar_start` used as the exclusive upper bound regardless of where else it might sort);
zero-volume sample retained (contributes `0` to the sum, counted in `used`); missing-volume
sample excluded and separately counted in `missing`, not `used`; insufficient history (`used <
minimum_samples` -> `VOLUME_BASELINE_INSUFFICIENT_SAMPLES`, quality `UNAVAILABLE`); empty window
(`used == 0` -> `VOLUME_BASELINE_WINDOW_EMPTY`); mixed intervals in the candidate pool (excluded
by the interval filter, not silently mixed into the mean) -> counted in `missing` with
`VOLUME_BASELINE_MIXED_INTERVALS`; mixed sessions (same treatment,
`VOLUME_BASELINE_MIXED_SESSIONS`); mixed providers (ambiguous unless explicit provider given,
same as returns); mixed volume units (`BarVolumeUnit` recorded in
`provenance.provider_metadata["volume_unit"]` — bars whose unit differs from the target's unit are
excluded, `VOLUME_BASELINE_MIXED_UNITS`); partial bar excluded from the window; corrected bar
before/after correction receipt; cancelled bar before/after cancellation receipt; out-of-order
input observations; duplicate bar observations (`build_bar_series` already dedupes identical
raw records upstream — proven here that the baseline sees no duplicate contribution); same-boundary
provider conflict (`CONFLICTED` quality bar excluded from window, counted in `missing` with
`METRIC_CONFLICTED_INPUT`); requested count larger than available count (uses what's available,
reports accurate `requested`/`eligible`/`used`); minimum sample threshold met/not met (both
branches); exact Decimal mean (e.g. mean of `1000, 1001, 1002` is exactly `1001`, and a
non-terminating mean like `1000, 1001` -> `1000.5` stays exact — a genuinely non-terminating
case such as `1000, 1000, 1001` (mean `1000.33...`) is asserted to retain full `Decimal`
precision rather than being silently truncated, per handoff's "no floating point" / "exact
Decimal" requirement — this exercises `Decimal` division precision context explicitly); no
relative-volume output (the result object has no field where a ratio could be attached — a
static/type-level guarantee, plus a grep-based isolation test); supporting observation IDs
preserved and sorted; stable series/result hash across two independent runs.

### `tests/metrics/test_diagnostics.py`
Stable diagnostic code values (string-literal regression test — codes are a public contract,
accidental renames must fail a test); deterministic ordering of a diagnostics tuple built from
diagnostics constructed in several different orders; one test per general diagnostic category
required by handoff §36 (missing input, insufficient history, zero denominator, mixed units,
mixed sessions, mixed providers, unknown availability, partial input, cancelled input, conflict
input) — most already covered by the per-metric test files; this file adds direct unit-level
tests against `metrics/diagnostics.py` helpers in isolation (sort function, severity mapping)
rather than re-deriving them end-to-end.

### `tests/metrics/test_cli.py`
Valid metric request (each of the four families) -> exit 0, JSON on stdout, stable key order;
invalid metric name / invalid metric version -> exit 1, JSON error on stderr (matching the
existing `main()` `except Exception` -> stderr contract exactly, no new exit-code convention);
missing `--as-of` / missing `--symbol` -> `argparse` usage error, non-zero exit (existing
`argparse required=True` behavior, not new code); invalid input file (bad JSON, bad fixture path)
-> exit 1; no eligible bars -> exit 0 with a `MetricResult` whose quality is `UNAVAILABLE` (a
"no data" answer is not a CLI failure — only a malformed *request* is); deterministic repeated
output (same command run twice -> byte-identical stdout, `diff`-checked in the test); grep the
full stdout of every case for a small deny-list of qualitative words (`"bullish"`, `"bearish"`,
`"strong"`, `"weak"`, `"breakout"`, `"score"`, `"rank"`, `"recommend"`, `"buy"`, `"sell"`) as a
belt-and-suspenders isolation check; confirm no network call is attempted (no `socket`/`http`
import reachable from `metrics/` or the new CLI branches — static `ast`-based check, see isolation
plan below).

### `tests/metrics/test_compatibility.py`
- Full `tests/compatibility/` suite still passes unmodified (imported and re-run, or simply relied
  on via the existing suite — this file specifically re-asserts the Phase 1 anchor manifest hashes
  listed in the handoff, reading them from
  `tests/fixtures/compatibility/phase_1_anchor_manifest.json` directly rather than hardcoding the
  handoff's possibly-stale copy, since the handoff itself says the committed manifest is
  authoritative).
- `schema_version` referenced anywhere in `metrics/` is the literal `"1.0.0"` string only via the
  `Observation`/`BarPayload` objects it reads — `metrics/` defines no competing schema version of
  its own for `MetricResult` (`MetricResult` is a new model, not a schema-versioned wire format
  shared with Phase 1, so it intentionally has no `schema_version` field — documented in the
  design spec's field table, §4).
- Existing `build-bar-series`/`build-evidence`/etc. CLI commands produce byte-identical output
  before and after the Phase 2A CLI additions (regression-runs one existing golden CLI case).

### `tests/metrics/test_isolation.py`
Static checks (via `ast.walk` over `src/squeeze_core/metrics/*.py` and the new `__main__.py`
branches) that no forbidden import appears: `socket`, `http`, `urllib`, `requests`, `sqlite3`,
`psycopg2`, any `pandas`/`numpy` import, any GUI toolkit, any broker/order-related identifier.
Confirms `datetime.now()` / `time.time()` / `uuid4` are never called inside `metrics/` (grep +
AST check for `Enum`-free randomness — every ID must come from `deterministic_metric_id`, every
timestamp from an explicit `as_of` or bar metadata, never wall-clock).

### `tests/metrics/test_anchors.py`
Regenerates each of the sixteen required anchors (handoff §34) from their source fixtures twice
in the same test run (two independent calls, not a cached value) and asserts byte-for-byte
identical `canonical_hash` output both times, then asserts the hash matches the value recorded in
`expected_phase_2a_metric_metadata.json`. This file is the single source of truth for "did
Phase 2A regenerate byte-identically" in the completion report.

## 3. Ordering of implementation commits (mirrors handoff §40, adjusted to this repo's actual
module layout discovered during research)

1. `docs: specify phase 2a foundational market metrics` — this file + `phase-2a-design.md` (this
   commit).
2. `feat: add deterministic metric contracts and serialization` — `metrics/models.py`,
   `metrics/identifiers.py`, `metrics/serialization.py`, `metrics/diagnostics.py`, `metrics/__init__.py`.
3. `feat: add point-in-time market-bar metric selection` — `metrics/selection.py`.
4. `feat: add absolute and percentage return metrics` — `metrics/returns.py`.
5. `feat: add absolute and percentage session gap metrics` — `metrics/gaps.py`.
6. `feat: add absolute and percentage bar range metrics` — `metrics/ranges.py`.
7. `feat: add deterministic volume baseline metrics` — `metrics/volume_baselines.py`.
8. `test: add phase 2a lifecycle and no-look-ahead fixtures` — `tests/fixtures/metrics/**`,
   `tests/metrics/**`.
9. `feat: extend offline cli for foundational market metrics` — `__main__.py` additions.
10. `docs: document phase 2a metric semantics and verification` — remaining docs/ADRs +
    `phase-2a-progress.md` + anchor metadata + completion-report inputs.

Each commit leaves the full test suite (`--basetemp=.pytest-run-*`) passing; new tests are added
in the same commit as the code they exercise wherever practical, consistent with how Phase 1's
own commit history interleaves `feat`/`test` commits per sub-domain (see `git log --oneline` for
phase/1h and phase/1i).
