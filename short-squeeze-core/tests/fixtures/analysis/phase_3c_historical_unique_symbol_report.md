# Phase 3C Descriptive Research Analysis

## Scope

- Analysis result ID: `711e68db-1075-5149-9eaa-f9c623b19d16`.
- Source dataset ID: `5d3461d4-387d-5200-b11a-3156e640fee9`.
- Source registry ID: `None`.
- This analysis is deterministic and descriptive only.

## Cohort Definition

- Cohort type: `HISTORICAL_COMPLETED_CASES`.
- Provenance classifications: `SANITIZED_PUBLIC_HISTORICAL_DATA`.

## Analysis Unit

- Analysis unit: `UNIQUE_SYMBOL_POLICY_SELECTED_BOUNDARY`.
- Statistics policy: `phase_3c_descriptive_statistics_policy.v1`.
- Interval policy: `phase_3c_interval_policy.v1` at confidence `0.95`.
- Sample-size policy: `phase_3c_sample_size_policy.v1`.

## Included Cases

- `BIYA_EARLIEST_BOUNDARY`

## Excluded Cases

- `BIYA_LATEST_BOUNDARY` — `ANALYSIS_COHORT_EXCLUDED_DUPLICATE_SYMBOL_BOUNDARY`
- `SYN_FALSE_NEGATIVE` — `ANALYSIS_COHORT_EXCLUDED_SYNTHETIC_CASE`
- `SYN_FALSE_POSITIVE` — `ANALYSIS_COHORT_EXCLUDED_SYNTHETIC_CASE`
- `SYN_MIXED_VOLATILE` — `ANALYSIS_COHORT_EXCLUDED_SYNTHETIC_CASE`
- `SYN_OUTCOME_INSUFFICIENT` — `ANALYSIS_COHORT_EXCLUDED_SYNTHETIC_CASE`
- `SYN_OUTCOME_UNKNOWN` — `ANALYSIS_COHORT_EXCLUDED_SYNTHETIC_CASE`
- `SYN_SUBSTANTIAL_DOWNWARD` — `ANALYSIS_COHORT_EXCLUDED_SYNTHETIC_CASE`
- `SYN_TRUE_NEGATIVE` — `ANALYSIS_COHORT_EXCLUDED_SYNTHETIC_CASE`
- `SYN_TRUE_POSITIVE` — `ANALYSIS_COHORT_EXCLUDED_SYNTHETIC_CASE`
- `SYN_UNEVALUABLE_CONFLICTED` — `ANALYSIS_COHORT_EXCLUDED_SYNTHETIC_CASE`
- `SYN_UNEVALUABLE_INSUFFICIENT` — `ANALYSIS_COHORT_EXCLUDED_SYNTHETIC_CASE`
- `SYN_UNEVALUABLE_UNKNOWN` — `ANALYSIS_COHORT_EXCLUDED_SYNTHETIC_CASE`

## Boundary Selection

- Policy: `earliest_detection_boundary_per_symbol.v1`.
- Selection is outcome-blind.
- Boundary count before policy selection: 2.

## Sample Size

- `ONE_OBSERVATION`: n=1, unique symbols=1, unit=`UNIQUE_SYMBOL_POLICY_SELECTED_BOUNDARY`.

## Dependence

- Dependence detected: `false`.
- Independence assumption satisfied: `true`.
- Repeated-boundary count: 0.
- Recommended analysis unit: `UNIQUE_SYMBOL_POLICY_SELECTED_BOUNDARY`.

## Counts

- Cases: 1.
- Unique symbols: 1.
- Boundaries: 2.
- Confusion matrix: TP=1, FP=0, TN=0, FN=0, unevaluable=0.

## Defined Rates

