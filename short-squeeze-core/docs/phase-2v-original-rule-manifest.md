# Phase 2V Original Platform Rule Manifest

Descriptive reconstruction of the original screener's rules **as actually implemented**
at the moment BIYA was observed. This is evidence, not judgement: nothing here is
silently corrected, and where implementation contradicts documentation both are
recorded and the contradiction is the finding.

## 0. Which code this describes, and why it matters

All rules below are read from `ScreenerProject` commit **`b016d92f`**
(`2026-07-17T11:56:43` America/New_York) — the last commit before the advisor meeting
began at `12:46:15`.

This is **not** the archived working tree. The archived checkout is `6dbefd1a`, which
includes commit `5a0f6eb4`, *"Redesign Prime/Subprime classification around a
squeeze-mechanics composite"*, made at `15:39:27` — 2h53m **after** the meeting.

Describing the original rules from the checked-out tree would attribute
`core/squeeze_score.py::classify_tier()` to the BIYA event. **That function did not
exist when BIYA was surfaced.** Verified by `git grep classify_tier b016d92f`, which
returns nothing.

Read-only inspection only: no archived repository was reset, checked out, cleaned,
committed, amended, merged, reformatted, or otherwise modified.

## 1. RULE-001 — Prime/Subprime classification

| Field | Value |
| --- | --- |
| `display_name` | "Prime Setup" / "Subprime Setup" |
| `source_file` | `core/scoring.py`, applied at `core/ib_api.py:208` and `core/filters.py:98` |
| `source_lines_or_symbol` | `score_setup()`; grouping at `rank_and_group_stocks_ib()` lines 250–253 |
| `implemented_formula` | `+1 if 2 <= price <= 20`; `+1 if change_percent >= 10`; `+1 if rel_volume >= 5`; `+1 if short_float_percent >= 5`. **Prime = 4/4, Subprime = 3/4**, anything lower is dropped |
| `intended_meaning` | "This ticker is set up for a short squeeze" |
| `actual_input_fields` | `price`, `change_percent`, `rel_volume`, `short_float_percent` |
| `providers` | IB (price/change/volume), yfinance `.info` (float, shares short) |
| `missing_value_behavior` | Comparison against `None` raises; upstream `_build_row()` supplies defaults so a row is scored regardless |
| `known_mislabeling` | **Yes — the label names a squeeze mechanic the formula never evaluates** |

**The central finding of this phase.** `score_setup()` reads four inputs, and **none of
them is a squeeze mechanic**. Borrow fee, days to cover, and TTM Squeeze are computed
and displayed, but are never scored. A ticker is labelled "Prime Setup" — presented as
a squeeze classification — on the strength of a price band, a momentum threshold, a
liquidity threshold, and a single short-float floor.

The project's own contemporaneous handoff (ART-003) reaches the same conclusion
independently:

> "`score_setup()` never looks at borrow fee, days-to-cover, or TTM Squeeze at all. It's
> a price/momentum/liquidity/short-float screener, not a squeeze-mechanics detector.
> That gap is the direct cause of the advisor's LBGJ/BIYA complaints."

This explains both of the advisor's live objections without needing any BIYA field
value: LBGJ at +13% qualified because 13 ≥ 10, and BIYA surfaced on momentum while its
short interest was visibly low.

**Classification: `MOMENTUM_DISCOVERY_ONLY`.** The rubric is a serviceable
low-float-mover discovery filter. It cannot confirm short-squeeze pressure, and the
Prime/Subprime vocabulary asserts a conclusion the inputs do not support.

## 2. RULE-002 — "Short Interest (%)" column

| Field | Value |
| --- | --- |
| `display_name` | "Short Interest (%)" — renamed from "Short Float (%)" at `05c81f85`, `2026-07-17T10:42:26`, **2h04m before the meeting** |
| `source_file` | `core/short_interest.py::calculate_short_float_percent`; display in `ui/view.py` and `static/index.html` |
| `implemented_formula` | `round((shares_short / float_shares) * 100, 2)` |
| `original_output_field` | `ShortFloat` / `short_float_percent` (internal names unchanged by the rename) |
| `providers` | yfinance `.info` — `shares_short`, `float_shares` |
| `missing_value_behavior` | Returns `(None, reason)`; falls back to yfinance's own `shortPercentOfFloat` with flag `short_float_percent_provider_supplied`; disagreement beyond 2.0 points raises `short_float_percent_discrepancy` |
| `known_mislabeling` | **Yes** |

The rename commit's own message argues the new label is more accurate:

> "The value itself already is the textbook short-interest formula
> (`shares_short / float_shares`); this just makes the on-screen name match what it
> actually is."

That reasoning is half right, and the half that is wrong is the half that matters.
`shares_short / float_shares` is short interest **as a percentage of float** — a *ratio*.
"Short Interest" unqualified conventionally denotes the **absolute reported share
count**. A column headed "Short Interest (%)" showing a percent-of-float is therefore
ambiguous at best, and it changed **two hours before** the advisor looked at the screen
and said BIYA's *"short interest appears to be low, and I am not sure why."*

The underlying arithmetic is correct. The label is not.

**Classification: `MISLABELED`.** The value is sound; the presentation misdescribes it.
The correction is to display both quantities under distinct, unambiguous labels rather
than to change the formula.

## 3. RULE-003 — Days to cover

| Field | Value |
| --- | --- |
| `source_file` | `core/short_interest.py::calculate_days_to_cover`, called at `core/ib_api.py:517` |
| `implemented_formula` | `round(shares_short / average_daily_volume, 2)` |
| Numerator | `shares_short` from yfinance `.info` — ultimately FINRA's **twice-monthly** reported open short position |
| Denominator | `hist["avg_volume"]` = `statistics.mean(volumes[:-1])` (`core/ib_api.py:609`) — trailing mean of **completed** daily bars, current incomplete bar excluded |
| `missing_value_behavior` | `(None, reason)`; flag `days_to_cover_unavailable`; **never defaulted to zero** |
| `timestamp_behavior` | Denominator served from `_hist_cache` with a **1-hour TTL** at this commit (shortened to 5 minutes only on 2026-07-18, `6dbefd1a`) |

The structure is better than expected and deserves credit. Excluding the current
incomplete bar (`volumes[:-1]`) is exactly right, and matches the rebuilt Phase 2C
contract — *published short interest ÷ trailing mean completed daily share volume*
(ADR 0036). Missing inputs return `None` with a reason rather than zero.

Two real defects remain:

1. **Numerator staleness is invisible.** `shares_short` derives from a twice-monthly
   FINRA filing, published with a settlement lag. `short_interest_as_of` is captured
   but the ratio is displayed beside live-updating price and volume with no indication
   that its numerator can be two weeks stale. The composite quantity was presented as
   though it were current — which is precisely the advisor's 2026-07-16 objection to
   "real-time" days to cover.
2. **Denominator staleness up to one hour**, from the cache TTL in force at detection.
3. Single-bar fallback `else volumes[-1]` uses one possibly-incomplete bar when history
   is thin.

**Classification: `SUPPORTED_WITH_CORRECTION`.** The formula and its denominator are
defensible; the required corrections are to surface reporting-period age and
availability age alongside the value, and never to present it as real-time.

For BIYA specifically the value is **not reconstructable** — `shares_short` was never
recorded in any surviving artifact — and is therefore held `UNKNOWN` rather than
estimated from later data.

## 4. RULE-004 — News loading and timestamps

| Field | Value |
| --- | --- |
| `source_file` | `core/yfinance_news_api.py:52`, `core/newsapi_news_api.py:65` |
| `implemented_formula` | `headline = content.get("title", "No title")`; `timestamp = content.get("pubDate", "Unknown time")` |
| Relevance filter | `_mentions_ticker()` — word-boundary regex over title and summary |
| `missing_value_behavior` | **Default string substitution**: a missing publication time becomes the literal string `"Unknown time"`; a missing title becomes `"No title"` |
| `timestamp_behavior` | Provider string passed through unparsed; no timezone normalization; no distinction among publication, update, capture, and receipt time |

A missing publication time is replaced by a display string rather than preserved as a
typed null. Downstream, `"Unknown time"` is indistinguishable from a real timestamp by
type, so no code path can filter on news recency or establish whether an item existed
at detection.

There is no record of whether any news item was shown for BIYA. NewsAPI is queried with
`sortBy=publishedAt&pageSize=10`, so ordering is by publication time, but no
availability-time semantics exist.

**Classification: `MISSING_DEFAULT_SUBSTITUTION`.** The correction is a typed
`published_at` that is nullable, timezone-aware, and separated from capture/receipt
time — which the rebuilt engine already provides (`docs/news-availability-semantics.md`).

## 5. RULE-005 — Market data freshness

