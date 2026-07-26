# Phase 3A Original-Rule Mapping

| Original rule/behavior | Original problem | Phase 3A replacement | Category | Disposition |
|---|---|---|---|---|
| Price band | embedded in composite rubric | `PRICE_RANGE` | momentum | PRESERVED |
| Change percent | embedded in composite rubric | `PERCENTAGE_CHANGE_MINIMUM` using Phase 2 metrics | momentum | CORRECTED |
| Relative volume | ambiguous legacy calculation | `RELATIVE_VOLUME_MINIMUM` using Phase 2B | momentum | CORRECTED |
| Short float minimum | no canonical BIYA source survives | documented deferred rule | short pressure | DEFERRED |
| Prime/Subprime | implied squeeze confirmation from momentum-heavy points | none | none | REMOVED |
| Days-to-cover display | displayed beside live fields without reporting-age meaning | `DAYS_TO_COVER_MINIMUM` | short pressure | SEPARATED |
| Borrow fee/availability displays | did not affect legacy tier | four independent borrow rules | short pressure | SEPARATED |
| News-presence check | inadequate timestamp handling | three publication-time-gated news rules | catalyst | CORRECTED |
| Missing-value defaults | could erase unavailable/zero distinction | `NO_DEFAULT_SUBSTITUTION` plus six-state outcomes | validity | REMOVED |
| TTM Squeeze and technical indicators | no validated canonical Phase 3A inputs | documented deferred rules | deferred | DEFERRED |

