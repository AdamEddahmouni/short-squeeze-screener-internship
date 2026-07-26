# Testing and Validation

## Phase 2V outcome amendment

Network access is excluded from tests. Sanitized recorded fixtures live under
`tests/fixtures/validation/outcome_amendment/`; edge-only acquisition states are labeled
synthetic. Run `scripts/generate_phase_2v_outcome_anchors.py` twice and verify
`expected_phase_2v_outcome_metadata.json` remains byte-identical. The generator does not
write any earlier anchor manifest.

Dedicated tests cover acquisition states and serialization, bar normalization, both
detection boundaries and eight windows, point-in-time exclusions, separate conclusion
semantics, public-export sanitization, CLI failure behavior, and anchor regeneration.

## Phase 2A derived-metric coverage and commands

Phase 2A tests (`tests/metrics/`) cover models, deterministic identifiers, diagnostics ordering,
point-in-time/lifecycle/provider selection, all required return/gap/range/volume-baseline cases
(positive/negative/zero, missing/zero inputs, partial/corrected/cancelled bars before and after
their own availability, mixed providers/intervals/sessions/units, deterministic reordering, exact
`Decimal` preservation), the offline CLI, isolation (no networking/credentials/database/GUI/
randomness/wall-clock/relative-volume/scoring/ranking), full Phase 1 compatibility, and byte-for-byte
regeneration of the sixteen Phase 2A anchors.

```powershell
.\.venv\Scripts\python.exe -m squeeze_core build-market-metrics --input tests\fixtures\metrics\cli_demo_bars.jsonl --symbol TESTA --as-of 2026-01-20T22:00:00Z --spec tests\fixtures\metrics\phase_2a_metric_cases.json
```

## Phase 2B normalized-metric coverage and commands

Phase 2B tests (`tests/metrics/test_statistics.py`, `test_normalized_models.py`,
`test_normalized_identifiers.py`, `test_relative_volume.py`, `test_volume_standardization.py`,
`test_return_baselines.py`, `test_return_standardization.py`, `test_normalized_lifecycle.py`,
`test_normalized_cli.py`, `test_normalized_anchors.py`, extended `test_isolation.py`, and
`tests/compatibility/test_phase_2b_isolation.py`) cover Decimal population statistics, immutable
normalized models, deterministic identity and non-collision, all required relative-volume/
volume-deviation/volume-z-score/return-baseline/return-z-score cases (positive/negative/zero,
missing/zero/insufficient inputs, zero variance, target exclusion, corrected/cancelled evidence
before and after its own availability, mixed providers/intervals/sessions/units, deterministic
reordering, exact `Decimal` preservation), the offline CLI, isolation (no networking/credentials/
database/GUI/randomness/wall-clock/scoring/ranking/technical-indicator concepts), full Phase 1 and
Phase 2A compatibility, and byte-for-byte regeneration of the twenty-one Phase 2B anchors.

```powershell
.\.venv\Scripts\python.exe -m squeeze_core build-market-metrics --input tests\fixtures\metrics\phase_2b_cli_demo_bars.jsonl --symbol TESTB --as-of 2026-02-01T22:00:00Z --spec tests\fixtures\metrics\phase_2b_normalized_metric_cases.json
```

## Phase 2C pressure-metric coverage and commands

