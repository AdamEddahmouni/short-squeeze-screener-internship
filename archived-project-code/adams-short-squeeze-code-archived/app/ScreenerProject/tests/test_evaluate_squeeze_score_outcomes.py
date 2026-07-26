import os
import sys
import tempfile
from datetime import datetime, timezone

sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

import evaluate_squeeze_score_outcomes as evaluator


def test_score_band_boundaries():
    assert evaluator.score_band(100) == "90+"
    assert evaluator.score_band(90) == "90+"
    assert evaluator.score_band(89.9) == "70-89"
    assert evaluator.score_band(70) == "70-89"
    assert evaluator.score_band(69.9) == "40-69"
    assert evaluator.score_band(40) == "40-69"
    assert evaluator.score_band(39.9) == "0-39"
    assert evaluator.score_band(0) == "0-39"


def test_score_at_or_before_returns_latest_matching_entry():
    history = [
        (datetime(2026, 7, 10, 9, 0, tzinfo=timezone.utc), 50.0),
        (datetime(2026, 7, 10, 9, 15, tzinfo=timezone.utc), 65.0),
        (datetime(2026, 7, 10, 9, 30, tzinfo=timezone.utc), 80.0),
    ]
    when = datetime(2026, 7, 10, 9, 20, tzinfo=timezone.utc)
    assert evaluator.score_at_or_before(history, when) == 65.0


def test_score_at_or_before_returns_none_when_history_starts_after():
    history = [(datetime(2026, 7, 10, 9, 30, tzinfo=timezone.utc), 80.0)]
    when = datetime(2026, 7, 10, 9, 0, tzinfo=timezone.utc)
    assert evaluator.score_at_or_before(history, when) is None


def test_load_score_history_groups_by_ticker_sorted_oldest_first():
    with tempfile.TemporaryDirectory() as directory:
        path = os.path.join(directory, "squeeze_score_history.csv")
        with open(path, "w", encoding="utf-8") as f:
            f.write("timestamp,ticker,squeeze_score\n")
            f.write("2026-07-10T09:15:00+00:00,GME,65.0\n")
            f.write("2026-07-10T09:00:00+00:00,GME,50.0\n")
            f.write("2026-07-10T09:00:00+00:00,AMC,30.0\n")

        history = evaluator.load_score_history(path=path)

    assert [score for _, score in history["GME"]] == [50.0, 65.0]
    assert history["AMC"] == [(datetime(2026, 7, 10, 9, 0, tzinfo=timezone.utc), 30.0)]


def test_load_score_history_tolerates_malformed_row():
    with tempfile.TemporaryDirectory() as directory:
        path = os.path.join(directory, "squeeze_score_history.csv")
        with open(path, "w", encoding="utf-8") as f:
            f.write("timestamp,ticker,squeeze_score\n")
            f.write("2026-07-10T09:00:00+00:00,GME,not-a-number\n")
            f.write("2026-07-10T09:15:00+00:00,GME,65.0\n")

        history = evaluator.load_score_history(path=path)

    assert [score for _, score in history["GME"]] == [65.0]


def test_load_score_history_returns_empty_dict_when_file_missing():
    with tempfile.TemporaryDirectory() as directory:
        path = os.path.join(directory, "squeeze_score_history.csv")
        assert evaluator.load_score_history(path=path) == {}


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
