# Batch 07 — Phase 3A 25-Rule Dependency Readiness Audit

Dependency-readiness for every rule in
`src/squeeze_core/evaluation/policies/phase_3a_transparent_candidate_policy_v1.json`
against the Batch 05 `DETECTION_CONTEXT_PRECEDING_24H` evidence plus existing pre-outcome
evidence. **This is dependency analysis, not rule evaluation:** every value is an
admissibility status; no rule receives PASS/FAIL, no `RuleEvaluationResult` is created,
and no evaluation is executed. Generated deterministically by `operation_readiness`.

## Distribution over 25 rules

| admissibility status | count | rules |
|----------------------|-------|-------|
| ADMISSIBLE | 2 | MARKET_DATA_AVAILABLE, COMPLETED_BAR_AVAILABLE |
| ADMISSIBLE_WITH_CONSTRAINTS | 1 | PERCENTAGE_CHANGE_MINIMUM |
| BLOCKED_MISSING_SEMANTICS | 2 | PRICE_RANGE, RELATIVE_VOLUME_MINIMUM |
| BLOCKED_MISSING_EVIDENCE | 13 | FLOAT_MAXIMUM + all 7 SHORT_PRESSURE_CONFIRMATION + all 5 CATALYST_EVIDENCE |
| NOT_APPLICABLE | 7 | all 7 EVIDENCE_VALIDITY meta-rules |

## Full matrix

| rule_id | category | touches bars | admissibility | reason codes |
|---------|----------|--------------|---------------|--------------|
| MARKET_DATA_AVAILABLE | MOMENTUM_DISCOVERY | yes | ADMISSIBLE | MARKET_BARS_PRESENT |
| COMPLETED_BAR_AVAILABLE | MOMENTUM_DISCOVERY | yes | ADMISSIBLE | FINAL_BAR_DEFINITELY_COMPLETED, MARKET_BARS_PRESENT |
| PERCENTAGE_CHANGE_MINIMUM | MOMENTUM_DISCOVERY | yes | ADMISSIBLE_WITH_CONSTRAINTS | DIVIDEND_ADJUSTMENT_NOT_APPLIED, MARKET_BARS_PRESENT, PRICE_RATIO_SPLIT_INVARIANT |
| PRICE_RANGE | MOMENTUM_DISCOVERY | yes | BLOCKED_MISSING_SEMANTICS | PRICE_ABSOLUTE_LEVEL_CORPORATE_ACTION_UNCONFIRMED |
| RELATIVE_VOLUME_MINIMUM | MOMENTUM_DISCOVERY | yes | BLOCKED_MISSING_SEMANTICS | VOLUME_UNIT_UNRESOLVED, VOLUME_CORPORATE_ACTION_UNKNOWN, VOLUME_FILTER_STATIONARITY_UNPROVEN |
| FLOAT_MAXIMUM | MOMENTUM_DISCOVERY | no | BLOCKED_MISSING_EVIDENCE | REQUIRED_DOMAIN_ABSENT (CANDIDATE_SNAPSHOT) |
| PUBLISHED_SHORT_INTEREST_AVAILABLE | SHORT_PRESSURE_CONFIRMATION | no | BLOCKED_MISSING_EVIDENCE | REQUIRED_DOMAIN_ABSENT |
| SHORT_INTEREST_PERCENTAGE_CHANGE_MINIMUM | SHORT_PRESSURE_CONFIRMATION | no | BLOCKED_MISSING_EVIDENCE | REQUIRED_DOMAIN_ABSENT |
| DAYS_TO_COVER_MINIMUM | SHORT_PRESSURE_CONFIRMATION | no | BLOCKED_MISSING_EVIDENCE | REQUIRED_DOMAIN_ABSENT |
| BORROW_FEE_MINIMUM | SHORT_PRESSURE_CONFIRMATION | no | BLOCKED_MISSING_EVIDENCE | REQUIRED_DOMAIN_ABSENT |
| BORROW_FEE_CHANGE_MINIMUM | SHORT_PRESSURE_CONFIRMATION | no | BLOCKED_MISSING_EVIDENCE | REQUIRED_DOMAIN_ABSENT |
| BORROW_AVAILABILITY_MAXIMUM | SHORT_PRESSURE_CONFIRMATION | no | BLOCKED_MISSING_EVIDENCE | REQUIRED_DOMAIN_ABSENT |
| BORROW_AVAILABILITY_CHANGE_MAXIMUM | SHORT_PRESSURE_CONFIRMATION | no | BLOCKED_MISSING_EVIDENCE | REQUIRED_DOMAIN_ABSENT |
| NEWS_AVAILABLE | CATALYST_EVIDENCE | no | BLOCKED_MISSING_EVIDENCE | REQUIRED_DOMAIN_ABSENT |
| NEWS_AVAILABLE_BEFORE_AS_OF | CATALYST_EVIDENCE | no | BLOCKED_MISSING_EVIDENCE | REQUIRED_DOMAIN_ABSENT |
| NEWS_TIMESTAMP_KNOWN | CATALYST_EVIDENCE | no | BLOCKED_MISSING_EVIDENCE | REQUIRED_DOMAIN_ABSENT |
| SEC_FILING_AVAILABLE | CATALYST_EVIDENCE | no | BLOCKED_MISSING_EVIDENCE | REQUIRED_DOMAIN_ABSENT |
| CORPORATE_ACTION_CONTEXT_AVAILABLE | CATALYST_EVIDENCE | no | BLOCKED_MISSING_EVIDENCE | REQUIRED_DOMAIN_ABSENT |
| REQUIRED_DOMAINS_PRESENT | EVIDENCE_VALIDITY | no | NOT_APPLICABLE | OPERATION_INDEPENDENT_OF_THIS_EVIDENCE |
| NO_MATERIAL_CONFLICTS | EVIDENCE_VALIDITY | no | NOT_APPLICABLE | OPERATION_INDEPENDENT_OF_THIS_EVIDENCE |
| POINT_IN_TIME_ELIGIBLE | EVIDENCE_VALIDITY | no | NOT_APPLICABLE | OPERATION_INDEPENDENT_OF_THIS_EVIDENCE |
| REQUIRED_UNITS_COMPATIBLE | EVIDENCE_VALIDITY | no | NOT_APPLICABLE | OPERATION_INDEPENDENT_OF_THIS_EVIDENCE |
| REQUIRED_HISTORY_SUFFICIENT | EVIDENCE_VALIDITY | no | NOT_APPLICABLE | OPERATION_INDEPENDENT_OF_THIS_EVIDENCE |
| NO_DEFAULT_SUBSTITUTION | EVIDENCE_VALIDITY | no | NOT_APPLICABLE | OPERATION_INDEPENDENT_OF_THIS_EVIDENCE |
| PROVIDER_SCOPE_EXPLICIT | EVIDENCE_VALIDITY | no | NOT_APPLICABLE | OPERATION_INDEPENDENT_OF_THIS_EVIDENCE |