Phase 2C tests (`tests/metrics/test_source_age.py`, `test_short_interest_changes.py`,
`test_short_interest_revision_delta.py`, `test_days_to_cover.py`, `test_borrow_fee_changes.py`,
`test_borrow_availability_changes.py`, `test_pressure_lifecycle.py`,
`test_pressure_cross_domain.py`, `test_pressure_cli.py`, `test_pressure_anchors.py`, extended
`test_diagnostics.py`/`test_isolation.py`, and `tests/compatibility/test_phase_2c_isolation.py`)
cover source-age construction, point-in-time short-interest/borrow selection (revision,
cancellation, conflict, exact-boundary resolution), all required short-interest-change/
revision-delta/days-to-cover/borrow-fee-change/borrow-availability-change cases (positive/
negative/zero, missing/zero-denominator inputs, cancelled/revised evidence before and after its
own availability, mixed providers, deterministic reordering, exact `Decimal` preservation),
cross-domain unit/provider isolation for `DAYS_TO_COVER`, the offline CLI, isolation (no
networking/credentials/database/GUI/randomness/wall-clock/hard-to-borrow-classification/
squeeze-or-pressure-scoring concepts), full Phase 1/2A/2B compatibility, and byte-for-byte
regeneration of the 26 Phase 2C anchors.

```powershell
.\.venv\Scripts\python.exe -m squeeze_core build-market-metrics --input tests\fixtures\metrics\phase_2c_cli_demo_observations.jsonl --symbol TESTC --as-of 2026-03-15T12:00:00Z --spec tests\fixtures\metrics\phase_2c_metric_cases.json
```

## Phase 2D evidence-readiness coverage and commands

Phase 2D tests (`tests/readiness/test_models.py`, `test_policies.py`, `test_coverage.py`,
`test_age_alignment.py`, `test_reporting_alignment.py`, `test_conflicts.py`,
`test_missingness.py`, `test_sufficiency.py`, `test_snapshot.py`,
`test_phase_2d_anchors.py`, and `tests/compatibility/test_phase_2d_isolation.py`) cover domain
coverage classification (present/missing/unavailable/conflicted/cancelled/partial/unknown,
including future-evidence exclusion, cancellation-only domains, and revision chains that stay
`PRESENT`), cross-domain availability-age and reporting-period alignment (identical/spread ages,
missing-age domains, exact integer arithmetic), conflict summaries (temporal-difference and
revision/correction/cancellation exclusion), missingness summaries (zero-vs-missing,
unknown-vs-missing, conflict-vs-missing distinctions), operation-scoped input sufficiency for
all 17 supported operations, before/after correction and cancellation readiness-snapshot
lifecycle, the offline CLI, full Phase 1/2A/2B/2C compatibility, and byte-for-byte regeneration
of the 32 Phase 2D anchors.

```powershell
.\.venv\Scripts\python.exe -m squeeze_core build-evidence-readiness --input tests\fixtures\readiness\phase_2d_cli_demo_observations.jsonl --symbol TESTD --as-of 2026-03-01T12:00:00Z --operation PUBLISHED_SHORT_INTEREST_ABSOLUTE_CHANGE
```

## Phase 1I deterministic validation

Trade/quote tests cover exact and invalid prices, missing versus zero and invalid sizes, size units, conditions, one-sided quotes, venue and market scope, sequence scope/reset/duplicate/out-of-order behavior, publication/receipt/event gates, immutable corrections/cancellations, conflicts, replay, series, CLI, and Phase 1A-1H anchors. Fixtures are representative or synthetic only. Repeated generation must preserve mixed JSONL, strict replay, timeline, series, bundle, and serialized hashes without synthetic NBBO, aggressor side, spread, order-flow, or strategy output.

## Phase 1H market-bar coverage and commands

Phase 1H tests 43 representative/synthetic cases covering all aliases; required 1-, 5-, and 15-minute, 1-hour, and daily intervals; start/end labels; offset, time-only, IANA, unknown-zone, and DST behavior; regular/extended/unknown sessions; missing versus zero volume and trade count; invalid OHLC; duplicates, conflicts, overlap, revisions, partial/completed/corrected/cancelled lifecycle; publication/receipt/effective gates; explicit gap states; stable series, mixed replay, CLI output, repeated generation, credential scans, and every Phase 1A-1G compatibility anchor.