- confusion_matrix/sensitivity_descriptive_research_classification_rate: 1/1 (100%).
- confusion_matrix/positive_predictive_value_descriptive_research_classification_rate: 1/1 (100%).
- confusion_matrix/false_negative_descriptive_research_classification_rate: 0/1 (0%).
- detection_prevalence/detected_prevalence_among_all_cases: 1/1 (100%).
- detection_prevalence/not_detected_prevalence_among_all_cases: 0/1 (0%).
- detection_prevalence/unevaluable_prevalence_among_all_cases: 0/1 (0%).
- detection_prevalence/detection_rate_among_evaluable_cases: 1/1 (100%).
- outcome_prevalence/substantial_upward_move_prevalence_among_all_cases: 1/1 (100%).
- outcome_prevalence/no_substantial_upward_move_prevalence_among_all_cases: 0/1 (0%).
- outcome_prevalence/substantial_downward_move_prevalence_among_all_cases: 0/1 (0%).
- outcome_prevalence/mixed_or_volatile_prevalence_among_all_cases: 0/1 (0%).
- outcome_prevalence/outcome_unknown_prevalence_among_all_cases: 0/1 (0%).
- outcome_prevalence/outcome_insufficient_data_prevalence_among_all_cases: 0/1 (0%).
- outcome_prevalence/substantial_upward_move_prevalence_among_complete_outcomes: 1/1 (100%).
- classification_prevalence/true_positive_prevalence_among_all_cases: 1/1 (100%).
- classification_prevalence/false_positive_prevalence_among_all_cases: 0/1 (0%).
- classification_prevalence/true_negative_prevalence_among_all_cases: 0/1 (0%).
- classification_prevalence/false_negative_prevalence_among_all_cases: 0/1 (0%).
- classification_prevalence/unevaluable_prevalence_among_all_cases: 0/1 (0%).
- classification_prevalence/not_applicable_prevalence_among_all_cases: 0/1 (0%).
- classification_prevalence/research_classification_evaluability_rate_among_all_cases: 1/1 (100%).
- rule:BORROW_AVAILABILITY_CHANGE_MAXIMUM/pass_rate_among_all_cases: 0/1 (0%).
- rule:BORROW_AVAILABILITY_CHANGE_MAXIMUM/unknown_rate_among_all_cases: 1/1 (100%).
- rule:BORROW_AVAILABILITY_CHANGE_MAXIMUM/conflicted_rate_among_all_cases: 0/1 (0%).
- rule:BORROW_AVAILABILITY_CHANGE_MAXIMUM/insufficient_data_rate_among_all_cases: 0/1 (0%).
- rule:BORROW_AVAILABILITY_CHANGE_MAXIMUM/not_applicable_rate_among_all_cases: 0/1 (0%).
- rule:BORROW_AVAILABILITY_MAXIMUM/pass_rate_among_all_cases: 0/1 (0%).
- rule:BORROW_AVAILABILITY_MAXIMUM/unknown_rate_among_all_cases: 1/1 (100%).
- rule:BORROW_AVAILABILITY_MAXIMUM/conflicted_rate_among_all_cases: 0/1 (0%).
- rule:BORROW_AVAILABILITY_MAXIMUM/insufficient_data_rate_among_all_cases: 0/1 (0%).
- rule:BORROW_AVAILABILITY_MAXIMUM/not_applicable_rate_among_all_cases: 0/1 (0%).
- rule:BORROW_FEE_CHANGE_MINIMUM/pass_rate_among_all_cases: 0/1 (0%).
- rule:BORROW_FEE_CHANGE_MINIMUM/unknown_rate_among_all_cases: 1/1 (100%).
- rule:BORROW_FEE_CHANGE_MINIMUM/conflicted_rate_among_all_cases: 0/1 (0%).
- rule:BORROW_FEE_CHANGE_MINIMUM/insufficient_data_rate_among_all_cases: 0/1 (0%).
- rule:BORROW_FEE_CHANGE_MINIMUM/not_applicable_rate_among_all_cases: 0/1 (0%).
- rule:BORROW_FEE_MINIMUM/pass_rate_among_all_cases: 0/1 (0%).
- rule:BORROW_FEE_MINIMUM/unknown_rate_among_all_cases: 1/1 (100%).
- rule:BORROW_FEE_MINIMUM/conflicted_rate_among_all_cases: 0/1 (0%).
- rule:BORROW_FEE_MINIMUM/insufficient_data_rate_among_all_cases: 0/1 (0%).
- rule:BORROW_FEE_MINIMUM/not_applicable_rate_among_all_cases: 0/1 (0%).
- rule:COMPLETED_BAR_AVAILABLE/pass_rate_among_all_cases: 1/1 (100%).
- rule:COMPLETED_BAR_AVAILABLE/pass_rate_among_evaluable_cases: 1/1 (100%).
- rule:COMPLETED_BAR_AVAILABLE/fail_rate_among_evaluable_cases: 0/1 (0%).
- rule:COMPLETED_BAR_AVAILABLE/unknown_rate_among_all_cases: 0/1 (0%).
- rule:COMPLETED_BAR_AVAILABLE/conflicted_rate_among_all_cases: 0/1 (0%).
- rule:COMPLETED_BAR_AVAILABLE/insufficient_data_rate_among_all_cases: 0/1 (0%).
- rule:COMPLETED_BAR_AVAILABLE/not_applicable_rate_among_all_cases: 0/1 (0%).
- rule:CORPORATE_ACTION_CONTEXT_AVAILABLE/pass_rate_among_all_cases: 1/1 (100%).
- rule:CORPORATE_ACTION_CONTEXT_AVAILABLE/pass_rate_among_evaluable_cases: 1/1 (100%).
- rule:CORPORATE_ACTION_CONTEXT_AVAILABLE/fail_rate_among_evaluable_cases: 0/1 (0%).
- rule:CORPORATE_ACTION_CONTEXT_AVAILABLE/unknown_rate_among_all_cases: 0/1 (0%).
- rule:CORPORATE_ACTION_CONTEXT_AVAILABLE/conflicted_rate_among_all_cases: 0/1 (0%).
- rule:CORPORATE_ACTION_CONTEXT_AVAILABLE/insufficient_data_rate_among_all_cases: 0/1 (0%).
- rule:CORPORATE_ACTION_CONTEXT_AVAILABLE/not_applicable_rate_among_all_cases: 0/1 (0%).
- rule:DAYS_TO_COVER_MINIMUM/pass_rate_among_all_cases: 0/1 (0%).
- rule:DAYS_TO_COVER_MINIMUM/unknown_rate_among_all_cases: 1/1 (100%).
- rule:DAYS_TO_COVER_MINIMUM/conflicted_rate_among_all_cases: 0/1 (0%).
- rule:DAYS_TO_COVER_MINIMUM/insufficient_data_rate_among_all_cases: 0/1 (0%).
- rule:DAYS_TO_COVER_MINIMUM/not_applicable_rate_among_all_cases: 0/1 (0%).
- rule:FLOAT_MAXIMUM/pass_rate_among_all_cases: 0/1 (0%).
- rule:FLOAT_MAXIMUM/unknown_rate_among_all_cases: 1/1 (100%).
- rule:FLOAT_MAXIMUM/conflicted_rate_among_all_cases: 0/1 (0%).
- rule:FLOAT_MAXIMUM/insufficient_data_rate_among_all_cases: 0/1 (0%).
- rule:FLOAT_MAXIMUM/not_applicable_rate_among_all_cases: 0/1 (0%).
- rule:MARKET_DATA_AVAILABLE/pass_rate_among_all_cases: 1/1 (100%).
- rule:MARKET_DATA_AVAILABLE/pass_rate_among_evaluable_cases: 1/1 (100%).
- rule:MARKET_DATA_AVAILABLE/fail_rate_among_evaluable_cases: 0/1 (0%).
- rule:MARKET_DATA_AVAILABLE/unknown_rate_among_all_cases: 0/1 (0%).
- rule:MARKET_DATA_AVAILABLE/conflicted_rate_among_all_cases: 0/1 (0%).
- rule:MARKET_DATA_AVAILABLE/insufficient_data_rate_among_all_cases: 0/1 (0%).
- rule:MARKET_DATA_AVAILABLE/not_applicable_rate_among_all_cases: 0/1 (0%).
- rule:NEWS_AVAILABLE/pass_rate_among_all_cases: 1/1 (100%).
- rule:NEWS_AVAILABLE/pass_rate_among_evaluable_cases: 1/1 (100%).
- rule:NEWS_AVAILABLE/fail_rate_among_evaluable_cases: 0/1 (0%).
- rule:NEWS_AVAILABLE/unknown_rate_among_all_cases: 0/1 (0%).
- rule:NEWS_AVAILABLE/conflicted_rate_among_all_cases: 0/1 (0%).
- rule:NEWS_AVAILABLE/insufficient_data_rate_among_all_cases: 0/1 (0%).
- rule:NEWS_AVAILABLE/not_applicable_rate_among_all_cases: 0/1 (0%).
- rule:NEWS_AVAILABLE_BEFORE_AS_OF/pass_rate_among_all_cases: 1/1 (100%).
- rule:NEWS_AVAILABLE_BEFORE_AS_OF/pass_rate_among_evaluable_cases: 1/1 (100%).
- rule:NEWS_AVAILABLE_BEFORE_AS_OF/fail_rate_among_evaluable_cases: 0/1 (0%).
- rule:NEWS_AVAILABLE_BEFORE_AS_OF/unknown_rate_among_all_cases: 0/1 (0%).
- rule:NEWS_AVAILABLE_BEFORE_AS_OF/conflicted_rate_among_all_cases: 0/1 (0%).
- rule:NEWS_AVAILABLE_BEFORE_AS_OF/insufficient_data_rate_among_all_cases: 0/1 (0%).
- rule:NEWS_AVAILABLE_BEFORE_AS_OF/not_applicable_rate_among_all_cases: 0/1 (0%).
- rule:NEWS_TIMESTAMP_KNOWN/pass_rate_among_all_cases: 1/1 (100%).
- rule:NEWS_TIMESTAMP_KNOWN/pass_rate_among_evaluable_cases: 1/1 (100%).
- rule:NEWS_TIMESTAMP_KNOWN/fail_rate_among_evaluable_cases: 0/1 (0%).
- rule:NEWS_TIMESTAMP_KNOWN/unknown_rate_among_all_cases: 0/1 (0%).
- rule:NEWS_TIMESTAMP_KNOWN/conflicted_rate_among_all_cases: 0/1 (0%).
- rule:NEWS_TIMESTAMP_KNOWN/insufficient_data_rate_among_all_cases: 0/1 (0%).
- rule:NEWS_TIMESTAMP_KNOWN/not_applicable_rate_among_all_cases: 0/1 (0%).
- rule:NO_DEFAULT_SUBSTITUTION/pass_rate_among_all_cases: 1/1 (100%).
- rule:NO_DEFAULT_SUBSTITUTION/pass_rate_among_evaluable_cases: 1/1 (100%).
- rule:NO_DEFAULT_SUBSTITUTION/fail_rate_among_evaluable_cases: 0/1 (0%).
- rule:NO_DEFAULT_SUBSTITUTION/unknown_rate_among_all_cases: 0/1 (0%).
- rule:NO_DEFAULT_SUBSTITUTION/conflicted_rate_among_all_cases: 0/1 (0%).
- rule:NO_DEFAULT_SUBSTITUTION/insufficient_data_rate_among_all_cases: 0/1 (0%).
- rule:NO_DEFAULT_SUBSTITUTION/not_applicable_rate_among_all_cases: 0/1 (0%).
- rule:NO_MATERIAL_CONFLICTS/pass_rate_among_all_cases: 1/1 (100%).
- rule:NO_MATERIAL_CONFLICTS/pass_rate_among_evaluable_cases: 1/1 (100%).
- rule:NO_MATERIAL_CONFLICTS/fail_rate_among_evaluable_cases: 0/1 (0%).
- rule:NO_MATERIAL_CONFLICTS/unknown_rate_among_all_cases: 0/1 (0%).
- rule:NO_MATERIAL_CONFLICTS/conflicted_rate_among_all_cases: 0/1 (0%).
- rule:NO_MATERIAL_CONFLICTS/insufficient_data_rate_among_all_cases: 0/1 (0%).
- rule:NO_MATERIAL_CONFLICTS/not_applicable_rate_among_all_cases: 0/1 (0%).
- rule:PERCENTAGE_CHANGE_MINIMUM/pass_rate_among_all_cases: 0/1 (0%).
- rule:PERCENTAGE_CHANGE_MINIMUM/unknown_rate_among_all_cases: 1/1 (100%).
- rule:PERCENTAGE_CHANGE_MINIMUM/conflicted_rate_among_all_cases: 0/1 (0%).
- rule:PERCENTAGE_CHANGE_MINIMUM/insufficient_data_rate_among_all_cases: 0/1 (0%).
- rule:PERCENTAGE_CHANGE_MINIMUM/not_applicable_rate_among_all_cases: 0/1 (0%).
- rule:POINT_IN_TIME_ELIGIBLE/pass_rate_among_all_cases: 1/1 (100%).
- rule:POINT_IN_TIME_ELIGIBLE/pass_rate_among_evaluable_cases: 1/1 (100%).
- rule:POINT_IN_TIME_ELIGIBLE/fail_rate_among_evaluable_cases: 0/1 (0%).
- rule:POINT_IN_TIME_ELIGIBLE/unknown_rate_among_all_cases: 0/1 (0%).
- rule:POINT_IN_TIME_ELIGIBLE/conflicted_rate_among_all_cases: 0/1 (0%).
- rule:POINT_IN_TIME_ELIGIBLE/insufficient_data_rate_among_all_cases: 0/1 (0%).
- rule:POINT_IN_TIME_ELIGIBLE/not_applicable_rate_among_all_cases: 0/1 (0%).
- rule:PRICE_RANGE/pass_rate_among_all_cases: 1/1 (100%).
- rule:PRICE_RANGE/pass_rate_among_evaluable_cases: 1/1 (100%).
- rule:PRICE_RANGE/fail_rate_among_evaluable_cases: 0/1 (0%).
- rule:PRICE_RANGE/unknown_rate_among_all_cases: 0/1 (0%).
- rule:PRICE_RANGE/conflicted_rate_among_all_cases: 0/1 (0%).
- rule:PRICE_RANGE/insufficient_data_rate_among_all_cases: 0/1 (0%).
- rule:PRICE_RANGE/not_applicable_rate_among_all_cases: 0/1 (0%).
- rule:PROVIDER_SCOPE_EXPLICIT/pass_rate_among_all_cases: 1/1 (100%).
- rule:PROVIDER_SCOPE_EXPLICIT/pass_rate_among_evaluable_cases: 1/1 (100%).
- rule:PROVIDER_SCOPE_EXPLICIT/fail_rate_among_evaluable_cases: 0/1 (0%).
- rule:PROVIDER_SCOPE_EXPLICIT/unknown_rate_among_all_cases: 0/1 (0%).
- rule:PROVIDER_SCOPE_EXPLICIT/conflicted_rate_among_all_cases: 0/1 (0%).
- rule:PROVIDER_SCOPE_EXPLICIT/insufficient_data_rate_among_all_cases: 0/1 (0%).
- rule:PROVIDER_SCOPE_EXPLICIT/not_applicable_rate_among_all_cases: 0/1 (0%).
- rule:PUBLISHED_SHORT_INTEREST_AVAILABLE/pass_rate_among_all_cases: 0/1 (0%).
- rule:PUBLISHED_SHORT_INTEREST_AVAILABLE/unknown_rate_among_all_cases: 1/1 (100%).
- rule:PUBLISHED_SHORT_INTEREST_AVAILABLE/conflicted_rate_among_all_cases: 0/1 (0%).
- rule:PUBLISHED_SHORT_INTEREST_AVAILABLE/insufficient_data_rate_among_all_cases: 0/1 (0%).
- rule:PUBLISHED_SHORT_INTEREST_AVAILABLE/not_applicable_rate_among_all_cases: 0/1 (0%).
- rule:RELATIVE_VOLUME_MINIMUM/pass_rate_among_all_cases: 0/1 (0%).
- rule:RELATIVE_VOLUME_MINIMUM/unknown_rate_among_all_cases: 1/1 (100%).
- rule:RELATIVE_VOLUME_MINIMUM/conflicted_rate_among_all_cases: 0/1 (0%).
- rule:RELATIVE_VOLUME_MINIMUM/insufficient_data_rate_among_all_cases: 0/1 (0%).
- rule:RELATIVE_VOLUME_MINIMUM/not_applicable_rate_among_all_cases: 0/1 (0%).
- rule:REQUIRED_DOMAINS_PRESENT/pass_rate_among_all_cases: 0/1 (0%).
- rule:REQUIRED_DOMAINS_PRESENT/unknown_rate_among_all_cases: 1/1 (100%).
- rule:REQUIRED_DOMAINS_PRESENT/conflicted_rate_among_all_cases: 0/1 (0%).
- rule:REQUIRED_DOMAINS_PRESENT/insufficient_data_rate_among_all_cases: 0/1 (0%).
- rule:REQUIRED_DOMAINS_PRESENT/not_applicable_rate_among_all_cases: 0/1 (0%).
- rule:REQUIRED_HISTORY_SUFFICIENT/pass_rate_among_all_cases: 0/1 (0%).
- rule:REQUIRED_HISTORY_SUFFICIENT/unknown_rate_among_all_cases: 0/1 (0%).
- rule:REQUIRED_HISTORY_SUFFICIENT/conflicted_rate_among_all_cases: 0/1 (0%).
- rule:REQUIRED_HISTORY_SUFFICIENT/insufficient_data_rate_among_all_cases: 1/1 (100%).
- rule:REQUIRED_HISTORY_SUFFICIENT/not_applicable_rate_among_all_cases: 0/1 (0%).
- rule:REQUIRED_UNITS_COMPATIBLE/pass_rate_among_all_cases: 1/1 (100%).
- rule:REQUIRED_UNITS_COMPATIBLE/pass_rate_among_evaluable_cases: 1/1 (100%).
- rule:REQUIRED_UNITS_COMPATIBLE/fail_rate_among_evaluable_cases: 0/1 (0%).
- rule:REQUIRED_UNITS_COMPATIBLE/unknown_rate_among_all_cases: 0/1 (0%).
- rule:REQUIRED_UNITS_COMPATIBLE/conflicted_rate_among_all_cases: 0/1 (0%).
- rule:REQUIRED_UNITS_COMPATIBLE/insufficient_data_rate_among_all_cases: 0/1 (0%).
- rule:REQUIRED_UNITS_COMPATIBLE/not_applicable_rate_among_all_cases: 0/1 (0%).
- rule:SEC_FILING_AVAILABLE/pass_rate_among_all_cases: 0/1 (0%).
- rule:SEC_FILING_AVAILABLE/unknown_rate_among_all_cases: 1/1 (100%).
- rule:SEC_FILING_AVAILABLE/conflicted_rate_among_all_cases: 0/1 (0%).
- rule:SEC_FILING_AVAILABLE/insufficient_data_rate_among_all_cases: 0/1 (0%).
- rule:SEC_FILING_AVAILABLE/not_applicable_rate_among_all_cases: 0/1 (0%).
- rule:SHORT_INTEREST_PERCENTAGE_CHANGE_MINIMUM/pass_rate_among_all_cases: 0/1 (0%).
- rule:SHORT_INTEREST_PERCENTAGE_CHANGE_MINIMUM/unknown_rate_among_all_cases: 1/1 (100%).
- rule:SHORT_INTEREST_PERCENTAGE_CHANGE_MINIMUM/conflicted_rate_among_all_cases: 0/1 (0%).
- rule:SHORT_INTEREST_PERCENTAGE_CHANGE_MINIMUM/insufficient_data_rate_among_all_cases: 0/1 (0%).
- rule:SHORT_INTEREST_PERCENTAGE_CHANGE_MINIMUM/not_applicable_rate_among_all_cases: 0/1 (0%).

