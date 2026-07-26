# Phase 3B Research Classification Semantics

Classification is one immutable truth table:

| Detection | Outcome | Classification |
| --- | --- | --- |
| `DETECTED` | `SUBSTANTIAL_UPWARD_MOVE` | `TRUE_POSITIVE` |
| `DETECTED` | `NO_SUBSTANTIAL_UPWARD_MOVE` | `FALSE_POSITIVE` |
| `NOT_DETECTED` | `SUBSTANTIAL_UPWARD_MOVE` | `FALSE_NEGATIVE` |
| `NOT_DETECTED` | `NO_SUBSTANTIAL_UPWARD_MOVE` | `TRUE_NEGATIVE` |
| `UNEVALUABLE` | any outcome | `UNEVALUABLE` |
| any detection | `OUTCOME_UNKNOWN` | `UNEVALUABLE` |
| any detection | `OUTCOME_INSUFFICIENT_DATA` | `UNEVALUABLE` |
| any detection | `MIXED_OR_VOLATILE` | `UNEVALUABLE` |
| any detection | `SUBSTANTIAL_DOWNWARD_MOVE` | `UNEVALUABLE` |

The specific-outcome unevaluable rows take precedence over binary classification. Downward movement remains unevaluable unless a future, separately approved policy defines a mapping. Original-platform status never changes classification.

Limitations: these labels describe agreement with a provisional research predicate, not model accuracy, causal confirmation, investment quality, or a trading result.

