def score_setup(price, change_percent, rel_volume, short_float_percent):
    """Shared Prime/Subprime rubric: price band, change%, relative volume, short-float% - one
    point each, 4/4. Used identically by core/ib_api.py, core/schwab_api.py, core/filters.py's
    rank_and_group_stocks_*() (Prime = 4, Subprime = 3) and by cross-provider corroboration, which
    reapplies this same rubric to a second provider's numbers for the same ticker rather than
    inventing a separate matching criterion."""
    score = 0
    if 2 <= price <= 20:
        score += 1
    if change_percent >= 10:
        score += 1
    if rel_volume >= 5:
        score += 1
    if short_float_percent >= 5:
        score += 1
    return score