## Undefined Rates

- confusion_matrix/specificity_descriptive_research_classification_rate: Undefined (0/0; ZERO_DENOMINATOR).
- confusion_matrix/negative_predictive_value_descriptive_research_classification_rate: Undefined (0/0; ZERO_DENOMINATOR).
- confusion_matrix/false_positive_descriptive_research_classification_rate: Undefined (0/0; ZERO_DENOMINATOR).
- rule:BORROW_AVAILABILITY_CHANGE_MAXIMUM/pass_rate_among_evaluable_cases: Undefined (0/0; ZERO_DENOMINATOR).
- rule:BORROW_AVAILABILITY_CHANGE_MAXIMUM/fail_rate_among_evaluable_cases: Undefined (0/0; ZERO_DENOMINATOR).
- rule:BORROW_AVAILABILITY_MAXIMUM/pass_rate_among_evaluable_cases: Undefined (0/0; ZERO_DENOMINATOR).
- rule:BORROW_AVAILABILITY_MAXIMUM/fail_rate_among_evaluable_cases: Undefined (0/0; ZERO_DENOMINATOR).
- rule:BORROW_FEE_CHANGE_MINIMUM/pass_rate_among_evaluable_cases: Undefined (0/0; ZERO_DENOMINATOR).
- rule:BORROW_FEE_CHANGE_MINIMUM/fail_rate_among_evaluable_cases: Undefined (0/0; ZERO_DENOMINATOR).
- rule:BORROW_FEE_MINIMUM/pass_rate_among_evaluable_cases: Undefined (0/0; ZERO_DENOMINATOR).
- rule:BORROW_FEE_MINIMUM/fail_rate_among_evaluable_cases: Undefined (0/0; ZERO_DENOMINATOR).
- rule:DAYS_TO_COVER_MINIMUM/pass_rate_among_evaluable_cases: Undefined (0/0; ZERO_DENOMINATOR).
- rule:DAYS_TO_COVER_MINIMUM/fail_rate_among_evaluable_cases: Undefined (0/0; ZERO_DENOMINATOR).
- rule:FLOAT_MAXIMUM/pass_rate_among_evaluable_cases: Undefined (0/0; ZERO_DENOMINATOR).
- rule:FLOAT_MAXIMUM/fail_rate_among_evaluable_cases: Undefined (0/0; ZERO_DENOMINATOR).
- rule:PERCENTAGE_CHANGE_MINIMUM/pass_rate_among_evaluable_cases: Undefined (0/0; ZERO_DENOMINATOR).
- rule:PERCENTAGE_CHANGE_MINIMUM/fail_rate_among_evaluable_cases: Undefined (0/0; ZERO_DENOMINATOR).
- rule:PUBLISHED_SHORT_INTEREST_AVAILABLE/pass_rate_among_evaluable_cases: Undefined (0/0; ZERO_DENOMINATOR).
- rule:PUBLISHED_SHORT_INTEREST_AVAILABLE/fail_rate_among_evaluable_cases: Undefined (0/0; ZERO_DENOMINATOR).
- rule:RELATIVE_VOLUME_MINIMUM/pass_rate_among_evaluable_cases: Undefined (0/0; ZERO_DENOMINATOR).
- rule:RELATIVE_VOLUME_MINIMUM/fail_rate_among_evaluable_cases: Undefined (0/0; ZERO_DENOMINATOR).
- rule:REQUIRED_DOMAINS_PRESENT/pass_rate_among_evaluable_cases: Undefined (0/0; ZERO_DENOMINATOR).
- rule:REQUIRED_DOMAINS_PRESENT/fail_rate_among_evaluable_cases: Undefined (0/0; ZERO_DENOMINATOR).
- rule:REQUIRED_HISTORY_SUFFICIENT/pass_rate_among_evaluable_cases: Undefined (0/0; ZERO_DENOMINATOR).
- rule:REQUIRED_HISTORY_SUFFICIENT/fail_rate_among_evaluable_cases: Undefined (0/0; ZERO_DENOMINATOR).
- rule:SEC_FILING_AVAILABLE/pass_rate_among_evaluable_cases: Undefined (0/0; ZERO_DENOMINATOR).
- rule:SEC_FILING_AVAILABLE/fail_rate_among_evaluable_cases: Undefined (0/0; ZERO_DENOMINATOR).
- rule:SHORT_INTEREST_PERCENTAGE_CHANGE_MINIMUM/pass_rate_among_evaluable_cases: Undefined (0/0; ZERO_DENOMINATOR).
- rule:SHORT_INTEREST_PERCENTAGE_CHANGE_MINIMUM/fail_rate_among_evaluable_cases: Undefined (0/0; ZERO_DENOMINATOR).

