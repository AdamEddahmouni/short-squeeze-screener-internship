# Phase 2D Test-First Implementation Plan

This plan enumerates the test files under `tests/readiness/` and the representative
cases each covers, mapped against the handoff's required-case lists (sections 20-26).
Given the volume of named cases in the handoff (approximately 190 across seven
categories), this plan consolidates related cases into parametrized tests within
each file rather than one Python test function per bullet, while still ensuring
every *distinction* called out in the handoff has at least one dedicated assertion.
Where a handoff case is not separately implemented, it is because an equivalent
distinction is already covered by a nearby case and is noted inline as "covered by."

## Files and coverage

### `tests/readiness/conftest.py`
Shared fixture builders: a small deterministic `AdapterContext`/observation factory
per domain (short interest, borrow fee/availability, bars, SEC filings), and a
`build_bundle(...)` helper wrapping `build_point_in_time_evidence` for a given
`as_of`. Mirrors `tests/metrics/conftest.py`'s helper-function style.

### `tests/readiness/test_models.py`
Model-level tests (handoff Section 34 "Models"): frozen/immutable enforcement for
every new model, stable enum values, `Quality`/`DiagnosticSeverity` reuse (no new
quality enum defined), canonical serialization round-trip, deterministic hashing
across two independent constructions of identical content, and that no model
defines `schema_version`, `score`, `rank`, `confidence`, `recommendation`, or any
qualitative-label field (`prime`, `subprime`, `bullish`, `bearish`, `strong`, `weak`).

