import os
import sys

sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

from core.technical_indicators import compute_rsi, compute_weekly_volatility, compute_ttm_squeeze


def test_rsi_neutral_default_on_insufficient_data():
    assert compute_rsi([1, 2, 3]) == 50.0


def test_rsi_all_gains_is_100():
    closes = [10 + i for i in range(15)]  # steadily rising, no losses
    assert compute_rsi(closes) == 100.0


def test_rsi_hand_computed_example():
    closes = [100, 101, 102, 103, 104, 105, 106, 107,
              106, 105, 104, 103, 102, 101, 100]
    rsi = compute_rsi(closes)
    assert 0 <= rsi <= 100


def test_weekly_volatility_zero_on_flat_prices():
    closes = [100, 100, 100, 100, 100, 100]
    assert compute_weekly_volatility(closes) == 0.0


def test_weekly_volatility_insufficient_data_returns_zero():
    assert compute_weekly_volatility([100, 101]) == 0.0


# TTM Squeeze (Bollinger Bands vs. Keltner Channels) - added 2026-07-16, requested by the
# advisor (professor feedback: "TTM Squeeze is not yet translated to the table"). Squeeze ON
# means Bollinger Bands sit entirely inside the Keltner Channel - compressed volatility, often
# building ahead of a breakout.

def test_ttm_squeeze_returns_none_on_insufficient_data():
    on, momentum = compute_ttm_squeeze([1] * 5, [1] * 5, [1] * 5)
    assert on is None
    assert momentum is None


def test_ttm_squeeze_on_for_tight_consolidation():
    # Closes barely move day to day (small Bollinger width) but each day still has a normal ~2pt
    # high/low trading range (wider Keltner width from the true range) - the classic squeeze
    # setup: low realized volatility with normal intraday range, not literally zero movement.
    closes = [100 + (i % 2) * 0.1 for i in range(21)]
    highs = [c + 1.0 for c in closes]
    lows = [c - 1.0 for c in closes]
    on, momentum = compute_ttm_squeeze(highs, lows, closes)
    assert on is True
    assert abs(momentum) < 1.0  # flat consolidation - no meaningful directional momentum


def test_ttm_squeeze_off_for_wide_volatile_swings():
    # A trending random walk (not a bounded back-and-forth oscillation, which stays
    # mean-reverting and can still look tight) accumulates real dispersion in closing prices,
    # blowing the Bollinger width out past the Keltner width. Fixed seed for reproducibility.
    import random
    rng = random.Random(1)
    closes = [100]
    for _ in range(20):
        closes.append(closes[-1] + rng.choice([-8, 8]))
    highs = [c + 1.0 for c in closes]
    lows = [c - 1.0 for c in closes]
    on, momentum = compute_ttm_squeeze(highs, lows, closes)
    assert on is False


def test_ttm_squeeze_momentum_sign_tracks_trend_direction():
    rising = [100 + i for i in range(21)]
    falling = [120 - i for i in range(21)]

    _, rising_momentum = compute_ttm_squeeze(
        [c + 0.5 for c in rising], [c - 0.5 for c in rising], rising
    )
    _, falling_momentum = compute_ttm_squeeze(
        [c + 0.5 for c in falling], [c - 0.5 for c in falling], falling
    )

    assert rising_momentum > 0
    assert falling_momentum < 0


def main():
    tests = [obj for name, obj in list(globals().items()) if name.startswith("test_")]
    passed, failed = 0, 0

    for test in tests:
        try:
            test()
            print(f"PASS {test.__name__}")
            passed += 1
        except AssertionError as e:
            print(f"FAIL {test.__name__}: {e}")
            failed += 1

    print(f"\n{passed} passed, {failed} failed")
    raise SystemExit(1 if failed else 0)


if __name__ == "__main__":
    main()