## Confidence Intervals

- confusion_matrix/sensitivity_descriptive_research_classification_rate: [0.206549314377, 1.000000000000] using `WILSON_SCORE` at 0.95; independence satisfied=`true`.
- confusion_matrix/positive_predictive_value_descriptive_research_classification_rate: [0.206549314377, 1.000000000000] using `WILSON_SCORE` at 0.95; independence satisfied=`true`.
- confusion_matrix/false_negative_descriptive_research_classification_rate: [0E-12, 0.793450685623] using `WILSON_SCORE` at 0.95; independence satisfied=`true`.
- detection_prevalence/detected_prevalence_among_all_cases: [0.206549314377, 1.000000000000] using `WILSON_SCORE` at 0.95; independence satisfied=`true`.
- detection_prevalence/not_detected_prevalence_among_all_cases: [0E-12, 0.793450685623] using `WILSON_SCORE` at 0.95; independence satisfied=`true`.
- detection_prevalence/unevaluable_prevalence_among_all_cases: [0E-12, 0.793450685623] using `WILSON_SCORE` at 0.95; independence satisfied=`true`.
- detection_prevalence/detection_rate_among_evaluable_cases: [0.206549314377, 1.000000000000] using `WILSON_SCORE` at 0.95; independence satisfied=`true`.
- outcome_prevalence/substantial_upward_move_prevalence_among_all_cases: [0.206549314377, 1.000000000000] using `WILSON_SCORE` at 0.95; independence satisfied=`true`.
- outcome_prevalence/no_substantial_upward_move_prevalence_among_all_cases: [0E-12, 0.793450685623] using `WILSON_SCORE` at 0.95; independence satisfied=`true`.
- outcome_prevalence/substantial_downward_move_prevalence_among_all_cases: [0E-12, 0.793450685623] using `WILSON_SCORE` at 0.95; independence satisfied=`true`.
- outcome_prevalence/mixed_or_volatile_prevalence_among_all_cases: [0E-12, 0.793450685623] using `WILSON_SCORE` at 0.95; independence satisfied=`true`.
- outcome_prevalence/outcome_unknown_prevalence_among_all_cases: [0E-12, 0.793450685623] using `WILSON_SCORE` at 0.95; independence satisfied=`true`.
- outcome_prevalence/outcome_insufficient_data_prevalence_among_all_cases: [0E-12, 0.793450685623] using `WILSON_SCORE` at 0.95; independence satisfied=`true`.
- outcome_prevalence/substantial_upward_move_prevalence_among_complete_outcomes: [0.206549314377, 1.000000000000] using `WILSON_SCORE` at 0.95; independence satisfied=`true`.
- classification_prevalence/true_positive_prevalence_among_all_cases: [0.206549314377, 1.000000000000] using `WILSON_SCORE` at 0.95; independence satisfied=`true`.
- classification_prevalence/false_positive_prevalence_among_all_cases: [0E-12, 0.793450685623] using `WILSON_SCORE` at 0.95; independence satisfied=`true`.
- classification_prevalence/true_negative_prevalence_among_all_cases: [0E-12, 0.793450685623] using `WILSON_SCORE` at 0.95; independence satisfied=`true`.
- classification_prevalence/false_negative_prevalence_among_all_cases: [0E-12, 0.793450685623] using `WILSON_SCORE` at 0.95; independence satisfied=`true`.
- classification_prevalence/unevaluable_prevalence_among_all_cases: [0E-12, 0.793450685623] using `WILSON_SCORE` at 0.95; independence satisfied=`true`.
- classification_prevalence/not_applicable_prevalence_among_all_cases: [0E-12, 0.793450685623] using `WILSON_SCORE` at 0.95; independence satisfied=`true`.
- classification_prevalence/research_classification_evaluability_rate_among_all_cases: [0.206549314377, 1.000000000000] using `WILSON_SCORE` at 0.95; independence satisfied=`true`.
- rule:BORROW_AVAILABILITY_CHANGE_MAXIMUM/pass_rate_among_all_cases: [0E-12, 0.793450685623] using `WILSON_SCORE` at 0.95; independence satisfied=`true`.
- rule:BORROW_AVAILABILITY_CHANGE_MAXIMUM/unknown_rate_among_all_cases: [0.206549314377, 1.000000000000] using `WILSON_SCORE` at 0.95; independence satisfied=`true`.
- rule:BORROW_AVAILABILITY_CHANGE_MAXIMUM/conflicted_rate_among_all_cases: [0E-12, 0.793450685623] using `WILSON_SCORE` at 0.95; independence satisfied=`true`.
- rule:BORROW_AVAILABILITY_CHANGE_MAXIMUM/insufficient_data_rate_among_all_cases: [0E-12, 0.793450685623] using `WILSON_SCORE` at 0.95; independence satisfied=`true`.
- rule:BORROW_AVAILABILITY_CHANGE_MAXIMUM/not_applicable_rate_among_all_cases: [0E-12, 0.793450685623] using `WILSON_SCORE` at 0.95; independence satisfied=`true`.
- rule:BORROW_AVAILABILITY_MAXIMUM/pass_rate_among_all_cases: [0E-12, 0.793450685623] using `WILSON_SCORE` at 0.95; independence satisfied=`true`.
- rule:BORROW_AVAILABILITY_MAXIMUM/unknown_rate_among_all_cases: [0.206549314377, 1.000000000000] using `WILSON_SCORE` at 0.95; independence satisfied=`true`.
- rule:BORROW_AVAILABILITY_MAXIMUM/conflicted_rate_among_all_cases: [0E-12, 0.793450685623] using `WILSON_SCORE` at 0.95; independence satisfied=`true`.
- rule:BORROW_AVAILABILITY_MAXIMUM/insufficient_data_rate_among_all_cases: [0E-12, 0.793450685623] using `WILSON_SCORE` at 0.95; independence satisfied=`true`.
- rule:BORROW_AVAILABILITY_MAXIMUM/not_applicable_rate_among_all_cases: [0E-12, 0.793450685623] using `WILSON_SCORE` at 0.95; independence satisfied=`true`.
- rule:BORROW_FEE_CHANGE_MINIMUM/pass_rate_among_all_cases: [0E-12, 0.793450685623] using `WILSON_SCORE` at 0.95; independence satisfied=`true`.
- rule:BORROW_FEE_CHANGE_MINIMUM/unknown_rate_among_all_cases: [0.206549314377, 1.000000000000] using `WILSON_SCORE` at 0.95; independence satisfied=`true`.
- rule:BORROW_FEE_CHANGE_MINIMUM/conflicted_rate_among_all_cases: [0E-12, 0.793450685623] using `WILSON_SCORE` at 0.95; independence satisfied=`true`.
- rule:BORROW_FEE_CHANGE_MINIMUM/insufficient_data_rate_among_all_cases: [0E-12, 0.793450685623] using `WILSON_SCORE` at 0.95; independence satisfied=`true`.
- rule:BORROW_FEE_CHANGE_MINIMUM/not_applicable_rate_among_all_cases: [0E-12, 0.793450685623] using `WILSON_SCORE` at 0.95; independence satisfied=`true`.
- rule:BORROW_FEE_MINIMUM/pass_rate_among_all_cases: [0E-12, 0.793450685623] using `WILSON_SCORE` at 0.95; independence satisfied=`true`.
- rule:BORROW_FEE_MINIMUM/unknown_rate_among_all_cases: [0.206549314377, 1.000000000000] using `WILSON_SCORE` at 0.95; independence satisfied=`true`.
- rule:BORROW_FEE_MINIMUM/conflicted_rate_among_all_cases: [0E-12, 0.793450685623] using `WILSON_SCORE` at 0.95; independence satisfied=`true`.
- rule:BORROW_FEE_MINIMUM/insufficient_data_rate_among_all_cases: [0E-12, 0.793450685623] using `WILSON_SCORE` at 0.95; independence satisfied=`true`.
- rule:BORROW_FEE_MINIMUM/not_applicable_rate_among_all_cases: [0E-12, 0.793450685623] using `WILSON_SCORE` at 0.95; independence satisfied=`true`.
- rule:COMPLETED_BAR_AVAILABLE/pass_rate_among_all_cases: [0.206549314377, 1.000000000000] using `WILSON_SCORE` at 0.95; independence satisfied=`true`.
- rule:COMPLETED_BAR_AVAILABLE/pass_rate_among_evaluable_cases: [0.206549314377, 1.000000000000] using `WILSON_SCORE` at 0.95; independence satisfied=`true`.
- rule:COMPLETED_BAR_AVAILABLE/fail_rate_among_evaluable_cases: [0E-12, 0.793450685623] using `WILSON_SCORE` at 0.95; independence satisfied=`true`.
- rule:COMPLETED_BAR_AVAILABLE/unknown_rate_among_all_cases: [0E-12, 0.793450685623] using `WILSON_SCORE` at 0.95; independence satisfied=`true`.
- rule:COMPLETED_BAR_AVAILABLE/conflicted_rate_among_all_cases: [0E-12, 0.793450685623] using `WILSON_SCORE` at 0.95; independence satisfied=`true`.
- rule:COMPLETED_BAR_AVAILABLE/insufficient_data_rate_among_all_cases: [0E-12, 0.793450685623] using `WILSON_SCORE` at 0.95; independence satisfied=`true`.
- rule:COMPLETED_BAR_AVAILABLE/not_applicable_rate_among_all_cases: [0E-12, 0.793450685623] using `WILSON_SCORE` at 0.95; independence satisfied=`true`.
- rule:CORPORATE_ACTION_CONTEXT_AVAILABLE/pass_rate_among_all_cases: [0.206549314377, 1.000000000000] using `WILSON_SCORE` at 0.95; independence satisfied=`true`.
- rule:CORPORATE_ACTION_CONTEXT_AVAILABLE/pass_rate_among_evaluable_cases: [0.206549314377, 1.000000000000] using `WILSON_SCORE` at 0.95; independence satisfied=`true`.
- rule:CORPORATE_ACTION_CONTEXT_AVAILABLE/fail_rate_among_evaluable_cases: [0E-12, 0.793450685623] using `WILSON_SCORE` at 0.95; independence satisfied=`true`.
- rule:CORPORATE_ACTION_CONTEXT_AVAILABLE/unknown_rate_among_all_cases: [0E-12, 0.793450685623] using `WILSON_SCORE` at 0.95; independence satisfied=`true`.
- rule:CORPORATE_ACTION_CONTEXT_AVAILABLE/conflicted_rate_among_all_cases: [0E-12, 0.793450685623] using `WILSON_SCORE` at 0.95; independence satisfied=`true`.
- rule:CORPORATE_ACTION_CONTEXT_AVAILABLE/insufficient_data_rate_among_all_cases: [0E-12, 0.793450685623] using `WILSON_SCORE` at 0.95; independence satisfied=`true`.
- rule:CORPORATE_ACTION_CONTEXT_AVAILABLE/not_applicable_rate_among_all_cases: [0E-12, 0.793450685623] using `WILSON_SCORE` at 0.95; independence satisfied=`true`.
- rule:DAYS_TO_COVER_MINIMUM/pass_rate_among_all_cases: [0E-12, 0.793450685623] using `WILSON_SCORE` at 0.95; independence satisfied=`true`.
- rule:DAYS_TO_COVER_MINIMUM/unknown_rate_among_all_cases: [0.206549314377, 1.000000000000] using `WILSON_SCORE` at 0.95; independence satisfied=`true`.
- rule:DAYS_TO_COVER_MINIMUM/conflicted_rate_among_all_cases: [0E-12, 0.793450685623] using `WILSON_SCORE` at 0.95; independence satisfied=`true`.
- rule:DAYS_TO_COVER_MINIMUM/insufficient_data_rate_among_all_cases: [0E-12, 0.793450685623] using `WILSON_SCORE` at 0.95; independence satisfied=`true`.
- rule:DAYS_TO_COVER_MINIMUM/not_applicable_rate_among_all_cases: [0E-12, 0.793450685623] using `WILSON_SCORE` at 0.95; independence satisfied=`true`.
- rule:FLOAT_MAXIMUM/pass_rate_among_all_cases: [0E-12, 0.793450685623] using `WILSON_SCORE` at 0.95; independence satisfied=`true`.
- rule:FLOAT_MAXIMUM/unknown_rate_among_all_cases: [0.206549314377, 1.000000000000] using `WILSON_SCORE` at 0.95; independence satisfied=`true`.
- rule:FLOAT_MAXIMUM/conflicted_rate_among_all_cases: [0E-12, 0.793450685623] using `WILSON_SCORE` at 0.95; independence satisfied=`true`.
- rule:FLOAT_MAXIMUM/insufficient_data_rate_among_all_cases: [0E-12, 0.793450685623] using `WILSON_SCORE` at 0.95; independence satisfied=`true`.
- rule:FLOAT_MAXIMUM/not_applicable_rate_among_all_cases: [0E-12, 0.793450685623] using `WILSON_SCORE` at 0.95; independence satisfied=`true`.
- rule:MARKET_DATA_AVAILABLE/pass_rate_among_all_cases: [0.206549314377, 1.000000000000] using `WILSON_SCORE` at 0.95; independence satisfied=`true`.
- rule:MARKET_DATA_AVAILABLE/pass_rate_among_evaluable_cases: [0.206549314377, 1.000000000000] using `WILSON_SCORE` at 0.95; independence satisfied=`true`.
- rule:MARKET_DATA_AVAILABLE/fail_rate_among_evaluable_cases: [0E-12, 0.793450685623] using `WILSON_SCORE` at 0.95; independence satisfied=`true`.
- rule:MARKET_DATA_AVAILABLE/unknown_rate_among_all_cases: [0E-12, 0.793450685623] using `WILSON_SCORE` at 0.95; independence satisfied=`true`.
- rule:MARKET_DATA_AVAILABLE/conflicted_rate_among_all_cases: [0E-12, 0.793450685623] using `WILSON_SCORE` at 0.95; independence satisfied=`true`.
- rule:MARKET_DATA_AVAILABLE/insufficient_data_rate_among_all_cases: [0E-12, 0.793450685623] using `WILSON_SCORE` at 0.95; independence satisfied=`true`.
- rule:MARKET_DATA_AVAILABLE/not_applicable_rate_among_all_cases: [0E-12, 0.793450685623] using `WILSON_SCORE` at 0.95; independence satisfied=`true`.
- rule:NEWS_AVAILABLE/pass_rate_among_all_cases: [0.206549314377, 1.000000000000] using `WILSON_SCORE` at 0.95; independence satisfied=`true`.
- rule:NEWS_AVAILABLE/pass_rate_among_evaluable_cases: [0.206549314377, 1.000000000000] using `WILSON_SCORE` at 0.95; independence satisfied=`true`.
- rule:NEWS_AVAILABLE/fail_rate_among_evaluable_cases: [0E-12, 0.793450685623] using `WILSON_SCORE` at 0.95; independence satisfied=`true`.
- rule:NEWS_AVAILABLE/unknown_rate_among_all_cases: [0E-12, 0.793450685623] using `WILSON_SCORE` at 0.95; independence satisfied=`true`.
- rule:NEWS_AVAILABLE/conflicted_rate_among_all_cases: [0E-12, 0.793450685623] using `WILSON_SCORE` at 0.95; independence satisfied=`true`.
- rule:NEWS_AVAILABLE/insufficient_data_rate_among_all_cases: [0E-12, 0.793450685623] using `WILSON_SCORE` at 0.95; independence satisfied=`true`.
- rule:NEWS_AVAILABLE/not_applicable_rate_among_all_cases: [0E-12, 0.793450685623] using `WILSON_SCORE` at 0.95; independence satisfied=`true`.
- rule:NEWS_AVAILABLE_BEFORE_AS_OF/pass_rate_among_all_cases: [0.206549314377, 1.000000000000] using `WILSON_SCORE` at 0.95; independence satisfied=`true`.
- rule:NEWS_AVAILABLE_BEFORE_AS_OF/pass_rate_among_evaluable_cases: [0.206549314377, 1.000000000000] using `WILSON_SCORE` at 0.95; independence satisfied=`true`.
- rule:NEWS_AVAILABLE_BEFORE_AS_OF/fail_rate_among_evaluable_cases: [0E-12, 0.793450685623] using `WILSON_SCORE` at 0.95; independence satisfied=`true`.
- rule:NEWS_AVAILABLE_BEFORE_AS_OF/unknown_rate_among_all_cases: [0E-12, 0.793450685623] using `WILSON_SCORE` at 0.95; independence satisfied=`true`.
- rule:NEWS_AVAILABLE_BEFORE_AS_OF/conflicted_rate_among_all_cases: [0E-12, 0.793450685623] using `WILSON_SCORE` at 0.95; independence satisfied=`true`.
- rule:NEWS_AVAILABLE_BEFORE_AS_OF/insufficient_data_rate_among_all_cases: [0E-12, 0.793450685623] using `WILSON_SCORE` at 0.95; independence satisfied=`true`.
- rule:NEWS_AVAILABLE_BEFORE_AS_OF/not_applicable_rate_among_all_cases: [0E-12, 0.793450685623] using `WILSON_SCORE` at 0.95; independence satisfied=`true`.
- rule:NEWS_TIMESTAMP_KNOWN/pass_rate_among_all_cases: [0.206549314377, 1.000000000000] using `WILSON_SCORE` at 0.95; independence satisfied=`true`.
- rule:NEWS_TIMESTAMP_KNOWN/pass_rate_among_evaluable_cases: [0.206549314377, 1.000000000000] using `WILSON_SCORE` at 0.95; independence satisfied=`true`.
- rule:NEWS_TIMESTAMP_KNOWN/fail_rate_among_evaluable_cases: [0E-12, 0.793450685623] using `WILSON_SCORE` at 0.95; independence satisfied=`true`.
- rule:NEWS_TIMESTAMP_KNOWN/unknown_rate_among_all_cases: [0E-12, 0.793450685623] using `WILSON_SCORE` at 0.95; independence satisfied=`true`.
- rule:NEWS_TIMESTAMP_KNOWN/conflicted_rate_among_all_cases: [0E-12, 0.793450685623] using `WILSON_SCORE` at 0.95; independence satisfied=`true`.
- rule:NEWS_TIMESTAMP_KNOWN/insufficient_data_rate_among_all_cases: [0E-12, 0.793450685623] using `WILSON_SCORE` at 0.95; independence satisfied=`true`.
- rule:NEWS_TIMESTAMP_KNOWN/not_applicable_rate_among_all_cases: [0E-12, 0.793450685623] using `WILSON_SCORE` at 0.95; independence satisfied=`true`.
- rule:NO_DEFAULT_SUBSTITUTION/pass_rate_among_all_cases: [0.206549314377, 1.000000000000] using `WILSON_SCORE` at 0.95; independence satisfied=`true`.
- rule:NO_DEFAULT_SUBSTITUTION/pass_rate_among_evaluable_cases: [0.206549314377, 1.000000000000] using `WILSON_SCORE` at 0.95; independence satisfied=`true`.
- rule:NO_DEFAULT_SUBSTITUTION/fail_rate_among_evaluable_cases: [0E-12, 0.793450685623] using `WILSON_SCORE` at 0.95; independence satisfied=`true`.
- rule:NO_DEFAULT_SUBSTITUTION/unknown_rate_among_all_cases: [0E-12, 0.793450685623] using `WILSON_SCORE` at 0.95; independence satisfied=`true`.
- rule:NO_DEFAULT_SUBSTITUTION/conflicted_rate_among_all_cases: [0E-12, 0.793450685623] using `WILSON_SCORE` at 0.95; independence satisfied=`true`.
- rule:NO_DEFAULT_SUBSTITUTION/insufficient_data_rate_among_all_cases: [0E-12, 0.793450685623] using `WILSON_SCORE` at 0.95; independence satisfied=`true`.
- rule:NO_DEFAULT_SUBSTITUTION/not_applicable_rate_among_all_cases: [0E-12, 0.793450685623] using `WILSON_SCORE` at 0.95; independence satisfied=`true`.
- rule:NO_MATERIAL_CONFLICTS/pass_rate_among_all_cases: [0.206549314377, 1.000000000000] using `WILSON_SCORE` at 0.95; independence satisfied=`true`.
- rule:NO_MATERIAL_CONFLICTS/pass_rate_among_evaluable_cases: [0.206549314377, 1.000000000000] using `WILSON_SCORE` at 0.95; independence satisfied=`true`.
- rule:NO_MATERIAL_CONFLICTS/fail_rate_among_evaluable_cases: [0E-12, 0.793450685623] using `WILSON_SCORE` at 0.95; independence satisfied=`true`.
- rule:NO_MATERIAL_CONFLICTS/unknown_rate_among_all_cases: [0E-12, 0.793450685623] using `WILSON_SCORE` at 0.95; independence satisfied=`true`.
- rule:NO_MATERIAL_CONFLICTS/conflicted_rate_among_all_cases: [0E-12, 0.793450685623] using `WILSON_SCORE` at 0.95; independence satisfied=`true`.
- rule:NO_MATERIAL_CONFLICTS/insufficient_data_rate_among_all_cases: [0E-12, 0.793450685623] using `WILSON_SCORE` at 0.95; independence satisfied=`true`.
- rule:NO_MATERIAL_CONFLICTS/not_applicable_rate_among_all_cases: [0E-12, 0.793450685623] using `WILSON_SCORE` at 0.95; independence satisfied=`true`.
- rule:PERCENTAGE_CHANGE_MINIMUM/pass_rate_among_all_cases: [0E-12, 0.793450685623] using `WILSON_SCORE` at 0.95; independence satisfied=`true`.
- rule:PERCENTAGE_CHANGE_MINIMUM/unknown_rate_among_all_cases: [0.206549314377, 1.000000000000] using `WILSON_SCORE` at 0.95; independence satisfied=`true`.
- rule:PERCENTAGE_CHANGE_MINIMUM/conflicted_rate_among_all_cases: [0E-12, 0.793450685623] using `WILSON_SCORE` at 0.95; independence satisfied=`true`.
- rule:PERCENTAGE_CHANGE_MINIMUM/insufficient_data_rate_among_all_cases: [0E-12, 0.793450685623] using `WILSON_SCORE` at 0.95; independence satisfied=`true`.
- rule:PERCENTAGE_CHANGE_MINIMUM/not_applicable_rate_among_all_cases: [0E-12, 0.793450685623] using `WILSON_SCORE` at 0.95; independence satisfied=`true`.
- rule:POINT_IN_TIME_ELIGIBLE/pass_rate_among_all_cases: [0.206549314377, 1.000000000000] using `WILSON_SCORE` at 0.95; independence satisfied=`true`.
- rule:POINT_IN_TIME_ELIGIBLE/pass_rate_among_evaluable_cases: [0.206549314377, 1.000000000000] using `WILSON_SCORE` at 0.95; independence satisfied=`true`.
- rule:POINT_IN_TIME_ELIGIBLE/fail_rate_among_evaluable_cases: [0E-12, 0.793450685623] using `WILSON_SCORE` at 0.95; independence satisfied=`true`.
- rule:POINT_IN_TIME_ELIGIBLE/unknown_rate_among_all_cases: [0E-12, 0.793450685623] using `WILSON_SCORE` at 0.95; independence satisfied=`true`.
- rule:POINT_IN_TIME_ELIGIBLE/conflicted_rate_among_all_cases: [0E-12, 0.793450685623] using `WILSON_SCORE` at 0.95; independence satisfied=`true`.
- rule:POINT_IN_TIME_ELIGIBLE/insufficient_data_rate_among_all_cases: [0E-12, 0.793450685623] using `WILSON_SCORE` at 0.95; independence satisfied=`true`.
- rule:POINT_IN_TIME_ELIGIBLE/not_applicable_rate_among_all_cases: [0E-12, 0.793450685623] using `WILSON_SCORE` at 0.95; independence satisfied=`true`.
- rule:PRICE_RANGE/pass_rate_among_all_cases: [0.206549314377, 1.000000000000] using `WILSON_SCORE` at 0.95; independence satisfied=`true`.
- rule:PRICE_RANGE/pass_rate_among_evaluable_cases: [0.206549314377, 1.000000000000] using `WILSON_SCORE` at 0.95; independence satisfied=`true`.
- rule:PRICE_RANGE/fail_rate_among_evaluable_cases: [0E-12, 0.793450685623] using `WILSON_SCORE` at 0.95; independence satisfied=`true`.
- rule:PRICE_RANGE/unknown_rate_among_all_cases: [0E-12, 0.793450685623] using `WILSON_SCORE` at 0.95; independence satisfied=`true`.
- rule:PRICE_RANGE/conflicted_rate_among_all_cases: [0E-12, 0.793450685623] using `WILSON_SCORE` at 0.95; independence satisfied=`true`.
- rule:PRICE_RANGE/insufficient_data_rate_among_all_cases: [0E-12, 0.793450685623] using `WILSON_SCORE` at 0.95; independence satisfied=`true`.
- rule:PRICE_RANGE/not_applicable_rate_among_all_cases: [0E-12, 0.793450685623] using `WILSON_SCORE` at 0.95; independence satisfied=`true`.
- rule:PROVIDER_SCOPE_EXPLICIT/pass_rate_among_all_cases: [0.206549314377, 1.000000000000] using `WILSON_SCORE` at 0.95; independence satisfied=`true`.
- rule:PROVIDER_SCOPE_EXPLICIT/pass_rate_among_evaluable_cases: [0.206549314377, 1.000000000000] using `WILSON_SCORE` at 0.95; independence satisfied=`true`.
- rule:PROVIDER_SCOPE_EXPLICIT/fail_rate_among_evaluable_cases: [0E-12, 0.793450685623] using `WILSON_SCORE` at 0.95; independence satisfied=`true`.
- rule:PROVIDER_SCOPE_EXPLICIT/unknown_rate_among_all_cases: [0E-12, 0.793450685623] using `WILSON_SCORE` at 0.95; independence satisfied=`true`.
- rule:PROVIDER_SCOPE_EXPLICIT/conflicted_rate_among_all_cases: [0E-12, 0.793450685623] using `WILSON_SCORE` at 0.95; independence satisfied=`true`.
- rule:PROVIDER_SCOPE_EXPLICIT/insufficient_data_rate_among_all_cases: [0E-12, 0.793450685623] using `WILSON_SCORE` at 0.95; independence satisfied=`true`.
- rule:PROVIDER_SCOPE_EXPLICIT/not_applicable_rate_among_all_cases: [0E-12, 0.793450685623] using `WILSON_SCORE` at 0.95; independence satisfied=`true`.
- rule:PUBLISHED_SHORT_INTEREST_AVAILABLE/pass_rate_among_all_cases: [0E-12, 0.793450685623] using `WILSON_SCORE` at 0.95; independence satisfied=`true`.
- rule:PUBLISHED_SHORT_INTEREST_AVAILABLE/unknown_rate_among_all_cases: [0.206549314377, 1.000000000000] using `WILSON_SCORE` at 0.95; independence satisfied=`true`.
- rule:PUBLISHED_SHORT_INTEREST_AVAILABLE/conflicted_rate_among_all_cases: [0E-12, 0.793450685623] using `WILSON_SCORE` at 0.95; independence satisfied=`true`.
- rule:PUBLISHED_SHORT_INTEREST_AVAILABLE/insufficient_data_rate_among_all_cases: [0E-12, 0.793450685623] using `WILSON_SCORE` at 0.95; independence satisfied=`true`.
- rule:PUBLISHED_SHORT_INTEREST_AVAILABLE/not_applicable_rate_among_all_cases: [0E-12, 0.793450685623] using `WILSON_SCORE` at 0.95; independence satisfied=`true`.
- rule:RELATIVE_VOLUME_MINIMUM/pass_rate_among_all_cases: [0E-12, 0.793450685623] using `WILSON_SCORE` at 0.95; independence satisfied=`true`.
- rule:RELATIVE_VOLUME_MINIMUM/unknown_rate_among_all_cases: [0.206549314377, 1.000000000000] using `WILSON_SCORE` at 0.95; independence satisfied=`true`.
- rule:RELATIVE_VOLUME_MINIMUM/conflicted_rate_among_all_cases: [0E-12, 0.793450685623] using `WILSON_SCORE` at 0.95; independence satisfied=`true`.
- rule:RELATIVE_VOLUME_MINIMUM/insufficient_data_rate_among_all_cases: [0E-12, 0.793450685623] using `WILSON_SCORE` at 0.95; independence satisfied=`true`.
- rule:RELATIVE_VOLUME_MINIMUM/not_applicable_rate_among_all_cases: [0E-12, 0.793450685623] using `WILSON_SCORE` at 0.95; independence satisfied=`true`.
- rule:REQUIRED_DOMAINS_PRESENT/pass_rate_among_all_cases: [0E-12, 0.793450685623] using `WILSON_SCORE` at 0.95; independence satisfied=`true`.
- rule:REQUIRED_DOMAINS_PRESENT/unknown_rate_among_all_cases: [0.206549314377, 1.000000000000] using `WILSON_SCORE` at 0.95; independence satisfied=`true`.
- rule:REQUIRED_DOMAINS_PRESENT/conflicted_rate_among_all_cases: [0E-12, 0.793450685623] using `WILSON_SCORE` at 0.95; independence satisfied=`true`.
- rule:REQUIRED_DOMAINS_PRESENT/insufficient_data_rate_among_all_cases: [0E-12, 0.793450685623] using `WILSON_SCORE` at 0.95; independence satisfied=`true`.
- rule:REQUIRED_DOMAINS_PRESENT/not_applicable_rate_among_all_cases: [0E-12, 0.793450685623] using `WILSON_SCORE` at 0.95; independence satisfied=`true`.
- rule:REQUIRED_HISTORY_SUFFICIENT/pass_rate_among_all_cases: [0E-12, 0.793450685623] using `WILSON_SCORE` at 0.95; independence satisfied=`true`.
- rule:REQUIRED_HISTORY_SUFFICIENT/unknown_rate_among_all_cases: [0E-12, 0.793450685623] using `WILSON_SCORE` at 0.95; independence satisfied=`true`.
- rule:REQUIRED_HISTORY_SUFFICIENT/conflicted_rate_among_all_cases: [0E-12, 0.793450685623] using `WILSON_SCORE` at 0.95; independence satisfied=`true`.
- rule:REQUIRED_HISTORY_SUFFICIENT/insufficient_data_rate_among_all_cases: [0.206549314377, 1.000000000000] using `WILSON_SCORE` at 0.95; independence satisfied=`true`.
- rule:REQUIRED_HISTORY_SUFFICIENT/not_applicable_rate_among_all_cases: [0E-12, 0.793450685623] using `WILSON_SCORE` at 0.95; independence satisfied=`true`.
- rule:REQUIRED_UNITS_COMPATIBLE/pass_rate_among_all_cases: [0.206549314377, 1.000000000000] using `WILSON_SCORE` at 0.95; independence satisfied=`true`.
- rule:REQUIRED_UNITS_COMPATIBLE/pass_rate_among_evaluable_cases: [0.206549314377, 1.000000000000] using `WILSON_SCORE` at 0.95; independence satisfied=`true`.
- rule:REQUIRED_UNITS_COMPATIBLE/fail_rate_among_evaluable_cases: [0E-12, 0.793450685623] using `WILSON_SCORE` at 0.95; independence satisfied=`true`.
- rule:REQUIRED_UNITS_COMPATIBLE/unknown_rate_among_all_cases: [0E-12, 0.793450685623] using `WILSON_SCORE` at 0.95; independence satisfied=`true`.
- rule:REQUIRED_UNITS_COMPATIBLE/conflicted_rate_among_all_cases: [0E-12, 0.793450685623] using `WILSON_SCORE` at 0.95; independence satisfied=`true`.
- rule:REQUIRED_UNITS_COMPATIBLE/insufficient_data_rate_among_all_cases: [0E-12, 0.793450685623] using `WILSON_SCORE` at 0.95; independence satisfied=`true`.
- rule:REQUIRED_UNITS_COMPATIBLE/not_applicable_rate_among_all_cases: [0E-12, 0.793450685623] using `WILSON_SCORE` at 0.95; independence satisfied=`true`.
- rule:SEC_FILING_AVAILABLE/pass_rate_among_all_cases: [0E-12, 0.793450685623] using `WILSON_SCORE` at 0.95; independence satisfied=`true`.
- rule:SEC_FILING_AVAILABLE/unknown_rate_among_all_cases: [0.206549314377, 1.000000000000] using `WILSON_SCORE` at 0.95; independence satisfied=`true`.
- rule:SEC_FILING_AVAILABLE/conflicted_rate_among_all_cases: [0E-12, 0.793450685623] using `WILSON_SCORE` at 0.95; independence satisfied=`true`.
- rule:SEC_FILING_AVAILABLE/insufficient_data_rate_among_all_cases: [0E-12, 0.793450685623] using `WILSON_SCORE` at 0.95; independence satisfied=`true`.
- rule:SEC_FILING_AVAILABLE/not_applicable_rate_among_all_cases: [0E-12, 0.793450685623] using `WILSON_SCORE` at 0.95; independence satisfied=`true`.
- rule:SHORT_INTEREST_PERCENTAGE_CHANGE_MINIMUM/pass_rate_among_all_cases: [0E-12, 0.793450685623] using `WILSON_SCORE` at 0.95; independence satisfied=`true`.
- rule:SHORT_INTEREST_PERCENTAGE_CHANGE_MINIMUM/unknown_rate_among_all_cases: [0.206549314377, 1.000000000000] using `WILSON_SCORE` at 0.95; independence satisfied=`true`.
- rule:SHORT_INTEREST_PERCENTAGE_CHANGE_MINIMUM/conflicted_rate_among_all_cases: [0E-12, 0.793450685623] using `WILSON_SCORE` at 0.95; independence satisfied=`true`.
- rule:SHORT_INTEREST_PERCENTAGE_CHANGE_MINIMUM/insufficient_data_rate_among_all_cases: [0E-12, 0.793450685623] using `WILSON_SCORE` at 0.95; independence satisfied=`true`.
- rule:SHORT_INTEREST_PERCENTAGE_CHANGE_MINIMUM/not_applicable_rate_among_all_cases: [0E-12, 0.793450685623] using `WILSON_SCORE` at 0.95; independence satisfied=`true`.

