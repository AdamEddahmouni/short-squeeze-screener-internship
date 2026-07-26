import csv
import os
import sys
import tempfile

sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

from core import corroboration_track_record


def _write_outcomes(path, rows):
    with open(path, "w", newline="", encoding="utf-8") as file:
        writer = csv.DictWriter(file, fieldnames=corroboration_track_record.OUTCOME_FIELDS)
        writer.writeheader()
        writer.writerows(rows)


def test_score_band_maps_integer_scores_to_string_labels():
    assert corroboration_track_record.score_band(4) == "4"
    assert corroboration_track_record.score_band(0) == "0"
    assert corroboration_track_record.score_band(2.0) == "2"


def test_score_band_returns_unknown_for_out_of_range_score():
    assert corroboration_track_record.score_band(7) == "unknown"


def test_summarize_outcomes_returns_empty_list_when_file_missing():
    with tempfile.TemporaryDirectory() as directory:
        path = os.path.join(directory, "corroboration_outcomes.csv")
        assert corroboration_track_record.summarize_outcomes(path=path) == []


def test_summarize_outcomes_computes_avg_and_hit_rate_per_band():
    with tempfile.TemporaryDirectory() as directory:
        path = os.path.join(directory, "corroboration_outcomes.csv")
        _write_outcomes(path, [
            {"timestamp": "t1", "ticker": "GME", "corroboration_score": 4,
             "logged_price": 10, "current_price": 12, "pct_change": 20.0},
            {"timestamp": "t2", "ticker": "AMC", "corroboration_score": 4,
             "logged_price": 10, "current_price": 8, "pct_change": -20.0},
            {"timestamp": "t3", "ticker": "KOSS", "corroboration_score": 1,
             "logged_price": 5, "current_price": 5.5, "pct_change": 10.0},
        ])

        summary = corroboration_track_record.summarize_outcomes(path=path)

    by_band = {row["score_band"]: row for row in summary}
    assert by_band["4"]["n"] == 2
    assert by_band["4"]["avg_change_percent"] == 0.0
    assert by_band["4"]["hit_rate_percent"] == 50.0
    assert by_band["1"]["n"] == 1
    assert by_band["1"]["hit_rate_percent"] == 100.0
    # Ordered 4 -> 0, skipping empty bands
    assert [row["score_band"] for row in summary] == ["4", "1"]


def test_summarize_outcomes_computes_alpha_relative_to_benchmark():
    with tempfile.TemporaryDirectory() as directory:
        path = os.path.join(directory, "corroboration_outcomes.csv")
        _write_outcomes(path, [
            {"timestamp": "t1", "ticker": "GME", "corroboration_score": 4,
             "logged_price": 10, "current_price": 12, "pct_change": 20.0,
             "benchmark_pct_change": 5.0, "alpha_percent": 15.0},
            {"timestamp": "t2", "ticker": "AMC", "corroboration_score": 4,
             "logged_price": 10, "current_price": 9, "pct_change": -10.0,
             "benchmark_pct_change": 5.0, "alpha_percent": -15.0},
        ])

        summary = corroboration_track_record.summarize_outcomes(path=path)

    row = summary[0]
    assert row["avg_alpha_percent"] == 0.0
    assert row["beat_benchmark_rate_percent"] == 50.0


def test_summarize_outcomes_omits_alpha_keys_when_no_row_has_benchmark_data():
    with tempfile.TemporaryDirectory() as directory:
        path = os.path.join(directory, "corroboration_outcomes.csv")
        _write_outcomes(path, [
            {"timestamp": "t1", "ticker": "GME", "corroboration_score": 4,
             "logged_price": 10, "current_price": 12, "pct_change": 20.0,
             "benchmark_pct_change": "", "alpha_percent": ""},
        ])

        summary = corroboration_track_record.summarize_outcomes(path=path)

    assert "avg_alpha_percent" not in summary[0]
    assert "beat_benchmark_rate_percent" not in summary[0]


def test_summarize_outcomes_tolerates_malformed_row():
    with tempfile.TemporaryDirectory() as directory:
        path = os.path.join(directory, "corroboration_outcomes.csv")
        _write_outcomes(path, [
            {"timestamp": "t1", "ticker": "GME", "corroboration_score": 4,
             "logged_price": 10, "current_price": 12, "pct_change": "not-a-number"},
            {"timestamp": "t2", "ticker": "AMC", "corroboration_score": 4,
             "logged_price": 10, "current_price": 12, "pct_change": 20.0},
        ])

        summary = corroboration_track_record.summarize_outcomes(path=path)

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
