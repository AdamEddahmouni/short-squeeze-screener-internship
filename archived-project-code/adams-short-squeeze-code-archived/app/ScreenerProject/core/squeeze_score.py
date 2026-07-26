# Composite 0-100 short-squeeze-pressure score, requested by the advisor 2026-07-16 ("come back
# and tell me which one is primed to go for a short squeeze"). Inspired by Tapeboard's published
# Short Squeeze Score methodology (a weighted composite of short%-of-float, IB borrow fee, float
# utilization, FINRA short-volume ratio, days-to-cover, price momentum, and borrow-fee change,
# each z-score normalized against a ~500-stock daily universe: https://tapeboard.com/short-squeeze-stocks)
# but deliberately simplified: this app has no market-wide comparison universe to z-score
# normalize against, only the ~50 tickers IB's scanner already flagged that cycle. Using just the
# 3 inputs this app already has (short_float_percent, ib_borrow_fee_rate, days_to_cover), with
# fixed saturation thresholds per component instead of statistical normalization. This is a
# simplified approximation inspired by a published methodology, not a literal replication of it.

# Relative weights kept proportional to Tapeboard's own published weights for these same 3
# inputs (short% 25, borrow fee 20, days-to-cover 10 - summing to 55 of their original 100),
# renormalized to sum to 1.0 across just these three - plus a 4th, ttm_squeeze, added 2026-07-17
# per advisor feedback (SQUEEZE_FORMULA_REDESIGN_HANDOFF.md): Tapeboard's own methodology has no
# TTM Squeeze component at all (this app's own addition, not part of the source methodology), so
# its weight (20) is a judgment call, not derived from theirs - elevated because it's the
# advisor's most literal, explicit ask ("put that as a column so we can do sorting", "that's not
# really a squeeze" about a ticker with TTM squeeze not on). Starting calibration, not
# statistically validated - retune once tests/evaluate_historical_squeezes.py has real evidence.
_WEIGHTS = {"short_float": 25 / 75, "borrow_fee": 20 / 75, "days_to_cover": 10 / 75, "ttm_squeeze": 20 / 75}

# Value at/above which a component saturates at the maximum sub-score of 100. Calibrated from
# commonly-cited squeeze-setup thresholds in short-interest literature (short float above
# ~20-40%, days-to-cover above ~5-10, and hard-to-borrow fee rates in the tens of percent are all
# widely treated as "extreme") - a reasonable calibration, not derived from a specific published
# statistical procedure. ttm_squeeze has no saturation point - it's state-based (_ttm_score
# below), not a linear ramp, since only compute_ttm_squeeze()'s squeeze_on/momentum sign are
# reliable, not momentum's exact magnitude (core/technical_indicators.py).
_SATURATION = {"short_float": 50.0, "borrow_fee": 50.0, "days_to_cover": 10.0}


def _saturating_linear_score(value, saturation_point):
    """Maps [0, saturation_point] linearly onto [0, 100]; clamped at the ends. None in, None
    out - a missing input is excluded from the composite below, never treated as zero."""
    if value is None:
        return None
    if value <= 0:
        return 0.0
    if value >= saturation_point:
        return 100.0
    return round((value / saturation_point) * 100, 1)


def _ttm_score(ttm_squeeze_on, ttm_squeeze_momentum):
    """State-based sub-score for TTM Squeeze (core/technical_indicators.py::compute_ttm_squeeze()):
    squeeze_on (volatility actively compressed, often ahead of a breakout) scores highest;
    squeeze_on=False with positive momentum (already released, bullish direction) scores a
    middle value; anything else scores zero. Deliberately ignores momentum's magnitude - only
    its sign and the squeeze_on state are trustworthy per that function's own docstring. None in
    (not enough bar history yet), None out - excluded from the composite below like any other
    missing input, never treated as zero."""
    if ttm_squeeze_on is None:
        return None
    if ttm_squeeze_on:
        return 100.0
    return 60.0 if (ttm_squeeze_momentum is not None and ttm_squeeze_momentum > 0) else 0.0


def _sub_scores(short_float_percent, ib_borrow_fee_rate, days_to_cover, ttm_squeeze_on=None,
                 ttm_squeeze_momentum=None):
    return {
        "short_float": _saturating_linear_score(short_float_percent, _SATURATION["short_float"]),
        "borrow_fee": _saturating_linear_score(ib_borrow_fee_rate, _SATURATION["borrow_fee"]),
        "days_to_cover": _saturating_linear_score(days_to_cover, _SATURATION["days_to_cover"]),
        "ttm_squeeze": _ttm_score(ttm_squeeze_on, ttm_squeeze_momentum),
    }