```powershell
.\.venv\Scripts\python.exe -m squeeze_core normalize-provider --provider market-bars --input tests\fixtures\providers\market_bars\representative_cases.json --context tests\fixtures\providers\market_bars\context.json --case bar-complete-one-minute
.\.venv\Scripts\python.exe -m squeeze_core build-bar-series --input tests\fixtures\evidence\normalized_phase_1h_point_in_time.jsonl --symbol TESTA --interval 1_MINUTE --session REGULAR --as-of 2026-01-31T14:35:01Z
```

All Phase 1H fixtures are representative or synthetic because archive inspection found shapes but no saved record with defensible complete provenance. No case is labelled recorded.

## Phase 1G objective news coverage and commands

Phase 1G tests 35 representative/synthetic cases, all documented aliases, strict records, URL and timestamp policies, explicit/missing/empty symbols, immutable lifecycle observations, duplicates, same-ID conflicts, syndication, eligibility gates, coverage, ages, mixed replay, CLI output, repeated artifact generation, and every Phase 1A–1F compatibility anchor.

```powershell
.\.venv\Scripts\python.exe tests\phase_1g_fixture_builders.py --write
.\.venv\Scripts\python.exe -m squeeze_core validate tests\fixtures\evidence\normalized_phase_1g_point_in_time.jsonl
.\.venv\Scripts\python.exe -m squeeze_core replay tests\fixtures\evidence\normalized_phase_1g_point_in_time.jsonl --mode strict
.\.venv\Scripts\python.exe -m squeeze_core normalize-provider --provider news --input tests\fixtures\providers\news\representative_cases.json --context tests\fixtures\providers\news\context.json --case news-complete-v1
.\.venv\Scripts\python.exe -m squeeze_core build-evidence --input tests\fixtures\evidence\normalized_phase_1g_point_in_time.jsonl --symbol TESTA --as-of 2026-01-31T15:01:00Z
.\.venv\Scripts\python.exe -m squeeze_core build-evidence-timeline --input tests\fixtures\evidence\normalized_phase_1g_point_in_time.jsonl --symbol TESTA --as-of-file tests\fixtures\evidence\news_availability_timeline.json
```

No fixture uses archived `data/news_snapshot.json`; no case is labeled recorded.

## Behavior coverage

Tests cover required/enumerated fields, timezone awareness/UTC normalization, schema rejection, numeric bounds, event/payload binding, deterministic identity, quality reasons, missing versus zero, stable serialization/hash, JSON round trips, replay order, diagnostics, monotonic clock, wall-clock independence, CLI behavior, fixture hashes, and secret-like content. Phase 1B adds IBKR units/timestamps/duplicates/conflicts. Phase 1C adds the additive market snapshot, evidence-backed Finviz aliases, explicit percentages, decimal K/M/B/T quantities, approximation, timestamp placeholders, partial rows, evidence selection/coverage, compatible conflicts, unchanged observation membership, local CLI paths, mixed strict replay, and deterministic bundle hashes.

Phase 1D adds FINRA-shaped schema/type/origin validation, exact shares and percentages, settlement/publication/receipt/effective distinctions, date-only availability policies, daily short-volume rejection, partial/zero/missing behavior, immutable revisions, historical timeline rebuilds, fourth-domain coverage, reporting/availability ages, settlement-period conflicts, mixed strict replay, CLI timelines, and repeated artifact generation.

These tests validate engineering behavior only. They do not validate a provider, data entitlement, financial formula, squeeze prediction, strategy, or trading outcome.

## Offline fixtures