### `tests/readiness/test_policies.py`
- Known-operation lookup for all 17 policies.
- Unknown-operation lookup raises with a stable message/diagnostic code.
- Policy version mismatch (requesting a `policy_version` the registry doesn't have)
  is rejected explicitly, not silently ignored.
- Required vs optional domains are disjoint per policy.
- No policy contains a numeric trading threshold (AST/field scan).

### `tests/readiness/test_coverage.py` -- Domain coverage (handoff Section 20)
1. All requested domains present -> `test_all_domains_present`
2. One / multiple missing domains -> `test_missing_domain`, `test_multiple_missing_domains`
3. Only future evidence (not yet published) -> `test_future_evidence_is_unavailable_not_missing`
4. Publication after `as_of` (covered by #3 -- same diagnostic family)
5. Receipt after `as_of` -> `test_received_after_as_of_is_unavailable`
6. Eligible active record -> `test_present_domain`
7. Only cancelled record -> `test_domain_with_only_cancelled_record_is_cancelled`
8. Active record + older cancellation -> `test_active_plus_older_cancellation_is_present`
9. Unresolved conflict -> `test_conflicted_domain`
10. Exact duplicate records (covered by #9's negative case: duplicates alone, no
    disagreement, must not classify as `CONFLICTED` -- `test_duplicates_are_not_conflicted`)
11. Revision chain (no conflict) -> `test_revision_chain_is_present_not_conflicted`
12. Partial market bar -> `test_partial_bar_domain`
13. Completed market bar (covered by #6)
14. Unknown availability (domain never evaluated by bundle policy) -> `test_unknown_domain_when_not_evaluated`
15. Zero-valued evidence counted as present -> `test_zero_value_is_present_not_missing`
16. Null-valued required field counted as missing -> `test_null_value_field_is_unavailable`
17. Input ordering invariance -> `test_coverage_snapshot_order_invariant_to_observation_order`
18. Requested-domain ordering invariance -> `test_coverage_snapshot_order_invariant_to_requested_domain_order`
19. Stable deterministic ID -> `test_deterministic_id_stable_across_rebuilds`
20. Stable serialization -> `test_canonical_serialization_stable`
21. No coverage score interpretation -> `test_no_score_field_on_snapshot`
22. No candidate label -> `test_no_candidate_label_field`

### `tests/readiness/test_sufficiency.py` -- Input sufficiency (handoff Section 21)
Parametrized across representative operations spanning all three metric phases:
- `ABSOLUTE_RETURN` sufficient / missing bar / partial bar under completed-bar policy
- `RELATIVE_VOLUME` sufficient / insufficient volume history / zero baseline
- `PERCENTAGE_RETURN_Z_SCORE` sufficient / zero variance (delegated to referenced
  metric's own `Quality`, not recomputed)
- `PUBLISHED_SHORT_INTEREST_ABSOLUTE_CHANGE` sufficient / missing starting period
- `DAYS_TO_COVER` sufficient / missing short interest / insufficient volume history /
  intraday-volume-interval incompatibility
- `BORROW_FEE_ABSOLUTE_CHANGE` sufficient / mixed units
- `BORROW_AVAILABILITY_ABSOLUTE_CHANGE` sufficient / mixed scope
- Conflicted required input -> `structural_state == CONFLICTED`
- Unknown availability -> `structural_state == UNKNOWN`
- Future input excluded / correction after `as_of` excluded / cancellation after
  `as_of` excluded -> all three via `build_bundle` at an early `as_of`, asserting the
  excluded observation never appears in `input_observation_ids`
- Later recalculation reflects correction -> same fixture rebuilt at a later `as_of`
- Required metric result supplied directly vs absent-but-raw-inputs-sufficient (two
  cases sharing one parametrized test, `test_referenced_metric_optional`)
- No downstream metric recalculation where not required -> asserts the sufficiency
  builder never imports/calls a `build_*_result` function (import-graph assertion)
- Operation policy identity stable across two builds -> `test_policy_identity_stable`
- Structural state deterministic across two runs -> `test_sufficiency_deterministic`
- No generic trading-readiness state -> `test_no_trading_state_values` (asserts
  `StructuralState` has exactly `{SUFFICIENT, INSUFFICIENT, UNKNOWN, CONFLICTED}`)

### `tests/readiness/test_age_alignment.py` -- (handoff Section 22)
1/2/3. Identical ages / different ages / three-domain min-max-spread ->
   `test_two_domains_identical_age`, `test_two_domains_different_age`,
   `test_three_domain_spread`
4/5. Single comparable domain / no comparable domains -> `test_single_domain`,
   `test_no_comparable_domains`
6. Missing effective time (defensively handled; in practice every eligible
   observation has one) -> `test_domain_with_no_eligible_observations_excluded`
7. Unknown availability domain excluded from age set -> `test_unknown_domain_excluded`
8. Future availability excluded (inherited from bundle point-in-time filtering) ->
   `test_future_observation_never_appears`
9/10. Exact integer seconds / deterministic mean -> `test_exact_integer_arithmetic`
11. Input-order invariance -> `test_age_alignment_order_invariant`
12/13/14. Availability age vs reporting-period age kept distinct, including "old
   short-interest reporting period with recent receipt" and "recent bars with old
   short-interest reporting period" -> `test_availability_age_and_reporting_period_age_distinct`
15/16. No stale/fresh label, no threshold -> `test_no_staleness_field_anywhere`

### `tests/readiness/test_reporting_alignment.py` -- (handoff Section 23)
Same reporting period across domains / different periods / one domain without
reporting-period semantics / missing field / short-interest period preserved / SEC
filing period preserved / publication time not substituted / receipt time not
substituted / earliest+latest selection / deterministic spread / order invariance /
no alignment score -- one test per bullet, `test_reporting_alignment.py::test_*`.

### `tests/readiness/test_conflicts.py` -- (handoff Section 24)
No conflicts / one conflict / multiple conflicts one domain / conflicts across
domains / duplicate not counted / revision not counted / correction not counted /
cancellation not counted / temporal difference not counted / stable conflict IDs /
stable ordering / stable affected-observation ordering / no provider winner / no
averaging -- one test per bullet.

### `tests/readiness/test_missingness.py` -- (handoff Section 25)
Missing domain / missing required metric / unknown availability / insufficient
history / zero not missing / null counted missing / conflict not counted missing /
unit mismatch not counted missing / cancelled classified separately / deterministic
counts / stable ordering / no default substitution -- one test per bullet
(`MISSING_REQUIRED_FIELD` intentionally has no case here per design doc Section 9).

### `tests/readiness/test_snapshot.py` -- Readiness snapshot (handoff Section 26)
Sufficient / insufficient / unknown / conflicted operation; optional domain missing
but sufficient; required domain missing; required metric missing; required history
insufficient; unit mismatch; provider ambiguity; session mismatch; interval
mismatch; correction unavailable-before/available-after receipt; cancellation
unavailable-before/active-after receipt; historical snapshot byte-identical when
rebuilt at the same `as_of`; later snapshot changes deterministically at a later
`as_of`; input reordering invariance; and explicit absence checks for `score`,
`rank`, `recommendation`, `bullish/bearish`, `Prime/Subprime` fields on the model
(`test_no_scoring_fields`) plus a docstring/field-name grep asserting
`structural_state` is documented as operation-scoped, not candidate-scoped.

### `tests/readiness/test_cli.py`
Valid coverage/sufficiency/full-readiness request; invalid operation; unsupported
policy version; missing symbol/`as-of`/input file/policy file; invalid domain name;
insufficient/conflicted/unknown required input; deterministic repeated output
(run twice, byte-compare stdout); nonzero exit for invalid requests; no qualitative
language in output (grep stdout for a forbidden-word list); local-only (no network
imports in the CLI branch's call graph, delegated to the isolation test).

### `tests/readiness/test_phase_2d_anchors.py`
Loads `tests/fixtures/readiness/expected_phase_2d_readiness_metadata.json` and
recomputes every named anchor via `scripts/generate_phase_2d_anchors.py`'s builder
functions (imported directly, not subprocess, except for the CLI-output anchor),
asserting byte-for-byte hash equality. A second test invokes the generator script
as a subprocess twice and asserts the two output files are byte-identical
(regeneration stability).

### `tests/compatibility/test_phase_2d_isolation.py`
Extends the `test_phase_2c_isolation.py` pattern: prior-manifest unchanged since
`61b15ab3f44c2dc70a25e95db88cdaab413dcd94`, no forbidden runtime dependency
(`socket, http, urllib, requests, sqlite3, psycopg2, pandas, numpy, scipy, tkinter,
asyncio`) in any new `readiness/` module, no `readiness/` import from any Phase 1/2A/
2B/2C-only module, and an explicit source-text scan of every new file for the
forbidden-vocabulary list (`score`, `rank`, `recommend`, `prime`, `subprime`,
`bullish`, `bearish`, `alert`, `confidence_percent`) outside of comments/docstrings
that explain the *absence* of that concept.

## Fixture and anchor provenance

All Phase 2D fixtures are `SYNTHETIC_EDGE_CASE`, built the same way
`generate_phase_2c_anchors.py` builds its observations (via the real adapter
normalizers, not hand-crafted `Observation` objects), so every fixture observation
passes through the same validation path production data would. No credentials,
account identifiers, or live endpoint URLs appear anywhere in `tests/fixtures/
readiness/`.
