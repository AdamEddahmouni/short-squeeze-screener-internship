> Companion to [batch-08-phase3a-request-result-freeze-plan.md](batch-08-phase3a-request-result-freeze-plan.md).

# Batch 08 — Admissible Evidence Mapping

What Batch 07 authorised, what Batch 08 actually attached to each Phase 3A request, and
what was deliberately left missing. Batch 07's verdicts are consumed unchanged: Batch 08
rebuilds the Batch 07 report through Batch 07's own code path and cites its record ids, so
no admissibility verdict is recomputed or restated here.

## 1. Two independent authorisations, both cited

Every frozen request and result carries both:

| Citation | Value | Meaning |
| --- | --- | --- |
| Batch 04 global preflight | `PREFLIGHT_REJECTED` | The bundle is **not** globally ready. Unchanged, unweakened, and echoed into every record. |
| Batch 07 per-case admissibility | `PHASE3A_REQUEST_READY`, temporal alignment `ADMISSIBLE` | A strictly narrower authorisation for specific operations only. |

The second never overrides the first. Batch 08 operates only inside the narrower
authorisation.

## 2. The 25-rule admissibility map (identical for all 13 cases)

| Batch 07 status | Count | Rules |
| --- | --- | --- |
| `ADMISSIBLE` | 2 | `MARKET_DATA_AVAILABLE`, `COMPLETED_BAR_AVAILABLE` |
| `ADMISSIBLE_WITH_CONSTRAINTS` | 1 | `PERCENTAGE_CHANGE_MINIMUM` |
| `BLOCKED_MISSING_SEMANTICS` | 2 | `PRICE_RANGE`, `RELATIVE_VOLUME_MINIMUM` |
| `BLOCKED_MISSING_EVIDENCE` | 13 | `FLOAT_MAXIMUM`, the seven short-pressure rules, the five catalyst rules |
| `NOT_APPLICABLE` (readiness level) | 7 | the seven `EVIDENCE_VALIDITY` meta-rules |

## 3. Evidence actually attached to each request

| Input | Present | Source |
| --- | --- | --- |
| Frozen case identity + boundary | yes | Batch 01 freeze, boundary id recomputed with the project's own identifier function |
| Detection-context artifact identity | yes | Batch 05 provenance manifest (SHA-256, byte length, coverage) |
| Batch 06 price semantics | yes (`SPLIT_ADJUSTED`) | provenance only; never used to adjust a value |
| Batch 07 admissibility record | yes | Batch 07 report record id and association id |
| `EventType.BAR` observations | yes | detection-context CSV, definitely-completed bars, normalized through the canonical market-bar adapter |
| `PERCENTAGE_RETURN` metric | yes | canonical Phase 2 `build_return_result`, `close_to_close_completed.v1` |
| `DomainCoverageSnapshot` | yes | canonical Phase 2D builder |
| `EvidenceConflictSummary` | yes | canonical Phase 2D builder |
| `InputSufficiencyResult` | yes | canonical Phase 2D builder, operation `PERCENTAGE_RETURN` |

## 4. Evidence deliberately absent

| Omitted input | Why | What was **not** done |
| --- | --- | --- |
| Absolute price level (`PRICE_RANGE`) | Batch 07 `BLOCKED_MISSING_SEMANTICS`: an absolute level is not invariant to an unconfirmed corporate action | not substituted, not defaulted, not zeroed |
| Volume of any kind | Batch 07 `BLOCKED_MISSING_SEMANTICS`: volume unit unresolved, corporate-action handling unknown, filtered-feed stationarity unproven | bars carry `volume = None`; no `RELATIVE_VOLUME` metric constructed |
| Trade count, WAP | same volume-semantics block; not required by any admissible operation | left null |
| `float_shares` | no detection-time float evidence exists | no `MARKET_SNAPSHOT` observation created |
| Short interest, days-to-cover, borrow fee, borrow availability | no detection-time evidence exists | no observation, no metric, no provider declared |
| News, SEC filings, corporate actions | no detection-time evidence exists | no observation; no news provider declared |
| Scanner score, tier, targets, sentiment | out of scope and outcome-adjacent | no such field exists on any Batch 08 model |
| Forward-window bars | forward artifact is blocked | referenced by hash and byte length only |
| Outcome labels | Phase 3B is not started | no outcome field exists on any Batch 08 model |

Missing fields stay missing. The frozen request has no defaulted field:
`default_substitution_fields` is empty for all 13 cases, and the evaluator confirms this
by resolving `NO_DEFAULT_SUBSTITUTION` to `PASS`.

## 5. Domains requested versus present

The requested domain set is derived from the committed Phase 3A policy — the union of
`required_domains` across the 25 rules — not hand-picked:

| Domain | State at the boundary |
| --- | --- |
| `MARKET_BARS` | `PRESENT` |
| `CANDIDATE_SNAPSHOT` | `MISSING` |
| `PUBLISHED_SHORT_INTEREST` | `MISSING` |
| `BORROW_FEE` | `MISSING` |
| `BORROW_AVAILABILITY` | `MISSING` |
| `NEWS` | `MISSING` |
| `SEC_FILINGS` | `MISSING` |

One of seven required domains is present. This is the missing-evidence profile of the
study as it stands, and it is why `REQUIRED_DOMAINS_PRESENT` resolves `FAIL` — a statement
about the completeness of the evidence request, not about any candidate.

## 6. Blocking reason codes (455 rule-case pairs)

| Code | Count | Meaning |
| --- | --- | --- |
| `NO_DETECTION_TIME_EVIDENCE_EXISTS` | 169 | the domain was never collected at detection time |
| `REQUIRED_DOMAIN_ABSENT_FROM_EVIDENCE` | 169 | the rule's required domain is not in this evidence set |
| `EVIDENCE_META_RULE_NOT_BAR_DEPENDENT` | 91 | an `EVIDENCE_VALIDITY` meta-rule validates the assembled request, not the bars |
| `VOLUME_SEMANTICS_BLOCKED_BY_BATCH07` | 13 | volume unit / corporate action / filter stationarity unresolved |
| `ABSOLUTE_PRICE_LEVEL_BLOCKED_BY_BATCH07` | 13 | absolute price level not split-invariant |

Counts are descriptive frequencies over rule-case pairs. They are not a performance
measure of any kind.