def compute_squeeze_score(short_float_percent, ib_borrow_fee_rate, days_to_cover,
                           ttm_squeeze_on=None, ttm_squeeze_momentum=None):
    """Composite 0-100 score combining official short interest (short_float_percent), IB's live
    borrow cost (ib_borrow_fee_rate - core/ib_borrow_rate.py), days-to-cover, and TTM Squeeze
    state (ttm_squeeze_on/ttm_squeeze_momentum, added 2026-07-17 - see _ttm_score above). Higher
    means more squeeze pressure across the inputs available. Missing inputs are excluded and the
    remaining weights renormalized rather than fabricating a value from absent data; returns
    None only when every input is missing (nothing to score). ttm_squeeze_on/momentum default to
    None (excluded) so existing callers that don't pass them keep working unchanged."""
    sub_scores = _sub_scores(short_float_percent, ib_borrow_fee_rate, days_to_cover,
                              ttm_squeeze_on, ttm_squeeze_momentum)
    available = {name: score for name, score in sub_scores.items() if score is not None}
    if not available:
        return None

    weight_total = sum(_WEIGHTS[name] for name in available)
    weighted_sum = sum(_WEIGHTS[name] * score for name, score in available.items())
    return round(weighted_sum / weight_total, 1)


def compute_squeeze_score_breakdown(short_float_percent, ib_borrow_fee_rate, days_to_cover,
                                     ttm_squeeze_on=None, ttm_squeeze_momentum=None):
    """Same inputs as compute_squeeze_score(), but returns the four per-component sub-scores
    (each 0-100, or None if that input was missing) instead of the single composite - lets the
    web UI show which factor is actually driving a ticker's score instead of just the final
    number. Purely additive: compute_squeeze_score()'s own signature/behavior is unchanged."""
    return _sub_scores(short_float_percent, ib_borrow_fee_rate, days_to_cover,
                        ttm_squeeze_on, ttm_squeeze_momentum)


# Prime/Subprime gate (2026-07-17 redesign, SQUEEZE_FORMULA_REDESIGN_HANDOFF.md), replacing
# core/scoring.py::score_setup() for classification purposes. score_setup() itself is unchanged
# and still used for cross-provider corroboration only (core/schwab_api.py's
# score_tickers_for_corroboration()) - that reuse is deliberate (CROSS_PROVIDER_CORROBORATION_PLAN.md
# §3.1) and changing it wasn't part of this redesign's scope. These thresholds are the starting
# sketch from planning, not yet statistically validated - retune once
# tests/evaluate_historical_squeezes.py has real evidence.
_TIER_THRESHOLDS = {"prime": 70.0, "prime_short_float_floor": 5.0, "subprime": 40.0}


def classify_tier(squeeze_score, short_float_percent):
    """Prime = composite squeeze_score >= 70 AND short_float_percent >= 5 (a floor so a high
    score driven entirely by borrow fee/days-to-cover on a low-short-interest name doesn't alone
    qualify). Subprime = 40-69, no floor. Anything else, or a None score (nothing to classify),
    returns None - the caller drops the row rather than defaulting it into a tier."""
    if squeeze_score is None:
        return None
    if squeeze_score >= _TIER_THRESHOLDS["prime"] and (short_float_percent or 0) >= _TIER_THRESHOLDS["prime_short_float_floor"]:
        return "prime"
    if squeeze_score >= _TIER_THRESHOLDS["subprime"]:
        return "subprime"
    return None


def is_squeeze_confirmed(rel_volume, change_percent, ttm_squeeze_momentum):
    """Independent 'is this actively squeezing right now' flag (advisor 2026-07-17: 'we don't
    want to open them one by one - that's too late'), separate from Prime/Subprime tier. Requires
    high relative volume, a large price move already underway, and TTM momentum not contradicting
    the move. Starting calibration, not validated - the 50% change threshold is a guess loosely
    anchored to the advisor's own '80, 90, 100, 200, 300' comment about what a real squeeze move
    looks like; retune once tests/evaluate_historical_squeezes.py has real evidence. False
    whenever a required input is missing - never a fabricated True from absent data."""
    if rel_volume is None or change_percent is None:
        return False
    if rel_volume < 5 or abs(change_percent) < 50:
        return False
    if ttm_squeeze_momentum is not None and ttm_squeeze_momentum < 0:
        return False
    return True


def is_ttm_squeeze_fired(prev_squeeze_on, current_squeeze_on, current_momentum):
    """True exactly when TTM compression just released: was on last time we saw this ticker
    (from the same data source - see Controller._apply_ttm_fired), isn't on now, and momentum
    doesn't contradict a bullish release. False whenever the prior observation is missing -
    never a fabricated True from absent data. Independent of Prime/Subprime tier and
    squeeze_score, same as is_squeeze_confirmed() above - this is the "catch it before it jumps"
    answer to the same advisor complaint, but a leading transition event instead of a lagging
    already-moved-50% confirmation."""
    if prev_squeeze_on is not True or current_squeeze_on is not False:
        return False
    if current_momentum is not None and current_momentum < 0:
        return False
    return True
