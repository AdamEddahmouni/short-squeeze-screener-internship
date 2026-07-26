# Prime Methodology Comparison

All outputs are labeled **EXPERIMENTAL RESEARCH CLASSIFICATION — NOT PREDICTIVE
VALIDATION**. The methodologies remain separate; agreement is not validation.

| Method | Purpose | Output behavior |
| --- | --- | --- |
| Legacy Prime Setup | Historical reference | Exact $2–$20 price, daily change ≥10%, relative volume ≥5, published SI% ≥5%. Any missing, stale, conflicted, semantically different, or unit-incompatible input makes it `UNEVALUABLE`. |
| Peer Reference | Structured external reference, not our model | Preserves the stated weights and Prime thresholds. It returns `REFERENCE_DEFINITION_INCOMPLETE` because normalization, estimated-SI, float mapping, TTM, Subprime boundaries, and missing-data rules were not supplied. It invents no score. |
| Adam Evidence-Gated Prime v1 | Independently preregistered descriptive policy | Separates Pressure, Ignition, and Evidence Coverage. Only timestamped, fresh, point-in-time, exact-unit, research-admissible evidence contributes. A dimension needs ≥70% supported weight and its critical domains. |
| Canonical Phase 3A | Existing transparent evidence evaluation | Remains the authoritative 25-rule evaluator. Batch 14 does not rewrite its outcomes. |
| Canonical Research Detection | Existing detection policy | Remains separate from every experimental methodology. |

Adam Pressure uses published SI% (30%), days to cover (25%), annualized borrow fee
(20%), borrow availability as percent of compatible float (15%), and float tightness
(10%). Published SI% and one additional pressure domain are critical.

Adam Ignition uses current canonical percentage change (35%), canonical relative volume
(30%), completed-bar acceleration (20%), and timestamped catalyst age (15%). Percentage
change and relative volume are critical.

Coverage below 70% in either dimension withholds that score. Missing is never zero.
Classification precedence is `CONFLICTED`, `UNEVALUABLE`, `PRIME`, `SUBPRIME`, `WATCH`,
then `NOT_QUALIFIED`, exactly as preregistered.

It is designed to be more explicit about missing evidence and provider compatibility.
Comparative predictive performance remains unvalidated.
