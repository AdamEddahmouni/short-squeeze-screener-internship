import os
import sys
import tempfile

sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

from core import squeeze_score_history


def test_read_score_history_returns_empty_list_when_file_missing():
    with tempfile.TemporaryDirectory() as directory:
        path = os.path.join(directory, "squeeze_score_history.csv")
        assert squeeze_score_history.read_score_history("GME", path=path) == []


def test_append_then_read_round_trips_for_matching_ticker():
    with tempfile.TemporaryDirectory() as directory:
        path = os.path.join(directory, "squeeze_score_history.csv")
        squeeze_score_history.append_scores([("GME", 72.5), ("AMC", 40.0)], path=path)
        squeeze_score_history.append_scores([("GME", 81.0)], path=path)

        points = squeeze_score_history.read_score_history("gme", path=path)

    assert len(points) == 2
    assert [p["squeeze_score"] for p in points] == [72.5, 81.0]
    assert all("timestamp" in p for p in points)


def test_append_scores_skips_none_scores():
    with tempfile.TemporaryDirectory() as directory:
        path = os.path.join(directory, "squeeze_score_history.csv")
        squeeze_score_history.append_scores([("GME", None), ("AMC", 40.0)], path=path)

        assert squeeze_score_history.read_score_history("GME", path=path) == []
        assert len(squeeze_score_history.read_score_history("AMC", path=path)) == 1


def test_read_score_history_ignores_other_tickers():
    with tempfile.TemporaryDirectory() as directory:
        path = os.path.join(directory, "squeeze_score_history.csv")
        squeeze_score_history.append_scores([("GME", 72.5), ("AMC", 40.0)], path=path)

        assert len(squeeze_score_history.read_score_history("AMC", path=path)) == 1


def test_read_score_history_tolerates_malformed_row():
    with tempfile.TemporaryDirectory() as directory:
        path = os.path.join(directory, "squeeze_score_history.csv")
        with open(path, "w", encoding="utf-8") as file:
            file.write("timestamp,ticker,squeeze_score\n")
            file.write("2026-07-16T00:00:00+00:00,GME,not-a-number\n")
            file.write("2026-07-16T00:01:00+00:00,GME,55.0\n")

        points = squeeze_score_history.read_score_history("GME", path=path)

    assert len(points) == 1
    assert points[0]["squeeze_score"] == 55.0


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
