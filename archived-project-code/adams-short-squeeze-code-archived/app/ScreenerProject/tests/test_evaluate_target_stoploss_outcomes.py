import os
import sys

sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

import evaluate_target_stoploss_outcomes as evaluator


def test_first_level_hit_returns_target_when_high_reaches_target_first():
    bars = [("2026-07-10", 5.0, 4.5), ("2026-07-11", 6.5, 5.8)]
    outcome, date = evaluator.first_level_hit(bars, target_price=6.0, stop_price=3.0)
    assert outcome == "target"
    assert date == "2026-07-11"


def test_first_level_hit_returns_stop_when_low_breaches_stop_first():
    bars = [("2026-07-10", 5.0, 2.5), ("2026-07-11", 6.5, 5.8)]
    outcome, date = evaluator.first_level_hit(bars, target_price=6.0, stop_price=3.0)
    assert outcome == "stop"
    assert date == "2026-07-10"


def test_first_level_hit_picks_earliest_bar_when_target_hit_later_than_stop():
    bars = [("2026-07-10", 5.0, 4.5), ("2026-07-11", 5.5, 2.0), ("2026-07-12", 6.5, 5.0)]
    outcome, date = evaluator.first_level_hit(bars, target_price=6.0, stop_price=3.0)
    assert outcome == "stop"
    assert date == "2026-07-11"


def test_first_level_hit_returns_both_when_same_bar_crosses_both_levels():
    bars = [("2026-07-10", 7.0, 2.0)]
    outcome, date = evaluator.first_level_hit(bars, target_price=6.0, stop_price=3.0)
    assert outcome == "both"
    assert date == "2026-07-10"


def test_first_level_hit_returns_none_when_neither_touched():
    bars = [("2026-07-10", 5.0, 4.5), ("2026-07-11", 5.2, 4.6)]
    outcome, date = evaluator.first_level_hit(bars, target_price=6.0, stop_price=3.0)
    assert outcome is None
    assert date is None


def test_first_level_hit_returns_none_for_empty_bars():
    outcome, date = evaluator.first_level_hit([], target_price=6.0, stop_price=3.0)
    assert outcome is None
    assert date is None


def main():
    tests = [obj for name, obj in list(globals().items()) if name.startswith("test_")]
    passed, failed = 0, 0
    for test in tests:
        try:
            test()
            print(f"PASS {test.__name__}")
            passed += 1
        except Exception as error:
            print(f"FAIL {test.__name__}: {error}")
            failed += 1
    print(f"\n{passed} passed, {failed} failed")
    raise SystemExit(1 if failed else 0)


if __name__ == "__main__":
    main()
