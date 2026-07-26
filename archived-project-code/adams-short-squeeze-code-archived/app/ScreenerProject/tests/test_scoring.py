import os
import sys

sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

from core.scoring import score_setup


def test_score_setup_full_match_scores_four():
    assert score_setup(price=10, change_percent=15, rel_volume=6, short_float_percent=8) == 4


def test_score_setup_boundaries_count_as_matches():
    assert score_setup(price=2, change_percent=10, rel_volume=5, short_float_percent=5) == 4
    assert score_setup(price=20, change_percent=10, rel_volume=5, short_float_percent=5) == 4


def test_score_setup_just_outside_boundaries_do_not_count():
    assert score_setup(price=1.99, change_percent=10, rel_volume=5, short_float_percent=5) == 3
    assert score_setup(price=20.01, change_percent=10, rel_volume=5, short_float_percent=5) == 3
    assert score_setup(price=10, change_percent=9.99, rel_volume=5, short_float_percent=5) == 3
    assert score_setup(price=10, change_percent=10, rel_volume=4.99, short_float_percent=5) == 3
    assert score_setup(price=10, change_percent=10, rel_volume=5, short_float_percent=4.99) == 3


def test_score_setup_no_match_scores_zero():
    assert score_setup(price=50, change_percent=1, rel_volume=1, short_float_percent=1) == 0


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
