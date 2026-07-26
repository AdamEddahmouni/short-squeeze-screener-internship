# Phase 2V Root-Cause Report

> Additive outcome note: later historical price evidence confirms a substantial BIYA
> move but changes none of the root causes documented here. Provider failures, absent
> original values, mislabeled semantics, inadequate news timing, and momentum-heavy
> classification remain intact.

Written after the evidence analysis, not before it. Findings are separated by how well
the surviving record supports them, because the difference between "demonstrated by code
and artifacts" and "strongly suspected" is exactly what this phase exists to preserve.

## 1. Confirmed root causes

Each is demonstrated directly by archived code at the detection-time commit
(`b016d92f`, 2026-07-17T11:56:43 America/New_York) or by the platform's own application
log. Citations are in `docs/phase-2v-original-rule-manifest.md`.

### 1.1 The classification label promised a mechanism the formula never evaluated

`core/scoring.py::score_setup()` awarded one point each for a price band
(`2 <= price <= 20`), a change threshold (`>= 10%`), a relative-volume threshold
(`>= 5`), and a short-float floor (`>= 5%`). Prime required 4/4, Subprime 3/4.

**Borrow fee, days to cover, and TTM Squeeze are never read by this function.** They
were computed and displayed, but contributed nothing to the label. A ticker could
therefore be presented as a squeeze setup purely on momentum and liquidity.

This single fact accounts for both live objections raised in the review: LBGJ at +13%
qualified because 13 ≥ 10, and BIYA surfaced while its short interest was visibly low.
The project's own contemporaneous handoff reached the same conclusion independently.

### 1.2 A column was relabelled to a name that misdescribes its value

Commit `05c81f85` (10:42:26, **2h04m before the review**) renamed the displayed column
from "Short Float %" to "Short Interest %". The underlying value is unchanged and its
arithmetic is correct — `(shares_short / float_shares) * 100` — but that is short
interest expressed as a **percentage of float**, whereas "short interest" unqualified
conventionally denotes the **absolute reported share count**.

The rename's own commit message argues the new label "makes the on-screen name match
what it actually is." That reasoning is half right: the value *is* a short-interest
quantity, but it is a ratio, and the new label drops the qualifier that made it
unambiguous.

### 1.3 The screener ran on delayed market data and did not say so

The application log records IB `Error 10089` for every symbol including BIYA:
*"Requested market data requires additional subscription for API… Delayed market data is
available."* The account lacked the required subscription, so the platform fell back to
delayed data.

Every price, change percent, and relative volume displayed during the review — including
those the advisor read aloud — was **delayed**, on a screener whose stated objective was
minute-by-minute operation. The interface carried no delayed-data indicator.

### 1.4 Cross-provider corroboration failed silently

Every Schwab corroboration call in the observed run failed with
`NameResolutionError` on `api.schwabapi.com`. No corroboration ran at all, and the
interface did not surface its absence — a viewer could not distinguish "corroborated"
from "corroboration never executed."

Separately, and independent of the outage: corroboration reapplied the *same* four-point
rubric to a second provider's numbers. Agreement under one rubric tests data agreement,
not rule validity, so the mechanism was weaker than its name implied even when working.

### 1.5 Missing news timestamps were replaced by a display string

`core/yfinance_news_api.py:52` and `core/newsapi_news_api.py:65` substitute the literal
strings `"Unknown time"` and `"No title"` for a missing publication time and headline.
Absence therefore becomes type-indistinguishable from a real value, and no downstream
code can filter on recency or establish whether an item existed at detection.

### 1.6 A composite pressure score existed but did not gate the label

At `b016d92f`, `core/squeeze_score.py::compute_squeeze_score()` was displayed as an
independent column while `classify_tier()` **did not yet exist**. Prime/Subprime came
solely from `score_setup()`. A ticker could therefore show a low composite score and
still be labelled Prime — a visible internal inconsistency.

## 2. Probable root causes

Strongly supported by the evidence, but lacking a complete record.

### 2.1 Days to cover was presented as current while resting on a twice-monthly filing

The formula and denominator are sound: `shares_short / average_daily_volume`, where the
denominator is `statistics.mean(volumes[:-1])` — a trailing mean of **completed** daily
bars, correctly excluding the incomplete current bar, matching the rebuilt Phase 2C
contract (ADR 0036).

The numerator derives from a twice-monthly FINRA filing published with a settlement lag,
yet was displayed beside live-updating price and volume with no reporting-period age. The
denominator additionally came from a cache with a **1-hour TTL** at this commit (shortened
to 5 minutes only the following day).

Classified probable rather than confirmed because no BIYA days-to-cover value survives,
so the *displayed* staleness in this specific case cannot be measured — only the
mechanism that produced it.

