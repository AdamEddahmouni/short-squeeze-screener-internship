# Phase 2V BIYA Case Study

> Outcome-data amendment (2026-07-21): the original forensic conclusion below remains
> `INSUFFICIENT_EVIDENCE`. A separate additive result now records
> `OUTCOME_CONFIRMED_METHODOLOGY_UNVERIFIED` because retained historical prices exceed
> the predeclared substantial-move threshold from both detection boundaries. See
> `phase-2v-biya-outcome-report.md`; no missing original value was reconstructed.

The complete case, end to end. Evidence detail is in
`docs/phase-2v-biya-artifact-inventory.md`; rule reconstruction is in
`docs/phase-2v-original-rule-manifest.md`; findings are in
`docs/phase-2v-root-cause-report.md`.

## 1. The question

On 2026-07-17 the original screener surfaced BIYA. During a review session that day the
advisor observed it on screen and remarked that it had "rose sharply this morning at
approximately 4:00 a.m." while "its short interest appears to be low, and I am not sure
why," later asking for its TTM Squeeze value and noting "that stock may not actually be
experiencing a squeeze."

Phase 2V asks: **why did the platform surface it, what was genuinely knowable at that
moment, and does the recorded methodology hold up?**

## 2. Detection time

`BOUNDED_TIME_WINDOW`, `2026-07-17T14:23:58Z` – `2026-07-17T16:54:58Z`
(America/New_York `10:23:58` – `12:54:58`), a 2h31m window.

Bounded below by the screener run's start and above by the application log's last write.
BIYA's first log line is at file line 4, so it was surfaced essentially at startup.

`EXACT_TIMESTAMP` is not claimed: the log carries no timestamps at all, so both bounds
rest on filesystem metadata. The 8m43s meeting interval derived from the recording
filename bounds *discussion*, not detection, and is recorded as corroboration only.

## 3. What the platform was actually running

The code at detection is `ScreenerProject` commit `b016d92f` (11:56:43), **not** the
archived working tree. The Prime/Subprime redesign landed at 15:39:27 — 2h53m after the
meeting — so `classify_tier()` did not exist when BIYA was surfaced.

At detection, the label came from `core/scoring.py::score_setup()`:

```
score = (2 <= price <= 20) + (change% >= 10) + (rel_volume >= 5) + (short_float >= 5)
Prime = 4/4, Subprime = 3/4, otherwise dropped
```

**None of those four inputs is a squeeze mechanic.** Borrow fee, days to cover, and TTM
Squeeze were computed and displayed, and scored nothing.

## 4. What the original platform recorded about BIYA

Almost nothing. The only direct platform record is `logs/app.log`, and all 43 of its BIYA
lines are failures:

- IB `Error 10089` — no market-data subscription, fall back to **delayed** data — carrying
  a genuine IB contract (`conId=900208122`, `NASDAQ.SCM`), confirming BIYA was a real
  instrument in the screening universe rather than test data.
- Schwab corroboration calls failing with `NameResolutionError`.

No price, change, relative volume, float, short float, days to cover, borrow fee, news,
score, or label survives. **Every original field value is `UNKNOWN`**, and is left
unknown rather than reconstructed from later data.

## 5. Replay

Run at both window edges against the evidence that actually exists. Both return no
eligible observations, because the archive contains no BIYA observation in any domain —
no bar, quote, trade, short-interest record, borrow record, filing, halt, or news item.

The empty replay is the finding, not a gap in method.

## 6. Field comparison

Not possible. Comparison requires an original value, and none survives. Rather than
present an empty grid, the case records why and the demonstration replaces the table with
an explanation.

## 7. Rule classifications

| Rule | Classification |
| --- | --- |
| RULE-001 Prime/Subprime `score_setup()` | `MOMENTUM_DISCOVERY_ONLY` |
| RULE-002 "Short Interest (%)" column | `MISLABELED` |
| RULE-003 Days to cover | `SUPPORTED_WITH_CORRECTION` |
| RULE-004 News loading and timestamps | `MISSING_DEFAULT_SUBSTITUTION` |
| RULE-005 Market data freshness | `UNAVAILABLE_AT_DETECTION` |
| RULE-006 Cross-provider corroboration | `REDUNDANT` |
| RULE-007 Composite pressure score | `SUPPORTED_WITH_CORRECTION` |

