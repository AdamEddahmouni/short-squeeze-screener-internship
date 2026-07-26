import statistics

# Shared technical-indicator math for any provider that only supplies raw price/volume bars
# (core/ib_api.py, core/schwab_api.py, ...) - kept in one place so every provider's RSI/
# volatility figures are computed identically instead of each reimplementing its own copy.


def compute_rsi(closes, period=14):
    """Standard Wilder's RSI over a closing-price series. Falls back to 50 (neutral)
    on insufficient data."""
    if len(closes) < period + 1:
        return 50.0

    deltas = [closes[i] - closes[i - 1] for i in range(1, len(closes))]
    gains = [d if d > 0 else 0 for d in deltas]
    losses = [-d if d < 0 else 0 for d in deltas]

    avg_gain = sum(gains[-period:]) / period
    avg_loss = sum(losses[-period:]) / period

    if avg_loss == 0:
        return 100.0

    rs = avg_gain / avg_loss
    return round(100 - (100 / (1 + rs)), 2)


def compute_weekly_volatility(closes, days=5):
    """Stdev of daily returns over the most recent week, expressed as a percent."""
    if len(closes) < days + 1:
        return 0.0

    recent = closes[-(days + 1):]
    returns = [
        (recent[i] - recent[i - 1]) / recent[i - 1]
        for i in range(1, len(recent)) if recent[i - 1]
    ]
    if len(returns) < 2:
        return 0.0

    return round(statistics.stdev(returns) * 100, 2)


def _true_range(high, low, prev_close):
    return max(high - low, abs(high - prev_close), abs(low - prev_close))


def _average_true_range(highs, lows, closes, period):
    """Wilder's ATR isn't used here - a plain rolling mean of True Range over `period` bars,
    which is what the standard TTM Squeeze definition (and most retail platforms' default
    implementation) actually uses for the Keltner Channel width."""
    trues = [_true_range(highs[i], lows[i], closes[i - 1]) for i in range(1, len(closes))]
    if len(trues) < period:
        return None
    return statistics.mean(trues[-period:])


def _linreg_endpoint(values):
    """Least-squares line fit to `values` (evenly spaced), returned at its most recent point -
    the standard TTM Squeeze momentum histogram value."""
    n = len(values)
    xs = range(n)
    x_mean = (n - 1) / 2
    y_mean = sum(values) / n
    denominator = sum((x - x_mean) ** 2 for x in xs)
    if denominator == 0:
        return 0.0
    slope = sum((x - x_mean) * (y - y_mean) for x, y in zip(xs, values)) / denominator
    intercept = y_mean - slope * x_mean
    return slope * (n - 1) + intercept


# John Carter's TTM Squeeze (popularized on thinkorswim/TD Ameritrade, PROJECT_NOTES.md's §6
# advisor-priority discussion): compression of Bollinger Bands inside Keltner Channels signals
# volatility is unusually low and building - often ahead of a sharp breakout in either direction.
# Display-only, like Float - not a Prime/Subprime scoring criterion, since it measures a
# different thing (a volatility setup, not this app's price/change/relvol/short-float rubric)
# and changing that rubric's validated behavior is out of scope for adding this signal.
#
# Simplified from the exact thinkorswim study in one place: the momentum histogram's Donchian
# midline/SMA reference is computed once over the current period window rather than recomputed
# at every bar in the regression - a standard, widely-used approximation (matches most open-
# source TTM Squeeze implementations), not the literal broker formula. Treat SqueezeOn as the
# reliable signal; SqueezeMomentum's sign (bullish/bearish direction) is the useful part of the
# value, not its exact magnitude.
def compute_ttm_squeeze(highs, lows, closes, period=20, bb_mult=2.0, kc_mult=1.5):
    """Returns (squeeze_on, momentum). squeeze_on is True when Bollinger Bands sit entirely
    inside the Keltner Channel (compressed volatility); momentum is a linear-regression estimate
    of price displacement from the channel midline (positive = bullish, negative = bearish).
    Returns (None, None) when there isn't yet enough bar history (period + 1 bars minimum)."""
    if len(closes) < period + 1 or len(highs) < period + 1 or len(lows) < period + 1:
        return None, None

    recent_closes = closes[-period:]
    basis = statistics.mean(recent_closes)
    stdev = statistics.stdev(recent_closes)
    bb_upper, bb_lower = basis + bb_mult * stdev, basis - bb_mult * stdev

    atr = _average_true_range(highs, lows, closes, period)
    if atr is None:
        return None, None
    kc_upper, kc_lower = basis + kc_mult * atr, basis - kc_mult * atr

    squeeze_on = bb_upper < kc_upper and bb_lower > kc_lower

    donchian_mid = (max(highs[-period:]) + min(lows[-period:])) / 2
    avg_mid = (donchian_mid + basis) / 2
    momentum_series = [c - avg_mid for c in recent_closes]

    return squeeze_on, round(_linreg_endpoint(momentum_series), 4)