### 2.2 BIYA was a momentum surfacing, not a short-pressure surfacing

Consistent with §1.1, with the advisor's contemporaneous observation that short interest
"appears to be low," and with the ticker's presence in the screening universe. But every
original field value is unknown, so the actual scoring path for this specific ticker
cannot be reconstructed. This remains an inference from mechanism, not a measurement.

## 3. Unresolved questions

These cannot be answered from the surviving evidence, and are recorded rather than
guessed:

- **What did the platform actually display for BIYA?** Price, change, relative volume,
  float, short float, days to cover, borrow fee, news, score, and tier are all unknown.
  The only direct platform record preserves no field value.
- **Was BIYA labelled Prime, labelled Subprime, or merely present?** Unknown.
- **Was any news item shown for BIYA, and when was it published?** Unknown.
- **What happened to BIYA after detection?** No market data for this symbol exists in the
  workspace at any interval on any date.
- **Does the reported advisor message about BIYA squeezing exist?** It is not in the
  local email record, which ends 2026-07-17 with no BIYA reference. See §6.

## 4. Useful original behavior worth retaining

The original platform was not uniformly wrong, and Phase 3A should preserve these
deliberately:

- **Per-field quality flags.** `shares_short_unavailable`, `days_to_cover_unavailable`,
  `rel_volume_unavailable`, `ttm_squeeze_unavailable`, `ib_borrow_rate_unavailable`,
  `historical_bars_unavailable`, `short_float_percent_provider_supplied`. Genuine,
  per-row missingness tracking.
- **No zero-substitution in the numeric core.** `core/short_interest.py` and
  `core/squeeze_score.py` return `None` with a reason rather than defaulting to zero, and
  the composite excludes missing inputs and renormalizes instead of fabricating them.
- **Provider-discrepancy detection.** `check_short_float_discrepancy()` flags
  calculated-versus-provider disagreement beyond 2.0 points rather than silently picking
  one.
- **Correct volume-baseline construction.** `volumes[:-1]` excludes the incomplete
  current bar.
- **Explicit provenance fields.** `ShortInterestAsOf`, `ShortInterestSource`, `FloatAsOf`,
  `FloatSource`, `IbBorrowRateAsOf` were captured even where unused.

**The defects are concentrated in labelling and presentation, not in the numeric core.**
That is the most useful single finding for Phase 3A: the arithmetic largely survives
scrutiny; the vocabulary wrapped around it does not.

## 5. Required corrections before Phase 3A

1. **Separate discovery from confirmation.** A momentum/liquidity filter is a legitimate
   discovery stage. It must not emit a label asserting squeeze mechanics.
2. **Retire the Prime/Subprime vocabulary.** It asserts a conclusion its inputs cannot
   support. Report rule-by-rule outcomes instead of a collapsed tier.
3. **Label the two short-interest quantities distinctly** — percent-of-float and absolute
   share count — and show both.
4. **Attach reporting-period age and availability age** to every derived quantity built
   on periodic filings, and never present such a quantity as real time.
5. **Surface data delay per field**, so a delayed price is visibly delayed.
6. **Make corroboration failure explicit** rather than silently absent, and corroborate
   with an independent criterion rather than the same rubric.
7. **Replace default-string substitution** with nullable, timezone-aware timestamps,
   separating publication, update, capture, and receipt time.
8. **Do not reinstate a composite as a classification gate.** Report components.

## 6. The premise conflict

The Phase 2V brief states the advisor reported that BIYA "squeezed up yesterday as
predicted by your platform." **No such artifact exists in this workspace.** The local
email record is complete through 2026-07-17 and contains no BIYA reference.

The only recorded advisor statements about BIYA are the opposite in tone: that its short
interest "appears to be low, and I am not sure why," and that "that stock may not
actually be experiencing a squeeze." In the surviving record BIYA is an example of a
*suspected defect*, not a validated success.

This is recorded as a finding, not as a defect in the brief — the message may well exist
outside the workspace. But it cannot be used as evidence, and if produced later it would
still not change the conclusion: with no original values recorded, there is nothing for
an outcome to validate. See ADR 0042.

## 7. Generalization limits

One case cannot validate or invalidate a methodology. This report reconstructs a single
identification and establishes a repeatable format; it does not establish a hit rate, a
false-positive rate, or any claim about the approach as a whole.

The stronger limitation is specific: because no original BIYA value survives, this case
contributes evidence about **the platform's rules** (which are fully reconstructable from
code) and almost none about **this particular selection**. The rule-level findings in §1
generalize across every candidate the platform surfaced. The BIYA-specific findings in §3
generalize to nothing.
