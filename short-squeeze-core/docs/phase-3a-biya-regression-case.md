# Phase 3A BIYA Regression Case

> Phase 3B reuse: both frozen boundary evaluations are consumed unchanged. Their required detection rules pass and their short-pressure results remain unknown. Separate partial outcome windows directly cross +25%, which supports an upward outcome label under the approved asymmetry but does not establish squeeze causation or alter Phase 3A.

BIYA is evaluated independently at `2026-07-17T14:23:58Z` and
`2026-07-17T16:54:58Z`. The case references Phase 2V fixtures rather than duplicating raw data.
Only bars whose provider bar-end is at or before the boundary enter a request. Later outcome
bars never enter. Historical news uses its explicit `PUBLICATION_TIMESTAMP` availability basis;
the reverse-split action uses its provider-published effective time. Original observation IDs
are preserved. This is a retrospective public-history projection, not a claim that the original
platform received those records.

| Rule group | Earliest | Latest |
|---|---|---|
| Price range | `PASS`, close 4.34499979019165, bar `72722a20-55c9-5609-beb0-1a8c25d0ead1` | `PASS`, close 4.215000152587891, bar `3f07ba33-97fe-5420-b454-b62e880cdfe1` |
| Market/completed bar | `PASS` / `PASS` | `PASS` / `PASS` |
| Percentage change / relative volume / float | `UNKNOWN` / `UNKNOWN` / `UNKNOWN` | same |
| All seven short-pressure rules | `UNKNOWN`; no supporting short-interest/borrow observation or metric | same |
| News availability/before/timestamp | `PASS` / `PASS` / `PASS`, four pre-boundary items | same |
| SEC filing / corporate action | `UNKNOWN` / `PASS`; reverse split `6a18ab70-d65e-57d7-86b8-f09321e7ec4c` | same |
| Validity | domains `UNKNOWN`, conflicts `PASS`, point-in-time `PASS`, units `PASS`, history `INSUFFICIENT_DATA`, no defaults `PASS`, scope `PASS` | same outcomes with boundary-distinct readiness IDs |

Days to cover has no observed value, not zero. Phase 2V's separate conclusion
`OUTCOME_CONFIRMED_METHODOLOGY_UNVERIFIED` does not appear in either evaluation. The two
candidate IDs differ, while repeated serialization of each boundary is byte-identical. There
is no BIYA score, label, rank, recommendation, or inferred squeeze cause.

Both projections are runnable through the offline CLI. Use the matching timestamp and evidence
file, providers `yahoo-chart` and `yahoo-search`, and the default policy. For example:

```powershell
.\.venv\Scripts\python.exe -m squeeze_core build-candidate-evaluation `
  --policy tests\fixtures\evaluation\phase_3a_default_policy.json `
  --evidence tests\fixtures\evaluation\biya_earliest_evidence.jsonl `
  --symbol BIYA --as-of 2026-07-17T14:23:58Z `
  --provider yahoo-chart --provider yahoo-search `
  --output build\evaluation\biya-earliest.json
```