| Fixture | Records | SHA-256 |
|---|---:|---|
| `minimal_session.jsonl` | 13 | `ceeba255e569c3efc61c92f60a763057a9b68bb4c19cea4b12999f95ec8aabec` |
| `quality_edge_cases.jsonl` | 9 | `475e5a6eb0070ae7586cecf3055fbec779b0f5ab410a1e8b070d1f6792289025` |
| `out_of_order_session.jsonl` | 3 | `1d22c176cacbb6e46210d458a4bdbb7b371aa13386db89c7c83072d788e8a18c` |
| `providers/ibkr/normalized_session.jsonl` | 6 | `e3b876ec8f3e9ccf0aa44a58ac6b3cda865e722fcb9b7614b3709d79049fa619` |
| `evidence/normalized_point_in_time.jsonl` | 3 | `10384755d94b1744297b32edb65b5311acf3d49554189ac7997c899dad6d267c` |
| `evidence/normalized_phase_1d_point_in_time.jsonl` | 5 | `de24c62a4d964e4ff9a555a4357b9fc0a212430c2c5336f676cc61c0fe6fb5f0` |

Fixtures use only `TESTA`, `TESTB`, or no symbol. They contain no accounts, credentials, live URLs, network dependency, or real ticker claim. The builder in `tests/fixture_builders.py` documents their construction; the committed JSONL and recorded hashes are the golden inputs.

IBKR provider fixtures use only representative provider shape and invented values. No preserved recorded row exists, so none is labeled recorded. `tests/provider_fixture_builders.py --write` generates the committed six-observation JSONL and expected hash metadata. Its strict replay result hash is `b7371c43fc1403b94af0a2f7ba13461f30ac7335becbe7a59ba821a711c51708`; regeneration fails if the expected six observations are not produced.

Finviz fixtures are representative or synthetic only. `tests/phase_1c_fixture_builders.py --write` produces the mixed JSONL and metadata. Key hashes are Finviz raw record `4df0763a0ed2f8ddc03b7efdff4cf7e5e79b9d17eca13c06946d6ccd0b39cb09`, Finviz observation `a1e744c68c18adf4bd03dd84687fdd1e3220378b26090e7f4bfb3c4af9a0f9c4`, strict replay `9e42a75e2d831ac4184eef37cedd4325c1b404708e3db0e9a7f1cdca83d6676b`, and evidence bundle `d633447eb59cc8cdb059429e53498ca8a49f3895da0800fb56c1ff43729f2455`.

FINRA-shaped fixtures are representative or synthetic only; no recorded row exists. `tests/phase_1d_fixture_builders.py --write` produces the five-observation mixed JSONL and timeline metadata. Its strict replay hash is `2532dc3171da766e4fc9a631fd69a0fa8142462f3cd02e1b9f416073730380ff`; the after-correction bundle hash is `667ae58af765655d637409864bd9786e1228d30c7e7832599d4078b64ba64c12`.

## Commands

```powershell
.\.venv\Scripts\python.exe -m pytest
.\.venv\Scripts\python.exe -m squeeze_core validate tests\fixtures\minimal_session.jsonl
.\.venv\Scripts\python.exe -m squeeze_core replay tests\fixtures\minimal_session.jsonl --mode strict
.\.venv\Scripts\python.exe tests\provider_fixture_builders.py --write
.\.venv\Scripts\python.exe -m squeeze_core validate tests\fixtures\providers\ibkr\normalized_session.jsonl
.\.venv\Scripts\python.exe -m squeeze_core replay tests\fixtures\providers\ibkr\normalized_session.jsonl --mode strict
.\.venv\Scripts\python.exe tests\phase_1c_fixture_builders.py --write
.\.venv\Scripts\python.exe -m squeeze_core replay tests\fixtures\evidence\normalized_point_in_time.jsonl --mode strict
.\.venv\Scripts\python.exe -m squeeze_core build-evidence --input tests\fixtures\evidence\normalized_point_in_time.jsonl --symbol TESTA --as-of 2026-01-15T15:30:00Z
.\.venv\Scripts\python.exe tests\phase_1d_fixture_builders.py --write
.\.venv\Scripts\python.exe -m squeeze_core replay tests\fixtures\evidence\normalized_phase_1d_point_in_time.jsonl --mode strict
.\.venv\Scripts\python.exe -m squeeze_core build-evidence-timeline --input tests\fixtures\evidence\normalized_phase_1d_point_in_time.jsonl --symbol TESTA --as-of-file tests\fixtures\evidence\short_interest_publication_timeline.json
```

