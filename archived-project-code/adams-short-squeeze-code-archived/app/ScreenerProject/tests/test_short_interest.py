import os
import sys

sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

from core.short_interest import (
    calculate_days_to_cover,
    calculate_short_float_percent,
    check_short_float_discrepancy,
)


def test_short_float_percent_hand_computed_example():
    value, reason = calculate_short_float_percent(2500000, 15000000)
    assert value == 16.67
    assert reason is None


def test_short_float_percent_missing_inputs_returns_reason():
    assert calculate_short_float_percent(None, 15000000) == (None, "missing_shares_short_or_float_shares")
    assert calculate_short_float_percent(2500000, None) == (None, "missing_shares_short_or_float_shares")


def test_short_float_percent_rejects_negative_shares_short():
    value, reason = calculate_short_float_percent(-1, 15000000)
    assert value is None
    assert reason == "negative_shares_short"


def test_short_float_percent_rejects_non_positive_float():
    value, reason = calculate_short_float_percent(2500000, 0)
    assert value is None
    assert reason == "non_positive_float_shares"


def test_days_to_cover_hand_computed_example():
    value, reason = calculate_days_to_cover(2500000, 1000000)
    assert value == 2.5
    assert reason is None


def test_days_to_cover_missing_inputs_returns_reason():
    assert calculate_days_to_cover(None, 1000000) == (None, "missing_shares_short_or_average_volume")
    assert calculate_days_to_cover(2500000, None) == (None, "missing_shares_short_or_average_volume")


def test_days_to_cover_rejects_non_positive_average_volume():
    value, reason = calculate_days_to_cover(2500000, 0)
    assert value is None
    assert reason == "non_positive_average_volume"


def test_discrepancy_flagged_beyond_tolerance():
    assert check_short_float_discrepancy(16.67, 10.0) == "short_float_percent_discrepancy"


def test_discrepancy_not_flagged_within_tolerance():
    assert check_short_float_discrepancy(16.67, 15.5) is None


def test_discrepancy_not_flagged_when_either_value_missing():
    assert check_short_float_discrepancy(None, 10.0) is None
    assert check_short_float_discrepancy(16.67, None) is None


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
