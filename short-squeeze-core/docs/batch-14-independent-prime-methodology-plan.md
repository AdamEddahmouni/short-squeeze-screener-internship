# Batch 14 Independent Prime Methodology Preregistration

**Policy ID:** `adam_evidence_gated_prime.v1`

**Frozen before first evaluation:** 2026-07-25

**Status:** Provisional experimental research policy; not outcome-optimized

**Label:** `EXPERIMENTAL RESEARCH CLASSIFICATION — NOT PREDICTIVE VALIDATION`

This document freezes the components, weights, normalization, thresholds, evidence gates,
and missing-data behavior before the policy is applied to current candidates. Changes
after evaluation require a new policy version unless they correct an implementation defect
that makes the code disagree with this document.

## Common evidence eligibility

A component supports a score only when all of the following are true:

- the value exists; missing is never zero;
- provider and provider field are identified;
- event and receipt times are preserved;
- the unit matches the component contract;
- the value is point-in-time eligible at the classification instant;
- the provider evidence is research-admissible for this policy;
- the freshness limit below is satisfied;
- no material provider conflict affects the component.

Display availability and scoring eligibility are separate flags. A display-only Finviz
Short Float, Short Ratio, or Relative Volume value remains visible but contributes no
weight until its canonical semantics and admissibility are established.

For every continuous component, `linear(x; low, high)` means
`100 × clamp((x - low) / (high - low), 0, 1)`. `inverse_linear` is
`100 - linear`. These are provisional transforms, not probabilities or validated
relationships.

## Pressure

| Component | Canonical concept | Provider policy | Unit | Freshness | Normalization | Weight | Missing behavior | Rationale |
| --- | --- | --- | --- | --- | --- | ---: | --- | --- |
| Published SI % | published short-interest shares divided by compatible float shares | canonical published-SI provider plus compatible float provider | percent | publication no older than 45 calendar days | `linear(5, 30)` | 30% | missing | Direct published short-position pressure |
| Days to cover | canonical published SI shares divided by admissible average daily volume | canonical metric providers | days | inputs within their own limits | `linear(1, 7)` | 25% | missing | Persistence relative to trading capacity |
| Cost to borrow | current annualized borrow fee | borrow provider | percent annualized | receipt age at most 20 minutes | `linear(2, 50)` | 20% | missing | Current financing friction |
| Borrow availability | current shortable shares divided by compatible float | borrow plus float providers | percent of float | receipt age at most 20 minutes; float at most 24 hours | `inverse_linear(0.1, 10)` | 15% | missing | Scarcity of lendable supply |
| Float tightness | canonical float shares | canonical float provider | shares | receipt age at most 24 hours | `inverse_linear(10,000,000, 50,000,000)` | 10% | missing | Smaller tradable supply may amplify pressure |

Published SI % is critical. At least one of Days to Cover, Cost to Borrow, or Borrow
Availability must also be supported. Float tightness alone can never produce a Pressure
score. Finviz Short Float is not substituted for published SI, and Finviz Short Ratio is
not substituted for canonical Days to Cover.

## Ignition

| Component | Canonical concept | Provider policy | Unit | Freshness | Normalization | Weight | Missing behavior | Rationale |
| --- | --- | --- | --- | --- | --- | ---: | --- | --- |
| Current percentage change | canonical completed-bar percentage return over the disclosed current window | canonical market-bar metric | percent | latest completed bar age at most 20 minutes | `linear(0, 20)` | 35% | missing | Observed positive price expansion |
| Relative volume | canonical target volume divided by compatible baseline volume | canonical volume metric | ratio | receipt age at most 20 minutes | `linear(1, 10)` | 30% | missing | Current activity relative to a compatible baseline |
| Completed-bar acceleration | return over latest three completed bars minus return over the preceding three completed bars | canonical completed market bars | percentage points | newest bar age at most 20 minutes; at least seven ordered completed bars | `linear(0, 5)` | 20% | missing | Acceleration distinguishes developing from static momentum |
| Timestamped catalyst evidence | objective news or SEC filing available before `as_of`, with a known publication time and symbol association | canonical news/SEC evidence | categorical age | at most 72 hours | 100 at ≤24h; 50 at >24h and ≤72h | 15% | missing unless a complete provider query establishes no qualifying item | Context for observed ignition |