The out-of-order fixture must fail strict replay and succeed in normalized mode with a diagnostic.

## Phase 1E commands

```powershell
.\.venv\Scripts\python.exe tests\phase_1e_fixture_builders.py --write
.\.venv\Scripts\python.exe -m squeeze_core replay tests\fixtures\evidence\normalized_phase_1e_point_in_time.jsonl --mode strict
.\.venv\Scripts\python.exe -m squeeze_core normalize-provider --provider sec --input tests\fixtures\providers\sec\representative_cases.json --context tests\fixtures\providers\sec\context.json --case sec-complete-original-v1
.\.venv\Scripts\python.exe -m squeeze_core build-evidence-timeline --input tests\fixtures\evidence\normalized_phase_1e_point_in_time.jsonl --symbol TESTA --as-of-file tests\fixtures\evidence\sec_filing_availability_timeline.json
```

## Phase 1F trading-halt coverage

Phase 1F tests strict halt shape/origin validation, exact and time-only timestamp rules, explicit session/timezone requirements, codes, raw hashes, missing fields, duplicates, conflicts, immutable revisions, scheduled versus actual quote/trade resumption, publication/receipt/effective gates, objective halt states, independent coverage, ages, mixed strict replay, CLI timelines, and every Phase 1A–1E compatibility anchor.

Halt fixtures are representative or synthetic only; archive search found no recorded halt row. The provider fixtures contain 30 cases, the mixed source contains 15 scenarios, and the committed replay contains 12 observations. `tests/phase_1f_fixture_builders.py --write` regenerates the artifacts deterministically.

Key anchors are mixed JSONL `c5cb4b76f75b73ba89165edcf53d60a39cee193c103b718f163991a02a4106c4`, strict replay `1c1a9e84de1dfdbff032642ba6616e2573cb25e5965eb059b031ca136006f937`, final bundle `af9c72db36d3b3bccba590c6580e74a5922bad7f2d826107ca9f529c66b48ae5`, and serialized final bundle `79aea01b32b873e39e5c27860bf5821fbe198259a53a8623df83e99cb9786f27`.

## Phase 1F commands

```powershell
.\.venv\Scripts\python.exe tests\phase_1f_fixture_builders.py --write
.\.venv\Scripts\python.exe -m squeeze_core validate tests\fixtures\evidence\normalized_phase_1f_point_in_time.jsonl
.\.venv\Scripts\python.exe -m squeeze_core replay tests\fixtures\evidence\normalized_phase_1f_point_in_time.jsonl --mode strict
.\.venv\Scripts\python.exe -m squeeze_core normalize-provider --provider halts --input tests\fixtures\providers\halts\representative_cases.json --context tests\fixtures\providers\halts\context.json --case halt-complete-v1
.\.venv\Scripts\python.exe -m squeeze_core build-evidence-timeline --input tests\fixtures\evidence\normalized_phase_1f_point_in_time.jsonl --symbol TESTA --as-of-file tests\fixtures\evidence\halt_resumption_timeline.json
.\.venv\Scripts\python.exe -m squeeze_core build-halt-state --input tests\fixtures\evidence\normalized_phase_1f_point_in_time.jsonl --symbol TESTA --as-of 2026-01-15T15:31:00Z
```

SEC fixtures are representative or synthetic only. Repeated generation must preserve mixed JSONL, replay, timeline, and bundle bytes, and every Phase 1A–1D compatibility hash.

## Phase 2V commands

```powershell
.\.venv\Scripts\python.exe scripts\generate_phase_2v_anchors.py
.\.venv\Scripts\python.exe -m squeeze_core build-candidate-validation --case-spec tests\fixtures\validation\biya_validation_case.json --output build\validation\biya-validation.json
.\.venv\Scripts\python.exe -m squeeze_core export-validation-demo --validation-case build\validation\biya-validation.json --output apps\biya-validation-demo\data\biya-case.json
.\.venv\Scripts\python.exe -m pytest tests\validation --basetemp=.pytest-run-phase2v-validation
```

