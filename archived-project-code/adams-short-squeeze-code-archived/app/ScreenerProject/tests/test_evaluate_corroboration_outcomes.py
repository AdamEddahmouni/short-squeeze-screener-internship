import os
import sys
from datetime import datetime, timezone

sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

import evaluate_corroboration_outcomes as evaluator


def test_score_at_or_before_returns_latest_matching_entry():
    history = [
        (datetime(2026, 7, 17, 9, 0, tzinfo=timezone.utc), 2),
        (datetime(2026, 7, 17, 9, 15, tzinfo=timezone.utc), 3),
        (datetime(2026, 7, 17, 9, 30, tzinfo=timezone.utc), 4),
    ]
    when = datetime(2026, 7, 17, 9, 20, tzinfo=timezone.utc)
    assert evaluator.score_at_or_before(history, when) == 3


def test_score_at_or_before_returns_none_when_history_starts_after():
    history = [(datetime(2026, 7, 17, 9, 30, tzinfo=timezone.utc), 4)]
    when = datetime(2026, 7, 17, 9, 0, tzinfo=timezone.utc)
    assert evaluator.score_at_or_before(history, when) is None


def test_load_score_history_groups_by_ticker_sorted_oldest_first():
    import tempfile
    with tempfile.TemporaryDirectory() as directory:
        path = os.path.join(directory, "corroboration_history.csv")
        with open(path, "w", encoding="utf-8") as f:
            f.write("timestamp,ticker,corroboration_score\n")
            f.write("2026-07-17T09:15:00+00:00,GME,3\n")
            f.write("2026-07-17T09:00:00+00:00,GME,2\n")
            f.write("2026-07-17T09:00:00+00:00,AMC,4\n")

        history = evaluator.load_score_history(path=path)

    assert [score for _, score in history["GME"]] == [2.0, 3.0]
    assert history["AMC"] == [(datetime(2026, 7, 17, 9, 0, tzinfo=timezone.utc), 4.0)]


def test_load_score_history_returns_empty_dict_when_file_missing():
    import tempfile
    with tempfile.TemporaryDirectory() as directory:
        path = os.path.join(directory, "corroboration_history.csv")
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
