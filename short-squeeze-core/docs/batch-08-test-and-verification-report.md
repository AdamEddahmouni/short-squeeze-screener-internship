> Companion to [batch-08-phase3a-request-result-freeze-plan.md](batch-08-phase3a-request-result-freeze-plan.md).

# Batch 08 — Test and Verification Report

## 1. Entry gates (all passed before any modification)

| Gate | Expected | Observed |
| --- | --- | --- |
| Branch | `batch/phase-3d-operation-specific-readiness-07` | matched |
| HEAD | `238986695c2bc053d54a6fd1037cdb145e9c5781` | matched |
| Working tree | clean except untracked `docs/phase-3c-complete-handoff.md` | matched |
| Remotes | none | matched |
| `phase-1-rc1^{}` | `f903d4d144d3f7e9717b1ab8e684da406d7968fb` | matched |
| Baseline suite | 2,256 passed / 1 skipped / 0 failed | JUnit XML: 2,257 tests, 1 skipped, 0 failures, 0 errors |
| Batch 05 private raw hashes | 26 artifacts / 0 mismatches | matched |
| Archived parent HEAD | `0897562e05d75b812dd284de81dfafdfa1dea916` | matched |
| Archived nested submodule | `6dbefd1a6b271bfc48106c4aa002f211735551cd` | matched |

Baseline reproduced with a fresh explicit `--basetemp=.pytest-run-b08-baseline` and
`-p no:cacheprovider`; the locked `.pytest-tmp` was not used and no `.pytest-run-*`
directory was deleted.

## 2. Test files added

| File | Tests | Scope |
| --- | --- | --- |
| `tests/acquisition/test_batch08_phase3a_freeze.py` | 52 | freeze semantics, isolation, determinism, leakage, rule outcomes |
| `tests/acquisition/test_batch08_cli_and_documentation.py` | 11 | offline CLI round-trip, tamper detection, required documentation |

All tests use the committed synthetic Batch 05-shaped fixture under
`tests/fixtures/acquisition/batch08/synthetic-batch05/`. No real provider value is asserted
or committed.

## 3. Required coverage map

| Required check | Test |
| --- | --- |
| exact Batch 07 checkpoint / policy versions | `test_frozen_policy_versions_are_exact` |
| exact 13-case source order | `test_cohort_source_order_is_exact_and_unreordered` |
| exact boundary | `test_frozen_boundary_is_exact`, `test_boundary_ids_match_the_recomputed_batch01_freeze` |
| global preflight remains `PREFLIGHT_REJECTED` | `test_global_preflight_remains_rejected_and_unchanged` |
| Batch 07 readiness consumed unchanged | `test_batch07_readiness_is_consumed_unchanged` |
| only detection-context OHLCV can be opened | `test_only_detection_context_artifacts_may_be_opened` |
| forward OHLCV access hard-fails | `test_forward_artifact_access_hard_fails` |
| Phase 3B outcome access hard-fails | `test_phase3b_outcome_artifact_access_hard_fails` |
| no forward/outcome access recorded | `test_no_forward_or_outcome_access_is_recorded` |
| forward identity cited without opening | `test_forward_artifact_identity_is_recorded_without_opening_it` |
| no network, no `ibapi` | `test_package_imports_no_network_or_ibapi` |
| canonical Phase 2 metric reused | `test_percentage_change_minimum_uses_only_the_canonical_admissible_metric` |
| no ad hoc percentage formula | `test_package_contains_no_percentage_arithmetic` |
| existing evaluator, not a replacement | `test_the_existing_evaluator_produces_every_outcome` |
| no manual rule-outcome assignment | `test_package_never_names_a_rule_outcome_value` |
| all 25 rules present and ordered | `test_all_twenty_five_rules_present_and_ordered_per_case` |
| `MARKET_DATA_AVAILABLE` supported | `test_market_data_available_is_supported_and_evaluated` |
| `COMPLETED_BAR_AVAILABLE` supported | `test_completed_bar_available_is_supported_and_evaluated` |
| `PERCENTAGE_CHANGE_MINIMUM` admissible inputs only | `test_percentage_change_minimum_uses_only_the_canonical_admissible_metric`, `test_percentage_metric_threshold_is_inclusive_and_unchanged` |
| `PRICE_RANGE` receives no absolute-price evidence | `test_price_range_receives_no_absolute_price_evidence` |
| `RELATIVE_VOLUME_MINIMUM` receives no volume | `test_relative_volume_minimum_receives_no_volume_evidence`, `test_no_volume_is_ever_attached_to_a_request` |
| no float fabrication | `test_no_float_fabrication` |
| no short-pressure fabrication | `test_no_short_pressure_fabrication` |
| no catalyst fabrication | `test_no_catalyst_fabrication` |
| blocked rules never forced to `FAIL` | `test_blocked_rules_are_never_forced_to_fail` |
| null never substituted with zero | `test_missing_evidence_is_never_substituted_with_zero` |
| `EVIDENCE_VALIDITY` canonical behaviour pinned | `test_evidence_validity_outcomes_are_evaluator_determined` |
| requested domains derived from the policy | `test_requested_domains_are_derived_from_the_policy` |
| definitely-completed selection, envelope edges | `test_only_definitely_completed_bars_are_included` |
| START/END value invariance | `test_percentage_metric_value_is_invariant_to_the_timestamp_interpretation` |
| bounded supply changes no outcome | `test_supply_policy_widening_changes_counts_but_no_outcome` |
| receipt sensitivity disclosed | `test_local_retrieval_receipt_sensitivity_is_disclosed` |
| request frozen before result, result before any outcome | `test_freeze_ordering_places_request_before_result_before_any_outcome` |
| all 13 leakage audits pass | `test_all_thirteen_leakage_audits_pass` |
| evaluation fields carry no outcome token | `test_evaluation_input_fields_contain_no_outcome_token` |
| request and result ids deterministic | `test_request_and_result_identities_are_deterministic` |
| identity excludes wall clock and paths | `test_request_identity_excludes_wall_clock_and_paths` |
| generation byte-identical | `test_repeated_generation_is_byte_identical`, `test_regeneration_is_byte_identical` |
| committed golden byte-identical | `test_committed_synthetic_golden_report_matches_byte_for_byte` |
| artifact hashes and byte lengths recorded | `test_frozen_artifact_hashes_and_byte_lengths_are_recorded`, `test_case_manifest_records_hashes_and_byte_lengths` |
| no score/rank/recommendation fields | `test_no_model_carries_a_score_rank_or_recommendation_field` |
| no Phase 3B publication | `test_publication_readiness_preview_publishes_nothing` |
| no Phase 3E, no Phase 3B started | `test_phase3b_and_phase3e_remain_unstarted` |
| no real data committed | `test_real_private_outputs_are_gitignored`, `test_sanitized_report_contains_no_price_or_return_value` |
| Batch 05 private hashes unchanged | `test_batch05_private_hash_manifest_is_untouched_by_this_batch` |
| Batch 07 golden unchanged | `test_batch07_golden_report_is_unchanged` |
| schema remains `1.0.0` | `test_schema_version_remains_1_0_0` |
| required documentation exists | `test_all_required_batch08_documents_exist` |
| Batch 09 handoff is a real document | `test_batch09_handoff_is_a_real_document` |
| documents make no predictive/trading claim | `test_batch08_documents_make_no_predictive_or_trading_claim` |
| CLI offline round-trip and tamper detection | `test_generate_then_verify_round_trips`, `test_verify_reports_a_mismatch_when_bytes_change` |

