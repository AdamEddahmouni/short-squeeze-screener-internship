import csv
import os
import sys
import tempfile

sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

from core import squeeze_score_track_record


def _write_outcomes(path, rows):
    with open(path, "w", newline="", encoding="utf-8") as file:
        writer = csv.DictWriter(file, fieldnames=squeeze_score_track_record.OUTCOME_FIELDS)
        writer.writeheader()
        writer.writerows(rows)


def test_score_band_boundaries():
    assert squeeze_score_track_record.score_band(95) == "90+"
    assert squeeze_score_track_record.score_band(70) == "70-89"
    assert squeeze_score_track_record.score_band(40) == "40-69"
    assert squeeze_score_track_record.score_band(0) == "0-39"


def test_summarize_outcomes_returns_empty_list_when_file_missing():
    with tempfile.TemporaryDirectory() as directory:
        path = os.path.join(directory, "squeeze_score_outcomes.csv")
        assert squeeze_score_track_record.summarize_outcomes(path=path) == []


def test_summarize_outcomes_computes_avg_and_hit_rate_per_band():
    with tempfile.TemporaryDirectory() as directory:
        path = os.path.join(directory, "squeeze_score_outcomes.csv")
        _write_outcomes(path, [
            {"timestamp": "t1", "ticker": "GME", "squeeze_score": 95, "logged_price": 10,
             "current_price": 12, "pct_change": 20.0, "score_band": "90+"},
            {"timestamp": "t2", "ticker": "AMC", "squeeze_score": 92, "logged_price": 10,
             "current_price": 8, "pct_change": -20.0, "score_band": "90+"},
            {"timestamp": "t3", "ticker": "KOSS", "squeeze_score": 50, "logged_price": 5,
             "current_price": 5.5, "pct_change": 10.0, "score_band": "40-69"},
        ])

        summary = squeeze_score_track_record.summarize_outcomes(path=path)

    by_band = {row["score_band"]: row for row in summary}
    assert by_band["90+"]["n"] == 2
    assert by_band["90+"]["avg_change_percent"] == 0.0
    assert by_band["90+"]["hit_rate_percent"] == 50.0
    assert by_band["40-69"]["n"] == 1
    assert by_band["40-69"]["hit_rate_percent"] == 100.0
    # Ordered 90+ -> 0-39, skipping empty bands (no 70-89 or 0-39 rows above)
    assert [row["score_band"] for row in summary] == ["90+", "40-69"]


def test_summarize_outcomes_computes_alpha_relative_to_benchmark():
    with tempfile.TemporaryDirectory() as directory:
        path = os.path.join(directory, "squeeze_score_outcomes.csv")
        _write_outcomes(path, [
            {"timestamp": "t1", "ticker": "GME", "squeeze_score": 95, "logged_price": 10,
             "current_price": 12, "pct_change": 20.0, "score_band": "90+",
             "benchmark_pct_change": 5.0, "alpha_percent": 15.0},
            {"timestamp": "t2", "ticker": "AMC", "squeeze_score": 92, "logged_price": 10,
             "current_price": 9, "pct_change": -10.0, "score_band": "90+",
             "benchmark_pct_change": 5.0, "alpha_percent": -15.0},
        ])

        summary = squeeze_score_track_record.summarize_outcomes(path=path)

    row = summary[0]
    assert row["avg_alpha_percent"] == 0.0
    assert row["beat_benchmark_rate_percent"] == 50.0


def test_summarize_outcomes_omits_alpha_keys_when_no_row_has_benchmark_data():
    with tempfile.TemporaryDirectory() as directory:
        path = os.path.join(directory, "squeeze_score_outcomes.csv")
        _write_outcomes(path, [
            {"timestamp": "t1", "ticker": "GME", "squeeze_score": 95, "logged_price": 10,
             "current_price": 12, "pct_change": 20.0, "score_band": "90+",
             "benchmark_pct_change": "", "alpha_percent": ""},
        ])

        summary = squeeze_score_track_record.summarize_outcomes(path=path)

    assert "avg_alpha_percent" not in summary[0]
    assert "beat_benchmark_rate_percent" not in summary[0]


def test_summarize_outcomes_tolerates_malformed_row():
    with tempfile.TemporaryDirectory() as directory:
        path = os.path.join(directory, "squeeze_score_outcomes.csv")
        _write_outcomes(path, [
            {"timestamp": "t1", "ticker": "GME", "squeeze_score": 95, "logged_price": 10,
             "current_price": 12, "pct_change": "not-a-number", "score_band": "90+"},
            {"timestamp": "t2", "ticker": "AMC", "squeeze_score": 92, "logged_price": 10,
             "current_price": 12, "pct_change": 20.0, "score_band": "90+"},
        ])

        summary = squeeze_score_track_record.summarize_outcomes(path=path)

    assert len(summary) == 1
    assert summary[0]["n"] == 1


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