| Field | Value |
| --- | --- |
| `source_file` | `core/ib_api.py` market data subscription |
| Observed behavior | IB `Error 10089` for **every** symbol including BIYA: *"Requested market data requires additional subscription… Delayed market data is available."* |
| `timestamp_behavior` | Fell back to delayed data; the interface carried no delayed-data indicator |

Direct platform evidence (ART-001), not inference. Every price, change percent, and
relative volume the advisor saw during the meeting — including BIYA's — was **delayed**,
not real-time, on a screener whose stated goal was minute-by-minute operation.

**Classification: `UNAVAILABLE_AT_DETECTION`** for real-time market data;
**`STALE`** (descriptive) for the delayed values actually displayed.

## 6. RULE-006 — Cross-provider corroboration

| Field | Value |
| --- | --- |
| `source_file` | `core/schwab_api.py::score_tickers_for_corroboration()`, reusing `score_setup()` |
| Observed behavior | Every corroboration call failed with `NameResolutionError` on `api.schwabapi.com` |

Corroboration reapplies the *same* four-point rubric to a second provider's numbers.
Two providers agreeing under one rubric is weaker evidence than it appears: it tests
data agreement, not rule validity. During the meeting it was moot — DNS failed, so no
corroboration ran at all, and the absence was not surfaced in the interface.

**Classification: `REDUNDANT`** as designed (same rubric, no independent information),
and **`UNAVAILABLE_AT_DETECTION`** as it actually behaved.

## 7. RULE-007 — Composite Squeeze Score (present, but not the label source)

| Field | Value |
| --- | --- |
| `source_file` | `core/squeeze_score.py::compute_squeeze_score` |
| `implemented_formula` | Weighted mean of saturating-linear sub-scores: `short_float` 25/55, `borrow_fee` 20/55, `days_to_cover` 10/55; missing inputs excluded and remaining weights renormalized |
| Role at detection | **Displayed as an independent column only.** It did not gate Prime/Subprime |

At `b016d92f` this composite existed and was shown, but `classify_tier()` did not exist
and Prime/Subprime came solely from RULE-001. A ticker could therefore display a low
composite score and still be labelled "Prime" — the exact inconsistency the advisor
was reacting to.

Its missing-input handling is genuinely good: `None` in, `None` out, excluded from the
composite and never treated as zero.

**Classification: `SUPPORTED_WITH_CORRECTION`** as a transparent per-component
breakdown; the correction is that its components must be reported separately rather
than collapsed into one number, and Phase 3A must not resurrect it as a composite gate.

## 8. Original behavior worth retaining

Recorded deliberately — the original platform was not uniformly wrong, and Phase 3A
should preserve these:

- **Quality flags.** `shares_short_unavailable`, `days_to_cover_unavailable`,
  `rel_volume_unavailable`, `ttm_squeeze_unavailable`, `ib_borrow_rate_unavailable`,
  `historical_bars_unavailable`, `short_float_percent_provider_supplied`. Per-row,
  per-field missingness tracking — a real strength.
- **No zero-substitution in the numeric core.** `core/short_interest.py` and
  `core/squeeze_score.py` return `None` with a reason instead of defaulting to zero.
- **Provider-discrepancy detection.** `check_short_float_discrepancy()` flags
  calculated-versus-provider disagreement beyond 2.0 points rather than silently
  picking one.
- **Correct volume-baseline construction.** `volumes[:-1]` excludes the incomplete
  current bar.
- **Explicit provenance fields.** `ShortInterestAsOf`, `ShortInterestSource`,
  `FloatAsOf`, `FloatSource`, `IbBorrowRateAsOf` were captured even when unused.

The defects are concentrated in **labelling and presentation**, not in the numeric
core. That is the single most useful finding for Phase 3A.

## 9. Summary

| Rule | Classification |
| --- | --- |
| RULE-001 Prime/Subprime `score_setup()` | `MOMENTUM_DISCOVERY_ONLY` |
| RULE-002 "Short Interest (%)" column | `MISLABELED` |
| RULE-003 Days to cover | `SUPPORTED_WITH_CORRECTION` |
| RULE-004 News loading and timestamps | `MISSING_DEFAULT_SUBSTITUTION` |
| RULE-005 Market data freshness | `UNAVAILABLE_AT_DETECTION` / `STALE` |
| RULE-006 Cross-provider corroboration | `REDUNDANT` / `UNAVAILABLE_AT_DETECTION` |
| RULE-007 Composite Squeeze Score | `SUPPORTED_WITH_CORRECTION` |

Every classification above is a **methodology** judgement about a rule. None is a
statement about BIYA's quality as a stock, and none is a trading label.