## Interpretation

- **Only 6 of 25 rules touch the detection-context bars** (all MOMENTUM_DISCOVERY). Of
  those, 2 availability rules are fully admissible, 1 percentage-change rule is admissible
  with stated constraints, and 2 (absolute price band, relative volume) are blocked on
  unresolved semantics. `FLOAT_MAXIMUM` sits in MOMENTUM_DISCOVERY but needs the
  `CANDIDATE_SNAPSHOT` domain, which is absent.
- **13 rules are blocked for lack of their evidence domain** — the short-pressure,
  catalyst, float, and corporate-action domains are simply not part of this evidence set.
  This is a missing-evidence fact, not a semantic defect.
- **7 EVIDENCE_VALIDITY meta-rules are NOT_APPLICABLE** to the bars in isolation: they
  validate a fully assembled request (all domains, units, point-in-time eligibility), so
  the detection-context bars neither satisfy nor block them. Their readiness depends on
  the whole request, which is a future step.
- Batch 05/06 evidence **changes readiness only for the 6 market-bar rules**; it does not
  change readiness for the 19 non-market-bar / meta rules. Batch 01 pre-outcome evidence
  (identity, boundary, eligibility) is unchanged and unread here beyond the frozen
  boundary/identity used for association.

No rule is evaluated. No PASS/FAIL is emitted. Blocked/NOT_APPLICABLE are valid, honest
outcomes for a readiness audit.
