# Pure short-interest formula helpers, per FRESH_START_DATA_AND_SHORT_INTEREST_PLAN.md §2.
#
# shares_short is the officially reported open short position count for a security on a
# settlement date (FINRA requires twice-monthly reporting) - it is not daily short-sale
# volume and not a broker's shortable-share inventory (see ib_shortable_shares in
# core/ib_api.py). These functions never substitute one for the other; missing/invalid
# inputs return None plus a reason instead of silently defaulting to zero.

DEFAULT_DISCREPANCY_TOLERANCE_POINTS = 2.0


def calculate_short_float_percent(shares_short, float_shares):
    """(shares_short / float_shares) * 100. Returns (value, reason); reason is None on success."""
    if shares_short is None or float_shares is None:
        return None, "missing_shares_short_or_float_shares"
    if shares_short < 0:
        return None, "negative_shares_short"
    if float_shares <= 0:
        return None, "non_positive_float_shares"
    return round((shares_short / float_shares) * 100, 2), None


def calculate_days_to_cover(shares_short, average_daily_volume):
    """FINRA's days-to-cover formula: shares_short / average_daily_share_volume."""
    if shares_short is None or average_daily_volume is None:
        return None, "missing_shares_short_or_average_volume"
    if shares_short < 0:
        return None, "negative_shares_short"
    if average_daily_volume <= 0:
        return None, "non_positive_average_volume"
    return round(shares_short / average_daily_volume, 2), None


def check_short_float_discrepancy(calculated_percent, provider_percent,
                                   tolerance_points=DEFAULT_DISCREPANCY_TOLERANCE_POINTS):
    """Returns a quality-flag string if a provider-supplied Short Float% disagrees with the
    locally calculated one beyond tolerance_points, else None."""
    if calculated_percent is None or provider_percent is None:
        return None
    if abs(calculated_percent - provider_percent) > tolerance_points:
        return "short_float_percent_discrepancy"
    return None
