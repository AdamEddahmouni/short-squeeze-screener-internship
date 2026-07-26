# Batch 14 Evidence Admissibility Results

| Finviz field | Decision | Reason |
|---|---|---|
| Shares Float | research-admissible | Published shares float matches canonical FLOAT units and concept. |
| Short Float | display-only | Percentage of float is not published short-interest shares. |
| Relative Volume | display-only | Finviz's three-month intraday-adjusted baseline differs from the canonical contract. |
| Short Ratio | display-only | It is not canonical Days to Cover without compatible underlying inputs. |
| Shares Outstanding | display-only | Distinct from float; absent from the current returned columns. |
| Price / Change | display-only fallback context | Does not replace fresher IBKR evidence globally. |
| News headlines | display-only catalyst context | Presence alone never produces catalyst PASS. |

Observed current coverage increased from 9/25 to 11/25. Exact newly evaluable rules:
`FLOAT_MAXIMUM` and `PROVIDER_SCOPE_EXPLICIT`. `FLOAT_MAXIMUM` consumes only Finviz
`Shares Float`; other activated fields remain excluded from canonical rules. All 16
current candidates remained `UNEVALUABLE` because required domains are incomplete.

Official definitions: https://finviz.com/help/screener