## Missingness Findings

- `PUBLISHED_SHORT_INTEREST`: 1/1; cases=`BIYA_EARLIEST_BOUNDARY`.
- `PUBLISHED_SHORT_INTEREST_CHANGE`: 1/1; cases=`BIYA_EARLIEST_BOUNDARY`.
- `DAYS_TO_COVER`: 1/1; cases=`BIYA_EARLIEST_BOUNDARY`.
- `BORROW_FEE`: 1/1; cases=`BIYA_EARLIEST_BOUNDARY`.
- `BORROW_FEE_CHANGE`: 1/1; cases=`BIYA_EARLIEST_BOUNDARY`.
- `BORROW_AVAILABILITY`: 1/1; cases=`BIYA_EARLIEST_BOUNDARY`.
- `BORROW_AVAILABILITY_CHANGE`: 1/1; cases=`BIYA_EARLIEST_BOUNDARY`.
- `FLOAT`: 1/1; cases=`BIYA_EARLIEST_BOUNDARY`.
- `PERCENTAGE_CHANGE_HISTORY`: 1/1; cases=`BIYA_EARLIEST_BOUNDARY`.
- `RELATIVE_VOLUME_HISTORY`: 1/1; cases=`BIYA_EARLIEST_BOUNDARY`.
- `NEWS`: 0/1; cases=none.
- `NEWS_TIMESTAMP`: 0/1; cases=none.
- `SEC_FILINGS`: 1/1; cases=`BIYA_EARLIEST_BOUNDARY`.
- `CORPORATE_ACTION_CONTEXT`: 0/1; cases=none.
- `PROVIDER_SCOPE`: 0/1; cases=none.
- `CONFLICTED_EVIDENCE`: 0/1; cases=none.
- `INSUFFICIENT_HISTORY`: 1/1; cases=`BIYA_EARLIEST_BOUNDARY`.
- `PARTIAL_OUTCOME_WINDOW`: 0/1; cases=none.
- `UNKNOWN_PLATFORM_STATUS`: 0/1; cases=none.
- `IDENTITY_CONFLICT`: 0/1; cases=none.
- `INCOMPLETE_CANDIDATE_CASE`: 0/1; cases=none.
- `MULTIPLE_BOUNDARIES_PER_SYMBOL`: 0/1; cases=none.