Run the anchor generator at least twice and compare bytes; the manifest, the comparison-case manifest, the fixture-provenance metadata, and the demo payload must all be byte-identical. The CLI and the public export must likewise be byte-identical across repeated runs.

Phase 2V fixtures are classified in `tests/fixtures/validation/phase_2v_fixture_metadata.json`. `SANITIZED_LOCAL_ARTIFACT` entries trace to an artifact id recorded in the BIYA artifact inventory; `SYNTHETIC_EDGE_CASE` entries are constructed to exercise a branch and are never presented as recorded evidence. No fixture may contain an absolute local path or a provider credential, and a test scans for both.

One hash collision is expected and explained: `mixed_phase_2v_output` equals `serialized_phase_2v_collection` because canonical JSON array serialization is exactly the concatenation of element bytes. Phase 2C and Phase 2D record the same property for their own manifests. Any other collision fails the suite.

## Phase 3A verification

`tests/evaluation` covers frozen models, exact enums, policy provenance, all six outcomes,
momentum, short pressure, catalysts, evidence validity, aggregation, BIYA boundaries, CLI, and
42 anchors. Run `scripts/generate_phase_3a_anchors.py` twice and compare every file under
`tests/fixtures/evaluation`. The full compatibility suite and all Phase 1–2V manifest diffs must
remain clean.

## Phase 3B verification

`tests/research` covers every detection, outcome, classification, registry, ordering, batch, summary, missingness, dataset, export, BIYA, CLI, identity, isolation, and partial-window branch. `tests/compatibility/test_phase_3b_compatibility.py` proves that all prior runtime packages and pre-3B fixture families remain byte-unchanged from `b7c7394d5fe8ee16bd3bd1482ce218a203162104`.

Run `scripts/generate_phase_3b_anchors.py` twice and compare every research fixture. Run both Phase 3B CLI commands twice for JSON, JSONL, and CSV outputs, and separately build both BIYA boundaries twice. Then run research, evaluation, validation, readiness, metrics, compatibility, and the complete suite with fresh explicit `--basetemp` paths.

## Phase 3C verification

`tests/analysis` covers contracts, policies, identities, cohort predicates, outcome-blind selection, exact proportions, fixed-arithmetic Wilson intervals, sample size, symbol dependence, confusion matrices, prevalence, missingness, registry quality, runner composition, serialization, reports, BIYA, standard cohorts, CLI behavior, 38 anchors, and AST isolation. `tests/compatibility/test_phase_3c_compatibility.py` pins schema `1.0.0`, prior runtime packages, prior fixture families, and all nine Phase 1–3B manifests.

Run `scripts/generate_phase_3c_anchors.py` twice and compare every file in `tests/fixtures/analysis`. Run both Phase 3C CLI commands twice and compare output bytes. All suites remain offline and use fresh explicit `--basetemp` directories.

## Phase 3D verification

`tests/acquisition` covers frozen contracts, policy identity, artifact hashing, time-separated provenance, identity conflicts, eligibility, boundary freeze, leakage, lifecycle, migrations, Phase 3B adapters, serialization, reports, CLI status, fixture regeneration, 40 anchors, documentation, and AST isolation. `tests/compatibility/test_phase_3d_compatibility.py` proves additive runtime changes and byte-unchanged Phase 1–3C fixture families and manifests from `14d35abfc9aacc6f2f4adaa3ad264950ec556d17`.

Generate the 20 acquisition fixtures twice and compare bytes. Run all four Phase 3D commands twice with explicit inputs, then run acquisition, analysis, research, evaluation, validation, readiness, metrics, compatibility, and the full suite with fresh `--basetemp` paths.
