import os
import sys

sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

from core.squeeze_score import compute_squeeze_score, classify_tier

# Historical-squeeze calibration check (SQUEEZE_FORMULA_REDESIGN_HANDOFF.md §4.6), following this
# project's "evidence over formula" pattern (see tests/evaluate_squeeze_score_outcomes.py) - but
# calibrating against known, already-happened squeezes instead of this app's own live picks.
# Advisor 2026-07-17: "you can actually ask AI which of the tickers are actually facing a short
# squeeze... see how you can tweak the formula to match that kind of behavior." Not wired into the
# main app loop or CI; run manually when recalibrating core/squeeze_score.py's weights/thresholds.
#
# Every figure below is a real, researched, cited number, not an invented one - the plan for this
# work was explicit that fabricating "ground truth" here would undermine the entire point of
# calibrating against reality. Precision and sourcing vary by ticker (noted per entry below); this
# script and its citations should be re-verified/tightened before being treated as authoritative
# regression data.
#
# Only short_float_percent (and, where sourced, borrow fee) could be reliably dated to *before*
# each stock's main breakout move - days_to_cover and TTM Squeeze state aren't available
# retroactively without the original daily OHLC bar history, which is out of scope here (per the
# handoff, this check targets short_float/borrow_fee/days_to_cover, and TTM Squeeze is this app's
# own technical-indicator addition with no independent historical dataset to source from). Missing
# components are excluded and the composite renormalizes over what's available, per
# core/squeeze_score.py's own None-handling - not treated as zero.
HISTORICAL_SQUEEZES = [
    {
        "ticker": "GME",
        "as_of": "2021-01-15 (mid-January, before the Jan 25-28 parabolic move)",
        "short_float_percent": 114.0,
        "ib_borrow_fee_rate": None,
        "days_to_cover": None,
        "source": (
            "Wikipedia, 'GameStop short squeeze': short interest 'fell to 39 percent of "
            "free-floating shares, from 114 percent in mid-January' (retrospective figure "
            "dated Feb 1, 2021, citing contemporaneous reporting)."
        ),
    },
    {
        "ticker": "AMC",
        "as_of": "2021-05-28 (before AMC's larger early-June 2021 leg to its cycle peak)",
        "short_float_percent": 20.0,
        "ib_borrow_fee_rate": None,
        "days_to_cover": None,
        "source": (
            "Forbes, 'AMC's Stock Set Up For A Short Squeeze' (Chuck Jones, 2021-05-28), citing "
            "S3 Partners' Ihor Dusaniwsky: '89.6 million shares are shorted or 20% of the 448 "
            "million shares.'"
        ),
    },
    {
        "ticker": "KOSS",
        "as_of": "2021-01-25 (day before KOSS's Jan 26-27 spike)",
        "short_float_percent": 35.0,
        "ib_borrow_fee_rate": None,
        "days_to_cover": None,
        "source": (
            "LOWER CONFIDENCE than the other three: multiple contemporaneous outlets "
            "(Urban Milwaukee 2021-01-26, valuethemarkets.com) independently reported KOSS "
            "'short interest above 35%' as part of a circulated WallStreetBets-adjacent "
            "short-interest screen (attributed to a Will Meade tweet), not a single named "
            "primary data provider (S3/Ortex/FINRA) I could directly verify. Treat this figure "
            "as an approximate, secondary citation, not a settlement-date-precise one."
        ),
    },
    {
        "ticker": "BBBY",
        "as_of": "2022-07-31 (FINRA settlement date, before the Aug 12-17 2022 Ryan Cohen rally)",
        "short_float_percent": 47.2,
        "ib_borrow_fee_rate": None,
        "days_to_cover": None,
        "source": (
            "LOWER CONFIDENCE, same caveat as KOSS: figure ('29.07 million shares... 47.2% of "
            "the float' as of the 2022-07-31 settlement) came from aggregated financial-data "
            "reporting rather than a single directly-fetched primary article. A later, "
            "higher figure (52.51% / 32.34M shares, S3 Partners via wccftech) exists but is "
            "from during/after the rally had already started and was deliberately not used here "
            "- it would no longer be 'before the move' data."
        ),
    },
]

# Bar every historical squeeze must clear: classified as an elevated squeeze-risk setup at all
# (Prime or Subprime), not dropped as noise. NOT "must be Prime" - see AMC below, where only
# short_float_percent could be sourced (no borrow fee/days-to-cover), and the composite's
# available-inputs-only renormalization (core/squeeze_score.py) lands it right at the Subprime
# boundary rather than Prime. That's an honest result of incomplete historical data, not a bug -
# forcing it to "pass" as Prime would mean fabricating a borrow-fee/days-to-cover number this
# script doesn't actually have, which the plan for this work explicitly ruled out.
def main():
    print("Historical-squeeze calibration check (core/squeeze_score.py, 2026-07-17 redesign)\n")
    all_classified = True
    for case in HISTORICAL_SQUEEZES:
        score = compute_squeeze_score(
            case["short_float_percent"], case["ib_borrow_fee_rate"], case["days_to_cover"]
        )
        tier = classify_tier(score, case["short_float_percent"])
        status = "OK" if tier is not None else "MISS"
        if tier is None:
            all_classified = False
        print(f"{case['ticker']:6} as_of={case['as_of']}")
        print(f"       squeeze_score={score}  tier={tier or 'none (dropped)'}  [{status}]")
        print(f"       source: {case['source']}\n")

    prime_count = sum(
        1 for case in HISTORICAL_SQUEEZES
        if classify_tier(
            compute_squeeze_score(case["short_float_percent"], case["ib_borrow_fee_rate"], case["days_to_cover"]),
            case["short_float_percent"],
        ) == "prime"
    )
    print(f"{prime_count}/{len(HISTORICAL_SQUEEZES)} classified Prime, "
          f"{len(HISTORICAL_SQUEEZES) - prime_count}/{len(HISTORICAL_SQUEEZES)} Subprime or dropped.")

    if not all_classified:
        print("\nFAIL: at least one known historical squeeze was dropped entirely (score below "
              "the Subprime floor) using only the data available before its breakout.")
        raise SystemExit(1)

    print("\nPASS: every known historical squeeze cleared at least the Subprime bar using only "
          "data available before its breakout. Tickers landing Subprime rather than Prime (see "
          "above) reflect incomplete historical sourcing (missing borrow fee/days-to-cover), not "
          "necessarily a formula miscalibration - re-run this check if better-sourced figures for "
          "those components become available.")


if __name__ == "__main__":
    main()