These judge **methodology**, not the stock. Note they are recoverable in full even though
the BIYA-specific values are not — the rules come from code, which survives completely.

## 8. Days to cover, audited

| Aspect | Finding |
| --- | --- |
| Original displayed value | **UNKNOWN** — not recorded in any artifact |
| Original formula | `round(shares_short / average_daily_volume, 2)` |
| Numerator | `shares_short` from yfinance `.info`, ultimately a twice-monthly FINRA filing |
| Denominator | `statistics.mean(volumes[:-1])` — trailing mean of completed daily bars, incomplete current bar correctly excluded |
| Volume sample count | Unknown for this symbol |
| Current volume included | No — correctly excluded |
| Missing-value handling | Returns `None` with a reason; flags `days_to_cover_unavailable`; never zero |
| Presented as real time | Effectively yes — displayed beside live price and volume with no reporting-period age |
| Rebuilt value | Not computable — no BIYA short-interest or volume evidence exists |

The structure is sound and matches the rebuilt Phase 2C contract (ADR 0036). The defect
is presentation: a ratio whose numerator can be two weeks old, shown as though current,
with a denominator from a 1-hour cache.

Because the original value cannot be reconstructed, it is classified unknown rather than
estimated from later data.

## 9. News, audited

No BIYA news item is recorded in any artifact, so headline, publisher, publication time,
capture time, and availability at detection are all unknown.

What *is* established, from code, is the mechanism: a missing publication time became the
literal string `"Unknown time"` and a missing headline `"No title"`, making absence
type-indistinguishable from a real value. No availability-time semantics existed, so the
platform could not have determined whether a news item predated detection even if one had
been shown.

## 10. Outcome

Not measurable. No BIYA market bar exists in the workspace at any interval on any date.
All seven evaluation windows are recorded as uncomputable with
`VALIDATION_OUTCOME_DATA_INCOMPLETE`; no aggregate is computed and no fill, entry, exit,
or P&L is inferred.

An outcome could not have validated this case regardless: with no original value
recorded, there is nothing for a subsequent move to confirm or contradict.

## 11. Conclusion

**`INSUFFICIENT_EVIDENCE`.**

There is not enough evidence to determine how the original candidate was produced. Every
original field value is unknown, so the decision cannot be reproduced, compared, or
invalidated.

This is a statement about the surviving record, not a verdict that the platform was
wrong. Note also what it is *not*: not `OUTCOME_CONFIRMED_METHODOLOGY_UNVERIFIED`, which
would require a confirmed outcome, and none is confirmable here.

## 12. What would change this

In rough order of value:

1. **A screenshot of the platform showing BIYA.** Would recover the displayed values and
   likely move the conclusion to `PARTIALLY_VALIDATED` or `NOT_POINT_IN_TIME_VALID`.
2. **A saved candidate row, snapshot, or score-history record.** Same effect, with better
   provenance.
3. **A recalled detection time.** Would narrow a 2h31m window substantially.
4. **BIYA market data for 2026-07-17 onward.** Enables the outcome observation. Does not
   by itself change the conclusion.
5. **The reported advisor message.** Corroborates the outcome; does not validate the
   methodology.

## 13. What this case does establish

Though BIYA-specific values are absent, the case is not empty. The rule-level findings
come from code that survives in full, and they apply to **every** candidate the platform
surfaced — not just this one. The single most consequential result stands independent of
the missing values:

> The label asserted squeeze mechanics that the formula never evaluated.

## 14. Phase 3A additive regression

Phase 3A now evaluates BIYA at both bounded detection timestamps under a new transparent policy.
This does not recover any original platform value or change the Phase 2V conclusion. The
retrospective case partitions acquired public history at each boundary, excludes later market
outcomes, preserves news/action provenance, and reports short-interest and borrow inputs as
unknown. See `phase-3a-biya-regression-case.md`.