## 4. Verification actions performed

1. Verified starting branch and HEAD.
2. Reproduced the baseline from authoritative JUnit XML.
3. Verified Batch 01–07 committed artifacts via the full suite.
4. Verified Batch 05 private hashes: 26 artifacts, 0 mismatches.
5. Created `batch/phase-3d-phase3a-freeze-08` from the Batch 07 HEAD.
6. Inspected the Phase 3A request, policy, evaluator, result, identity, and serialization
   contracts, and empirically probed evaluator behaviour on synthetic input before freezing
   any decision.
7. Preregistered and committed the plan before constructing any real request or opening any
   permitted private OHLCV.
8. Implemented the thin admissible-evidence adapter.
9. Built exactly 13 canonical requests.
10. Froze request bytes and identities.
11. Executed the existing evaluator.
12. Froze exactly 13 results.
13. Ran exactly 13 leakage audits — all passed.
14. Generated the private outputs twice.
15. Compared private bytes: full recursive diff, identical; `verify-phase3a-freeze` reports
    26 artifacts / 0 mismatches.
16. Generated the committed synthetic fixture twice.
17. Compared committed bytes: identical, and asserted byte-for-byte in tests.
18. Ran the focused Batch 08 tests.
19. Ran the acquisition, evaluation, metrics, and readiness suites.
20. Ran one authoritative final full suite.
21. Verified the global preflight is unchanged and still `PREFLIGHT_REJECTED`.
22. Verified no forward OHLCV was read.
23. Verified no outcome was accessed.
24. Verified no new fetch occurred.
25. Verified prior bytes unchanged.
26. Verified archived topology unchanged.
27. Wrote the completion report.
28. Wrote the professor brief.
29. Created the actual Batch 09 handoff.
30. Reported the exact final HEAD.

## 5. Measurements recorded during implementation

Point-in-time evidence-bundle scaling (used to justify the bounded observation supply):

| Observations | `build_bar_series` | `build_point_in_time_evidence` |
| --- | --- | --- |
| 2 | 0.00 s | 0.00 s |
| 25 | 0.02 s | 0.11 s |
| 50 | 0.01 s | 0.42 s |
| 100 | 0.01 s | 1.82 s |
| 200 | 0.03 s | 12.73 s |

Per-case freeze time under the bounded supply: ≈0.6 s. Full 13-case freeze, both receipt
policies: a few seconds.

## 6. Result

The final full suite is reported in
[batch-08-completion-report.md](batch-08-completion-report.md). No prior test was modified,
skipped, or weakened; the single pre-existing skip is unchanged.