Percentage change and Relative Volume are both critical. Positive movement and positive
acceleration are intentionally the ignition directions: a known value at or below zero
normalizes to zero; it is not treated as missing. This directional choice is provisional
and is not a performance claim.

## Dimension scores

Each dimension has 100 total component weight.

1. Sum the weights of eligible components.
2. If supported weight is below 70%, or a critical-domain rule is unmet, withhold the
   dimension score as `PARTIAL ... — INSUFFICIENT COVERAGE`.
3. Otherwise calculate the explicitly partial weighted mean:
   `sum(weight × normalized value) / supported weight`.
4. Return the supported component count, required component count, supported weight, every
   missing component, and the coverage limitation beside the score.

The 70% rule prevents a single field from being normalized into a misleading 0–100
dimension. A reported score is an experimental dimension value, never probability.

## Evidence Coverage

Coverage reports both counts and eligible weight:

- Pressure fields available / 5 and supported weight / 100;
- Ignition fields available / 4 and supported weight / 100;
- total fields available / 9;
- total supported weight / 200;
- critical domains present;
- point-in-time eligibility;
- unit compatibility;
- freshness;
- provider conflicts.

The category is:

- `CONFLICTED`: a material provider, unit, identity, or timing conflict blocks evaluation;
- `HIGH COVERAGE`: total supported weight at least 85%, both dimension scores available,
  all critical domains present, point-in-time eligible, units compatible, and fresh;
- `MODERATE COVERAGE`: total supported weight from 70% through 84.999%, both scores
  available, and all critical validity checks pass;
- `LOW COVERAGE`: total supported weight from 50% through 69.999% without a material
  conflict;
- `INSUFFICIENT EVIDENCE`: total supported weight below 50% or any critical validity check
  fails.

Coverage measures evidentiary support, not squeeze likelihood.

## Classification

`strong` means a dimension score at least 70. `developing` means at least 50 and below 70.

- `CONFLICTED`: Coverage is `CONFLICTED`.
- `UNEVALUABLE`: Coverage is `INSUFFICIENT EVIDENCE`, Coverage is `LOW COVERAGE`, or either
  dimension score is withheld.
- `PRIME`: Pressure and Ignition are both strong and Coverage is `HIGH COVERAGE`.
- `SUBPRIME`: one dimension is strong, the other is at least developing, and Coverage is
  at least `MODERATE COVERAGE`.
- `WATCH`: Coverage is at least `MODERATE COVERAGE`, at least one dimension is developing
  or strong, and neither Prime nor Subprime applies.
- `NOT QUALIFIED`: Coverage is at least `MODERATE COVERAGE`, both dimension scores are
  available, and both are below 50.

Classification precedence is the order above. Thresholds and weights are provisional and
not optimal or validated.

## Candidate visibility

Every discovered candidate remains in session state and appears by default. Filtering and
sorting operate only on response/view copies. Clearing a visual filter restores every
candidate. Candidates that meet no methodology remain visible as `NOT QUALIFIED` or
`UNEVALUABLE`.

## Conflict policy

A conflict is material when two eligible providers disagree on symbol identity, unit,
point-in-time ordering, or a component value beyond an existing canonical compatibility
rule and field-level provider selection cannot resolve it. The affected component is not
scored and the overall classification is `CONFLICTED`. Provider absence is missingness,
not conflict.

## Provider admissibility

Canonical Phase 3A evidence and metrics retain their existing admissibility decisions.
The experimental policy may consume them but may not change their outcomes. A new provider
field requires an explicit adapter, unit contract, timestamp semantics, freshness rule,
and tests before it can be scoring-eligible. Current data never fills a frozen or
historical gap.

## Limitations

- The policy has not been retrospectively or prospectively validated.
- No threshold or weight was fitted to outcomes.
- Current provider support may leave most or all candidates unevaluable.
- Published short interest, borrow fee, canonical days to cover, and canonical relative
  volume may be unavailable.
- TTM Squeeze is not implemented and is not an Adam v1 component.
- Scores do not measure probability, expected return, trade quality, or profitability.
- Phase 3E is unstarted and remains outside this batch.