## Limitations

- The historical completed dataset currently represents one unique symbol.
- The two BIYA boundaries are dependent observations of the same symbol.
- Case-boundary counts are not independent performance samples.
- The default unique-symbol analysis selects the earliest boundary without using the outcome.
- The historical sample is insufficient for predictive validation.
- Outcome confirmation does not prove short-squeeze causation.
- Missing short-pressure evidence remains material.
- Rule prevalence does not prove predictive importance.
- Confidence intervals do not repair an unrepresentative sample.
- Synthetic cases are excluded from empirical performance estimates.
- Thresholds and policies were not optimized.
- No P&L, backtest, entry, exit, recommendation, or trading simulation was performed.
- The two BIYA outcome labels were established from observed threshold crossings within partial 24-hour observation windows; partial windows could not establish absence of a crossing.
- BIYA demonstrates that the deterministic pipeline can preserve a detected case and a later substantial move without injecting outcome information into the original evaluation.
- It does not validate squeeze causation or general predictive performance.

## Forbidden Interpretations

- Do not interpret these counts as predictive validation.
- Do not infer short-squeeze causation.
- Do not infer rule importance from prevalence.
- Do not combine synthetic cases with historical empirical estimates.
- Do not use these results for threshold selection or trading decisions.

## No Recommendation

No candidate score, rank, alert, or trading recommendation is produced.
